"""Copy the filing chunks from Qdrant into an Azure AI Search index.

The vectors are copied as they are (no re-embedding), so both stores hold
exactly the same data and the comparison is fair.
Run once:  python -m src.ingest.azure_search_store
"""
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    VectorSearch,
    VectorSearchProfile,
)
from src.qdrant_client_factory import get_qdrant_client

load_dotenv()

QDRANT_COLLECTION = "finance_filings"
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "finance-filings")
BATCH_SIZE = 100

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])


def load_from_qdrant() -> list:
    """Read every chunk (id, vector, payload) out of Qdrant, page by page."""
    qdrant = get_qdrant_client()
    points, offset = [], None
    while True:
        batch, offset = qdrant.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=True,
        )
        points.extend(batch)
        if offset is None:
            return points


def build_index(vector_size: int) -> SearchIndex:
    """Describe the index, like the columns of a table, plus the vector column."""
    fields = [
        SearchField(name="id", type=SearchFieldDataType.STRING, key=True, filterable=True),
        SearchField(name="chunk_id", type=SearchFieldDataType.STRING),
        SearchField(name="ticker", type=SearchFieldDataType.STRING, filterable=True),
        SearchField(name="source_file", type=SearchFieldDataType.STRING),
        SearchField(name="chunk_index", type=SearchFieldDataType.INT32, filterable=True, sortable=True),
        SearchField(name="token_count", type=SearchFieldDataType.INT32),
        SearchField(name="text", type=SearchFieldDataType.STRING, searchable=True),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.SINGLE),
            searchable=True,
            vector_search_dimensions=vector_size,
            vector_search_profile_name="vector-profile",
        ),
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw", parameters=HnswParameters(metric="cosine"))],
        profiles=[VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw")],
    )
    return SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)


def main():
    points = load_from_qdrant()
    print(f"Read {len(points)} chunks from Qdrant")
    vector_size = len(points[0].vector)
    print(f"Vector size: {vector_size}")

    index_client = SearchIndexClient(endpoint, credential)
    if INDEX_NAME in list(index_client.list_index_names()):
        index_client.delete_index(INDEX_NAME)
        print(f"Deleted old index '{INDEX_NAME}'")
    index_client.create_index(build_index(vector_size))
    print(f"Created index '{INDEX_NAME}'")

    search_client = SearchClient(endpoint, INDEX_NAME, credential)
    docs = [
        {
            "id": str(p.id),  # Azure needs the key as text
            "chunk_id": str(p.payload["chunk_id"]),
            "ticker": p.payload["ticker"],
            "source_file": p.payload["source_file"],
            "chunk_index": p.payload["chunk_index"],
            "token_count": p.payload["token_count"],
            "text": p.payload["text"],
            "embedding": p.vector,
        }
        for p in points
    ]
    for start in range(0, len(docs), BATCH_SIZE):
        results = search_client.upload_documents(documents=docs[start:start + BATCH_SIZE])
        failed = [r for r in results if not r.succeeded]
        if failed:
            raise RuntimeError(f"{len(failed)} chunks failed to upload. First one: {failed[0]}")
        print(f"  Uploaded {min(start + BATCH_SIZE, len(docs))}/{len(docs)}")

    print("Done. (Azure can take a few seconds before every chunk shows up in searches.)")


if __name__ == "__main__":
    main()