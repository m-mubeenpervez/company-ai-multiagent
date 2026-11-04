# CompanyAI Gemini API Runtime

## Final model stack

- Main ADK LLM: `gemini-3.5-flash-lite`
- RAG embedding model: `gemini-embedding-2`
- Embedding dimension: `768`
- MCP transport: local `STDIO`
- Vector database: local Qdrant
- Structured company database: SQLite

All 18 registered CompanyAI agents use native Google ADK Gemini model selection through `build_llm()`. LiteLLM and LM Studio are no longer part of the runtime.

## Authentication

Create a Gemini API key in Google AI Studio and put it only in `.env`:

```env
GEMINI_API_KEY=your-real-key
GEMINI_LLM_MODEL=gemini-3.5-flash-lite
GEMINI_EMBED_MODEL=gemini-embedding-2
GEMINI_EMBED_DIM=768
```

Never commit `.env`.

## Why Gemini 3.8 Flash

CompanyAI uses many short agent/tool turns, so the stable Flash model is preferred for lower latency while retaining function calling and agentic capabilities.

## RAG migration

The previous local embeddings are not compatible with Gemini embeddings. `setup_windows.ps1` and `run_tests.ps1` therefore rebuild the Qdrant policy collection using `gemini-embedding-2` at 768 dimensions.

## Verification

`verify_gemini.py` performs two live checks:

1. generation through `gemini-3.5-flash-lite`
2. a 768-dimensional embedding through `gemini-embedding-2`

`run_tests.ps1` additionally rebuilds the RAG collection and performs a live Qdrant retrieval test.

## Start

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
powershell -ExecutionPolicy Bypass -File .\start_project.ps1
adk web
```

No LM Studio process is required.
