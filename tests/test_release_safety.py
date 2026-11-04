"""Release data-safety and authorization regressions, always on disposable data."""
from __future__ import annotations

import hashlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluations.runtime_isolation import prepare_isolated_runtime

prepare_isolated_runtime("release_safety")
from company_system.database.db import get_connection, DB_PATH
from company_system.tools import auth_tools, finance_tools, hr_tools, leave_tools
from company_system.rag.ingest import ingest_pdf
from company_system.rag.vector_store import upsert_chunks
from mcp_server.session_store import SessionToolContext, create_mcp_session, context_from_session_token
from initialize_database import initialize


def identity(username, password):
    context = SessionToolContext({})
    assert auth_tools.login(username, password, context)["status"] == "success"
    return context


class ReleaseSafetyTests(unittest.TestCase):
    def test_initialization_preserves_existing_database(self):
        before = hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
        initialize()
        self.assertEqual(hashlib.sha256(DB_PATH.read_bytes()).hexdigest(), before)

    def test_ingestion_preserves_existing_collection_without_api_call(self):
        # A nonexistent PDF proves the preservation check precedes loading/API calls.
        self.assertEqual(ingest_pdf(ROOT / "nonexistent.pdf")["status"], "preserved")

    def test_invalid_expense_and_leave_inputs_do_not_write(self):
        context = identity("intern.mubeen", "Intern#2026")
        for amount in [-1, 0, float("nan"), float("inf")]:
            self.assertEqual(finance_tools.submit_expense("Travel", amount, "test", context)["status"], "error")
        for start, end, days in [("bad", "bad", 1), ("2026-11-05", "2026-11-01", 1),
                                 ("2026-11-01", "2026-11-01", -1), ("2026-11-01", "2026-11-01", 2)]:
            self.assertEqual(leave_tools.request_leave("annual", start, end, days, "test", context)["status"], "error")

    def test_manager_cannot_approve_own_leave(self):
        context = identity("manager.asim", "Manager#2026")
        row = leave_tools.request_leave("annual", "2026-11-05", "2026-11-05", 1, "test", context)
        self.assertEqual(leave_tools.approve_leave(row["request_id"], "approved", context)["status"], "forbidden")

    def test_leave_approval_updates_balance_once_and_rejection_restores_it(self):
        intern = identity("intern.mubeen", "Intern#2026")
        hr = identity("hr.admin", "HrAdmin#2026")
        before = leave_tools.get_leave_balance(5, intern)["balance"]["annual_remaining"]
        row = leave_tools.request_leave("annual", "2026-11-10", "2026-11-10", 1, "Isolated test", intern)
        for _ in range(2):
            self.assertEqual(leave_tools.approve_leave(row["request_id"], "approved", hr)["status"], "success")
        self.assertEqual(leave_tools.get_leave_balance(5, intern)["balance"]["annual_remaining"], before - 1)
        self.assertEqual(leave_tools.approve_leave(row["request_id"], "rejected", hr)["status"], "success")
        self.assertEqual(leave_tools.get_leave_balance(5, intern)["balance"]["annual_remaining"], before)
        self.assertEqual(leave_tools.request_leave("annual", "2026-11-01", "2026-11-30", 30, "test", intern)["status"], "error")

    def test_password_rotation_and_credential_removal_invalidate_sessions(self):
        hr = identity("hr.admin", "HrAdmin#2026")
        target = identity("employee.sara", "Employee#2026")
        old = create_mcp_session(target.state)
        self.assertEqual(hr_tools.update_user_credentials("employee.sara", "Rotated#2026", "", hr)["status"], "success")
        self.assertEqual(context_from_session_token(old)[1]["status"], "auth_required")
        target = identity("employee.sara", "Rotated#2026")
        token = create_mcp_session(target.state)
        self.assertEqual(hr_tools.delete_user_credentials("employee.sara", hr)["status"], "success")
        self.assertEqual(hr_tools.create_user_credentials(4, "employee.sara", "Replacement#2026", "employee", hr)["status"], "success")
        # Recreating credentials must never resurrect the pre-removal bearer token.
        self.assertEqual(context_from_session_token(token)[1]["status"], "auth_required")
        self.assertEqual(auth_tools.login("employee.sara", "Rotated#2026", SessionToolContext({}))["status"], "error")
        self.assertEqual(auth_tools.login("employee.sara", "Replacement#2026", SessionToolContext({}))["status"], "success")
        conn = get_connection()
        try:
            self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            conn.close()

    def test_sql_injection_and_invalid_tokens_do_not_authorize(self):
        self.assertEqual(auth_tools.login("' OR 1=1 --", "anything", SessionToolContext({}))["status"], "error")
        self.assertEqual(context_from_session_token("' OR 1=1 --")[1]["status"], "auth_required")

    def test_vector_batch_validation_and_runtime_path_boundary(self):
        with self.assertRaises(ValueError):
            upsert_chunks([{"chunk_id": 1}], [])
        with self.assertRaises(ValueError):
            prepare_isolated_runtime("../outside")

    def test_context_supplies_identity_without_secrets_and_overwrites_forged_token(self):
        from company_system.agents.common import with_session_context
        from company_system.mcp.client import inject_mcp_session_token
        context = SimpleNamespace(state={"auth_employee_id": 5, "mcp_session_token": "private-token", "password": "private-password"})
        prompt = with_session_context("Domain rules")(context)
        self.assertIn('"auth_employee_id": 5', prompt)
        self.assertNotIn("private-token", prompt)
        self.assertNotIn("private-password", prompt)
        arguments = {"session_token": "forged-token"}
        inject_mcp_session_token(None, arguments, context)
        self.assertNotIn("session_token", arguments)  # bearer stays below ADK events

    def test_missing_collection_reports_not_ready_without_embedding(self):
        from company_system.rag import retriever
        with patch.object(retriever, "COLLECTION", "missing_release_collection"), patch.object(retriever, "embed_query") as embedding:
            self.assertEqual(retriever.search_policy("policy question")["status"], "not_ready")
            embedding.assert_not_called()


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseSafetyTests))
    raise SystemExit(not result.wasSuccessful())
