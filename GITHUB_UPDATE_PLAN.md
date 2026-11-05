# GitHub update plan

Prepared: 2026-11-05 (Asia/Karachi)

Repository: `https://github.com/m-mubeenpervez/company-ai-multiagent`

Migration workspace: `D:\companyai-github-migration`

Integration branch: `integration/latest-shareable-migration`
Base: `origin/main` at `50e54e4`

## Safety and history

The existing repository was cloned; it was not reinitialized. The integration branch starts at the current remote `main` tip, so commits `4625527` and `50e54e4` and their ancestry remain intact. No push, merge, force-push, remote branch update, or remote deletion has been performed. The source directory `D:\companyai-secure-multi-agent-platform` was read only and remains outside Git.

## File-level migration

The lists below describe the branch worktree before commits. `GITHUB_UPDATE_PLAN.md` itself is also an ADD.

### ADD (124)

- `CHANGELOG.md`
- `EVALUATION_SECURITY_IMPLEMENTATION.md`
- `FINAL_RELEASE_REPORT.md`
- `GEMINI_MIGRATION.md`
- `GITHUB_UPDATE_PLAN.md`
- `LLM_ROUTING_ARCHITECTURE.md`
- `MCP_ARCHITECTURE.md`
- `TEST_REPORT.md`
- `company_system/local_ui.html`
- `company_system/local_ui.js`
- `company_system/local_web.py`
- `company_system/mcp/__init__.py`
- `company_system/mcp/client.py`
- `company_system/mcp/secure_toolset.py`
- `company_system/routing/catalog.py`
- `company_system/routing/semantic_router_agent.py`
- `company_system/security/quota.py`
- `company_system/security/secret_boundary.py`
- `docs/AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/CLEANUP_REPORT.md`
- `docs/DATABASE_GUIDE.md`
- `docs/EVALUATION.md`
- `docs/MASTER_FINALIZATION_AUDIT.md`
- `docs/MCP.md`
- `docs/MCP_GUIDE.md`
- `docs/PROJECT_AUDIT_REPORT.md`
- `docs/RAG.md`
- `docs/RAG_GUIDE.md`
- `docs/RECOVERY_AUDIT.md`
- `docs/RELEASE_REMEDIATION_PLAN.md`
- `docs/SECURITY.md`
- `docs/SETUP.md`
- `evaluations/AGENT_ACCEPTANCE_REPORT.md`
- `evaluations/APPROVED_INTEGRITY_CONTRACT_IMPLEMENTATION.md`
- `evaluations/CONSOLIDATED_RELEASE_CLOSURE_REPORT.md`
- `evaluations/DEEPEVAL_ROOT_CAUSE_REPORT.md`
- `evaluations/DEPENDENCY_SECURITY_REPORT.md`
- `evaluations/EVALUATION_GUIDE.md`
- `evaluations/FINAL_BLOCKER_CLOSURE_AUDIT.md`
- `evaluations/FINAL_IMPLEMENTATION_AND_VERIFICATION_REPORT.md`
- `evaluations/FINAL_INTEGRITY_GAP_REMEDIATION.md`
- `evaluations/FINAL_OWNER_APPROVED_IMPLEMENTATION_REPORT.md`
- `evaluations/FINAL_PROJECT_COMPLETION_REPORT.md`
- `evaluations/FINAL_RELEASE_OWNER_APPROVAL_PACKAGE.md`
- `evaluations/FINAL_RELEASE_READINESS_REPORT.md`
- `evaluations/FINAL_RELEASE_REMEDIATION_REPORT.md`
- `evaluations/FINAL_RELEASE_VERIFICATION_PREFLIGHT.md`
- `evaluations/INITIAL_INTEGRITY_METADATA_PRODUCER_REPORT.md`
- `evaluations/INTEGRITY_GATE_ENFORCEMENT_REPORT.md`
- `evaluations/LIVE_EXECUTION_SAFETY_REPORT.md`
- `evaluations/METADATA_PRODUCER_DISCOVERY_REPORT.md`
- `evaluations/RAGAS_VERIFICATION.md`
- `evaluations/RAG_QUALITY_ANALYSIS.md`
- `evaluations/RELEASE_BLOCKER_TRIAGE.md`
- `evaluations/RELEASE_INTEGRITY_AUDIT.md`
- `evaluations/RELEASE_INTEGRITY_CONTRACT_DECISIONS.md`
- `evaluations/SECURITY_TEST_REPORT.md`
- `evaluations/__init__.py`
- `evaluations/adk_harness.py`
- `evaluations/audit_dependencies.py`
- `evaluations/checkpointing.py`
- `evaluations/compare_rag_retrieval.py`
- `evaluations/datasets/agent_acceptance_cases.json`
- `evaluations/datasets/agent_cases.json`
- `evaluations/datasets/deepeval_failure_cases.json`
- `evaluations/datasets/rag_cases.json`
- `evaluations/datasets/routing_cases.json`
- `evaluations/datasets/security_cases.json`
- `evaluations/gemini_judge.py`
- `evaluations/record_command.py`
- `evaluations/renderer_contract.py`
- `evaluations/reporting.py`
- `evaluations/run_agent_acceptance.py`
- `evaluations/run_deepeval_eval.py`
- `evaluations/run_ragas_eval.py`
- `evaluations/run_routing_eval.py`
- `evaluations/runtime_isolation.py`
- `evaluations/test_acceptance_accounting.py`
- `evaluations/test_approved_integrity_contract.py`
- `evaluations/test_checkpointing.py`
- `evaluations/test_data_safety.py`
- `evaluations/test_deepeval_eval.py`
- `evaluations/test_gemini_verification.py`
- `evaluations/test_integrity_artifacts.py`
- `evaluations/test_live_execution_safety.py`
- `evaluations/test_ragas_eval.py`
- `evaluations/test_release_decision_immutable.py`
- `evaluations/test_release_integrity_audit.py`
- `evaluations/test_runtime_isolation.py`
- `evaluations/verify_mcp_release.py`
- `evaluations/verify_startup.py`
- `mcp_client/__init__.py`
- `mcp_client/client.py`
- `mcp_server/__init__.py`
- `mcp_server/server.py`
- `mcp_server/session_store.py`
- `requirements-bootstrap.txt`
- `requirements-evaluation-lock.txt`
- `requirements-evaluation.txt`
- `requirements-runtime-lock.txt`
- `run_evaluations.ps1`
- `run_tests.ps1`
- `scripts/integrity_artifacts.py`
- `scripts/master_integrity.py`
- `scripts/prepare_release.py`
- `scripts/run_isolated_regressions.py`
- `scripts/sync_staging.py`
- `security/SECURITY_ASSESSMENT.md`
- `security/__init__.py`
- `security/run_prompt_injection_eval.py`
- `security/run_security_regression.py`
- `setup_evaluation.ps1`
- `tests/test_gemini_configuration.py`
- `tests/test_gemini_live.py`
- `tests/test_llm_routing_live.py`
- `tests/test_mcp_architecture.py`
- `tests/test_mcp_catalog.py`
- `tests/test_mcp_security_regression.py`
- `tests/test_rag_chunker_quality.py`
- `tests/test_rag_live.py`
- `tests/test_release_safety.py`
- `tests/test_secret_boundary.py`
- `verify_gemini.py`

