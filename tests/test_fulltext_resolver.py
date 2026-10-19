from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch

from services import fulltext_resolver
from services import paper_read_service


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeModel:
    def __init__(self, decision: str):
        self.decision = decision
        self.calls = []

    def invoke(self, prompt: str):
        self.calls.append(prompt)
        return FakeResponse(self.decision)


class FulltextResolverTests(unittest.IsolatedAsyncioTestCase):
    def paper(self, **overrides):
        paper = {
            "title": "A paper",
            "abstract": "a" * 500,
            "source": "openalex",
            "paper_id": "W123",
        }
        paper.update(overrides)
        return paper

    async def test_sufficient_abstract_does_not_call_academic_mcp(self):
        mcp_read = AsyncMock()

        with patch.object(fulltext_resolver, "academic_read_paper", mcp_read):
            result = await fulltext_resolver.resolve_paper_content(
                self.paper(), "summarize the abstract", FakeModel("sufficient")
            )

        self.assertEqual(result["content_type"], "abstract")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["content"], "a" * 500)
        mcp_read.assert_not_awaited()

    async def test_insufficient_abstract_uses_academic_mcp(self):
        mcp_read = AsyncMock(return_value="full paper text")
        paper = self.paper(abstract="short")

        with patch.object(fulltext_resolver, "academic_read_paper", mcp_read):
            result = await fulltext_resolver.resolve_paper_content(
                paper, "extract the method", FakeModel("insufficient")
            )

        self.assertEqual(result["content_type"], "fulltext")
        self.assertEqual(result["content"], "full paper text")
        self.assertEqual(result["status"], "ready")
        mcp_read.assert_awaited_once_with(searcher="openalex", paper_id="W123")

    async def test_academic_mcp_failure_requests_fulltext(self):
        mcp_read = AsyncMock(side_effect=RuntimeError("paper unavailable"))

        with patch.object(fulltext_resolver, "academic_read_paper", mcp_read):
            result = await fulltext_resolver.resolve_paper_content(
                self.paper(abstract="short"), "extract the method", FakeModel("insufficient")
            )

        self.assertEqual(result["status"], "need_fulltext")
        self.assertIsNone(result["content"])
        self.assertIn("paper unavailable", result["error"])

    async def test_existing_local_pdf_is_used_before_academic_mcp(self):
        mcp_read = AsyncMock(side_effect=AssertionError("MCP must not be called"))
        with TemporaryDirectory() as directory:
            workspace = Path(directory)
            pdf_path = workspace / "A_paper.pdf"
            pdf_path.write_bytes(b"fake pdf")

            with patch.object(fulltext_resolver, "academic_read_paper", mcp_read), patch.object(
                fulltext_resolver,
                "_read_local_pdf_text",
                return_value="provided PDF text",
            ):
                result = await fulltext_resolver.resolve_paper_content(
                    self.paper(abstract="short"),
                    "extract the method",
                    FakeModel("insufficient"),
                    workspace_dir=workspace,
                )

        self.assertEqual(result["content_type"], "fulltext")
        self.assertEqual(result["content"], "provided PDF text")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["pdf_path"], str(pdf_path))
        mcp_read.assert_not_awaited()

    async def test_missing_academic_mcp_identifiers_requests_fulltext(self):
        mcp_read = AsyncMock()

        with patch.object(fulltext_resolver, "academic_read_paper", mcp_read):
            result = await fulltext_resolver.resolve_paper_content(
                self.paper(abstract="short", source=None, paper_id=None),
                "extract the method",
                FakeModel("insufficient"),
            )

        self.assertEqual(result["status"], "need_fulltext")
        mcp_read.assert_not_awaited()

    async def test_prepare_paper_read_owns_caches_analysis_and_missing_items(self):
        model = FakeModel("analysis")
        reader_calls = []

        def paper_reader(paper):
            reader_calls.append(paper)
            return {**paper, "abstract": "short"}

        async def resolver(paper, task, model, workspace_dir):
            if paper["title"] == "Needs PDF":
                return {
                    "paper": paper,
                    "task": task,
                    "status": "need_fulltext",
                    "content": None,
                }
            return {
                "paper": paper,
                "task": task,
                "status": "ready",
                "content_type": "abstract",
                "content": "cached content",
            }

        result = await paper_read_service.prepare_paper_read(
            selected_papers=[
                {"title": "Ready Paper", "openalex_id": "W1"},
                {
                    "title": "Needs PDF",
                    "doi": "10.1000/example",
                    "openalex_id": "W2",
                },
            ],
            task="extract method",
            model=model,
            paper_reader=paper_reader,
            resolver=resolver,
            thread_id="service-test",
        )

        self.assertEqual(len(reader_calls), 2)
        self.assertIn("W1", result["paper_contents"])
        self.assertEqual(len(result["paper_analyses"]), 1)
        self.assertEqual(result["missing"][0]["title"], "Needs PDF")
        self.assertIn(
            "data/workspace/service-test",
            result["missing"][0]["pdf_target_path"].replace("\\", "/"),
        )

