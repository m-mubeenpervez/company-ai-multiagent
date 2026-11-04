# CompanyAI Secure Multi-Agent Platform

CompanyAI is a local company-management multi-agent application built with Python,
Google ADK, Gemini semantic routing, MCP, SQLite and handbook RAG backed by local
Qdrant and Gemini embeddings.

It has **18 domain/auth agents and 39 MCP tools** for employee and intern records,
attendance, leave, recruitment, performance, training, projects/tasks, payroll,
expenses, assets, document metadata, analytics, notifications and audit logs.
Policy answers use the official handbook rather than model memory. Authentication,
revocable sessions and role/record authorization are enforced by the tool layer.

This is a local development application. See [the release report](FINAL_RELEASE_REPORT.md)
for executed checks, quota-blocked model tests and unresolved dependency advisories.
It is not a verified production deployment.

## Architecture and source layout

The Gemini supervisor selects a specialist using structured semantic classification,
confidence checking and the existing configured Gemini fallback. Each specialist
has a filtered MCP toolset. The MCP server validates the host-injected token and
business permissions before accessing SQLite or the handbook retriever.

```text
CompanyAI/
  company_system/     # ADK app: agents, routing, tools, security, database, RAG
  mcp_server/         # 39 tools; STDIO and loopback streamable HTTP
  mcp_client/         # Standalone local demo client
  tests/              # Offline and live regressions
  evaluations/        # Goldens, RAGAS/DeepEval/routing, reports and provenance
  security/           # Deterministic and live injection tests
  scripts/            # Isolated regression and release utilities
  docs/               # Architecture, operation, audit and security guides
```

The ADK application/import name remains `company_system`; its supervisor remains
`company_ai_supervisor`. These stable identifiers are not project branding.

## Requirements and installation

Use Windows PowerShell, the Windows Python launcher and Python **3.14** for the application runtime. The evaluation environment remains pinned to Python **3.12** for its evaluator stack. Gemini
requires a Google AI Studio API key with access/quota for the configured models.
Graphviz system binaries are only needed for optional graph rendering, not normal
routing/retrieval. The application uses local SQLite/Qdrant, not external servers.

From the project directory:

```powershell
# Preserve existing private configuration:
if (-not (Test-Path -LiteralPath .env)) { Copy-Item -LiteralPath .env.example -Destination .env }
# Edit .env privately and set GEMINI_API_KEY, then:
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
```

Setup creates `.venv`, installs the bounded dependencies with tested version
constraints, checks pip/Gemini, requires existing approved SQLite and Qdrant data, and runs
isolated regressions. Setup does not initialize or ingest company data. Never overwrite a
configured `.env`. `.env.example` contains placeholders only.

The repository currently preserves its historical tracked demo SQLite database, while
the newer schema includes revocable MCP sessions. Before first use, back up that file and
run `python initialize_database.py` only after confirming the data is demo-safe; this
applies additive schema creation and seed logic. Build the ignored local vector index with
`python ingest_documents.py`. For non-demo data, point `COMPANYAI_DB_PATH` and
`COMPANYAI_QDRANT_PATH` at separately protected runtime locations instead of committing
their contents.

Configuration uses `GEMINI_LLM_MODEL`, `GEMINI_ROUTER_MODEL`,
`GEMINI_ROUTER_FALLBACK_MODEL`, `GEMINI_ROUTER_MIN_CONFIDENCE`,
`GEMINI_EMBED_MODEL`, `GEMINI_EMBED_DIM`, `GEMINI_EVAL_MODEL`,
`RAG_COLLECTION`, `RAG_TOP_K`, `RAG_MIN_SCORE` and `RAG_MAX_SCORE_DROP`. The score-drop limit keeps only results close to the best semantic match, reducing unrelated context without weakening the minimum score. Optional data overrides are
`COMPANYAI_DB_PATH` and `COMPANYAI_QDRANT_PATH`. Default paths resolve from the
project files, so moving the project does not depend on the previous working copy.
The existing configured Gemini models are preserved; no other provider is substituted.

