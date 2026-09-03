from pathlib import Path
from src.parser.loader import DocumentParser
from src.retriever.vector_store import VectorStoreManager
from src.agent.evaluator import DocumentAuditorEngine

pdf_path = Path("data/uploads/sample.pdf")

if not pdf_path.exists():
    print("File not found")

else:
    print("1. Ingesting pdf")
    parser = DocumentParser()
    chunks = parser.process_document(pdf_path)

    print("2. Indexing in chroma db")
    vector_mgr = VectorStoreManager()
    vector_mgr.create_index(chunks)

    print("3.Initializing Audit Engine")
    auditor = DocumentAuditorEngine(vector_manager=vector_mgr)

    test_rules = [
        "The aggreement must specifiy a writtem termination notice period",
        "Payment must be completed within 30 days of invoice receipt"
    ]

    print("\n4. Running Audit")
    report = auditor.run_full_audit(
        document_name=pdf_path.name , 
        rule_list=test_rules
    )

    print(f"\n Auditing Report : {report.document_name} ==== ")
    for idx , finding in enumerate(report.findings , 1):
        print(f"\n Rule {idx}: {finding.rule}")
        print(f" Status : {finding.status}")
        print(f" Evidence Quote: \"{finding.evidence}\"")
        print(f"• Reasoning: {finding.reasoning}")