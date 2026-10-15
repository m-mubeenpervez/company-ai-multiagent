from __future__ import annotations
from datetime import date
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, require_roles, log_audit

def get_expense_claims(employee_id: int, tool_context: ToolContext) -> dict:
    """View own expense claims; Finance/HR can view any employee's claims."""
    user, error = require_auth(tool_context)
    if error: return error
    if user["role"] not in {"finance","hr"} and user["employee_id"] != employee_id:
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute("SELECT * FROM expense_claims WHERE employee_id=? ORDER BY claim_date DESC", (employee_id,)).fetchall()
    conn.close()
    return {"status":"success","claims":[dict(r) for r in rows]}

def submit_expense(category: str, amount: float, description: str, tool_context: ToolContext) -> dict:
    """Submit an expense claim for the logged-in employee."""
    user, error = require_auth(tool_context)
    if error: return error
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
    conn.execute("UPDATE expense_claims SET status=?,reviewed_by=? WHERE id=?", (decision,user["employee_id"],claim_id))
    conn.commit(); conn.close()
    log_audit(user["user_id"],f"{decision}_expense","expense_claim",claim_id,"")
    return {"status":"success","claim_id":claim_id,"decision":decision}
