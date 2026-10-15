from __future__ import annotations

import argparse
from pathlib import Path
from company_system.database.db import get_connection, DB_PATH
from company_system.database.seed import seed

def initialize(reset: bool = False):
    schema_path = Path("company_system/database/schema.sql")
    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    conn = get_connection()
    schema = schema_path.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    conn.close()
    seed()
    print(f"SQLite database initialized: {DB_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    initialize(reset=args.reset)
