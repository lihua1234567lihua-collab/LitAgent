import asyncio
import os
import sys
import uuid

import aiosqlite
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agent.graph import build_research_graph


# =========================
# 1. 加载环境变量
# =========================

load_dotenv()

deepseek_api_key = os.getenv(
    "DEEPSEEK_API_KEY"
)


# =========================
# 2. 创建 LLM
# =========================

model = ChatOpenAI(
    model_name="deepseek-flash",
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com",
    reasoning_effort="none",
)

# =========================
# 4. thread_id
# =========================

def get_thread_id(existing_thread_id=None):
    if existing_thread_id:
        return existing_thread_id

    return str(uuid.uuid4())


# =========================
# 5. 异步主函数
# =========================

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # =========================
    # 3. 构建 LangGraph
    # =========================

    connection = await aiosqlite.connect("data/checkpoints.sqlite")
    try:
        checkpointer = AsyncSqliteSaver(connection)
        graph = build_research_graph(model, checkpointer=checkpointer)

        thread_id = get_thread_id()

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        print("当前 thread_id:", thread_id)

        initial_state = {
            "user_query": (
                "告诉我雷达传感器的机制"
            ),
            "trace": [],
            "messages": [],
            "step_results": [],
        }

        result = await graph.ainvoke(
            initial_state,
            config=config,
        )

        print("\n===== Final State =====")
        print(result)

        print("\n===== Plan =====")
        print(result.get("plan"))

        print("\n===== Current Step =====")
        print(result.get("current_step"))

        print("\n===== Step Results =====")
        print(result.get("step_results"))

        print("\n===== Step Action =====")
        print(result.get("step_action"))

    finally:
        await connection.close()


# =========================
# 6. 程序入口
# =========================

if __name__ == "__main__":
    asyncio.run(main())
