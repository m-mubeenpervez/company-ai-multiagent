# CompanyAI change log

## Unreleased local candidate — 2026-11-03

- Preserve the existing semantic Gemini supervisor, 18 domain/auth agents, 39 MCP
  tools, SQLite/Qdrant architecture and improved section/sentence chunking.
- Make database/collection setup non-destructive by default and resolve paths from
  project files. Missing policy collections now return not_ready before embedding.
- Supply non-secret session identity/date to specialists; retain independent
  server authorization. Close router/embedding clients and bound HTTP requests.
- Correct SDK text-response parsing in the standalone MCP client and add an
  explicit loopback HTTP server option alongside STDIO.
- Revoke sessions after credential changes/removal; preserve referenced account
  history and support HR credential replacement without token resurrection.
- Validate claims/leave inputs; prevent self leave decisions; atomically adjust
  leave balances once per approval/reversal and reject insufficient balances.
- Repair DeepEval's unavailable metric import, use async judging, record genuine
  errors/quality failures, and add independent denial cases without altering the
  original datasets. Add quota pacing/fail-fast, checkpoints and source provenance.
- Use unique isolated runtimes with SQLite backup snapshots. Restrict historical
  cleanup to disposable databases. Validate vector-batch lengths and IDs.
- Add safety/integrity/transport/startup checks, tested dependency constraints and
  actual architecture, data, RAG, evaluation, audit and security documentation.
- Retain all source, tests, reports, data and historical RAG evidence; no destructive
  file cleanup or Git changes. Keep generated caches/environments out of candidates.

This is not a FINAL/production release. Full live acceptance is blocked by Gemini
daily quota and dependency advisories remain under current framework constraints.
See `FINAL_RELEASE_REPORT.md` for exact measured results and copy disposition.


## 2026-11-04 local release remediation (gated)

- Move credential entry/administration into trusted authenticated local forms;
  preserve ADK semantic routing,18 agents and39 native MCP tool schemas.
- Keep host tokens out of ADK state/events/model declarations; redact nested
  credentials and require authenticated host context at model boundaries.
- Persist router metadata through ADK EventActions; clear stale errors and
  report quota unavailability as503.
- Add shared RetryInfo cooldown, atomic provenance-checked case resumption and
  accurate blocked/new-attempt counts; own one async DeepEval client per call.
- Patch pip in rebuildable environments and pin bootstrap 26.3. Keep framework
  versions; document every unresolved advisory and tested resolver incompatibility.
- Add separate 24-case agent acceptance fixtures,13 boundary and13 evaluator tests;
  preserve original goldens, company data, previous reports and rollback points.
- Verify controlled staging locally; retain final directory gate and no production claim.


## Master finalization refresh ? 2026-11-04

- Fix evaluation isolation before package/toolset imports; add fresh-process MCP
  environment regression checks for all 18 agents in both RAGAS/DeepEval runners.
- Make Gemini connectivity checks quota-aware and non-retrying; add two safety tests.
- Require existing company data during setup, without initialization/ingestion.
- Add isolated malicious-MCP-output live acceptance and canonical operational docs.
- Refresh all six dependency scans and primary upstream/advisory metadata; findings
  remain unresolved rather than suppressed.


### Final data and evidence guards

- Require existing SQLite and Qdrant state in normal runtime; keep creation explicit.
- Add full dependency/account/isolation provenance, truthful resumed-attempt counts,
  positive tool-result checks, and HTTP-date Retry-After support.
- Verify 23 focused tests across source/staging/fresh environments and 13 fresh
  boundary checks; preserve all pre-final measurements and interrupted checkpoints.
- Save startup and MCP evidence with output-specific paths, timestamps and source
  hashes, preserving earlier reports. No active data/index reset or dataset edit.
