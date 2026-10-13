import os
import shutil

from langchain_mcp_adapters.client import MultiServerMCPClient
from pathlib import Path
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()

def create_paper_mcp_client():
    """
    创建 Paper Search MCP 客户端。
    使用 stdio 直接启动本地 paper-search-mcp 子进程。
    """

    command = shutil.which("paper-search-mcp")

    if not command:
        raise RuntimeError(
            "找不到 paper-search-mcp，请确认已通过 uv tool 安装"
        )

    print("Paper MCP command:", command)

    return MultiServerMCPClient(
        {
            "paper_search": {
                "transport": "stdio",
                "command": command,
                "args": [],
                "env": os.environ.copy(),
            }
        }
    )


async def get_paper_mcp_tools():
    client = create_paper_mcp_client()

    tools = await client.get_tools()

    return tools


async def get_paper_mcp_tool(tool_name: str):
    tools = await get_paper_mcp_tools()

    for tool in tools:
        if tool.name == tool_name:
            return tool

    raise ValueError(
        f"找不到 MCP Tool: {tool_name}"
    )

async def download_paper_with_fallback(
    doi: str,
    title: str = "",
    source: str = "crossref",
    paper_id: str | None = None,
):
    """
    通过 Paper Search MCP 尝试从多个开放来源获取论文全文。
    """

    tool = await get_paper_mcp_tool(
        "download_with_fallback"
    )

    save_path = Path("data/papers").resolve()
    save_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Crossref 场景下 DOI 就可以作为 paper_id
    if paper_id is None:
        paper_id = doi

    result = await tool.ainvoke(
        {
            "source": source,
            "paper_id": paper_id,
            "doi": doi,
            "title": title,
            "save_path": str(save_path),

            # 只使用开放获取渠道
            "use_scihub": False,
        }
    )

    return result