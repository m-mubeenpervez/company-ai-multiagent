# Release remediation plan and disposition

Updated 2026-11-04 (Asia/Karachi). Working project remains the sole source of truth.
D:\CompanyAI remains uncreated and final copying is not authorized.
Initial plan and previous release report are retained under docs/archive.

| Issue | Severity | Actual evidence | Remediation / decision | Required check and result | Status |
|---|---|---|---|---|---|
| Credentials passed into router/history/auth tools | High | Raw user login reached Gemini; auth instruction contained a demo password; before-tool callback mutated event args | Separate trusted login/HR forms; no credential tools in model surface; host-only bearer context; prehistory and model guards; nested secret removal; log redaction | 13 boundary regressions, actual ADK+MCP identity roundtrip and forced offline spans: PASS in root and staging | FIXED for supported entry points |
| Unauthenticated ADK Web | High | Previous launcher exposed stock dev/session/debug APIs | Supported authenticated loopback UI around existing Runner; exact Host/Origin, ownership/cookies, body caps, no mounted debug APIs | Actual CLI startup,401 anonymous,403 cross-origin,404 debug, two non-loopback interface probes unreachable, closed-port cleanup: PASS | CONTROLLED LOCAL ONLY |
| Router state metadata lost | Medium | Installed InMemorySessionService returns copies; direct mutations did not reliably persist | ADK EventActions state deltas; clear stale error after successful classification; HTTP503 on quota failures | Native ADK state/0.99 confidence and quota recovery regressions: PASS | FIXED |
| Dependency advisories | Advisory-specific low/high | Six targets scanned; primary advisories/metadata and resolver dry-runs retained | Pip25.0.1 to26.3 in four rebuildable environments; bootstrap/locks updated. Framework bounds prevent remaining patches | All six pip checks PASS; runtime/staging-runtime audits FAIL(1 package), eval/staging-eval FAIL(4); frozen sets FAIL | UNRESOLVED:16 distinct IDs |
| Agent model execution coverage | Release blocker | New current-source 24-case entry point exits nonzero on known provider cooldown | Separate 18 explicit workflows,4 missing-input,2 denial fixtures; originals unchanged; per-agent inventory | All 18 registered/tool surfaces inspected; all24 current live cases BLOCKED | BLOCKED |
| Full routing | Release blocker | Controlled attempt:2 correct decisions, then500/day quota;34 incomplete. Previous16/20 report remains historical | Preserve semantic prompts/models/threshold; stop fallback on quota; per-case checkpoints/provenance | Final36-case entry point: all36 BLOCKED, no new requests | BLOCKED |
| Final RAGAS/DeepEval | Release blocker | Actual current factories/entry points and null/empty aggregates | One shared async RAGAS evaluator; native async DeepEval with one lazily owned client/call and finally cleanup |13 evaluator/checkpoint units PASS; final6 RAGAS and20 DeepEval cases BLOCKED | BLOCKED |
| Quota/retries/checkpoint integrity | Medium | Previous partial files lacked resumable validation | Persist provider deadline; bounded calls; atomic output-specific checkpoints; selected IDs/source/data/config/version checks; reject invalid scores/partial writes |13 evaluator units PASS; actual shared circuit prevents subsequent HTTP generation | FIXED, live completion external |
| Injection/security | High scope-dependent | Existing deterministic suites plus new credential/exposure regressions | Keep untrusted-data rules, tool allowlists and authoritative Python RBAC; safe isolated fixtures | Existing13 security checks,12 business checks,10 MCP checks,10 safety tests and13 new boundary checks PASS. Direct/indirect live tests BLOCKED | OFFLINE PASS / LIVE BLOCKED |
| Data and business residuals | Medium | Master SQLite/index fingerprints and isolated safety tests | No schema/policy migration or historical reconciliation. Atomic audit/operation failure policy and legacy constraints need separate reviewed design | SQLite integrity/FKs PASS; existing data/index/goldens unchanged | PRESERVED; residual design unresolved |
| RAG citation/trailing/cross-page limits | Quality | Historical contexts/judge traces; unchanged source/index | Preserve chunking/top-K/threshold/embeddings/references. No speculative score change | Historical reports retained; current six-case validation BLOCKED | DOCUMENTED |
| Staging/integrity | Release blocker | Starting sources matched; controlled sync backups/hashes and own-environment test logs | Working source only; verified transfer, no environment/data overwrite or deletion | Independent constrained installs/startup/offline/13 boundary/13 evaluator tests PASS; final hash evidence | LOCAL CHECKS PASS |
| Final-copy decision | Authorization/release blocker | Explicit user instruction and existing copy-decision report | No final copy, move, rename or publishing | D:\CompanyAI does not exist | KEEP GATED |

