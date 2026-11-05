# CompanyAI project audit

Audit scope: the existing evaluation/security working copy. The protected original
was read only for integrity fingerprints. No Git repository exists in the working
copy; branch, remote and tracked-history inspection is therefore not applicable.
No project repository was initialized and no commit/push/publication was performed.
Disposable empty Git fixtures under .evaluation_runtime were used only to verify
13 real ignore-policy patterns; they are excluded from the candidate.

Before significant edits a timestamped rollback copy preserved all non-generated
files, company data, PDF, datasets, reports and previous provenance. Its location
is recorded in `.release_backup_location`. Python environments and caches were
excluded. The initial source inventory parsed 90 Python modules; the final
inventory is regenerated after additions. Root utilities, PowerShell launchers,
dependency/configuration files, SQL schema and operational documentation were
also inspected.

## Actual inventory and findings

| Area | Finding | Action/status |
|---|---|---|
| Architecture | One Gemini semantic supervisor, 18 domain/auth agents, 39 MCP tools | Preserved; no router replacement, agent renaming or tool-schema changes |
| ADK | Existing API imports/runtime work with ADK 2.13.0 | Clean Python 3.12 install and actual loopback web startup tested |
| Agent context | Instructions refer to session employee ID but did not supply it | Non-secret dynamic context added; server authorization still authoritative; full live verification quota-blocked |
| SQLite initialization | DROP schema executed even without --reset | Existing DB now preserved unless reset explicitly requested; schema path portable |
| Qdrant setup | Setup always rebuilt collection, ignoring reset intent | Preserve existing collection; explicit reset required; no active collection reset in release work |
| Embeddings/router | GenAI clients lacked explicit close/HTTP timeout | Context managers and 120-second request bounds; configured models unchanged |
| Missing policy collection | Embedding API called before readiness check | Return not_ready first, without spending API quota |
| Vector upsert | zip silently truncated mismatched chunk/vector batches | Reject mismatched/nonempty/duplicate-ID batches |
| MCP client | Ignored valid JSON text tool responses in SDK 2.3.0 | Added response parsing fallback; all 39 tools tested over both transports |
| MCP HTTP | SDK supported transport but project CLI exposed only STDIO | Added explicit loopback HTTP option, preserving default STDIO |
| Resources/prompts | No application-defined resources/prompts | Verified empty; documented, no invented functionality |
| Credential lifecycle | Deletion conflicted with session FKs; password rotation retained tokens | Disable/revoke with retained identity; HR replacement flow; rotation revokes sessions |
| Input validation and balances | Negative/nonfinite claims, invalid leave dates/durations and status-only leave decisions | Reject invalid inputs/self decisions; check sufficient balance; atomic/idempotent approval/reversal adjustments |
| DeepEval | Missing ToolPermissionMetric import; metric exceptions still counted completed | Fixed async integration, explicit local authorization check, truthful errors/quality failures and checkpoints |
| Evaluation lifecycle | Reused/deleted runtime directories; inconsistent SQLite file copying | Unique constrained runtime names and SQLite backup API; no runtime deletion needed |
| Cleanup helper | Historical fixture deletion could target active data | Refuses all databases outside .evaluation_runtime |
| Live quota | Observed 15/minute, then 500/day Gemini generation limits | Sequential pacing; daily-quota fail-fast/blocked reporting; no model substitution |
| Security dependencies | Known advisories with incompatible/no advertised fixes | Audit retained; local mitigations documented; no incompatible forced upgrades |
| Startup | Script activated a child shell then merely printed a command | Script now runs loopback ADK web directly; -Check provides a finite import/config check |
| Documentation | Old directory tree and obsolete evaluation defaults | New actual architecture/operation/evaluation/security guides and CompanyAI README |
| Git ignore | Evaluation/security JSON evidence ignored | Keep reports reviewable; ignore private runtime/backups/environments instead |

## Partial/missing behavior and limits

Full model-backed verification of every agent is blocked by Gemini daily quota.
Only Authentication and HR completed full live judging in the paced DeepEval run;
Policy executed and returned grounded data before its judge calls were blocked.
All tool business paths have separate independent transport tests, but that does
not prove every LLM-driven workflow. Original underspecified agent cases need
review (see the evaluation guide). No golden reference was rewritten to hide this.

RAG retains irrelevant trailing passages, body-only citation judging artifacts
and the page 3–4 payroll boundary. No speculative global retrieval change was
made. The improved chunker and all six RAG goldens are preserved.

There is no authenticated public web deployment, production identity provider,
incremental migration framework, multi-process Qdrant service, comprehensive
operational monitoring or verified production backup/restore drill. ADK web is a
local unauthenticated development service. These capabilities were not invented
or labelled complete.

No dependency was removed merely because it was not imported by the entry point;
transitive/framework and dynamic uses were retained. No source/test/report/data
file was judged safely unnecessary enough to delete. Historical documentation and
comparison evidence retain a provenance purpose. See the cleanup report.

The final test and copy disposition, changed-file manifest, security residuals,
and original-backup verification are recorded in `FINAL_RELEASE_REPORT.md`.


## 2026-11-04 remediation (current disposition)

The earlier inventory/findings above are historical. The supported launcher now
uses an authenticated local UI rather than exposing stock ADK web. Login and HR
credential operations run in trusted host code. Bearers are outside ADK state;
model tool declarations omit secret parameters, credential methods are withheld,
and nested response secrets are removed. Root and specialist model callbacks
require a host invocation. HR instructions no longer ask for chat credentials.

Inspection of installed ADK showed that sessions are copies: router metadata now
persists through EventActions, with successful recovery clearing old quota errors.
This does not replace semantic classification or change its threshold/models.
A shared quota circuit honors actual RetryInfo, prevents quota fallback/replay and
supports source/data-validated resumption. Native DeepEval initialization is lazy,
so one async call owns exactly one client and closes both transports even on error.

Pip was patched in rebuildable environments; no framework migration was made.
Fresh scans still fail. All 18 agents remain registered and all 39 wire tools remain;
full current model-driven workflows/routing/judging/injection remain BLOCKED.
Final release, source/data integrity and independent staging checks are recorded
in FINAL_RELEASE_REPORT.md and remediation_* evidence. No final-copy authorization
or risk acceptance has been inferred. No production readiness is claimed.


## Master finalization refresh ? 2026-11-04

New evidence-based fixes: RAGAS/DeepEval selected disposable paths too late, after
CompanyAI package initialization had captured the MCP child environment. A live
RAGAS case routed correctly but received auth_required because host tokens lived in
the test database while the MCP subprocess used the original environment. Isolation
now precedes those imports; fresh-process tests verify all 18 child toolset paths
for both entry points. No router, tool schema, business permission or retrieval
configuration was changed. The failed checkpoint/log is retained. The standalone
connectivity script also now observes quota, and setup refuses missing company data.
Missing canonical MCP/RAG/evaluation/setup docs were added as links or accurate
operational instructions, retaining the detailed existing guides.
