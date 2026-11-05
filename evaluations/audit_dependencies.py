"""Audit actual environments and frozen dependency sets without changing them."""
from pathlib import Path
import json
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
AUDITOR = ROOT / ".evaluation_runtime/dependency_audit_env/Scripts/python.exe"


def main():
    import argparse, re
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", default="")
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    suffix = args.suffix
    if not re.fullmatch(r"[A-Za-z0-9_-]*", suffix):
        parser.error("Invalid audit suffix")
    out = ROOT / "evaluations/results"
    targets = {
        "runtime": ["--path", str(ROOT / ".venv/Lib/site-packages")],
        "evaluation": ["--path", str(ROOT / ".venv-eval/Lib/site-packages")],
        "candidate_runtime": ["--path", str(ROOT / ".release_candidate/CompanyAI/.venv/Lib/site-packages")],
        "candidate_evaluation": ["--path", str(ROOT / ".release_candidate/CompanyAI/.venv-eval/Lib/site-packages")],
        "runtime_lock": ["--no-deps", "-r", str(ROOT / "requirements-runtime-lock.txt")],
        "evaluation_lock": ["--no-deps", "-r", str(ROOT / "requirements-evaluation-lock.txt")],
    }
    records = []
    for name, flags in targets.items():
        if args.only and name not in args.only:
            continue
        report = out / f"remediation_audit_{name}{suffix}.json"
        command = [str(AUDITOR), "-m", "pip_audit", *flags, "--format", "json", "--output", str(report)]
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600)
        (out / f"remediation_audit_{name}{suffix}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        data = json.loads(report.read_text()) if report.exists() else {}
        vulnerable = [d for d in data.get("dependencies", []) if d.get("vulns")]
        record = {"name": name, "command": command, "started_at": started,
                  "finished_at": datetime.now(timezone.utc).isoformat(), "exit_status": result.returncode,
                  "status": "PASS" if result.returncode == 0 else "FAIL" if vulnerable else "BLOCKED",
                  "vulnerable_packages": len(vulnerable), "report": str(report)}
        records.append(record)
        print(json.dumps(record), flush=True)
        (out / f"remediation_dependency_scans{suffix}.json").write_text(json.dumps(records, indent=2))
    return int(any(r["status"] != "PASS" for r in records))


if __name__ == "__main__":
    raise SystemExit(main())
