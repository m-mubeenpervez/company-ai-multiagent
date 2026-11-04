from __future__ import annotations
from datetime import datetime
from datetime import date
import math
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
    try:
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    except ValueError:
        return {"status":"error", "message":"Leave dates must use YYYY-MM-DD."}
    if (leave_type not in {"annual", "sick", "casual"} or start > end
            or not math.isfinite(days) or days <= 0
            or days > (end - start).days + 1 or not reason.strip()):
        return {"status":"error", "message":"Invalid leave type, date range, days or reason."}
    conn = get_connection()
    balance = conn.execute("SELECT * FROM leave_balances WHERE employee_id=?", (user["employee_id"],)).fetchone()
    if balance is None or days > balance[leave_type + "_total"] - balance[leave_type + "_used"]:
        conn.close()
        return {"status":"error", "message":"Insufficient recorded leave balance. Ask HR to review any policy exception."}
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
    try:
        # Serialize the decision and balance adjustment, including repeated calls.
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM leave_requests WHERE id=?", (request_id,)).fetchone()
        if not row:
            return {"status":"not_found"}
        if user["role"] == "manager" and not can_view_employee(user, row["employee_id"]):
            return {"status":"forbidden"}
        if row["employee_id"] == user["employee_id"]:
            return {"status":"forbidden", "message":"You cannot approve or reject your own leave."}
        if row["status"] == decision:
            return {"status":"success", "request_id":request_id, "decision":decision}
        if row["status"] not in {"pending", "approved", "rejected"}:
            return {"status":"error", "message":"Unknown recorded request state. Ask HR to review it."}
        leave_type = row["leave_type"]
        if leave_type not in {"annual", "sick", "casual"} or not math.isfinite(row["days"]) or row["days"] <= 0:
            return {"status":"error", "message":"Invalid recorded leave request. Ask HR to review it."}
        balance = conn.execute("SELECT * FROM leave_balances WHERE employee_id=?", (row["employee_id"],)).fetchone()
        if balance is None:
            return {"status":"error", "message":"No recorded leave balance. Ask HR to review it."}
        adjustment = row["days"] if decision == "approved" else (-row["days"] if row["status"] == "approved" else 0)
        if adjustment < 0 and balance[leave_type + "_used"] < -adjustment:
            return {"status":"error", "message":"Recorded usage requires HR reconciliation before reversal."}
        if decision == "approved" and adjustment > balance[leave_type + "_total"] - balance[leave_type + "_used"]:
            return {"status":"error", "message":"Insufficient recorded leave balance. Ask HR to review any policy exception."}
        conn.execute(
            """UPDATE leave_balances SET
               annual_used=annual_used + CASE WHEN ?='annual' THEN ? ELSE 0 END,
               sick_used=sick_used + CASE WHEN ?='sick' THEN ? ELSE 0 END,
               casual_used=casual_used + CASE WHEN ?='casual' THEN ? ELSE 0 END
               WHERE employee_id=?""",
            (leave_type, adjustment, leave_type, adjustment, leave_type, adjustment, row["employee_id"]),
        )
        conn.execute("UPDATE leave_requests SET status=?,approved_by=? WHERE id=?", (decision,user["employee_id"],request_id))
        conn.commit()
    finally:
        conn.close()
    log_audit(user["user_id"],f"{decision}_leave","leave_request",request_id,"")
    return {"status":"success","request_id":request_id,"decision":decision}
