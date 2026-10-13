import asyncio

from tools.paper_search_mcp import (
    download_paper_with_fallback,
)


async def main():

    result = await download_paper_with_fallback(
        source="arxiv",
        paper_id="1706.03762",
        doi="",
        title="Attention Is All You Need",
    )

    print("\n===== Download Result =====")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())