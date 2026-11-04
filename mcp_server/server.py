from __future__ import annotations

from pathlib import Path
import sys
import os

# Local default excludes vulnerable inbound tracestate parsing; see docs/SECURITY.md.
os.environ.setdefault("OTEL_PROPAGATORS", "baggage")
os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import MCPServer

from mcp_server.session_store import (
    SessionToolContext,
    context_from_session_token,
    create_mcp_session,
    ensure_mcp_sessions_table,
    revoke_mcp_session,
)
from company_system.tools import (
    analytics_tools,
    attendance_tools,
    audit_tools,
    auth_tools,
    document_tools,
    employee_tools,
    finance_tools,
    hr_tools,
    intern_tools,
    it_tools,
    leave_tools,
    notification_tools,
    payroll_tools,
    performance_tools,
    policy_tools,
    project_tools,
    recruitment_tools,
    training_tools,
)

mcp = MCPServer("CompanyAI MCP Server")

ensure_mcp_sessions_table()

@mcp.tool()
def ping_companyai() -> dict:
    """Check whether the CompanyAI MCP server is running."""
    return {"status": "success", "message": "CompanyAI MCP Server is running."}

@mcp.tool()
def login(username: str, password: str, session_token: str = "") -> dict:
    """Authenticate a CompanyAI user and create a revocable MCP session. session_token is host-injected when replacing an existing login."""
    context = SessionToolContext({})
    result = auth_tools.login(username=username, password=password, tool_context=context)
    if result.get("status") != "success":
        return result
    if session_token:
        revoke_mcp_session(session_token)
    token = create_mcp_session(context.state)
    return {
        **result,
        "user_id": context.state.get("auth_user_id"),
        "session_token": token,
    }

@mcp.tool()
def logout(session_token: str = "") -> dict:
    """Log out. session_token is injected by the CompanyAI host."""
    context, error = context_from_session_token(session_token)
    if error:
        return error
    result = auth_tools.logout(tool_context=context)
    revoke_mcp_session(session_token)
    return result

@mcp.tool()
def get_login_identity(session_token: str = "") -> dict:
    """Return current login identity. session_token is injected by the CompanyAI host."""
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return auth_tools.get_login_identity(tool_context=context)

@mcp.tool()
def company_people_summary(session_token: str = "") -> dict:
    'Aggregated company headcount summary. HR, managers and admin only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return analytics_tools.company_people_summary(tool_context=context)

@mcp.tool()
def company_operational_summary(session_token: str = "") -> dict:
    'Aggregated operational dashboard. HR, managers and admin only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return analytics_tools.company_operational_summary(tool_context=context)

@mcp.tool()
def get_attendance(employee_id: int, start_date: str, end_date: str, session_token: str = "") -> dict:
    'Get attendance rows for an employee in a date range.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return attendance_tools.get_attendance(employee_id=employee_id, start_date=start_date, end_date=end_date, tool_context=context)

@mcp.tool()
def attendance_summary(employee_id: int, session_token: str = "") -> dict:
    'Return present, late, absent counts for an employee.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return attendance_tools.attendance_summary(employee_id=employee_id, tool_context=context)

@mcp.tool()
def get_recent_audit_logs(limit: int, session_token: str = "") -> dict:
    'Read recent audit logs. Admin and HR only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return audit_tools.get_recent_audit_logs(limit=limit, tool_context=context)

@mcp.tool()
def list_documents(employee_id: int, session_token: str = "") -> dict:
    'List document metadata visible to the authenticated user.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return document_tools.list_documents(employee_id=employee_id, tool_context=context)

@mcp.tool()
def get_employee_profile(employee_id: int, session_token: str = "") -> dict:
    'Get an employee profile if the current user has permission.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return employee_tools.get_employee_profile(employee_id=employee_id, tool_context=context)

