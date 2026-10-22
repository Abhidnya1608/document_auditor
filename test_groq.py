
from config.settings import settings
from langchain_openai import ChatOpenAI
from src.agent.schemas import AuditFinding

print("Testing Groq connection...", flush=True)

llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    timeout=30,
    max_retries=0,
)

structured_llm = llm.with_structured_output(
    AuditFinding,
    method="json_schema",
)

rule = """
The service provider must submit a monthly maintenance report.
"""

contract_context = """
The contract requires the service provider to submit a monthly
maintenance report by the fifth working day of each month.
"""

prompt = f"""
You are a contract compliance auditor.

Evaluate whether the contract context complies with the rule.

RULE:
{rule}

CONTRACT CONTEXT:
{contract_context}

Return a finding using the required schema. Base your decision
only on the supplied context.
"""

print("Sending one rule to Groq...", flush=True)

try:
    result = structured_llm.invoke(prompt)
    print("\nGroq response received!")
    print(result.model_dump_json(indent=2))
except Exception as e:
    print(f"\nTest failed: {type(e).__name__}: {e}")
