from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    config = (PROJECT_ROOT / "company_system" / "config.py").read_text(encoding="utf-8")
    env = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    router = (PROJECT_ROOT / "company_system" / "routing" / "semantic_router_agent.py").read_text(encoding="utf-8")
    embeddings = (PROJECT_ROOT / "company_system" / "rag" / "embeddings.py").read_text(encoding="utf-8")

    assert '"gemini-3.5-flash-lite"' in config
    assert '"gemini-3.1-flash-lite"' in config
    assert "GEMINI_ROUTER_MODEL" in config
    assert "GEMINI_ROUTER_MIN_CONFIDENCE" in config
    assert 'thinking_level="medium"' in config
    assert 'thinking_level="minimal"' in router
    assert "response_schema=RoutingDecision" in router
    assert "genai.Client" in router
    assert "genai.Client" in embeddings
    assert "LM_STUDIO" not in config
    assert "LiteLlm" not in config
    assert "GEMINI_LLM_MODEL=gemini-3.5-flash-lite" in env

    print("PASS | Gemini 3.5 Flash-Lite specialist configuration is active")
    print("PASS | Gemini semantic router + fallback configuration is active")
    print("PASS | Router uses minimal thinking; specialists use medium thinking")
    print("PASS | Gemini embeddings remain configured for RAG")


if __name__ == "__main__":
    main()
