from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_FILE = PROJECT_ROOT / "mcp_server" / "server.py"


def _structured(result) -> dict:
    data = getattr(result, "structured_content", None)
    if isinstance(data, dict):
        return data
    for item in getattr(result, "content", []) or []:
        text = getattr(item, "text", None)
        if isinstance(text, str):
            try:
                parsed = json.loads(text)
            except ValueError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return {}


async def main() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_FILE)],
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    async with Client(server) as client:
        tools = await client.list_tools()
        print("Connected to CompanyAI MCP Server")
        print(f"Available tools: {len(tools.tools)}")
        print(", ".join(sorted(tool.name for tool in tools.tools)))

        # Demo login. Change these values only for local testing.
        login_result = await client.call_tool(
            "login",
            {
                "username": "demo.intern",
                "password": "DemoIntern#2026",
            },
        )
        login_data = _structured(login_result)
        print("Login status:", login_data.get("status"))

        token = login_data.get("session_token")
        if not token:
            print("No MCP session token returned; stopping demo.")
            return

        try:
            profile_result = await client.call_tool(
                "get_employee_profile",
                {
                    "employee_id": 5,
                    "session_token": token,
                },
            )
            print("Employee profile:", _structured(profile_result))
        finally:
            logout_result = await client.call_tool(
                "logout",
                {"session_token": token},
            )
            print("Logout:", _structured(logout_result))


if __name__ == "__main__":
    asyncio.run(main())
