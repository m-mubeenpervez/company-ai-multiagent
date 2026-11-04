# Metadata producer discovery report

Status: **BLOCKED — OWNER IDENTIFICATION REQUIRED**.

## Bounded inspection

Inspected exact filename references in project source/docs, the integrity and
recovery consumers, `scripts/sync_staging.py`, relevant result manifests and
command-receipt locations, and attempted Git history queries. The working copy
has no Git repository (`git log` and `git status` return exit 128), so no commit,
rename or deleted-file history is available.

Relevant files inspected:

- `scripts/master_integrity.py`
- `.evaluation_runtime/render_master_final.py`
- `.evaluation_runtime/recovery_audit.py`
- `scripts/sync_staging.py`
- `evaluations/results/master_initial_integrity.json`
- `evaluations/results/remediation_initial_integrity.json`
- `evaluations/results/*.command.json` receipts and file-audit reports
- `docs/CLEANUP_REPORT.md` and `docs/MASTER_FINALIZATION_AUDIT.md`

## Producer determination

No repository script or command receipt was found that writes, copies, renames,
or generates `evaluations/results/master_initial_integrity.json`. All exact
source references are consumers or documentation references. The related
`remediation_initial_integrity.json` is a separate historical artifact used by
staging/remediation documentation and does not prove the producer of the master
file.

The file was therefore most likely produced by an external recovery/finalization
workflow or manual operation, but the available evidence cannot distinguish
those possibilities. That is not treated as proven provenance.

## Required owner decision

The release owner must identify the authoritative producer or provide its exact
historical command/workflow, including:

1. producer path/function or external tool and invocation;
2. canonical root and backup semantics;
3. definition of the positive `files` count and manifest relationship;
4. timestamp and additive-field semantics; and
5. whether the workflow is the approved producer for future metadata.

Only after that information is supplied can the producer be changed to emit
`schema: companyai.integrity.v1`. The historical metadata was not rewritten and
no replacement artifact was created.

## Remaining blockers

- **B:** External signing trust root, key ownership and signature artifact remain
  unavailable.
- **E:** Source/staging component boundaries and approved exclusions remain
  unapproved.
- **F:** Authoritative renderer evidence mappings and output mutation scope remain
  unapproved.

No source code, tests, staging, protected original, databases, Qdrant data,
receipts, checkpoints, historical metadata or release decision were modified.

**RELEASE BLOCKED — OWNER IDENTIFICATION REQUIRED**
