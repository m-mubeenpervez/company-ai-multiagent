from __future__ import annotations

import unittest
from evaluations.run_deepeval_eval import _measure


class Judge:
    def __init__(self, score, passed=True):
        self.score, self.passed = score, passed
        self.reason = "test judge"

    async def a_measure(self, case, _show_indicator=False):
        return self.score

    def is_successful(self):
        return self.passed


class DeepEvalIntegrityTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_or_nonfinite_scores_are_errors(self):
        for value in [None, float("nan"), float("inf"), -0.1, 1.1]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                await _measure(Judge(value), None)

    async def test_quality_failure_is_retained(self):
        result = await _measure(Judge(0.2, passed=False), None)
        self.assertEqual(result["score"], 0.2)
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
