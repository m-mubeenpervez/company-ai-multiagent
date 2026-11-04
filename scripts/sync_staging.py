"""Transfer the sole working source into the existing private staging snapshot.

Never updates active databases, Qdrant, private configuration or environments.
Existing staged files are backed up before replacement; no files are removed.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / ".release_candidate/CompanyAI"
EXCLUDED = {".release_backups", ".release_candidate", ".evaluation_runtime", ".git", ".adk", ".deepeval",
            "__pycache__", ".pytest_cache", ".mypy_cache", "qdrant_storage"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync():
    assert ROOT.name in {"company_ai_multiagent_gemini_llm_mcp_eval_security_final", "companyai-secure-multi-agent-platform"}
    if not STAGE.is_dir() or STAGE.is_symlink() or STAGE.is_junction():
        raise RuntimeError("Expected private staging directory is missing or a link.")
    initial = json.loads((ROOT / "evaluations/results/remediation_initial_integrity.json").read_text())
    base = json.loads((Path(initial["backup"]) / "manifest.json").read_text())
    previous_path = ROOT / "evaluations/results/remediation_stage_sync.json"
    previous = json.loads(previous_path.read_text()).get("copied_sha256", {}) if previous_path.exists() else {}
    candidates = []
    for directory, dirs, names in os.walk(ROOT):
        dirs[:] = [name for name in dirs if name not in EXCLUDED and not name.startswith(".venv")]
        for name in names:
            source = Path(directory) / name
            if name in {".env", ".release_backup_location"} or source.suffix in {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo"}:
                continue
            if source.is_symlink() or source.is_junction():
                raise RuntimeError("Review filesystem link before syncing.")
            relative = str(source.relative_to(ROOT))
            destination = STAGE / relative
            if not destination.resolve().is_relative_to(STAGE.resolve()):
                raise RuntimeError("Staging destination escapes the expected snapshot.")
            if destination.is_symlink() or destination.is_junction():
                raise RuntimeError("Staging destination is a link.")
            if destination.exists() and source.suffix in {".py", ".ps1"}:
                expected = previous.get(relative) or base.get(relative, {}).get("sha256")
                if expected and digest(destination) != expected:
                    raise RuntimeError("Independent staged source change requires review: " + relative)
            candidates.append((source, destination, relative))
    backup = ROOT / ".release_backups" / ("stage_sync_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    copied, changed = {}, []
    for source, destination, relative in candidates:
        expected = digest(source)
        if not destination.exists() or digest(destination) != expected:
            if destination.exists():
                saved = backup / relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, saved)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            changed.append(relative)
        if digest(destination) != expected:
            raise RuntimeError("Copied hash mismatch: " + relative)
        copied[relative] = expected
    # Respect the already observed provider deadline in the independent snapshot.
    circuit = ROOT / ".evaluation_runtime/gemini_quota_circuit.json"
    if circuit.exists():
        target = STAGE / ".evaluation_runtime/gemini_quota_circuit.json"
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(circuit, target)
    result = {"created_at": datetime.now(timezone.utc).isoformat(), "source": str(ROOT), "stage": str(STAGE),
              "status": "PASS", "backup": str(backup), "changed": changed, "copied_sha256": copied,
              "deleted": [], "data_configuration_and_environments_copied": False,
              "final_directory_created": False}
    previous_path.write_text(json.dumps(result, indent=2))
    print(json.dumps({key: result[key] for key in ("status", "source", "stage", "backup", "deleted")}))
    print("Verified source/evidence files:", len(copied), "; changed:", len(changed))


if __name__ == "__main__":
    sync()
