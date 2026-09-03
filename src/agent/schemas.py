from typing import List , Literal
from pydantic import BaseModel , Field

class AuditFinding(BaseModel):
    """Structured audit report output"""

    rule: str = Field(
        description = "The specific compilance rule or requirement evaluated"
    )
    status: Literal["Pass" , "Fail" , "Needs_review"] = Field(
        description = "Pass if complaint , Fail if non-complaint , NEEDS_REVIEW if information is ambiguous or missing" 
    )
    evidence: str = Field(
        description = "Direct verbatim text quote from the document supporting this finding. If status is NEEDS_REVIEW , state what is missing"
    )
    reasoning: str = Field(
        description="Clear, step-by-step logical explanation of why the rule passed or failed."
    )
    page_number: int = Field(
        description="Primary page number where the supporting evidence text was found."
    )

class AuditReport(BaseModel):
    document_name: str = Field(description = "Name of the PDF" )
    total_rules_checked : int = Field(description = "Total number of rules audited")
    findings: List[AuditFinding] = Field(
        description="List of detailed audit findings for each rule"
    )