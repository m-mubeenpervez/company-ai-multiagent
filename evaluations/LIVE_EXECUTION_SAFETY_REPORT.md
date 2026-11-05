# Live execution safety report

Status remains **RELEASE BLOCKED**. This patch made only offline safety changes; no
live evaluation, staging command, embedding request, database operation, or
protected-original access was performed.

## Quota preflight

`evaluations/verify_mcp_release.py` performed disposable runtime setup before any
explicit quota check. Because its retrieval verification can invoke Gemini
embeddings, this left a preflight gap. It now calls the existing
`company_system.security.quota.check_quota()` interface before runtime setup.
When the circuit is blocked, setup and all embedding/tool work are prevented.
No quota policy, model, threshold, or evaluation behavior changed.

## Log and receipt preservation

`evaluations/record_command.py` previously opened `<label>.log` with write mode,
which could overwrite prior evidence. It now accepts `--log`, requires the path
to remain inside the working tree, rejects an existing log, and rejects an
existing `<label>.command.json` receipt. Receipt semantics and destination remain
unchanged. Existing logs and receipts were not touched.

## Focused offline verification

Command:

`.\\.venv-eval\\Scripts\\python.exe -m unittest evaluations.test_live_execution_safety evaluations.test_release_integrity_audit -v`

**PASSED** — 11/11 tests, exit code 0. This includes quota-block prevention,
existing-log preservation/rejection, and the existing release-integrity tests.

Command:

`.\\.venv-eval\\Scripts\\python.exe .evaluation_runtime/test_recovery_renderer.py`

**PASSED** — 4/4 tests, exit code 0.

## Prepared commands (verified, not executed)

All commands below use unique attempt log paths. They require explicit approval
for their group and the live services stated below. The recorder writes receipts
under the source working tree at `evaluations/results/<label>.command.json`.

### Group A — live evaluation

Agent acceptance (Gemini/ADK access; resumes the existing checkpoint; isolated
runtime and quota controls are required):

```powershell
.\\.venv-eval\\Scripts\\python.exe evaluations/record_command.py --label master_agents_final --cwd D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final --log evaluations/results/master_agents_final_attempt_20261104.log --report D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\evaluations\\results\\agent_acceptance_master_final.json -- D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.venv-eval\\Scripts\\python.exe evaluations/run_agent_acceptance.py --output evaluations/results/agent_acceptance_master_final.json --resume
```

Prompt injection (Gemini access; isolated fixtures/index; no current checkpoint
exists, so quota fail-fast and no automatic retry are required):

```powershell
.\\.venv-eval\\Scripts\\python.exe evaluations/record_command.py --label master_injection_final --cwd D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final --log evaluations/results/master_injection_final_attempt_20261104.log --report D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\security\\reports\\prompt_injection_master_final.json -- D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.venv-eval\\Scripts\\python.exe security/run_prompt_injection_eval.py --output security/reports/prompt_injection_master_final.json
```

### Group B — staging MCP acceptance

These commands require staging access and Gemini embedding access. They must run
from the independent staging snapshot and must not run `sync_staging.py`.

STDIO:

```powershell
.\\.venv-eval\\Scripts\\python.exe evaluations/record_command.py --label master_stage_mcp_stdio --cwd D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI --log evaluations/results/master_stage_mcp_stdio_attempt_20261104.log --report D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI\\evaluations\\results\\master_stage_mcp_stdio.json -- D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI\\.venv-eval\\Scripts\\python.exe evaluations/verify_mcp_release.py --transport stdio --output D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI\\evaluations\\results\\master_stage_mcp_stdio.json
```

Streamable HTTP:

```powershell
.\\.venv-eval\\Scripts\\python.exe evaluations/record_command.py --label master_stage_mcp_streamable_http --cwd D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI --log evaluations/results/master_stage_mcp_streamable_http_attempt_20261104.log --report D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI\\evaluations\\results\\master_stage_mcp_streamable_http.json -- D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI\\.venv-eval\\Scripts\\python.exe evaluations/verify_mcp_release.py --transport streamable-http --output D:\\company_ai_multiagent_gemini_llm_mcp_eval_security_final\\.release_candidate\\CompanyAI\\evaluations\\results\\master_stage_mcp_streamable_http.json
```

The pre-existing `master_agents_final.log` and `master_injection.log` remain
preserved. Reusing any label after a receipt is created requires a new label;
the recorder intentionally refuses overwrite.

## Remaining risks and approvals

The six current evidence inputs remain missing. Group A requires explicit
authorization for live Gemini evaluation and quota availability. Group B requires
explicit authorization for staging execution, staging isolation, and Gemini
embedding availability. A quota circuit block, account mismatch, unexpected
overwrite, or staging change must stop that group. Release classification and
`master_release_decision.json` remain unchanged and blocked.
