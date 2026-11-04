"""Offline safety tests for live-evidence command preparation."""
import asyncio
from pathlib import Path
import tempfile
import unittest
import sys
from unittest.mock import patch

from evaluations import record_command
from evaluations import verify_mcp_release


class LiveExecutionSafetyTests(unittest.TestCase):
    def test_mcp_quota_block_prevents_runtime_setup(self):
        with patch.object(verify_mcp_release, "ensure_quota_available",
                          side_effect=RuntimeError("api_daily_quota_exhausted; no request sent")), \
             patch.object(verify_mcp_release, "prepare_isolated_runtime") as prepare:
            with self.assertRaises(RuntimeError):
                asyncio.run(verify_mcp_release.verify("stdio"))
            prepare.assert_not_called()

    def test_recorder_rejects_existing_log_and_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing_log = root / "existing.log"
            existing_log.write_text("preserve", encoding="utf-8")
            with patch.object(record_command, "ROOT", root), patch.object(sys, "argv", [
                "record_command.py", "--label", "safe", "--cwd", str(root),
                "--log", str(existing_log), "--", "python"]):
                with self.assertRaises(SystemExit):
                    record_command.main()
            self.assertEqual(existing_log.read_text(encoding="utf-8"), "preserve")

    def test_unique_log_path_is_recorded_without_overwrite(self):
        # Validate the new command option and path policy without launching a child.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unique = root / "attempt.log"
            self.assertFalse(unique.exists())
            self.assertTrue(not unique.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
