'''把外部数据正式导入知识库：接收一篇论文->构造成document->切分chunk->embedding->写入向量库'''
from langchain_core.documents import Document

from rag.retriever import split_documents
from rag.vector_store import get_vector_store


def ingest_paper(
    content: str,
    knowledge_paper_id: int,
    doi: str | None = None,
    title: str | None = None,
):
    vector_store = get_vector_store()

    existing=vector_store.get(where={
        "knowledge_paper_id": knowledge_paper_id
    },
        limit=1,
    )

    if existing["ids"]:##论文去重
        return 0
    else:
        document = Document(
        page_content=content,
        metadata={
            "knowledge_paper_id": knowledge_paper_id,
            "doi": doi,
            "title": title,
        },
    )
        chunks = split_documents([document])
        vector_store.add_documents(chunks)
        return len(chunks)