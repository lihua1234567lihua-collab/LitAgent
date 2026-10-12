from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from agent.graph import build_research_graph

import os


load_dotenv()


# 创建模型
model = ChatOpenAI(
    model_name="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    reasoning_effort="none",
)


# 创建 Graph
graph = build_research_graph(model)


# 这个 ID 后面恢复时必须完全一样
config = {
    "configurable": {
        "thread_id": "research-003"
    }
}


user_query = (
    "帮我找3篇关于 LiDAR tree crown segmentation 的论文"
)


initial_state = {
    "user_query": user_query,
    "trace": [],
    "messages": [
        HumanMessage(content=user_query)
    ]
}


# 开始执行
result = graph.invoke(
    initial_state,
    config=config,
)


print("\n===== 第一次运行结果 =====")
print(result)


# 查看当前保存状态
checkpoint = graph.get_state(config)

print("\n===== 当前 State =====")
print(checkpoint.values)

print("\n===== 下一节点 =====")
print(checkpoint.next)