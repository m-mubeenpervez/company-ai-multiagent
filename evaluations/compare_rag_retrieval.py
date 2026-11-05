"""Compare corpus changes with identical tool queries and Gemini query vectors.

Prepare once before reindexing; compare afterward. No references or judge scores
are used to retrieve, rerank, or filter passages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from company_system.config import GEMINI_EMBED_MODEL, GEMINI_EMBED_DIM
from company_system.rag.embeddings import embed_texts
from company_system.rag.retriever import TOP_K, MIN_SCORE
from company_system.rag.vector_store import COLLECTION, QDRANT_PATH
from qdrant_client import QdrantClient

BASELINE = ROOT / "evaluations/results/ragas_eval_diagnostic_baseline.json"
CACHE = ROOT / "evaluations/provenance/rag_quality_query_vectors.json"
BEFORE_INDEX = ROOT / "evaluations/provenance/rag_quality_corpus_before/qdrant_storage"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluations/results/release_frozen_retrieval_comparison.json")
    args = parser.parse_args()
    settings = {
        "model": GEMINI_EMBED_MODEL, "dimensions": GEMINI_EMBED_DIM,
        "top_k": TOP_K, "min_score": MIN_SCORE, "collection": COLLECTION,
        "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
    }
    if args.prepare:
        if CACHE.exists():
            raise FileExistsError("Frozen baseline query vectors already exist; preserve them for comparison.")
        report = json.loads(BASELINE.read_text(encoding="utf-8"))
        queries = [
            {"id": row["id"], "query": call["input_parameters"]["query"]}
            for row in report["results"] for call in row["tools_called"]
            if call["name"] == "search_company_policy"
        ]
        vectors = embed_texts([row["query"] for row in queries])
        CACHE.write_text(json.dumps({"settings": settings, "queries": [
            {**row, "vector": vector} for row, vector in zip(queries, vectors, strict=True)
        ]}), encoding="utf-8")
        print(f"Prepared {len(queries)} fixed tool queries and query vectors.")
        return

    cached = json.loads(CACHE.read_text(encoding="utf-8"))
    if cached["settings"] != settings:
        raise RuntimeError("Query model, retrieval settings, or baseline changed since preparation")
    for path in (BEFORE_INDEX, QDRANT_PATH):
        if not path.resolve().is_relative_to(ROOT.resolve()) or not path.exists():
            raise RuntimeError(f"Expected an existing index inside the working copy: {path}")

    def retrieve(client, vector):
        response = client.query_points(collection_name=COLLECTION, query=vector,
                                       limit=TOP_K, score_threshold=MIN_SCORE, with_payload=True)
        return [{"rank": rank, "point_id": point.id,
                 "score": round(float(point.score), 4), **(point.payload or {})}
                for rank, point in enumerate(response.points, 1)]

    with closing(QdrantClient(path=str(BEFORE_INDEX))) as before, closing(QdrantClient(path=str(QDRANT_PATH))) as after:
        rows = [{"id": row["id"], "query": row["query"],
                 "before": retrieve(before, row["vector"]),
                 "after": retrieve(after, row["vector"])} for row in cached["queries"]]
    output = args.output
    if output.exists():
        from datetime import datetime, timezone
        archive = output.with_name(output.stem + "_previous_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + output.suffix)
        archive.write_bytes(output.read_bytes())
    output.write_text(json.dumps({"settings": settings, "results": rows}, indent=2), encoding="utf-8")
    print(f"Saved controlled retrieval comparison: {output}")


if __name__ == "__main__":
    main()
