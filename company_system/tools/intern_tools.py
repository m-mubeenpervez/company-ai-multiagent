from __future__ import annotations

import re

from google.adk.tools import ToolContext

from company_system.database.db import get_connection
from company_system.security.authz import (
    can_view_employee,
    require_auth,
    require_roles,
)


REPORT_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _validate_report_month(report_month: str) -> dict | None:
    """
    Validate monthly report format.

    Expected format:
    YYYY-MM

    Example:
    2026-09
    """

    if not REPORT_MONTH_PATTERN.fullmatch(report_month.strip()):
        return {
            "status": "error",
            "message": (
                "Invalid report month. "
                "Use YYYY-MM format, for example 2026-09."
            ),
        }

    return None


def get_intern_profile(
    employee_id: int,
    tool_context: ToolContext,
) -> dict:
    """
    Get an intern's profile.

    Access rules:
    - User can view their own profile.
    - HR/Admin can view permitted employee profiles.
    - Managers can view direct reports.
    """

    user, error = require_auth(tool_context)

    if error:
        return error

    if not can_view_employee(user, employee_id):
        return {
            "status": "forbidden",
            "message": (
                "You do not have permission to view "
                "this intern profile."
            ),
        }

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT
                e.id,
                e.full_name,
                i.training_track,
                i.internship_start,
                i.internship_end,
                i.supervisor_employee_id,
                i.conversion_status
            FROM intern_profiles i
            JOIN employees e
                ON e.id = i.employee_id
            WHERE i.employee_id = ?
            """,
            (employee_id,),
        ).fetchone()

    finally:
        conn.close()

    if not row:
        return {
            "status": "not_found",
            "message": "Intern profile not found.",
        }

    return {
        "status": "success",
        "intern": dict(row),
    }


def get_intern_report_status(
    employee_id: int,
    report_month: str,
    tool_context: ToolContext,
) -> dict:
    """
    Get one intern's monthly report status.

    report_month must use YYYY-MM format.
    """

    user, error = require_auth(tool_context)

    if error:
        return error

    report_month = report_month.strip()

    validation_error = _validate_report_month(report_month)

    if validation_error:
        return validation_error

    if not can_view_employee(user, employee_id):
        return {
            "status": "forbidden",
            "message": (
                "You do not have permission to view "
                "this intern report."
            ),
        }

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT *
            FROM intern_monthly_reports
            WHERE intern_employee_id = ?
              AND report_month = ?
            """,
            (
                employee_id,
                report_month,
            ),
        ).fetchone()

    finally:
        conn.close()

    if not row:
        return {
            "status": "not_found",
            "message": (
                f"No internship report record was found "
                f"for {report_month}."
            ),
        }

    return {
        "status": "success",
        "report": dict(row),
    }


def list_missing_intern_reports(
    report_month: str,
    tool_context: ToolContext,
) -> dict:
    """
    List interns whose monthly report status is marked missing.

    Allowed roles:
    - HR
    - Manager
    - Admin

    Managers only see their permitted/direct-report interns.
    """

    user, error = require_roles(
        tool_context,
        {"hr", "manager", "admin"},
    )

    if error:
        return error

    report_month = report_month.strip()

    validation_error = _validate_report_month(report_month)

    if validation_error:
        return validation_error

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                e.id,
                e.full_name,
                r.report_month,
                r.status,
                r.review_status
            FROM intern_monthly_reports r
            JOIN employees e
                ON e.id = r.intern_employee_id
            WHERE r.report_month = ?
              AND r.status = 'missing'
            """,
            (report_month,),
        ).fetchall()

    finally:
        conn.close()

    if user["role"] == "manager":
        rows = [
            row
            for row in rows
            if can_view_employee(
                user,
                row["id"],
            )
        ]

    return {
        "status": "success",
        "report_month": report_month,
        "missing": [
            dict(row)
            for row in rows
        ],
    }