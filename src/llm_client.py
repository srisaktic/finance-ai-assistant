from src.config import LLM_PROVIDER
import os
from google import genai
from google.genai import errors as genai_errors
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.logger import logger
from src.usage_tracker import track_call

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"

# Azure OpenAI client. Only created when Azure is switched on,
# so the Gemini setup keeps working even without Azure keys.
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
azure_client = None
if LLM_PROVIDER == "azure":
    azure_client = OpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        max_retries=4,  # the library retries rate limits and network errors by itself
    )


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

def call_azure(**kwargs):
    """Centralized Azure OpenAI call (Responses API)."""
    kwargs.setdefault("model", AZURE_DEPLOYMENT)
    track_call("azure_openai")
    return azure_client.responses.create(**kwargs)


def generate_text(prompt: str, system: str | None = None, max_tokens: int | None = None) -> str:
    """Send a prompt, get plain text back, whichever provider is switched on."""
    if LLM_PROVIDER == "gemini":
        kwargs = {"input": prompt}
        if system:
            kwargs["system_instruction"] = system
        if max_tokens:
            kwargs["generation_config"] = {"max_output_tokens": max_tokens}
        return call_gemini(**kwargs).output_text.strip()

    if LLM_PROVIDER == "azure":
        kwargs = {"input": prompt}
        if system:
            kwargs["instructions"] = system
        if max_tokens:
            kwargs["max_output_tokens"] = max_tokens
        return call_azure(**kwargs).output_text.strip()

    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")