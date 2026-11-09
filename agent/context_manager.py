''''对话上下文管理器：提取最近的历史消息，供Router和LLM使用'''
from typing import Any, Mapping
from langchain_core.messages import AnyMessage


def get_recent_messages(
    state: Mapping[str, Any],
    limit: int = 6,
) -> list[AnyMessage]:
    """Return the most recent conversation messages."""

    messages = state.get("messages", [])

    if limit <= 0:
        return []

    return list(messages[-limit:])

def get_router_history(
    state: Mapping[str, Any],
    limit: int = 4,
) -> list[AnyMessage]:
    """Return previous messages for routing, excluding current user message."""

    messages = list(state.get("messages", []))

    if not messages:
        return []

    # API 入口已经把当前 user_query 作为 HumanMessage 放进 messages
    current_query = state.get("user_query")

    if messages[-1].content == current_query:
        messages = messages[:-1]

    return messages[-limit:]