from __future__ import annotations

import os
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DB_PATH = PROJECT_ROOT / ".companyai_runtime" / "company.db"


def resolve_data_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else PROJECT_ROOT / path).resolve()


DB_PATH = resolve_data_path(os.getenv("COMPANYAI_DB_PATH", str(_DEFAULT_DB_PATH)))

def get_connection() -> sqlite3.Connection:
    # Normal runtime must never silently replace missing company data.
    conn = sqlite3.connect(DB_PATH.as_uri() + "?mode=rw", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn

def row_to_dict(row):
    return dict(row) if row is not None else None
