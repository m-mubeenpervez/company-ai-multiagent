"""Explicit local integrity artifact workflows; never rewrites historical reports."""
from __future__ import annotations
import argparse, base64, hashlib, json, os, stat
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "companyai.integrity.v1"
SHA256 = 64
ATTESTATION_SCHEMA = "companyai.component-attestation.v1"
DEFAULT_EXCLUSIONS = (".venv", ".venv-eval", ".evaluation_runtime", ".release_backups", ".release_candidate", "__pycache__", ".pytest_cache", ".mypy_cache")
APPROVED_COMPONENT_ROOTS = ("company_system", "mcp_server", "scripts", "evaluations", "security", "docs")
APPROVED_COMPONENT_FILES = ("README.md", "requirements.txt", "requirements-evaluation.txt", "requirements-runtime-lock.txt", "requirements-evaluation-lock.txt")
CURRENT_COMPONENT_ROOTS = ("company_system", "mcp_client", "mcp_server", "scripts", "evaluations", "security", "docs", "tests")
CURRENT_COMPONENT_FILES = (".env.example", ".gitattributes", ".gitignore", "README.md",
    "requirements.txt", "requirements-bootstrap.txt", "requirements-evaluation.txt",
    "requirements-evaluation-lock.txt", "requirements-runtime-lock.txt", "ingest_documents.py",
    "initialize_database.py", "verify_gemini.py", "run_evaluations.ps1", "run_tests.ps1",
    "setup_evaluation.ps1", "setup_windows.ps1", "start_project.ps1")
CURRENT_EXCLUDED_SUBTREES = ("company_system/.adk", "company_system/database",
    "company_system/qdrant_storage", "evaluations/provenance", "evaluations/results",
    "security/reports", "docs/archive")

def _root(path: str) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_dir() or p.is_symlink():
        raise ValueError(f"invalid root: {path}")
    return p

def validate_manifest(manifest: object) -> dict:
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("manifest must be a nonempty object")
    for name, row in manifest.items():
        p = Path(name)
        if not isinstance(name, str) or p.is_absolute() or ".." in p.parts:
            raise ValueError(f"invalid manifest path: {name}")
        if not isinstance(row, dict) or set(row) != {"sha256"} or not isinstance(row["sha256"], str) or len(row["sha256"]) != SHA256:
            raise ValueError(f"invalid manifest entry: {name}")
    return manifest

def produce_metadata(manifest_path: Path, output: Path, root: str, backup: str) -> dict:
    manifest = validate_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
    source, backup_root = _root(root), _root(backup)
    for name in manifest:
        if not (backup_root / name).is_file() or (backup_root / name).is_symlink():
            raise ValueError(f"manifest path missing or linked in backup: {name}")
    data = {"schema": SCHEMA, "timestamp": datetime.now(timezone.utc).isoformat(),
            "root": str(source), "backup": str(backup_root), "files": len(manifest),
            "manifest": str(manifest_path.resolve())}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data

def _canonical(path: Path) -> bytes:
    return path.read_bytes()

