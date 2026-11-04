# CompanyAI Evaluation & Security Implementation — Validation Report

## Static inspection and validation performed on the uploaded project copy

| Check | Result |
|---|---|
| Existing agent files | 18 found |
| Existing MCP tool wrappers | 39 found |
| Agents using filtered MCP toolsets | 18/18 |
| MCP tools requiring a session token | All protected tools; only `login` and `ping_companyai` are intentionally public |
| Existing Python files before additions | 80 |
| Python files after implementation | 90 |
| Python syntax compilation after implementation | 90/90 passed |
| JSON datasets/config files | 5/5 parsed successfully |
| Targeted MCP session tests | Role change, account disable, and expiry invalidation passed on copied SQLite DB |
| Targeted login tests | Case-insensitive valid login works; five failed attempts trigger a temporary lockout on copied SQLite DB |
| Expected tools in new agent dataset | 18/18 exist in the MCP server catalog |
| End-to-end agent goldens | 18 cases cover 18/18 routes |

## Changes included in this build

- Added isolated SQLite and Qdrant runtime paths for regression/evaluation runs.
- Omitted local ADK session history from the distributable archive and cleared stale MCP session hashes from its packaged database.
- Changed `run_tests.ps1` to use copied local data by default.
- Added current-user/role/account-state validation to every MCP session-token check.
- Added basic per-username failed-login throttling and generic invalid-credential errors.
- Strengthened router and Policy Agent prompt-injection instructions.
- Marked retrieved RAG passages as untrusted document evidence.
- Added 36 routing goldens covering all 18 routes.
- Added 6 handbook-grounded RAG goldens.
- Added 18 real-agent evaluation cases, one for each specialist route.
- Added 10 security attack/authorization cases.
- Added RAGAS, DeepEval, routing, session-security, and live prompt-injection runners.
- Updated architecture documentation to describe the actual Gemini semantic router.

## Tests not executed in this build environment

The uploaded archive intentionally has no Gemini API key. This build environment also does not have the Qdrant/MCP/RAGAS/DeepEval packages installed. Therefore the following have **not** been claimed as live-passed:

- Windows setup and full dependency resolution.
- MCP server runtime and tool execution.
- Gemini live routing.
- Live RAGAS or DeepEval scoring.
- Live direct/indirect prompt-injection execution.
- End-to-end ADK runner evaluation with the user's API quota.

These checks are included in the project scripts and must be executed on the target Windows machine.

## Commands on the target machine

Application regression:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_tests.ps1
```

Optional live Gemini checks:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_tests.ps1 -Live
```

Install evaluation environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_evaluation.ps1
```

Offline security and regression:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_evaluations.ps1 -Mode offline
```

Full live evaluation:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_evaluations.ps1 -Mode all
```

The implementation should be considered runtime-verified only after these commands pass on the user's Windows environment with the configured Gemini API key and available quota.
