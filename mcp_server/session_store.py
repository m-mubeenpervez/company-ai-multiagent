from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from company_system.database.db import get_connection

SESSION_TTL_HOURS = 12


class SessionToolContext:
    """Minimal ToolContext-compatible object used by existing CompanyAI tools."""

    def __init__(self, state: dict):
        self.state = state


def ensure_mcp_sessions_table() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mcp_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                employee_id INTEGER,
                full_name TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_mcp_session(state: dict) -> str:
    ensure_mcp_sessions_table()

    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=SESSION_TTL_HOURS)

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO mcp_sessions(
                token_hash,
                user_id,
                username,
                role,
                employee_id,
                full_name,
                created_at,
                expires_at,
                revoked_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                token_hash,
                state.get("auth_user_id"),
                state.get("auth_username"),
                state.get("auth_role"),
                state.get("auth_employee_id"),
                state.get("auth_full_name"),
                now.isoformat(timespec="seconds"),
                expires_at.isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return token


def context_from_session_token(token: str) -> tuple[SessionToolContext | None, dict | None]:
    ensure_mcp_sessions_table()

    if not token:
        return None, {
            "status": "auth_required",
            "message": "Please log in first using your CompanyAI username and password.",
        }

    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT *
            FROM mcp_sessions
            WHERE token_hash = ?
            """,
            (_hash_token(token),),
        ).fetchone()

        current_user = None
        if row is not None:
            current_user = conn.execute(
                """
                SELECT u.id, u.username, u.role, u.employee_id, u.is_active,
                       e.full_name
                FROM users u
                LEFT JOIN employees e ON e.id = u.employee_id
                WHERE u.id = ?
                """,
                (row["user_id"],),
            ).fetchone()
    finally:
        conn.close()

    if row is None or row["revoked_at"] is not None:
        return None, {
            "status": "auth_required",
            "message": "Your CompanyAI MCP session is not valid. Please log in again.",
        }

    try:
        expires_at = datetime.fromisoformat(row["expires_at"])
    except (TypeError, ValueError):
        expires_at = datetime.min.replace(tzinfo=timezone.utc)

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= datetime.now(timezone.utc):
        revoke_mcp_session(token)
        return None, {
            "status": "auth_required",
            "message": "Your CompanyAI MCP session has expired. Please log in again.",
        }

    # Do not trust role/employee identity snapshots stored when the token
    # was created. Re-check the authoritative users table on every call.
    # If the account was disabled, deleted, or had its role/employee binding
    # changed, revoke the old token immediately.
    identity_changed = (
        current_user is None
        or not bool(current_user["is_active"])
        or current_user["username"] != row["username"]
        or current_user["role"] != row["role"]
        or current_user["employee_id"] != row["employee_id"]
    )
    if identity_changed:
        revoke_mcp_session(token)
        return None, {
            "status": "auth_required",
            "message": "Your CompanyAI account or permissions changed. Please log in again.",
        }

    state = {
        "auth_user_id": current_user["id"],
        "auth_username": current_user["username"],
        "auth_role": current_user["role"],
        "auth_employee_id": current_user["employee_id"],
        "auth_full_name": current_user["full_name"],
    }

    return SessionToolContext(state), None


def revoke_mcp_session(token: str) -> bool:
    if not token:
        return False

    ensure_mcp_sessions_table()

    conn = get_connection()
    try:
        cur = conn.execute(
            """
            UPDATE mcp_sessions
            SET revoked_at = ?
            WHERE token_hash = ?
              AND revoked_at IS NULL
            """,
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                _hash_token(token),
            ),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
