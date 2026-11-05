from __future__ import annotations

import os
import shutil
import re
import tempfile
import sqlite3
from contextlib import closing
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def configured_sources() -> tuple[Path, Path]:
    """Resolve runtime sources before importing modules that cache data paths."""
    def resolve(variable: str, default: str) -> Path:
        value = Path(os.getenv(variable, default)).expanduser()
        return (value if value.is_absolute() else PROJECT_ROOT / value).resolve()

    return (
        resolve("COMPANYAI_DB_PATH", ".companyai_runtime/company.db"),
        resolve("COMPANYAI_QDRANT_PATH", ".companyai_runtime/qdrant"),
    )


def prepare_isolated_runtime(
    name: str,
    *,
    qdrant_collection: str | None = None,
    copy_qdrant: bool = True,
) -> dict[str, Path]:
    """
    Create disposable copies of SQLite and Qdrant data for a test run.

    The environment variables are set before importing CompanyAI modules,
    so both the main process and child MCP STDIO servers use the copies.
    """
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("Runtime name must contain only letters, numbers, underscores or hyphens.")
    runtime_base = PROJECT_ROOT / ".evaluation_runtime"
    runtime_base.mkdir(exist_ok=True)
    runtime_root = Path(tempfile.mkdtemp(prefix=name + "_", dir=runtime_base))

    source_db, source_qdrant = configured_sources()
    if not source_db.exists():
        raise FileNotFoundError(
            f"CompanyAI database not found: {source_db}. "
            "Run the normal project setup first."
        )

    db_copy = runtime_root / "company.db"
    # SQLite's backup API includes committed WAL data in a consistent snapshot.
    with closing(sqlite3.connect(f"{source_db.as_uri()}?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(db_copy)) as destination:
            source.backup(destination)

    qdrant_copy = runtime_root / "qdrant_storage"
    if copy_qdrant and source_qdrant.exists():
        shutil.copytree(source_qdrant, qdrant_copy)
    else:
        qdrant_copy.mkdir(parents=True, exist_ok=True)

    os.environ["COMPANYAI_DB_PATH"] = str(db_copy)
    os.environ["COMPANYAI_QDRANT_PATH"] = str(qdrant_copy)
    os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

    if qdrant_collection:
        os.environ["RAG_COLLECTION"] = qdrant_collection

    return {
        "runtime_root": runtime_root,
        "database": db_copy,
        "qdrant": qdrant_copy,
    }
