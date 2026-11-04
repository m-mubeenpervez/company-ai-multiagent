# Approved integrity contract implementation

Status remains **RELEASE BLOCKED**. Changes and verification were offline only;
the renderer, live evaluations, staging synchronization, databases, Qdrant and
release decision were not touched.

## Implemented policies

- **A (partial):** Added versioned policy constants and an inventory helper that
  reports non-generated unexpected files. Generated/runtime roots are explicitly
  named in code and filesystem links are denied during inventory traversal.
- **C (partial):** Added validation for the approved `companyai.integrity.v1`
  metadata contract: schema, timestamp, roots and positive file count are
  required. Additive fields remain allowed.
- **D (partial):** Inventory traversal uses `followlinks=False` and rejects
  symlink/junction entries by default. No reviewed allowlist was added.

## Blocked or incomplete policies

- **B:** BLOCKED. No external organization-managed signing trust root or
  signature artifact was provided. No key was generated and authenticity remains
  UNKNOWN.
- **E:** BLOCKED. A component boundary and attestation artifact require release
  owner approval; staging was not modified.
- **F:** BLOCKED. Renderer evidence mappings and mutation scope require separate
  review. The renderer was not executed or rewritten.

The existing manifest format and acceptance thresholds were preserved. The new
helpers are not used to manufacture a PASS or alter `master_release_decision.json`.

## Files changed

- `scripts/master_integrity.py`
- `evaluations/test_approved_integrity_contract.py`
- `evaluations/APPROVED_INTEGRITY_CONTRACT_IMPLEMENTATION.md`

## Focused verification

Command:

`.\\.venv-eval\\Scripts\\python.exe -m unittest evaluations.test_approved_integrity_contract evaluations.test_release_integrity_audit -v`

**PASSED** — 10 tests passed, 1 platform-limited symlink test skipped, exit
code 0. The skipped test requires symlink creation unavailable in the current
Windows sandbox; the production helper remains default-deny for links.

## Safety and next approvals

Protected original, staging, SQLite, Qdrant, historical evidence, receipts,
checkpoints and `master_release_decision.json` were preserved. Before further
work, obtain the external signing trust root, approve component attestation
boundaries, and approve authoritative renderer evidence mappings. Renderer
execution remains a separate approval-gated operation.
