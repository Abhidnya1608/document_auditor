from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings 


class DocumentParser:
    """Handles loading PDFs and spliiting them into chunks with metadata"""

    def __init__(
            self,
            chunk_size: int = settings.CHUNK_SIZE,
            chunk_overlap: int = settings.CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n" , "\n" , " " , ""]
        )

    def load_pdf(self,file_path: str | Path) -> List[Document]:
        """Loads a PDF and extracts text page by page"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Pdf file not found at: {path}")

        loader = PyPDFLoader(str(path))
        raw_pages = loader.load()
        return raw_pages

    def process_document(self , file_path : str | Path) -> List[Document]:

        raw_pages = self.load_pdf(str(file_path))

        chunks = self.text_splitter.split_documents(raw_pages)

        for chunk in chunks:
            chunk.metadata["source_file"] = Path(file_path).name
            chunk.metadata["page_number"] = chunk.metadata.get("page" , 0) + 1

        return chunks


    
