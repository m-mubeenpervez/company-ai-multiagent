from __future__ import annotations
from datetime import datetime
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, require_roles, can_view_employee, log_audit

def get_leave_balance(employee_id: int, tool_context: ToolContext) -> dict:
    """Get leave balance for self, direct report, HR or admin."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    row = conn.execute("SELECT * FROM leave_balances WHERE employee_id=?", (employee_id,)).fetchone()
    conn.close()
    if not row: return {"status":"not_found"}
    data = dict(row)
    data["annual_remaining"] = data["annual_total"] - data["annual_used"]
    data["sick_remaining"] = data["sick_total"] - data["sick_used"]
    data["casual_remaining"] = data["casual_total"] - data["casual_used"]
    return {"status":"success","balance":data}

def request_leave(leave_type: str, start_date: str, end_date: str, days: float, reason: str, tool_context: ToolContext) -> dict:
    """Create a leave request for the currently logged-in employee/intern."""
    user, error = require_auth(tool_context)
    if error: return error
    if not user["employee_id"]:
        return {"status":"error","message":"Account is not linked to an employee."}
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,days,reason,status,created_at)
           VALUES (?,?,?,?,?,?,'pending',?)""",
        (user["employee_id"],leave_type,start_date,end_date,days,reason,datetime.utcnow().isoformat(timespec="seconds")),
    )
    conn.commit()
    request_id = cur.lastrowid
    conn.close()
    log_audit(user["user_id"],"request_leave","leave_request",request_id,f"{leave_type} {days} days")
    return {"status":"success","request_id":request_id,"request_status":"pending"}

def approve_leave(request_id: int, decision: str, tool_context: ToolContext) -> dict:
    """Approve or reject leave. HR or manager only. Managers can only act on their direct reports."""
    user, error = require_roles(tool_context, {"hr","manager"})
    if error: return error
    if decision not in {"approved","rejected"}:
        return {"status":"error","message":"decision must be approved or rejected"}
    conn = get_connection()
    row = conn.execute("SELECT * FROM leave_requests WHERE id=?", (request_id,)).fetchone()
    if not row:
        conn.close(); return {"status":"not_found"}
    if user["role"] == "manager" and not can_view_employee(user, row["employee_id"]):
        conn.close(); return {"status":"forbidden"}
    conn.execute("UPDATE leave_requests SET status=?,approved_by=? WHERE id=?", (decision,user["employee_id"],request_id))
    conn.commit(); conn.close()
    log_audit(user["user_id"],f"{decision}_leave","leave_request",request_id,"")
    return {"status":"success","request_id":request_id,"decision":decision}
