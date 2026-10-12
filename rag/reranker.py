import os

import httpx
from dotenv import load_dotenv
from langchain_core.documents import Document


load_dotenv()


class Reranker:

    def __init__(self):
        self.api_key = os.getenv("SILICONFLOW_API_KEY")

        if not self.api_key:
            raise ValueError(
                "没有找到 SILICONFLOW_API_KEY"
            )

        self.url = "https://api.siliconflow.cn/v1/rerank"

        self.model = "BAAI/bge-reranker-v2-m3"

    def rerank(
        self,
        query: str,
        chunks: list[Document],
        top_n: int = 3,
    ) -> list[Document]:

        documents = [
            chunk.page_content
            for chunk in chunks
        ]

        payload = {
            "model": self.model,
            "query": query,
            "documents": documents,
            "top_n": top_n,
            "return_documents": False,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = httpx.post(
            self.url,
            json=payload,
            headers=headers,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        reranked_chunks = []

        for result in data["results"]:

            index = result["index"]

            chunk = chunks[index]

            chunk.metadata["rerank_score"] = (
                result["relevance_score"]
            )

            reranked_chunks.append(chunk)

        return reranked_chunks