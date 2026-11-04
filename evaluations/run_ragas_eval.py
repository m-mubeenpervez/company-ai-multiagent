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


METRIC_NAMES = ("faithfulness", "context_precision", "context_recall")


def _score_value(result) -> float:
    value = getattr(result, "value", None)
    if value is None:
        raise ValueError("Metric returned no score")
    score = float(value)
    if not math.isfinite(score) or not 0 <= score <= 1:
        raise ValueError(f"Metric returned an invalid score: {score}")
    return score


def create_evaluator():
    """Build the single async Gemini evaluator shared by every metric."""
    import instructor
    from company_system.security.quota import guarded_completion
    from ragas.llms import llm_factory

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing. Add it to the working copy's .env file.")

    model = os.getenv("GEMINI_EVAL_MODEL") or os.getenv("GEMINI_LLM_MODEL", "gemini-3.5-flash-lite")
    # Configure Gemini API for LiteLLM
    os.environ["GEMINI_API_KEY"] = api_key

    # LiteLLM Gemini model identifier
    litellm_model = (
        model if model.startswith("gemini/")
        else f"gemini/{model}"
    )

    # Create async Instructor client
    async_client = instructor.from_litellm(
        guarded_completion,
        async_client=True
    )

    # Initialize RAGAS async evaluator
    evaluator_llm = llm_factory(
        litellm_model,
        provider="google",
        client=async_client,
        adapter="litellm",
        max_retries=3,
        num_retries=2,
    )

    print(f"RAGAS evaluator: {type(evaluator_llm).__module__}.{type(evaluator_llm).__name__}")
    print(f"Evaluator client: {type(evaluator_llm.client).__name__}; model: {litellm_model}")
    print(f"Async support: {evaluator_llm.is_async}", flush=True)
    if evaluator_llm.client is not async_client or not evaluator_llm.is_async:
        raise RuntimeError("RAGAS requires the async Instructor LiteLLM client")
    return evaluator_llm, model


