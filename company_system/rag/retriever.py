from __future__ import annotations
import os
from dotenv import load_dotenv
from pathlib import Path
from .embeddings import embed_query
from .vector_store import get_client, COLLECTION

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
TOP_K = int(os.getenv("RAG_TOP_K", "5"))
MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.45"))

def search_policy(query: str) -> dict:
    vector = embed_query(query)
    client = get_client()
    try:
        if not client.collection_exists(COLLECTION):
            return {"status":"not_ready","message":"Policy vector database has not been ingested yet."}
        response = client.query_points(
            collection_name=COLLECTION,
            query=vector,
            limit=TOP_K,
            score_threshold=MIN_SCORE,
            with_payload=True,
        )
    finally:
        client.close()

    results = []
    for point in response.points:
        payload = point.payload or {}
        results.append({
            "score": round(float(point.score),4),
            "source": payload.get("source"),
            "page": payload.get("page"),
            "text": payload.get("text"),
        })
    if not results:
        return {"status":"not_found","message":"No sufficiently relevant company policy passage was found."}
    return {"status":"success","results":results}
