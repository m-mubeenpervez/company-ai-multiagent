# Synthetic demo database proposal

The tracked historical `company_system/database/company.db` is not modified by
this proposal. It must not be copied into a new fixture or replaced until an
independent reviewer approves the generated database.

Fresh local setup instead targets the ignored path configured by
`COMPANYAI_DB_PATH` and invokes `initialize_database.py --synthetic`. The
synthetic seed uses invented names, `example.invalid` email addresses, `DEMO-*`
employee codes, generic business records, and public demo-only passwords. The
passwords are stored as independently salted PBKDF2-HMAC-SHA256 hashes through
the application's existing password helper; plaintext passwords are never
stored in SQLite.

Independent verification must confirm:

1. The destination did not exist before generation and is outside tracked data.
2. `PRAGMA integrity_check` returns `ok` and `PRAGMA foreign_key_check` is empty.
3. Every email ends in `@example.invalid` and every employee code starts with
   `DEMO-`.
4. No historical employee/candidate name, email, username, document filename,
   salt, or password hash appears in the generated fixture.
5. Each documented synthetic credential verifies with `verify_password`, while
   plaintext passwords do not occur in the database bytes.
6. Authentication, authorization, database-sanity, and isolated regression
   tests pass against the generated fixture.

Only after those checks should a separate, explicitly approved commit consider
replacing or removing the historical binary. This proposal does neither.