async def _run(args) -> int:
    # Package imports construct MCP toolsets with a snapshot of child env.
    # Select disposable data before any CompanyAI import captures those paths.
    runtime = prepare_isolated_runtime("ragas") if not args.verify_evaluator else None
    from evaluations.reporting import provider_quota_blocked, provenance
    from evaluations.checkpointing import CaseCheckpoint
    from company_system.security.quota import record_quota
    from company_system.security.secret_boundary import redact
    evaluator_llm, model = create_evaluator()
    if args.verify_evaluator:
        from pydantic import BaseModel

        class EvaluationTest(BaseModel):
            answer: str

        result = await evaluator_llm.agenerate(
            prompt="Return a short answer saying Gemini async evaluation works.",
            response_model=EvaluationTest,
        )
        if not result.answer.strip():
            raise RuntimeError("Async evaluator returned an empty answer")
        print(f"API TEST RESULT: {result.answer}")
        print("ASYNC GEMINI TEST PASSED")
        return 0

    # Observe the same structured generations used by the metrics. Do not
    # change prompts, outputs, or scores, or make additional judge requests.
    generation_trace = []
    active_metric = None
    original_agenerate = evaluator_llm.agenerate

    async def traced_agenerate(prompt, response_model):
        result = await original_agenerate(prompt, response_model)
        generation_trace.append({
            "metric": active_metric,
            "response_model": response_model.__name__,
            "output": result.model_dump(mode="json"),
        })
        return result

    evaluator_llm.agenerate = traced_agenerate

    from ragas.metrics.collections import Faithfulness, ContextPrecision, ContextRecall
    from evaluations.adk_harness import close_runner, run_companyai_case

    faithfulness_metric = Faithfulness(llm=evaluator_llm)
    precision_metric = ContextPrecision(llm=evaluator_llm)
    recall_metric = ContextRecall(llm=evaluator_llm)
    metrics = dict(zip(METRIC_NAMES, (faithfulness_metric, precision_metric, recall_metric)))
    if any(metric.llm is not evaluator_llm or not metric.llm.is_async for metric in metrics.values()):
        raise RuntimeError("All metrics must share the async evaluator")

    dataset_path = ROOT / "evaluations" / "datasets" / "rag_cases.json"
    manifest = provenance(dataset_path)
    rows = json.loads(dataset_path.read_text(encoding="utf-8"))
    if args.limit is not None:
        rows = rows[: max(1, args.limit)]

    checkpoint_path = Path(getattr(args, "output", None) or ROOT / "evaluations/results/ragas_eval_improved.json").with_suffix(".checkpoint.json")
    checkpoint = CaseCheckpoint(checkpoint_path, manifest, rows, resume=getattr(args, "resume", False))
    report_rows = []
    try:
        for index, case in enumerate(rows, 1):
            if case["id"] in checkpoint.completed:
                report_rows.append(checkpoint.completed[case["id"]])
                print("RESUMED completed case: " + case["id"], flush=True)
                continue
            generation_trace.clear()
            print(f"\nRAGAS case {index}/{len(rows)}: {case['id']}", flush=True)
            row = {"id": case["id"], "question": case["question"],
                   "reference": case["reference"], "status": "error", **dict.fromkeys(METRIC_NAMES)}
            try:
                run = await run_companyai_case(case["question"], username="intern.mubeen")
                contexts = run["retrieval_context"]
                answer = run["actual_output"]
                row.update(
                    route=run["route"],
                    tool_names=[tool["name"] for tool in run["tools_called"]],
                    retrieved_context_count=len(contexts),
                    actual_output=answer,
                    retrieved_contexts=contexts,
                    retrieved_sources=run.get("retrieved_sources", []),
                    tools_called=run["tools_called"],
                )
                if run["route"] != "policy_agent":
                    raise RuntimeError(f"Expected policy_agent, got {run['route']!r}; {run.get('routing_error') or 'no router error recorded'}")
                if not contexts:
                    raise RuntimeError("Policy Agent did not return retrievable context passages.")
                if not answer:
                    raise RuntimeError("CompanyAI returned an empty final answer.")

                metric_errors = {}
                for name, metric in metrics.items():
                    active_metric = name
                    inputs = dict(user_input=case["question"], retrieved_contexts=contexts)
                    if name == "faithfulness":
                        inputs["response"] = answer
                    else:
                        inputs["reference"] = case["reference"]
                    try:
                        result = await metric.ascore(**inputs)
                        row[name] = _score_value(result)
                        row[f"{name}_reason"] = getattr(result, "reason", None)
                    except Exception as exc:
                        record_quota(exc)
                        metric_errors[name] = redact(f"{type(exc).__name__}: {exc}")
                        if provider_quota_blocked(exc):
                            break
                if metric_errors:
                    row["metric_errors"] = metric_errors
                    row["error"] = "; ".join(f"{name}: {error}" for name, error in metric_errors.items())
                else:
                    row["status"] = "completed"
            except Exception as exc:
                record_quota(exc)
                row["error"] = redact(f"{type(exc).__name__}: {exc}")
                row["attempted"] = "no request sent" not in str(exc)

            if provider_quota_blocked(row.get("error", "")):
                row["status"] = "blocked"
            row["metric_trace"] = list(generation_trace)
            report_rows.append(row)
            console_row = {key: value for key, value in row.items() if key not in {
                "metric_trace", "retrieved_contexts", "retrieved_sources", "tools_called",
            }}
            print(json.dumps(console_row, indent=2, allow_nan=False), flush=True)
            if provider_quota_blocked(row.get("error", "")):
                row["status"] = "blocked"
                row.setdefault("attempted", True)
                report_rows.extend({"id": remaining["id"], "status": "blocked", "attempted": False,
                                    "error": "Not executed: Gemini provider quota cooldown."}
                                   for remaining in rows[index:])
                checkpoint.save(report_rows)
                break
            checkpoint.save(report_rows)
            if index < len(rows) and args.delay > 0:
                await asyncio.sleep(args.delay)
    finally:
        await close_runner()

    valid = [row for row in report_rows if row.get("status") == "completed"]
    averages = {}
    for name in METRIC_NAMES:
        values = [row[name] for row in valid if row.get(name) is not None]
        averages[name] = round(sum(values) / len(values), 4) if values else None

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provenance": manifest,
        "evaluator_model": model,
        "evaluator_type": f"{type(evaluator_llm).__module__}.{type(evaluator_llm).__name__}",
        "evaluator_async": evaluator_llm.is_async,
        "runtime_database": str(runtime["database"]),
        "cases_configured": len(rows),
        "cases_run": sum(row.get("attempted", True) and row["id"] not in checkpoint.completed for row in report_rows),
        "resumed": len(checkpoint.completed),
        "completed": len(valid),
        "failed": sum(row.get("status") == "error" for row in report_rows),
        "blocked": sum(row.get("status") == "blocked" for row in report_rows),
        "average_scores": averages,
        "results": report_rows,
    }

    results_dir = ROOT / "evaluations" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output = Path(args.output) if getattr(args, "output", None) else results_dir / "ragas_eval_improved.json"
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        archive = results_dir / f"ragas_eval_previous_{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}.json"
        archive.write_bytes(output.read_bytes())
    output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")

    print("\nRAGAS SUMMARY")
    print(json.dumps({"completed": len(valid), "failed": report["failed"], "blocked": report["blocked"], "average_scores": averages}, indent=2))
    print(f"Report: {output}")
    return 0 if valid and len(valid) == len(report_rows) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAGAS on the real CompanyAI Policy Agent.")
    parser.add_argument("--limit", type=int, default=None, help="Number of RAG goldens (default: all).")
    parser.add_argument("--resume", action="store_true", help="Resume completed cases only when checkpoint provenance matches.")
    parser.add_argument("--verify-evaluator", action="store_true", help="Test async structured generation using the evaluation's actual factory.")
    parser.add_argument("--delay", type=float, default=65.0, help="Seconds between test cases (default 65 for free-tier quotas).")
    parser.add_argument("--output", type=Path, help="Report path (default: results/ragas_eval_improved.json; preserves baseline).")
    args = parser.parse_args()
    return asyncio.run(_run(args))


if __name__ == "__main__":
    raise SystemExit(main())
