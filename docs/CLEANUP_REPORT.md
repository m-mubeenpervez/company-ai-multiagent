# CompanyAI cleanup and preservation

No existing source, test, dataset, document, evaluation/security report, company
data, Git configuration/history or useful documentation was deleted.

The rollback backup is recorded in `.release_backup_location` in the working
copy. It contains all non-generated files, local data and previous evidence.
The protected original is never used as a working directory.

The following are excluded from a release copy rather than deleted from the
working copy:

| Path/pattern | Reason and evidence | Regenerable? |
|---|---|---|
| `.venv*`, `venv`, `env` | Interpreter installations contain absolute launcher paths; fresh environments are required | Yes, locked dependencies |
| `__pycache__`, `.pytest_cache`, `.mypy_cache` | Interpreter/test-generated caches, not source | Yes |
| Disposable `.evaluation_runtime` test clones | Runners create unique data copies; not application runtime data | Yes |
| `.release_backups`, `.release_backup_location` | Working-copy rollback material; retained at the rollback location | Backup retained |
| `.deepeval` local framework state | Machine-specific evaluation cache/configuration | Yes |

Historical RAG comparison vectors/index snapshots are provenance rather than
disposable runtime data and must be retained if their comparison script is shipped.
Actual `company_system/database/company.db`, Qdrant storage, handbook, datasets,
reports and Git history (if present) must be included. `.env` is a private local
runtime configuration, never a publishable artifact. No public release or push
is authorized. Final-copy status is recorded in `FINAL_RELEASE_REPORT.md`.


## 2026-11-04 remediation retention

No starting source/data/test/report file was removed. A new timestamped whole
non-generated rollback snapshot was created before edits; the earlier rollback
was retained. The previous release report, initial remediation plan and security
report were also archived for review. Historical RAGAS/goldens/index were unchanged.

scripts/sync_staging.py is the only source transfer path: it validates the fixed
staging destination, rejects divergent staged Python/PowerShell sources, backs up
replaced files, checks copied hashes, and never overwrites private .env, databases,
Qdrant or virtual environments. Staging packages were installed in its own clean
Python 3.12 environments. A private quota deadline copy prevents redundant model
requests there. It contains a key fingerprint, not the key. No files are deleted.
All implementation edits remain in the working source; final-copy creation stays
unauthorized. Detailed added/modified/removed paths are in remediation_file_changes.json.


## Master finalization refresh ? 2026-11-04

No existing files were deleted. A new verified snapshot of 481 starting project
files is at `.release_backups/master_20261103T231018Z/project`; its manifest and
`evaluations/results/master_initial_integrity.json` record hashes and exact paths.
The previous rollback also matched every manifest entry. Static file classification
and compile results are in `evaluations/results/master_file_audit.json`. Caches,
backups, SQLite, Qdrant, source documents and historical evidence remain intact.
