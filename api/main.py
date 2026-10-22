import os
import shutil
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.parser.loader import DocumentParser
from src.parser.rule_extractor import RuleExtractor
from src.retriever.vector_store import VectorStoreManager
from src.agent.evaluator import DocumentAuditorEngine
from src.agent.schemas import AuditReport

app = FastAPI(
    title="RAG Document Auditing Microservice",
    description="Backend API for automated legal compliance auditing using Groq and Gemini.",
    version="1.0.0"
)

# Allow Streamlit UI to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)


@app.get("/")
def health_check():
    return {"status": "online", "message": "RAG Document Auditing Engine is ready."}


@app.post("/audit", response_model=AuditReport)
async def run_audit(
    policy_file: UploadFile = File(...),
    contract_file: UploadFile = File(...)
):
    """
    Upload policy PDF and contract PDF to execute a full compliance audit.
    """
    policy_path = TEMP_DIR / policy_file.filename
    contract_path = TEMP_DIR / contract_file.filename

    try:
        # 1. Save uploaded PDF files to temp directory
        with open(policy_path, "wb") as buffer:
            shutil.copyfileobj(policy_file.file, buffer)
            
        with open(contract_path, "wb") as buffer:
            shutil.copyfileobj(contract_file.file, buffer)

        # 2. Extract rules from Policy PDF
        rule_extractor = RuleExtractor(chunk_size=1500, chunk_overlap=200)
        extracted_rules = rule_extractor.extract_rules_from_pdf(policy_path)

        if not extracted_rules:
            raise HTTPException(status_code=400, detail="No valid rules could be extracted from the policy document.")

        # 3. Parse Target Contract PDF & Build Chroma Vector Store
        parser = DocumentParser()
        contract_chunks = parser.process_document(contract_path)

        vector_mgr = VectorStoreManager()
        vector_mgr.create_index(contract_chunks)

        # 4. Run Groq Audit Engine
        auditor = DocumentAuditorEngine(vector_manager=vector_mgr)
        report = auditor.run_full_audit(
            document_name=contract_file.filename,
            rule_list=extracted_rules
        )

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit process failed: {str(e)}")

    finally:
        # Clean up temporary saved files after execution
        if policy_path.exists():
            os.remove(policy_path)
        if contract_path.exists():
            os.remove(contract_path)