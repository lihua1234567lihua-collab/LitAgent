import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from services.local_pdf_resolver import resolve_paper_content


class FulltextResolverTests(unittest.IsolatedAsyncioTestCase):

    async def test_existing_pdf(self):
        with TemporaryDirectory() as directory:
            pdf = Path(directory) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.4")

            with patch(
                "services.local_pdf_resolver.extract_pdf_text",
                return_value="Example paper content",
            ):
                result = await resolve_paper_content(
                    paper={"title": "paper", "pdf_path": str(pdf)},
                    task="read paper",
                )

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["content_type"], "fulltext")
        self.assertEqual(result["content"], "Example paper content")

    async def test_missing_pdf(self):
        with TemporaryDirectory() as directory:
            result = await resolve_paper_content(
                paper={"title": "paper"},
                task="read paper",
                workspace_dir=directory,
            )

        self.assertEqual(result["status"], "need_fulltext")
        self.assertIsNone(result["content"])

    async def test_unreadable_pdf(self):
        with TemporaryDirectory() as directory:
            pdf = Path(directory) / "paper.pdf"
            pdf.write_bytes(b"%PDF-1.4")

            with patch(
                "services.local_pdf_resolver.extract_pdf_text",
                return_value=None,
            ):
                result = await resolve_paper_content(
                    paper={"title": "paper", "pdf_path": str(pdf)},
                    task="read paper",
                )

        self.assertEqual(result["status"], "need_fulltext")
        self.assertIsNone(result["content"])