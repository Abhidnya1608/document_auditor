from typing import List
from langchain_chroma import Chroma 
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import settings

class VectorStoreManager:


    """Manages chunk embedding , vector search indexing"""

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model = settings.EMBEDDING_MODEL,
            google_api_key = settings.GEMINI_API_KEY
        )
        self.vector_store = None

    def create_index(self , chunks: List[Document]) -> Chroma:
        """Embeds text chunks amd indexes thme in memory Qdrant database"""

        if not chunks:
            raise ValueError("Empty chunks")

        self.vector_store = Chroma.from_documents(
            documents = chunks,
            embedding = self.embeddings ,
            # location = ":memory:",
            collection_name = settings.CHROMA_COLLECTION_NAME
        )
        return self.vector_store

    def similarity_search(
            self , query: str , k : int = settings.TOP_K_RETRIEVAL
    )-> List[Document]:
        if self.vector_store is None:
            raise RuntimeError(
                "Vector store index not created yet"
            )

        return self.vector_store.similarity_search(query , k=k)

