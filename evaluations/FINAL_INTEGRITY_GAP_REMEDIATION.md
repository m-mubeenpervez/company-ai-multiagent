# Final integrity gap remediation

Status: **RELEASE BLOCKED**. Inspection and testing were offline only. No
renderer, live model evaluation, staging synchronization, database/Qdrant
operation, dependency operation, or release-decision write was performed.

## Gap classification

| Gap | Classification | Finding |
|---|---|---|
| Exhaustive unexpected-file inventory | CONTRACT DECISION REQUIRED | The established manifests enumerate protected files and hashes; they do not define an exhaustive tree inventory or generated-file allowlist. |
| Manifest authenticity/signing | CONTRACT DECISION REQUIRED | Existing evidence records SHA-256 manifests and rollback locations, but defines no signing key, trust root, or signature format. |
| Malformed initial-integrity metadata | PARTIALLY RESOLVABLE | Empty manifests, invalid entries, traversal/absolute paths and SHA-256 format are validated. Required metadata/version/schema rules are not defined. |
| Ancestor symlinks outside enumerated paths | PARTIALLY RESOLVABLE | Enumerated manifest paths reject directory/file links and escape paths. Unenumerated ancestor/tree links are outside the current contract. |
| Complete source/staging tree attestation | CONTRACT DECISION REQUIRED | Current checks compare owned source code/documents and protected data; no complete source/stage equivalence contract exists. |
| Renderer legacy hardcoded claims | PARTIALLY RESOLVABLE | Required gate/status/count helpers are fail-closed and tested. Several report prose/matrix claims lack dedicated current inputs, so replacing them safely requires an evidence mapping decision. |

No gap met the unambiguous-contract requirement for a new implementation. No
code changes were made.

## Existing protections verified

`validate_manifest` rejects empty/non-object manifests, absolute and traversal
paths, malformed SHA-256 values, root escapes, and links along enumerated paths.
Qdrant probes reject empty or count-inconsistent point sets. Renderer helpers
reject unknown gate names, invalid statuses, inconsistent report counts and
unknown dependency dispositions; missing inputs fail before output writes.

## Focused test

Command:

`.\\.venv-eval\\Scripts\\python.exe -m unittest evaluations.test_release_integrity_audit -v`

**PASSED** — 8/8 tests, exit code 0.

## Required contract decisions

Before further remediation, define and approve: the exhaustive file inventory and
generated-file policy; manifest authenticity/signing and trust roots; initial
integrity metadata schema/version; whether all ancestor directories and links
must be attested; the exact source/staging equivalence scope; and evidence
sources for each renderer prose/matrix claim. These decisions must not weaken
fail-closed classification or convert unknown evidence into PASS.

Protected original, staging source, databases, Qdrant data, historical evidence,
receipts, checkpoints and `master_release_decision.json` were preserved.
