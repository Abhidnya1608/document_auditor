from pathlib import Path
from src.parser.loader import DocumentParser
from src.retriever.vector_store import VectorStoreManager

pdf_path = Path("data/uploads/sample.pdf")

if not pdf_path.exists():
    print("FIle not found")

else:
    print("1.Parsing pdf...")
    parser = DocumentParser()
    chunks = parser.process_document(pdf_path)

    print("2.Generating Embeddings")
    vector_mgr = VectorStoreManager()
    vector_mgr.create_index(chunks)
    print("Index created")

    print("3. Testing Retrival Search")
    query = "what is machine learning"
    results = vector_mgr.similarity_search(query , k=2)

    print(f" Query : '{query}' ")
    for i,doc in enumerate(results , 1):
        print(f"Tope result {i} (Page {doc.metadata.get('page_number')})")
        print(f"Text: {doc.page_content[:200]}")