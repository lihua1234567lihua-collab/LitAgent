import os
import uuid
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from fastapi.responses import StreamingResponse
from agent.graph import build_research_graph


# =========================
# 1. 环境变量
# =========================

load_dotenv()

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")


# =========================
# 2. 创建模型
# =========================

model = ChatOpenAI(
    model_name="deepseek-flash",
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com",
    reasoning_effort="none",
)


# =========================
# 3. 构建 Agent Graph
# =========================

graph = build_research_graph(model)


# =========================
# 4. 创建 FastAPI
# =========================

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


# =========================
# 5. Chat Gateway
# =========================

@app.post("/chat")
def chat(request: ChatRequest):

    # 没有 thread_id → 新任务
    # 有 thread_id → 继续原任务
    thread_id = request.thread_id or str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "user_query": request.message,
        "trace": [],
        "messages": [],
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    return {
        "thread_id": thread_id,
        "answer": result.get("answer"),
    }

@app.post("/chat/stream")
def chat_stream(request: ChatRequest):

    thread_id = request.thread_id or str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "user_query": request.message,
        "trace": [],
        "messages": [],
    }

    def event_generator():

        # 先把 thread_id 告诉前端
        yield f"data: {json.dumps({
            'type': 'thread',
            'thread_id': thread_id
        }, ensure_ascii=False)}\n\n"

        # LangGraph 每执行完一个节点，
        # 就会产生一次 update
        for chunk in graph.stream(
            initial_state,
            config=config,
            stream_mode="updates",
        ):

            for node_name, update in chunk.items():

                # 告诉前端当前执行到了哪个节点
                yield f"data: {json.dumps({
                    'type': 'node',
                    'node': node_name
                }, ensure_ascii=False)}\n\n"

                # 如果这个节点产生了最终 answer
                if isinstance(update, dict) and update.get("answer"):

                    yield f"data: {json.dumps({
                        'type': 'answer',
                        'content': update['answer']
                    }, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({
            'type': 'done'
        })}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )