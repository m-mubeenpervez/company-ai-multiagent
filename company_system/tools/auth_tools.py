from __future__ import annotations

from google.adk.tools import ToolContext

from company_system.database.db import get_connection
from company_system.security.passwords import verify_password


def login(
    username: str,
    password: str,
    tool_context: ToolContext,
) -> dict:
    """
    Authenticate a CompanyAI user and save identity/role
    in the current ADK session state.
    """

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            u.*,
            e.full_name,
            e.employee_code
        FROM users u
        LEFT JOIN employees e
            ON e.id = u.employee_id
        WHERE u.username = ?
        """,
        (username.strip(),),
    ).fetchone()

    conn.close()

    if not row or not row["is_active"]:
        return {
            "status": "error",
            "message": "Invalid or inactive account.",
        }

    if not verify_password(
        password,
        row["password_salt"],
        row["password_hash"],
    ):
        return {
            "status": "error",
            "message": "Invalid username or password.",
        }

    tool_context.state["auth_user_id"] = row["id"]
    tool_context.state["auth_username"] = row["username"]
    tool_context.state["auth_role"] = row["role"]
    tool_context.state["auth_employee_id"] = row["employee_id"]
    tool_context.state["auth_full_name"] = row["full_name"]

    return {
        "status": "success",
        "username": row["username"],
        "role": row["role"],
        "employee_id": row["employee_id"],
        "full_name": row["full_name"],
    }


def logout(
    tool_context: ToolContext,
) -> dict:
    """
    Log out the currently authenticated user.

    ADK ToolContext state does not support dict.pop(),
    so authentication values are cleared by assigning None.
    """

    tool_context.state["auth_user_id"] = None
    tool_context.state["auth_username"] = None
    tool_context.state["auth_role"] = None
    tool_context.state["auth_employee_id"] = None
    tool_context.state["auth_full_name"] = None

    return {
        "status": "success",
        "message": "Logged out successfully.",
    }


def get_login_identity(
    tool_context: ToolContext,
) -> dict:
    """
    Return ONLY the current login/session identity.

    Use this tool ONLY for explicit authentication questions such as:
    - Who am I?
    - Am I logged in?
    - What account am I logged in as?
    - What is my login role?

    Do NOT use this tool for company-domain information such as:
    - designation
    - department
    - employee profile
    - employee code
    - employee email
    - employment type
    - joining date
    - work location
    - manager
    - intern profile
    - attendance
    - leave
    - payroll
    - projects
    - training
    """

    username = tool_context.state.get("auth_username")

    if not username:
        return {
            "status": "auth_required",
            "message": "No user is logged in.",
        }

    return {
        "status": "success",
        "username": username,
        "role": tool_context.state.get("auth_role"),
        "employee_id": tool_context.state.get("auth_employee_id"),
        "full_name": tool_context.state.get("auth_full_name"),
    }