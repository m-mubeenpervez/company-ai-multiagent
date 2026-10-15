from __future__ import annotations

import hashlib
import hmac
import os

ITERATIONS = 200_000

def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )
    return salt.hex(), digest.hex()

def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )
    return hmac.compare_digest(digest.hex(), hash_hex)
