from pathlib import Path

import numpy as np

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from rag.embeddings import EmbeddingModel


def load_documents(folder: str) -> list[Document]:
    documents = []

    for pattern in ("*.txt", "*.md"):
        for file_path in Path(folder).glob(pattern):

            text = file_path.read_text(
                encoding="utf-8"
            )

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": file_path.name
                    },
                )
            )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:

    # Markdown 标题层级
    headers_to_split_on = [
        ("#", "title"),
        ("##", "section"),
        ("###", "subsection"),
        ("####", "subsubsection"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,

        # 标题不要从正文中删掉
        # 这样标题本身也会参与 embedding
        strip_headers=False,
    )

    # 某个章节如果还是太长，
    # 再继续切成小块
    chunk_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    all_chunks = []

    for document in documents:

        # 第一步：
        # 根据 Markdown 标题切 section
        sections = markdown_splitter.split_text(
            document.page_content
        )

        # 把原论文的 source 信息加回来
        for section in sections:
            section.metadata.update(
                document.metadata
            )

        # 第二步：
        # 超长 section 继续切
        chunks = chunk_splitter.split_documents(
            sections
        )

        all_chunks.extend(chunks)

    return all_chunks

def rerank_chunks(query, chunks):
    query_words = set(query.lower().split())

    rescored = []

    for chunk in chunks:
        text = chunk.page_content.lower()

        keyword_hits = sum(
            1 for word in query_words
            if word in text
        )

        vector_score = chunk.metadata.get("score", 0.0)

        final_score = vector_score + 0.05 * keyword_hits

        chunk.metadata["rerank_score"] = final_score
        chunk.metadata["keyword_hits"] = keyword_hits

        rescored.append(chunk)

    rescored.sort(
        key=lambda x: x.metadata["rerank_score"],
        reverse=True
    )

    return rescored


class VectorRetriever:

    def __init__(
        self,
        chunks: list[Document],
    ):

        self.chunks = chunks

        self.embedding_model = EmbeddingModel()

        texts = [
            chunk.page_content
            for chunk in chunks
        ]

        print(
            f"正在为 {len(texts)} 个 chunks 创建 embeddings..."
        )

        self.chunk_embeddings = (
            self.embedding_model.embed_documents(
                texts
            )
        )

        print(
            "Embedding 创建完成。"
        )


    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[Document]:

        query_embedding = (
            self.embedding_model.embed_query(
                query
            )
        )

        scores = np.dot(
            self.chunk_embeddings,
            query_embedding,
        )

        ranked_indices = (
            np.argsort(scores)[::-1]
        )

        top_indices = ranked_indices[:top_k]

        results = []

        for index in top_indices:

            chunk = self.chunks[index]

            chunk.metadata["score"] = float(
                scores[index]
            )

            results.append(chunk)

        return results