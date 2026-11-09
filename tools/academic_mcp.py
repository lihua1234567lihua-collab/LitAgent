import os
import shutil
import json
from typing import Any
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()

def create_academic_mcp_client():
    """
    创建 Academic MCP 客户端。
    使用 stdio 直接启动本地 academic-mcp 子进程。
    """
    command = shutil.which("academic-mcp")

    if not command:
        raise RuntimeError(
            "找不到 academic-mcp，请确认已经安装"
        )

    return MultiServerMCPClient(
        {
            "academic": {
                "transport": "stdio",
                "command": command,
                "args": [],
                "env": os.environ.copy(),
            }
        }
    )

async def get_academic_tool(tool_name: str):
    client = create_academic_mcp_client()

    tools = await client.get_tools()

    for tool in tools:
        if tool.name == tool_name:
            return tool

    raise ValueError(
        f"找不到 Academic MCP Tool: {tool_name}"
    )

def _extract_text(result) -> str:
    """
    把 MCP ContentBlock 返回值转换成普通文本。
    """

    if isinstance(result, list):
        texts = []

        for item in result:
            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                texts.append(
                    item.get("text", "")
                )

        return "\n".join(texts).strip()

    return str(result).strip()

async def read_paper(
    searcher: str,
    paper_id: str,
) -> str:
    """
    通过 academic-mcp 获取并读取论文全文。

    例如：
    searcher="arxiv"
    paper_id="1706.03762"

    或：
    searcher="semantic"
    paper_id="DOI:10.xxxx/xxxx"
    """

    tool = await get_academic_tool(
        "paper_read"
    )

    try:
        result = await asyncio.wait_for(
            tool.ainvoke(
                {
                    "searcher": searcher,
                    "paper_id": paper_id,
                }
            ),
            timeout=60,
        )
    except asyncio.TimeoutError:
        raise RuntimeError(
            f"Academic MCP 读取论文超时: {searcher}/{paper_id}"
        )

    text = _extract_text(result)

    if not text:
        raise RuntimeError(
            f"论文读取失败: "
            f"{searcher}/{paper_id}"
        )

    return text



def _parse_search_result(result: Any) -> list[dict]:
    """
    把 academic-mcp 的 paper_search 返回值
    转换成 list[dict]。
    """

    # MCP 通常返回 ContentBlock 列表
    if isinstance(result, list):
        texts = []

        for item in result:
            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                texts.append(
                    item.get("text", "")
                )

        text = "\n".join(texts).strip()

    else:
        text = str(result).strip()

    if not text:
        return []

    # paper_search 的文本通常是 JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"无法解析 Academic MCP 搜索结果：{text[:500]}"
        ) from exc

    # 兼容直接返回 list
    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    # 兼容外层套一层 results / papers
    if isinstance(data, dict):

        for key in (
            "results",
            "papers",
            "data",
        ):
            value = data.get(key)

            if isinstance(value, list):
                return [
                    item
                    for item in value
                    if isinstance(item, dict)
                ]

    raise RuntimeError(
        f"未知的 Academic MCP 搜索结果格式：{type(data)}"
    )


async def search_papers(
    query: str,
    max_results: int = 10,
    searcher: str | None = None,
    year: str | None = None,
) -> list[dict]:
    """
    通过 academic-mcp 搜索论文。

    searcher=None：
        让 academic-mcp 从所有启用的数据源搜索。

    searcher="arxiv"：
        只搜索 arXiv。

    searcher="semantic"：
        搜索 Semantic Scholar，并可使用 year 参数。
    """

    tool = await get_academic_tool(
        "paper_search"
    )

    paper_query = {
        "query": query,
        "max_results": max_results,
    }

    if searcher:
        paper_query["searcher"] = searcher

    # academic-mcp 当前只有 Semantic Scholar
    # 明确支持 year 参数
    if year:
        if searcher != "semantic":
            raise ValueError(
                "year 参数目前只适用于 "
                "searcher='semantic'"
            )

        paper_query["year"] = year

    result = await tool.ainvoke(
        {
            "query_list": [
                paper_query
            ]
        }
    )

    papers = _parse_search_result(
        result
    )

    return papers
