from __future__ import annotations

import inspect
import asyncio
import json
from typing import Any

from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import InMemorySessionService
from google.genai import types

from company_system.agent import root_agent
from company_system.database.db import get_connection
from mcp_server.session_store import create_mcp_session, revoke_mcp_session
from company_system.security.secret_boundary import host_token, reject_secret_text, install_log_redaction


APP_NAME = "companyai_eval"
_runner: Runner | None = None

SPECIALIST_ROUTE_NAMES = {
    "auth_agent",
    "hr_agent",
    "employee_agent",
    "intern_agent",
    "attendance_agent",
    "leave_agent",
    "policy_agent",
    "recruitment_agent",
    "performance_agent",
    "training_agent",
    "project_agent",
    "payroll_agent",
    "finance_agent",
    "it_agent",
    "document_agent",
    "analytics_agent",
    "notification_agent",
    "audit_agent",
}


def _get_runner() -> Runner:
    global _runner
    if _runner is None:
        _runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=InMemorySessionService(),
        )
    return _runner


def _part_text(part: Any) -> str:
    value = getattr(part, "text", None)
    return value if isinstance(value, str) else ""


def _extract_function_call(part: Any) -> dict | None:
    call = getattr(part, "function_call", None)
    if call is None:
        return None
    name = getattr(call, "name", None)
    args = getattr(call, "args", None) or {}
    if not name:
        return None
    safe_args = dict(args) if isinstance(args, dict) else {}
    for sensitive_key in ("session_token", "password", "new_password", "api_key"):
        safe_args.pop(sensitive_key, None)
    return {"name": str(name), "input_parameters": safe_args}


def _extract_function_response(part: Any) -> tuple[str | None, Any]:
    response = getattr(part, "function_response", None)
    if response is None:
        return None, None
    name = getattr(response, "name", None)
    payload = getattr(response, "response", None)
    return (str(name) if name else None), payload


def _find_status(payload: Any) -> str | None:
    if isinstance(payload, str):
        try:
            return _find_status(json.loads(payload))
        except (TypeError, ValueError):
            return None
    if isinstance(payload, dict):
        status = payload.get("status")
        if isinstance(status, str):
            return status
        for child in payload.values():
            found = _find_status(child)
            if found:
                return found
    elif isinstance(payload, list):
        for child in payload:
            found = _find_status(child)
            if found:
                return found
    return None



def _collect_policy_contexts(payload: Any) -> list[dict]:
    found: list[dict] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            try:
                walk(json.loads(value))
            except (TypeError, ValueError):
                return

        elif isinstance(value, dict):
            rows = value.get("results")

            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict) and isinstance(row.get("text"), str):
                        found.append({
                            "text": row["text"],
                            "source": row.get("source"),
                            "page": row.get("page"),
                            "score": row.get("score"),
                        })

            # Inspect nested dictionaries, lists AND strings.
            for child in value.values():
                walk(child)

        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload)

    unique: list[dict] = []
    seen: set[tuple] = set()

    for row in found:
        key = (row.get("source"), row.get("page"), row.get("text"))

        if key not in seen:
            seen.add(key)
            unique.append(row)

    return unique





def _load_user_state(username: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT u.id AS user_id, u.username, u.role, u.employee_id,
                   u.is_active, e.full_name
            FROM users u
            LEFT JOIN employees e ON e.id = u.employee_id
            WHERE u.username = ?
            """,
            (username,),
        ).fetchone()
    finally:
        conn.close()

    if row is None or not bool(row["is_active"]):
        raise ValueError(f"Evaluation account {username!r} is missing or inactive.")

    return {
        "auth_user_id": row["user_id"],
        "auth_username": row["username"],
        "auth_role": row["role"],
        "auth_employee_id": row["employee_id"],
        "auth_full_name": row["full_name"],
    }


async def run_companyai_case(prompt: str, username: str = "intern.mubeen") -> dict:
    """Run a real CompanyAI root-agent turn using an isolated evaluation session."""
    from company_system.security.quota import check_quota
    check_quota()
    install_log_redaction()
    reject_secret_text(prompt)
    runner = _get_runner()
    state = _load_user_state(username)
    token = create_mcp_session(state)
    user_id = f"eval-user-{state['auth_user_id']}"
    session = None

    try:
        session = await runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state=state,
        )

        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )

        events = []
        with host_token(token):
          async with asyncio.timeout(300):
              async for event in runner.run_async(
                  user_id=user_id,
                  session_id=session.id,
                  new_message=message,
                  run_config=RunConfig(max_llm_calls=12),
              ):
                  events.append(event)

        final_parts: list[str] = []
        fallback_parts: list[str] = []
        tools: list[dict] = []
        tool_results: list[dict] = []
        policy_contexts: list[dict] = []
        executed_routes: list[str] = []

        for event in events:
            content = getattr(event, "content", None)
            author = getattr(event, "author", None)

            if author in SPECIALIST_ROUTE_NAMES:
                executed_routes.append(author)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                text = _part_text(part)
                if text:
                    fallback_parts.append(text)

                call = _extract_function_call(part)
                if call:
                    tools.append(call)

                tool_name, payload = _extract_function_response(part)
                if tool_name:
                    tool_results.append({"name": tool_name, "status": _find_status(payload)})
                if tool_name == "search_company_policy":
                    policy_contexts.extend(_collect_policy_contexts(payload))

            try:
                if event.is_final_response():
                    final_parts.extend(
                        _part_text(part)
                        for part in parts
                        if _part_text(part)
                    )
            except Exception:
                pass

        final_output = "\n".join(final_parts).strip()
        if not final_output and fallback_parts:
            final_output = fallback_parts[-1].strip()

        completed_session = await runner.session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session.id,
        )
        session_state = getattr(completed_session, "state", {}) or {}

        return {
            "input": prompt,
            "actual_output": final_output,
            "route": (session_state.get("last_route") or (executed_routes[-1] if executed_routes else None)),
            "route_confidence": session_state.get("last_route_confidence"),
            "routing_error": session_state.get("routing_error"),
            "tools_called": tools,
            "tool_results": tool_results,
            "executed_specialists": sorted(set(executed_routes)),
            "retrieval_context": [row["text"] for row in policy_contexts],
            "retrieved_sources": [
                {"source": row.get("source"), "page": row.get("page"), "score": row.get("score")}
                for row in policy_contexts
            ],
        }
    finally:
        try:
            if session is not None:
                await runner.session_service.delete_session(
                    app_name=APP_NAME, user_id=user_id, session_id=session.id,
                )
        finally:
            revoke_mcp_session(token)


async def close_runner() -> None:
    global _runner
    if _runner is None:
        return
    try:
        close = getattr(_runner, "close", None)
        if callable(close):
            result = close()
            if inspect.isawaitable(result):
                await result
    finally:
        _runner = None
