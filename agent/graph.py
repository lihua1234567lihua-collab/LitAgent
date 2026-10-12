from typing import TypedDict, NotRequired, Annotated
import operator
import os
import re
import sqlite3

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt

from langchain_core.messages import AnyMessage, AIMessage

from agent.router import create_router
from agent.paper_search_pipeline import search_papers_with_agent

from rag.pipeline import answer_with_rag
from rag.query_rewriter import rewrite_query
import json
from tools.paper_search import search_papers
from tools.paper_reader import read_paper
# ============================================================
# 1. State
# ============================================================

class ResearchState(TypedDict):
    # -------------------------
    # 用户输入
    # -------------------------
    user_query: str

    # -------------------------
    # Router
    # -------------------------
    route: NotRequired[str]

    # -------------------------
    # RAG
    # -------------------------
    search_query: NotRequired[str]

    # -------------------------
    # 最终回答
    # -------------------------
    answer: NotRequired[str]

    # -------------------------
    # 调试：记录经过的节点
    #
    # operator.add 表示每个节点返回：
    # {"trace": ["xxx"]}
    #
    # LangGraph 会自动追加，而不是覆盖
    # -------------------------
    trace: Annotated[list[str], operator.add]

    # -------------------------
    # 对话消息
    # -------------------------
    messages: Annotated[list[AnyMessage], add_messages]
    
    # -------------------------
    # 论文检索词
    # -------------------------
    search_query: NotRequired[str]
    # -------------------------
    # Human-in-the-loop
    # -------------------------
    approved: NotRequired[bool]

    # ========================================================
    # Planner
    # ========================================================

    # 完整计划
    plan: NotRequired[list[str]]

    # 当前执行到第几步
    current_step: NotRequired[int]

    # 当前步骤应该由哪种能力执行
    step_action: NotRequired[str]

    # 保存 Planner 每一步产生的结果
    step_results: Annotated[list[str], operator.add]
    
    #保存搜索到的文章
    selected_papers: NotRequired[list[dict]]

# ============================================================
# 2. 构建 Graph
# ============================================================

