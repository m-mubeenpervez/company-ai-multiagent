"""Fresh-process checks catch package initialization before disposable paths."""
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RuntimeIsolationTests(unittest.TestCase):
    def test_runners_capture_disposable_mcp_environment(self):
        for module in ("run_ragas_eval", "run_deepeval_eval"):
            with self.subTest(module=module):
                script = r"""
import asyncio, os
from types import SimpleNamespace
from unittest.mock import patch
from evaluations import MODULE as runner
class Verified(Exception): pass
def checkpoint(*args, **kwargs):
    from company_system.agent import root_agent
    from company_system.database.db import DB_PATH
    assert str(DB_PATH) == os.environ['COMPANYAI_DB_PATH']
    assert '.evaluation_runtime' in str(DB_PATH)
    for agent in root_agent.sub_agents:
        for toolset in agent.tools:
            env = toolset.connection_params.server_params.env
            assert env['COMPANYAI_DB_PATH'] == str(DB_PATH), agent.name
            assert env['COMPANYAI_QDRANT_PATH'] == os.environ['COMPANYAI_QDRANT_PATH'], agent.name
    raise Verified()
args=SimpleNamespace(verify_evaluator=False, full=True, limit=None, delay=0, resume=False, output=None, judge_arguments=False)
with patch('evaluations.checkpointing.CaseCheckpoint', side_effect=checkpoint):
    try: asyncio.run(runner._run(args))
    except Verified: print('PASS: all 18 MCP child environments use disposable data')
    else: raise AssertionError('Checkpoint verification did not execute')
""".replace("MODULE", module)
                result = subprocess.run([sys.executable, "-c", script], cwd=ROOT, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS: all 18", result.stdout)

if __name__ == "__main__":
    unittest.main(verbosity=2)
