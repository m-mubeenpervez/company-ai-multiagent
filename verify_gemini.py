from __future__ import annotations

from google import genai
from google.genai import types

from company_system.config import (
    GEMINI_API_KEY,
    GEMINI_EMBED_DIM,
    GEMINI_EMBED_MODEL,
    GEMINI_LLM_MODEL,
    GEMINI_ROUTER_MODEL,
)
from company_system.routing.semantic_router_agent import classify_route
from company_system.security.quota import check_quota, record_quota


def _validate_key() -> None:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_GEMINI_API_KEY_HERE":
        raise SystemExit(
            "Gemini API key is not configured. Open .env and replace "
            "PASTE_YOUR_GEMINI_API_KEY_HERE with your Google AI Studio key."
        )


def _verify() -> None:
    _validate_key()
    check_quota()  # Honor the same provider cooldown as all evaluation entry points.

    print(f"Configured Gemini LLM: {GEMINI_LLM_MODEL}")
    print(f"Configured Gemini router: {GEMINI_ROUTER_MODEL}")
    print(f"Configured Gemini embedding model: {GEMINI_EMBED_MODEL}")

    with genai.Client(api_key=GEMINI_API_KEY, http_options=types.HttpOptions(timeout=120_000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
        response = client.models.generate_content(
            model=GEMINI_LLM_MODEL,
            contents="Reply with exactly: COMPANYAI_GEMINI_OK",
        )
        text = (response.text or "").strip()
        if "COMPANYAI_GEMINI_OK" not in text:
            raise RuntimeError(f"Unexpected Gemini model response: {text!r}")
        print("PASS | Gemini generation API is reachable")

        route = classify_route("How many vacation days do I have left?")
        if route.route != "leave_agent":
            raise RuntimeError(f"Gemini semantic router returned {route.route}: {route.reason}")
        print(f"PASS | Gemini semantic router is reachable ({route.route}, {route.confidence:.2f})")

        embedding_response = client.models.embed_content(
            model=GEMINI_EMBED_MODEL,
            contents="CompanyAI embedding connectivity test",
            config=types.EmbedContentConfig(output_dimensionality=GEMINI_EMBED_DIM),
        )
        embeddings = embedding_response.embeddings or []
        if len(embeddings) != 1 or embeddings[0].values is None:
            raise RuntimeError("Gemini embedding API returned no vector.")

        dimension = len(embeddings[0].values)
        if dimension != GEMINI_EMBED_DIM:
            raise RuntimeError(f"Expected embedding dimension {GEMINI_EMBED_DIM}, got {dimension}.")
        print(f"PASS | Gemini embedding API is reachable ({dimension} dimensions)")


def main() -> None:
    try:
        _verify()
    except Exception as exc:
        record_quota(exc)
        raise SystemExit("Gemini verification failed or is quota-blocked; no automatic retry. "
                         "Inspect the private quota circuit and provider access.") from None


if __name__ == "__main__":
    main()
