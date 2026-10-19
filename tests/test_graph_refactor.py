import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiosqlite
from agent import graph as graph_module
from langgraph.types import Command
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from services import fulltext_resolver


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeModel:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []

    def invoke(self, prompt):
        self.calls.append(prompt)
        if self.responses:
            return FakeResponse(self.responses.pop(0))
        return FakeResponse("analysis")


class FakeRouter:
    def __init__(self, route="planner"):
        self.route = route

    def invoke(self, payload):
        return SimpleNamespace(route=self.route)


class FakeSearchTool:
    def __init__(self, papers):
        self.papers = papers
        self.calls = []

    def invoke(self, payload):
        self.calls.append(payload)
        return self.papers


class GraphRefactorTests(unittest.IsolatedAsyncioTestCase):
    async def build_graph(self, model=None, route="planner"):
        connection = await aiosqlite.connect(":memory:")
        with patch.object(
            graph_module,
            "create_router",
            lambda _model: FakeRouter(route),
        ):
            graph = graph_module.build_research_graph(
                model or FakeModel(),
                checkpointer=AsyncSqliteSaver(connection),
            )
        self.addAsyncCleanup(connection.close)
        return graph

    def test_state_is_minimal_and_explicit(self):
        annotations = graph_module.ResearchState.__annotations__

        self.assertIn("search_query", annotations)
        self.assertIn("search_results", annotations)
        self.assertIn("paper_contents", annotations)
        self.assertIn("paper_analyses", annotations)
        self.assertIn("step_output", annotations)
        self.assertIn("step_validation", annotations)
        self.assertNotIn("status", annotations)
        self.assertEqual(list(annotations).count("search_query"), 1)

    def test_planner_returns_plan_without_search_query(self):
        model = FakeModel(
            [
                "SEARCH_QUERY: should be ignored\n"
                "1. Search papers\n"
                "2. Compare methods"
            ]
        )

        with patch.object(
            graph_module,
            "create_router",
            lambda _model: FakeRouter(),
        ):
            handlers = graph_module.create_node_handlers(model)
            update = handlers["planner"](
                {
                    "user_query": "find and compare papers",
                    "trace": [],
                }
            )

        self.assertEqual(update["plan"], ["Search papers", "Compare methods"])
        self.assertEqual(update["current_step"], 0)
        self.assertNotIn("search_query", update)

    def test_paper_search_output_is_sent_to_validator(self):
        search = FakeSearchTool(
            [
                {"title": "Paper A", "openalex_id": "W1"},
                {"title": "Paper B", "openalex_id": "W2"},
            ]
        )

        state = {
            "user_query": "find papers",
            "search_query": "find papers",
            "plan": ["Search papers"],
            "current_step": 0,
            "step_results": [],
            "trace": [],
        }

        captured = {}

        def fake_validate(step_goal, search_results):
            captured["step_goal"] = step_goal
            captured["search_results"] = search_results
            return {
                "passed": True,
                "reason": "valid",
                "failed_constraints": [],
            }

        with patch.object(graph_module, "search_papers", search), patch.object(
            graph_module,
            "create_router",
            lambda _model: FakeRouter(),
        ):
            handlers = graph_module.create_node_handlers(FakeModel())
            search_update = handlers["paper_search"](state)

        with patch.object(
            graph_module,
            "validate_paper_search",
            side_effect=fake_validate,
        ):
            validation_update = handlers["validator"](
                {**state, **search_update}
            )

        self.assertEqual(captured["step_goal"], "Search papers")
        self.assertEqual(
            captured["search_results"],
            search_update["step_output"]["search_results"],
        )

        self.assertEqual(search_update["step_output"]["action"], "paper_search")
        self.assertNotIn("current_step", search_update)
        self.assertNotIn("step_results", search_update)

        self.assertEqual(validation_update["current_step"], 1)
        self.assertIn("step_results", validation_update)
        self.assertTrue(validation_update["step_validation"]["passed"])


    def test_validator_failure_keeps_current_step_and_rejects_result(self):
        state = {
            "user_query": "find papers",
            "plan": ["Search papers"],
            "current_step": 0,
            "step_output": {
                "action": "paper_search",
                "search_results": [
                    {"title": "Paper A", "openalex_id": "W1"},
                ],
                "summary": "one result",
            },
            "step_results": [],
            "trace": [],
        }

        failed_validation = {
            "passed": False,
            "reason": "not enough papers",
            "failed_constraints": [
                {
                    "type": "paper_count",
                    "required": 3,
                    "actual": 1,
                }
            ],
        }

        with patch.object(
            graph_module,
            "create_router",
            lambda _model: FakeRouter(),
        ):
            handlers = graph_module.create_node_handlers(FakeModel())

        with patch.object(
            graph_module,
            "validate_paper_search",
            return_value=failed_validation,
        ):
            update = handlers["validator"](state)

        self.assertFalse(update["step_validation"]["passed"])
        self.assertNotIn("current_step", update)
        self.assertNotIn("step_results", update)
        self.assertEqual(state["current_step"], 0)

    async def test_compiled_graph_routes_search_through_validator(self):
        model = FakeModel(
            [
                "1. Search papers",
                "paper_search",
                "final answer",
            ]
        )
        search = FakeSearchTool(
            [
                {"title": "Paper A", "openalex_id": "W1"},
                {"title": "Paper B", "openalex_id": "W2"},
            ]
        )
        validation = {
            "passed": True,
            "reason": "valid",
            "failed_constraints": [],
        }

        with patch.object(
            graph_module,
            "search_papers",
            search,
        ), patch.object(
            graph_module,
            "validate_paper_search",
            return_value=validation,
        ):
            graph = await self.build_graph(model=model)
            result = await graph.ainvoke(
                {
                    "user_query": "find papers",
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                },
                config={"configurable": {"thread_id": "validator-route"}},
            )

        self.assertEqual(len(search.calls), 1)
        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["answer"], "final answer")
        self.assertEqual(len(result["step_results"]), 1)
        self.assertIn("paper_search", result["trace"])
        self.assertIn("validator", result["trace"])

    async def test_graph_registers_only_reusable_capability_nodes(self):
        graph = await self.build_graph()
        nodes = set(graph.get_graph().nodes)
        expected = {
            "router",
            "direct_answer",
            "rewrite_query",
            "rag",
            "approval",
            "paper_search",
            "cancel",
            "planner",
            "executor",
            "paper_read",
            "reasoning",
            "final_answer",
            "validator",
        }

        self.assertTrue(expected <= nodes)
        self.assertFalse(
            {
                "planner_paper_search",
                "planner_paper_read",
                "planner_rag",
                "planner_reasoning",
                "planner_final",
                "paper_search_step",
            }
            & nodes
        )

    def test_paper_search_reuses_cached_results(self):
        model = FakeModel()
        search = FakeSearchTool(
            [
                {"title": "Paper A", "openalex_id": "W1"},
                {"title": "Paper B", "openalex_id": "W2"},
            ]
        )
        state = {
            "user_query": "tree crown segmentation",
            "route": "planner",
            "search_query": "tree crown segmentation",
            "plan": ["Search papers"],
            "current_step": 0,
            "trace": [],
            "step_results": [],
        }

        with patch.object(graph_module, "search_papers", search), patch.object(
            graph_module,
            "create_router",
            lambda _model: FakeRouter(),
        ):
            handlers = graph_module.create_node_handlers(model)
            first_update = handlers["paper_search"](state)
            second_state = {**state, **first_update, "current_step": 0}
            second_update = handlers["paper_search"](second_state)

        self.assertEqual(len(search.calls), 1)
        self.assertEqual(first_update["search_results"], second_update["search_results"])
        self.assertEqual(second_update["selected_papers"], first_update["selected_papers"])

    async def test_paper_read_caches_content_and_analysis(self):
        model = FakeModel()
        read_calls = []
        resolve_calls = []

        def fake_read(paper):
            read_calls.append(paper)
            return {**paper, "abstract": "A sufficiently long abstract."}

        async def fake_resolve(paper, task, model, workspace_dir):
            resolve_calls.append((paper, task))
            return {
                "paper": paper,
                "task": task,
                "content_type": "abstract",
                "content": paper["abstract"],
                "status": "ready",
            }

        state = {
            "user_query": "compare methods",
            "route": "planner",
            "plan": ["Extract method, dataset, advantages and limitations"],
            "current_step": 0,
            "selected_papers": [{"title": "Paper A", "openalex_id": "W1"}],
            "trace": [],
            "step_results": [],
        }

        with patch.object(graph_module, "read_paper", fake_read), patch.object(
            graph_module, "resolve_paper_content", fake_resolve
        ), patch.object(
            graph_module,
            "create_router",
            lambda _model: FakeRouter(),
        ):
            handlers = graph_module.create_node_handlers(model)
            first_update = await handlers["paper_read"](state)
            second_state = {**state, **first_update, "current_step": 0}
            second_update = await handlers["paper_read"](second_state)

        self.assertEqual(len(read_calls), 1)
        self.assertEqual(len(resolve_calls), 1)
        self.assertEqual(len(model.calls), 1)
        self.assertEqual(second_update["paper_contents"], first_update["paper_contents"])
        self.assertEqual(second_update["paper_analyses"], first_update["paper_analyses"])

    async def test_paper_read_flow_uses_validator_before_advancing(self):
        model = FakeModel(
            [
                "1. Read the selected papers",
                "paper_read",
                "final answer",
            ]
        )
        prepared = {
            "paper_contents": {
                "W1": {
                    "status": "ready",
                    "content_type": "abstract",
                    "content": "paper content",
                }
            },
            "paper_analyses": {
                "W1": {
                    "analysis": "structured analysis",
                }
            },
            "missing": [],
            "summary": "Read 1 papers and cached reusable analyses.",
        }

        with patch.object(
            graph_module,
            "prepare_paper_read",
            AsyncMock(return_value=prepared),
        ):
            graph = await self.build_graph(model=model)
            result = await graph.ainvoke(
                {
                    "user_query": "read the selected papers",
                    "selected_papers": [
                        {"title": "Paper A", "openalex_id": "W1"},
                    ],
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                },
                config={
                    "configurable": {
                        "thread_id": "paper-read-validator",
                    }
                },
            )

        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["answer"], "final answer")
        self.assertTrue(result["step_validation"]["passed"])
        self.assertIn("paper_read", result["trace"])
        self.assertIn("validator", result["trace"])

    async def test_reasoning_flow_uses_validator_before_advancing(self):
        model = FakeModel(
            [
                "1. Compare the papers",
                "reasoning",
                "reasoning result",
                "final answer",
            ]
        )

        graph = await self.build_graph(model=model)
        result = await graph.ainvoke(
            {
                "user_query": "compare the papers",
                "trace": [],
                "messages": [],
                "step_results": [],
            },
            config={
                "configurable": {
                    "thread_id": "reasoning-validator",
                }
            },
        )

        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["answer"], "final answer")
        self.assertTrue(result["step_validation"]["passed"])
        self.assertEqual(
            result["step_validation"]["source"],
            "deterministic",
        )
        self.assertIn("reasoning", result["trace"])
        self.assertIn("validator", result["trace"])

    async def test_missing_fulltext_interrupts_at_paper_read(self):
        model = FakeModel(
            [
                "SEARCH_QUERY: tree crown segmentation\n1. Read the selected papers",
                "paper_read",
            ]
        )

        with patch.object(
            graph_module,
            "read_paper",
            lambda paper: {**paper, "abstract": ""},
        ), patch.object(
            graph_module,
            "resolve_paper_content",
            AsyncMock(return_value={"status": "need_fulltext"}),
        ):
            graph = await self.build_graph(model=model)
            config = {"configurable": {"thread_id": "test-thread"}}
            result = await graph.ainvoke(
                {
                    "user_query": "read this paper",
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                    "selected_papers": [
                        {
                            "title": "Paper A",
                            "doi": "10.1000/example",
                            "openalex_id": "W1",
                        }
                    ],
                },
                config=config,
            )

        self.assertIn("__interrupt__", result)
        payload = result["__interrupt__"][0].value
        self.assertEqual(payload["type"], "fulltext_required")
        self.assertEqual(payload["papers"][0]["title"], "Paper A")
        self.assertEqual(payload["papers"][0]["doi"], "10.1000/example")
        self.assertIn(
            "data/workspace/test-thread",
            payload["papers"][0]["pdf_target_path"].replace("\\", "/"),
        )
        snapshot = await graph.aget_state(config)
        self.assertNotIn("executor", snapshot.next)

    async def test_resume_uses_user_pdf_without_repeating_academic_mcp(self):
        model = FakeModel(
            [
                "SEARCH_QUERY: read the paper\n1. Read the selected paper",
                "paper_read",
            ]
        )
        mcp_read = AsyncMock(side_effect=RuntimeError("fulltext unavailable"))

        def fake_read(paper):
            return {**paper, "abstract": "", "source": "arxiv", "paper_id": "W1"}

        with patch.object(graph_module, "read_paper", fake_read), patch.object(
            fulltext_resolver, "academic_read_paper", mcp_read
        ), patch.object(
            fulltext_resolver,
            "_read_local_pdf_text",
            return_value="provided PDF text",
        ):
            graph = await self.build_graph(model=model)
            config = {"configurable": {"thread_id": "resume-test"}}
            initial = await graph.ainvoke(
                {
                    "user_query": "read the paper",
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                    "selected_papers": [
                        {
                            "title": "Paper A",
                            "openalex_id": "W1",
                            "source": "arxiv",
                            "paper_id": "W1",
                        }
                    ],
                },
                config=config,
            )
            self.assertIn("__interrupt__", initial)

            target = Path("data") / "workspace" / "resume-test" / "Paper_A.pdf"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"user supplied pdf")
            try:
                resumed = await graph.ainvoke(Command(resume=True), config=config)
            finally:
                target.unlink(missing_ok=True)

        self.assertNotIn("__interrupt__", resumed)
        self.assertEqual(resumed["current_step"], 1)
        self.assertEqual(mcp_read.await_count, 1)
        content = resumed["paper_contents"]["W1"]
        self.assertEqual(content["content"], "provided PDF text")
        self.assertEqual(content["content_type"], "fulltext")

    async def test_fastapi_can_import_new_graph(self):
        graph = await self.build_graph(route="direct_answer")
        self.assertTrue(graph.get_graph().nodes["router"])

    async def test_planner_loop_advances_once_per_completed_step(self):
        model = FakeModel(
            [
                "SEARCH_QUERY: tree crown segmentation\n"
                "1. Search papers\n"
                "2. Compare the papers",
                "paper_search",
                "reasoning",
                "comparison result",
                "final answer",
            ]
        )
        search = FakeSearchTool(
            [{"title": "Paper A", "openalex_id": "W1"}]
        )

        with patch.object(
            graph_module,
            "search_papers",
            search,
        ):
            graph = await self.build_graph(model=model)
            result = await graph.ainvoke(
                {
                    "user_query": "find and compare papers",
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                },
                config={"configurable": {"thread_id": "loop-test"}},
            )

        self.assertEqual(result["current_step"], 2)
        self.assertEqual(len(search.calls), 1)
        self.assertEqual(result["answer"], "final answer")
        self.assertEqual(result["trace"].count("executor"), 2)

    async def test_paper_search_flow_uses_real_validator(self):
        model = FakeModel(
            [
                "1. Search papers",
                "paper_search",
                "final answer",
            ]
        )

        search = FakeSearchTool(
            [
                {"title": "Paper A", "openalex_id": "W1"},
                {"title": "Paper B", "openalex_id": "W2"},
            ]
        )

        with patch.object(
            graph_module,
            "search_papers",
            search,
        ):
            graph = await self.build_graph(model=model)

            result = await graph.ainvoke(
                {
                    "user_query": "find papers",
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                },
                config={
                    "configurable": {
                        "thread_id": "real-validator-test",
                    }
                },
            )

        self.assertEqual(len(search.calls), 1)
        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["answer"], "final answer")

        self.assertTrue(result["step_validation"]["passed"])
        self.assertEqual(
            result["step_validation"]["source"],
            "deterministic",
        )

        self.assertEqual(len(result["step_results"]), 1)
        self.assertIn("paper_search", result["trace"])
        self.assertIn("validator", result["trace"])




if __name__ == "__main__":
    unittest.main()
