from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, can_view_employee

def get_attendance(employee_id: int, start_date: str, end_date: str, tool_context: ToolContext) -> dict:
    """Get attendance rows for an employee in a date range."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute(
        """SELECT work_date,status,check_in,check_out,working_hours
           FROM attendance WHERE employee_id=? AND work_date BETWEEN ? AND ? ORDER BY work_date""",
        (employee_id,start_date,end_date),
    ).fetchall()
    conn.close()
    return {"status":"success","attendance":[dict(r) for r in rows]}

def attendance_summary(employee_id: int, tool_context: ToolContext) -> dict:
    """Return present, late, absent counts for an employee."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute(
        "SELECT status,COUNT(*) count FROM attendance WHERE employee_id=? GROUP BY status",
        (employee_id,),
    ).fetchall()
    conn.close()
    return {"status":"success","summary":{r["status"]:r["count"] for r in rows}}
