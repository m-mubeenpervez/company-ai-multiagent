# Release integrity contract decisions

This proposal records decisions needed to turn the remaining UNKNOWN integrity
items into implementable, reviewable checks. It does not approve or implement a
new trust model. Current status remains **RELEASE BLOCKED**.

## A. Unexpected files and generated-file allowlist

| Aspect | Proposal |
|---|---|
| Existing evidence | `master_integrity.py` verifies listed manifest entries and selected source/data comparisons; it does not enumerate every tree entry. Existing reports explicitly call exhaustive inventory undefined. |
| Missing contract | Whether the manifest is exhaustive, which runtime/cache/generated paths are permitted, and whether transient files are ignored or attested. |
| Options | (1) Exhaustive manifest plus versioned generated-file allowlist. (2) Baseline inventory with explicit ignored roots and per-run unexpected-file report. (3) Keep listed-file scope and document it as non-exhaustive. |
| Risks | Option 1 increases churn from caches/runtime files; option 2 can miss newly ignored paths; option 3 leaves release-time false assurance. |
| Recommendation | Option 2: attest all non-ignored files and require a reviewed, versioned ignore/allowlist. It fits the existing tree checks without pretending generated state is immutable. |
| Likely impact | `scripts/master_integrity.py`, focused integrity tests, manifest/attestation documentation. |
| Approval | Human approval of ignored roots and generated-file policy; no secret required. |

## B. Manifest authenticity, signing and trust root

| Aspect | Proposal |
|---|---|
| Existing evidence | SHA-256 manifests and rollback locations exist; no signature, key, or trust root is defined. |
| Missing contract | Who signs manifests, where the public trust root is stored, key rotation/revocation, and whether local development may use unsigned manifests. |
| Options | (1) Offline signing with an organization-managed public key and verified signature file. (2) Trusted CI/release attestation service. (3) Hash-only manifests with an explicit non-authenticating label. |
| Risks | Option 1 creates key custody/rotation obligations; option 2 adds service dependency; option 3 does not protect against manifest replacement. |
| Recommendation | Option 1 for a local release, only after security approval and provision of an externally managed public trust root. Do not generate keys in this project. |
| Likely impact | Manifest producer/verifier, documentation, focused tamper/signature tests. |
| Approval | Security/release-owner approval and an authorized signing public key/trust-root procedure are required. |

## C. Initial-integrity metadata schema and version

| Aspect | Proposal |
|---|---|
| Existing evidence | The runner consumes `master_initial_integrity.json` fields such as `backup`; manifest validation now rejects empty or malformed entries. |
| Missing contract | Required metadata fields, schema version, path semantics, timestamp format, producer identity, and behavior for unknown fields. |
| Options | (1) Versioned JSON schema with required fields and reject-unknown policy. (2) Versioned schema allowing additive unknown fields. (3) Keep field-presence checks only. |
| Risks | Reject-unknown harms forward compatibility; permissive schemas can hide typos; option 3 preserves ambiguity. |
| Recommendation | Option 2: require a version and security-critical fields, allow documented additive fields, reject wrong types and missing required values. |
| Likely impact | `scripts/master_integrity.py`, metadata producer, schema fixtures/tests. |
| Approval | Human approval of the canonical schema/version; no secret required. |

## D. Ancestor directory and symlink scope

| Aspect | Proposal |
|---|---|
| Existing evidence | Enumerated manifest paths reject directory/file links and root escapes. Unenumerated ancestors/tree links are not fully attested. |
| Missing contract | Whether every ancestor from each attested root must be a real directory and whether links are categorically forbidden or allowlisted. |
| Options | (1) Reject all symlinks/junctions in every attested root. (2) Permit an explicit reviewed link allowlist with resolved-target confinement. (3) Check only manifest paths. |
| Risks | Option 1 may reject legitimate deployment links; option 2 adds complex platform-specific policy; option 3 leaves traversal risk. |
| Recommendation | Option 2, with default deny and root confinement; use option 1 for release staging if no legitimate links exist. |
| Likely impact | `scripts/master_integrity.py`, Windows junction/symlink fixtures, focused tests. |
| Approval | Human approval of any allowed links; no secret required. |

## E. Source/staging equivalence and attestation

| Aspect | Proposal |
|---|---|
| Existing evidence | Current checks compare owned source code/documents and selected data/Qdrant assets; staging is an independent snapshot with separate private configuration. |
| Missing contract | Which files must match byte-for-byte, which may legitimately differ (environment/private data), and how runtime-generated state is handled. |
| Options | (1) Full tree attestation with explicit private/runtime exclusions. (2) Component manifest attestation for code, schemas, tests and declared assets. (3) Keep current selected-file comparison. |
| Risks | Full-tree comparison leaks or couples private configuration; component scope can omit a new security-relevant file; option 3 leaves divergence unknown. |
| Recommendation | Option 2 with a versioned component inventory and explicit preimage/hash evidence; keep private `.env`, virtualenvs and runtime data separately attested. |
| Likely impact | `scripts/master_integrity.py`, staging verification utility, component manifest and tests. |
| Approval | Release owner must approve component boundaries and permitted staging differences. |

## F. Renderer prose and matrix evidence mapping

| Aspect | Proposal |
|---|---|
| Existing evidence | Renderer validates several schemas and named gates, but emits legacy prose/matrix rows that are not all backed by dedicated current inputs. It also writes release reports and the decision file. |
| Missing contract | Authoritative source for each claim, required status when evidence is absent, and whether prose may contain historical/contextual statements. |
| Options | (1) Evidence-keyed templates: every claim maps to a validated input field or is omitted. (2) Separate historical/context section with explicit provenance labels. (3) Keep hardcoded prose and rely on fail-closed classification. |
| Risks | Option 1 can make reports less readable; option 2 increases template complexity; option 3 permits contradictory claims even when classification is blocked. |
| Recommendation | Combine options 1 and 2: derive current status/matrix rows from validated evidence, label historical/contextual text, and fail closed on missing mappings. |
| Likely impact | `.evaluation_runtime/render_master_final.py`, renderer regression tests, report template fixtures. |
| Approval | Human approval of authoritative evidence mappings and report mutation scope; no secret required. |

## Dependencies and implementation sequence

1. Approve A, C and D together because path inventory and metadata schema define
   what an attestation means.
2. Approve B before claiming manifest authenticity; implementation cannot begin
   without an authorized trust root.
3. Approve E after A/C/D so source and staging inventories use the same rules.
4. Approve F before any renderer execution; current release decision and report
   outputs must remain protected until mappings are tested.
5. Implement each decision in isolated commits/changes with malformed, traversal,
   symlink, unexpected-file, tamper, provenance, count and no-write-on-failure
   tests. Run only focused offline tests before any renderer approval.

## Remaining blockers

Until these policies are approved and implemented, exhaustive inventory,
authenticity, metadata scope, ancestor coverage, complete staging attestation and
renderer claim provenance remain UNKNOWN. Existing live results do not waive
these integrity gates.

**RELEASE BLOCKED — CONTRACT APPROVAL REQUIRED**