@mcp.tool()
def search_employee_by_name(name: str, session_token: str = "") -> dict:
    'Search employee names with role-based visibility.\n\nHR/Admin:\n    Can search all employees.\n\nManager:\n    Can search self and direct reports.\n\nOther users:\n    Can search only themselves.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return employee_tools.search_employee_by_name(name=name, tool_context=context)

@mcp.tool()
def get_expense_claims(employee_id: int, session_token: str = "") -> dict:
    "View own expense claims; Finance/HR can view any employee's claims.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it."
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return finance_tools.get_expense_claims(employee_id=employee_id, tool_context=context)

@mcp.tool()
def submit_expense(category: str, amount: float, description: str, session_token: str = "") -> dict:
    'Submit an expense claim for the logged-in employee.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return finance_tools.submit_expense(category=category, amount=amount, description=description, tool_context=context)

@mcp.tool()
def review_expense(claim_id: int, decision: str, session_token: str = "") -> dict:
    'Approve/reject expense claim. Finance only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return finance_tools.review_expense(claim_id=claim_id, decision=decision, tool_context=context)

@mcp.tool()
def list_employees(session_token: str = "") -> dict:
    'List company employees. HR and managers only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return hr_tools.list_employees(tool_context=context)

@mcp.tool()
def create_employee(employee_code: str, full_name: str, email: str, department_id: int, designation: str, employment_type: str, manager_employee_id: int, joining_date: str, session_token: str = "") -> dict:
    'Create an employee record. HR only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return hr_tools.create_employee(employee_code=employee_code, full_name=full_name, email=email, department_id=department_id, designation=designation, employment_type=employment_type, manager_employee_id=manager_employee_id, joining_date=joining_date, tool_context=context)

@mcp.tool()
def update_employee_status(employee_id: int, status: str, session_token: str = "") -> dict:
    'Update an employee lifecycle status. HR only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return hr_tools.update_employee_status(employee_id=employee_id, status=status, tool_context=context)

@mcp.tool()
def create_user_credentials(employee_id: int, username: str, password: str, role: str, session_token: str = "") -> dict:
    'Create CompanyAI login credentials for an employee. ONLY HR can do this.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return hr_tools.create_user_credentials(employee_id=employee_id, username=username, password=password, role=role, tool_context=context)

@mcp.tool()
def update_user_credentials(username: str, new_password: str, new_role: str, session_token: str = "") -> dict:
    "Update a user's password and/or role. ONLY HR can do this. Use empty string for a field that should not change.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it."
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return hr_tools.update_user_credentials(username=username, new_password=new_password, new_role=new_role, tool_context=context)

@mcp.tool()
def delete_user_credentials(username: str, session_token: str = "") -> dict:
    'Delete CompanyAI login credentials. ONLY HR can do this. HR cannot delete the account currently logged into the session.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return hr_tools.delete_user_credentials(username=username, tool_context=context)

@mcp.tool()
def get_intern_profile(employee_id: int, session_token: str = "") -> dict:
    "Get an intern's profile.\n\nAccess rules:\n- User can view their own profile.\n- HR/Admin can view permitted employee profiles.\n- Managers can view direct reports.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it."
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return intern_tools.get_intern_profile(employee_id=employee_id, tool_context=context)

@mcp.tool()
def get_intern_report_status(employee_id: int, report_month: str, session_token: str = "") -> dict:
    "Get one intern's monthly report status.\n\nreport_month must use YYYY-MM format.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it."
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return intern_tools.get_intern_report_status(employee_id=employee_id, report_month=report_month, tool_context=context)

@mcp.tool()
def list_missing_intern_reports(report_month: str, session_token: str = "") -> dict:
    'List interns whose monthly report status is marked missing.\n\nAllowed roles:\n- HR\n- Manager\n- Admin\n\nManagers only see their permitted/direct-report interns.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return intern_tools.list_missing_intern_reports(report_month=report_month, tool_context=context)

