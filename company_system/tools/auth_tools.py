from __future__ import annotations

from datetime import datetime, timedelta, timezone

from google.adk.tools import ToolContext

from company_system.database.db import get_connection
from company_system.security.passwords import verify_password, hash_password

# Unknown/disabled accounts still perform the same password derivation. This
# reduces the obvious account-existence timing difference without inventing users.
_DUMMY_SALT, _DUMMY_HASH = hash_password("CompanyAI-timing-placeholder-not-a-login")


MAX_FAILED_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_MINUTES = 15
LOGIN_LOCKOUT_MINUTES = 15


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_login_attempts_table() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_login_attempts (
                username_key TEXT PRIMARY KEY,
                failed_attempts INTEGER NOT NULL,
                window_started_at TEXT NOT NULL,
                locked_until TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _login_is_rate_limited(username: str) -> bool:
    _ensure_login_attempts_table()
    key = (username or "").strip().casefold() or "<empty>"

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT locked_until, window_started_at FROM auth_login_attempts WHERE username_key = ?",
            (key,),
        ).fetchone()
    finally:
        conn.close()

    if row is None or not row["locked_until"]:
        return False

    try:
        locked_until = datetime.fromisoformat(row["locked_until"])
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return False

    return locked_until > _utc_now()


def _record_failed_login(username: str) -> None:
    _ensure_login_attempts_table()
    key = (username or "").strip().casefold()
    if not key:
        key = "<empty>"
    now = _utc_now()
    now_text = now.isoformat(timespec="seconds")

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT failed_attempts, window_started_at FROM auth_login_attempts WHERE username_key = ?",
            (key,),
        ).fetchone()

        if row is None:
            failures = 1
            window_started = now
        else:
            try:
                window_started = datetime.fromisoformat(row["window_started_at"])
                if window_started.tzinfo is None:
                    window_started = window_started.replace(tzinfo=timezone.utc)
            except (TypeError, ValueError):
                window_started = now

            if now - window_started > timedelta(minutes=LOGIN_WINDOW_MINUTES):
                failures = 1
                window_started = now
            else:
                failures = int(row["failed_attempts"]) + 1

        locked_until = None
        if failures >= MAX_FAILED_LOGIN_ATTEMPTS:
            locked_until = (now + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)).isoformat(timespec="seconds")

        conn.execute(
            """
            INSERT INTO auth_login_attempts(
                username_key, failed_attempts, window_started_at, locked_until, updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username_key) DO UPDATE SET
                failed_attempts = excluded.failed_attempts,
                window_started_at = excluded.window_started_at,
                locked_until = excluded.locked_until,
                updated_at = excluded.updated_at
            """,
            (
                key,
                failures,
                window_started.isoformat(timespec="seconds"),
                locked_until,
                now_text,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _clear_failed_logins(username: str) -> None:
    _ensure_login_attempts_table()
    key = (username or "").strip().casefold() or "<empty>"
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM auth_login_attempts WHERE username_key = ?",
            (key,),
        )
        conn.commit()
    finally:
        conn.close()


def login(
    username: str,
    password: str,
    tool_context: ToolContext,
) -> dict:
    """Authenticate a user with generic errors and per-username throttling."""

    username = username.strip() if isinstance(username, str) else ""
    if _login_is_rate_limited(username):
        return {
            "status": "rate_limited",
            "message": "Too many unsuccessful login attempts. Please wait before trying again.",
        }

    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT
                u.*,
                e.full_name,
                e.employee_code
            FROM users u
            LEFT JOIN employees e
                ON e.id = u.employee_id
            WHERE lower(u.username) = lower(?)
            """,
            (username,),
        ).fetchone()
    finally:
        conn.close()

    valid = False
    if isinstance(password, str) and len(password) <= 1024:
        try:
            active = row is not None and bool(row["is_active"])
            derived = verify_password(
                password,
                row["password_salt"] if active else _DUMMY_SALT,
                row["password_hash"] if active else _DUMMY_HASH,
            )
            valid = active and derived
        except (AttributeError, TypeError, ValueError):
            valid = False

    if not valid:
        _record_failed_login(username)
        return {
            "status": "error",
            "message": "Invalid username or password.",
        }

    _clear_failed_logins(username)

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
    """Clear the authenticated identity from the current ADK session."""

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
    """Return only the current login/session identity."""

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
