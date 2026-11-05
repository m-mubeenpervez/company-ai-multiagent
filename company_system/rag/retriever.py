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
MAX_SCORE_DROP = float(os.getenv("RAG_MAX_SCORE_DROP", "0.12"))

def search_policy(query: str) -> dict:
    try:
        client = get_client()
    except FileNotFoundError:
        return {"status":"not_ready","message":"Policy vector database has not been ingested yet."}
    try:
        if not client.collection_exists(COLLECTION):
            return {"status":"not_ready","message":"Policy vector database has not been ingested yet."}
        vector = embed_query(query)
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
    best_score = float(response.points[0].score) if response.points else None
    for point in response.points:
        if best_score is not None and best_score - float(point.score) > MAX_SCORE_DROP:
            continue
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
