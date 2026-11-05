# Consolidated release closure report

Status: **RELEASE BLOCKED**. This bounded pass performed no live calls, renderer
execution, release pipeline, staging synchronization, data mutation, Git
operation, or release-decision write.

## Work completed

- Confirmed A and C are wired into `scripts/master_integrity.py:129-144`:
  metadata validation runs before manifest acceptance, and rollback/protected-
  original unexpected-file inventories run before integrity checks. Errors raise
  and fail closed.
- Confirmed D default-deny link handling remains active for manifest paths,
  `owned_files()`, and inventory traversal.
- Confirmed existing manifest hash and Qdrant validation remain in the `bad`
  predicate.
- Confirmed renderer mappings remain partially implemented only; no renderer
  behavior was changed.
- Confirmed no metadata producer was created; authoritative ownership remains
  unknown.

## Focused verification

Command:

`.\\.venv-eval\\Scripts\\python.exe -m unittest evaluations.test_approved_integrity_contract evaluations.test_release_integrity_audit -v`

**PASSED:** 13 tests, 1 symlink test skipped, exit code 0.

A disposable temporary Windows junction was then created under `%TEMP%` using
`mklink /J`; `inventory_unexpected()` rejected it with the expected
`RuntimeError`, and the temporary directory was removed. No protected or staging
path was involved. The in-process symlink test remains skipped because ordinary
symlink creation is unavailable, but junction default-deny behavior was directly
verified.

## Verified gates

Previously completed current evidence remains valid: Group A agent acceptance
(24/24 passed), prompt injection (3/3 passed), and staging MCP STDIO and
Streamable HTTP (39/39 tools and schemas each). These results do not waive
integrity-contract blockers.

## Consolidated owner inputs required

### Metadata producer

Provide the exact producer command/path or external workflow; canonical root and
backup semantics; definition of the positive `files` count; timestamp and
additive-field semantics; and owner approval of the future producer. The current
historical metadata lacks `companyai.integrity.v1` and was not rewritten.

### B — manifest authenticity

Provide the organization-managed public trust root, key owner, key ID,
fingerprint, signature algorithm, trust-store location, rotation/revocation
process, and detached signature artifact for the canonical manifest. No key was
generated.

### E — source/staging equivalence

Approve the component inventory and boundaries, explicit exclusions, separate
private/runtime/data attestations, and permitted source/staging differences.

### F — renderer

Approve authoritative evidence for every current report claim; label historical
claims `HISTORICAL`; approve exact renderer output files that may be created or
overwritten; and confirm `master_release_decision.json` remains unchanged unless
separately authorized.

## Exact blockers

The historical metadata producer is unidentified; current metadata therefore
fails the approved schema gate. Manifest authenticity, component attestation,
and renderer evidence/mutation contracts remain externally unapproved. Renderer
execution remains unauthorized.

Protected original, staging, SQLite, Qdrant, historical metadata, receipts,
checkpoints and release decision were left untouched.
