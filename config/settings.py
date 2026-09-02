import os
from pathlib import Path
from dotenv import load_dotenv

#Defines root directory of project
BASE_DIR = Path(__file__).resolve().parent.parent

#Load environment variables from .env files
load_dotenv(BASE_DIR / ".env")

class Settings:

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY" , "")


    #PRoject file paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    RULES_DIR: Path = DATA_DIR / "rules"


    #Rag details
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    #LLM
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.0

    #Vector db
    CHROMA_COLLECTION_NAME: str = "document_audit_chunks"
    TOP_K_RETRIEVAL: int = 3

    def validate(self)-> None:
        """Verifies essential configurations"""
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "API key missing"
            )
        self.UPLOADS_DIR.mkdir(parents=True , exist_ok = True)
        self.RULES_DIR.mkdir(parents=True , exist_ok = True)

settings = Settings()