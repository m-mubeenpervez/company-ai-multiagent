# Final release verification preflight

Status: **RELEASE BLOCKED**. This was read-only verification. The renderer and
full release pipeline were not executed.

## Current evidence

All six current renderer inputs exist, parse as JSON, and are current Group A/B
receipts or reports:

| Input | Result |
|---|---|
| `evaluations/results/agent_acceptance_master_final.json` | VERIFIED: 24 configured/completed/passed, 0 failed/blocked |
| `security/reports/prompt_injection_master_final.json` | VERIFIED: 3 run/passed, 0 failed/blocked |
| `evaluations/results/master_agents_final.command.json` | VERIFIED: PASS, exit 0, agrees with report |
| `evaluations/results/master_injection_final.command.json` | VERIFIED: PASS, exit 0, agrees with report |
| `evaluations/results/master_stage_mcp_stdio.command.json` | VERIFIED: PASS, exit 0; 39 tools/schemas passed |
| `evaluations/results/master_stage_mcp_streamable_http.command.json` | VERIFIED: PASS, exit 0; 39 tools/schemas passed |

Staging result files are also present and valid:

- `.release_candidate/CompanyAI/evaluations/results/master_stage_mcp_stdio.json`: 39/39 tools, 39 schemas, all passed.
- `.release_candidate/CompanyAI/evaluations/results/master_stage_mcp_streamable_http.json`: 39/39 tools, 39 schemas, all passed.

Receipt paths, result paths, exit codes, counts and timestamps agree. Unique
logs were used; historical logs were not overwritten. No historical evidence was
substituted.

## Integrity and remaining blockers

Previously identified integrity items remain **UNKNOWN / NOT VERIFIED**, because
the existing evidence contract does not define them: exhaustive unexpected-file
inventory, manifest authenticity/signing, malformed initial-integrity metadata
rules, ancestor links outside enumerated paths, and complete source/staging tree
attestation. These remain release blockers and are not silently waived.

Legacy renderer hardcoded claims remain a documented risk. Some prose and matrix
rows are not derived from dedicated current inputs (for example public deployment
scope and broad integrity statements). The renderer's fail-closed gate helper is
tested, but its current `main()` still has legacy assumptions and writes release
artifacts; this preflight does not treat that as a clean release gate.

## Renderer readiness and mutation scope

Required JSON inputs are available, but execution is **NOT APPROVED in this
preflight**. The command would be:

```powershell
.\\.venv-eval\\Scripts\\python.exe .evaluation_runtime\\render_master_final.py
```

from the working source directory. It would write or replace
`FINAL_RELEASE_REPORT.md`, `evaluations/AGENT_ACCEPTANCE_REPORT.md`,
`evaluations/SECURITY_TEST_REPORT.md`, `evaluations/results/master_test_runs.json`,
and `evaluations/results/master_release_decision.json`, and may create archive
copies under `docs/archive`. Therefore it can overwrite current release outputs
and modify the release decision; it was not run.

## Recommendation

**RELEASE BLOCKED — not ready for renderer approval.** Resolve or explicitly
review the UNKNOWN integrity contracts and renderer legacy evidence mappings,
then authorize renderer execution separately. No protected original, staging
source, database, Qdrant data, historical evidence, or release decision was
modified by this preflight.
