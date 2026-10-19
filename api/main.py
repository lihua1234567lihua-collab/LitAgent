from contextlib import asynccontextmanager
from pathlib import Path
import os
import uuid
import json
import aiosqlite
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
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

graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph

    connection = await aiosqlite.connect("data/checkpoints.sqlite")
    try:
        checkpointer = AsyncSqliteSaver(connection)
        graph = build_research_graph(model, checkpointer=checkpointer)
        app.state.graph = graph
        app.state.checkpoint_connection = connection
        yield
    finally:
        graph = None
        await connection.close()


async def get_graph():
    """Build the async-checkpointed graph once for the FastAPI process."""

    if graph is None:
        raise RuntimeError("FastAPI lifespan has not initialized the graph")
    return graph


# =========================
# 4. 创建 FastAPI
# =========================

app = FastAPI(lifespan=lifespan)

FRONTEND_PATH = Path(__file__).resolve().parent.parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(FRONTEND_PATH)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    resume: bool | None = None


# =========================
# 5. Chat Gateway
# =========================

@app.post("/chat")
async def chat(request: ChatRequest):

    # 没有 thread_id → 新任务
    # 有 thread_id → 继续原任务
    thread_id = request.thread_id or str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    graph_input = (
        Command(resume=request.resume)
        if request.resume is not None
        else {
            "user_query": request.message,
            "trace": [],
            "messages": [],
        }
    )

    active_graph = await get_graph()
    try:
        result = await active_graph.ainvoke(
            graph_input,
            config=config,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 429:
            raise

        retry_after = exc.response.headers.get("retry-after")
        return JSONResponse(
            status_code=429,
            content={
                "detail": "论文搜索服务暂时达到速率限制，请稍后重试。",
                "retry_after": retry_after,
            },
        )

    interrupts = result.get("__interrupt__") or []
    interrupt_payload = (
        getattr(interrupts[0], "value", None)
        if interrupts
        else None
    )

    return {
        "thread_id": thread_id,
        "answer": result.get("answer"),
        "interrupt": interrupt_payload,
    }

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):

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

    async def event_generator():

        active_graph = await get_graph()

        # 先把 thread_id 告诉前端
        yield f"data: {json.dumps({
            'type': 'thread',
            'thread_id': thread_id
        }, ensure_ascii=False)}\n\n"

        # LangGraph 每执行完一个节点，
        # 就会产生一次 update
        async for chunk in active_graph.astream(
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
