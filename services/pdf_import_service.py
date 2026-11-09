from pathlib import Path

from tools.pdf_parser import extract_pdf_text
from tools.knowledge_backend_client import add_paper_to_topic
from services.paper_ingest_service import ingest_paper


async def import_pdf(
    pdf_path: str | Path,
    topic_id: int,
    doi: str,
    title: str,
):
    # 1. 解析 PDF
    content = extract_pdf_text(Path(pdf_path))

    if not content or len(content.strip()) < 500:
        raise ValueError("PDF 全文解析失败或有效文本不足")

    # 2. 调用 Spring Boot，保存论文及 Topic 关联
    result = await add_paper_to_topic(
        topic_id=topic_id,
        doi=doi,
        title=title,
        pdf_path=str(Path(pdf_path).resolve()),
    )

    knowledge_paper_id = result["paperId"]

    # 3. 文本分块、向量化、存入 Chroma
    chunk_count = ingest_paper(
        content=content,
        knowledge_paper_id=knowledge_paper_id,
        doi=doi,
        title=title,
    )

    return {
        **result,
        "chunk_count": chunk_count,
    }