# Release integrity utility audit

2026-11-04; working source only. **Release remains BLOCKED.** Neither full utility
was run. No release decision, acceptance criterion or product behavior was changed.

## Evidence and scope

Reviewed `scripts/master_integrity.py`, `.evaluation_runtime/render_master_final.py`,
`docs/RECOVERY_AUDIT.md`, `evaluations/results/master_release_decision.json`, relevant
input availability in `evaluations/results/recovery_audit.json`, and
`.evaluation_runtime/test_recovery_renderer.py` with its existing
`evaluations/results/recovery_renderer_tests.command.json` receipt (four tests passed).
The complete recovery audit, company-data checks and live suites were not repeated.
Line numbers below refer to the files after the one-line correction.

## 1. `scripts/master_integrity.py`

| Finding | Evidence and consequence | Severity / confidence | Disposition |
|---|---|---|---|
| **Confirmed false PASS: staged SQLite mismatch omitted** | `main`, lines 143 and 152–157: records `stage_company_database_matches_source`, but the original final `bad` expression ignored it. An otherwise clean synthetic result with this field false incorrectly allowed PASS/exit 0. | High / High | **FIXED:** add `or not report["stage_company_database_matches_source"]`. Existing preservation requirement is enforced, not relaxed. |
| **Protected-file checks work for listed entries, but manifest validation is incomplete** | Lines 41–58: missing listed files and changed SHA-256 bytes populate errors. Missing keys/malformed JSON cause exceptions. There is no required nonempty original-manifest/count validation: an empty original manifest produces zero checked files and no original error. SHA strings and manifest-relative paths are not schema validated. | High potential false assurance / High | Remains a validation blocker. No actual modified/empty manifest or original corruption is alleged. Broader manifest-schema changes need a defined trusted-input contract. |
| **Path and unexpected-file coverage is incomplete** | `main` joins `initial["backup"]` and manifest keys directly; absolute/`..` keys are not rejected or confined. `owned_files`, lines 28–35, checks file links but not ancestor/directory links. Expected manifest entries are checked, not an exhaustive unexpected-file inventory; newly added Qdrant files are not compared against a baseline inventory. | Medium / High | Scope is listed-file fingerprint verification, not a complete directory attestation. Do not infer absence of unexpected files or path confinement. No new path traversal was performed. |
| **Structural probe has vacuous-success gaps** | Lines 82–102: `all(...)` on an empty point list is true; no equality assertion binds scanned points to `info.points_count`, and no expected collection/dimension/count contract is enforced there. Missing payload can instead raise an exception. | Medium / High | Incomplete validation, not evidence of an empty/corrupt active index. Define required index invariants before expanding checks. No Qdrant probe was run in this task. |
| **Mixed gate status and incomplete error evidence** | Lines 106–119 and 152: missing live reports and staging differences join corruption findings in `bad`. This conservatively prevents PASS, but a generic FAIL cannot identify data corruption. Missing files, permission errors and malformed inputs can abort before writing a fresh report; an older output may remain. Exit is nonzero on such exceptions, but no structured result is guaranteed. | Medium / High | Preserve separate integrity/snapshot/acceptance meanings in consumers. Missing evidence must remain blocked, never be cleared to make this utility pass. |

The current root assertion is not comprehensive path validation and is removable
with Python optimization. Fingerprints provide byte comparisons to the supplied
manifest, not independent proof of manifest authenticity. These limitations remain
visible; this narrow fix does not certify the whole utility for final acceptance.

The utility also invokes `git status` at line 133 and writes the fixed
`master_final_integrity.json` output without archival/atomic replacement at line
159. Those operations were **not invoked**. Full execution is outside this task
and cannot be used as a safe substitute for the focused tests.

## 2. `.evaluation_runtime/render_master_final.py`

**Status: missing evidence plus incomplete validation; unchanged and not executed.**

