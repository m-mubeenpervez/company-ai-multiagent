from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, can_view_employee

def get_performance_reviews(employee_id: int, tool_context: ToolContext) -> dict:
    """Get performance reviews for self, direct report, HR or admin."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute(
        "SELECT review_period,score,manager_feedback,review_status FROM performance_reviews WHERE employee_id=? ORDER BY id DESC",
        (employee_id,),
    ).fetchall()
    conn.close()
    return {"status":"success","reviews":[dict(r) for r in rows]}
