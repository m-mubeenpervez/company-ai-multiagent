from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.genai import types


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

# Free-tier friendly model used by specialist agents.
GEMINI_LLM_MODEL = os.getenv(
    "GEMINI_LLM_MODEL",
    "gemini-3.5-flash-lite",
)

# LLM-based semantic router. This is intentionally NOT deterministic Python routing.
GEMINI_ROUTER_MODEL = os.getenv(
    "GEMINI_ROUTER_MODEL",
    "gemini-3.5-flash-lite",
)

# Second Gemini model used only if the primary router call fails.
GEMINI_ROUTER_FALLBACK_MODEL = os.getenv(
    "GEMINI_ROUTER_FALLBACK_MODEL",
    "gemini-3.1-flash-lite",
)

GEMINI_ROUTER_MIN_CONFIDENCE = float(
    os.getenv("GEMINI_ROUTER_MIN_CONFIDENCE", "0.72")
)

GEMINI_EMBED_MODEL = os.getenv(
    "GEMINI_EMBED_MODEL",
    "gemini-embedding-2",
)

GEMINI_EMBED_DIM = int(os.getenv("GEMINI_EMBED_DIM", "768"))

RAG_COLLECTION = os.getenv("RAG_COLLECTION", "company_policies")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.45"))


def build_llm():
    """Keep the configured Gemini model with bounded HTTP time and no 429 replay."""
    from google.adk.models.google_llm import Gemini
    return Gemini(
        model=GEMINI_LLM_MODEL,
        retry_options=types.HttpRetryOptions(attempts=1),
        client_kwargs={"http_options": types.HttpOptions(timeout=120_000)},
    )


def build_agent_generation_config() -> types.GenerateContentConfig:
    """Balanced reasoning for MCP tool selection and grounded responses."""
    return types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="medium"),
    )


def build_router_generation_config() -> types.GenerateContentConfig:
    """Fast constrained classification for the semantic router."""
    return types.GenerateContentConfig(
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_level="minimal"),
    )
