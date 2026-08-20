import os
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.logger import logger
from src.usage_tracker import track_call

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"


def _log_retry(retry_state):
    logger.warning(
        f"Gemini call failed (attempt {retry_state.attempt_number}), retrying: {retry_state.outcome.exception()}"
    )


@retry(
    retry=retry_if_exception_type(genai_errors.APIError),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(4),
    before_sleep=_log_retry,
)
def call_gemini(**kwargs):
    """Centralized Gemini call with automatic retry/backoff on API errors (e.g. rate limits)."""
    kwargs.setdefault("model", MODEL)
    track_call("gemini")
    return client.interactions.create(**kwargs)