"""Focused offline contract tests; writer main functions are never executed."""
import ast
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from evaluations.renderer_contract import write_renderer_output, write_unprotected_output

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "evaluations/results/master_release_decision.json"
WRITERS = (ROOT / ".evaluation_runtime/recovery_audit.py", ROOT / ".evaluation_runtime/render_master_final.py")


class ReleaseDecisionImmutableTests(unittest.TestCase):
    def test_writers_have_no_decision_mutation_or_archive_call(self):
        mutators = {"write_text", "write_bytes", "open", "replace", "rename", "copy", "copy2", "move"}
        for writer in WRITERS:
            tree = ast.parse(writer.read_text(encoding="utf-8"), filename=str(writer))
            violations = []
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if name in mutators and "master_release_decision" in ast.get_source_segment(writer.read_text(encoding="utf-8"), node):
                    violations.append((node.lineno, name))
            self.assertEqual(violations, [], str(writer))

    def test_both_write_boundaries_reject_decision_without_side_effects(self):
        before = hashlib.sha256(DECISION.read_bytes()).hexdigest()
        existing_alternates = set(DECISION.parent.glob(DECISION.stem + "_previous_*" + DECISION.suffix))
        for boundary in (write_renderer_output, write_unprotected_output):
            with patch.object(Path, "write_text") as write:
                with self.assertRaises(PermissionError):
                    boundary(DECISION, "forbidden", root=ROOT)
                write.assert_not_called()
        self.assertEqual(hashlib.sha256(DECISION.read_bytes()).hexdigest(), before)
        self.assertEqual(set(DECISION.parent.glob(DECISION.stem + "_previous_*" + DECISION.suffix)), existing_alternates)

    def test_renderer_boundary_rejects_alternate_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "master_release_decision.json"
            with self.assertRaises(ValueError):
                write_renderer_output(target, "forbidden", root=ROOT)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