### REPLACE (50)

- `.env.example`
- `.gitignore`
- `PROJECT_FLOW.md`
- `README.md`
- `company_system/__init__.py`
- `company_system/agent.py`
- `company_system/agents/analytics_agent.py`
- `company_system/agents/attendance_agent.py`
- `company_system/agents/audit_agent.py`
- `company_system/agents/auth_agent.py`
- `company_system/agents/common.py`
- `company_system/agents/document_agent.py`
- `company_system/agents/employee_agent.py`
- `company_system/agents/finance_agent.py`
- `company_system/agents/hr_agent.py`
- `company_system/agents/intern_agent.py`
- `company_system/agents/it_agent.py`
- `company_system/agents/leave_agent.py`
- `company_system/agents/notification_agent.py`
- `company_system/agents/payroll_agent.py`
- `company_system/agents/performance_agent.py`
- `company_system/agents/policy_agent.py`
- `company_system/agents/project_agent.py`
- `company_system/agents/recruitment_agent.py`
- `company_system/agents/training_agent.py`
- `company_system/config.py`
- `company_system/database/db.py`
- `company_system/database/schema.sql`
- `company_system/rag/chunker.py`
- `company_system/rag/embeddings.py`
- `company_system/rag/ingest.py`
- `company_system/rag/retriever.py`
- `company_system/rag/vector_store.py`
- `company_system/tools/auth_tools.py`
- `company_system/tools/employee_tools.py`
- `company_system/tools/finance_tools.py`
- `company_system/tools/hr_tools.py`
- `company_system/tools/intern_tools.py`
- `company_system/tools/leave_tools.py`
- `company_system/tools/payroll_tools.py`
- `company_system/tools/policy_tools.py`
- `company_system/tools/recruitment_tools.py`
- `ingest_documents.py`
- `initialize_database.py`
- `requirements.txt`
- `scripts/cleanup_test_data.py`
- `setup_windows.ps1`
- `start_project.ps1`
- `tests/test_rag.py`
- `tests/test_routing_regression.py`

