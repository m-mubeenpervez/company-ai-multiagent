"""Missing-data guards and explicit initialization, using disposable paths only."""
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from company_system.database import db
from company_system.rag import vector_store, retriever
from company_system.security import quota
import initialize_database


class DataSafetyTests(unittest.TestCase):
    def test_runtime_sqlite_does_not_create_missing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "missing.db"
            with patch.object(db, "DB_PATH", target), self.assertRaises(sqlite3.OperationalError):
                db.get_connection()
            self.assertFalse(target.exists())

    def test_explicit_initializer_can_create_disposable_database(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "explicit.db"
            with patch.object(db, "DB_PATH", target), patch.object(initialize_database, "DB_PATH", target), \
                 patch.object(initialize_database, "seed") as seed:
                initialize_database.initialize()
                connection = db.get_connection()
                try:
                    self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                    self.assertIsNotNone(connection.execute("SELECT name FROM sqlite_master WHERE name='users'").fetchone())
                finally:
                    connection.close()
                seed.assert_called_once()

    def test_missing_policy_index_does_not_create_directory_or_embed(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "missing_index"
            with patch.object(vector_store, "QDRANT_PATH", target), patch.object(retriever, "embed_query") as embed:
                self.assertEqual(retriever.search_policy("test question")["status"], "not_ready")
                embed.assert_not_called()
            self.assertFalse(target.exists())

    def test_retry_after_http_date_numeric_and_invalid_headers(self):
        with patch.object(quota.time, "time", return_value=1000):
            for header, expected in (("Thu, 01 Jan 1970 00:17:40 GMT", 60), ("17", 17), ("invalid-date", None)):
                error = SimpleNamespace(response=SimpleNamespace(headers={"retry-after": header}))
                self.assertEqual(quota.retry_after_seconds(error), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
