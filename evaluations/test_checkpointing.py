from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, AsyncMock
from types import SimpleNamespace

from evaluations.checkpointing import CaseCheckpoint
from company_system.security import quota


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "cases.json"
        self.manifest = {"dataset": "fingerprint", "model": "same", "source": "same"}
        self.cases = [{"id": "a"}, {"id": "b"}]

    def test_resume_retains_completed_failure_and_retries_only_blocked(self):
        checkpoint = CaseCheckpoint(self.path, self.manifest, self.cases)
        rows = [{"id": "a", "status": "completed", "passed": False, "metrics": [{"score": 0.2}]},
                {"id": "b", "status": "blocked", "attempted": False}]
        checkpoint.save(rows)
        resumed = CaseCheckpoint(self.path, self.manifest, self.cases, resume=True)
        self.assertEqual(resumed.completed, {"a": rows[0]})
        self.assertFalse(self.path.with_suffix(".json.tmp").exists())

    def test_stale_provenance_and_duplicate_ids_are_rejected(self):
        checkpoint = CaseCheckpoint(self.path, self.manifest, self.cases)
        checkpoint.save([])
        with self.assertRaises(ValueError):
            CaseCheckpoint(self.path, {**self.manifest, "source": "changed"}, self.cases, resume=True)
        with self.assertRaises(ValueError):
            CaseCheckpoint(self.path, self.manifest, [{"id": "a"}, {"id": "a"}])
        with self.assertRaises(ValueError):
            CaseCheckpoint(self.path, self.manifest, self.cases[:1], resume=True)

    def test_partial_write_requires_review_and_null_never_completes(self):
        checkpoint = CaseCheckpoint(self.path, self.manifest, self.cases)
        checkpoint.save([{"id": "a", "status": "error", "tool_names": ["submit_expense"]}])
        with self.assertRaises(ValueError):
            CaseCheckpoint(self.path, self.manifest, self.cases, resume=True)
        checkpoint.save([{"id": "a", "status": "blocked", "faithfulness": None}])
        self.assertFalse(CaseCheckpoint(self.path, self.manifest, self.cases, resume=True).completed)
        checkpoint.save([{"id": "a", "status": "completed", "faithfulness": None}])
        with self.assertRaises(ValueError):
            CaseCheckpoint(self.path, self.manifest, self.cases, resume=True)

    def test_provider_deadline_is_respected_and_not_extended(self):
        with patch.object(quota, "STATE", self.path), patch.object(quota.time, "time", return_value=1000):
            quota.record_quota(RuntimeError("429 quota requestsPerDay retryDelay: '50989s'"))
            saved = json.loads(self.path.read_text())
            self.assertEqual(saved["retry_after_seconds"], 50989)
            with self.assertRaises(RuntimeError) as caught:
                quota.check_quota()
            quota.record_quota(caught.exception)
            self.assertEqual(saved, json.loads(self.path.read_text()))
        with patch.object(quota, "STATE", self.path), patch.object(quota.time, "time", return_value=53000):
            quota.check_quota()

    def test_router_daily_quota_does_not_fallback_or_retry(self):
        from company_system.routing import semantic_router_agent as router
        with patch.object(quota, "STATE", self.path), \
             patch.object(router, "_classify_with_model", side_effect=RuntimeError("429 quota requestsPerDay retryDelay: '3600s'")) as call:
            with self.assertRaises(RuntimeError):
                router.classify_route("Show my employee profile")
            self.assertEqual(call.call_count, 1)
            with self.assertRaises(RuntimeError):
                router.classify_route("Show my employee profile")
            self.assertEqual(call.call_count, 1)


class JudgeCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_native_structured_async_path_uses_scoped_client(self):
        from evaluations.gemini_judge import QuotaAwareGeminiJudge
        from pydantic import BaseModel
        from unittest.mock import Mock
        class StructuredAnswer(BaseModel):
            answer: str
        expected = StructuredAnswer(answer="offline SDK boundary test")
        generate = AsyncMock(return_value=SimpleNamespace(parsed=expected, usage_metadata=None))
        client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate), aclose=AsyncMock()), close=Mock())
        with patch.object(QuotaAwareGeminiJudge, "_build_client", return_value=client) as build, \
             patch("evaluations.gemini_judge.check_quota"):
            judge = QuotaAwareGeminiJudge(model="gemini-3.5-flash-lite", api_key="dummy-test-key")
            build.assert_not_called()
            result, cost = await judge.a_generate("unchanged test prompt", StructuredAnswer)
            self.assertIs(result, expected)
            build.assert_called_once()
            generate.assert_awaited_once()
            self.assertIs(generate.call_args.kwargs["config"].response_schema, StructuredAnswer)
            client.aio.aclose.assert_awaited_once()
            client.close.assert_called_once()

    async def test_native_generation_is_once_and_clients_close_on_quota(self):
        from evaluations.gemini_judge import QuotaAwareGeminiJudge, GeminiModel
        from unittest.mock import Mock
        client = SimpleNamespace(aio=SimpleNamespace(aclose=AsyncMock()), close=Mock())
        with patch.object(QuotaAwareGeminiJudge, "_build_client", return_value=client) as build, \
             patch("evaluations.gemini_judge.check_quota"), patch("evaluations.gemini_judge.record_quota") as record, \
             patch.object(GeminiModel.a_generate, "__wrapped__", AsyncMock(side_effect=RuntimeError("429 quota"))) as generate:
            judge = QuotaAwareGeminiJudge(model="gemini-3.5-flash-lite", api_key="dummy-test-key")
            build.assert_not_called()
            with self.assertRaises(RuntimeError):
                await judge.a_generate("unchanged judge prompt")
            build.assert_called_once()
            generate.assert_awaited_once()
            record.assert_called_once()
            client.aio.aclose.assert_awaited_once()
            client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
