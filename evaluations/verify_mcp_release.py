"""Exercise the entire real MCP catalog on copied data over either transport."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluations.runtime_isolation import prepare_isolated_runtime
from mcp import Client, StdioServerParameters
from mcp_client.client import _structured


def ensure_quota_available():
    """Fail before disposable setup or any Gemini embedding/tool operation."""
    from company_system.security.quota import check_quota
    check_quota()


async def verify(transport, output_path=None):
    ensure_quota_available()
    runtime = prepare_isolated_runtime("mcp_release_" + transport.replace("-", "_"))
    server_file = ROOT / "mcp_server/server.py"
    server = StdioServerParameters(command=sys.executable, args=[str(server_file)], cwd=str(ROOT), env=dict(os.environ))
    process = None
    records = []
    log = None
    try:
        if transport == "streamable-http":
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            log = (runtime["runtime_root"] / "http_server.log").open("w")
            process = subprocess.Popen([sys.executable, str(server_file), "--transport", transport, "--port", str(port)],
                                       cwd=ROOT, env=dict(os.environ), stdout=log, stderr=log,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError("MCP HTTP server stopped; inspect isolated server log")
                try:
                    reader, writer = await asyncio.open_connection("127.0.0.1", port)
                    writer.close()
                    await writer.wait_closed()
                    break
                except OSError:
                    await asyncio.sleep(0.1)
            server = f"http://127.0.0.1:{port}/mcp"
        async with Client(server, read_timeout_seconds=120) as client:
            tools = (await client.list_tools()).tools
            catalog = {t.name for t in tools}
            assert len(tools) == len(catalog) == 39
            from jsonschema import Draft202012Validator
            for tool in tools:
                Draft202012Validator.check_schema(tool.input_schema)
            invalid = await client.call_tool("get_employee_profile", {"employee_id": "1 OR 1=1"})
            unknown = await client.call_tool("not_a_companyai_tool", {})
            assert invalid.is_error and unknown.is_error
            # The app currently publishes tools only; no invented resources/prompts.
            discovery = {}
            for kind in ("resources", "prompts"):
                try:
                    response = await getattr(client, "list_" + kind)()
                    discovery[kind] = len(getattr(response, kind))
                except Exception as exc:
                    discovery[kind] = type(exc).__name__ + ": not advertised by this tool-only server"

            async def call(name, args=None, token=None, expected="success"):
                arguments = dict(args or {})
                if token:
                    arguments["session_token"] = token
                result = await client.call_tool(name, arguments)
                payload = _structured(result)
                status = payload.get("status")
                passed = not result.is_error and status == expected
                records.append({"tool": name, "status": status, "expected": expected, "passed": passed})
                print(("PASS" if passed else "FAIL") + " | " + name + " | " + str(status), flush=True)
                if not passed:
                    raise AssertionError(f"{name}: expected {expected}, got {status}; MCP error={result.is_error}")
                return payload

            await call("ping_companyai")
            await call("get_employee_profile", {"employee_id": 5}, expected="auth_required")
            tokens = {}
            for role, username, password in [("hr", "demo.hr", "DemoHr#2026"), ("intern", "demo.intern", "DemoIntern#2026"),
                                              ("finance", "demo.finance", "DemoFinance#2026"), ("it", "demo.it", "DemoSupport#2026"),
                                              ("recruiter", "demo.recruiter", "DemoRecruit#2026")]:
                tokens[role] = (await call("login", {"username": username, "password": password}))["session_token"]
            hr, intern = tokens["hr"], tokens["intern"]
            reads = [
                ("get_login_identity", {}, intern), ("company_people_summary", {}, hr), ("company_operational_summary", {}, hr),
                ("get_attendance", {"employee_id": 5, "start_date": "2026-10-01", "end_date": "2026-10-31"}, intern),
                ("attendance_summary", {"employee_id": 5}, hr), ("get_recent_audit_logs", {"limit": 10}, hr),
                ("list_documents", {"employee_id": 5}, intern), ("get_employee_profile", {"employee_id": 5}, intern),
                ("search_employee_by_name", {"name": "Mubeen"}, hr), ("get_expense_claims", {"employee_id": 5}, intern),
                ("list_employees", {}, hr), ("get_intern_profile", {"employee_id": 5}, intern),
                ("get_intern_report_status", {"employee_id": 5, "report_month": "2026-09"}, intern),
                ("list_missing_intern_reports", {"report_month": "2026-09"}, hr), ("get_assigned_assets", {"employee_id": 5}, intern),
                ("list_available_assets", {}, tokens["it"]), ("get_leave_balance", {"employee_id": 5}, intern),
                ("get_my_notifications", {}, intern), ("get_payroll", {"employee_id": 5, "pay_month": "2026-09"}, intern),
                ("get_performance_reviews", {"employee_id": 5}, intern), ("get_training_assignments", {"employee_id": 5}, intern),
                ("get_employee_projects", {"employee_id": 5}, intern), ("get_employee_tasks", {"employee_id": 5}, intern),
                ("list_candidates", {"stage": ""}, tokens["recruiter"]), ("get_interview_status", {"candidate_id": 1}, tokens["recruiter"]),
                ("search_company_policy", {"query": "monthly internship report deadline"}, intern),
            ]
            for name, arguments, token in reads:
                await call(name, arguments, token)
            claim = await call("submit_expense", {"category": "Travel", "amount": 100, "description": "Isolated release test"}, intern)
            await call("review_expense", {"claim_id": claim["claim_id"], "decision": "approved"}, tokens["finance"])
            leave = await call("request_leave", {"leave_type": "annual", "start_date": "2026-11-10", "end_date": "2026-11-10", "days": 1, "reason": "Isolated test"}, intern)
            await call("approve_leave", {"request_id": leave["request_id"], "decision": "approved"}, hr)
            await call("send_notification", {"employee_id": 5, "title": "Release test", "message": "Isolated copy only"}, hr)
            employee = await call("create_employee", {"employee_code": "REL-TEST", "full_name": "Release Test", "email": "release-test@example.invalid", "department_id": 2,
                                                      "designation": "Test", "employment_type": "intern", "manager_employee_id": 2, "joining_date": "2026-11-03"}, hr)
            await call("update_employee_status", {"employee_id": employee["employee_id"], "status": "inactive"}, hr)
            await call("create_user_credentials", {"employee_id": employee["employee_id"], "username": "release.test", "password": "Isolated#2026", "role": "intern"}, hr)
            await call("update_user_credentials", {"username": "release.test", "new_password": "Rotated#2026", "new_role": ""}, hr)
            await call("delete_user_credentials", {"username": "release.test"}, hr)
            for token in tokens.values():
                await call("logout", token=token)
            assert {r["tool"] for r in records} == catalog, catalog - {r["tool"] for r in records}
            report = {"created_at": datetime.now(timezone.utc).isoformat(), "cwd": str(ROOT),
                      "python": sys.executable, "runtime_database": str(runtime["database"]),
                      "versions": {name: version(name) for name in ("google-adk", "google-genai", "mcp", "qdrant-client")},
                      "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                        for folder in (ROOT / "company_system", ROOT / "mcp_server")
                                        for path in folder.rglob("*.py")},
                      "transport": transport, "tools_discovered": len(catalog), "tools_executed": len({r["tool"] for r in records}),
                      "schemas_validated": len(tools), "invalid_argument_rejected": invalid.is_error, "unknown_tool_rejected": unknown.is_error,
                      "discovery": discovery, "passed": all(r["passed"] for r in records), "results": records}
            output = output_path or ROOT / "evaluations/results" / f"remediation_mcp_{transport}.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists():
                output.with_name(output.stem + "_previous_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + output.suffix).write_bytes(output.read_bytes())
            output.write_text(json.dumps(report, indent=2))
    finally:
        if process:
            if os.name == "nt" and process.poll() is None:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               capture_output=True, timeout=10, check=False)
            elif process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            with socket.socket() as probe:
                probe.settimeout(1)
                if probe.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("MCP HTTP test server still listens after shutdown")
            if "report" in locals():
                report["server_shutdown_verified"] = True
                output.write_text(json.dumps(report, indent=2))
        if log:
            log.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    asyncio.run(verify(args.transport, args.output))
