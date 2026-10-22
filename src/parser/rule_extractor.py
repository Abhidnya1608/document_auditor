from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RuleExtractor:
    """Splits Rule PDF into 100% comprehensive, un-filtered policy chunks for vector matching."""

    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
        )

    def extract_rules_from_pdf(self, rule_pdf_path: str | Path) -> List[str]:
        """Loads Rule PDF and converts 100% of text blocks into testable search rules."""
        path = Path(rule_pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"Rule PDF not found at {path}")

        loader = PyPDFLoader(str(path))
        pages = loader.load()

        # Split entire policy into comprehensive chunks
        raw_chunks = self.text_splitter.split_documents(pages)

        # Filter out empty headers or page numbers
        rule_list = []
        for chunk in raw_chunks:
            text = chunk.page_content.strip()
            # Ignore tiny fragments like page headers/footers
            if len(text) > 30:
                rule_list.append(text)

        return rule_list