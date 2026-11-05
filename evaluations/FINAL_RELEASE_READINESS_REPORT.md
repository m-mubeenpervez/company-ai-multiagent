# Final release readiness — remaining offline work

**Status: RELEASE BLOCKED. VERIFIED:** focused offline remediation is complete. No
live producer, staging acceptance, renderer, dependency operation or full pipeline
was executed. The release decision was not changed.

## Integrity contract decisions

The existing evidence defines manifests as nonempty objects of
`{relative path: {sha256: 64 lowercase hex}}`. The validator now checks that shape,
relative/non-traversing paths, confinement and links. Qdrant validation rejects empty
scans and count mismatches. Focused tests pass.

The following remain UNKNOWN/UNRESOLVED because existing evidence does not define a
contract: exhaustive unexpected-file inventory, manifest authenticity/signing,
malformed initial-integrity schema/version rules, every ancestor link outside
enumerated paths, and complete source/stage tree equivalence. No new manifest format
or trust root was invented.

## Renderer hardcoded claims

The renderer now validates named gates, accepted statuses, report/result counts,
dependency dispositions and receipt/report count agreement before output work. Its
classification remains fail-closed and it was not executed because six current
inputs are MISSING.

Legacy fixed claims still include the 39-tool AST count, “four environments/two
frozen sets,” fixed pip-check scope, frozen-retrieval summary and fixed security /
architecture prose. Supporting current evidence is outside the renderer inputs or
requires missing receipts, so these remain unresolved rather than being guessed.

## Prepared live commands — VERIFIED, NOT EXECUTED

All commands require separate authorization and must run from the working source.
`record_command.py` retains the receipt and log.

Agent acceptance (Gemini/ADK live; isolated disposable runtime; checkpoint provenance
must be checked before resuming):

```powershell
.\.venv-eval\Scripts\python.exe evaluations/record_command.py --label master_agents_final --cwd D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final --report D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\evaluations\results\agent_acceptance_master_final.json -- D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.venv-eval\Scripts\python.exe evaluations/run_agent_acceptance.py --output evaluations/results/agent_acceptance_master_final.json --resume
```

Prompt injection (Gemini live; isolated fixtures/index; no production data; no
current final checkpoint exists, so no `--resume`):

```powershell
.\.venv-eval\Scripts\python.exe evaluations/record_command.py --label master_injection_final --cwd D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final --report D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\security\reports\prompt_injection_master_final.json -- D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.venv-eval\Scripts\python.exe security/run_prompt_injection_eval.py --output security/reports/prompt_injection_master_final.json
```

Staging MCP STDIO (staging access plus Gemini embedding/tool calls):

```powershell
.\.venv-eval\Scripts\python.exe evaluations/record_command.py --label master_stage_mcp_stdio --cwd D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI --report D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI\evaluations\results\master_stage_mcp_stdio.json -- D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI\.venv-eval\Scripts\python.exe evaluations/verify_mcp_release.py --transport stdio --output D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI\evaluations\results\master_stage_mcp_stdio.json
```

Staging MCP Streamable HTTP (same requirements, loopback HTTP):

```powershell
.\.venv-eval\Scripts\python.exe evaluations/record_command.py --label master_stage_mcp_streamable_http --cwd D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI --report D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI\evaluations\results\master_stage_mcp_streamable_http.json -- D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI\.venv-eval\Scripts\python.exe evaluations/verify_mcp_release.py --transport streamable-http --output D:\company_ai_multiagent_gemini_llm_mcp_eval_security_final\.release_candidate\CompanyAI\evaluations\results\master_stage_mcp_streamable_http.json
```

The two staging commands must not be preceded by `sync_staging.py`; that would be a
separate staging mutation. Expected current outputs are the two staging JSON files,
two working-source command receipts and logs. Quota circuit, provenance/account
fingerprints, pacing and disposable paths must be checked first.

## Focused offline verification

```powershell
.\.venv-eval\Scripts\python.exe -m unittest evaluations.test_release_integrity_audit -v
.\.venv-eval\Scripts\python.exe .evaluation_runtime/test_recovery_renderer.py
```

**PASS:** 8/8 integrity tests and 4/4 renderer tests, exit code 0. No live service,
application runner, database mutation or Qdrant mutation was invoked.

## Remaining blockers and order

1. **MISSING/BLOCKED:** separately authorize and run agent acceptance and injection.
2. **MISSING/BLOCKED:** separately authorize and run both staging MCP checks.
3. With all inputs present, perform offline schema/provenance/receipt validation;
   only then consider renderer execution.
4. Define the UNKNOWN manifest attestation contract before further expansion.

Protected original, staging, databases, Qdrant, private configuration, historical
reports, checkpoints and receipts were not modified. `D:\CompanyAI` remains absent;
`master_release_decision.json` remains byte-for-byte unchanged and `RELEASE BLOCKED`.
