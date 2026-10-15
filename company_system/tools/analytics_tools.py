from __future__ import annotations
from google.adk.tools import ToolContext
from company_system.database.db import get_connection
from company_system.security.authz import require_roles

def company_people_summary(tool_context: ToolContext) -> dict:
    """Aggregated company headcount summary. HR, managers and admin only."""
    user, error = require_roles(tool_context, {"hr","manager","admin"})
    if error: return error
    conn = get_connection()
    by_type = conn.execute("SELECT employment_type,COUNT(*) count FROM employees WHERE status='active' GROUP BY employment_type").fetchall()
    by_dept = conn.execute(
        "SELECT d.name department,COUNT(*) count FROM employees e JOIN departments d ON d.id=e.department_id WHERE e.status='active' GROUP BY d.name"
    ).fetchall()
    conn.close()
    return {
        "status":"success",
        "by_employment_type":[dict(r) for r in by_type],
        "by_department":[dict(r) for r in by_dept],
    }

def company_operational_summary(tool_context: ToolContext) -> dict:
    """Aggregated operational dashboard. HR, managers and admin only."""
    user, error = require_roles(tool_context, {"hr","manager","admin"})
    if error: return error
    conn = get_connection()
    pending_leave = conn.execute("SELECT COUNT(*) c FROM leave_requests WHERE status='pending'").fetchone()["c"]
    overdue_tasks = conn.execute("SELECT COUNT(*) c FROM tasks WHERE status!='done' AND due_date < date('now')").fetchone()["c"]
    missing_reports = conn.execute("SELECT COUNT(*) c FROM intern_monthly_reports WHERE status='missing'").fetchone()["c"]
    conn.close()
    return {
        "status":"success",
        "pending_leave_requests":pending_leave,
        "overdue_tasks":overdue_tasks,
        "missing_intern_reports":missing_reports,
    }
