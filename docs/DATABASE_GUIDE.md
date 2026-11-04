# CompanyAI data guide

SQLite defaults to `company_system/database/company.db`. Override it with
`COMPANYAI_DB_PATH` before importing application modules. Connections enable
foreign keys and a five-second busy timeout. Queries use parameter binding;
there is no general SQL execution tool. The schema covers employees, departments,
users, intern reports, attendance, leave, recruitment, performance, training,
projects/tasks, payroll, claims, assets, document metadata, notifications and audit
records. Login-attempt and revocable-session tables are initialized idempotently.

```powershell
# Creates and seeds only when missing. Preserves an existing database.
.\.venv\Scripts\python.exe initialize_database.py
```

`initialize_database.py --reset` is explicitly destructive and intended for a
disposable/demo database only. `schema.sql` contains DROP statements: never apply
it directly to company data. There is no incremental migration framework; plan
and review any future schema migration separately.

Credential removal disables the account and revokes its sessions, retaining the
identity referenced by session/audit history. Authorized HR can create replacement
credentials for a disabled employee account. Password/role changes revoke existing
sessions. Existing role and record scopes remain server-side.

Qdrant defaults to `company_system/qdrant_storage`, configurable through
`COMPANYAI_QDRANT_PATH`. The `company_policies` collection uses cosine similarity
and 768-dimensional `gemini-embedding-2` vectors by default. Each point has an
integer chunk ID and `source`, `page`, `text` payload. Embedding model and dimensions
must remain consistent with the collection. A missing collection returns
`not_ready` without calling the embedding API.

Stop ADK, MCP servers, ingestion and other data writers before backing up. Use
SQLite's backup API for a consistent database snapshot (including committed WAL
data). Copy the entire closed Qdrant directory, the handbook, `.env` securely,
and the matching model settings. Restore into a separate directory and validate
before replacing anything. Never copy an open local Qdrant store; it uses a local
file lock and is not a multi-process database server.

Evaluation runners use SQLite backup snapshots and copied Qdrant directories
under uniquely named `.evaluation_runtime` directories. The historical cleanup
helper now refuses to run outside that directory. Do not run individual legacy
mutation tests directly against the active database; use the isolated wrappers.
