# CompanyAI recovery audit

**RELEASE BLOCKED. Final-copy authorization: false.**

Offline recovery on 2026-11-04T10:06:21.200325+00:00. No live evaluations were launched, dependencies installed, staging synchronized or final-copy operations performed during recovery. The pre-existing evaluation process tree was terminated; a process query verified zero remaining matching jobs. No Git repository exists and none was initialized.

| Suite | Configured | Attempted | Completed | Passed | Failed | Blocked | Not run |
|---|---:|---:|---:|---:|---:|---:|---:|
| ragas | 6 | 6 | 6 | 6 | 0 | 0 | 0 |
| deepeval | 20 | 20 | 19 | 11 | 9 | 0 | 0 |
| routing | 36 | 36 | 36 | 36 | 0 | 0 | 0 |
| agents | 24 | unknown | 13 | 13 | 0 | 0 | unknown |
| injection | 3 | 0 | 0 | 0 | 0 | 0 | 3 |

RAGAS PASS denotes six completed numeric evaluations, not a quality threshold. Actual Faithfulness **0.8889**, Context Precision **1.0000**, Context Recall **1.0000**. Evaluator: LiteLLMStructuredLLM, async true. Late-arrival Faithfulness is 0.3333; all other cases are 1.0. Historical scores remain separate.

DeepEval FAIL: 11 passes, eight completed assertion failures and one audit-case timeout (19 completed judgments, 20 attempted). Context relevance for policy is 0.1304348; missing/relative input and tool mismatches remain in the original cases. Other failures include finance correctness, document answer relevance, and denial answer relevance. No golden/reference changes were applied. Failed metric names are recorded per case in recovery_audit.json.

Routing PASS: 36/36, accuracy 1.0. Agent acceptance BLOCKED by interruption/no-live restriction: 13 saved workflow passes, at least 13 attempts, 11 without recorded outcome. An in-flight attempt may have been killed; exact attempted/not-run counts cannot be recovered from this checkpoint. The missing outcomes are not asserted to be unattempted, blocked by quota, passes or failures. Injection NOT RUN: all three queued cases had not started. No current quota blockage is inferred.

| Reviewed file | Status |
|---|---|
| .evaluation_runtime/render_master_final.py | ISSUE |
| company_system/database/db.py | PASS |
| company_system/rag/ingest.py | PASS |
| company_system/rag/retriever.py | PASS |
| company_system/rag/vector_store.py | PASS |
| company_system/security/quota.py | PASS |
| evaluations/reporting.py | PASS |
| evaluations/run_agent_acceptance.py | PASS |
| evaluations/test_acceptance_accounting.py | PASS |
| evaluations/test_data_safety.py | PASS |
| evaluations/verify_mcp_release.py | PASS |
| evaluations/verify_startup.py | PASS |
| initialize_database.py | PASS |
| scripts/master_integrity.py | ISSUE |
| security/run_prompt_injection_eval.py | PASS |

PASS in this table means inspected source and syntax plus applicable existing receipts; it does not certify exhaustive live behavior. Full before/start diffs are in evaluations/results/recovery_15_files.diff.

Renderer corrections: fail closed when dependency findings, incomplete suites or missing gate evidence exist; missing result flags no longer imply FAIL; six historically fixed pip findings are separated from the 16 unresolved advisories. Four focused offline regression tests PASS. The renderer remains **BLOCKED / NOT EXECUTED**: six required current reports/receipts are absent and hardcoded broad claims/mapping assumptions need complete-evidence review. We stopped legacy report generation rather than manufacture its inputs. This recovery notice is based on verified saved evidence only.

scripts/master_integrity.py ISSUE: it combines missing live reports and expected staging snapshot differences with actual integrity failure. It was not executed. Separate recovery integrity checks avoid confusing incomplete acceptance with corrupted company data.

Offline evidence reused: source/stage/fresh focused suites 23/23, source/stage offline 11 regression scripts plus 13 security checks, fresh credential/model-payload/history/trace/web-boundary 13/13, and actual authenticated fresh-environment startup PASS. Receipts retain exact commands, cwd, interpreter, timestamps, exit status and logs. New recovery syntax check: 116 owned Python modules PASS; four renderer tests PASS. No successful expensive tests were repeated.

Integrity PASS: protected original 103/103; master rollback 481/481; all 16 protected source and staged assets match their starting hashes. Source .env unchanged from the master snapshot; staged .env matches the prior remediation snapshot and remains independent. Source, staging and rollback SQLite integrity=ok with zero foreign-key errors. Disposable Qdrant probe: 17 points, 768 dimensions, cosine, valid finite vectors and source metadata. Active index was never opened for mutation. All 39 native tool definitions and schemas remain byte-for-byte unchanged in mcp_server/server.py. Existing model-free boundary/security tests remain evidence for authorization, session and secret handling; they do not replace live injection acceptance.

Staging remains an independent snapshot. No unexpected Python/PowerShell preimage changes were found. Its changed generated security receipt reports 13/13 and matches the independently executed stage offline run. Eight pre-recovery source/doc changes were pending synchronization; no synchronization was attempted while acceptance evidence is incomplete. Root live results are not staged live acceptance. Source/stage environment/model/path separation is documented in master_configuration_comparison.json.

Dependency audit **FAIL**: 16 unresolved IDs involving opentelemetry-api, filelock, diskcache and ragas. Six fixed pip findings remain historical. Existing installed-environment and frozen-lock scans remain visible; pip check is dependency consistency only. No external rescan, incompatible upgrade, suppression or risk acceptance occurred.

Remaining gates: investigate nine DeepEval failures/errors; obtain authorized future live completion of the 11 missing agent outcomes and three injection cases; complete independent staging transport acceptance; finish renderer input/mapping validation and controlled synchronization; resolve or separately review dependency/security blockers. No live continuation is authorized by this recovery task. D:\CompanyAI remains absent.

Evidence: evaluations/results/recovery_audit.json; recovery_integrity.json; recovery_audit_corrected.command.json/.log; recovery_renderer_tests.command.json/.log; master_release_decision.json. Existing historical reports/checkpoints/logs and rollback snapshots are preserved.
