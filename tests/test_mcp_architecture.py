from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = PROJECT_ROOT / "company_system" / "agents"

AGENTS = [
    "auth_agent.py",
    "hr_agent.py",
    "employee_agent.py",
    "intern_agent.py",
    "attendance_agent.py",
    "leave_agent.py",
    "policy_agent.py",
    "recruitment_agent.py",
    "performance_agent.py",
    "training_agent.py",
    "project_agent.py",
    "payroll_agent.py",
    "finance_agent.py",
    "it_agent.py",
    "document_agent.py",
    "analytics_agent.py",
    "notification_agent.py",
    "audit_agent.py",
]


def main() -> None:
    failures: list[str] = []

    for filename in AGENTS:
        text = (AGENTS_DIR / filename).read_text(encoding="utf-8")

        if "from company_system.tools" in text:
            failures.append(f"{filename}: still imports native tools directly")

        if "build_mcp_toolset(" not in text:
            failures.append(f"{filename}: missing MCP toolset")

        if "before_tool_callback=inject_mcp_session_token" not in text:
            failures.append(f"{filename}: missing MCP session-token injection")

    demo_agent = AGENTS_DIR / "mcp_employee_agent.py"
    if demo_agent.exists():
        failures.append("Temporary mcp_employee_agent.py still exists")

    if failures:
        for failure in failures:
            print("FAIL |", failure)
        raise SystemExit(1)

    print("PASS | All 18 registered CompanyAI agents use MCP toolsets")
    print("PASS | No specialist directly registers company_system.tools functions")
    print("PASS | Temporary MCP demo agent has been removed")


if __name__ == "__main__":
    main()
