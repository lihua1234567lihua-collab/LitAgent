from rag.retriever import (
    load_documents,
    split_documents,
)

from rag.vector_store import (
    get_vector_store,
)


# =========================
# 1. 加载论文
# =========================

documents = load_documents(
    "data/papers"
)

print(
    "论文数量：",
    len(documents)
)


# =========================
# 2. Chunking
# =========================

chunks = split_documents(
    documents
)

print(
    "Chunk 数量：",
    len(chunks)
)


# =========================
# 3. 打开 Chroma
# =========================

vector_store = get_vector_store()


# =========================
# 4. 检查是否已经建库
# =========================

existing = vector_store.get(
    limit=1
)

if existing["ids"]:

    print(
        "Chroma 中已经存在数据，跳过建库。"
    )

else:

    print(
        "开始创建 Embedding 并写入 Chroma..."
    )

    vector_store.add_documents(
        documents=chunks
    )

    print(
        "向量库创建完成。"
    )