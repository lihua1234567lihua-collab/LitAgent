from contextlib import asynccontextmanager
from pathlib import Path
import os
import uuid
import json
import aiosqlite
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from agent.graph import build_research_graph
from langchain_core.messages import HumanMessage
from langgraph.types import Command, Overwrite
from services.pdf_import_service import import_pdf
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
    latest_uploaded_paper_id: int | None = None
    user_id:int

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "papers"

@app.post("/papers/upload")
async def upload_paper(
    file: UploadFile = File(...),
    topic_id: int = Form(...),
    title: str = Form(...),
    doi: str = Form(...)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # 使用 UUID 命名，避免文件名冲突
    pdf_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.pdf"

    size = 0

    try:
        with pdf_path.open("wb") as f:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)

                if size > 20 * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF 文件不能超过 20MB"
                    )

                if size == len(chunk) and not chunk.startswith(b"%PDF-"):
                    raise HTTPException(
                        status_code=400,
                        detail="文件不是有效的 PDF 格式"
                    )

                f.write(chunk)

    except Exception:
        pdf_path.unlink(missing_ok=True)
        raise

    finally:
        await file.close()

    # PDF 已保存，开始解析和收藏
    try:
        result = await import_pdf(
            pdf_path=pdf_path,
            topic_id=topic_id,
            doi=doi,
            title=title,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    return {
        "status": "collected",
        "filename": file.filename,
        "pdf_path": str(pdf_path),
        **result
    }
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
            "user_id":request.user_id,
            "latest_uploaded_paper_id": request.latest_uploaded_paper_id,
            "messages": [HumanMessage(content=request.message)],

            # 新任务：重置 Task State
            "route": None,
            "search_query": None,
            "search_results": [],
            "selected_papers": [],
            "paper_contents": Overwrite({}),
            "paper_analyses": Overwrite({}),
            "plan": [],
            "retry_count": 0,
            "current_step": 0,
            "step_action": None,
            "step_output": None,
            "step_validation": None,
            "step_results": Overwrite([]),
            "answer": None,
            "pending_fulltext": [],

            "trace": [],
        }
)

    active_graph = await get_graph()
    try:
        result = await active_graph.ainvoke(
            graph_input,
            config=config,
        )
        print("\n===== TASK STATE CHECK =====")
        print("route:", result.get("route"))
        print("plan:", result.get("plan"))
        print("current_step:", result.get("current_step"))
        print("search_results:", result.get("search_results"))
        print("step_results:", result.get("step_results"))
        print("paper_analyses:", result.get("paper_analyses"))

        print("\nmessages:")
        for msg in result.get("messages", []):
            print(type(msg).__name__, ":", msg.content[:100])

        print("============================\n")
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
    print("===== INTERRUPT =====")
    print(interrupt_payload)
    print("=====================")

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
        "messages": [HumanMessage(content=request.message)],
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
