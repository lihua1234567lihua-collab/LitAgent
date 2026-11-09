"""LangGraph orchestration for LitAgent.

This module deliberately contains workflow state, node boundaries, routing, and
checkpoint wiring only. Network calls, paper reading, full-text resolution, and
RAG remain implemented by the existing tools, services, and rag packages.工作流编排，定义节点，连接节点，管理执行顺序和状态流转
"""

import json
import logging
import operator
import re
from typing import Annotated, Any, Callable, NotRequired, TypedDict
from langchain_core.messages import AIMessage, AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt
from services.topic_service import resolve_topic_from_query
from services.library_rag_service import (
    answer_topic_question,
    answer_user_library_question,
    answer_uploaded_paper_question,
)
from agent.router import create_router
from rag.pipeline import answer_with_rag
from rag.query_rewriter import rewrite_query
from services.code_reproduce_service import run_code_reproduce
from services.local_pdf_resolver import resolve_paper_content
from agent.step_validator import (
    validate_code_reproduce,
    validate_paper_read,
    validate_paper_search,
    validate_reasoning,
)
from services.paper_read_service import prepare_paper_read
from tools.paper_metadata import fetch_paper_metadata
from tools.paper_search import search_papers
from services.paper_search_request_service import build_search_request
from agent.context_manager import (
    get_router_history,
    get_recent_messages,
)


logger = logging.getLogger(__name__)

ROUTES = {"direct_answer", "local_rag", "paper_search", "planner"}
ACTIONS = {"paper_search", "paper_read", "rag", "reasoning", "code_reproduce"}


