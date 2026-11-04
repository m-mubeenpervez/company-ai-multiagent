# Dependency security report

2026-11-04 (Asia/Karachi). **Audit FAIL; not dependency-clean.**

Fresh installed-environment scans cover runtime, evaluation and both staging environments. Frozen runtime/evaluation sets were also scanned. Original scans remain intact. After fixing staging pip, runtime and staging runtime each retain one affected package; evaluation and staging evaluation each retain four. Sixteen distinct unresolved advisory IDs remain across those four packages; duplicate PYSEC entries are counted once.

Primary evidence: `results/remediation_dependency_scans.json`, `results/remediation_dependency_scans_post_bootstrap.json`, `results/remediation_dependency_scans_validated_locks.json`, `results/remediation_upstream_metadata.json`, `results/remediation_advisory_details.json` and `results/remediation_dependency_assessment.json`. Every scan records exact command/time/exit status. One intermediate locked-set scan failed because of an editing-induced UTF-8 BOM conversion; it is retained, corrected and rerun rather than labelled clean.

## Advisory register

| Package / scanned version | Advisory and primary source | Severity | Vulnerable range | Advertised fixes | Decision |
|---|---|---|---|---|---|
| diskcache 5.6.3 | [PYSEC-2026-2447](https://github.com/advisories/GHSA-w8v5-vhqr-4h9v) | medium | <= 5.6.3 | None advertised | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112940](https://github.com/advisories/GHSA-v4x8-3wr5-3wq8) | high | >= 3.20.4, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112913](https://github.com/advisories/GHSA-9vhv-jxww-xfm5) | low | >= 3.20.4, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112907](https://github.com/advisories/GHSA-567q-5qvw-pf92) | low | >= 3.22.0, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112938](https://github.com/advisories/GHSA-m462-7rxw-wvpg) | medium | >= 3.30.0, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112936](https://github.com/advisories/GHSA-j8f7-rjxc-mr56) | medium | >= 3.20.4, <= 4.0.8 | 4.0.9 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112910](https://github.com/advisories/GHSA-8mx5-7m5m-r77g) | medium | >= 3.10.0, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112909](https://github.com/advisories/GHSA-69hj-f68j-2879) | medium | <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112911](https://github.com/advisories/GHSA-9c4x-gm8v-wgc4) | medium | >= 3.30.0, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112939](https://github.com/advisories/GHSA-rfpc-qcw5-3pc4) | medium | >= 3.22.0, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112915](https://github.com/advisories/GHSA-cwqr-hh33-gh44) | medium | >= 3.20.4, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112935](https://github.com/advisories/GHSA-fq56-3cx3-fjxp) | medium | >= 3.22.0, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112912](https://github.com/advisories/GHSA-9j6q-wvj5-jgjg) | low | >= 3.32.6, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| filelock 3.32.7 | [CVE-2026-112908](https://github.com/advisories/GHSA-6627-m3xw-93mp) | medium | >= 3.30.0, <= 4.2.0 | 4.2.1 | UNRESOLVED |
| opentelemetry-api 1.44.0 | [CVE-2026-114603](https://github.com/advisories/GHSA-xcq7-p3pf-p88h) | medium | <= 1.45.0 | 1.45.1 | UNRESOLVED |
| ragas 0.4.3 | [PYSEC-2026-3046](https://github.com/advisories/GHSA-95ww-475f-pr4f) | low | >= 0.2.3, <= 0.4.3 | None advertised | UNRESOLVED |
| pip 25.0.1 | [PYSEC-2026-1795](https://github.com/advisories/GHSA-4xh5-x5gv-qwph) | medium | <= 25.2 | 25.3 | FIXED: stage26.3 |
| pip 25.0.1 | [PYSEC-2026-1796](https://github.com/advisories/GHSA-6vgw-5pg2-w6jp) | low | < 26.0 | 26.0 | FIXED: stage26.3 |
| pip 25.0.1 | [PYSEC-2026-2875](https://github.com/advisories/GHSA-58qw-9mgm-455v) | medium | <= 26.0.1 | 26.1 | FIXED: stage26.3 |
| pip 25.0.1 | [PYSEC-2026-2876](https://github.com/advisories/GHSA-jp4c-xjxw-mgf9) | medium | < 26.1 | 26.1 | FIXED: stage26.3 |
| pip 25.0.1 | [PYSEC-2026-196](https://github.com/advisories/GHSA-wf93-45jw-7689) | medium | < 26.1.2 | 26.1.2 | FIXED: stage26.3 |
| pip 25.0.1 | [PYSEC-2026-3721](https://github.com/advisories/GHSA-qwm4-qh6w-59xr) | medium | < 26.2.0 | 26.2 | FIXED: stage26.3 |

## Dependency paths, reachability and compatibility

### opentelemetry-api

Transitive dependency. Runtime path: `google-adk -> opentelemetry-api`; evaluation also has `deepeval -> opentelemetry-api`.

ADK imports tracing. Supported launcher disables the SDK and inbound tracecontext; native authenticated app does not mount ADK debug endpoints. Package remains installed and vulnerable.

UNRESOLVED: ADK 2.13.0 caps API and SDK at 1.44; await compatible ADK release and test a paired upgrade.

### filelock

Transitive dependency. Dependency path: `litellm -> filelock`.

Transitive evaluation dependency. Direct LiteLLM use found in proxy CLI configure_profiles/claude_settings, not this Gemini completion path. HuggingFace/cache dependencies can also use file locks. Local writable lock/cache paths remain a conditional risk; OS ACLs not exhaustively audited.

UNRESOLVED: LiteLLM 1.106.6 requires filelock<4; fixed family starts at 4.2.1 (latest checked 4.2.7). Await compatible LiteLLM or separately review a bounded migration.

### diskcache

Transitive dependency. Dependency path: `ragas -> diskcache`.

Installed through RAGAS. The evaluator does not supply a DiskCacheBackend and LiteLLM disk caching is not enabled. Attacker-writable caches remain unsafe if this optional functionality is enabled.

UNRESOLVED: latest package remains 5.6.3; no advertised patch. Keep disk cache disabled/private and never ingest untrusted cache files.

### ragas

Direct declared dependency. Dependency path: `ragas`.

Project uses text-only Faithfulness/ContextPrecision/ContextRecall; no multimodal faithfulness or public evaluation upload endpoint. Affected multimodal file/URL path is outside the supported configured flow.

UNRESOLVED: latest remains 0.4.3 with no advertised fixed release. Keep text-only trusted local datasets; separately review future patched release.

### pip

Direct declared dependency. Dependency path: `pip`.

Environment installer, not an application request path. Staging venv creation had pip 25.0.1. Both stage environments now use26.3; bootstrap and both locks pin26.3.

FIXED in both staging environments: installer26.3. No framework dependency changed.

## Constraints and verification

Only pip changed:25.0.1 to26.3 in both staging environments, the clean verification environment and the audit tooling environment. Main/evaluation environments already had26.3. Application/evaluation framework versions remain unchanged. FastAPI and Uvicorn, already installed transitively at tested versions, are now declared directly because the trusted local UI imports them. `requirements-bootstrap.txt` pins patched pip and both constraint files agree. Setup scripts bootstrap it before dependency installation.

Official current package metadata confirms ADK 2.13.0 bounds `opentelemetry-api<=1.44,>=1.39` and the same SDK bound. LiteLLM 1.106.6 requires `filelock<4.0,>=3.16.1`. Forcing patched versions would violate metadata; no incompatible override or breaking framework migration was performed. Pip consistency and vulnerability status are separate checks. Final pip-check/install results are in `results/remediation_test_runs.json`.

Private caches and disabled unused code paths are compensating controls, not patched dependencies. No OS ACL completeness, exploit impossibility or clean audit is claimed. A future compatible framework release needs an isolated constrained install, pip check, transport/authentication/regression tests and live evaluation before replacing these versions. Risk acceptance requires a separate explicit user decision; final copying remains unauthorized.

Resolver dry-runs in `results/remediation_compatibility_probes.json` confirmed both patched-version combinations produce ResolutionImpossible without installing anything. All six application/evaluation/verification/tooling environments subsequently passed pip check with pip 26.3; see `results/remediation_environment_checks.json`.


## Master finalization refresh ? 2026-11-04

Fresh scans of all four installed environments and both frozen sets remain FAIL:
runtime targets have one affected package; evaluation targets have four. The same
16 unresolved advisory IDs remain. Exact commands/times/exits are in
`results/remediation_dependency_scans_master_network.json`; reports use the
`_master_network` suffix. Initial sandbox-denied scan attempts are retained as
BLOCKED (`_master`), not clean results. Current official PyPI metadata is saved in
`results/master_upstream_metadata.json`; primary GitHub advisory refresh is in
`results/master_advisory_refresh.json` (22 records include six already-fixed pip
findings). Package versions and ADK/LiteLLM constraints are unchanged. No compatible
new patch was found; no dependency override or risk acceptance was performed.
