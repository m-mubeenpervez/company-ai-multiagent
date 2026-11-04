from __future__ import annotations

import os
import shutil
import re
import tempfile
import sqlite3
from contextlib import closing
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "company_system" / "database" / "company.db"
DEFAULT_QDRANT = PROJECT_ROOT / "company_system" / "qdrant_storage"


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

    if not DEFAULT_DB.exists():
        raise FileNotFoundError(
            f"CompanyAI database not found: {DEFAULT_DB}. "
            "Run the normal project setup first."
        )

    db_copy = runtime_root / "company.db"
    # SQLite's backup API includes committed WAL data in a consistent snapshot.
    with closing(sqlite3.connect(f"{DEFAULT_DB.as_uri()}?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(db_copy)) as destination:
            source.backup(destination)

    qdrant_copy = runtime_root / "qdrant_storage"
    if copy_qdrant and DEFAULT_QDRANT.exists():
        shutil.copytree(DEFAULT_QDRANT, qdrant_copy)
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
