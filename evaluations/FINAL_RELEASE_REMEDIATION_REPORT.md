# Final release remediation — offline controlled execution

**Status: RELEASE BLOCKED. VERIFIED:** this phase performed only source-side offline
validation. No live Gemini, embedding, DeepEval, RAGAS or staging MCP command was
run. `master_release_decision.json` was not changed.

## Files changed

- `scripts/master_integrity.py`: validates nonempty manifest objects, exact SHA-256
  entries, relative/non-traversing paths, confined roots and directory links;
  separates missing evidence from source mismatches; rejects empty/inconsistent
  Qdrant point scans and checks scanned counts against collection metadata.
- `.evaluation_runtime/render_master_final.py`: validates report schemas/counts,
  dependency dispositions, complete named gate identities/statuses and
  receipt/report count agreement; keeps fail-closed classification and delays the
  test-ledger write until validation has completed.
- `evaluations/test_release_integrity_audit.py` and
  `.evaluation_runtime/test_recovery_renderer.py`: focused regression coverage.
- This report.

A pre-edit snapshot was verified and created at
`.release_backups/final_remediation_20261104T104803654120Z`; the existing staged
SQLite mismatch guard was preserved.

Unknown status applies to whether a future exhaustive-file attestation would
classify additional files as unexpected; current evidence does not prove that.

## Confirmed defects fixed

1. The integrity runner previously recorded a staged database mismatch but omitted
   it from the final failure predicate. That false-PASS path is now covered and
   blocked.
2. Empty Qdrant scans previously passed `all(...)` validation. They now fail, and
   scanned point count must equal the reported collection count.
3. Malformed/empty manifests, invalid hashes, absolute paths, traversal paths and
   link traversal are rejected before comparison.
4. Renderer helper classification previously accepted arbitrary gate names. It now
   requires the complete named gate set and accepted statuses.
5. Renderer report counts, dependency dispositions and receipt/report count
   agreement are validated before report output work. Missing inputs still raise
   and produce no output replacement.

## Intentionally unresolved

- Full unexpected-file inventory and manifest authenticity remain undefined by the
  existing manifest contract; no new attestation format was invented.
- Ancestor directory links outside manifest paths, malformed initial-integrity
  metadata, and complete source/stage tree attestation need a separately reviewed
  contract.
- The full renderer is not executable because six current inputs are missing. No
  report, receipt, checkpoint or historical artifact was promoted.
- Hardcoded prose claims in the legacy renderer require complete gate/evidence
  mapping before safe removal; the renderer was not run with incomplete evidence.

## Focused offline verification

Command, working source and Python 3.12 evaluation interpreter:

```powershell
.\.venv-eval\Scripts\python.exe -m unittest evaluations.test_release_integrity_audit -v
.\.venv-eval\Scripts\python.exe .evaluation_runtime/test_recovery_renderer.py
```

Result: **PASS**, 8/8 integrity tests and 4/4 renderer tests, exit code 0. Tests
cover empty/traversal/absolute/bad-hash manifests, Qdrant empty and count mismatch,
staged-database mismatch, missing evidence, invalid gate identity, invalid counts,
unknown dependency disposition, and failure-before-write behavior. No application
runner, model, database mutation or Qdrant mutation was invoked.

## Missing evidence and authorization checklist

| Required current input | Producer/command | Required access | Expected output |
|---|---|---|---|
| `evaluations/results/agent_acceptance_master_final.json` | `evaluations/run_agent_acceptance.py --output evaluations/results/agent_acceptance_master_final.json` | Gemini/ADK live execution; isolated disposable runtime | JSON report plus `.checkpoint.json` |
| `security/reports/prompt_injection_master_final.json` | `security/run_prompt_injection_eval.py --output security/reports/prompt_injection_master_final.json` | Gemini live execution; isolated fixture/index; no production data | JSON report plus checkpoint |
| `evaluations/results/master_agents_final.command.json` | `evaluations/record_command.py --label master_agents_final ...` wrapping the agent command | Same live authorization as agent run | Command receipt with exit/counts/log path |
| `evaluations/results/master_injection_final.command.json` | `evaluations/record_command.py --label master_injection_final ...` wrapping injection command | Same live authorization as injection run | Command receipt with exit/counts/log path |
| `evaluations/results/master_stage_mcp_stdio.command.json` | Stage `.venv-eval` `evaluations/verify_mcp_release.py --transport stdio` through `record_command.py` | Staging access plus Gemini embedding/tool calls | Independent staging receipt and result JSON |
| `evaluations/results/master_stage_mcp_streamable_http.command.json` | Same verifier with `--transport streamable-http` | Staging access plus Gemini embedding/tool calls and loopback HTTP | Independent staging receipt and result JSON |

Quota circuit, provenance/account fingerprints, disposable paths and pacing must be
checked before any future live run. Historical blocked reports and the 13-row agent
checkpoint remain historical/partial evidence only.

## Next actions

1. Obtain explicit authorization for the live agent and injection suites.
2. Obtain explicit staging authorization for both MCP transports.
3. After those inputs exist, run a separate offline renderer schema/provenance
   validation and only then consider rendering.
4. Define and review the remaining manifest/unexpected-file attestation contract.

Protected original, staging, SQLite, Qdrant, private configuration, goldens,
checkpoints, receipts and historical reports were not modified. No final copy was
created or authorized; the release remains **BLOCKED**.
