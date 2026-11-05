from __future__ import annotations

import re
from collections.abc import Iterator


_NUMBERED_HEADING = re.compile(r"^\d+(?:\.\d+)*[.)]\s+\S")
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“])")


def _title_line(line: str) -> bool:
    """Recognize a short page-opening title without treating wrapped prose as one."""
    words = line.split()
    return (
        2 <= len(words) <= 10
        and len(line) <= 80
        and not line.endswith((".", ":", ";", ",", "?", "!"))
        and all(word[0].isupper() or word in {"and", "of", "the", "for", "in"} for word in words)
    )


def _pack_sentences(body: str, budget: int, overlap: int) -> Iterator[str]:
    """Use complete sentences; the size limit is soft for an overlong sentence."""
    buffer: list[str] = []
    for sentence in _SENTENCE_BREAK.split(body):
        if buffer and len(" ".join([*buffer, sentence])) > budget:
            yield " ".join(buffer)
            carry: list[str] = []
            for previous in reversed(buffer):
                candidate = [previous, *carry]
                if (len(" ".join(candidate)) > overlap
                        or len(" ".join([*candidate, sentence])) > budget):
                    break
                carry = candidate
            buffer = carry
        buffer.append(sentence)
    if buffer:
        yield " ".join(buffer)


def chunk_pages(pages: list[dict], chunk_size: int = 1000, overlap: int = 150) -> list[dict]:
    """Keep numbered policy sections and their rules together on each PDF page.

    PDF newlines usually mark visual wrapping, not paragraph boundaries. Section
    headings delimit topics; complete sentences delimit oversized sections.
    Source/page metadata remains tied to the original page. Headings continue
    across pages of the same document, but passage bodies never cross pages.
    """
    if chunk_size <= 0 or not 0 <= overlap < chunk_size:
        raise ValueError("chunk_size must be positive and 0 <= overlap < chunk_size")

    chunks: list[dict] = []
    heading = ""
    previous_source = None
    for page in pages:
        if page["source"] != previous_source:
            heading = ""
        previous_source = page["source"]
        lines = [" ".join(line.split()) for line in page["text"].splitlines() if line.strip()]
        if not lines:
            continue
        if _title_line(lines[0]):
            heading = lines.pop(0)

        sections: list[tuple[str, str]] = []
        body_lines: list[str] = []
        for line in lines:
            if _NUMBERED_HEADING.match(line):
                if body_lines:
                    sections.append((heading, " ".join(body_lines)))
                heading = line
                body_lines = []
            else:
                body_lines.append(line)
        if body_lines:
            sections.append((heading, " ".join(body_lines)))

        for title, body in sections:
            prefix = f"{title}\n" if title else ""
            budget = max(1, chunk_size - len(prefix))
            for passage in _pack_sentences(body, budget, overlap):
                chunks.append({
                    "chunk_id": len(chunks) + 1,
                    "source": page["source"],
                    "page": page["page"],
                    "text": prefix + passage,
                })
    return chunks
