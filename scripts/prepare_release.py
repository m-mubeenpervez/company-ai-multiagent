"""Create a private CompanyAI candidate without overwriting a destination.

The protected original is never a source or destination. Environments are rebuilt,
not copied. All active company data, reports, fixtures and Git history are retained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def configured_path(variable: str, default: str) -> Path:
    """Resolve configured paths relative to the project without guessing targets."""
    value = Path(os.getenv(variable, default)).expanduser()
    return (value if value.is_absolute() else ROOT / value).resolve()


PROTECTED = configured_path("COMPANYAI_PROTECTED_ORIGINAL", ".protected_original")
FINAL = configured_path("COMPANYAI_FINAL_DESTINATION", ".release_output/CompanyAI")
EXCLUDED = {".release_backups", ".release_backup_location", ".release_candidate", ".evaluation_runtime",
            ".deepeval", "__pycache__", ".pytest_cache", ".mypy_cache", ".adk", "venv", "env"}


def copy_candidate(destination: Path, *, allow_blocked: bool = False):
    destination = destination.resolve()
    if destination not in {ROOT / ".release_candidate/CompanyAI", FINAL}:
        raise ValueError(f"Destination must be the isolated candidate or configured final destination: {FINAL}")
    if destination == PROTECTED or destination.is_relative_to(PROTECTED):
        raise ValueError("Protected original cannot be a release destination.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing destination: {destination}")
    if destination == FINAL:
        gates = json.loads((ROOT / "evaluations/results/release_gates.json").read_text(encoding="utf-8"))
        if not all(row["status"] == "PASS" for row in gates["checks"]) and not allow_blocked:
            raise RuntimeError("Release gates are incomplete. Final copying requires explicit approval of a blocked local candidate.")

    def ignore(directory, names):
        for name in names:
            path = Path(directory) / name
            if path.is_symlink() or path.is_junction():
                raise ValueError(f"Review filesystem link before packaging: {path}")
        return {name for name in names if name in EXCLUDED or name.startswith(".venv") or name.endswith((".pyc", ".pyo"))}

    shutil.copytree(ROOT, destination, ignore=ignore)
    manifest = {}
    for path in destination.rglob("*"):
        if path.is_file():
            manifest[str(path.relative_to(destination))] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {"source": str(ROOT), "destination": str(destination), "files": manifest,
              "excluded_names": sorted(EXCLUDED), "private_configuration_included": True,
              "status": "CANDIDATE", "note": "Copy success is not evidence that blocked live acceptance checks passed."}
    (destination / "evaluations/results/release_copy_manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Created private candidate: {destination}; {len(manifest)} files. Rebuild environments before startup.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=ROOT / ".release_candidate/CompanyAI")
    parser.add_argument("--allow-blocked", action="store_true", help="Use only after explicit approval of a local candidate with documented incomplete gates.")
    args = parser.parse_args()
    copy_candidate(args.destination, allow_blocked=args.allow_blocked)
