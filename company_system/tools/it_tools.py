from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, require_roles, can_view_employee

def get_assigned_assets(employee_id: int, tool_context: ToolContext) -> dict:
    """Get assigned company assets for self/direct report/HR/admin/IT."""
    user, error = require_auth(tool_context)
    if error: return error
    if user["role"] != "it" and not can_view_employee(user, employee_id):
        return {"status":"forbidden"}
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.asset_tag,a.asset_type,a.model,aa.assigned_date,aa.status
           FROM asset_assignments aa JOIN assets a ON a.id=aa.asset_id
           WHERE aa.employee_id=? AND aa.status='active'""",
        (employee_id,),
    ).fetchall()
    conn.close()
    return {"status":"success","assets":[dict(r) for r in rows]}

def list_available_assets(tool_context: ToolContext) -> dict:
    """List available assets. IT only."""
    user, error = require_roles(tool_context, {"it"})
    if error: return error
    conn = get_connection()
    rows = conn.execute("SELECT * FROM assets WHERE status='available'").fetchall()
    conn.close()
    return {"status":"success","assets":[dict(r) for r in rows]}
