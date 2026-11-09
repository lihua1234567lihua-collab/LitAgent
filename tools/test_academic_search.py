import asyncio
import os
import shutil

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()


async def main():
    command = shutil.which("academic-mcp")

    client = MultiServerMCPClient(
        {
            "academic": {
                "transport": "stdio",
                "command": command,
                "args": [],
                "env": os.environ.copy(),
            }
        }
    )

    tools = await client.get_tools()

    paper_search = next(
        tool for tool in tools
        if tool.name == "paper_search"
    )

    result = await paper_search.ainvoke(
        {
            "query_list": [
                {
                    "searcher": "arxiv",
                    "query": "tree crown segmentation",
                    "max_results": 3,
                }
            ]
        }
    )

    print("RAW RESULT:")
    print(repr(result))


if __name__ == "__main__":
    asyncio.run(main())