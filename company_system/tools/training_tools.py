from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, can_view_employee

def get_training_assignments(employee_id: int, tool_context: ToolContext) -> dict:
    """Get training assignments for self, direct report, HR or admin."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute(
        """SELECT c.title,c.category,c.mandatory,a.status,a.progress_percentage,a.due_date
           FROM training_assignments a JOIN training_courses c ON c.id=a.course_id
           WHERE a.employee_id=? ORDER BY c.id""",
        (employee_id,),
    ).fetchall()
    conn.close()
    return {"status":"success","training":[dict(r) for r in rows]}
