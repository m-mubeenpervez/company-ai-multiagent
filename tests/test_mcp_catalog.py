from __future__ import annotations

import asyncio

from mcp import Client

from company_system.mcp.client import DOMAIN_TOOLS
from mcp_server.server import mcp


async def main() -> None:
    expected = {"ping_companyai"}
    for names in DOMAIN_TOOLS.values():
        expected.update(names)

    async with Client(mcp) as client:
        result = await client.list_tools()
        actual = {tool.name for tool in result.tools}

    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)

    print(f"Expected tools: {len(expected)}")
    print(f"Actual tools:   {len(actual)}")

    if missing:
        print("Missing:", missing)
    if unexpected:
        print("Unexpected:", unexpected)

    if missing or unexpected:
        raise SystemExit(1)

    print("PASS | Full CompanyAI MCP tool catalog is exposed")


if __name__ == "__main__":
    asyncio.run(main())
