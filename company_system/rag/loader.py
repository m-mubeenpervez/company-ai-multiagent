from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader

def load_pdf_pages(path: str | Path) -> list[dict]:
    path = Path(path)
    reader = PdfReader(str(path))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({
                "source": path.name,
                "page": page_number,
                "text": text,
            })
    return pages
