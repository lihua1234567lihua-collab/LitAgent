import asyncio
import shutil
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import aiosqlite
from agent import graph as graph_module
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from services.code_reproduce_service import run_code_reproduce
from services.sandbox_service import DockerSandboxRunner


class FakeSandbox:
    def __init__(self, result=None):
        self.result = result or {
            "status": "success",
            "repository": "https://github.com/example/project",
            "project_type": "python",
            "steps": [
                {
                    "name": "clone",
                    "command": "git clone --depth 1 ...",
                    "exit_code": 0,
                }
            ],
            "executed_command": "python -m pytest -q tests/test_smoke.py",
            "exit_code": 0,
            "stdout": "ok",
            "stderr": "",
            "summary": "Smoke test passed.",
        }
        self.repositories = []

    async def run_repository_smoke_test(self, repository):
        self.repositories.append(repository)
        return self.result


class CodeReproduceServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_docker_unavailable_is_structured(self):
        with patch.object(shutil, "which", return_value=None):
            result = await DockerSandboxRunner().run_repository_smoke_test(
                "https://github.com/example/project"
            )

        self.assertEqual(result["status"], "sandbox_unavailable")
        self.assertIn("Docker", result["error"])

    async def test_code_reproduce_calls_injected_sandbox(self):
        sandbox = FakeSandbox()

        result = await run_code_reproduce(
            "Please smoke test https://github.com/example/project",
            sandbox=sandbox,
        )

        self.assertEqual(
            sandbox.repositories,
            ["https://github.com/example/project"],
        )
        self.assertEqual(result["status"], "success")

    async def test_code_reproduce_without_github_url_is_structured(self):
        sandbox = FakeSandbox()

        result = await run_code_reproduce("reproduce the code", sandbox=sandbox)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(sandbox.repositories, [])
        self.assertIn("GitHub", result["error"])

    async def test_failure_result_preserves_stderr(self):
        sandbox = FakeSandbox(
            {
                "status": "failed",
                "repository": "https://github.com/example/project",
                "project_type": "python",
                "steps": [],
                "executed_command": "python -m pytest -q tests/test_smoke.py",
                "exit_code": 1,
                "stdout": "",
                "stderr": "dependency installation failed",
                "summary": "Smoke test failed.",
            }
        )

        result = await run_code_reproduce(
            "https://github.com/example/project",
            sandbox=sandbox,
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("dependency installation failed", result["stderr"])


class GraphCodeReproduceTests(unittest.IsolatedAsyncioTestCase):
    class Model:
        def __init__(self, responses):
            self.responses = list(responses)

        def invoke(self, _prompt):
            return SimpleNamespace(content=self.responses.pop(0))

    async def _build_graph(self, model):
        connection = await aiosqlite.connect(":memory:")
        self.addAsyncCleanup(connection.close)
        with patch.object(
            graph_module,
            "create_router",
            lambda _model: SimpleNamespace(
                invoke=lambda _payload: SimpleNamespace(route="planner",paper_scope="none",reason="测试")
            ),
        ):
            return graph_module.build_research_graph(
                model,
                checkpointer=AsyncSqliteSaver(connection),
            )

    async def test_executor_routes_code_reproduce_and_advances_once(self):
        model = self.Model(
            [
                "SEARCH_QUERY: reproduce repository\n"
                "1. Run the repository smoke test",
                "code_reproduce",
                "final answer",
            ]
        )
        calls = []

        async def fake_reproduce(task):
            calls.append(task)
            return {
                "status": "success",
                "repository": "https://github.com/example/project",
                "project_type": "python",
                "steps": [{"name": "smoke", "exit_code": 0}],
                "executed_command": "python -m pytest -q",
                "exit_code": 0,
                "stdout": "ok",
                "stderr": "",
                "summary": "Smoke test passed.",
            }

        graph = await self._build_graph(model)
        with patch.object(graph_module, "run_code_reproduce", fake_reproduce):
            result = await graph.ainvoke(
                {
                    "user_query": "run https://github.com/example/project",
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                },
                config={"configurable": {"thread_id": "code-reproduce-success"}},
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["answer"], "final answer")
        self.assertTrue(result["step_validation"]["passed"])
        self.assertEqual(
            result["step_validation"]["source"],
            "deterministic",
        )
        self.assertIn('"status": "success"', result["step_results"][0])

    async def test_sandbox_failure_does_not_loop_or_crash(self):
        model = self.Model(
            [
                "SEARCH_QUERY: reproduce repository\n"
                "1. Run the repository smoke test",
                "code_reproduce",
                "final answer",
            ]
        )
        calls = []

        async def fake_reproduce(task):
            calls.append(task)
            return {
                "status": "sandbox_unavailable",
                "repository": "https://github.com/example/project",
                "steps": [],
                "stdout": "",
                "stderr": "Docker runtime is not available.",
                "summary": "Docker daemon is not available.",
            }

        graph = await self._build_graph(model)
        with patch.object(graph_module, "run_code_reproduce", fake_reproduce):
            result = await graph.ainvoke(
                {
                    "user_query": "run https://github.com/example/project",
                    "trace": [],
                    "messages": [],
                    "step_results": [],
                },
                config={"configurable": {"thread_id": "code-reproduce-failure"}},
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(result["current_step"], 0)
        self.assertNotIn("answer", result)
        self.assertEqual(result["step_results"], [])
        self.assertFalse(result["step_validation"]["passed"])


if __name__ == "__main__":
    unittest.main()