### REMOVE (4)

- `company_system/routing/deterministic_router_agent.py`
- `company_system/routing/dispatcher.py`
- `company_system/routing/router.py`
- `verify_lmstudio.py`

Removal rationale:

- The three deterministic routing modules are superseded by `company_system/routing/semantic_router_agent.py` and `company_system/routing/catalog.py`; current imports and tests reference the new routing implementation.
- `verify_lmstudio.py` is superseded by `verify_gemini.py`; the current configuration and requirements use Gemini, not LM Studio.

### KEEP (26)

- `.gitattributes`
- `DEMO_CREDENTIALS.md`
- `ROLE_PERMISSION_MATRIX.md`
- `company_system/agents/__init__.py`
- `company_system/database/__init__.py`
- `company_system/database/company.db`
- `company_system/database/seed.py`
- `company_system/documents/company_handbook.pdf`
- `company_system/rag/__init__.py`
- `company_system/rag/loader.py`
- `company_system/routing/__init__.py`
- `company_system/security/__init__.py`
- `company_system/security/authz.py`
- `company_system/security/passwords.py`
- `company_system/tools/__init__.py`
- `company_system/tools/analytics_tools.py`
- `company_system/tools/attendance_tools.py`
- `company_system/tools/audit_tools.py`
- `company_system/tools/document_tools.py`
- `company_system/tools/it_tools.py`
- `company_system/tools/notification_tools.py`
- `company_system/tools/performance_tools.py`
- `company_system/tools/project_tools.py`
- `company_system/tools/training_tools.py`
- `tests/test_database_sanity.py`
- `tests/test_security_regression.py`

`company_system/database/company.db` is deliberately KEEP, not REPLACE.

### EXCLUDE

These are exact exclusion scopes from the local source. No file under these directories is copied:

- `.deepeval/**`
- `.evaluation_runtime/**`
- `.release_backups/**`
- `.release_candidate/**`
- `.venv/**`
- `.venv-eval/**`
- `.venv-release/**`
- `company_system/qdrant_storage/**`
- `evaluations/results/**`
- `evaluations/provenance/**`
- `security/reports/**`
- `docs/archive/**`

These exact source-root files are excluded:

- `.env`
- `.release_backup_location`

The selection also excludes any unlisted cache/temporary/backup artifact matching `__pycache__/**`, `.pytest_cache/**`, `htmlcov/**`, `*.pyc`, `*.pyo`, `*.log`, `*.tmp`, `*.bak`, and local `*.sqlite` or `*.sqlite3` runtime storage. The tracked historical `company_system/database/company.db` is the single intentional database exception and is preserved unchanged. `.env.example` is included because it contains placeholders and documents required configuration.

## Evaluation-directory review

Evaluation material was reviewed by purpose:

- ADD source runners, unit tests, safety tests, datasets, checkpoint/reporting helpers, and human-readable evaluation/security reports.
- EXCLUDE `evaluations/results/**` because it contains generated logs, receipts, checkpoints, signatures, attestations, and repeated run outputs rather than reusable project source.
- EXCLUDE `evaluations/provenance/**` because it includes generated vectors and a copied Qdrant corpus/database.
- EXCLUDE `security/reports/**` because it is generated run output.
- Preserve factual status language: the portfolio is not presented as production-ready; reports retain RELEASE BLOCKED, quota/dependency limitations, skips, and not-run outcomes.

