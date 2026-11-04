"""Connectivity checks must never bypass provider cooldowns."""
import unittest
from unittest.mock import patch
import verify_gemini

class ConnectivitySafetyTests(unittest.TestCase):
    def test_open_circuit_prevents_client_creation(self):
        with patch.object(verify_gemini, "_validate_key"), patch.object(verify_gemini, "check_quota", side_effect=RuntimeError("api_daily_quota_exhausted; no request sent")), patch.object(verify_gemini.genai, "Client") as client:
            with self.assertRaises(SystemExit):
                verify_gemini.main()
            client.assert_not_called()

    def test_provider_failure_is_recorded_once_without_echo(self):
        error = RuntimeError("429 quota dummy-sensitive-detail")
        with patch.object(verify_gemini, "_verify", side_effect=error) as run, patch.object(verify_gemini, "record_quota") as record:
            with self.assertRaises(SystemExit) as caught:
                verify_gemini.main()
            run.assert_called_once()
            record.assert_called_once_with(error)
            self.assertNotIn("dummy-sensitive-detail", str(caught.exception))

if __name__ == "__main__":
    unittest.main(verbosity=2)
