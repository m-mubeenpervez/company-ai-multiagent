"""Fail-closed evidence and output contract for release reporting."""
from pathlib import Path
import hashlib
import json

DECISION = Path("evaluations/results/master_release_decision.json")
ALLOWED_OUTPUTS = {Path("FINAL_RELEASE_REPORT.md"), Path("evaluations/AGENT_ACCEPTANCE_REPORT.md"), Path("evaluations/SECURITY_TEST_REPORT.md"), Path("evaluations/results/master_test_runs.json")}


def _relative_to_root(path: Path, root: Path) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path is outside the project root: {path}") from exc


def validate_current_evidence(path: Path, *, root: Path, approval: dict):
    """Accept evidence only when an explicit receipt and current sources bind it."""
    root = root.resolve()
    relative = _relative_to_root(path, root)
    if (not isinstance(approval, dict) or not {"label", "evidence", "receipt"}.issubset(approval)
            or set(approval) - {"label", "evidence", "receipt", "receipt_root"}):
        raise ValueError("explicit current-evidence approval is required")
    if Path(approval["evidence"]) != relative:
        raise ValueError("evidence path is not the approved current source")
    receipt_path = root / Path(approval["receipt"])
    if not path.is_file() or not receipt_path.is_file():
        raise ValueError(f"missing evidence or approval receipt: {path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    recorded_report = Path(receipt.get("report", ""))
    if recorded_report.is_absolute():
        recorded_root = Path(approval.get("receipt_root", ""))
        try:
            recorded_report = recorded_report.relative_to(recorded_root)
        except ValueError as exc:
            raise ValueError("absolute receipt report is outside its approved recorded root") from exc
    if (receipt.get("label") != approval["label"] or receipt.get("status") not in {"PASS", "FAIL", "BLOCKED"}
            or recorded_report != relative):
        raise ValueError("receipt does not approve this evidence path")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ValueError(f"invalid evidence: {path}")
    source_hashes = data.get("provenance", {}).get("source_sha256")
    if not isinstance(source_hashes, dict) or not source_hashes:
        raise ValueError("evidence lacks explicit source provenance")
    for name, expected in source_hashes.items():
        source = root / Path(name)
        if (Path(name).is_absolute() or ".." in Path(name).parts or not source.is_file()
                or source.is_symlink() or source.is_junction()
                or hashlib.sha256(source.read_bytes()).hexdigest() != expected):
            raise ValueError(f"evidence source provenance is not current: {name}")
    return data


def assert_decision_immutable(path: Path, *, root: Path):
    if path.resolve() == (root.resolve() / DECISION).resolve():
        raise PermissionError("release decision is immutable")


def validate_output_target(path: Path, *, root: Path = Path(".")):
    assert_decision_immutable(path, root=root)
    rel = _relative_to_root(path, root)
    if rel not in ALLOWED_OUTPUTS:
        raise ValueError(f"renderer output is not allowed: {path}")
    return rel


def write_renderer_output(path: Path, content: str, *, root: Path):
    validate_output_target(path, root=root)
    path.write_text(content, encoding="utf-8")


def write_unprotected_output(path: Path, content: str, *, root: Path):
    assert_decision_immutable(path, root=root)
    path.write_text(content, encoding="utf-8")
