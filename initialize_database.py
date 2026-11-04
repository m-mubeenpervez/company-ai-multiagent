from __future__ import annotations

import argparse
import sqlite3
from contextlib import closing
from pathlib import Path
from company_system.database.db import get_connection, DB_PATH
from company_system.database.seed import seed

def initialize(reset: bool = False):
    schema_path = Path(__file__).resolve().parent / "company_system/database/schema.sql"
    if DB_PATH.exists() and not reset:
        print(f"Existing SQLite database preserved: {DB_PATH}")
        return
    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Database creation belongs only to this explicitly invoked initializer.
    with closing(sqlite3.connect(DB_PATH)):
        pass
    with closing(get_connection()) as conn:
        schema = schema_path.read_text(encoding="utf-8")
        conn.executescript(schema)
        conn.commit()
    seed()
    print(f"SQLite database initialized: {DB_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    initialize(reset=args.reset)
