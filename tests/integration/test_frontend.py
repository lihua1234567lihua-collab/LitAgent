import json
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from langgraph.types import Command

from api import main as api_main


def test_homepage_serves_simple_chat_page():
    homepage = next(
        route
        for route in api_main.app.routes
        if getattr(route, "path", None) == "/"
        and "GET" in getattr(route, "methods", set())
    )

    response = homepage.endpoint()
    page_path = Path(response.path)
    html = page_path.read_text(encoding="utf-8")

    assert page_path.name == "index.html"
    assert "fetch('/chat'" in html
    assert "textarea" in html
    assert "answer" in html
    assert 'id="stop-button"' in html
    assert "AbortController" in html
    assert ".abort()" in html
    assert "external_search_approval" in html
    assert "window.confirm" in html
    assert "resume" in html
    assert 'id="new-chat-button"' in html
    assert 'id="conversation-list"' in html
    assert 'id="message-list"' in html
    assert "activeConversationId" in html
    assert "localStorage" in html
    assert "thread_id" in html
    assert "conversation.messages" in html
    assert "deleteConversation(conversation)" in html
    assert "deleteButton.setAttribute('role', 'menuitem')" in html
    assert "buildInterruptMessage(data.interrupt)" in html
    assert "interrupt.papers" in html
    assert "paper?.title" in html
    assert "data.answer || '当前没有返回回答。'" not in html
    assert "flex: 1 1 auto;" in html
    assert "scrollbar-width: thin;" in html
    assert "overflow-y: scroll" not in html
    assert "sidebar-collapse" not in html
    assert "fetch('/papers/upload'" in html
    assert "new FormData(paperUploadForm)" in html
    assert "renderUploadSuccess(data)" in html
    assert "navigator.clipboard.writeText" in html
    assert 'id="open-upload-modal-button"' in html
    assert '<dialog id="paper-upload-dialog"' in html
    assert "message.type === 'paper_upload_result'" in html
    assert "uploadConversationId" in html
    assert ".showModal()" in html


class ChatGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_returns_interrupt_payload(self):
        payload = {
            "type": "external_search_approval",
            "message": "Continue with external paper search?",
            "query": "find papers",
        }

        class InterruptGraph:
            async def ainvoke(self, *_args, **_kwargs):
                return {
                    "__interrupt__": [
                        type("Interrupt", (), {"value": payload})()
                    ]
                }

        async def fake_get_graph():
            return InterruptGraph()

        with patch.object(api_main, "get_graph", fake_get_graph):
            result = await api_main.chat(
                api_main.ChatRequest(message="find papers")
            )

        self.assertIn("thread_id", result)
        self.assertEqual(result["interrupt"], payload)

    async def test_chat_resume_uses_command(self):
        calls = []

        class ResumableGraph:
            async def ainvoke(self, value, **_kwargs):
                calls.append(value)
                return {"answer": "search completed"}

        async def fake_get_graph():
            return ResumableGraph()

        with patch.object(api_main, "get_graph", fake_get_graph):
            result = await api_main.chat(
                api_main.ChatRequest(
                    message="find papers",
                    thread_id="approval-thread",
                    resume=True,
                )
            )

        self.assertIsInstance(calls[0], Command)
        self.assertEqual(result["answer"], "search completed")

    async def test_openalex_rate_limit_returns_frontend_error(self):
        request = httpx.Request(
            "GET",
            "https://api.openalex.org/works",
        )
        response = httpx.Response(
            429,
            request=request,
            headers={"Retry-After": "30"},
        )
        error = httpx.HTTPStatusError(
            "rate limited",
            request=request,
            response=response,
        )

        class FailingGraph:
            async def ainvoke(self, *_args, **_kwargs):
                raise error

        async def fake_get_graph():
            return FailingGraph()

        with patch.object(api_main, "get_graph", fake_get_graph):
            result = await api_main.chat(
                api_main.ChatRequest(message="find papers")
            )

        self.assertEqual(result.status_code, 429)
        body = json.loads(result.body)
        self.assertTrue(body["detail"])
        self.assertEqual(body["retry_after"], "30")
