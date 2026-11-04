#Ye Qdrant ke sath connection aur vector storage/search handle karta hai.

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

_DEFAULT_QDRANT_PATH = Path(__file__).resolve().parents[1] / "qdrant_storage"
QDRANT_PATH = Path(os.getenv("COMPANYAI_QDRANT_PATH", str(_DEFAULT_QDRANT_PATH))).expanduser().resolve()
COLLECTION = os.getenv("RAG_COLLECTION", "company_policies")

def get_client(*, create: bool = False) -> QdrantClient:
    if not create and not (QDRANT_PATH / "meta.json").is_file():
        raise FileNotFoundError("Existing company policy index is required; runtime will not create one.")
    return QdrantClient(path=str(QDRANT_PATH))

def recreate_collection(vector_size: int):
    client = get_client(create=True)
    try:
        if client.collection_exists(COLLECTION):
            client.delete_collection(COLLECTION)
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
    finally:
        client.close()

def upsert_chunks(chunks: list[dict], vectors: list[list[float]]):
    if len(chunks) != len(vectors) or not chunks:
        raise ValueError("Provide one vector for each nonempty chunk batch.")
    if len({chunk["chunk_id"] for chunk in chunks}) != len(chunks):
        raise ValueError("Chunk IDs must be unique within a batch.")
    client = get_client()
    try:
        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(
                models.PointStruct(
                    id=chunk["chunk_id"],
                    vector=vector,
                    payload={
                        "source": chunk["source"],
                        "page": chunk["page"],
                        "text": chunk["text"],
                    },
                )
            )
        client.upsert(collection_name=COLLECTION, points=points, wait=True)
    finally:
        client.close()
