from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

from agent.graph import build_research_graph


load_dotenv()

model = ChatOpenAI(
    model_name="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    reasoning_effort="none",
)

graph = build_research_graph(model)

config = {
    "configurable": {
        "thread_id": "research-001"
    }
}

checkpoint = graph.get_state(config)

print("===== 从 SQLite 读取的 State =====")
print(checkpoint.values)

print("\n下一节点：")
print(checkpoint.next)