| Finding | Reproducible evidence | Severity / confidence |
|---|---|---|
| Current entry point is fail-closed, not release-ready | `main:75–76` omits `gate_statuses`; `release_classification:39–58` therefore returns `C. RELEASE BLOCKED`. Missing required JSON raises before output. The focused test forces a missing input and verifies zero report writes/copies. | Blocking evidence gap / High |
| Helper can give a misleading positive classification if called differently | Offline call `release_classification([], [], [], {"arbitrary": "PASS"})` returns `B. VERIFIED LOCAL DEVELOPMENT CANDIDATE`. Required suite identities, gate names and per-case/count consistency are not validated. **Current `main` does not take this positive path.** | High latent defect / High |
| Summary/report consistency is not fully validated | `load:14` only parses JSON. `main` trusts summary counts and inventory, marks inventory registration PASS, and uses an AST count of 39 (`line 92`), which is not native discovery/schema execution. Missing staged transport JSON becomes `{}` (`line 97`), while a receipt can still supply PASS. Source/dataset/account provenance and receipt/report agreement are not checked by the renderer. | High potential false assurance / High |
| Hardcoded claims and nontransactional writes | Lines 125–127 hardcode scan/pip/retrieval statuses; later prose hardcodes verification details and dependency totals. Existing assessment filtering correctly excludes `FIXED` entries, but unknown disposition strings would be dropped rather than validated. Line 115 writes a ledger before later receipt reads; lines 366–393 overwrite reports/decision, so a later failure can leave partial outputs. The archive uses the old starting snapshot, not necessarily each current report preimage. | Medium / High |

The existing `status` helper correctly keeps absent/noncompleted results from PASS,
and unresolved findings or missing gate evidence block classification. Those
controls do **not** validate all surrounding report claims. Missing inputs prevent
safe completion of that validation; no permissive fallback, synthesized report,
classification relaxation or renderer rewrite was made.

Required inputs still absent:

- `evaluations/results/agent_acceptance_master_final.json`
- `security/reports/prompt_injection_master_final.json`
- `evaluations/results/master_agents_final.command.json`
- `evaluations/results/master_injection_final.command.json`
- `evaluations/results/master_stage_mcp_stdio.command.json`
- `evaluations/results/master_stage_mcp_streamable_http.command.json`

**Recommended next action:** retain the execution block. Validate complete input
schemas, named gates/suites, provenance, counts, native MCP evidence, and receipt
agreement before any future rendering; derive claims from that evidence and
preserve output preimages. Missing live evidence needs separate authorization to
obtain, not fabricated placeholders. No such work was started here.

## Changes, rollback and focused tests

Changed implementation: **only `scripts/master_integrity.py`**, one failure-condition
line. Added test: **`evaluations/test_release_integrity_audit.py`**. Renderer unchanged.
This document is the only report updated; the release decision is unchanged.

Verified the script matched its recovery rollback preimage before editing, then
copied and SHA-256 verified a fresh preimage at:
`.release_backups/integrity_audit_20261104T102853948106Z/project/scripts/master_integrity.py`.
Its adjacent `manifest.json` records the hash. Existing snapshots/evidence remain.

Exact test command, from the working source using its Python 3.12 evaluation env:

```powershell
.\.venv-eval\Scripts\python.exe -m unittest evaluations.test_release_integrity_audit -v
```

- **Before fix: FAIL**, exit 1; 3/4 passed. The staged database mismatch failed to
  prevent PASS. Reproduction summary: `.evaluation_runtime/release_integrity_audit_before.log`.
- **After fix: PASS**, exit 0; **4/4 passed**. Covers staged mismatch, clean
  synthetic checks, missing live evidence still preventing PASS, and missing
  renderer input producing no output writes. AST evaluation uses the actual final
  failure expression; no application, database, model or full runner is invoked.
- Exact command/cwd/start/end/exit and unchanged-decision hash check:
  `.evaluation_runtime/release_integrity_audit_receipt.json`.
  Output: `.evaluation_runtime/release_integrity_audit_after.log`.
  Run: **2026-11-04 10:28:55 UTC**.

These four focused passes prove the narrow correction and fail-closed missing-input
behavior; they do not clear the remaining manifest, path or renderer validation gaps.

## Safety and remaining gates

No live evaluations, dependency/environment changes, Git operations, protected-original
or staging modifications, final-directory operations, database resets, ingestion or
migration occurred. Neither full utility nor unrelated test suite was run. No
existing reports, checkpoints, logs, goldens or private configuration were overwritten.
`master_release_decision.json` remains byte-for-byte unchanged and **RELEASE BLOCKED**.

Remaining blockers: complete renderer evidence, validated utility input contracts,
the specific unchecked invariants above, and the previously recorded release gates.
No release PASS or full-utility verification is claimed. Stop after this audit;
live completion or broader remediation requires separate authorization.
