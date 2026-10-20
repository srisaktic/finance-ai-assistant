import os
import voyageai
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from src.usage_tracker import track_call
from src.config import VECTOR_STORE
from types import SimpleNamespace
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from src.qdrant_client_factory import get_qdrant_client

load_dotenv()

COLLECTION_NAME = "finance_filings"
EMBED_MODEL = "voyage-4"

voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

# qdrant_client = QdrantClient(host="localhost", port=6333)


qdrant_client = get_qdrant_client()

# Azure AI Search client. Only created when Azure search is switched on.
azure_search_client = None
if VECTOR_STORE == "azure":
    azure_search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX", "finance-filings"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY")),
    )


def embed_query(query: str) -> list[float]:
    track_call("voyage")
    result = voyage_client.embed([query], model=EMBED_MODEL, input_type="query")
    return result.embeddings[0]




def _search_qdrant(query: str, top_k: int = 5, ticker: str | None = None):
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


def _search_azure(query: str, top_k: int = 5, ticker: str | None = None):
    query_vector = embed_query(query)  # same Voyage embedding as Qdrant uses

    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields="embedding")
    filter_expr = f"ticker eq '{ticker}'" if ticker else None

    results = azure_search_client.search(
        search_text=None,  # None means vector search only, the same as Qdrant
        vector_queries=[vector_query],
        filter=filter_expr,
        top=top_k,
        select=["id", "chunk_id", "ticker", "source_file", "chunk_index", "text", "token_count"],
    )

    hits = []
    for doc in results:
        hits.append(SimpleNamespace(
            id=int(doc["id"]),
            # Azure reports score = 1 / (1 + cosine distance).
            # Convert it back to plain cosine similarity so it means the same as Qdrant's score.
            score=2 - 1 / doc["@search.score"],
            payload={k: doc[k] for k in ["chunk_id", "ticker", "source_file", "chunk_index", "text", "token_count"]},
        ))
    return hits


def search(query: str, top_k: int = 5, ticker: str | None = None):
    """Search the filings in whichever vector store is switched on."""
    if VECTOR_STORE == "qdrant":
        return _search_qdrant(query, top_k=top_k, ticker=ticker)

    if VECTOR_STORE == "azure":
        return _search_azure(query, top_k=top_k, ticker=ticker)

    raise ValueError(f"Unknown VECTOR_STORE: {VECTOR_STORE!r}")


def print_results(query: str, results):
    print(f"\nQuery: {query}")
    for r in results:
        p = r.payload
        snippet = p["text"][:200].replace("\n", " ")
        print(f"  [{r.score:.3f}] {p['ticker']} chunk#{p['chunk_index']} - {snippet}...")


if __name__ == "__main__":
    test_query = "What does the company say about supply chain risk?"
    print_results(test_query, search(test_query, top_k=5))