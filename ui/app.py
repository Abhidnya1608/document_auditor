import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))


import tempfile
import streamlit as st
from config.settings import settings 
from src.parser.loader import DocumentParser
from src.retriever.vector_store import VectorStoreManager
from src.agent.evaluator import DocumentAuditorEngine

st.set_page_config(
    page_title = "RAG Document Auditor",
    layout = "wide"
)

st.title("Rag Document Auditing Agent")
st.caption("Cross-Examines contracts over rules")

#Side Bar

with st.sidebar:
    st.header("Audit Checklist")
    rules_input = st.text_area(
        "Enter compilance rules:",
        value = (
            "The agreement must specify a written termination notice period.\n"
            "Payment must be completed within 30 days of invoice receipt."
        ),
        height = 200
        )

    rule_list = [r.strip() for r in rules_input.split("\n") if r.strip()]


#Main

uploaded_file = st.file_uploader("Upload PDF Document" , type = ["pdf"])


if uploaded_file and rule_list:
    if st.button("Run document Audit" , type = "primary"):
        with st.status("Running Audit Pipeline..." , expanded = True) as status:
            #Save uploaded PDF to temp file
            with tempfile.NamedTemporaryFile(delete = False , suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = Path(tmp.name)

            # Parse pdf

            st.write('Parsing pdf to chunks')
            parser = DocumentParser()
            chunks = parser.process_document(tmp_path)


            # Index in Chroma DB
            st.write("Embedding chunks in chroma db")
            vector_mgr = VectorStoreManager()
            vector_mgr.create_index(chunks)

            #RUnning audit engine
            st.write("Evaluating compilance rules")
            auditor = DocumentAuditorEngine(vector_manager=vector_mgr)
            report = auditor.run_full_audit(
                document_name= uploaded_file.name,
                rule_list = rule_list
            )

            st.subheader("Audit results for {report.document_name}")
            st.write(f"Total Rules Cheked : **{report.total_rules_checked}**")

            for idx , finding in enumerate(report.findings , 1):
                with st.expander(f"Rule {idx}: {finding.rule}" , expanded=True):
                    col1 , col2 = st.columns([1,4])

                    with col1:
                        if finding.status == "Pass":
                            st.success(f"{finding.status}")
                        elif finding.status == "Fail":
                            st.error(f"{finding.status}")
                        else:
                            st.warning(f"{finding.status}")
                        st.caption(f"Page {finding.page_number}")

                    with col2:
                        st.markdown(f"Evidence: {finding.evidence}")
                        st.markdown(f"Reasoning: {finding.reasoning}")


elif not uploaded_file:
    st.info("Pls upload pdf")