from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, can_view_employee

def list_documents(employee_id: int, tool_context: ToolContext) -> dict:
    """List document metadata visible to the authenticated user."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    if user["role"] == "hr":
        rows = conn.execute("SELECT * FROM document_records WHERE employee_id=? OR visibility='company'", (employee_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM document_records WHERE (employee_id=? AND visibility!='hr_only') OR visibility='company'",
            (employee_id,),
        ).fetchall()
    conn.close()
    return {"status":"success","documents":[dict(r) for r in rows]}
