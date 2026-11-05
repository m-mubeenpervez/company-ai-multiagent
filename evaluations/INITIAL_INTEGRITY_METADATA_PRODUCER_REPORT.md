# Initial integrity metadata producer report

Status: **BLOCKED — producer not present in the working source**.

## Inspection result

Search for the exact filename `master_initial_integrity.json` found only
consumers:

- `scripts/master_integrity.py` loads it at `main()`.
- `.evaluation_runtime/render_master_final.py` loads it for report context.
- `.evaluation_runtime/recovery_audit.py` loads it for audit context.

No current script, function or command in the working source writes
`evaluations/results/master_initial_integrity.json`. The existing file is a
historical artifact from an earlier recovery/finalization operation. Its current
fields do not include the approved `companyai.integrity.v1` schema field.

## Decision

No producer change was made. Creating a new producer would require guessing the
intended backup-generation workflow, canonical root semantics and file-count
scope, which would violate the requirement to preserve existing metadata
semantics. The historical metadata was not rewritten and no replacement release
artifact was generated.

Once the owner identifies or approves the metadata-producing workflow, it must
emit:

- `schema: companyai.integrity.v1`
- valid nonempty timestamp
- canonical root and backup paths
- positive integer `files`
- all existing additive fields unchanged

The existing validator already accepts additive fields and rejects missing or
invalid required values.

## Verification

The previously focused contract tests remain the applicable offline evidence;
no producer test could be added without a producer. No live API, renderer,
integrity pipeline, dependency, staging, database or Qdrant operation occurred.

Existing `master_initial_integrity.json`, release artifacts, receipts,
checkpoints, staging and protected original were preserved. Release remains
**BLOCKED** until the authoritative producer is identified or separately
approved.
