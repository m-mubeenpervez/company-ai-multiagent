# Final blocker closure audit

Status: **RELEASE BLOCKED — FINAL APPROVALS REQUIRED**. This audit was
read-only. No code, tests, staging, data, renderer or release decision changed.

## Actual enforcement

| Policy | Finding | Evidence |
|---|---|---|
| A: unexpected inventory | **NOT ENFORCED** | `inventory_unexpected()` exists at `scripts/master_integrity.py:54`, but `main()` never calls it and its result cannot affect `bad` at line 241. The focused test calls the helper directly only. |
| C: metadata schema | **NOT ENFORCED** | `validate_initial_integrity_metadata()` exists at line 37, but `main()` loads metadata at line 129 without invoking it. The test validates the helper only. |
| D: links | **PARTIALLY ENFORCED** | `owned_files()` rejects links during its actual `main()` traversal (line 150), and manifest paths reject links. The new inventory helper is not in the main path; unenumerated tree links remain outside enforcement. |
| Manifest path/hash | **ENFORCED** | `main()` invokes `validate_manifest()` for rollback and protected-original manifests (lines 132 and 138), then compares listed hashes. |
| Qdrant checks | **ENFORCED** | `main()` invokes `validate_qdrant_points()` during the disposable structural probe (line 181) and includes invalid results in `bad`. |
| False PASS risk | **REMAINS** | A/C helper failures cannot currently influence the release integrity result because their helpers are not called by `main()`. |

Existing focused tests pass for helper behavior and prior fail-closed checks, but
they do not prove A/C enforcement through `main()`.

## Approval package

### B — manifest signing

Required external input: an organization-managed public key or certificate,
provided out-of-band with owner, fingerprint, algorithm, key identifier,
rotation/revocation procedure and trust-store location. The signature artifact
should be a detached signature over the canonical manifest bytes plus schema
version and signer key ID. No key was generated. Until the trust root is
provided and verified, authenticity is **UNKNOWN/BLOCKED**.

### E — component attestation

Minimal inventory requiring approval:

- source/runtime code: `company_system`, `mcp_server`, `scripts`, startup/setup scripts;
- evaluation/security code and tests;
- MCP schemas and declared tool inventories;
- public non-secret configuration and lock/requirements files;
- private `.env` and account-specific data: hash-only, never values;
- SQLite, Qdrant, handbook and generated runtime/evaluation outputs: separate
  data/runtime attestations, not source equivalence.

The release owner must approve this boundary and permitted source/staging
differences before an attestation can be authoritative.

### F — renderer claim mapping

| Legacy claim | Current evidence | Action |
|---|---|---|
| 18-agent architecture/inventory | agent inventory and current acceptance report | Derive from validated inventory; block if absent. |
| 39 MCP tools/transports | staging result JSON and receipts | Derive counts/status; never substitute AST count. |
| SQLite/Qdrant/data integrity | `master_final_integrity.json` | Derive only after integrity report status/provenance validation; otherwise block. |
| Dependency audit state | dependency scan and assessment JSON | Derive unresolved findings; label FAIL, never imply clean. |
| Public deployment/TLS/MFA/ACL scope | no current acceptance input | Label as scope limitation or omit. |
| Historical comparisons and prior runs | archived reports/checkpoints | Label HISTORICAL; never mix into current status. |
| Final-copy authorization | `master_release_decision.json` | Derive, preserve false unless separately authorized. |

## Symlink test limitation

The focused Windows symlink test was skipped because link creation is unavailable
in the sandbox. No permission changes or links in protected/staging paths are
appropriate. A future isolated test may use a disposable temporary directory and
an unprivileged directory junction created by an approved Windows test fixture;
otherwise retain the default-deny production behavior and mark the test BLOCKED.

## Next sequence

1. Obtain and verify the external signing trust root (B).
2. Approve component boundaries and permitted differences (E).
3. Wire A/C helpers into `master_integrity.main()` and add end-to-end fail-closed tests.
4. Expand D coverage for approved attested roots and isolated junction fixtures.
5. Approve and implement F mappings with no-write-on-validation-failure tests.
6. Run focused offline tests, then request separate renderer approval.

Remaining blockers are the unenforced A/C policies, partial D coverage, missing
signing trust root, unapproved component attestation scope, and renderer claim
mapping. Release remains blocked.

**RELEASE BLOCKED — FINAL APPROVALS REQUIRED**
