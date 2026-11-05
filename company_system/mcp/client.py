from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from company_system.mcp.secure_toolset import HostAuthenticatedToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MCP_SERVER_FILE = PROJECT_ROOT / "mcp_server" / "server.py"


DOMAIN_TOOLS = {
    "auth": ["login", "logout", "get_login_identity"],
    "hr": [
        "list_employees",
        "create_employee",
        "update_employee_status",
        "create_user_credentials",
        "update_user_credentials",
        "delete_user_credentials",
    ],
    "employee": ["get_employee_profile", "search_employee_by_name"],
    "intern": [
        "get_intern_profile",
        "get_intern_report_status",
        "list_missing_intern_reports",
    ],
    "attendance": ["get_attendance", "attendance_summary"],
    "leave": ["get_leave_balance", "request_leave", "approve_leave"],
    "policy": ["search_company_policy"],
    "recruitment": ["list_candidates", "get_interview_status"],
    "performance": ["get_performance_reviews"],
    "training": ["get_training_assignments"],
    "project": ["get_employee_projects", "get_employee_tasks"],
    "payroll": ["get_payroll"],
    "finance": ["get_expense_claims", "submit_expense", "review_expense"],
    "it": ["get_assigned_assets", "list_available_assets"],
    "document": ["list_documents"],
    "analytics": ["company_people_summary", "company_operational_summary"],
    "notification": ["get_my_notifications", "send_notification"],
    "audit": ["get_recent_audit_logs"],
}


def build_mcp_toolset(domain: str) -> HostAuthenticatedToolset:
    tool_names = DOMAIN_TOOLS[domain]

    child_env = dict(os.environ)
    child_env["PYTHONPATH"] = str(PROJECT_ROOT)

    return HostAuthenticatedToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(MCP_SERVER_FILE)],
                cwd=str(PROJECT_ROOT),
                env=child_env,
            ),
            timeout=15,
        ),
        tool_filter=tool_names,
    )


def inject_mcp_session_token(tool, args: dict, tool_context):
    """Strip model-supplied secrets; the transport wrapper owns bearer injection."""

    # HostAuthenticatedTool injects credentials only at the transport boundary.
    # Strip model-provided secrets without ever writing a token into ADK events.
    for key in ("session_token", "password", "new_password", "api_key"):
        args.pop(key, None)
    return None



def _parse_mcp_payload(tool_response) -> dict | None:
    if isinstance(tool_response, dict):
        if "status" in tool_response:
            return dict(tool_response)

        structured = tool_response.get("structuredContent") or tool_response.get("structured_content")
        if isinstance(structured, dict):
            return dict(structured)

        content = tool_response.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                else:
                    text = getattr(item, "text", None)
                if isinstance(text, str):
                    try:
                        parsed = json.loads(text)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(parsed, dict):
                        return parsed

    return None


def sync_auth_state_from_mcp(tool, args: dict, tool_context, tool_response):
    """Clear non-secret ADK identity after logout; login is a trusted host operation."""

    payload = _parse_mcp_payload(tool_response)
    if payload is None:
        return None

    if tool.name == "login":
        return {"status": "forbidden", "message": "Use the secure login form."}

    if tool.name == "logout" and payload.get("status") in {"success", "auth_required"}:
        tool_context.state["auth_user_id"] = None
        tool_context.state["auth_username"] = None
        tool_context.state["auth_role"] = None
        tool_context.state["auth_employee_id"] = None
        tool_context.state["auth_full_name"] = None
        return {
            "status": "success",
            "message": "Logged out successfully.",
        }

    return None
