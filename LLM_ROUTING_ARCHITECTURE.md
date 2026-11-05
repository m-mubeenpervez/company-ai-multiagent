# CompanyAI Gemini Semantic Routing Architecture

## Final routing design

CompanyAI uses Gemini LLM-based semantic routing. It does not use phrase-based deterministic Python routing.

```text
User request
    |
    v
GeminiSemanticRouterAgent
    |
    v
RoutingDecision (route + confidence + reason)
    |
    v
Selected specialist agent
    |
    v
Filtered MCP toolset
    |
    v
CompanyAI MCP server
    |
    v
Server-side authorization + business logic
```

## Reliability controls

1. A Pydantic structured-output schema limits route names to the known specialist routes plus `unknown`.
2. The router receives route descriptions, domain-collision rules, and representative examples.
3. Semantic classification supports natural paraphrases.
4. Recent conversation context is used only to resolve follow-ups; the current request takes priority.
5. Confidence is validated in the range 0.0–1.0.
6. Low-confidence decisions receive a second LLM review and are clarified rather than silently dispatched.
7. If the primary router call fails, the configured Gemini fallback model is attempted.
8. Recent context and the current request are explicitly treated as untrusted data. Embedded instructions cannot override routing policy.
9. Authorization is never decided by the router. MCP server-side tools enforce authentication and authorization.

## Models

Model names are configured in `.env`:
- Specialist agents: `GEMINI_LLM_MODEL`
- Primary router: `GEMINI_ROUTER_MODEL`
- Router fallback: `GEMINI_ROUTER_FALLBACK_MODEL`
- RAG embeddings: `GEMINI_EMBED_MODEL`
- Embedding dimensions: `GEMINI_EMBED_DIM`

The checked-in `.env.example` contains the current defaults. Model availability and free-tier quotas depend on the Google AI Studio project and can change.
