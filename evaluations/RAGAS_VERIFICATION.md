# RAGAS async Gemini verification

Verified in the evaluation/security working copy on 2026-11-03 using
`.venv-eval\Scripts\python.exe` (Python 3.12, RAGAS 0.4.3,
LiteLLM 1.106.6, Instructor 1.17.0).

## Diagnosis

The file initially on disk already used `instructor.from_litellm(acompletion,
async_client=True)` and `adapter="litellm"`. Before editing, the real one-case
evaluation succeeded with scores 1.0 / 0.5 / 1.0. The saved synchronous-client
error did not reproduce with that file. No replacement evaluator, metric-owned
default client, or dependency conflict was found.

Reconstructing the earlier `genai.Client` configuration locally reproduced the
exact exception without making an API request:

- Evaluator: `ragas.llms.base.InstructorLLM`
- Wrapped client: `instructor.v2.core.client.Instructor`
- `is_async=False`
- Failure: `ragas/llms/base.py:1093`, in `InstructorLLM.agenerate`, called by
  the Faithfulness statement-generation step in that configuration.

The earlier configuration chooses RAGAS's Instructor adapter for Google's new
SDK. A synchronous Google client becomes a synchronous Instructor wrapper;
awaiting a metric cannot convert that wrapper into an asynchronous client.

The retained asynchronous configuration creates
`ragas.llms.litellm_llm.LiteLLMStructuredLLM`, with `AsyncInstructor` and
`is_async=True`. All three metric instances retain the same evaluator object
and call awaited `ascore` methods. Runtime guards now enforce both properties.

## Changes

- One evaluator factory shared by normal scoring and `--verify-evaluator`.
- Concise runtime type/model/async diagnostics and identity checks.
- Three Instructor parse retries and two LiteLLM API retries (including
  rate-limit backoff), retaining LiteLLM's existing timeout; exhausted
  API/metric failures remain errors in the report. API retries were added
  after a live Gemini 503 demonstrated that Instructor parse retries alone
  do not retry provider errors.
- Each metric is attempted and its failure recorded separately. Missing,
  nonfinite, and out-of-range scores are errors. Failed cases are excluded
  from averages and make the command exit nonzero.
- ADK runner closure in `finally`, per-case ADK session deletion, MCP token
  revocation even if session deletion fails, and runner reset during cleanup.
- Default evaluation covers all six dataset rows; `--limit` still selects a
  subset. Previous latest reports are archived before replacement.
- Instructor explicitly pinned to the already installed 1.17.0. LiteLLM
  was already explicitly pinned to 1.106.6. No packages were reinstalled.
- Offline tests exercise real async wiring, invalid scores, independent
  metric failures, case continuation, summary exclusion, report archiving,
  and runner closure.

Production routing, agents, tools, database/retrieval implementations, the
dataset, and `run_evaluations.ps1` were not edited.

## Executed verification

| Check | Result |
| --- | --- |
| A: imports using `.venv-eval` | Passed; RAGAS 0.4.3 |
| B: `python -m pip check` | Passed; no broken requirements |
| C: `run_ragas_eval.py --verify-evaluator` | Passed; async structured Gemini response |
| D: `run_ragas_eval.py --limit 1` | Passed; 1 completed, 0 failed |
| E: `run_ragas_eval.py` | Passed; all 6 completed, 0 failed, exit 0 |
| F: `run_evaluations.ps1 -Mode offline` | Passed; exit 0, all 8 isolated scripts and 13/13 additional security checks |
| `python -m unittest evaluations.test_ragas_eval -v` | Passed; 3 tests |

Test D scores: Faithfulness **1.0**, Context Precision **0.5**, Context
Recall **1.0**. See `results/ragas_eval_one_case.json`. These are observed
metric values, not quality thresholds.

Final full-run averages: Faithfulness **0.8333**, Context Precision **0.7083**,
Context Recall **1.0**. The report was also checked against every dataset ID,
with six completed cases, a shared asynchronous evaluator, and finite numeric
scores in [0, 1] for every metric. See `results/ragas_eval_latest.json`.

| Case | Faithfulness | Context Precision | Context Recall |
| --- | ---: | ---: | ---: |
| Intern monthly deadline | 1.0 | 0.5 | 1.0 |
| Remote-work approval | 0.5 | 0.5 | 1.0 |
| Leave entitlements | 1.0 | 1.0 | 1.0 |
| Late arrival | 1.0 | 0.25 | 1.0 |
| Report revision | 1.0 | 1.0 | 1.0 |
| Leave approval | 0.5 | 1.0 | 1.0 |

Two Faithfulness scores of 0.5 and the late-arrival Context Precision score
of 0.25 are measured quality findings, not execution errors. The retrieval
and answer-generation pipeline was not changed to influence these scores.

An intermediate full attempt completed 3 cases and recorded 3 failures from
Gemini 503 responses and an added 60-second request cap. That cap was removed
to preserve existing timeout behavior, and bounded LiteLLM API retries were
enabled. Its report remains in `results/ragas_eval_first_full_attempt.json`;
the final one-case and six-case commands were both rerun successfully afterward.
The originally inspected synchronous-client error report is retained in
`results/ragas_eval_original_error.json`, and the unmodified source's successful
live baseline is in `results/ragas_eval_baseline_success.json`.

The initial sandboxed reproduction could not reach Gemini (WinError 10013),
so live runs used approved network access. The synchronous-client exception
was reproduced separately using the earlier client construction. The full
production pipeline worked in the approved live baseline and test D.

The complete offline command output is saved in
`results/offline_regression_verification.log`. It confirms the Gemini semantic
router, 18 agents, 39 MCP tools, authentication/RBAC, Gemini embedding
configuration, database sanity, and offline RAG smoke checks still pass.
No required test remains pending or blocked. Intermittent Gemini service demand
can still exhaust bounded retries in a future run; such failures are recorded
and return a nonzero exit status.
