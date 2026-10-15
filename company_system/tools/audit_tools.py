from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_roles

def get_recent_audit_logs(limit: int, tool_context: ToolContext) -> dict:
    """Read recent audit logs. Admin and HR only."""
    user, error = require_roles(tool_context, {"admin","hr"})
    if error: return error
    limit = max(1, min(limit, 100))
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return {"status":"success","logs":[dict(r) for r in rows]}
