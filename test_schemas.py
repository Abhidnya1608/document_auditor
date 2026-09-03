from config.settings import settings
from src.agent.schemas import AuditFinding

sample_finding = AuditFinding(
    rule = "30-day termination notice required",
    status = "Fail",
    evidence="Either party may terminate upon 14 days written notice.",
    reasoning="The contract specifies 14 days, which is less than the required 30 days.",
    page_number=4
)

print("✅ Schema instantiated successfully!")
print(f"• Status: {sample_finding.status}")
print(f"• Evidence: {sample_finding.evidence}")
print(f"• Page: {sample_finding.page_number}")