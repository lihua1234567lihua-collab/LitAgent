from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from dotenv import load_dotenv
from agent.graph import build_research_graph
import uuid
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

def get_thread_id(existing_thread_id=None):
    if existing_thread_id:
        return existing_thread_id

    return str(uuid.uuid4())

thread_id = get_thread_id()

config = {
    "configurable": {
        "thread_id": thread_id
    }
}
print("当前thread_id",thread_id)
initial_state = {
    "user_query": "帮我找3篇 LiDAR tree crown segmentation 的论文，并比较它们的方法、数据集和优缺点",
    "trace": [],
    "messages": [],
}

result = graph.invoke(
    initial_state,
    config=config,
)

print("===== Final State =====")
print(result)

print("\n===== Plan =====")
print(result.get("plan"))

print("\n===== Current Step =====")
print(result.get("current_step"))

print("\n===== Trace =====")
print(result.get("trace"))