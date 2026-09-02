from pathlib import Path
from src.parser.loader import DocumentParser

pdf_path = Path("data/uploads/sample.pdf")

if not pdf_path.exists():
    print("File not found")

else:
    parser = DocumentParser()
    chunks = parser.process_document(pdf_path)
    print("Successfully processed PDF")
    print(f"Total chunks:{len(chunks)}")
    print("\nSample chunk")
    print(f"Content:{chunks[0].page_content[:200]}...")
    print(f"Metadata:{chunks[0].metadata}")