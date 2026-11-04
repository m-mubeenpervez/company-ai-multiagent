from __future__ import annotations

import os
import sqlite3
from pathlib import Path

_DEFAULT_DB_PATH = Path(__file__).resolve().parent / "company.db"
DB_PATH = Path(os.getenv("COMPANYAI_DB_PATH", str(_DEFAULT_DB_PATH))).expanduser().resolve()

def get_connection() -> sqlite3.Connection:
    # Normal runtime must never silently replace missing company data.
    conn = sqlite3.connect(DB_PATH.as_uri() + "?mode=rw", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn

def row_to_dict(row):
    return dict(row) if row is not None else None