## Start and use

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1
```

This starts the authenticated CompanyAI local interface on `http://127.0.0.1:8000`.
Use its separate sign-in form, then enter business requests in chat. Never paste
credentials into chat. HR uses the separate credential-administration form. Demo accounts are documented in
[DEMO_CREDENTIALS.md](DEMO_CREDENTIALS.md); they are unsuitable for real deployment.
Use `-Port 8002` for another port or `-Check` for a finite configuration/import check.
The script launches the server itself; activation in a separate child shell is
not required. Stop with Ctrl+C.

## Tests and evaluation

```powershell
powershell -ExecutionPolicy Bypass -File .\run_tests.ps1
powershell -ExecutionPolicy Bypass -File .\setup_evaluation.ps1
powershell -ExecutionPolicy Bypass -File .\run_evaluations.ps1 -Mode offline
.\.venv-eval\Scripts\python.exe -m unittest evaluations.test_ragas_eval evaluations.test_deepeval_eval -v
```

Offline suites use copied SQLite/Qdrant data. Stop active data writers before
copying. Do not run legacy mutation tests directly against company data.

Live suites use Gemini and should run **sequentially**:

```powershell
.\.venv-eval\Scripts\python.exe evaluations\run_routing_eval.py --full
.\.venv-eval\Scripts\python.exe evaluations\run_ragas_eval.py --output evaluations/results/ragas_eval_final_candidate.json
.\.venv-eval\Scripts\python.exe evaluations\run_deepeval_eval.py --full
.\.venv-eval\Scripts\python.exe security\run_prompt_injection_eval.py
```

RAGAS runs all six unchanged policy goldens with the shared async Gemini/LiteLLM/
Instructor evaluator. DeepEval covers the 18 agent cases and separate denial cases.
Defaults pace cases for constrained API quotas; daily exhaustion remains BLOCKED,
not PASS. Reports preserve scores, errors and coverage. See the
[evaluation guide](evaluations/EVALUATION_GUIDE.md).

For the MCP server/client and all-tool transport tests, see
[the MCP guide](docs/MCP_GUIDE.md). Both STDIO and loopback HTTP are preserved.
There are no application-defined MCP resources or prompts.

## Data, security and troubleshooting

- Existing company data, Qdrant storage and handbook are preserved. Database or
  collection resets require an explicit flag and a prior backup. See
  [the database guide](docs/DATABASE_GUIDE.md).
- If Qdrant is locked, stop other CompanyAI/MCP/ingestion processes and retry.
  Do not remove/reset its collection to bypass a lock. An absent collection returns
  `not_ready`; run normal ingestion only after checking the intended path/model.
- For imports, use the matching `.venv` or `.venv-eval` interpreter. For API 429
  errors, inspect whether the limit is per-minute or per-day. Increase pacing or
  wait for reset; do not silently switch model/provider.
- Use the authenticated local interface; stock `adk web` remains an unsupported
  debug interface. Credentials belong only in the secure forms, never chat.
  Protect `.env`, data, caches, backups and conversations with OS permissions.
- Dependency auditing found known advisories with current framework constraints.
  Loopback/telemetry/cache mitigations do not make that scan clean. Read
  [the security guide](docs/SECURITY.md) before real use.
- Retrieval applies both a minimum score and a maximum drop from the best match; broad queries may still return adjacent policy text, and source citations can be misjudged by body-only faithfulness metrics. See
  [the RAG guide](docs/RAG_GUIDE.md) and [quality analysis](evaluations/RAG_QUALITY_ANALYSIS.md).

Additional details: [architecture](docs/ARCHITECTURE.md), [agents](docs/AGENTS.md),
[audit](docs/PROJECT_AUDIT_REPORT.md), [security test report](evaluations/SECURITY_TEST_REPORT.md),
[change log](CHANGELOG.md), and [release status](FINAL_RELEASE_REPORT.md).

## Credential boundary and release remediation

Use `start_project.ps1` (or `python -m company_system.local_web`), not stock
`adk web`, for company access. The host keeps bearer tokens outside ADK state and
model-visible tool calls. Model-facing toolsets withhold login and HR credential
operations; the 39 public MCP tool schemas remain unchanged for trusted clients.
See [security](docs/SECURITY.md), [remediation plan](docs/RELEASE_REMEDIATION_PLAN.md),
and [dependency assessment](evaluations/DEPENDENCY_SECURITY_REPORT.md).
Final-copy creation remains unauthorized while release gates are incomplete.
