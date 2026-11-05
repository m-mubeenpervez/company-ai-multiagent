from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from evaluations.runtime_isolation import prepare_isolated_runtime


COMMON_OWN_TOOLS = [
    "login", "logout", "get_login_identity",
    "get_employee_profile", "search_employee_by_name", "get_attendance", "attendance_summary", "get_leave_balance",
    "get_intern_profile", "get_intern_report_status",
    "request_leave", "submit_expense",
    "search_company_policy", "get_performance_reviews",
    "get_training_assignments", "get_employee_projects", "get_employee_tasks",
    "get_payroll", "get_expense_claims", "get_assigned_assets",
    "list_documents", "get_my_notifications",
]

ROLE_ALLOWED_TOOLS = {
    "intern": COMMON_OWN_TOOLS + [
        "get_intern_profile", "get_intern_report_status",
    ],
    "employee": COMMON_OWN_TOOLS,
    "manager": COMMON_OWN_TOOLS + [
        "search_employee_by_name", "get_intern_profile", "get_intern_report_status",
        "approve_leave", "attendance_summary", "company_operational_summary",
        "company_people_summary", "list_missing_intern_reports",
        "send_notification",
    ],
    "hr": COMMON_OWN_TOOLS + [
        "list_employees", "create_employee", "update_employee_status",
        "create_user_credentials", "update_user_credentials", "delete_user_credentials",
        "search_employee_by_name", "get_intern_profile", "get_intern_report_status",
        "list_missing_intern_reports", "attendance_summary", "approve_leave",
        "list_candidates", "get_interview_status", "company_people_summary",
        "company_operational_summary", "get_recent_audit_logs", "send_notification",
    ],
    "recruiter": COMMON_OWN_TOOLS + ["list_candidates", "get_interview_status"],
    "finance": COMMON_OWN_TOOLS + ["review_expense"],
    "it": COMMON_OWN_TOOLS + ["list_available_assets"],
    "admin": COMMON_OWN_TOOLS + [
        "list_employees", "search_employee_by_name", "get_intern_profile",
        "get_intern_report_status", "list_missing_intern_reports",
        "attendance_summary", "company_people_summary",
        "company_operational_summary", "get_recent_audit_logs", "send_notification",
    ],
}



async def _measure(metric, test_case) -> dict:
    await metric.a_measure(test_case, _show_indicator=False)
    score = getattr(metric, "score", None)
    if score is None or not math.isfinite(float(score)) or not 0 <= float(score) <= 1:
        raise ValueError("Metric returned a missing or invalid score")
    return {
        "name": type(metric).__name__ if type(metric).__name__ != "GEval" else "ExpectedAnswerCorrectness",
        "score": float(score),
        "reason": getattr(metric, "reason", None),
        "passed": bool(metric.is_successful()),
    }