def merge_dicts(
    left: dict[str, Any] | None,
    right: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge cache updates instead of replacing the whole cache."""

    return {**(left or {}), **(right or {})}


class ResearchState(TypedDict):
    """Small, explicit state shared by every workflow node."""

    user_query: str
    user_id:NotRequired[int]
    topic_id: NotRequired[int]
    latest_uploaded_paper_id: NotRequired[int | None]
    route: NotRequired[str]
    search_query: NotRequired[str]
    search_results: NotRequired[list[dict[str, Any]]]
    selected_papers: NotRequired[list[dict[str, Any]]]
    paper_contents: NotRequired[
        Annotated[dict[str, dict[str, Any]], merge_dicts]
    ]
    paper_analyses: NotRequired[
        Annotated[dict[str, dict[str, Any]], merge_dicts]
    ]
    plan: NotRequired[list[str]]
    retry_count:NotRequired[int]
    current_step: NotRequired[int]
    step_action: NotRequired[str]
    step_output:NotRequired[dict[str,Any]] ##保存房前尝试结果
    step_validation:NotRequired[dict[str,Any]] ##预留validator结果
    step_results: Annotated[list[str], operator.add]
    answer: NotRequired[str]
    messages: Annotated[list[AnyMessage], add_messages]##当前thread的对话历史。add_messages持续累积
    trace: Annotated[list[str], operator.add]
    approved: NotRequired[bool]
    pending_fulltext: NotRequired[list[dict[str, Any]]]
    paper_scope: NotRequired[str]


def _response_text(response: Any) -> str:
    content = getattr(response, "content", response)
    return str(content).strip()


def _parse_plan_response(content: str, fallback_query: str) -> list[str]:
    plan = []
    for line in content.splitlines():
        match = re.match(r"^\s*\d+\s*[.)、]\s*(.+?)\s*$", line)
        if match:
            plan.append(match.group(1).strip())

    if not plan:
        plan = [fallback_query]

    return plan


def _normalize_action(action: str) -> str:
    normalized = action.strip().lower().strip("`*_ ").replace("-", "_")
    if normalized == "local_rag":
        return "rag"
    if normalized not in ACTIONS:
        raise ValueError(f"Executor returned unsupported action: {action!r}")
    return normalized


def _normalize_papers(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, list):
        raise TypeError("paper search must return a list of paper dictionaries")
    return [paper for paper in value if isinstance(paper, dict)]


def _current_step(state: ResearchState) -> tuple[int, str]:
    index = state.get("current_step", 0)
    plan = state.get("plan", [])
    if index >= len(plan):
        raise ValueError("current_step points past the end of the plan")
    return index, plan[index]

def _record_step_output(
    state: ResearchState,
    output: dict[str, Any],
    trace_name: str,
) -> dict[str, Any]:
    return {
        "step_output": dict(output),
        "trace": [trace_name],
    }

def _step_update(
    state: ResearchState,
    result: str,
    trace_name: str,
) -> dict[str, Any]:
    index, step = _current_step(state)
    return {
        "step_results": [f"Step {index + 1}: {step}\nResult: {result}"],
        "current_step": index + 1,
        "trace": [trace_name],
    }


def create_node_handlers(model: Any) -> dict[str, Callable[..., dict[str, Any]]]:
    """Create node callables with the model dependency injected.

    Keeping dependency injection at this boundary makes the graph easy to
    compile with the real model and easy to test without network calls.
    """

    router = create_router(model)

    def router_node(state: ResearchState) -> dict[str, Any]:
        history = get_router_history(state, limit=4)

        decision = router.invoke({
            "question": state["user_query"],
            "history": history,
        })

        route = decision.route
        if route not in ROUTES:
            raise ValueError(f"Router returned unsupported route: {route!r}")
        logger.info("[Router] route=%s", route)
        return {"route": route, "paper_scope": decision.paper_scope, "trace": ["router"]}

    def planner_node(state: ResearchState) -> dict[str, Any]:
        prompt = f"""
                You are a research task planner.

                Break the user's request into a concise numbered plan.

                Each plan item must describe exactly one task.
                Do not answer the user's question.
                Do not generate search queries.

                User request:
                {state["user_query"]}
                """

        plan = _parse_plan_response(
            _response_text(model.invoke(prompt)),
            state["user_query"],
        )
        return {
            "plan": plan,
            "current_step": 0,
            "trace": ["planner"],
        }

    def validator_node(state: ResearchState) -> dict[str, Any]:
        _, step = _current_step(state)
        output = state.get("step_output", {})

        if output.get("action") == "paper_read":
            validation = validate_paper_read(
                step_goal=step,
                paper_contents=state.get("paper_contents", {}),
                paper_analyses=state.get("paper_analyses", {}),
            )
        elif output.get("action") == "reasoning":
            validation = validate_reasoning(
                step_goal=step,
                result=output.get("result", ""),
            )
        elif output.get("action") == "code_reproduce":
            validation = validate_code_reproduce(
                step_goal=step,
                result=output.get("result", {}),
            )
        else:
            validation = validate_paper_search(
                step_goal=step,
                search_results=output.get("search_results", []),
            )

        if not validation["passed"]:
            return {
                "step_validation": validation,
                "trace": ["validator_failed"],
            }

        update = _step_update(
            state,
            output.get("summary", "Paper search accepted."),
            "validator",
        )
        update["step_validation"] = validation
        return update


    def executor_node(state: ResearchState) -> dict[str, Any]:
        index, step = _current_step(state)
        prompt = f"""
                Choose exactly one capability for this research plan step:
                - paper_search: search for new paper metadata
                - paper_read: read selected paper content and extract structured details
                - rag: answer from the local paper knowledge base
                - reasoning: compare, summarize, or analyze information already in state
                - code_reproduce: run one safe smoke test for an explicitly provided GitHub repository

                Plan step {index + 1}:
                {step}

                Return only one capability name.
                """
        action = _normalize_action(_response_text(model.invoke(prompt)))
        logger.info("[Executor] step=%s action=%s", index + 1, action)
        return {"step_action": action, "trace": ["executor"]}

    def direct_answer_node(state: ResearchState) -> dict[str, Any]:
        context = get_recent_messages(state, limit=6)
        model_input = context if context else state["user_query"]
        answer = _response_text(model.invoke(model_input))
        return {
            "answer": answer,
            "messages": [AIMessage(content=answer)],
            "trace": ["direct_answer"],
        }

    def rewrite_query_node(state: ResearchState) -> dict[str, Any]:
        query = rewrite_query(model, state["user_query"])
        return {"search_query": query, "trace": ["rewrite_query"]}

    async def rag_node(state: ResearchState) -> dict[str, Any]:
        is_planner_step = bool(state.get("plan"))

        query = (
            state["plan"][state.get("current_step", 0)]
            if is_planner_step
            else state["user_query"]
        )

        user_id = state.get("user_id")
        search_query = state.get("search_query")

        if user_id is not None:

            paper_scope = state.get("paper_scope", "none")
            paper_id = state.get("latest_uploaded_paper_id")

            if paper_scope == "current_paper":
                # 用户正在询问当前论文
                if paper_id is None:
                    answer = "当前会话没有关联的论文，请先上传 PDF。"
                else:
                    answer = await answer_uploaded_paper_question(
                        user_id=user_id,
                        paper_id=paper_id,
                        user_query=query,
                        model=model,
                    )

            elif paper_scope == "topic":
                # 用户询问某个 Topic 下的论文
                topic_id = await resolve_topic_from_query(
                    user_id=user_id,
                    user_query=state["user_query"],
                )

                if topic_id is None:
                    answer = "无法确定你要查询的 Topic，请提供具体的 Topic 名称。"
                else:
                    answer = await answer_topic_question(
                        topic_id=topic_id,
                        user_query=query,
                        model=model,
                    )

            else:
                # 用户论文库范围，或未明确指定范围
                answer = await answer_user_library_question(
                    user_id=user_id,
                    user_query=query,
                    model=model,
                )

        if not is_planner_step:
            return {
                "answer": answer,
                "messages": [AIMessage(content=answer)],
                "trace": ["rag"],
            }

        update = _step_update(state, answer, "rag")
        if search_query is not None:
            update["search_query"] = search_query
        return update

    def paper_search_node(state: ResearchState) -> dict[str, Any]:
        results = list(state.get("search_results") or [])
        query = state.get("search_query")

        if not results:
            # 解析用户的论文检索条件
            request = build_search_request(
                model,
                state["user_query"],
            )

            query = request.query

            logger.info(
                "[PaperSearch] query=%s top_k=%s years=%s-%s",
                request.query,
                request.top_k,
                request.start_year,
                request.end_year,
            )

            # 调用 OpenAlex
            results = _normalize_papers(
                search_papers.invoke(request.model_dump())
            )


        # 新增：验证论文搜索结果
        validation = validate_paper_search(
            step_goal=state["user_query"],
            search_results=results,
        )

        logger.info("[PaperSearch Validator] %s", validation)
        print("[PaperSearch Validator]", validation, flush=True)

        selected = list(state.get("selected_papers") or results[:3])
        update: dict[str, Any] = {
            "search_results": results,
            "selected_papers": selected,
            "search_query": query,
        }


        if state.get("plan"):
            update.update(
            _record_step_output(
                state,
                {
                    "action": "paper_search",
                    "query": state.get("search_query") or state["user_query"],
                    "search_results": results,
                    "selected_papers": selected,
                    "summary": (
                        f"Cached {len(results)} search results "
                        f"and selected {len(selected)} papers."
                    ),
                },
                "paper_search",
            )
        )
            return update

        prompt = f"""
                Answer the user's paper-search request using only these search results:
                {json.dumps(results, ensure_ascii=False)}

                User request:
                {state['user_query']}
                """
        answer = _response_text(model.invoke(prompt))
        update.update(
            {
                "answer": answer,
                "messages": [AIMessage(content=answer)],
                "trace": ["paper_search"],
            }
        )
        return update

    async def paper_read_node(state: ResearchState, config: RunnableConfig | None = None) -> dict[str, Any]:
        _, step = _current_step(state)
        result = await prepare_paper_read(
            task=step,
            model=model,
            state=state,
            config=config,
            paper_reader=fetch_paper_metadata,
            resolver=resolve_paper_content,
        )
        if result["missing"]:
            logger.warning(
                "[PaperRead] fulltext unavailable: %s",
                len(result["missing"]),
            )

            return {
                # 关键：先把 mcp_attempts 保存进 State
                "paper_contents": result["paper_contents"],
                "paper_analyses": result["paper_analyses"],
                "pending_fulltext": result["missing"],
                "trace": ["paper_read_missing"],
            }

        return {
        "paper_contents": result["paper_contents"],
        "paper_analyses": result["paper_analyses"],
        "pending_fulltext": [],
        "step_output": {
            "action": "paper_read",
            "summary": result["summary"],
        },
        "trace": ["paper_read"],
    }

    async def code_reproduce_node(state: ResearchState) -> dict[str, Any]:
        _, step = _current_step(state)
        result = await run_code_reproduce(
            f"{state['user_query']}\nPlan step: {step}"
        )
        return {
            "step_output": {
                "action": "code_reproduce",
                "result": result,
                "summary": json.dumps(result, ensure_ascii=False),
            },
            "trace": ["code_reproduce"],
        }

    def reasoning_node(state: ResearchState) -> dict[str, Any]:
        _, step = _current_step(state)
        evidence = {
            "search_results": state.get("search_results", []),
            "paper_contents": state.get("paper_contents", {}),
            "paper_analyses": state.get("paper_analyses", {}),
            "step_results": state.get("step_results", []),
        }
        prompt = f"""
Complete only this research step using the evidence already in state:
{step}

Evidence:
{json.dumps(evidence, ensure_ascii=False)}
"""
        result = _response_text(model.invoke(prompt))
        return {
            "step_output": {
                "action": "reasoning",
                "result": result,
                "summary": result,
            },
            "trace": ["reasoning"],
        }

    def paper_read_wait_node(state: ResearchState) -> dict[str, Any]:
        _, step = _current_step(state)

        interrupt({
            "type": "fulltext_required",
            "message": "暂时无法自动获取论文全文，请上传 PDF 后继续。",
            "papers": state.get("pending_fulltext", []),
            "step": step,
        })

        return {
            "trace": ["paper_read_resumed"],
    }

    def final_answer_node(state: ResearchState) -> dict[str, Any]:
        prompt = f"""
Answer the user's original request using the completed research results.

Question:
{state['user_query']}

Results:
{json.dumps(state.get('step_results', []), ensure_ascii=False)}

Cached paper analyses:
{json.dumps(state.get('paper_analyses', {}), ensure_ascii=False)}
"""
        answer = _response_text(model.invoke(prompt))
        return {
            "answer": answer,
            "messages": [AIMessage(content=answer)],
            "trace": ["final_answer"],
        }

    def approval_node(state: ResearchState) -> dict[str, Any]:
        approved = interrupt(
            {
                "type": "external_search_approval",
                "message": "Continue with external paper search?",
                "query": state["user_query"],
            }
        )
        return {"approved": bool(approved), "trace": ["approval"]}

    def cancel_node(state: ResearchState) -> dict[str, Any]:
        return {
            "answer": "Paper search cancelled.",
            "messages": [AIMessage(content="Paper search cancelled.")],
            "trace": ["cancel"],
        }

    return {
        "router": router_node,
        "planner": planner_node,
        "executor": executor_node,
        "direct_answer": direct_answer_node,
        "rewrite_query": rewrite_query_node,
        "rag": rag_node,
        "paper_search": paper_search_node,
        "paper_read": paper_read_node,
        "code_reproduce": code_reproduce_node,
        "reasoning": reasoning_node,
        "final_answer": final_answer_node,
        "approval": approval_node,
        "cancel": cancel_node,
        "validator": validator_node,
        "paper_read_wait": paper_read_wait_node,
    }


def route_from_state(state: ResearchState) -> str:
    return state["route"]


def approval_route(state: ResearchState) -> str:
    return "paper_search" if state.get("approved") else "cancel"


def action_route(state: ResearchState) -> str:
    return state["step_action"]


def plan_route(state: ResearchState) -> str:
    return (
        "finish"
        if state.get("current_step", 0) >= len(state.get("plan", []))
        else "continue"
    )


def capability_route(state: ResearchState) -> str:
    if not state.get("plan"):
        return "end"
    return plan_route(state)


def paper_search_route(state: ResearchState) -> str:
    if not state.get("plan"):
        return "end"
    return "validate"


def validation_route(state: ResearchState) -> str:
    validation = state.get("step_validation", {})

    if not validation.get("passed"):
        return "failed"

    return capability_route(state)

def paper_read_route(state: ResearchState) -> str:
    if state.get("pending_fulltext"):
        return "wait"
    return "validate"


def build_research_graph(model: Any, checkpointer=None):
    """Build and compile the maintained LitAgent workflow."""

    handlers = create_node_handlers(model)
    builder = StateGraph(ResearchState)

    for node_name, handler in handlers.items():
        builder.add_node(node_name, handler)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        route_from_state,
        {
            "direct_answer": "direct_answer",
            "local_rag": "rewrite_query",
            "paper_search": "approval",
            "planner": "planner",
        },
    )
    builder.add_edge("direct_answer", END)
    builder.add_edge("rewrite_query", "rag")
    builder.add_conditional_edges(
        "rag",
        capability_route,
        {"end": END, "continue": "executor", "finish": "final_answer"},
    )
    builder.add_conditional_edges(
        "approval",
        approval_route,
        {"paper_search": "paper_search", "cancel": "cancel"},
    )
    builder.add_edge("cancel", END)
    builder.add_conditional_edges(
    "paper_search",
    paper_search_route,
    {
        "end": END,
        "validate": "validator",
    },
)
    builder.add_conditional_edges(
        "validator",
        validation_route,
        {
            "failed": END,
            "end": END,
            "continue": "executor",
            "finish": "final_answer",
        },
    )
    builder.add_edge("planner", "executor")
    builder.add_conditional_edges(
        "executor",
        action_route,
        {
            "paper_search": "paper_search",
            "paper_read": "paper_read",
            "rag": "rag",
            "reasoning": "reasoning",
            "code_reproduce": "code_reproduce",
        },
    )
    builder.add_conditional_edges(
    "paper_read",
    paper_read_route,
    {
        "retry": "paper_read",
        "wait": "paper_read_wait",
        "validate": "validator",
    },
)
    builder.add_edge("paper_read_wait", "paper_read")
    builder.add_edge("code_reproduce", "validator")
    builder.add_edge("reasoning", "validator")
    builder.add_edge("final_answer", END)

    return builder.compile(checkpointer=checkpointer)
