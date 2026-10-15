from __future__ import annotations

def chunk_pages(pages: list[dict], chunk_size: int = 1000, overlap: int = 150) -> list[dict]:
    chunks = []
    chunk_id = 1
    for page in pages:
        paragraphs = [p.strip() for p in page["text"].split("\n") if p.strip()]
        buffer = ""
        for paragraph in paragraphs:
            candidate = (buffer + "\n" + paragraph).strip() if buffer else paragraph
            if len(candidate) <= chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.append({
                    "chunk_id": chunk_id,
                    "source": page["source"],
                    "page": page["page"],
                    "text": buffer,
                })
                chunk_id += 1
                tail = buffer[-overlap:] if overlap > 0 else ""
                buffer = (tail + "\n" + paragraph).strip()
            else:
                chunks.append({
                    "chunk_id": chunk_id,
                    "source": page["source"],
                    "page": page["page"],
                    "text": paragraph[:chunk_size],
                })
                chunk_id += 1
                buffer = paragraph[max(0, chunk_size-overlap):]
        if buffer:
            chunks.append({
                "chunk_id": chunk_id,
                "source": page["source"],
                "page": page["page"],
                "text": buffer,
            })
            chunk_id += 1
    return chunks
