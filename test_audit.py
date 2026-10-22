# from pathlib import Path
# from src.parser.loader import DocumentParser
# from src.parser.rule_extractor import RuleExtractor
# from src.retriever.vector_store import VectorStoreManager
# from src.agent.evaluator import DocumentAuditorEngine

# def test_pipeline():
#     print("🚀 Starting Local Core Pipeline Test...")

#     # 1. Point to your local PDF files (Update these paths to match your actual test files)
#     rule_pdf_path = Path("data/sample_policy.pdf")      # Replace with your path
#     contract_pdf_path = Path("data/sample_contract.pdf")  # Replace with your path

#     if not rule_pdf_path.exists() or not contract_pdf_path.exists():
#         print(f"❌ Please place a sample policy PDF at '{rule_pdf_path}' and a contract PDF at '{contract_pdf_path}' to test.")
#         return

#     # 2. Extract Policy Rules (Using larger 1500 chunk size for fewer API calls)
#     print("\n✂️ Step 1: Extracting rules from Policy PDF...")
#     rule_extractor = RuleExtractor(chunk_size=1500, chunk_overlap=200)
#     extracted_rules = rule_extractor.extract_rules_from_pdf(rule_pdf_path)
#     print(f"✅ Success! Extracted {len(extracted_rules)} policy chunks.")
#     for i, rule in enumerate(extracted_rules[:3], 1):
#         print(f"   - Rule {i}: {rule[:100]}...")

#     # 3. Parse Target Contract
#     print("\n📖 Step 2: Parsing Target Contract PDF...")
#     parser = DocumentParser()
#     contract_chunks = parser.process_document(contract_pdf_path)
#     print(f"✅ Success! Parsed contract into {len(contract_chunks)} chunks.")

#     # 4. Create Vector Store Index
#     print("\n🗄️ Step 3: Building Chroma DB Vector Index...")
#     vector_mgr = VectorStoreManager()
#     vector_mgr.create_index(contract_chunks)
#     print("✅ Success! Vector store initialized.")

#     # 5. Run Gemini Evaluation Agent
#     print("\n🤖 Step 4: Running Gemini Audit Evaluation...")
#     auditor = DocumentAuditorEngine(vector_manager=vector_mgr)
    
#     # Let's test just the first 2 rules first to verify speed and prevent rate limits
#     test_rules = extracted_rules[:2] 
#     print(f"ℹ️ Testing audit on the first {len(test_rules)} rule(s)...")

#     report = auditor.run_full_audit(
#         document_name=contract_pdf_path.name,
#         rule_list=test_rules
#     )

#     print("\n🎯 Audit Completed Successfully!")
#     print(f"Total Rules Checked: {report.total_rules_checked}")
#     for idx, finding in enumerate(report.findings, 1):
#         print(f"\nFinding {idx}:")
#         print(f"  Status: {finding.status}")
#         print(f"  Page: {finding.page_number}")
#         print(f"  Evidence: {finding.evidence[:100]}...")
#         print(f"  Reasoning: {finding.reasoning[:150]}...")

# if __name__ == "__main__":
#     test_pipeline()

from config.settings import settings
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model=settings.LLM_MODEL,
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0,
    timeout=20,
    max_retries=0,
)

response = llm.invoke("Reply with exactly: OK")
print(response.content)