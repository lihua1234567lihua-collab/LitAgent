from langchain.agents import create_agent

from tools.paper_search import search_papers


def search_papers_with_agent(
    user_query: str,
    model,
    debug: bool = True,
) -> str:

    agent = create_agent(
        model=model,
        tools=[search_papers],
        system_prompt="""
你是一个森林遥感科研助手。

当用户要求查找、搜索或推荐论文时，
必须使用 search_papers 工具。

只能根据工具返回的信息回答。
如果工具没有返回摘要或研究内容，
不要根据论文标题猜测具体方法或结论。
不要编造论文。
""",
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_query,
                }
            ]
        }
    )

    if debug:
        for message in result["messages"]:
            print("\n----------------")
            print(type(message).__name__)
            print(message.content)

            if (
                hasattr(message, "tool_calls")
                and message.tool_calls
            ):
                print(
                    "Tool Calls:",
                    message.tool_calls,
                )

    return result["messages"][-1].content