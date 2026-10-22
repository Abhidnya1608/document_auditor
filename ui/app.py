import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tempfile
import streamlit as st
from config.settings import settings
from src.parser.loader import DocumentParser
from src.parser.rule_extractor import RuleExtractor
from src.retriever.vector_store import VectorStoreManager
from src.agent.evaluator import DocumentAuditorEngine
from src.utils.reporter import generate_pdf_report

st.set_page_config(
    page_title="Dual-PDF RAG Auditor",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Dual-PDF RAG Document Auditor")
st.caption(
    "Cross-examine 100% of a Policy/Rule PDF against a Target Contract PDF using Chroma DB Vector Search & Gemini LLM."
)

st.divider()

col_rule_pdf, col_contract_pdf = st.columns(2)

with col_rule_pdf:
    st.subheader("1. Policy / Rule PDF")
    uploaded_rule_pdf = st.file_uploader(
        "Upload Policy or Regulation PDF", 
        type=["pdf"], 
        key="rule_pdf"
    )

with col_contract_pdf:
    st.subheader("2. Target Contract PDF")
    uploaded_contract_pdf = st.file_uploader(
        "Upload Contract or Document to Audit", 
        type=["pdf"], 
        key="contract_pdf"
    )

st.divider()

if uploaded_rule_pdf and uploaded_contract_pdf:
    if st.button("🚀 Run Dual-PDF Audit", type="primary", use_container_width=True):
        with st.status("Executing Dual-PDF RAG Pipeline...", expanded=True) as status:
            
            # Save uploaded Rule PDF to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_rule:
                tmp_rule.write(uploaded_rule_pdf.read())
                rule_pdf_path = Path(tmp_rule.name)

            # Save uploaded Contract PDF to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_contract:
                tmp_contract.write(uploaded_contract_pdf.read())
                contract_pdf_path = Path(tmp_contract.name)

            # 1. Chunk 100% of Policy PDF (Zero Missed Rules)
            st.write("📋 Chunking 100% of Policy PDF for complete vector search coverage...")
            rule_extractor = RuleExtractor()
            extracted_rules = rule_extractor.extract_rules_from_pdf(rule_pdf_path)
            st.info(f"Loaded **{len(extracted_rules)} policy blocks** to cross-examine against Chroma DB.")

            # 2. Parse Target Contract PDF into page-aware chunks
            st.write("📄 Parsing Target Contract PDF into vector chunks...")
            parser = DocumentParser()
            contract_chunks = parser.process_document(contract_pdf_path)

            # 3. Create Chroma DB Vector Index for Contract
            st.write("🔍 Embedding contract chunks into Chroma DB...")
            vector_mgr = VectorStoreManager()
            vector_mgr.create_index(contract_chunks)

            # 4. Run RAG Audit (Policy Chunk vs Contract Index)
            st.write("🤖 Evaluating policy chunks against contract text with Gemini...")
            auditor = DocumentAuditorEngine(vector_manager=vector_mgr)
            report = auditor.run_full_audit(
                document_name=uploaded_contract_pdf.name,
                rule_list=extracted_rules
            )

            st.session_state["latest_dual_report"] = report
            st.session_state["extracted_rules"] = extracted_rules
            status.update(label="Dual-PDF Audit Complete!", state="complete", expanded=False)

# Display Findings & Download Report
if "latest_dual_report" in st.session_state:
    report = st.session_state["latest_dual_report"]
    extracted_rules = st.session_state.get("extracted_rules", [])

    st.subheader(f"Audit Summary for `{report.document_name}`")
    
    # Export Download Button
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as export_tmp:
        export_path = generate_pdf_report(report, export_tmp.name)
        with open(export_path, "rb") as f:
            st.download_button(
                label="📥 Download Full Audit PDF Report",
                data=f.read(),
                file_name=f"Audit_Report_{report.document_name}.pdf",
                mime="application/pdf",
                type="primary",
            )

    st.write("---")

    # Policy Chunks Viewer
    with st.expander("🔍 View All Extracted Policy Chunks (100% Coverage)", expanded=False):
        for idx, rule in enumerate(extracted_rules, 1):
            st.markdown(f"**Policy Block {idx}:** {rule}")

    # Audit Findings Cards
    st.markdown("### Compliance Audit Findings")
    for idx, finding in enumerate(report.findings, 1):
        with st.expander(f"Policy Rule {idx}: {finding.rule[:120]}...", expanded=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                if finding.status == "PASS":
                    st.success(f"**{finding.status}**")
                elif finding.status == "FAIL":
                    st.error(f"**{finding.status}**")
                else:
                    st.warning(f"**{finding.status}**")
                
                if finding.page_number > 0:
                    st.caption(f"📍 **Page {finding.page_number}**")
                else:
                    st.caption("📍 **Page N/A**")

            with col2:
                st.markdown(f"**Evaluated Policy Clause:**\n> *{finding.rule}*")
                st.markdown(f"**Evidence Quote from Contract:**\n> *\"{finding.evidence}\"*")
                st.markdown(f"**Reasoning:** {finding.reasoning}")

elif not (uploaded_rule_pdf and uploaded_contract_pdf):
    st.info("Please upload both a Policy/Rule PDF and a Target Contract PDF to start the audit.")