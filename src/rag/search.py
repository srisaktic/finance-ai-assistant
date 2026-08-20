import os
import voyageai
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from src.usage_tracker import track_call

load_dotenv()

COLLECTION_NAME = "finance_filings"
EMBED_MODEL = "voyage-4"

voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

# qdrant_client = QdrantClient(host="localhost", port=6333)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
qdrant_client = QdrantClient(host=QDRANT_HOST, port=6333)


def embed_query(query: str) -> list[float]:
    track_call("voyage")
    result = voyage_client.embed([query], model=EMBED_MODEL, input_type="query")
    return result.embeddings[0]




def search(query: str, top_k: int = 5, ticker: str | None = None):
    query_vector = embed_query(query)

    query_filter = None
    if ticker:
        query_filter = Filter(
            must=[FieldCondition(key="ticker", match=MatchValue(value=ticker))]
        )

    return qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=top_k,
    )


def print_results(query: str, results):
    print(f"\nQuery: {query}")
    for r in results:
        p = r.payload
        snippet = p["text"][:200].replace("\n", " ")
        print(f"  [{r.score:.3f}] {p['ticker']} chunk#{p['chunk_index']} - {snippet}...")


if __name__ == "__main__":
    test_query = "What does the company say about supply chain risk?"
    print_results(test_query, search(test_query, top_k=5))