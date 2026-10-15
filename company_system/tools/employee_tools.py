from __future__ import annotations

from google.adk.tools import ToolContext

from company_system.database.db import get_connection
from company_system.security.authz import (
    require_auth,
    can_view_employee,
)


def get_employee_profile(
    employee_id: int,
    tool_context: ToolContext,
) -> dict:
    """
    Get an employee profile if the current user has permission.
    """

    user, error = require_auth(tool_context)

    if error:
        return error

    if not can_view_employee(user, employee_id):
        return {
            "status": "forbidden",
            "message": "You cannot view this employee profile.",
        }

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT
                e.id,
                e.employee_code,
                e.full_name,
                e.email,
                d.name AS department,
                e.designation,
                e.employment_type,
                e.joining_date,
                e.status,
                e.work_location,
                e.manager_employee_id
            FROM employees e
            JOIN departments d
                ON d.id = e.department_id
            WHERE e.id = ?
            """,
            (employee_id,),
        ).fetchone()

    finally:
        conn.close()

    if not row:
        return {
            "status": "not_found",
            "message": "Employee profile not found.",
        }

    return {
        "status": "success",
        "employee": dict(row),
    }


def search_employee_by_name(
    name: str,
    tool_context: ToolContext,
) -> dict:
    """
    Search employee names with role-based visibility.

    HR/Admin:
        Can search all employees.

    Manager:
        Can search self and direct reports.

    Other users:
        Can search only themselves.
    """

    user, error = require_auth(tool_context)

    if error:
        return error

    name = name.strip()

    if not name:
        return {
            "status": "error",
            "message": "Employee name cannot be empty.",
        }

    conn = get_connection()

    try:

        if user["role"] in {"hr", "admin"}:
            rows = conn.execute(
                """
                SELECT
                    id,
                    employee_code,
                    full_name,
                    designation,
                    employment_type
                FROM employees
                WHERE full_name LIKE ?
                """,
                (f"%{name}%",),
            ).fetchall()

        elif user["role"] == "manager":
            rows = conn.execute(
                """
                SELECT
                    id,
                    employee_code,
                    full_name,
                    designation,
                    employment_type
                FROM employees
                WHERE (
                    manager_employee_id = ?
                    OR id = ?
                )
                AND full_name LIKE ?
                """,
                (
                    user["employee_id"],
                    user["employee_id"],
                    f"%{name}%",
                ),
            ).fetchall()

        else:
            rows = conn.execute(
                """
                SELECT
                    id,
                    employee_code,
                    full_name,
                    designation,
                    employment_type
                FROM employees
                WHERE id = ?
                  AND full_name LIKE ?
                """,
                (
                    user["employee_id"],
                    f"%{name}%",
                ),
            ).fetchall()

    finally:
        conn.close()

    return {
        "status": "success",
        "matches": [
            dict(row)
            for row in rows
        ],
    }