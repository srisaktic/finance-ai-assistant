import os
import voyageai
from dotenv import load_dotenv
from src.usage_tracker import track_call

load_dotenv()

RERANK_MODEL = "rerank-2.5"

voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))


def rerank(question: str, candidates: list, top_k: int = 5) -> list:
    """Re-score candidates by having the reranker read the question and each chunk together,
    instead of relying on pre-computed embedding similarity."""
    if not candidates:
        return []

    documents = [c.payload["text"] for c in candidates]
    track_call("voyage")
    result = voyage_client.rerank(question, documents, model=RERANK_MODEL, top_k=top_k)

    reranked = []
    for item in result.results:
        original = candidates[item.index]
        reranked.append({
            "payload": original.payload,
            "rerank_score": item.relevance_score,
            "original_score": original.score,
        })
    return reranked
