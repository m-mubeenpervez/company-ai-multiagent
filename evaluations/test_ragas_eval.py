"""Offline checks for async wiring and failure reporting; no Gemini calls."""
from __future__ import annotations

import asyncio
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from evaluations import run_ragas_eval as evaluation


class RagasEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.quota_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.quota_dir.cleanup)
        self.quota_patch = patch("company_system.security.quota.STATE", Path(self.quota_dir.name) / "quota.json")
        self.quota_patch.start()
        self.addCleanup(self.quota_patch.stop)

    def test_default_report_preserves_baseline_and_records_judge_outputs(self):
        from pydantic import BaseModel
        from ragas.metrics import collections

        class JudgeOutput(BaseModel):
            verdict: int

        llm = SimpleNamespace(is_async=True, agenerate=AsyncMock(return_value=JudgeOutput(verdict=1)))

        async def score(**inputs):
            result = await llm.agenerate("unchanged prompt", JudgeOutput)
            return SimpleNamespace(value=float(result.verdict))

        harness = SimpleNamespace(close_runner=AsyncMock(), run_companyai_case=AsyncMock(return_value={
            "route": "policy_agent", "tools_called": [], "actual_output": "grounded answer",
            "retrieval_context": ["actual passage"],
            "retrieved_sources": [{"source": "handbook.pdf", "page": 2, "score": 0.8}],
        }))
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            root = Path(directory)
            (root / "evaluations/datasets").mkdir(parents=True)
            (root / "evaluations/datasets/rag_cases.json").write_text(json.dumps([
                {"id": "case", "question": "original question", "reference": "original reference"}
            ]), encoding="utf-8")
            results = root / "evaluations/results"
            results.mkdir()
            baseline = results / "ragas_eval_latest.json"
            baseline.write_bytes(b'{"historical": true}')
            stack.enter_context(patch.object(evaluation, "ROOT", root))
            stack.enter_context(patch.object(evaluation, "create_evaluator", return_value=(llm, "test")))
            stack.enter_context(patch.object(evaluation, "prepare_isolated_runtime", return_value={"database": root / "test.db"}))
            stack.enter_context(patch.dict("sys.modules", {"evaluations.adk_harness": harness}))
            for name in ("Faithfulness", "ContextPrecision", "ContextRecall"):
                stack.enter_context(patch.object(collections, name, return_value=SimpleNamespace(llm=llm, ascore=score)))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            code = asyncio.run(evaluation._run(SimpleNamespace(verify_evaluator=False, limit=None, delay=0)))
            self.assertEqual(code, 0)
            self.assertEqual(baseline.read_bytes(), b'{"historical": true}')
            row = json.loads((results / "ragas_eval_improved.json").read_text())["results"][0]
            self.assertEqual(row["actual_output"], "grounded answer")
            self.assertEqual(row["retrieved_contexts"], ["actual passage"])
            self.assertEqual(row["retrieved_sources"][0]["page"], 2)
            self.assertEqual([trace["metric"] for trace in row["metric_trace"]], list(evaluation.METRIC_NAMES))
            self.assertTrue(all(trace["output"] == {"verdict": 1} for trace in row["metric_trace"]))

    def test_invalid_scores_are_errors(self):
        for value in (None, float("nan"), float("inf"), -0.1, 1.1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluation._score_value(SimpleNamespace(value=value))
        self.assertEqual(evaluation._score_value(SimpleNamespace(value=0)), 0)

    def test_actual_factory_and_metrics_share_async_client(self):
        from ragas.metrics.collections import Faithfulness, ContextPrecision, ContextRecall

        with contextlib.redirect_stdout(io.StringIO()):
            llm, _ = evaluation.create_evaluator()
        self.assertEqual(type(llm).__name__, "LiteLLMStructuredLLM")
        self.assertEqual(type(llm.client).__name__, "AsyncInstructor")
        self.assertTrue(llm.is_async)
        for metric_class in (Faithfulness, ContextPrecision, ContextRecall):
            metric = metric_class(llm=llm)
            self.assertIs(metric.llm, llm)
            self.assertTrue(metric.llm.is_async)

    def test_metric_failure_continues_cases_and_closes_runner(self):
        from ragas.metrics import collections

        llm = SimpleNamespace(is_async=True, agenerate=AsyncMock())
        faith = SimpleNamespace(llm=llm, ascore=AsyncMock(side_effect=RuntimeError("API rate limit")))
        precision = SimpleNamespace(llm=llm, ascore=AsyncMock(return_value=SimpleNamespace(value=float("nan"))))
        recall = SimpleNamespace(llm=llm, ascore=AsyncMock(return_value=SimpleNamespace(value=1.0)))
        harness = SimpleNamespace(
            close_runner=AsyncMock(),
            run_companyai_case=AsyncMock(return_value={
                "route": "policy_agent", "tools_called": [],
                "retrieval_context": ["policy"], "actual_output": "answer",
            }),
        )
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            root = Path(directory)
            (root / "evaluations/datasets").mkdir(parents=True)
            (root / "evaluations/datasets/rag_cases.json").write_text(json.dumps([
                {"id": str(i), "question": "question", "reference": "reference"} for i in range(2)
            ]), encoding="utf-8")
            output = root / "evaluations/results/ragas_eval_latest.json"
            output.parent.mkdir()
            output.write_text('{"previous": true}', encoding="utf-8")
            stack.enter_context(patch.object(evaluation, "ROOT", root))
            stack.enter_context(patch.object(evaluation, "create_evaluator", return_value=(llm, "test")))
            stack.enter_context(patch.object(evaluation, "prepare_isolated_runtime", return_value={"database": root / "test.db"}))
            stack.enter_context(patch.dict("sys.modules", {"evaluations.adk_harness": harness}))
            for name, metric in (("Faithfulness", faith), ("ContextPrecision", precision), ("ContextRecall", recall)):
                stack.enter_context(patch.object(collections, name, return_value=metric))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            code = asyncio.run(evaluation._run(SimpleNamespace(verify_evaluator=False, limit=None, delay=0, output=output)))
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(code, 1)
            self.assertEqual(report["cases_run"], 2)
            self.assertEqual(report["failed"], 2)
            self.assertEqual(report["completed"], 0)
            self.assertTrue(all(score is None for score in report["average_scores"].values()))
            for row in report["results"]:
                self.assertEqual(row["status"], "error")
                self.assertIsNone(row["faithfulness"])
                self.assertIsNone(row["context_precision"])
                self.assertEqual(row["context_recall"], 1.0)
                self.assertEqual(set(row["metric_errors"]), {"faithfulness", "context_precision"})
            harness.close_runner.assert_awaited_once()
            self.assertEqual(recall.ascore.await_count, 2)
            self.assertEqual(len(list(output.parent.glob("ragas_eval_previous_*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