def build_research_graph(model):

    # 创建 Router chain
    router = create_router(model)

    # ========================================================
    # Router Node
    # ========================================================

    def router_node(state: ResearchState) -> dict:
        """
        判断用户请求应该走哪条路线。
        """

        decision = router.invoke(
            {
                "question": state["user_query"]
            }
        )

        return {
            "route": decision.route,
            "trace": ["router"],
        }

    # ========================================================
    # Planner Node
    # ========================================================

    def planner_node(state: ResearchState) -> dict:
        user_query = state["user_query"]

        prompt = f"""
    你是一个科研任务规划器。

    请根据用户任务生成：

    SEARCH_QUERY:
    用于学术论文检索的简洁英文关键词。

    PLAN:
    1. ...
    2. ...
    3. ...

    要求：
    1. SEARCH_QUERY 只保留适合学术检索的核心关键词
    2. PLAN 每一步只做一件事情
    3. 不要回答用户问题
    4. 不要解释

    用户任务：
    {user_query}
    """

        response = model.invoke(prompt)

        content = response.content.strip()
        # =========================
        # 提取 search_query
        # =========================
        search_query = ""

        match = re.search(
            r"SEARCH_QUERY:\s*(.+)",
            content,
            re.IGNORECASE,
        )

        if match:
            search_query = match.group(1).strip()


        # =========================
        # 提取 plan
        # =========================
        plan = []

        for line in content.splitlines():
            line = line.strip()

            if re.match(r"^\d+[\.\、\)]", line):
                step = re.sub(
                    r"^\d+[\.\、\)]\s*",
                    "",
                    line,
                )

                plan.append(step)


        print("===== Planner Search Query =====")
        print(repr(search_query))

        print("===== Planner Plan =====")
        print(plan)

        return {
            "search_query": search_query,
            "plan": plan,
            "current_step": 0,
            "trace": ["planner"],
        }
    # ========================================================
    # Paper Read Node
    # ========================================================
    def planner_paper_read_node(state: ResearchState) -> dict:
        current_step = state["current_step"]
        step = state["plan"][current_step]

        selected_papers = state.get("selected_papers", [])

        print(f"\n[Paper Read] 当前步骤：{step}")

        paper_contents = []

        for paper in selected_papers:
            result = read_paper(paper)
            paper_contents.append(result)

        prompt = f"""
    当前任务步骤：

    {step}

    下面是已经筛选出的论文及其摘要信息：

    {json.dumps(paper_contents, ensure_ascii=False, indent=2)}

    请只完成当前步骤要求的信息提取。

    要求：
    1. 严格基于提供的论文信息
    2. 如果摘要中没有明确提到某项内容，就说明“摘要中未明确说明”
    3. 不要编造
    """

        response = model.invoke(prompt)

        result = response.content

        return {
            "step_results": [
                f"步骤 {current_step + 1}：{step}\n结果：{result}"
            ],
            "current_step": current_step + 1,
            "trace": ["planner_paper_read"],
        }


    # ========================================================
    # Executor Node
    # ========================================================

    def executor_node(state: ResearchState) -> dict:
        """
        Executor 本身不真正执行任务。

        它只负责：
        1. 读取 plan[current_step]
        2. 判断这个步骤应该交给哪个能力
        """

        current_step = state["current_step"]
        step = state["plan"][current_step]

        prompt = f"""
    你是一个任务执行调度器。

    当前任务步骤：

    {step}

    当前系统有以下四种能力：

    1. paper_search
    用途：
    - 搜索新的论文
    - 查找论文
    - 根据主题筛选论文
    - 获取论文标题、作者、DOI 等元数据

    注意：
    paper_search 不负责读取论文正文。

    2. paper_read
    用途：
    - 读取之前已经通过 paper_search 选中的论文
    - 根据 selected_papers 中的 DOI、URL 或论文标识获取摘要或正文
    - 提取论文的方法、数据集、实验结果、优缺点等具体内容

    3. local_rag
    用途：
    - 查询已经提前存入本地 Chroma 知识库的论文
    - 只有明确需要查询本地论文库时才使用

    不要使用 local_rag 去读取刚刚通过 paper_search 搜索到、但尚未存入 Chroma 的论文。

    4. reasoning
    用途：
    - 基于前面步骤已经得到的信息进行比较
    - 分析
    - 总结
    - 归纳
    - 生成表格或最终结论

    reasoning 不负责搜索新的论文，也不负责读取新的论文内容。

    请选择最适合当前步骤的一种能力。

    只能返回下面四个值之一：

    paper_search
    paper_read
    local_rag
    reasoning

    不要解释。
    """

        response = model.invoke(prompt)

        action = response.content.strip()

        print(
            f"\n[Executor] 第 {current_step + 1} 步：{step}"
        )
        print(
            f"[Executor] 选择能力：{action}"
        )

        return {
            "step_action": action,
            "trace": ["executor"],
        }

    # ========================================================
    # Planner - Paper Search
    # ========================================================

    def planner_paper_search_node(state: ResearchState) -> dict:
        current_step = state["current_step"]
        step = state["plan"][current_step]

        # 直接调用论文搜索工具，拿结构化结果
        papers = search_papers.invoke({
            "query": state["search_query"],
            "top_k": 5,
        })

        print("===== search_papers 原始返回 =====")
        print(type(papers))
        print(papers)
        print(repr(papers))

        # 如果工具返回的是 JSON 字符串
        if isinstance(papers, str):
            papers = json.loads(papers)

        # 目前先简单取前 3 篇
        selected_papers = papers[:3]

        return {
            "selected_papers": selected_papers,

            "step_results": [
                f"步骤 {current_step + 1}：已筛选出 {len(selected_papers)} 篇论文"
            ],

            "current_step": current_step + 1,
            "trace": ["planner_paper_search"],
        }

    # ========================================================
    # Planner - Local RAG
    # ========================================================

    def planner_rag_node(
        state: ResearchState,
    ) -> dict:
        """
        执行 Planner 中需要查询论文内容的步骤。
        """

        current_step = state["current_step"]
        step = state["plan"][current_step]

        # 为当前步骤生成 RAG 查询
        search_query = rewrite_query(
            model,
            step,
        )

        result = answer_with_rag(
            user_query=step,
            model=model,
            search_query=search_query,
        )

        return {
            "step_results": [
                f"步骤 {current_step + 1}：{step}\n结果：{result}"
            ],

            "current_step": current_step + 1,

            "trace": ["planner_rag"],
        }

    # ========================================================
    # Planner - Reasoning
    # ========================================================

    def planner_reasoning_node(
        state: ResearchState,
    ) -> dict:
        """
        使用 LLM 对前面步骤产生的结果进行分析、比较或总结。
        """

        current_step = state["current_step"]
        step = state["plan"][current_step]

        previous_results = "\n\n".join(
            state.get("step_results", [])
        )

        prompt = f"""
当前任务步骤：

{step}

以下是之前已经完成的步骤以及结果：

{previous_results}

请根据已有信息完成当前任务步骤。
不要执行当前步骤之外的任务。
"""

        response = model.invoke(prompt)

        result = response.content

        return {
            "step_results": [
                f"步骤 {current_step + 1}：{step}\n结果：{result}"
            ],

            "current_step": current_step + 1,

            "trace": ["planner_reasoning"],
        }

    # ========================================================
    # Planner Final Node
    # ========================================================

    def planner_final_node(
        state: ResearchState,
    ) -> dict:
        """
        所有 plan 执行完成后，
        根据所有 step_results 生成最终回答。
        """

        results = "\n\n".join(
            state.get("step_results", [])
        )

        prompt = f"""
                用户原始问题：

                {state["user_query"]}

                以下是任务执行过程中得到的结果：

                {results}

                请根据这些结果生成最终回答。
                """

        response = model.invoke(prompt)

        return {
            "answer": response.content,
            "trace": ["planner_final"],
        }

    # ========================================================
    # Human Approval
    # ========================================================

    def approval_node(
        state: ResearchState,
    ) -> dict:

        approved = interrupt(
            {
                "message": "即将调用外部论文检索，是否继续",
                "query": state["user_query"],
            }
        )

        return {
            "approved": approved,
            "trace": ["approval"],
        }

    # ========================================================
    # Cancel
    # ========================================================

    def cancel_node(
        state: ResearchState,
    ) -> dict:

        return {
            "answer": "已取消论文检索。",
            "trace": ["cancel"],
        }

    # ========================================================
    # Direct Answer
    # ========================================================

    def direct_answer_node(
        state: ResearchState,
    ) -> dict:

        response = model.invoke(
            [
                {
                    "role": "user",
                    "content": state["user_query"],
                }
            ]
        )

        return {
            "answer": response.content,
            "trace": ["direct_answer"],
        }

    # ========================================================
    # 普通 Local RAG 路线
    # ========================================================

    def rewrite_query_node(
        state: ResearchState,
    ) -> dict:

        search_query = rewrite_query(
            model,
            state["user_query"],
        )

        return {
            "search_query": search_query,
            "trace": ["rewrite_query"],
        }

    def local_rag_node(
        state: ResearchState,
    ) -> dict:

        answer = answer_with_rag(
            user_query=state["user_query"],
            model=model,
            search_query=state["search_query"],
        )

        return {
            "answer": answer,
            "trace": ["local_rag"],
            "messages": [
                AIMessage(content=answer)
            ],
        }

    # ========================================================
    # 普通 Paper Search 路线
    # ========================================================

    def paper_search_node(
        state: ResearchState,
    ) -> dict:

        answer = search_papers_with_agent(
            user_query=state["user_query"],
            model=model,
        )

        return {
            "answer": answer,
            "trace": ["paper_search"],
        }

    # ========================================================
    # 3. Conditional Routing
    # ========================================================

    def choose_route(
        state: ResearchState,
    ) -> str:
        """
        Router → 对应路线
        """
        return state["route"]

    def choose_after_approval(
        state: ResearchState,
    ) -> str:
        """
        用户批准 → 搜索
        用户拒绝 → cancel
        """

        if state["approved"]:
            return "paper_search"

        return "cancel"

    def choose_executor_action(
        state: ResearchState,
    ) -> str:
        """
        Executor 根据 step_action
        选择真正执行当前步骤的节点。
        """

        return state["step_action"]

    def choose_after_plan_step(
        state: ResearchState,
    ) -> str:
        """
        每执行完一个 plan step 后检查：

        还有步骤：
            回 executor

        全部完成：
            final
        """

        if state["current_step"] < len(
            state["plan"]
        ):
            return "continue"

        return "finish"

    # ========================================================
    # 4. 创建 Graph
    # ========================================================

    builder = StateGraph(ResearchState)

    # -------------------------
    # 基础节点
    # -------------------------
    builder.add_node(
        "router",
        router_node,
    )

    builder.add_node(
        "direct_answer",
        direct_answer_node,
    )

    builder.add_node(
        "rewrite_query",
        rewrite_query_node,
    )

    builder.add_node(
        "local_rag",
        local_rag_node,
    )

    builder.add_node(
        "approval",
        approval_node,
    )

    builder.add_node(
        "paper_search",
        paper_search_node,
    )

    builder.add_node(
        "cancel",
        cancel_node,
    )

    # -------------------------
    # Planner 节点
    # -------------------------

    builder.add_node(
        "planner",
        planner_node,
    )

    builder.add_node(
        "executor",
        executor_node,
    )

    builder.add_node(
        "planner_paper_search",
        planner_paper_search_node,
    )

    builder.add_node(
        "planner_rag",
        planner_rag_node,
    )

    builder.add_node(
        "planner_reasoning",
        planner_reasoning_node,
    )

    builder.add_node(
        "planner_final",
        planner_final_node,
    )

    builder.add_node(
    "planner_paper_read",
    planner_paper_read_node,)


    # ========================================================
    # 5. Graph Edge
    # ========================================================

    # -------------------------
    # 入口
    # -------------------------

    builder.add_edge(
        START,
        "router",
    )

    # -------------------------
    # Router
    # -------------------------

    builder.add_conditional_edges(
        "router",
        choose_route,
        {
            "direct_answer": "direct_answer",
            "local_rag": "rewrite_query",
            "paper_search": "approval",
            "planner": "planner",
        },
    )

    # ========================================================
    # 普通路线
    # ========================================================

    builder.add_edge(
        "direct_answer",
        END,
    )

    # RAG
    builder.add_edge(
        "rewrite_query",
        "local_rag",
    )

    builder.add_edge(
        "local_rag",
        END,
    )

    # Paper Search
    builder.add_conditional_edges(
        "approval",
        choose_after_approval,
        {
            "paper_search": "paper_search",
            "cancel": "cancel",
        },
    )

    builder.add_edge(
        "paper_search",
        END,
    )

    builder.add_edge(
        "cancel",
        END,
    )

    # ========================================================
    # Planner 路线
    # ========================================================

    # Planner 生成计划
    builder.add_edge(
        "planner",
        "executor",
    )

    # Executor 判断当前步骤应该交给谁
    builder.add_conditional_edges(
        "executor",
        choose_executor_action,
        {
            "paper_search": "planner_paper_search",
             "paper_read": "planner_paper_read",
            "local_rag": "planner_rag",
            "reasoning": "planner_reasoning",
        },
    )

    # 每种执行节点完成后，
    # 都检查 plan 是否还有剩余步骤
    for node_name in [
        "planner_paper_search",
        "planner_paper_read",
        "planner_rag",
        "planner_reasoning",
    ]:
        builder.add_conditional_edges(
            node_name,
            choose_after_plan_step,
            {
                "continue": "executor",
                "finish": "planner_final",
            },
        )

    # 所有步骤执行完成
    builder.add_edge(
        "planner_final",
        END,
    )

    # ========================================================
    # 6. SQLite Checkpoint
    # ========================================================

    conn = sqlite3.connect(
        "data/checkpoints.sqlite",
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(conn)

    graph = builder.compile(
        checkpointer=checkpointer,
    )

    return graph