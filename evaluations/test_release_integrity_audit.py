"""Focused offline checks; never invoke the integrity runner or render reports."""
import ast
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

spec_integrity = importlib.util.spec_from_file_location("integrity", ROOT / "scripts/master_integrity.py")
integrity = importlib.util.module_from_spec(spec_integrity)
spec_integrity.loader.exec_module(integrity)
spec_renderer = importlib.util.spec_from_file_location("renderer", ROOT / ".evaluation_runtime/render_master_final.py")


def failure_predicate(stage_database_matches=True, live_errors=None):
    """Evaluate the actual final decision with synthetic, otherwise clean checks."""
    tree = ast.parse((ROOT / "scripts/master_integrity.py").read_text(encoding="utf-8"))
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    assignment = next(node for node in main.body if isinstance(node, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "bad" for t in node.targets))
    values = {key: [] for key in ("rollback_errors", "original_errors", "asset_errors", "stage_errors",
                                  "stage_qdrant_errors", "matches")}
    values.update(live_errors=live_errors or {}, missing_evidence=live_errors or {}, integrity_errors=[],
                  database_check={"integrity_check": "ok", "foreign_key_errors": []},
                  backup_database_check={"integrity_check": "ok", "foreign_key_errors": []},
                  qdrant_checks=[{"finite_vectors_and_source_metadata_valid": True}],
                  report={"final_directory_exists": False, "source_private_configuration_preserved": True,
                          "stage_company_database_matches_source": stage_database_matches})
    return bool(eval(compile(ast.Expression(assignment.value), "<actual-integrity-predicate>", "eval"), values))


class ReleaseIntegrityAuditTests(unittest.TestCase):
    def test_manifest_rejects_empty_traversal_absolute_and_bad_sha(self):
        with self.assertRaises(ValueError):
            integrity.validate_manifest({}, ROOT, label="test")
        with self.assertRaises(ValueError):
            integrity.validate_manifest({"../escape": {"sha256": "0" * 64}}, ROOT, label="test")
        with self.assertRaises(ValueError):
            integrity.validate_manifest({str(ROOT / "absolute.txt"): {"sha256": "0" * 64}}, ROOT, label="test")
        with self.assertRaises(ValueError):
            integrity.validate_manifest({"file.txt": {"sha256": "bad"}}, ROOT, label="test")

    def test_qdrant_probe_rejects_empty_and_inconsistent_counts(self):
        from types import SimpleNamespace
        point = SimpleNamespace(vector=[0.1, 0.2], payload={"source": "x", "page": 1, "text": "policy"})
        self.assertTrue(integrity.validate_qdrant_points([point], 1, 2))
        self.assertFalse(integrity.validate_qdrant_points([], 0, 2))
        self.assertFalse(integrity.validate_qdrant_points([point], 2, 2))

    def test_staged_database_mismatch_prevents_pass(self):
        self.assertTrue(failure_predicate(stage_database_matches=False))

    def test_clean_synthetic_checks_do_not_fail(self):
        self.assertFalse(failure_predicate())

    def test_missing_live_evidence_still_prevents_pass(self):
        self.assertTrue(failure_predicate(live_errors={"missing.json": ["Report not yet available"]}))

    def test_missing_renderer_input_causes_no_output_writes(self):
        path = ROOT / ".evaluation_runtime/render_master_final.py"
        spec = importlib.util.spec_from_file_location("audited_renderer", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(module, "validate_current_evidence", side_effect=FileNotFoundError("dummy missing input")), \
             patch.object(Path, "write_text") as write:
            with self.assertRaises(FileNotFoundError):
                module.main()
            write.assert_not_called()

    def test_renderer_rejects_unknown_gate_and_empty_evidence(self):
        with self.assertRaises(ValueError):
            module = importlib.util.module_from_spec(spec_renderer)
            spec_renderer.loader.exec_module(module)
            module.validate_gate_statuses({"made_up": "PASS"})

    def test_renderer_validates_counts_and_assessment_dispositions(self):
        module = importlib.util.module_from_spec(spec_renderer)
        spec_renderer.loader.exec_module(module)
        report = {"cases_configured": 1, "results": [{"id": "x", "status": "completed"}],
                  "completed": 1, "passed": 1, "failed": 0, "blocked": 0}
        self.assertIs(module.validate_report(report, name="test"), report)
        with self.assertRaises(ValueError):
            module.validate_report({**report, "completed": 0}, name="test")
        with self.assertRaises(ValueError):
            module.validate_assessment([{"decision": "UNKNOWN"}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