The provider deadline observed on 2026-11-04 is approximately12:59:59 Asia/Karachi
(07:59:59 UTC). It is a retry deadline, not a guarantee of available quota.
No additional generation requests were sent after confirming the daily limit.
Unresolved risks are not accepted by silence. No breaking migration was attempted.


## Master finalization follow-up (2026-11-04)

| Issue | Severity | Evidence | Action/test | Status |
|---|---|---|---|---|
| MCP child env captured before evaluation isolation | High: invalid evaluation and wrong data target | Failed live RAGAS first case; fresh-process child-env diagnosis | Isolate first in RAGAS/DeepEval; check all 18 toolsets in fresh processes | FIXED; focused suite 23/23 |
| Runtime SQLite may create an empty replacement | High: data safety | sqlite3.connect default behavior in db.py | mode=rw; explicit initializer owns creation; missing-path and explicit-init tests | FIXED; disposable-path tests pass |
| Missing Qdrant runtime path may be initialized | Medium: data safety | QdrantClient default creation in vector_store.py | Require persisted meta for runtime; explicit ingestion/recreation owns creation; no-embedding missing-index test | FIXED |
| Connectivity verifier bypasses shared circuit | Medium: quota safety | verify_gemini.py direct client call | Check circuit; no SDK replay; generic errors; two regression tests | FIXED |
| Retry-After HTTP-date ignored | Medium: provider safety | Numeric-only parser | Parse HTTP-date and test numeric/date/invalid headers | FIXED |
| Resumed agent/injection completions counted as new attempts | Medium: report integrity | cases_run summed resumed attempted flags | Exclude completed checkpoint IDs; record resumed separately | FIXED; no-new-invocation regression tests |
| Positive agent smoke could pass auth_required output | Medium: acceptance integrity | Only name/nonempty text checked | Require actual success tool result for positive expected calls | FIXED; rejection regression test |
| Checkpoint lacked full environment/account/data-isolator fingerprint | Medium: integrity | Old provenance map omitted runtime_isolation.py and full distributions | Include isolator/requirements/locks/full installed versions and account hash | FIXED; old incompatible results not resumed |
| Malicious MCP-output live case absent | Medium: security coverage | Prior injection runner only two cases | Add third actual-tool/adversarial-output case | IMPLEMENTED; final live acceptance pending |
| Four packages/16 advisories | High/medium/low: see register | Six fresh scans and primary metadata | No compatible fixes; no overrides or accepted risk | UNRESOLVED / audit FAIL |
| Diluted policy context | Medium: quality | Actual DeepEval relevance 0.1364; RAGAS verdicts [1,0,0,0,0] | Retain failure; require separate measured context-assembly experiment | UNRESOLVED; no score-oriented changes |
| Underspecified original goldens | Medium: evaluation validity | Intern month and other required inputs absent | Preserve originals; separate explicit-input/missing-input suite | REVIEW REQUIRED |
| Different source/stage private API accounts | Medium: acceptance scope | Private comparison; non-secret settings match | Preserve both configurations; independently test staged scope | EXPLICIT LIMITATION; no overwrite |

The first six-case finalization RAGAS run completed at 1/1/1, but precedes the final
missing-data/provenance guards. It remains separate evidence. Final acceptance is
restarted with `*_master_final.json` outputs after the guarded code freeze. Blocked
or measured failing cases must remain visible; no historical scores are merged.
