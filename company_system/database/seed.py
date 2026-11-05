"""Backward-compatible entry point for the synthetic demo seed."""
from __future__ import annotations

from company_system.database.db import get_connection
from company_system.database.synthetic_demo import SYNTHETIC_USERS, seed_synthetic


DEMO_USERS = SYNTHETIC_USERS


def seed() -> None:
    connection = get_connection()
    try:
        seed_synthetic(connection)
    finally:
        connection.close()
