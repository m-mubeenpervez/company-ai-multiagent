from __future__ import annotations

import os

import requests
from dotenv import load_dotenv


load_dotenv()


BASE_URL = os.getenv(
    "LM_STUDIO_BASE_URL",
    "http://localhost:1234/v1",
)

LLM_MODEL = os.getenv(
    "LM_STUDIO_LLM_MODEL",
    "qwen2.5-7b-instruct-1m",
)

EMBED_MODEL = os.getenv(
    "LM_STUDIO_EMBED_MODEL",
    "text-embedding-nomic-embed-text-v1.5",
)


def main() -> None:
    print("Checking LM Studio...")

    response = requests.get(
        f"{BASE_URL.rstrip('/')}/models",
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    models = [
        item["id"]
        for item in data.get("data", [])
    ]

    print("LM Studio server: OK")
    print("Available models:")

    for model in models:
        print(f"  - {model}")

    print()
    print(f"Configured LLM: {LLM_MODEL}")
    print(f"Configured embedding model: {EMBED_MODEL}")

    if LLM_MODEL not in models:
        raise RuntimeError(
            f"Configured LLM is not available: {LLM_MODEL}"
        )

    if EMBED_MODEL not in models:
        raise RuntimeError(
            f"Configured embedding model is not available: "
            f"{EMBED_MODEL}"
        )

    print()
    print("LM Studio configuration: PASS")


if __name__ == "__main__":
    main()