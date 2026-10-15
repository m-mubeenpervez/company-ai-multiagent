from __future__ import annotations

import requests

from company_system.config import (
    LM_STUDIO_BASE_URL,
    LM_STUDIO_EMBED_MODEL,
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple text strings into embedding vectors
    using LM Studio's OpenAI-compatible embeddings API.
    """

    if not texts:
        return []

    response = requests.post(
        f"{LM_STUDIO_BASE_URL.rstrip('/')}/embeddings",
        json={
            "model": LM_STUDIO_EMBED_MODEL,
            "input": texts,
        },
        timeout=180,
    )

    response.raise_for_status()

    data = response.json()

    items = data.get("data", [])

    if len(items) != len(texts):
        raise RuntimeError(
            "LM Studio returned an unexpected number of embeddings."
        )

    # Keep the original order.
    items = sorted(
        items,
        key=lambda item: item.get("index", 0),
    )

    return [
        item["embedding"]
        for item in items
    ]


def embed_query(text: str) -> list[float]:
    """
    Convert one search/query string into one vector.
    """

    if not text.strip():
        raise ValueError("Embedding query cannot be empty.")

    return embed_texts([text])[0]