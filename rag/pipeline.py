from rag.vector_store import get_vector_store
from rag.reranker import Reranker
from rag.query_rewriter import rewrite_query


def answer_with_rag(
    user_query: str,
    model,
    search_query: str | None = None,
    debug: bool = True,
) -> str:

    # =========================
    # 1. Query Rewrite
    # =========================

    if search_query is None:
        search_query = rewrite_query(
        model,
        user_query,
    )

    if debug:
        print("原始问题:", user_query)
        print("检索 Query:", search_query)


    # =========================
    # 2. Chroma 粗召回
    # =========================

    vector_store = get_vector_store()

    search_results = (
        vector_store.similarity_search_with_score(
            query=search_query,
            k=50,
        )
    )

    candidates = []

    for document, distance in search_results:

        document.metadata["distance"] = float(
            distance
        )

        candidates.append(document)


    # =========================
    # 3. Reranker 精排
    # =========================

    reranker = Reranker()

    results = reranker.rerank(
        query=search_query,
        chunks=candidates,
        top_n=5,
    )


    # =========================
    # 4. Debug 查看检索结果
    # =========================

    # if debug:

    #     for i, chunk in enumerate(
    #         results,
    #         1,
    #     ):

            # print(f"\n--- Result {i} ---")

            # print(
            #     "Source:",
            #     chunk.metadata.get("source")
            # )

            # print(
            #     "Chroma Distance:",
            #     chunk.metadata.get("distance")
            # )

            # print(
            #     "Rerank Score:",
            #     chunk.metadata.get("rerank_score")
            # )

            # print(
            #     chunk.page_content[:800]
            # )


    # =========================
    # 5. 构造 Context
    # =========================

    context = "\n\n".join(
        [
            f"[Source: {chunk.metadata.get('source')}]\n"
            f"{chunk.page_content}"
            for chunk in results
        ]
    )


    # =========================
    # 6. Generation
    # =========================

    prompt = f"""
你是一个森林遥感科研助手。

请只根据下面提供的论文证据回答用户问题。

要求：
1. 不要使用证据之外的信息。
2. 如果证据不足，请明确说明。
3. 优先使用能够直接回答问题的方法描述。
4. 回答简洁、准确。

论文证据：

{context}

用户问题：

{user_query}
"""

    response = model.invoke(
        [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return response.content