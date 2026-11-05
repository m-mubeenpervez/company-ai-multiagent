from __future__ import annotations

import asyncio
import json

from mcp import Client

from mcp_server.server import mcp
from company_system.database.db import get_connection


def payload(result) -> dict:
    structured = getattr(result, "structured_content", None)
    if isinstance(structured, dict):
        return structured

    content = getattr(result, "content", None) or []
    for item in content:
        text = getattr(item, "text", None)
        if isinstance(text, str):
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                return data

    return {}


async def call(client, name: str, args: dict) -> dict:
    return payload(await client.call_tool(name, args))


async def login(client, username: str, password: str) -> str:
    result = await call(
        client,
        "login",
        {"username": username, "password": password},
    )
    assert result.get("status") == "success", result
    token = result.get("session_token")
    assert token, result
    return token


def check(name: str, result: dict, expected: str) -> bool:
    actual = result.get("status")
    if actual == expected:
        print(f"PASS | {name} -> {actual}")
        return True
    print(f"FAIL | {name}\n     Expected: {expected}\n     Actual:   {result}")
    return False


async def main() -> None:
    results: list[bool] = []

    async with Client(mcp) as client:
        results.append(check(
            "Unauthenticated MCP employee lookup is blocked",
            await call(client, "get_employee_profile", {"employee_id": 5}),
            "auth_required",
        ))

        intern_token = await login(client, "demo.intern", "DemoIntern#2026")

        results.append(check(
            "Intern can view own employee profile",
            await call(client, "get_employee_profile", {
                "employee_id": 5,
                "session_token": intern_token,
            }),
            "success",
        ))

        results.append(check(
            "Intern cannot view another employee profile",
            await call(client, "get_employee_profile", {
                "employee_id": 3,
                "session_token": intern_token,
            }),
            "forbidden",
        ))

        results.append(check(
            "Intern cannot view another employee payroll",
            await call(client, "get_payroll", {
                "employee_id": 3,
                "pay_month": "2026-09",
                "session_token": intern_token,
            }),
            "forbidden",
        ))

        logout_result = await call(client, "logout", {
            "session_token": intern_token,
        })
        results.append(check("Logout succeeds", logout_result, "success"))

        results.append(check(
            "Revoked MCP token cannot be reused",
            await call(client, "get_employee_profile", {
                "employee_id": 5,
                "session_token": intern_token,
            }),
            "auth_required",
        ))

        manager_token = await login(client, "demo.manager", "DemoManager#2026")
        results.append(check(
            "Manager can view direct report profile",
            await call(client, "get_employee_profile", {
                "employee_id": 3,
                "session_token": manager_token,
            }),
            "success",
        ))

        finance_token = await login(client, "demo.finance", "DemoFinance#2026")
        results.append(check(
            "Finance can view employee payroll",
            await call(client, "get_payroll", {
                "employee_id": 5,
                "pay_month": "2026-09",
                "session_token": finance_token,
            }),
            "success",
        ))

        hr_token = await login(client, "demo.hr", "DemoHr#2026")
        results.append(check(
            "HR can list employees through MCP",
            await call(client, "list_employees", {
                "session_token": hr_token,
            }),
            "success",
        ))

        employee_token = await login(client, "demo.employee", "DemoEmployee#2026")
        results.append(check(
            "Employee cannot access company analytics",
            await call(client, "company_people_summary", {
                "session_token": employee_token,
            }),
            "forbidden",
        ))

    passed = sum(results)
    total = len(results)
    failed = total - passed

    print("\n==============================")
    print("MCP SECURITY REGRESSION SUMMARY")
    print("==============================")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {total}")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM mcp_sessions")
        conn.commit()
    finally:
        conn.close()

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