## Database conflict resolution

Remote tracked database:

- Path: `company_system/database/company.db`
- Size: 176,128 bytes
- SHA-256: `D470F3C6CEFD630C307DE5F0DFD1A2CF3C367BBAE88500AAF554594712545C41`

Local source database:

- Path: `D:\companyai-secure-multi-agent-platform\company_system\database\company.db`
- SHA-256: `4BD1B6E6F88E664E3BB666E1FD2340555F3CE732227729290F0E6DC2F392BC99`

The files differ, and the latest schema adds revocable `mcp_sessions`. The source reports and scripts identify the source database as protected company/demo state, while the existing Git database is historical tracked data. Safest treatment: preserve the remote database byte-for-byte in this migration, update schema/initializer code, and require owner approval plus a separately reviewed sanitized/demo-data migration before ever replacing or removing the tracked database. Do not publish the source database. The runtime now opens an existing DB in read/write mode and supports `COMPANYAI_DB_PATH`; initialization remains explicit.

Unresolved owner decision: after reviewing whether the original tracked DB contains acceptable demo-only data, choose either (a) retain it for repository continuity, (b) replace it in a future commit with a verified sanitized fixture, or (c) stop tracking binary data and provide an explicit safe initializer/migration. This branch makes no destructive database choice.

## README and project description

`README.md` is replaced with the latest source version. It describes the current Gemini semantic supervisor, 18 specialist/auth agents, 39 MCP tools, filtered toolsets, local authenticated UI, SQLite/Qdrant RAG, setup, configuration, execution, MCP transports, evaluation commands, security boundaries, project structure, and known limitations. It explicitly describes a local development/portfolio application and does not claim production readiness or universal evaluation success.

## Proposed meaningful commit sequence

1. `feat: migrate Gemini multi-agent runtime and secure MCP architecture`
   - Core agents, semantic routing, MCP server/client, local UI, auth/session/security controls, RAG, setup, dependency files, and obsolete runtime removals.
2. `test: add isolated security, routing, RAG, MCP, and evaluation suites`
   - Tests, evaluation runners/datasets/helpers, security evaluation code, and safe execution scripts.
3. `docs: document current architecture, evaluation status, and migration`
   - README, architecture/setup/security/database/evaluation guides, reports, changelog, and this exact migration plan.

No commit should include generated results, secrets, local databases from the source, Qdrant storage, environments, caches, or backups.

## Validation checklist

Before any future push:

- Confirm branch ancestry with `git merge-base --is-ancestor origin/main HEAD`.
- Review `git status`, staged names, `git diff --cached --stat`, and full staged diff.
- Confirm the tracked database hash remains the remote hash above.
- Confirm ignored/excluded artifacts are absent from `git ls-files`.
- Scan tracked text for credential/private-key patterns and manually inspect `.env.example`.
- Run syntax compilation and offline unit/security suites in isolated temporary runtime paths.
- The selected offline batch ran 26 tests successfully with 1 link-capability skip. A test touched the clone database despite the intended isolation; the post-test hash check caught it, the file was restored from `origin/main`, and the generated runtime directory was removed. Do not rerun that batch against the default tracked database.
- Treat unavailable dependencies, live API quota checks, skips, and blocked evaluations as such; never relabel them PASS.

## Risks and approvals

- Database disposition requires the owner decision described above.
- Existing evaluation reports contain historical absolute paths and timestamps. They are retained as evidence, not current reproducibility claims.
- Dependency reports document unresolved advisories/framework constraints; publication must not imply production hardening.
- Live Gemini and end-to-end evaluations require credentials/quota and were not rerun for this migration.
- The source README specifies Windows Python 3.14 for runtime and Python 3.12 for evaluation; confirm those supported versions before publication if the target audience will reproduce the environment.
- No remote publication is authorized yet. After review, the owner must explicitly approve push/PR/merge steps.

## Current migration state

The isolated integration branch contains the selected latest shareable tree, with the original tracked database preserved. Existing Git history and the local source remain untouched. No remote state has changed.

