from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

QDRANT_PATH = Path(__file__).resolve().parents[1] / "qdrant_storage"
COLLECTION = os.getenv("RAG_COLLECTION", "company_policies")

def get_client() -> QdrantClient:
    return QdrantClient(path=str(QDRANT_PATH))

def recreate_collection(vector_size: int):
    client = get_client()
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
