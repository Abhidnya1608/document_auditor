from pathlib import Path
from src.parser.loader import DocumentParser
from src.retriever.vector_store import VectorStoreManager
from src.agent.evaluator import DocumentAuditorEngine

pdf_path = Path("data/uploads/sample.pdf")

if not pdf_path.exists():
    print("⚠️ Please make sure 'sample.pdf' exists in 'data/uploads/'.")
else:
    print("1. Ingesting PDF...")
    parser = DocumentParser()
    chunks = parser.process_document(pdf_path)

    print("2. Indexing in Chroma DB...")
    vector_mgr = VectorStoreManager()
    vector_mgr.create_index(chunks)

    print("3. Initializing Audit Engine...")
    auditor = DocumentAuditorEngine(vector_manager=vector_mgr)

    test_rules = [
        "The agreement must specify a written termination notice period.",
        "Payment must be completed within 30 days of invoice receipt."
    ]

    print("\n4. Running Audit...")
    report = auditor.run_full_audit(
        document_name=pdf_path.name,
        rule_list=test_rules
    )

    print(f"\n================ AUDIT REPORT: {report.document_name} ================")
    for idx, finding in enumerate(report.findings, 1):
        print(f"\nRule {idx}: {finding.rule}")
        print(f"• Status: {finding.status}")
        print(f"• Page Number: {finding.page_number}")
        print(f"• Evidence Quote: \"{finding.evidence}\"")
        print(f"• Reasoning: {finding.reasoning}")