import os
from dotenv import load_dotenv

load_dotenv()

# Which services to use. Change these in .env (or on Render). No code changes needed.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()   # "gemini" or "azure"
VECTOR_STORE = os.getenv("VECTOR_STORE", "qdrant").lower()   # "qdrant" or "azure"

TICKERS = ["AAPL", "MSFT", "NVDA"]

COMPANY_ALIASES = {
    "AAPL": ["apple", "aapl"],
    "MSFT": ["microsoft", "msft"],
    "NVDA": ["nvidia", "nvda"],
}