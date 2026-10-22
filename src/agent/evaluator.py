import time
from typing import List
from config.settings import settings
from src.agent.schemas import AuditFinding, AuditReport
from src.retriever.vector_store import VectorStoreManager
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

class DocumentAuditorEngine:
    def __init__(self, vector_manager: VectorStoreManager):
        self.vector_manager = vector_manager
        
        base_llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0,
            base_url = "https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
            timeout=30,
            max_retries=0
        )
        self.structured_llm = base_llm.with_structured_output(AuditFinding,
                                                              method="json_schema")

    
    def audit_single_rule(self, rule: str) -> AuditFinding:
        print("A: Starting retrieval...", flush=True)

        retrieved_docs = self.vector_manager.similarity_search(
        query=rule, k=3
    )

        print(f"B: Retrieval finished. Found {len(retrieved_docs)} docs.", flush=True)

        context_str = "\n\n".join(
        [
            f"[Page {doc.metadata.get('page', 'N/A')}]: {doc.page_content}"
            for doc in retrieved_docs
        ]
    )

        prompt = f"""You are a professional legal compliance auditor.
Evaluate whether the document context complies with the specified policy requirement.

RULE TO EVALUATE:
{rule}

RETRIEVED DOCUMENT CONTEXT:
{context_str}
"""

        print("C: Sending prompt to Gemini...", flush=True)

        result = self.structured_llm.invoke(prompt)

        print("D: Gemini response received.", flush=True)

        return result


    def run_full_audit(self, document_name: str, rule_list: List[str]) -> AuditReport:
        """Evaluates rules sequentially and reports timing."""
        audit_start = time.perf_counter()
        findings: List[AuditFinding] = []

        for i, rule in enumerate(rule_list, start=1):
            print(f"\nRule {i}/{len(rule_list)}")
            finding = self.audit_single_rule(rule)
            findings.append(finding)

            if i < len(rule_list):
                time.sleep(2.0)

        print(f"\nTotal audit time: {time.perf_counter() - audit_start:.2f}s")

        return AuditReport(
            document_name=document_name,
            total_rules_checked=len(rule_list),
            findings=findings,
        )
