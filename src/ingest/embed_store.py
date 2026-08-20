import json
import os
from pathlib import Path
from src.qdrant_client_factory import get_qdrant_client
import voyageai
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

load_dotenv()

PROCESSED_DIR = Path("data/processed")
COLLECTION_NAME = "finance_filings"
EMBED_MODEL = "voyage-4"   # covered by Voyage's 200M free-token allowance
BATCH_SIZE = 100

voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

qdrant_client = get_qdrant_client()


def load_all_chunks() -> list[dict]:
    chunks = []
    for filepath in sorted(PROCESSED_DIR.glob("*_chunks.json")):
        chunks.extend(json.loads(filepath.read_text(encoding="utf-8")))
    return chunks


def embed_batch(texts: list[str]) -> list[list[float]]:
    result = voyage_client.embed(texts, model=EMBED_MODEL, input_type="document")
    return result.embeddings


def main():
    chunks = load_all_chunks()
    print(f"Loaded {len(chunks)} chunks total")

    first_batch = chunks[:BATCH_SIZE]
    first_embeddings = embed_batch([c["text"] for c in first_batch])
    vector_size = len(first_embeddings[0])
    print(f"Embedding dimension: {vector_size}")

    if qdrant_client.collection_exists(COLLECTION_NAME):
            qdrant_client.delete_collection(COLLECTION_NAME)


    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="ticker",
        field_schema="keyword",
    )
    
    point_id = 0
    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_start:batch_start + BATCH_SIZE]
        embeddings = first_embeddings if batch_start == 0 else embed_batch([c["text"] for c in batch])

        points = [
            PointStruct(
                id=point_id + i,
                vector=vector,
                payload={
                    "chunk_id": chunk["id"],
                    "ticker": chunk["ticker"],
                    "source_file": chunk["source_file"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "token_count": chunk["token_count"],
                },
            )
            for i, (chunk, vector) in enumerate(zip(batch, embeddings))
        ]
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        point_id += len(batch)
        print(f"  Stored {point_id}/{len(chunks)} chunks")

    print(f"Done. {point_id} chunks stored in Qdrant collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()