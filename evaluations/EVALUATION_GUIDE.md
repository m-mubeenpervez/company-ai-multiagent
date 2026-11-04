# CompanyAI evaluation guide

Use Python 3.12 and `.venv-eval`. Keep application and evaluation dependencies
separate. The verified versions are RAGAS 0.4.3, LiteLLM 1.106.6, Instructor
1.17.0 and DeepEval 4.3.2; source/dependency fingerprints accompany new reports.

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_evaluation.ps1
.\.venv-eval\Scripts\python.exe -m pip check
powershell -ExecutionPolicy Bypass -File .\run_evaluations.ps1 -Mode offline
.\.venv-eval\Scripts\python.exe -m unittest evaluations.test_ragas_eval evaluations.test_deepeval_eval -v
```

Stop ADK/MCP/ingestion writers before tests copy local Qdrant data. Runners create
unique disposable SQLite backup snapshots and Qdrant copies. They never reset
active data. Keep these copies private; do not restore them over production data.

Run live suites sequentially, with the configured Gemini key and adequate quota:

```powershell
.\.venv-eval\Scripts\python.exe evaluations\run_routing_eval.py --full
.\.venv-eval\Scripts\python.exe evaluations\run_ragas_eval.py --verify-evaluator
.\.venv-eval\Scripts\python.exe evaluations\run_ragas_eval.py --output evaluations/results/ragas_eval_final_candidate.json
.\.venv-eval\Scripts\python.exe evaluations\run_deepeval_eval.py --full --output evaluations/results/deepeval_eval_final_candidate.json
.\.venv-eval\Scripts\python.exe security\run_prompt_injection_eval.py
```

Case delays default to 65 seconds in RAGAS/DeepEval and six seconds in routing,
because an actual Gemini free-tier response limited generation to 15 requests per
minute. Each case makes several API calls. Delays do not solve daily limits. On
observed daily quota exhaustion, RAGAS/DeepEval record blocked/unexecuted cases and
stop, rather than inventing scores or spending repeated requests. Failures return
nonzero. `--delay` may be adjusted for the account's actual quota; never run
multiple live suites concurrently on a constrained account.

## RAGAS

All six original `datasets/rag_cases.json` cases remain intact. A single
`LiteLLMStructuredLLM` uses `instructor.from_litellm(acompletion, async_client=True)`
with `adapter="litellm"`. Faithfulness, ContextPrecision and ContextRecall share
that async evaluator and await `ascore`. Model selection remains
`GEMINI_EVAL_MODEL` then `GEMINI_LLM_MODEL`; keys remain `GEMINI_API_KEY` or
`GOOGLE_API_KEY`. No OpenAI provider substitution is used.

Reports retain answers, actual tool queries, contexts, source/page/score metadata,
native judge traces, errors and per-case status. Missing/nonfinite scores are
errors, not successes. Only completed cases contribute to averages. Always inspect
coverage with the average: an average from one successful case is not a six-case
pass. Prior files are archived when a requested output already exists.

Historical baseline/latest and improved reports are preserved. Body-only
faithfulness and citation metadata are different scopes; supplemental citation
checks must be labelled separately rather than silently changing comparable inputs.

## DeepEval

`--full` runs the unchanged 18 agent cases plus two separate denial cases in
`datasets/deepeval_failure_cases.json`. Metrics use async `a_measure`: tool
correctness, answer relevancy, expected-answer correctness (GEval), plus
faithfulness/contextual relevancy for the RAG case. RAGAS already covers contextual
precision/recall, so those are not duplicated. `--judge-arguments` adds optional
argument judging at additional API cost.

DeepEval 4.3.2 does not export the previously referenced `ToolPermissionMetric`.
An explicitly named local `ToolAuthorizationCheck` instead compares attempted
tool names with role scopes and requires unauthorized attempts to be denied by
the server. It is not presented as a DeepEval metric. Separate denial cases also
require the expected forbidden status. Model judging supplements, rather than
replaces, the deterministic security regressions.

Metric exceptions yield null/error records and failed execution, while valid scores
below thresholds remain completed quality failures. Both return nonzero. Runner
cleanup is in finally. Checkpoints retain completed work if interrupted.

Some original agent goldens are underspecified: monthly intern status omits the
month; latest payroll omits a required pay_month; candidate-pipeline requests omit
a stage although the agent asks for one; Finance review-queue wording is broader
than the employee-specific claims tool. These are audit findings, not permission
to invent parameters or silently rewrite expected answers. Confirm intended
product behavior and review separate test corrections before declaring full
quality coverage. Original cases were not removed or modified.

See `FINAL_RELEASE_REPORT.md`, `SECURITY_TEST_REPORT.md` and
`RAG_QUALITY_ANALYSIS.md` for actual release results and blocked tests.

## 2026-11-04 final remediation and safe resumption

The trusted harness creates authenticated sessions in disposable SQLite/Qdrant
copies. Bearers use a host-only context variable, never ADK state/history. Do not
write credential login prompts; use the tested host authentication boundary.
No original RAG or agent reference was changed. `agent_acceptance_cases.json` is a
separate 24-case fixture set:18 explicit-input workflows,4 missing-input checks,
2 denials. It supplements rather than replaces original DeepEval goldens.

Run live suites sequentially, only after the provider deadline. The shared private
quota circuit under .evaluation_runtime stores a key fingerprint and provider
RetryInfo deadline, not the API key. A daily429 stops immediately, suppresses
fallback/retry HTTP calls and blocks other suites. Checking cooldown does not
extend it. Do not delete it to force requests into a known exhausted quota.
Case pacing defaults65 seconds (routing6); HTTP attempts/time and run calls are
bounded. This is a local circuit, not a distributed account-wide rate limiter.

RAGAS, DeepEval, routing, agent acceptance and prompt injection support --resume
with their matching --output path. Checkpoints are atomic output-specific files.
The same selected IDs, dataset/source/index/database fingerprints, model/config
and dependency versions must match. Completed cases (including measured failures)
are reused unchanged; blocked/error cases can run after cooldown. Source/data
changes require a fresh output path. Historical reports without matching provenance
cannot safely be merged. Partially judged write cases require manual review;
these acceptance fixtures use read-only business operations. Do not infer exactly
once writes after an ambiguous transport failure.

Example after cooldown, with unchanged source/data:

```powershell
.\.venv-eval\Scripts\python.exe evaluations/run_ragas_eval.py --resume --output evaluations/results/ragas_eval_remediation_final.json
.\.venv-eval\Scripts\python.exe evaluations/run_deepeval_eval.py --full --resume --output evaluations/results/deepeval_eval_remediation_final.json
.\.venv-eval\Scripts\python.exe evaluations/run_routing_eval.py --full --resume --output evaluations/results/routing_eval_remediation_final.json
.\.venv-eval\Scripts\python.exe evaluations/run_agent_acceptance.py --resume --output evaluations/results/agent_acceptance_remediation_final.json
.\.venv-eval\Scripts\python.exe security/run_prompt_injection_eval.py --resume --output security/reports/prompt_injection_remediation_final.json
```

The native DeepEval Gemini judge retains its prompts, schemas and cost behavior,
but bypasses automatic429 retries and closes both client transports. RAGAS remains
LiteLLMStructuredLLM/AsyncInstructor, async=True, with a single evaluator shared
by all three metrics. Missing/nonfinite scores are errors, never passing metrics.
`cases_run` counts newly attempted cases; `resumed` reports reused completions.
Known cooldown preflight is not a provider attempt. BLOCKED is never PASS.

Exact commands/interpreters/times/exits/counts/logs are in
results/remediation_test_runs.json. Dependency scans have separate ledgers. The
latest 0.9167/1/1 measurement is historical pre-final context, not final acceptance.
Final scores remain null while the quota circuit blocks current evaluation.


## Master finalization refresh ? 2026-11-04

Finalization outputs use separate `*_master_verified.json` paths. Start RAGAS and
DeepEval through their entry points: they now select disposable data before package
initialization captures MCP environments. The fresh-process regression is:
`.\.venv-eval\Scripts\python.exe -m unittest evaluations.test_runtime_isolation -v`.
The injection runner has three independent cases (user/document/MCP output). Never
reuse a checkpoint whose source/configuration/data provenance differs. Current
working `.env` and staging use different API accounts; staging private configuration
is preserved rather than overwritten. Do not combine their live acceptance results.
