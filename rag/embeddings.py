import os

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.embeddings import Embeddings


load_dotenv()


class EmbeddingModel(Embeddings):

    def __init__(self):
        api_key = os.getenv("SILICONFLOW_API_KEY")

        if not api_key:
            raise ValueError(
                "没有找到 SILICONFLOW_API_KEY"
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1",
        )

        self.model = "BAAI/bge-m3"


    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        embeddings = [
            item.embedding
            for item in response.data
        ]

        vectors = np.array(
            embeddings,
            dtype=np.float32,
        )

        norms = np.linalg.norm(
            vectors,
            axis=1,
            keepdims=True,
        )

        vectors = vectors / norms

        return vectors.tolist()


    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        vector = np.array(
            response.data[0].embedding,
            dtype=np.float32,
        )

        vector = vector / np.linalg.norm(vector)

        return vector.tolist()