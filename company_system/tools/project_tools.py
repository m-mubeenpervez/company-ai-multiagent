from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, can_view_employee

def get_employee_projects(employee_id: int, tool_context: ToolContext) -> dict:
    """Get project memberships for self/direct report/HR/admin."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.id,p.name,p.status,pm.project_role,p.start_date,p.end_date
           FROM project_members pm JOIN projects p ON p.id=pm.project_id WHERE pm.employee_id=?""",
        (employee_id,),
    ).fetchall()
    conn.close()
    return {"status":"success","projects":[dict(r) for r in rows]}

def get_employee_tasks(employee_id: int, tool_context: ToolContext) -> dict:
    """Get assigned tasks for self/direct report/HR/admin."""
    user, error = require_auth(tool_context)
    if error: return error
    if not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.id,p.name project,t.title,t.priority,t.status,t.due_date
           FROM tasks t JOIN projects p ON p.id=t.project_id WHERE t.assigned_to=? ORDER BY t.id""",
        (employee_id,),
    ).fetchall()
    conn.close()
    return {"status":"success","tasks":[dict(r) for r in rows]}
