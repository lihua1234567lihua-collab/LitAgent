import asyncio

from tools.paper_search_mcp import get_paper_mcp_tools


async def main():
    tools = await get_paper_mcp_tools()

    print("\n===== MCP Tools =====")

    for tool in tools:
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Args Schema: {tool.args_schema}")


if __name__ == "__main__":
    asyncio.run(main())