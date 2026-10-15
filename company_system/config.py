from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


LM_STUDIO_BASE_URL = os.getenv(
    "LM_STUDIO_BASE_URL",
    "http://localhost:1234/v1",
)

LM_STUDIO_LLM_MODEL = os.getenv(
    "LM_STUDIO_LLM_MODEL",
    "qwen2.5-7b-instruct-1m",
)

LM_STUDIO_EMBED_MODEL = os.getenv(
    "LM_STUDIO_EMBED_MODEL",
    "text-embedding-nomic-embed-text-v1.5",
)


RAG_COLLECTION = os.getenv(
    "RAG_COLLECTION",
    "company_policies",
)

RAG_TOP_K = int(
    os.getenv(
        "RAG_TOP_K",
        "5",
    )
)

RAG_MIN_SCORE = float(
    os.getenv(
        "RAG_MIN_SCORE",
        "0.45",
    )
)


def build_llm() -> LiteLlm:
    """
    Create the LLM connection used by all CompanyAI agents.

    Important:
    - The model runs locally inside LM Studio.
    - `openai/` tells LiteLLM to use an OpenAI-compatible API.
    - This does NOT use OpenAI's cloud API.
    """

    return LiteLlm(
        model=f"openai/{LM_STUDIO_LLM_MODEL}",
        api_base=LM_STUDIO_BASE_URL,
        api_key="lm-studio",
    )