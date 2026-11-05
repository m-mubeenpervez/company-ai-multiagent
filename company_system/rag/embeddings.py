from __future__ import annotations

from google import genai
from google.genai import types

from company_system.config import (
    GEMINI_API_KEY,
    GEMINI_EMBED_DIM,
    GEMINI_EMBED_MODEL,
)


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Gemini API key is missing. "
            "Set GEMINI_API_KEY in the project .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY, http_options=types.HttpOptions(timeout=120_000),
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple text strings into separate Gemini embeddings.

    Important:
    Gemini Embedding 2 aggregates plain multiple inputs if they are
    passed directly. Therefore each text is wrapped inside its own
    Content object so we receive one embedding per text/chunk.
    """

    if not texts:
        return []

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=text)
            ],
        )
        for text in texts
    ]

    with _get_client() as client:
        result = client.models.embed_content(
            model=GEMINI_EMBED_MODEL,
            contents=contents,
            config=types.EmbedContentConfig(
                output_dimensionality=GEMINI_EMBED_DIM,
            ),
        )

    embeddings = result.embeddings or []

    if len(embeddings) != len(texts):
        raise RuntimeError(
            f"Gemini returned {len(embeddings)} embeddings "
            f"for {len(texts)} input texts."
        )

    vectors: list[list[float]] = []

    for embedding in embeddings:
        values = embedding.values

        if values is None:
            raise RuntimeError(
                "Gemini returned an empty embedding vector."
            )

        vector = [
            float(value)
            for value in values
        ]

        if len(vector) != GEMINI_EMBED_DIM:
            raise RuntimeError(
                f"Expected {GEMINI_EMBED_DIM} dimensions, "
                f"but Gemini returned {len(vector)}."
            )

        vectors.append(vector)

    return vectors


def embed_query(text: str) -> list[float]:
    """
    Convert one RAG search query into one Gemini embedding.
    """

    if not text.strip():
        raise ValueError(
            "Embedding query cannot be empty."
        )

    return embed_texts([text])[0]