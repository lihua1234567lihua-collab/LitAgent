from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from dotenv import load_dotenv

from agent.graph import build_research_graph

import os


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
# 3. 构建 LangGraph
# =========================

graph = build_research_graph(
    model
)


# =========================
# 4. 配置 Thread
# =========================
# thread_id 用于让 Checkpointer
# 知道这些 State 属于同一个任务 / 会话

config = {
    "configurable": {
        "thread_id": "research-001"
    }
}


# =========================
# 5. 用户问题
# =========================

user_query = (
    "帮我找3篇关于 LiDAR tree crown segmentation 的论文"
)


# =========================
# 6. 创建初始 State
# =========================

initial_state = {
    "user_query": user_query,

    "trace": [],

    "messages": [
        HumanMessage(
            content=user_query
        )
    ]
}


# =========================
# 7. 第一次执行 Graph
# =========================

result = graph.invoke(
    initial_state,
    config=config,
)


# =========================
# 8. 处理 Interrupt
# =========================
# 如果 Graph 在 approval_node 中暂停，
# result 中会出现 __interrupt__

if "__interrupt__" in result:

    interrupt_info = result["__interrupt__"][0]

    print("\n===== Graph 已暂停 =====")
    print(interrupt_info.value)

    user_input = input(
        "\n是否继续？(y/n): "
    )

    approved = (
        user_input.strip().lower() == "y"
    )

    # 从刚才的 Checkpoint 恢复
    result = graph.invoke(
        Command(
            resume=approved
        ),
        config=config,
    )


# =========================
# 9. 输出最终结果
# =========================

print("\n===== Final State =====")
print(result)


print("\n===== Final Answer =====")
print(
    result.get(
        "answer",
        "没有生成最终答案。"
    )
)