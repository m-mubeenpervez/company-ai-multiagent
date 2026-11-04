# CompanyAI final release owner approval package

Status: **RELEASE BLOCKED — OWNER INPUTS REQUIRED**.

The technical A/C/D enforcement work and focused verification are complete. Group
A and Group B evidence remains current and consistent: 24/24 agent cases passed,
3/3 injection cases passed, and both staging transports passed 39/39 tools and
schemas. No live rerun is required for this handoff.

## Metadata producer

**OWNER ACTION REQUIRED:** identify the authoritative producer by supplying its
exact command/path or external workflow. Confirm:

- canonical source root and rollback/backup semantics;
- meaning of the positive `files` count and its relationship to the manifest;
- timestamp format/timezone and additive-field policy;
- approval that this workflow is the future producer.

The producer must emit `schema: companyai.integrity.v1` while preserving existing
metadata semantics. Required artifact: producer source or command specification,
not a rewritten historical JSON file.

## B — manifest authenticity

**OWNER ACTION REQUIRED:** supply an organization-managed public trust root and
detached signature policy:

- public key/certificate, key owner, key ID and fingerprint;
- signature algorithm and canonical manifest-byte encoding;
- trust-store location and verification command/API;
- rotation, revocation and compromise response process;
- detached signature artifact for the canonical rollback/protected manifest.

No key or signature is generated locally. Hash-only evidence remains
non-authenticating until this input is verified.

## E — source/staging equivalence

**OWNER ACTION REQUIRED:** approve this component inventory and boundaries:

1. Runtime/application code: `company_system`, `mcp_server`, startup/setup scripts.
2. Evaluation/security code and focused tests.
3. MCP tool schemas and declared inventories.
4. Public requirements, lock files and non-secret configuration.
5. Private `.env` and account-specific configuration: hash-only, never values.
6. SQLite, Qdrant, handbook and generated evaluation/runtime data: separate
   data attestations, not byte-for-byte source equivalence.

Approve explicit exclusions for virtual environments, caches, disposable runtime
directories and generated reports, plus the permitted source/staging differences.
Required artifact: signed/owned component inventory with approved exclusions and
preimage/hash evidence.

## F — renderer evidence and mutation scope

**OWNER ACTION REQUIRED:** approve the following mappings:

| Current claim | Authoritative evidence/action |
|---|---|
| Agent inventory and workflows | Current agent inventory and acceptance report; derive or block. |
| MCP tools/transports | Current staging result JSON plus receipts; derive counts/status. |
| SQLite/Qdrant integrity | Validated `master_final_integrity.json`; block if absent or unproven. |
| Dependency status | Dependency assessment; retain FAIL for unresolved advisories. |
| Deployment/TLS/MFA/ACL scope | Label as scope limitation or omit. |
| Historical comparisons/checkpoints | Label `HISTORICAL`; never merge into current status. |
| Final-copy authorization | Existing decision artifact; preserve `false`. |

Approve that renderer execution may create/replace only the explicitly reviewed
release reports and test ledger. Confirm that
`evaluations/results/master_release_decision.json` must remain unchanged unless
separately authorized in writing.

## Numbered approval checklist

1. [ ] Identify and approve the metadata producer and `companyai.integrity.v1` semantics.
2. [ ] Supply and approve the external manifest trust root and signature artifact.
3. [ ] Approve component inventory, exclusions and source/staging differences.
4. [ ] Approve renderer claim mappings and historical labels.
5. [ ] Approve exact renderer output paths and overwrite permissions.
6. [ ] Confirm release decision remains unchanged unless separately authorized.
7. [ ] After inputs are verified, authorize a separate renderer-only execution.

Items 1–3 can be reviewed together as the integrity attestation package. Items
4–6 can be reviewed together as the renderer/reporting package. Item 7 remains a
separate execution authorization.

## Remaining blockers

Missing producer provenance, signing trust root/signature, component-attestation
approval, and renderer evidence/mutation approval prevent final release. The
protected original, staging, SQLite, Qdrant, historical evidence, receipts,
checkpoints and `master_release_decision.json` remain untouched.

**RELEASE BLOCKED — OWNER INPUTS REQUIRED**