async def _run(args) -> int:
    # MCP child environments must capture disposable paths, never active data.
    runtime = prepare_isolated_runtime("deepeval")
    from evaluations.reporting import provider_quota_blocked, provenance
    from evaluations.checkpointing import CaseCheckpoint
    from company_system.security.quota import record_quota
    from company_system.security.secret_boundary import redact
    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")
    os.environ.setdefault("DEEPEVAL_HOME", str(runtime["runtime_root"] / "deepeval-home"))
    os.environ.setdefault("DEEPEVAL_RETRY_MAX_ATTEMPTS", "2")

    from evaluations.gemini_judge import QuotaAwareGeminiJudge
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        ToolCorrectnessMetric,
        ArgumentCorrectnessMetric,
        ContextualRelevancyMetric,
        GEval,
    )
    from deepeval.test_case import LLMTestCase, ToolCall, SingleTurnParams

    from evaluations.adk_harness import close_runner, run_companyai_case

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing. Add it to the working copy's .env file.")

    model_name = os.getenv("GEMINI_EVAL_MODEL") or os.getenv("GEMINI_LLM_MODEL", "gemini-3.5-flash-lite")
    from google.genai import types
    judge_model = QuotaAwareGeminiJudge(model=model_name, api_key=api_key, http_options=types.HttpOptions(timeout=120_000, retry_options=types.HttpRetryOptions(attempts=1)))

    dataset_path = ROOT / "evaluations" / "datasets" / "agent_cases.json"
    manifest = provenance(dataset_path)
    all_cases = json.loads(dataset_path.read_text(encoding="utf-8"))
    cases = all_cases if args.full else all_cases[: max(1, args.limit)]
    if args.full:
        cases += json.loads((dataset_path.parent / "deepeval_failure_cases.json").read_text(encoding="utf-8"))

    import hashlib
    manifest["selected_cases_sha256"] = hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest()
    manifest["judge_arguments"] = args.judge_arguments
    checkpoint = CaseCheckpoint(Path(args.output or ROOT / "evaluations/results/deepeval_eval_release.json").with_suffix(".checkpoint.json"),
                                manifest, cases, resume=getattr(args, "resume", False))
    resumed_ids = frozenset(checkpoint.completed)
    results = []
    try:
        for index, case in enumerate(cases, 1):
            if case["id"] in checkpoint.completed:
                results.append(checkpoint.completed[case["id"]])
                print("RESUMED completed case: " + case["id"], flush=True)
                continue
            print(f"\nDeepEval case {index}/{len(cases)}: {case['id']}")
            try:
                run = await run_companyai_case(case["input"], username=case["username"])
                if not run["route"]:
                    raise RuntimeError(f"No specialist executed: {run.get('routing_error') or 'router/model unavailable'}")
                actual_tools = [
                    ToolCall(
                        name=item["name"],
                        input_parameters=item.get("input_parameters") or {},
                    )
                    for item in run["tools_called"]
                ]
                expected_tools = [ToolCall(name=name) for name in case["expected_tools"]]

                test_case = LLMTestCase(
                    input=case["input"],
                    actual_output=run["actual_output"] or "(No final answer returned)",
                    expected_output=case["expected_output"],
                    retrieval_context=run["retrieval_context"] or None,
                    tools_called=actual_tools,
                    expected_tools=expected_tools,
                )

                if case.get("expected_tool_status") in {"forbidden", "auth_required"}:
                    relevance_metric = GEval(
                        name="DenialAwareAnswerRelevancy",
                        criteria=("Assess whether the actual answer directly addresses the input while preserving "
                                  "the expected access denial. A concise refusal is relevant when the expected "
                                  "output requires denial; penalize disclosure, evasion, or unrelated content."),
                        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT,
                                           SingleTurnParams.EXPECTED_OUTPUT],
                        model=judge_model, threshold=0.65, async_mode=True,
                    )
                else:
                    relevance_metric = AnswerRelevancyMetric(
                        model=judge_model, threshold=0.65, include_reason=True, async_mode=True,
                    )
                metrics = [
                    ToolCorrectnessMetric(
                        model=judge_model,
                        threshold=1.0,
                        include_reason=True,
                        async_mode=True,
                    ),
                    relevance_metric,
                ]

                metrics.append(GEval(
                    name="ExpectedAnswerCorrectness",
                    criteria=("Assess whether the actual answer fulfills the expected output for the input. "
                              "Do not penalize wording or formatting differences. Do penalize contradictions, "
                              "missing required facts, or disclosure when the expected answer requires denial."),
                    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
                    model=judge_model, threshold=0.70, async_mode=True,
                ))
                if case.get("evaluation_scope") == "rag":
                    metrics.extend([
                        FaithfulnessMetric(model=judge_model, threshold=0.70, include_reason=True),
                        ContextualRelevancyMetric(model=judge_model, threshold=0.65, include_reason=True),
                    ])

                if args.judge_arguments and actual_tools:
                    metrics.append(
                        ArgumentCorrectnessMetric(
                            model=judge_model,
                            threshold=0.70,
                            include_reason=True,
                            async_mode=True,
                        )
                    )

                allowed = set(ROLE_ALLOWED_TOOLS[case["role"]])
                unauthorized = sorted({tool.name for tool in actual_tools} - allowed)
                unblocked = [name for name in unauthorized if
                             not any(row["name"] == name for row in run["tool_results"])
                             or any(row["name"] == name and row["status"] not in {"forbidden", "auth_required"}
                                    for row in run["tool_results"])]
                metric_results = [{
                    "name": "ToolAuthorizationCheck", "score": 0.0 if unblocked else 1.0,
                    "passed": not unblocked, "reason": "Unblocked unauthorized tool names: " + ", ".join(unblocked),
                    "unauthorized_attempts": unauthorized,
                }]
                if case.get("expected_tool_status"):
                    status_ok = any(row["name"] in case["expected_tools"] and row["status"] == case["expected_tool_status"]
                                    for row in run["tool_results"])
                    metric_results.append({"name": "ExpectedFailureCheck", "score": float(status_ok), "passed": status_ok})
                for metric in metrics:
                    try:
                        metric_results.append(await _measure(metric, test_case))
                    except Exception as metric_error:
                        record_quota(metric_error)
                        metric_results.append({
                            "name": type(metric).__name__,
                            "score": None,
                            "passed": False,
                            "error": redact(f"{type(metric_error).__name__}: {metric_error}"),
                        })
                        if provider_quota_blocked(metric_error):
                            break

                row = {
                    "id": case["id"],
                    "expected_route": case["expected_route"],
                    "actual_route": run["route"],
                    "route_passed": run["route"] == case["expected_route"],
                    "tool_names": [item["name"] for item in run["tools_called"]],
                    "tools_called": run["tools_called"],
                    "expected_tool_names": case["expected_tools"],
                    "retrieved_context_count": len(run["retrieval_context"]),
                    "metrics": metric_results,
                    "actual_output": run["actual_output"],
                    "retrieval_context": run["retrieval_context"],
                    "retrieved_sources": run["retrieved_sources"],
                    "tool_results": run["tool_results"],
                    "status": "error" if any("error" in m for m in metric_results) else "completed",
                    "passed": run["route"] == case["expected_route"] and all(m["passed"] for m in metric_results),
                }
            except Exception as exc:
                record_quota(exc)
                row = {
                    "id": case["id"],
                    "status": "error",
                    "error": redact(f"{type(exc).__name__}: {exc}"),
                    "attempted": "no request sent" not in str(exc),
                }

            if provider_quota_blocked(json.dumps(row)):
                row["status"] = "blocked"
            results.append(row)
            print(json.dumps({k: v for k, v in row.items() if k not in {"retrieval_context"}}, indent=2), flush=True)
            if provider_quota_blocked(json.dumps(row)):
                row["status"] = "blocked"
                row.setdefault("attempted", True)
                results.extend({"id": remaining["id"], "status": "blocked", "attempted": False,
                                "passed": False, "reason": "Not executed: Gemini provider quota cooldown."}
                               for remaining in cases[index:])
                checkpoint.save(results)
                break
            checkpoint.save(results)
            if index < len(cases) and args.delay > 0:
                await asyncio.sleep(args.delay)
    finally:
        await close_runner()


    completed = [row for row in results if row.get("status") == "completed"]
    metric_summary = {}
    all_metric_names = sorted({
        metric["name"]
        for row in completed
        for metric in row.get("metrics", [])
    })
    for name in all_metric_names:
        values = [
            metric["score"]
            for row in completed
            for metric in row.get("metrics", [])
            if metric["name"] == name and metric.get("score") is not None
        ]
        metric_summary[name] = round(sum(values) / len(values), 4) if values else None

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provenance": manifest,
        "evaluator_model": model_name,
        "cases_configured": len(cases),
        "cases_run": sum(row.get("attempted", True) and row["id"] not in resumed_ids for row in results),
        "resumed": len(resumed_ids),
        "completed": len(completed),
        "errors": sum(row.get("status") == "error" for row in results),
        "blocked": sum(row.get("status") == "blocked" for row in results),
        "passed": sum(bool(row.get("passed")) for row in results),
        "failed": sum(row.get("status") != "blocked" and not bool(row.get("passed")) for row in results),
        "average_scores": metric_summary,
        "results": results,
    }

    results_dir = ROOT / "evaluations" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output = args.output or results_dir / "deepeval_eval_release.json"
    if output.exists():
        archive = output.with_name(output.stem + "_previous_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + output.suffix)
        output.replace(archive)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\nDEEPEVAL SUMMARY")
    print(json.dumps(metric_summary, indent=2))
    print(f"Report: {output}")
    return 0 if results and all(row.get("passed") for row in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DeepEval against real CompanyAI agent turns.")
    parser.add_argument("--resume", action="store_true", help="Resume provenance-matching completed cases without executing them twice.")
    parser.add_argument("--limit", type=int, default=3, help="Number of CompanyAI agent cases (default 3).")
    parser.add_argument("--full", action="store_true", help="Run all 18 specialist-agent cases and separate access-denial cases.")
    parser.add_argument("--output", type=Path, help="Separate JSON report path.")
    parser.add_argument("--delay", type=float, default=65.0, help="Seconds between test cases (default 65 for free-tier quotas).")
    parser.add_argument(
        "--judge-arguments",
        action="store_true",
        help="Also run the LLM-judged ArgumentCorrectnessMetric (extra Gemini calls).",
    )
    args = parser.parse_args()
    return asyncio.run(_run(args))


if __name__ == "__main__":
    raise SystemExit(main())
