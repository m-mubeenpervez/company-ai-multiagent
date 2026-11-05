"""Execute one acceptance command and retain its exact command/status/timing."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--cwd", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--log", type=Path, help="Unique log path; existing files are rejected.")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    args.cwd = args.cwd.resolve()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.label):
        parser.error("Invalid evidence label.")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    output = ROOT / "evaluations/results"
    receipt_path = output / (args.label + ".command.json")
    if receipt_path.exists():
        parser.error("Receipt already exists; choose a new evidence label.")
    log = (args.log or (output / (args.label + ".log"))).resolve()
    if not log.is_relative_to(ROOT) or log.exists():
        parser.error("Log path must be inside the working tree and must not already exist.")
    log.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    with log.open("wb") as stream:
        result = subprocess.run(command, cwd=args.cwd, stdout=stream, stderr=subprocess.STDOUT, timeout=2400)
    record = {"label": args.label, "command": command, "cwd": str(args.cwd),
              "interpreter": command[0], "started_at": started.isoformat(),
              "local_started_at": started.astimezone(ZoneInfo("Asia/Karachi")).isoformat(),
              "finished_at": datetime.now(timezone.utc).isoformat(), "exit_status": result.returncode,
              "status": "PASS" if result.returncode == 0 else "FAIL", "log": str(log)}
    content = log.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"Ran (\d+) tests? in", content)
    if matches:
        count = sum(map(int, matches))
        record["counts"] = {"configured": count, "passed": count if result.returncode == 0 else None,
                            "blocked": 0, "not_run": 0}
    script_count = len(re.findall(r"RUN \| tests[\\/]", content))
    if script_count:
        record["counts"] = {"regression_scripts": script_count,
                            "failed_scripts": 0 if result.returncode == 0 else None,
                            "security_checks": 13 if "Passed: 13/13" in content else None}
    if args.report and args.report.exists():
        data = json.loads(args.report.read_text(encoding="utf-8"))
        record["report"] = str(args.report)
        record["counts"] = {key: data.get(key) for key in (
            "cases_configured", "cases_run", "completed", "passed", "failed", "errors", "blocked")}
        if data.get("blocked"):
            record["status"] = "BLOCKED" if not data.get("failed", 0) else "FAIL"
        if "tools_executed" in data:
            record["counts"] = {"tools": data["tools_executed"], "schemas": data["schemas_validated"],
                                "passed": data["tools_executed"] if data["passed"] else None,
                                "failed": 0 if data["passed"] else None, "blocked": 0, "not_run": 0}
    receipt_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    ledger = output / "remediation_test_runs.json"
    records = json.loads(ledger.read_text()) if ledger.exists() else []
    records.append(record)
    ledger.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))
    print(content[-1600:])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
