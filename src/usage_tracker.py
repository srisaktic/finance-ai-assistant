import json
from pathlib import Path
from datetime import date
from src.logger import logger

USAGE_FILE = Path("logs/usage.json")

# only Gemini's limit is confirmed precisely (3.1-flash-lite free tier).
# Voyage's free tier is token-based, not a clean daily request count, and
# Tavily's exact current limit isn't verified here — so those track counts
# without asserting a specific number to compare against.
FREE_TIER_DAILY_LIMITS = {
    "gemini": 1500,
}


def _load() -> dict:
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {}


def _save(data: dict) -> None:
    USAGE_FILE.parent.mkdir(exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2))


def track_call(provider: str) -> None:
    """Increment today's call count for a given provider (e.g. 'gemini', 'voyage', 'tavily')."""
    today = str(date.today())
    data = _load()
    data.setdefault(today, {})
    data[today][provider] = data[today].get(provider, 0) + 1
    _save(data)

    count = data[today][provider]
    limit = FREE_TIER_DAILY_LIMITS.get(provider)
    if limit:
        logger.info(f"Usage: {provider} — {count}/{limit} requests today")
        if count >= limit * 0.8:
            logger.warning(f"Usage: {provider} at {count}/{limit} — approaching free-tier daily limit")
    else:
        logger.info(f"Usage: {provider} — {count} requests today")


def usage_summary() -> dict:
    """Return today's usage counts for all providers."""
    return _load().get(str(date.today()), {})