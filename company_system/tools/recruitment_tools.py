from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_roles

def list_candidates(stage: str, tool_context: ToolContext) -> dict:
    """List candidates by stage. Recruiter or HR only."""
    user, error = require_roles(tool_context, {"recruiter","hr"})
    if error: return error
    conn = get_connection()
    rows = conn.execute(
        "SELECT id,full_name,email,role_applied,stage,status FROM candidates WHERE stage LIKE ? ORDER BY id",
        (f"%{stage}%",),
    ).fetchall()
    conn.close()
    return {"status":"success","candidates":[dict(r) for r in rows]}

def get_interview_status(candidate_id: int, tool_context: ToolContext) -> dict:
    """Get candidate interview history. Recruiter or HR only."""
    user, error = require_roles(tool_context, {"recruiter","hr"})
    if error: return error
    conn = get_connection()
    rows = conn.execute("SELECT * FROM interviews WHERE candidate_id=? ORDER BY interview_date", (candidate_id,)).fetchall()
    conn.close()
    return {"status":"success","interviews":[dict(r) for r in rows]}
