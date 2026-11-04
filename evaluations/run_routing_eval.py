from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from company_system.routing.semantic_router_agent import classify_route
from evaluations.reporting import provider_quota_blocked, provenance
from evaluations.checkpointing import CaseCheckpoint, write_json_atomic
from company_system.security.secret_boundary import redact
from company_system.security.quota import record_quota


DATASET = ROOT / "evaluations" / "datasets" / "routing_cases.json"
RESULTS = ROOT / "evaluations" / "results"


def select_cases(rows: list[dict], limit: int, full: bool) -> list[dict]:
    if full:
        return rows
    # The default run covers every route once before adding paraphrases.
    first_per_route: dict[str, dict] = {}
    for row in rows:
        first_per_route.setdefault(row["expected_route"], row)
    selected = list(first_per_route.values())
    if limit <= len(selected):
        return selected[:limit]
    selected_ids = {row["id"] for row in selected}
    extras = [row for row in rows if row["id"] not in selected_ids]
    return selected + extras[: max(0, limit - len(selected))]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate CompanyAI Gemini semantic routing.")
    parser.add_argument("--output", type=Path, default=RESULTS / "routing_eval_remediation.json")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", type=int, default=18, help="Number of cases (default covers each route once).")
    parser.add_argument("--full", action="store_true", help="Run all routing paraphrases.")
    parser.add_argument("--delay", type=float, default=6.0, help="Seconds between Gemini calls (default 6 for free-tier quotas).")
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is missing. Add it to the working copy's .env file.")

    rows = json.loads(DATASET.read_text(encoding="utf-8"))
    selected = select_cases(rows, max(1, args.limit), args.full)

    manifest = provenance(DATASET)
    checkpoint = CaseCheckpoint(args.output.with_suffix(".checkpoint.json"), manifest, selected, resume=args.resume)
    results = []
    for index, case in enumerate(selected, 1):
        if case["id"] in checkpoint.completed:
            results.append(checkpoint.completed[case["id"]])
            print("RESUMED completed case: " + case["id"], flush=True)
            continue
        record = {
            "id": case["id"],
            "expected_route": case["expected_route"],
            "actual_route": None,
            "confidence": None,
            "passed": False,
            "error": None,
            "status": "completed",
        }
        try:
            decision = classify_route(case["input"])
            record["actual_route"] = decision.route
            record["confidence"] = decision.confidence
            record["reason"] = decision.reason
            record["passed"] = decision.route == case["expected_route"]
        except Exception as exc:
            record_quota(exc)
            record["error"] = redact(f"{type(exc).__name__}: {exc}")
            record["attempted"] = "no request sent" not in str(exc)
            record["status"] = "blocked" if provider_quota_blocked(exc) else "error"
        results.append(record)

        state = "BLOCKED" if record["status"] == "blocked" else "PASS" if record["passed"] else "FAIL"
        print(
            f"{state} | {index}/{len(selected)} | {case['id']} | "
            f"expected={case['expected_route']} actual={record['actual_route']} "
            f"confidence={record['confidence']}"
        )
        if record["status"] == "blocked":
            results.extend({"id": row["id"], "expected_route": row["expected_route"], "actual_route": None,
                            "confidence": None, "passed": False, "status": "blocked", "attempted": False,
                            "error": "Not executed: Gemini provider quota cooldown."}
                           for row in selected[index:])
            checkpoint.save(results)
            break
        checkpoint.save(results)
        if index < len(selected) and args.delay > 0:
            time.sleep(args.delay)

    passed = sum(bool(row["passed"]) for row in results)
    total = len(results)
    measured = [row for row in results if row.get("status") == "completed"]
    accuracy = passed / len(measured) if measured else None
    by_route = {}
    grouped = {}
    for row in results:
        grouped.setdefault(row["expected_route"], []).append(row)
    for route, items in grouped.items():
        by_route[route] = {
            "passed": sum(bool(item["passed"]) for item in items),
            "total": len(items),
        }

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provenance": manifest,
        "model": os.getenv("GEMINI_ROUTER_MODEL", "configured CompanyAI router model"),
        "cases_configured": total,
        "cases_run": sum(row.get("attempted", True) and row["id"] not in checkpoint.completed for row in results),
        "resumed": len(checkpoint.completed),
        "completed": len(measured),
        "passed": passed,
        "failed": sum(row.get("status") != "blocked" and not row["passed"] for row in results),
        "blocked": sum(row.get("status") == "blocked" for row in results),
        "accuracy_on_completed": round(accuracy, 4) if accuracy is not None else None,
        "coverage": round(len(measured) / total, 4) if total else 0,
        "per_route": by_route,
        "results": results,
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    output = args.output
    if output.exists():
        archive = output.with_name(output.stem + "_previous_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + output.suffix)
        archive.write_bytes(output.read_bytes())
    write_json_atomic(output, report)

    print("\nROUTING EVALUATION")
    print(f"Passed: {passed}/{total}")
    print(f"Completed: {len(measured)}/{total}; blocked: {report['blocked']}")
    print("Accuracy on completed: " + (f"{accuracy:.1%}" if accuracy is not None else "unavailable"))
    print(f"Report: {output}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
