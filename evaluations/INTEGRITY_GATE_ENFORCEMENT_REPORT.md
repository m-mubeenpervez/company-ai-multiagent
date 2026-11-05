# Integrity gate enforcement report

Status: **RELEASE BLOCKED**. Only the working-source integrity script and
focused tests changed. No renderer, release pipeline, live service, staging,
protected original, SQLite, Qdrant or release-decision operation was performed.

## Changes

`scripts/master_integrity.py` now calls `validate_initial_integrity_metadata()`
immediately after loading `master_initial_integrity.json`. It then calls
`inventory_unexpected()` for both rollback and protected-original roots using the
approved manifests as expected inventories. Any unexpected file, missing root,
directory/file link or traversal error raises and fails closed before acceptance.
Existing manifest hash checks, `owned_files()` link checks and Qdrant structural
validation remain active.

Current metadata predates the approved `companyai.integrity.v1` field and will
therefore fail closed until the metadata producer supplies the approved schema;
no metadata was rewritten in this task.

## Focused tests

Command:

`.\\.venv-eval\\Scripts\\python.exe -m unittest evaluations.test_approved_integrity_contract evaluations.test_release_integrity_audit -v`

**PASSED** — 12 tests passed, 1 symlink test skipped, exit code 0. The tests
cover actual `main()` fail-closed behavior for metadata and inventory errors,
unexpected-file detection, traversal/path validation, manifest hashes, Qdrant
count validation, and existing renderer/integrity regressions.

The symlink test remains skipped because link creation is unavailable in the
sandbox; production inventory behavior remains default-deny. No permissions or
protected/staging links were changed.

## Remaining blockers

- **B:** External organization-managed signing trust root and signature artifact
  are still unavailable; authenticity remains UNKNOWN.
- **E:** Source/staging component boundaries and permitted private/runtime
  differences still require release-owner approval.
- **F:** Renderer evidence mappings and mutation scope still require approval;
  renderer was not executed.
- The approved metadata producer must emit `companyai.integrity.v1` before a
  normal integrity run can pass.

Protected original, staging, databases, Qdrant, historical evidence,
`master_release_decision.json`, receipts and checkpoints were preserved.
