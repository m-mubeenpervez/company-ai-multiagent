# Recovery status - RELEASE BLOCKED

Updated 2026-11-04T10:06:21.200325+00:00. This current recovery status supersedes acceptance claims in the historical text below. Final-copy authorization remains **false**; `D:\CompanyAI` is absent.

RAGAS: **PASS execution**, six completed, scores **0.8889 / 1.0 / 1.0**. DeepEval: **FAIL**, 20 attempted, 19 completed, 11 passed, eight assertion failures plus one timeout. Routing: **PASS 36/36**. Agent acceptance: **BLOCKED/incomplete**, 13 recorded passes of 24; 11 unknown outcomes, exact interrupted attempt count unavailable. Injection: **NOT RUN 0/3**. Dependency audit: **FAIL**, 16 unresolved IDs.

Original 103 fingerprints, rollback 481 files, and 16 protected assets: **PASS**. SQLite source/stage/rollback integrity and foreign keys: **PASS**. Qdrant copied-index structure: **PASS**, 17 points, 768 dimensions. Existing source/stage/fresh offline receipts reused; four new renderer tests **PASS**. No live evaluations launched or packages installed during recovery; the pre-existing job was stopped.

Renderer classification/missing-status/dependency filtering defects corrected, but full renderer execution is **BLOCKED** by missing required evidence. No source/staging synchronization was performed. Full 15-file status, per-suite accounting, limitations and evidence paths: [recovery audit](../docs/RECOVERY_AUDIT.md).

---

## HISTORICAL - preserved previous report, superseded by recovery audit above

# Security test report

2026-11-04 (Asia/Karachi). Offline safeguards pass; live injection acceptance is
BLOCKED and dependency audit FAIL. No production-security claim is made.

## Executed current checks

| Scope | Result | Evidence |
|---|---|---|
| Trusted credential/web boundary | PASSED 13/13 in working/staging eval environments | remediation_boundary_sdk_verified.log; remediation_stage_boundary_sdk_verified.log |
| Evaluator/quota/checkpoints/native judge ownership | PASSED 13/13 in working/staging environments | remediation_units_complete.log; remediation_stage_units_complete.log |
| Existing session/MCP security runner | PASSED 13/13 | latest root/stage offline logs |
| Existing business RBAC | PASSED12/12 | offline suite logs |
| Existing MCP security | PASSED10/10 | offline suite logs |
| Release safety: validation, revocation, balances, cleanup paths | PASSED10/10 | offline suite logs |
| Actual STDIO/HTTP catalogs and operations | PASSED 39 tools and39 schemas per transport | remediation_mcp_stdio.json; remediation_mcp_streamable-http.json |
| Actual authenticated HTTP startup/exposure | PASSED | remediation_stage_startup_verified.json:401/403/404 and two non-loopback probes rejected |
| Direct prompt injection | BLOCKED | security/reports/prompt_injection_remediation_final.json |
| Indirect malicious-document/tool-output model injection | BLOCKED | same live report; offline secret-field/untrusted-data safeguards pass separately |
| Installed and locked dependency scans | FAILED with documented advisories | DEPENDENCY_SECURITY_REPORT.md and scan ledgers |
| Public deployment/TLS/enterprise identity/OS ACL certification | NOT RUN | Local development scope only |

The dummy-secret test performs actual ADK request construction, a real MCP identity
call, a second model request and persisted-history inspection. Only generation is
stubbed for this expressly OFFLINE test; it is not Gemini live acceptance. Native
ADK trace spans are forced into an in-memory exporter to verify that passwords,
host bearers and browser cookies do not occur in their attributes. The tests also
check logs/exceptions, generic login failure, credential rotation forms, model tool
schemas, nested unknown session/refresh/API secret fields, unauthorized requests,
Origin/Host/size/path rejection, state forgery, absent debug endpoints, metadata
persistence and recovery after quota errors. MCP bearer injection is necessary on
the protected transport wire but never enters model/event arguments.

All mutable safety tests use disposable SQLite/Qdrant copies. SQL injection,
unknown/invalid tools, forged/expired/revoked tokens, role changes, disabled accounts,
self leave decisions, credential replacement, balance idempotency and input errors
have independent deterministic/transport coverage. This is not an exhaustive role x
tool x record x argument matrix or proof of universal adversarial model resistance.

The final live injection command was actually invoked, exited1, and recorded both
cases BLOCKED with zero provider attempts. It avoids even preparing an embedding
while daily generation cooldown is known. No malicious material entered the active
index. The original reports and failed intermediate attempts are preserved.

Supported login/HR forms authenticate in trusted code before ADK, and model-facing
credential tools are removed. Do not use stock ADK web for real credentials: its
upstream raw transcripts are outside the supported authenticated interface and
were not erased or certified secret-free. Arbitrary unlabelled pasted secrets,
compromised local processes, stolen cookies, HTTP without TLS, public demo accounts,
unreviewed OS ACLs and unresolved advisories remain explicit limits. See
../docs/SECURITY.md. Configured-key scans found no matches outside private config
in inspected source/docs/reports; this is not a claim about every possible secret
format or historical private transcript.

Exact commands/interpreters/local+UTC times/exits/counts/log paths are in
results/remediation_test_runs.json. Scan ledgers and environment checks are separate.
One combined permission review timed out before process creation; the smaller
startup retry succeeded and verified shutdown. No blocked/failed attempt is PASS.


## Master finalization refresh ? 2026-11-04

The separate injection runner now configures three live cases: malicious user,
malicious handbook, and malicious MCP identity output. Its third case executes the
real identity tool, appends adversarial free text at the model-visible boundary and
requires actual delivery before allowing PASS. It checks unauthorized tool calls
and instruction-compliance markers; this finite fixture does not prove universal
injection resistance. Current execution evidence is reported separately from the
older two-case blocked reports. Offline connectivity safety tests pass 2/2.
