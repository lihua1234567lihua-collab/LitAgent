from langchain_openai import ChatOpenAI
from langgraph.types import Command
from dotenv import load_dotenv

from agent.graph import build_research_graph

import os


load_dotenv()


# 重新创建模型
model = ChatOpenAI(
    model_name="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    reasoning_effort="none",
)


# 重新创建 Graph
# 它会重新连接同一个 checkpoints.sqlite
graph = build_research_graph(model)


# 必须和第一个程序完全相同
config = {
    "configurable": {
        "thread_id": "research-003"
    }
}


# 先读取之前保存的 Checkpoint
checkpoint = graph.get_state(config)

print("===== 恢复前的 State =====")
print(checkpoint.values)

print("\n===== 下一节点 =====")
print(checkpoint.next)


# 用户批准，恢复执行
result = graph.invoke(
    Command(resume=True),
    config=config,
)


print("\n===== 恢复后的 Final State =====")
print(result)