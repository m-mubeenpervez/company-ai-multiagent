"""Offline regression checks for the final publication-blocker fixes."""
from __future__ import annotations

from contextlib import closing
import hashlib
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import initialize_database
from company_system.database import db
from company_system.database.synthetic_demo import SYNTHETIC_USERS
from company_system.security.passwords import verify_password


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_DB = ROOT / "company_system/database/company.db"


class PublicationBlockerTests(unittest.TestCase):
    def test_active_release_scripts_have_portable_configurable_paths(self):
        for relative in ("scripts/master_integrity.py", "scripts/prepare_release.py"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"[A-Za-z]:\\")
            self.assertIn("COMPANYAI_PROTECTED_ORIGINAL", text)
            self.assertIn("COMPANYAI_FINAL_DESTINATION", text)

    def test_relative_and_absolute_data_overrides(self):
        relative = db.resolve_data_path("runtime/custom.db")
        self.assertEqual(relative, (ROOT / "runtime/custom.db").resolve())
        with tempfile.TemporaryDirectory() as directory:
            absolute = Path(directory) / "absolute.db"
            self.assertEqual(db.resolve_data_path(absolute), absolute.resolve())

        script = """
from pathlib import Path
from company_system.database.db import DB_PATH
from company_system.rag.vector_store import QDRANT_PATH
assert DB_PATH == (Path.cwd() / 'custom/db.sqlite').resolve()
assert QDRANT_PATH == (Path.cwd() / 'custom/vectors').resolve()
"""
        env = os.environ.copy()
        env["COMPANYAI_DB_PATH"] = "custom/db.sqlite"
        env["COMPANYAI_QDRANT_PATH"] = "custom/vectors"
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=ROOT, env=env,
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_setup_orders_initialization_before_ingestion_and_tests(self):
        text = (ROOT / "setup_windows.ps1").read_text(encoding="utf-8-sig")
        initialize_at = text.index("initialize_database.py --synthetic")
        ingest_at = text.index("ingest_documents.py")
        tests_at = text.index("run_tests.ps1")
        self.assertLess(initialize_at, ingest_at)
        self.assertLess(ingest_at, tests_at)
        self.assertNotIn('company_system\\database\\company.db', text)

    def test_synthetic_database_is_new_hashed_and_disjoint_from_history(self):
        historical_hash = hashlib.sha256(HISTORICAL_DB.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "synthetic.db"
            with patch.object(db, "DB_PATH", target), \
                 patch.object(initialize_database, "DB_PATH", target):
                initialize_database.initialize(synthetic=True)

            raw = target.read_bytes()
            with closing(sqlite3.connect(target)) as generated, \
                 closing(sqlite3.connect(
                     f"file:{HISTORICAL_DB.as_posix()}?mode=ro&immutable=1", uri=True
                 )) as historical:
                self.assertEqual(generated.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(generated.execute("PRAGMA foreign_key_check").fetchall(), [])
                generated_people = set(generated.execute(
                    "SELECT full_name FROM employees UNION SELECT email FROM employees UNION SELECT username FROM users"
                ))
                historical_people = set(historical.execute(
                    "SELECT full_name FROM employees UNION SELECT email FROM employees UNION SELECT username FROM users"
                ))
                self.assertTrue(generated_people.isdisjoint(historical_people))
                self.assertTrue(all(row[0].endswith("@example.invalid") for row in generated.execute("SELECT email FROM employees")))
                self.assertTrue(all(row[0].startswith("DEMO-") for row in generated.execute("SELECT employee_code FROM employees")))
                for username, password, _role, _employee_id in SYNTHETIC_USERS:
                    salt, password_hash = generated.execute(
                        "SELECT password_salt,password_hash FROM users WHERE username=?", (username,)
                    ).fetchone()
                    self.assertTrue(verify_password(password, salt, password_hash))
                    self.assertNotIn(password.encode(), raw)

            self.assertEqual(hashlib.sha256(HISTORICAL_DB.read_bytes()).hexdigest(), historical_hash)


if __name__ == "__main__":
    unittest.main(verbosity=2)
