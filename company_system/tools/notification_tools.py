from __future__ import annotations
from datetime import datetime
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_auth, require_roles, log_audit

def get_my_notifications(tool_context: ToolContext) -> dict:
    """Get notifications for the logged-in employee."""
    user, error = require_auth(tool_context)
    if error: return error
    conn = get_connection()
    rows = conn.execute(
        "SELECT id,title,message,is_read,created_at FROM notifications WHERE employee_id=? ORDER BY id DESC",
        (user["employee_id"],),
    ).fetchall()
    conn.close()
    return {"status":"success","notifications":[dict(r) for r in rows]}

def send_notification(employee_id: int, title: str, message: str, tool_context: ToolContext) -> dict:
    """Send an internal notification. HR, managers and admin only."""
    user, error = require_roles(tool_context, {"hr","manager","admin"})
    if error: return error
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO notifications(employee_id,title,message,is_read,created_at) VALUES (?,?,?,0,?)",
        (employee_id,title,message,datetime.utcnow().isoformat(timespec="seconds")),
    )
    conn.commit(); nid = cur.lastrowid; conn.close()
    log_audit(user["user_id"],"send_notification","notification",nid,title)
    return {"status":"success","notification_id":nid}