@mcp.tool()
def get_assigned_assets(employee_id: int, session_token: str = "") -> dict:
    'Get assigned company assets for self/direct report/HR/admin/IT.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return it_tools.get_assigned_assets(employee_id=employee_id, tool_context=context)

@mcp.tool()
def list_available_assets(session_token: str = "") -> dict:
    'List available assets. IT only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return it_tools.list_available_assets(tool_context=context)

@mcp.tool()
def get_leave_balance(employee_id: int, session_token: str = "") -> dict:
    'Get leave balance for self, direct report, HR or admin.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return leave_tools.get_leave_balance(employee_id=employee_id, tool_context=context)

@mcp.tool()
def request_leave(leave_type: str, start_date: str, end_date: str, days: float, reason: str, session_token: str = "") -> dict:
    'Create a leave request for the currently logged-in employee/intern.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return leave_tools.request_leave(leave_type=leave_type, start_date=start_date, end_date=end_date, days=days, reason=reason, tool_context=context)

@mcp.tool()
def approve_leave(request_id: int, decision: str, session_token: str = "") -> dict:
    'Approve or reject leave. HR or manager only. Managers can only act on their direct reports.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return leave_tools.approve_leave(request_id=request_id, decision=decision, tool_context=context)

@mcp.tool()
def get_my_notifications(session_token: str = "") -> dict:
    'Get notifications for the logged-in employee.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return notification_tools.get_my_notifications(tool_context=context)

@mcp.tool()
def send_notification(employee_id: int, title: str, message: str, session_token: str = "") -> dict:
    'Send an internal notification. HR, managers and admin only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return notification_tools.send_notification(employee_id=employee_id, title=title, message=message, tool_context=context)

@mcp.tool()
def get_payroll(employee_id: int, pay_month: str, session_token: str = "") -> dict:
    'Get payroll. Employees/interns can see only their own; HR and Finance can see any employee payroll.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return payroll_tools.get_payroll(employee_id=employee_id, pay_month=pay_month, tool_context=context)

@mcp.tool()
def get_performance_reviews(employee_id: int, session_token: str = "") -> dict:
    'Get performance reviews for self, direct report, HR or admin.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return performance_tools.get_performance_reviews(employee_id=employee_id, tool_context=context)

@mcp.tool()
def search_company_policy(query: str, session_token: str = "") -> dict:
    'Search the official company handbook/policy documents using Qdrant RAG. Login required.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return policy_tools.search_company_policy(query=query, tool_context=context)

@mcp.tool()
def get_employee_projects(employee_id: int, session_token: str = "") -> dict:
    'Get project memberships for self/direct report/HR/admin.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return project_tools.get_employee_projects(employee_id=employee_id, tool_context=context)

@mcp.tool()
def get_employee_tasks(employee_id: int, session_token: str = "") -> dict:
    'Get assigned tasks for self/direct report/HR/admin.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return project_tools.get_employee_tasks(employee_id=employee_id, tool_context=context)

@mcp.tool()
def list_candidates(stage: str, session_token: str = "") -> dict:
    'List candidates by stage. Recruiter or HR only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return recruitment_tools.list_candidates(stage=stage, tool_context=context)

@mcp.tool()
def get_interview_status(candidate_id: int, session_token: str = "") -> dict:
    'Get candidate interview history. Recruiter or HR only.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return recruitment_tools.get_interview_status(candidate_id=candidate_id, tool_context=context)

@mcp.tool()
def get_training_assignments(employee_id: int, session_token: str = "") -> dict:
    'Get training assignments for self, direct report, HR or admin.\n\nThe session_token parameter is injected by the trusted CompanyAI host; the model should not supply it.'
    context, error = context_from_session_token(session_token)
    if error:
        return error
    return training_tools.get_training_assignments(employee_id=employee_id, tool_context=context)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CompanyAI MCP server")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--port", type=int, default=8001, help="Loopback HTTP port (default 8001).")
    args = parser.parse_args()
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=args.port)
