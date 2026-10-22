from pathlib import Path
from src.parser.loader import DocumentParser
from src.parser.rule_extractor import RuleExtractor
from src.retriever.vector_store import VectorStoreManager
from src.agent.evaluator import DocumentAuditorEngine

def test_local_pipeline():
    print("🚀 Starting Local Core Pipeline Test...")

    # 1. Point to your sample PDF files (Make sure these files exist in a 'data/' folder or update paths)
    rule_pdf_path = Path("data/sample_policy.pdf")
    contract_pdf_path = Path("data/sample_contract.pdf")

    if not rule_pdf_path.exists() or not contract_pdf_path.exists():
        print(f"\n❌ Sample PDFs not found!")
        print(f"Please create a 'data/' folder and place a sample policy PDF at '{rule_pdf_path}'")
        print(f"and a contract PDF at '{contract_pdf_path}' before running this test.")
        return

    # 2. Extract rules from Policy PDF
    print("\n✂️ Step 1: Extracting rules from Policy PDF...")
    rule_extractor = RuleExtractor(chunk_size=1500, chunk_overlap=200)
    extracted_rules = rule_extractor.extract_rules_from_pdf(rule_pdf_path)
    print(f"✅ Extracted {len(extracted_rules)} rule chunk(s).")

    # 3. Parse Target Contract PDF
    print("\n📖 Step 2: Parsing Target Contract PDF...")
    parser = DocumentParser()
    contract_chunks = parser.process_document(contract_pdf_path)
    print(f"✅ Parsed contract into {len(contract_chunks)} chunk(s).")

    # 4. Create Vector Store Index (Using Gemini Embeddings)
    print("\n🗄️ Step 3: Building Chroma DB Vector Index (Gemini Embeddings)...")
    vector_mgr = VectorStoreManager()
    vector_mgr.create_index(contract_chunks)
    print("✅ Vector index built successfully.")

    # 5. Run Groq Audit Engine
    print("\n🤖 Step 4: Running Groq Evaluation Engine...")
    auditor = DocumentAuditorEngine(vector_manager=vector_mgr)
    
    # Test on just the first rule to check speed and response structure
    test_rules = extracted_rules[:1] 
    print(f"ℹ️ Testing audit on {len(test_rules)} sample rule...")

    report = auditor.run_full_audit(
        document_name=contract_pdf_path.name,
        rule_list=test_rules
    )

    print("\n🎯 Pipeline Test Completed Successfully!")
    print(f"Document Name: {report.document_name}")
    print(f"Total Rules Checked: {report.total_rules_checked}")
    
    for idx, finding in enumerate(report.findings, 1):
        print(f"\n--- Finding {idx} ---")
        print(f"Status: {finding.status}")
        print(f"Page Number: {finding.page_number}")
        print(f"Evidence: {finding.evidence}")
        print(f"Reasoning: {finding.reasoning}")

if __name__ == "__main__":
    test_local_pipeline()