from __future__ import annotations
from datetime import date
import math
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, require_roles, log_audit

def get_expense_claims(employee_id: int, tool_context: ToolContext) -> dict:
    """View claims for an employee; Finance may use employee_id=0 for its pending review queue."""
    user, error = require_auth(tool_context)
    if error: return error
    if employee_id == 0 and user["role"] != "finance":
        return {"status":"forbidden"}
    if employee_id != 0 and user["role"] not in {"finance","hr"} and user["employee_id"] != employee_id:
        return {"status":"forbidden"}
    conn = get_connection()
    if employee_id == 0:
        rows = conn.execute("SELECT * FROM expense_claims WHERE status='pending' ORDER BY claim_date, id" ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM expense_claims WHERE employee_id=? ORDER BY claim_date DESC", (employee_id,)).fetchall()
    conn.close()
    return {"status":"success","claims":[dict(r) for r in rows]}

def submit_expense(category: str, amount: float, description: str, tool_context: ToolContext) -> dict:
    """Submit an expense claim for the logged-in employee."""
    user, error = require_auth(tool_context)
    if error: return error
    if not math.isfinite(amount) or amount <= 0 or not category.strip() or not description.strip():
        return {"status":"error", "message":"Expense requires a positive finite amount, category and description."}
    if not user["employee_id"]:
        return {"status":"error", "message":"Account is not linked to an employee."}
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO expense_claims(employee_id,category,amount,description,claim_date,status)
           VALUES (?,?,?,?,?,'pending')""",
        (user["employee_id"],category,amount,description,date.today().isoformat()),
    )
    conn.commit(); claim_id = cur.lastrowid; conn.close()
    log_audit(user["user_id"],"submit_expense","expense_claim",claim_id,f"{category} {amount}")
    return {"status":"success","claim_id":claim_id}

def review_expense(claim_id: int, decision: str, tool_context: ToolContext) -> dict:
    """Approve/reject expense claim. Finance only."""
    user, error = require_roles(tool_context, {"finance"})
    if error: return error
    if decision not in {"approved","rejected"}:
        return {"status":"error","message":"decision must be approved or rejected"}
    conn = get_connection()
    cur = conn.execute("UPDATE expense_claims SET status=?,reviewed_by=? WHERE id=?", (decision,user["employee_id"],claim_id))
    if not cur.rowcount:
        conn.close()
        return {"status":"not_found", "message":"Expense claim not found."}
    conn.commit(); conn.close()
    log_audit(user["user_id"],f"{decision}_expense","expense_claim",claim_id,"")
    return {"status":"success","claim_id":claim_id,"decision":decision}