def generate_keypair(private_path: Path, public_path: Path) -> None:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    private = Ed25519PrivateKey.generate(); public = private.public_key()
    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(private.private_bytes_raw()); public_path.write_bytes(public.public_bytes_raw())
    try: os.chmod(private_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError: pass

def sign(manifest_path: Path, private_path: Path, signature_path: Path, key_id: str) -> None:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    key = Ed25519PrivateKey.from_private_bytes(private_path.read_bytes())
    payload = {"schema": SCHEMA, "key_id": key_id, "signature": base64.b64encode(key.sign(_canonical(manifest_path))).decode("ascii")}
    signature_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def verify(manifest_path: Path, public_path: Path, signature_path: Path, key_id: str) -> None:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    data = json.loads(signature_path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA or data.get("key_id") != key_id:
        raise ValueError("signature trust metadata mismatch")
    Ed25519PublicKey.from_public_bytes(public_path.read_bytes()).verify(base64.b64decode(data["signature"], validate=True), _canonical(manifest_path))

def component_attestation(root: str, output: Path, exclusions=DEFAULT_EXCLUSIONS) -> dict:
    base = _root(root); rows=[]; excluded=[]
    for directory, dirs, files in os.walk(base, followlinks=False):
        rel_dir=Path(directory).relative_to(base)
        dirs[:] = [d for d in dirs if (rel_dir / d).parts[0] not in exclusions]
        if any((Path(directory)/d).is_symlink() for d in dirs) or any((Path(directory)/f).is_symlink() for f in files):
            raise ValueError("links are not permitted in component attestation")
        for name in files:
            rel = Path(name) if rel_dir == Path('.') else rel_dir / name
            if rel.parts[0] in exclusions: continue
            category = "private-config" if name == ".env" else ("runtime-data" if rel.parts[0] in {"company_system"} and any(x in rel.parts for x in ("qdrant_storage","documents","database")) else "source")
            rows.append({"path": str(rel), "category": category, "sha256": hashlib.sha256((base/rel).read_bytes()).hexdigest()})
    data={"schema":ATTESTATION_SCHEMA,"root":str(base),"exclusions":list(exclusions),"components":rows}
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(data,indent=2),encoding='utf-8'); return data

def bounded_component_attestation(root: str, output: Path) -> dict:
    base = _root(root); rows=[]; missing=[]
    for rel_root in APPROVED_COMPONENT_ROOTS:
        candidate=base/rel_root
        if not candidate.is_dir(): missing.append(rel_root); continue
        for directory, dirs, files in os.walk(candidate, followlinks=False):
            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUSIONS]
            if any((Path(directory)/d).is_symlink() for d in dirs) or any((Path(directory)/f).is_symlink() for f in files): raise ValueError(f"unsafe link in approved root: {rel_root}")
            for name in files:
                path=Path(directory)/name; rel=path.relative_to(base)
                category="private-config" if name=='.env' else ("data" if any(x in rel.parts for x in ('database','qdrant_storage','documents')) else "source")
                rows.append({"path":str(rel),"category":category,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    for name in APPROVED_COMPONENT_FILES:
        path=base/name
        if not path.is_file(): missing.append(name); continue
        rows.append({"path":name,"category":"public-config","sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    if missing: raise ValueError("approved roots/files missing: " + ', '.join(missing))
    data={"schema":ATTESTATION_SCHEMA,"root":str(base),"included_roots":list(APPROVED_COMPONENT_ROOTS),"included_files":list(APPROVED_COMPONENT_FILES),"exclusions":list(DEFAULT_EXCLUSIONS),"components":rows}
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(data,indent=2),encoding='utf-8'); return data

def _current_component_rows(base: Path) -> list[dict]:
    excluded = {Path(name) for name in CURRENT_EXCLUDED_SUBTREES}
    rows=[]; missing=[]
    for rel_root in CURRENT_COMPONENT_ROOTS:
        candidate=base/rel_root
        if not candidate.is_dir(): missing.append(rel_root); continue
        for directory, dirs, files in os.walk(candidate, followlinks=False):
            directory=Path(directory); rel_dir=directory.relative_to(base)
            dirs[:] = sorted(d for d in dirs if d not in DEFAULT_EXCLUSIONS and not any((rel_dir/d).is_relative_to(x) for x in excluded))
            if any((directory/d).is_symlink() or (directory/d).is_junction() for d in dirs): raise ValueError(f"unsafe directory link in current component root: {rel_dir}")
            for name in sorted(files):
                path=directory/name; rel=path.relative_to(base)
                if path.is_symlink() or path.is_junction(): raise ValueError(f"unsafe file link in current component root: {rel}")
                if path.suffix == '.sig' or any(rel.is_relative_to(x) for x in excluded): continue
                rows.append({"path":str(rel),"category":"source","sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    for name in CURRENT_COMPONENT_FILES:
        path=base/name
        if not path.is_file(): missing.append(name); continue
        if path.is_symlink() or path.is_junction(): raise ValueError(f"unsafe current component file link: {name}")
        rows.append({"path":name,"category":"public-config","sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    if missing: raise ValueError("current component roots/files missing: " + ', '.join(missing))
    return sorted(rows,key=lambda row:row['path'])

def current_component_attestation(root: str, output: Path) -> dict:
    base=_root(root)
    data={"schema":ATTESTATION_SCHEMA,"scope":"current-source-and-public-config",
          "root":str(base),"included_roots":list(CURRENT_COMPONENT_ROOTS),
          "included_files":list(CURRENT_COMPONENT_FILES),"excluded_subtrees":list(CURRENT_EXCLUDED_SUBTREES),
          "excluded_file_suffixes":[".sig"],"components":_current_component_rows(base)}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2),encoding='utf-8')
    return data

def verify_current_component_attestation(root: str, attestation: Path) -> None:
    base=_root(root); data=json.loads(attestation.read_text(encoding='utf-8'))
    expected={"schema":ATTESTATION_SCHEMA,"scope":"current-source-and-public-config",
              "root":str(base),"included_roots":list(CURRENT_COMPONENT_ROOTS),
              "included_files":list(CURRENT_COMPONENT_FILES),"excluded_subtrees":list(CURRENT_EXCLUDED_SUBTREES),
              "excluded_file_suffixes":[".sig"],"components":_current_component_rows(base)}
    if data != expected: raise ValueError("current component attestation does not match current inventory")

def produce_current_integrity_record(root: str, output: Path, *, historical_metadata: Path,
                                     backup_manifest: Path, attestation: Path, signature: Path) -> dict:
    base=_root(root); historical=json.loads(historical_metadata.read_text(encoding='utf-8'))
    data={"schema":"companyai.current-integrity.v1","root":str(base),
          "historical_metadata":{"path":str(historical_metadata.relative_to(base)),
              "sha256":hashlib.sha256(historical_metadata.read_bytes()).hexdigest(),
              "schema_present":isinstance(historical,dict) and "schema" in historical,
              "limitation":"Historical metadata predates the versioned schema and is preserved byte-for-byte."},
          "selected_backup":{"identity":backup_manifest.parent.name,"manifest":str(backup_manifest.relative_to(base)),
              "manifest_sha256":hashlib.sha256(backup_manifest.read_bytes()).hexdigest()},
          "current_attestation":{"path":str(attestation.relative_to(base)),"sha256":hashlib.sha256(attestation.read_bytes()).hexdigest(),
              "signature":str(signature.relative_to(base)),"signature_sha256":hashlib.sha256(signature.read_bytes()).hexdigest()}}
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(data,indent=2),encoding='utf-8'); return data

def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="op", required=True)
    m = sub.add_parser("metadata"); m.add_argument("--manifest", type=Path, required=True); m.add_argument("--output", type=Path, required=True); m.add_argument("--root", required=True); m.add_argument("--backup", required=True)
    k = sub.add_parser("keygen"); k.add_argument("--private", type=Path, required=True); k.add_argument("--public", type=Path, required=True)
    s = sub.add_parser("sign"); s.add_argument("--manifest", type=Path, required=True); s.add_argument("--private", type=Path, required=True); s.add_argument("--signature", type=Path, required=True); s.add_argument("--key-id", required=True)
    v = sub.add_parser("verify"); v.add_argument("--manifest", type=Path, required=True); v.add_argument("--public", type=Path, required=True); v.add_argument("--signature", type=Path, required=True); v.add_argument("--key-id", required=True)
    a = p.parse_args()
    if a.op == "metadata": produce_metadata(a.manifest, a.output, a.root, a.backup)
    elif a.op == "keygen": generate_keypair(a.private, a.public)
    elif a.op == "sign": sign(a.manifest, a.private, a.signature, a.key_id)
    else: verify(a.manifest, a.public, a.signature, a.key_id)
    return 0
if __name__ == "__main__": raise SystemExit(main())
