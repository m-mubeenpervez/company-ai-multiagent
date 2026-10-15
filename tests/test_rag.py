from pathlib import Path
from company_system.rag.loader import load_pdf_pages
from company_system.rag.chunker import chunk_pages

pdf = Path("company_system/documents/company_handbook.pdf")
pages = load_pdf_pages(pdf)
chunks = chunk_pages(pages)

assert len(pages) >= 3
assert len(chunks) >= 8
assert any("monthly progress report" in c["text"].lower() for c in chunks)
print(f"RAG document pipeline smoke test PASS: {len(pages)} pages -> {len(chunks)} chunks")
print(
    "Live embedding/Qdrant search uses "
    "LM Studio embeddings and local Qdrant."
)