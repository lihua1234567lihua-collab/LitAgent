from typing import Any

from tools.knowledge_backend_client import (
    get_topic_papers,
    get_user_papers,
)
from rag.pipeline import answer_with_rag


def _answer_scoped_question(
    papers: list[dict[str, Any]],
    user_query: str,
    model,
    empty_message: str,
    **rag_options,
) -> str:
    """在指定论文集合内执行 RAG 问答。"""

    # 提取论文 ID，并去重
    knowledge_paper_ids = list(dict.fromkeys(
        paper["id"]
        for paper in papers
        if paper.get("id") is not None
    ))

    if not knowledge_paper_ids:
        return empty_message

    return answer_with_rag(
        user_query=user_query,
        model=model,
        knowledge_paper_ids=knowledge_paper_ids,
        **rag_options,
    )


async def answer_topic_question(
    topic_id: int,
    user_query: str,
    model,
) -> str:
    """检索指定 Topic 下的论文。"""

    papers = await get_topic_papers(topic_id)

    return _answer_scoped_question(
        papers=papers,
        user_query=user_query,
        model=model,
        empty_message="当前 Topic 下还没有收藏任何论文，无法进行知识库检索。",
    )


async def answer_user_library_question(
    user_id: int,
    user_query: str,
    model,
) -> str:
    """检索指定用户收藏的论文。"""

    papers = await get_user_papers(user_id)

    return _answer_scoped_question(
        papers=papers,
        user_query=user_query,
        model=model,
        empty_message="当前用户的论文库为空，暂无可检索的论文。",
        debug=False,
    )


async def answer_uploaded_paper_question(
    user_id: int,
    paper_id: int,
    user_query: str,
    model,
) -> str:
    """只检索当前用户有权访问的指定论文。"""

    # 1. 获取用户收藏的论文
    papers = await get_user_papers(user_id)

    # 2. 找到指定论文，并检查是否属于当前用户
    target_papers = [
        paper for paper in papers
        if paper.get("id") == paper_id
    ]

    if not target_papers:
        return "当前论文不在你的论文库中，无法进行检索。"

    # 3. 只检索这篇论文
    return _answer_scoped_question(
        papers=target_papers,
        user_query=user_query,
        model=model,
        empty_message="指定论文不存在，无法进行检索。",
        debug=False,
    )