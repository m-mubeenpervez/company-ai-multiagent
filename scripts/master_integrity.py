"""Read-only release integrity checks; write evidence only in the working copy."""
from __future__ import annotations

import ast
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import re

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / ".release_candidate/CompanyAI"
EXCLUDED = {".release_backups", ".release_candidate", ".evaluation_runtime", ".git",
            ".adk", ".deepeval", "__pycache__", ".pytest_cache", ".mypy_cache"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
INTEGRITY_METADATA_SCHEMA = "companyai.integrity.v1"
# Policy v1: generated/runtime roots are excluded from exhaustive source-tree
# inventory; all other files under the attested root are inventory candidates.
GENERATED_ROOTS = {".evaluation_runtime", ".release_backups", ".release_candidate",
                   ".venv", ".venv-eval", "__pycache__", ".pytest_cache", ".mypy_cache"}


def validate_initial_integrity_metadata(metadata: object) -> None:
    """Validate the approved v1 metadata contract before consuming paths."""
    if not isinstance(metadata, dict):
        raise ValueError("initial integrity metadata must be an object")
    required = {"schema", "timestamp", "root", "backup", "files"}
    if not required.issubset(metadata):
        raise ValueError("initial integrity metadata is missing required fields")
    if metadata["schema"] != INTEGRITY_METADATA_SCHEMA:
        raise ValueError("unsupported initial integrity metadata schema")
    if not isinstance(metadata["timestamp"], str) or not metadata["timestamp"]:
        raise ValueError("initial integrity timestamp must be nonempty")
    if not isinstance(metadata["root"], str) or not isinstance(metadata["backup"], str):
        raise ValueError("initial integrity roots must be strings")
    if not isinstance(metadata["files"], int) or metadata["files"] <= 0:
        raise ValueError("initial integrity files must be a positive integer")


def inventory_unexpected(root: Path, expected: set[str], *, excluded_roots=GENERATED_ROOTS) -> list[str]:
    """Return non-generated files absent from the approved expected inventory."""
    root = root.resolve()
    unexpected = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        rel_dir = Path(directory).relative_to(root)
        if Path(directory).is_symlink() or Path(directory).is_junction():
            raise RuntimeError("review filesystem link before integrity inventory")
        if any((Path(directory) / name).is_symlink() or (Path(directory) / name).is_junction()
               for name in names):
            raise RuntimeError("review filesystem link before integrity inventory")
        dirs[:] = [d for d in dirs
                   if (rel_dir / d).parts[0] not in excluded_roots]
        if any((Path(directory) / d).is_symlink() or (Path(directory) / d).is_junction()
               for d in dirs):
            raise RuntimeError("review filesystem link before integrity inventory")
        for name in names:
            rel = str((rel_dir / name) if rel_dir != Path(".") else Path(name))
            if rel not in expected:
                unexpected.append(rel)
    return sorted(unexpected)


def validate_manifest(manifest, root: Path, *, label: str) -> list[str]:
    """Validate the established {relative path: {sha256: hex}} manifest contract."""
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError(f"{label} manifest must be a nonempty object")
    errors = []
    root = root.resolve()
    for name, row in manifest.items():
        if not isinstance(name, str) or not name or Path(name).is_absolute():
            raise ValueError(f"{label} manifest contains an absolute/invalid path")
        parts = Path(name).parts
        if ".." in parts:
            raise ValueError(f"{label} manifest contains traversal path: {name}")
        if not isinstance(row, dict) or set(row) != {"sha256"} or not isinstance(row["sha256"], str) or not SHA256_RE.fullmatch(row["sha256"]):
            raise ValueError(f"{label} manifest has invalid SHA-256 entry: {name}")
        candidate = (root / Path(name)).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError(f"{label} manifest path escapes its root: {name}")
        cursor = root
        for part in Path(name).parts[:-1]:
            cursor = cursor / part
            if cursor.is_symlink() or cursor.is_junction():
                raise ValueError(f"{label} manifest traverses a directory link: {name}")
        if candidate.exists() and (candidate.is_symlink() or candidate.is_junction()):
            raise ValueError(f"{label} manifest points to a link: {name}")
    return errors


def validate_qdrant_points(points, expected_count: int, dimension: int) -> bool:
    if expected_count <= 0 or not points or len(points) != expected_count:
        return False
    return all(isinstance(p.vector, list) and len(p.vector) == dimension
               and all(math.isfinite(value) for value in p.vector)
               and isinstance(p.payload, dict)
               and isinstance(p.payload.get("source"), str) and p.payload.get("source")
               and isinstance(p.payload.get("page"), int) and p.payload["page"] > 0
               and isinstance(p.payload.get("text"), str) and p.payload.get("text") for p in points)


def owned_files():
    for directory, dirs, names in os.walk(ROOT):
        dirs[:] = [name for name in dirs if name not in EXCLUDED and not name.startswith(".venv")]
        for name in names:
            path = Path(directory) / name
            if path.is_symlink() or path.is_junction():
                raise RuntimeError("Review filesystem link before integrity traversal.")
            yield path


def resolve_backup_directory(metadata: dict, root: Path = ROOT) -> Path:
    """Relocate an in-project backup without changing its selected identity.

    Preserve historical metadata and external absolute backups. Relative paths
    are project-relative. Never search for a replacement if a backup is absent.
    """
    backup = Path(metadata["backup"])
    recorded_root = Path(metadata["root"])
    if ".." in backup.parts:
        raise ValueError("backup path contains traversal")
    if backup.is_absolute():
        if recorded_root.is_absolute() and backup.is_relative_to(recorded_root):
            return root / backup.relative_to(recorded_root)
        return backup
    if backup.drive or backup.root:
        raise ValueError("backup path must be absolute or project-relative")
    return root / backup


def load_validated_backup(metadata: dict, root: Path = ROOT) -> tuple[Path, Path, dict]:
    """Resolve the selected backup and validate roots and manifest before use."""
    validate_initial_integrity_metadata(metadata)
    root = Path(root)
    if not root.is_dir() or root.is_symlink() or root.is_junction():
        raise ValueError("project root must be an existing non-link directory")
    root = root.resolve()
    backup = resolve_backup_directory(metadata, root)
    project = backup / "project"
    manifest_path = backup / "manifest.json"
    if backup.is_relative_to(root):
        cursor = root
        for part in backup.relative_to(root).parts:
            cursor = cursor / part
            if cursor.is_symlink() or cursor.is_junction():
                raise ValueError("backup path traverses a filesystem link")
    for path, label in ((backup, "backup"), (project, "backup project")):
        if not path.is_dir() or path.is_symlink() or path.is_junction():
            raise ValueError(f"{label} root must be an existing non-link directory")
    if not manifest_path.is_file() or manifest_path.is_symlink() or manifest_path.is_junction():
        raise ValueError("backup manifest must be an existing non-link file")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, project, label="rollback")
    return backup, project, manifest


