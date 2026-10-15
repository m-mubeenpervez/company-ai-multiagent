from __future__ import annotations
from pathlib import Path
from .loader import load_pdf_pages
from .chunker import chunk_pages
from .embeddings import embed_texts
from .vector_store import recreate_collection, upsert_chunks

def ingest_pdf(pdf_path: str | Path) -> dict:
    pages = load_pdf_pages(pdf_path)
    chunks = chunk_pages(pages)
    if not chunks:
        raise RuntimeError("No text chunks were produced from the PDF.")
    vectors = embed_texts([c["text"] for c in chunks])
    vector_size = len(vectors[0])
    recreate_collection(vector_size)
    upsert_chunks(chunks, vectors)
    return {
        "status":"success",
        "pages":len(pages),
        "chunks":len(chunks),
        "vector_size":vector_size,
        "source":Path(pdf_path).name,
    }
