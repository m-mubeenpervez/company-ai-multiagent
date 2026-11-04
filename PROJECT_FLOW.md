# CompanyAI — Current Project Flow

## Core architecture

```text
Company User
    |
    v
Google ADK Web / Runner
    |
    v
CompanyAI Supervisor (GeminiSemanticRouterAgent)
    |
    v
Gemini structured routing decision
    |
    +--> Authentication Agent
    +--> HR Agent
    +--> Employee Records Agent
    +--> Intern Management Agent
    +--> Attendance Agent
    +--> Leave Agent
    +--> Policy RAG Agent
    +--> Recruitment Agent
    +--> Performance Agent
    +--> Training Agent
    +--> Project / Task Agent
    +--> Payroll Agent
    +--> Finance Agent
    +--> IT Asset Agent
    +--> Document Agent
    +--> Analytics Agent
    +--> Notification Agent
    +--> Audit Agent
```

## Routing

Top-level routing is LLM-based. `GeminiSemanticRouterAgent` asks Gemini to return a structured `RoutingDecision` containing a route, confidence, and reason. It uses the route catalog, collision rules, recent conversation context, a confidence gate, a second-pass review, and a fallback model when the primary call fails.

There is no phrase-based deterministic Python router. Python validates the structured response and dispatches to the selected specialist.

Routing is not authorization. The selected agent and the model cannot grant permissions.

## Specialist and MCP flow

```text
Selected Specialist Agent
    |
    v
Filtered ADK McpToolset
    |
    v
Local MCP Server (STDIO)
    |
    v
MCP session-token validation
    |
    v
Existing CompanyAI domain tool
    |
    +--> SQLite structured records
    |
    +--> Gemini embeddings -> Qdrant (policy RAG)
```

All 18 registered agents use filtered MCP toolsets. The MCP server exposes 39 tools, including the health-check tool. Existing functions under `company_system/tools/` remain the business-logic and authorization layer.

## Authentication and authorization

1. The authentication tool verifies salted PBKDF2 password hashes.
2. The MCP server creates an opaque random token and stores only its SHA-256 hash.
3. The ADK host stores the raw token in session state.
4. The host callback overwrites any model-supplied `session_token` with the trusted session token.
5. The MCP server validates token existence, revocation, expiry, and current user account status/role.
6. The existing business tool enforces `require_auth`, `require_roles`, and record-level access checks.

A route selection never authorizes an action.

## RAG flow

```text
company_handbook.pdf
    |
    v
PDF extraction by page
    |
    v
Chunking with overlap
    |
    v
Gemini Embedding API (gemini-embedding-2, 768 dimensions)
    |
    v
Local Qdrant collection
    |
    v
Policy query embedding
    |
    v
Top-K retrieval
    |
    v
Policy Agent grounds its answer in retrieved evidence
```

Retrieved document passages are treated as untrusted evidence, not as instructions. The Policy Agent must ignore embedded commands and cite only source/page metadata returned by the retrieval tool.

## Data stores

- SQLite: employees, users, leave, payroll, attendance, projects, assets, documents, notifications, audit records, and MCP sessions.
- Qdrant: company handbook policy chunks only.
- ADK session store: conversation and session state.

Personal records, payroll, credentials, and employee-specific data must remain in structured systems, not the policy vector collection.

## Evaluation and security

The `evaluations/` and `security/` folders contain:
- Golden datasets for all 18 routing destinations.
- RAGAS evaluation of retrieval and answer grounding.
- DeepEval evaluation of answer relevance, faithfulness, and tool behavior.
- Routing accuracy and MCP catalog checks.
- Prompt-injection, session, token, and authorization regression tests.

Evaluation scripts use isolated copies of the SQLite database and Qdrant storage. They must not mutate the active project database or active Qdrant collection.

See `EVALUATION_SECURITY_IMPLEMENTATION.md` for commands and limitations.
