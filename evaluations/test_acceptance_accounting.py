"""Offline regression for resumed attempt counts and real tool-status requirements."""
import asyncio
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from evaluations import run_agent_acceptance as agents
from security import run_prompt_injection_eval as injection


class AcceptanceAccountingTests(unittest.TestCase):
    def test_resumed_agent_cases_make_no_new_attempts(self):
        cases = json.loads((agents.ROOT / "evaluations/datasets/agent_acceptance_cases.json").read_text(encoding="utf-8"))
        completed = {case["id"]: {"id": case["id"], "status": "completed", "passed": True, "attempted": True}
                     for case in cases}
        self._assert_resumed(agents, completed, agents.run)

    def test_resumed_injection_cases_make_no_new_attempts(self):
        completed = {name: {"id": name, "status": "completed", "passed": True, "attempted": True}
                     for name in ("direct_prompt_injection_payroll", "indirect_prompt_injection_in_rag_document",
                                  "malicious_mcp_tool_output")}
        self._assert_resumed(injection, completed, injection._main)

    def _assert_resumed(self, module, completed, run):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ), \
             patch("evaluations.checkpointing.CaseCheckpoint", return_value=SimpleNamespace(completed=completed, save=Mock())), \
             patch("evaluations.adk_harness.run_companyai_case", new_callable=AsyncMock) as invoke, \
             patch("evaluations.adk_harness.close_runner", new_callable=AsyncMock):
            # Agent runner imports its checkpoint at module scope.
            checkpoint = SimpleNamespace(completed=completed, save=Mock())
            target = "evaluations.run_agent_acceptance.CaseCheckpoint"
            with patch(target, return_value=checkpoint):
                output = Path(directory) / "report.json"
                code = asyncio.run(run(SimpleNamespace(output=output, resume=True, delay=0)))
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(code, 0)
            self.assertEqual(report["cases_run"], 0)
            self.assertEqual(report["resumed"], len(completed))
            invoke.assert_not_called()

    def test_agent_auth_required_tool_response_cannot_pass_positive_case(self):
        case = json.loads((agents.ROOT / "evaluations/datasets/agent_acceptance_cases.json").read_text(encoding="utf-8"))[0]
        original_read = Path.read_text

        def read(path, *args, **kwargs):
            if path == agents.ROOT / "evaluations/datasets/agent_acceptance_cases.json":
                return json.dumps([case])
            return original_read(path, *args, **kwargs)

        actual = {"route": case["expected_route"], "actual_output": "Session invalid", "tools_called": [
            {"name": name} for name in case["expected_tools"]], "tool_results": [
            {"name": name, "status": "auth_required"} for name in case["expected_tools"]]}
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ), patch.object(Path, "read_text", read), \
             patch.object(agents, "CaseCheckpoint", return_value=SimpleNamespace(completed={}, save=Mock())), \
             patch("evaluations.adk_harness.run_companyai_case", AsyncMock(return_value=actual)), \
             patch("evaluations.adk_harness.close_runner", AsyncMock()):
            output = Path(directory) / "report.json"
            self.assertEqual(asyncio.run(agents.run(SimpleNamespace(output=output, resume=False, delay=0))), 1)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["passed"], 0)
            self.assertEqual(report["failed"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
