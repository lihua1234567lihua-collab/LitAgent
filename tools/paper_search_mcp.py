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

def _get_mcp_text(result) -> str:
    if isinstance(result, list):
        parts = []

        for item in result:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))

        return "\n".join(parts)

    return str(result)

async def download_paper_with_fallback(
    doi: str,
    save_path: str | Path,
    title: str = "",
    source: str = "crossref",
    paper_id: str | None = None,
):
    """
    通过 Paper Search MCP 尝试从多个开放来源获取论文全文。
    返回统一格式：
    {
        "success": bool,
        "pdf_path": str | None,
        "error": str | None,
    }
    """

    tool = await get_paper_mcp_tool(
        "download_with_fallback"
    )

    save_path = Path(save_path).resolve()
    save_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    if paper_id is None:
        paper_id = doi

    # 调用前记录目录中已有的 PDF
    before_files = {
        p.resolve(): p.stat().st_mtime_ns
        for p in save_path.glob("*.pdf")
    }

    result = await tool.ainvoke(
        {
            "source": source,
            "paper_id": paper_id,
            "doi": doi,
            "title": title,
            "save_path": str(save_path),
            "use_scihub": False,
        }
    )

    text = _get_mcp_text(result)

    # 调用后重新检查 PDF
    candidate_files = []

    for pdf_path in save_path.glob("*.pdf"):
        resolved_path = pdf_path.resolve()

        # 新文件，或者原文件发生了变化
        if (
            resolved_path not in before_files
            or pdf_path.stat().st_mtime_ns
            != before_files[resolved_path]
        ):
            candidate_files.append(pdf_path)

    # 验证是不是真的 PDF
    for pdf_path in candidate_files:
        try:
            if pdf_path.stat().st_size == 0:
                continue

            with pdf_path.open("rb") as f:
                if f.read(4) != b"%PDF":
                    continue

            return {
                "success": True,
                "pdf_path": str(pdf_path.resolve()),
                "error": None,
            }

        except OSError:
            continue

    # 没发现有效 PDF
    return {
        "success": False,
        "pdf_path": None,
        "error": text,
    }