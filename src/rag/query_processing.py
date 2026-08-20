from src.config import COMPANY_ALIASES
#import anthropic
#from google import genai
from src.llm_client import call_gemini
import os
from dotenv import load_dotenv

def detect_ticker(question: str) -> str | None:
    """Return the ticker mentioned in the question, if any, else None."""
    question_lower = question.lower()
    for ticker, aliases in COMPANY_ALIASES.items():
        if any(alias in question_lower for alias in aliases):
            return ticker
    return None



load_dotenv()

#client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

REWRITE_PROMPT = """You are helping rewrite a user's question into the formal language used in SEC 10-K filings, so it matches better against filing text in a semantic search system.

Rewrite the question below using formal financial/corporate filing terminology (e.g., "employee" -> "human capital", "workforce", "personnel"; "money earned" -> "revenue", "net income"; "problems" -> "risks", "uncertainties"; "products sold" -> "sales", "shipments").

Rules:
- Preserve the original meaning and intent exactly. Do not answer the question, only rewrite it.
- Do not add assumptions or information not implied by the original question.
- Output ONLY the rewritten question, nothing else.

Original question: {question}

Rewritten question:"""


'''
def rewrite_query(question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=100,
        messages=[{"role": "user", "content": REWRITE_PROMPT.format(question=question)}],
    )
    return response.content[0].text.strip()
'''

def rewrite_query(question: str) -> str:
    interaction = call_gemini(input=REWRITE_PROMPT.format(question=question))
    return interaction.output_text.strip()