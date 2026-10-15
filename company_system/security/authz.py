from __future__ import annotations

from datetime import datetime, timezone

from google.adk.tools import ToolContext

from company_system.database.db import get_connection


def current_session_user(tool_context: ToolContext) -> dict | None:
    """
    Return the currently authenticated CompanyAI user.

    If required authentication values are missing or cleared,
    the session is treated as unauthenticated.
    """

    username = tool_context.state.get("auth_username")
    user_id = tool_context.state.get("auth_user_id")
    role = tool_context.state.get("auth_role")
    employee_id = tool_context.state.get("auth_employee_id")
    full_name = tool_context.state.get("auth_full_name")

    if not username or not user_id or not role:
        return None

    return {
        "user_id": user_id,
        "username": username,
        "role": role,
        "employee_id": employee_id,
        "full_name": full_name,
    }


def require_auth(tool_context: ToolContext):
    """
    Require a logged-in CompanyAI user.
    """

    user = current_session_user(tool_context)

    if not user:
        return None, {
            "status": "auth_required",
            "message": (
                "Please log in first using your "
                "CompanyAI username and password."
            ),
        }

    return user, None


def require_roles(
    tool_context: ToolContext,
    allowed_roles: set[str],
):
    """
    Require the logged-in user to have one of the allowed roles.
    """

    user, error = require_auth(tool_context)

    if error:
        return None, error

    if user["role"] not in allowed_roles:
        return None, {
            "status": "forbidden",
            "message": (
                f"Role '{user['role']}' is not allowed "
                "to perform this action."
            ),
        }

    return user, None


def is_manager_of(
    manager_employee_id: int,
    target_employee_id: int,
) -> bool:
    """
    Check whether one employee directly manages another employee.
    """

    conn = get_connection()

    row = conn.execute(
        """
        SELECT 1
        FROM employees
        WHERE id = ?
          AND manager_employee_id = ?
        """,
        (
            target_employee_id,
            manager_employee_id,
        ),
    ).fetchone()

    conn.close()

    return row is not None


def can_view_employee(
    user: dict,
    target_employee_id: int,
) -> bool:
    """
    Check whether the current user may view a target employee.
    """

    # HR and Admin can view all employee records.
    if user["role"] in {"hr", "admin"}:
        return True

    # Users can view their own employee record.
    if user["employee_id"] == target_employee_id:
        return True

    # Managers can view their direct reports.
    if (
        user["role"] == "manager"
        and user["employee_id"]
        and is_manager_of(
            user["employee_id"],
            target_employee_id,
        )
    ):
        return True

    return False


def log_audit(
    actor_user_id,
    action: str,
    target_type: str,
    target_id=None,
    details: str = "",
):
    """
    Store a security or administrative action in the audit log.
    """

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO audit_logs(
            actor_user_id,
            action,
            target_type,
            target_id,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            actor_user_id,
            action,
            target_type,
            (
                str(target_id)
                if target_id is not None
                else None
            ),
            details,
            datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
        ),
    )

    conn.commit()
    conn.close()