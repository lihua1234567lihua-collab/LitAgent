from langchain_chroma import Chroma

from rag.embeddings import EmbeddingModel


PERSIST_DIRECTORY = "data/chroma_db"

COLLECTION_NAME = "forest_papers"

##加载 EmbeddingModel→ 连接 data/chroma_db→ 使用 forest_papers collection→ 返回 vector_store

def get_vector_store():

    embedding_model = EmbeddingModel()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIRECTORY,
    )

    return vector_store