def main():
    assert ROOT.name in {"company_ai_multiagent_gemini_llm_mcp_eval_security_final", "companyai-secure-multi-agent-platform"}
    output = ROOT / "evaluations/results"
    initial = json.loads((output / "current_initial_integrity.json").read_text(encoding="utf-8"))
    backup, backup_project, manifest = load_validated_backup(initial, ROOT)
    rollback_unexpected = inventory_unexpected(backup_project, set(manifest))
    if rollback_unexpected:
        raise RuntimeError("rollback inventory contains unexpected files: " + ", ".join(rollback_unexpected[:10]))
    rollback_errors = [name for name, row in manifest.items()
                       if not (backup_project / name).is_file()
                       or digest(backup_project / name) != row["sha256"]]
    original = Path(r"D:\company_ai_multiagent_gemini_llm_mcp_final")
    original_manifest = json.loads((ROOT / ".release_backups/20261103_213826/original_manifest.json")
                                   .read_text(encoding="utf-8"))
    validate_manifest(original_manifest, original, label="protected-original")
    original_unexpected = inventory_unexpected(original, set(original_manifest))
    if original_unexpected:
        raise RuntimeError("protected-original inventory contains unexpected files: " + ", ".join(original_unexpected[:10]))
    original_errors = [name for name, row in original_manifest.items()
                       if not (original / name).is_file() or digest(original / name) != row["sha256"]]
    protected = [name for name in manifest if name.endswith((".db", ".pdf"))
                 or "qdrant_storage" in name or "datasets" in name
                 or name.endswith(("ragas_eval_latest.json", "ragas_eval_improved.json"))]
    asset_errors = [name for name in protected if not (ROOT / name).is_file()
                    or digest(ROOT / name) != manifest[name]["sha256"]]
    qdrant_files = [name for name in manifest if name.startswith("company_system\\qdrant_storage\\")
                   and not name.endswith(".lock")]
    stage_qdrant_errors = [name for name in qdrant_files if not (STAGE / name).is_file()
                           or digest(STAGE / name) != manifest[name]["sha256"]]
    paths = list(owned_files())
    sources = [p for p in paths if p.suffix in {".py", ".ps1", ".md"}]
    stage_errors = [str(p.relative_to(ROOT)) for p in sources
                    if not (STAGE / p.relative_to(ROOT)).is_file()
                    or digest(STAGE / p.relative_to(ROOT)) != digest(p)]
    modules = [p for p in paths if p.suffix == ".py"]
    for path in modules:
        source = path.read_text(encoding="utf-8-sig")
        ast.parse(source, filename=str(path))
        compile(source, str(path), "exec")
    database = ROOT / "company_system/database/company.db"
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as conn:
        database_check = {"integrity_check": conn.execute("PRAGMA integrity_check").fetchone()[0],
                          "foreign_key_errors": conn.execute("PRAGMA foreign_key_check").fetchall(),
                          "employees": conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]}
    backup_database = backup / "project/company_system/database/company.db"
    with closing(sqlite3.connect(backup_database.as_uri() + "?immutable=1", uri=True)) as conn:
        backup_database_check = {"integrity_check": conn.execute("PRAGMA integrity_check").fetchone()[0],
                                 "foreign_key_errors": conn.execute("PRAGMA foreign_key_check").fetchall()}
    # Probe a disposable index, never open the active Qdrant store for mutation.
    from qdrant_client import QdrantClient
    probe_root = Path(tempfile.mkdtemp(prefix="master_integrity_qdrant_", dir=ROOT / ".evaluation_runtime"))
    shutil.copytree(ROOT / "company_system/qdrant_storage", probe_root / "index")
    qdrant_checks = []
    with closing(QdrantClient(path=str(probe_root / "index"))) as client:
        for collection in client.get_collections().collections:
            info = client.get_collection(collection.name)
            dimension = info.config.params.vectors.size
            points, offset = client.scroll(collection.name, limit=1000, with_vectors=True, with_payload=True)
            if offset is not None:
                raise RuntimeError("Index exceeds this bounded structural probe; review pagination.")
            valid = validate_qdrant_points(points, info.points_count, dimension)
            qdrant_checks.append({"collection": collection.name, "points": info.points_count,
                                  "vectors_checked": len(points), "dimension": dimension,
                                  "distance": info.config.params.vectors.distance.value,
                                  "finite_vectors_and_source_metadata_valid": bool(valid),
                                  "duplicate_passages": len(points) - len({(p.payload.get("source"), p.payload.get("page"),
                                                                           p.payload.get("text")) for p in points})})
    live_errors = {}
    missing_evidence = {}
    integrity_errors = []
    report_paths = [output / name for name in ("ragas_eval_master_final.json", "deepeval_eval_master_final.json",
                    "routing_eval_master_final.json", "agent_acceptance_master_final.json")]
    report_paths.append(ROOT / "security/reports/prompt_injection_master_final.json")
    for path in report_paths:
        name = str(path.relative_to(ROOT))
        if not path.exists():
            missing_evidence[name] = ["Report not yet available"]
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        wrong = [name for name, sha in report["provenance"]["source_sha256"].items()
                 if not (ROOT / name).is_file() or digest(ROOT / name) != sha]
        if wrong:
            integrity_errors.append({"report": name, "source_mismatches": wrong})
    private_values = set()
    for env in (ROOT / ".env", STAGE / ".env"):
        for line in env.read_text(encoding="utf-8-sig").splitlines():
            key, _, value = line.partition("=")
            if key.strip() in {"GEMINI_API_KEY", "GOOGLE_API_KEY"}:
                value = value.strip().strip("\"'")
                if len(value) > 10:
                    private_values.add(value)
    matches = []
    for path in paths:
        if path.suffix not in {".py", ".ps1", ".md", ".json", ".txt", ".log"}:
            continue
        content = path.read_bytes()
        if any(value.encode(encoding) in content for value in private_values
               for encoding in ("utf-8", "utf-16-le")):
            matches.append(str(path.relative_to(ROOT)))
    git = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "python": sys.executable,
              "source": str(ROOT), "stage": str(STAGE), "backup": str(backup),
              "rollback_files_verified": len(manifest), "rollback_errors": rollback_errors,
              "protected_original_files_verified": len(original_manifest), "original_errors": original_errors,
              "protected_assets_checked": len(protected), "protected_asset_errors": asset_errors,
              "compiled_modules": len(modules), "stage_code_document_files_checked": len(sources),
              "stage_code_document_differences": stage_errors,
              "stage_private_configuration_matches_source": digest(STAGE / ".env") == digest(ROOT / ".env"),
              "source_private_configuration_preserved": digest(ROOT / ".env") == manifest[".env"]["sha256"],
              "stage_company_database_matches_source": digest(STAGE / "company_system/database/company.db") == digest(database),
              "stage_qdrant_files_checked": len(qdrant_files), "stage_qdrant_errors": stage_qdrant_errors,
              "sqlite": database_check, "rollback_sqlite": backup_database_check,
              "qdrant_structural_probe": qdrant_checks, "qdrant_probe_runtime": str(probe_root),
              "live_report_source_errors": live_errors,
              "missing_evidence": missing_evidence,
              "integrity_errors": integrity_errors,
              "configured_api_key_matches_in_owned_text_artifacts": matches,
              "git_status_exit": git.returncode, "git_status": git.stdout + git.stderr,
              "final_directory_exists": Path(r"D:\CompanyAI").exists(), "final_copy_authorized": False,
              "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources}}
    bad = (rollback_errors or original_errors or asset_errors or stage_errors or stage_qdrant_errors or live_errors
           or missing_evidence or integrity_errors or matches
           or database_check["integrity_check"] != "ok" or database_check["foreign_key_errors"]
           or backup_database_check["integrity_check"] != "ok" or backup_database_check["foreign_key_errors"]
           or not qdrant_checks or any(not row["finite_vectors_and_source_metadata_valid"] for row in qdrant_checks)
           or report["final_directory_exists"] or not report["source_private_configuration_preserved"]
           or not report["stage_company_database_matches_source"])
    report["status"] = "FAIL" if bad else "PASS_LOCAL_INTEGRITY"
    (output / "master_final_integrity.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "source_sha256"}, indent=2))
    return int(bool(bad))


if __name__ == "__main__":
    raise SystemExit(main())
