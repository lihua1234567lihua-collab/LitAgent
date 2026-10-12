from langchain_chroma import Chroma

from rag.embeddings import EmbeddingModel


PERSIST_DIRECTORY = "data/chroma_db"

COLLECTION_NAME = "forest_papers"


def get_vector_store():

    embedding_model = EmbeddingModel()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIRECTORY,
    )

    return vector_store