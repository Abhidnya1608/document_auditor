from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from config.settings import settings
from src.agent.prompts import AUDITOR_SYSTEM_PROMPT
from src.agent.schemas import AuditFinding , AuditReport
from src.retriever.vector_store import VectorStoreManager


class DocumentAuditorEngine:

    def __init__(self , vector_manager: VectorStoreManager):
        self.vector_manager = vector_manager

        base_llm = ChatGoogleGenerativeAI(
            model = settings.LLM_MODEL,
            temperature = settings.LLM_TEMPERATURE,
            google_api_key = settings.GEMINI_API_KEY,
        )
        self.structured_llm = base_llm.with_structured_output(AuditFinding)


    def format_context(self , chunks: List[Document]) -> str:
        context_blocks = []
        for chunk in chunks:
            page = chunk.metadata.get("page_number" , "Unknown")
            context_blocks.append(f"[Page {page}] \n {chunk.page_content}")
        return "\n\n---\n\n".join(context_blocks)


    def audit_single_rule(self, rule:str) -> AuditFinding:
        """Audits a single rule against indexed doc"""

        relevante_chunks = self.vector_manager.similarity_search(query = rule , k = settings.TOP_K_RETRIEVAL)

        if not relevante_chunks:
            return AuditFinding(
                rule = rule ,
                status = "NEEDS REVIEW",
                evidence= "No relevant text found in document",
                reasoning="The vector search found zero matching paragraphs in the uploaded file.",
                page_number=0
            )

        formatted_context = self.format_context(relevante_chunks)

        prompt = AUDITOR_SYSTEM_PROMPT.format(rule=rule , context = formatted_context)

        finding: AuditFinding = self.structured_llm.invoke(prompt)
        return finding

    def run_full_audit(
            self , document_name : str , rule_list : List[str]
    ) -> AuditReport:
        """Runs the audit engine accross a batch of compilance rules and returns a full report"""
        findings = List[AuditFinding]

        for rule in rule_list:
            finding = self.audit_single_rule(rule)
            findings.append(finding)

        return AuditReport(
            document_name = document_name,
            total_rules_checked = len(rule_list),
            findings = findings
        )