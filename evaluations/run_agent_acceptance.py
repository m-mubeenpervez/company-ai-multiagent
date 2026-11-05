"""Explicit-input agent smoke coverage, distinct from DeepEval model judgments."""
from __future__ import annotations
import argparse
import asyncio
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluations.runtime_isolation import prepare_isolated_runtime
from evaluations.checkpointing import CaseCheckpoint, write_json_atomic
from evaluations.reporting import provenance, provider_quota_blocked


async def run(args):
    runtime = prepare_isolated_runtime("agent_acceptance")
    from evaluations.adk_harness import run_companyai_case, close_runner
    from company_system.agent import root_agent
    from company_system.mcp.client import DOMAIN_TOOLS
    from company_system.mcp.secure_toolset import CREDENTIAL_TOOLS
    from company_system.security.secret_boundary import redact
    dataset = ROOT / "evaluations/datasets/agent_acceptance_cases.json"
    cases = json.loads(dataset.read_text())
    manifest = provenance(dataset)
    checkpoint = CaseCheckpoint(args.output.with_suffix(".checkpoint.json"), manifest, cases, resume=args.resume)
    resumed_ids = frozenset(checkpoint.completed)
    server = ast.parse((ROOT / "mcp_server/server.py").read_text())
    required = {node.name: [arg.arg for arg in node.args.args[:len(node.args.args)-len(node.args.defaults)]
                            if arg.arg != "session_token"] for node in server.body if isinstance(node, ast.FunctionDef)}
    inventory = []
    for agent in root_agent.sub_agents:
        domain = agent.name.removesuffix("_agent")
        inventory.append({"name": agent.name, "description": agent.description,
                          "instruction_file": "company_system/agents/" + agent.name + ".py",
                          "instruction_sha256": hashlib.sha256((ROOT / "company_system/agents" / (agent.name + ".py")).read_bytes()).hexdigest(),
                          "model_tools": [name for name in DOMAIN_TOOLS[domain] if name not in CREDENTIAL_TOOLS],
                          "required_tool_inputs": {name: required.get(name, []) for name in DOMAIN_TOOLS[domain]},
                          "authorization": "Authoritative MCP account, role and ownership checks; routing grants no rights.",
                          "response": "Concise factual text grounded in actual tool results; no universal structured JSON contract.",
                          "error_handling": "Preserve tool denial/not_found/error; provider failures are not successful output."})
    results = []
    try:
        for index, case in enumerate(cases):
            if case["id"] in checkpoint.completed:
                results.append(checkpoint.completed[case["id"]])
                continue
            row = {"id": case["id"], "agent": case["expected_route"], "kind": case["kind"], "passed": False}
            try:
                actual = await run_companyai_case(case["input"], case["username"])
                names = [tool["name"] for tool in actual["tools_called"]]
                if case["kind"] == "missing_input":
                    passed = not names and bool(actual["actual_output"])
                else:
                    passed = set(case["expected_tools"]).issubset(names) and bool(actual["actual_output"])
                    if not case.get("expected_tool_status"):
                        passed = passed and all(any(result["name"] == name and result["status"] == "success"
                                                   for result in actual["tool_results"])
                                                for name in case["expected_tools"])
                if case.get("expected_tool_status"):
                    passed = passed and any(item["name"] in case["expected_tools"] and item["status"] == case["expected_tool_status"]
                                            for item in actual["tool_results"])
                row.update(actual, status="completed", passed=passed and actual["route"] == case["expected_route"], tool_names=names)
            except Exception as exc:
                blocked = provider_quota_blocked(exc)
                row.update(status="blocked" if blocked else "error", error=redact(str(exc)), attempted="no request sent" not in str(exc))
                if blocked:
                    results.append(row)
                    results.extend({"id": item["id"], "agent": item["expected_route"], "kind": item["kind"],
                                    "status": "blocked", "passed": False, "attempted": False,
                                    "error": "Provider quota cooldown; no request sent."} for item in cases[index+1:])
                    checkpoint.save(results)
                    break
            results.append(row)
            checkpoint.save(results)
            if args.delay > 0 and index < len(cases)-1:
                await asyncio.sleep(args.delay)
    finally:
        await close_runner()
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "provenance": manifest,
              "runtime_database": str(runtime["database"]), "inventory": inventory,
              "cases_configured": len(cases),
              "cases_run": sum(item.get("attempted", True) and item["id"] not in resumed_ids for item in results),
              "resumed": len(resumed_ids),
              "completed": sum(item["status"] == "completed" for item in results),
              "passed": sum(item["passed"] for item in results),
              "failed": sum(not item["passed"] and item["status"] != "blocked" for item in results),
              "blocked": sum(item["status"] == "blocked" for item in results), "results": results,
              "note": "Tool/route smoke assertions are not model-judged answer quality or exhaustive workflow proof."}
    write_json_atomic(args.output, report)
    print(json.dumps({key: report[key] for key in ("cases_configured", "completed", "passed", "failed", "blocked")}))
    return 0 if report["passed"] == len(cases) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evaluations/results/agent_acceptance_remediation.json")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--delay", type=float, default=65)
    raise SystemExit(asyncio.run(run(parser.parse_args())))
