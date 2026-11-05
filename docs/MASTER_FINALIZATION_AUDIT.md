# CompanyAI master finalization audit

2026-11-04, Asia/Karachi. Working source is the only implementation tree;
staging is a controlled snapshot. D:\CompanyAI is not authorized.

| Area | Existing state | Verified evidence | Required action |
|---|---|---|---|
| Architecture | ADK/Gemini supervisor, 18 agents, 39 wire tools | Actual registration and domain catalog; previous current boundary suite | Preserve |
| Agents | 24 separate cases; prior live runs blocked | Original and explicit-input datasets; agent inventory | Run actual current model workflows; report failures honestly |
| Semantic routing | 36 goldens, Gemini classifier retained | Native RoutingDecision/EventActions tests; catalog | Full sequential live run |
| MCP | Both transports and all wire schemas verified | remediation_mcp_stdio.json / remediation_mcp_streamable-http.json | Staged transport checks; preserve schema hashes |
| SQLite | Existing company data, zero FK errors | Initial snapshot hashes; offline isolated suites | Final read-only integrity/hash check |
| Qdrant | Existing persisted handbook vectors | Snapshot/index hashes; live RAGAS retrieval | Preserve active index; no reingestion |
| RAG | Improved section-aware chunks, unchanged configuration | Historical quality analysis and current live contexts | Current six-case evaluation; no speculative score changes |
| Authentication/RBAC | Trusted forms and host-only bearers | 13 boundary tests; business/MCP/security suites | Preserve; no secrets in reports |
| RAGAS | Actual async structured generation succeeds | master_ragas.log | Fix reproduced isolation defect, then full current run |
| DeepEval | Async/native single-client judge and checkpoints | master_isolation_units.log, 16 tests | Fix same import-order defect; run 20 cases |
| Security | Local authenticated UI; residual local HTTP/OS limits | docs/SECURITY.md; boundary/trace tests | Add third malicious MCP-output case; actual live tests |
| Dependencies | 16 unresolved advisory IDs in four packages | Six fresh scans; refreshed primary advisories and PyPI metadata | No compatible patch; retain FAIL and require separate risk decision |
| Startup/setup | Fresh constrained 3.12 environments previously installed | Retained installation logs plus fresh six pip checks | Prevent missing-data creation and quota bypass; focused safety tests |
| Documentation | Detailed guides exist, four canonical paths missing | File inventory | Add canonical links/setup guide and correct stale setup/output claims |
| Cleanup | Historical evidence and backups are required | Full file classification and verified new rollback | Delete nothing without demonstrated safe need |

Backup: `.release_backups/master_20261103T231018Z/project`, 481 files verified.
The previous remediation backup also matches its complete manifest. All 103 original
fingerprints match. No repository exists (git status 128); none was initialized.
See `evaluations/results/master_initial_integrity.json` for exact paths/timestamp.

The current source and stage use different private API accounts. Their non-secret
model/retrieval settings match. Private configuration is preserved, not overwritten.
Do not treat source live results as independent staged live acceptance.

The source review found a concrete runtime defect: eager package initialization
constructed MCP toolsets before RAGAS/DeepEval chose disposable paths. Host tokens
and MCP servers consequently used different databases. Both entry points now isolate
first. Fresh-process tests inspect all 18 toolset environments, avoiding the cached
imports that hid this issue in earlier unit fixtures. Failed live evidence remains.

Static parsing/compilation and file classification are recorded separately; they do
not certify absence of every dead code path, race, security flaw or business-policy
gap. No speculative HR migration/reconciliation, framework replacement, tool-schema
change, cleanup deletion or production-readiness claim was made.
