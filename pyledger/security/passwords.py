"""
PyLedger Security - Password hashing (Phase 4)
stdlib-only PBKDF2 (no new dependency for enterprise use).
"""

import hashlib
import hmac
import os


def hash_password(password: str, salt: bytes = None, iterations: int = 210_000) -> str:
    """Hash password -> 'pbkdf2$iterations$salt_hex$hash_hex'."""
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time verification. Never raises; malformed hashes fail closed."""
    try:
        if not isinstance(stored, str):
            return False
        parts = stored.split("$")
        if len(parts) != 4:
            return False
        algo, it, salt_hex, hash_hex = parts
        if algo != "pbkdf2":
            return False
        iterations = int(it)
        if not 10_000 <= iterations <= 10_000_000:
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(),
                                 bytes.fromhex(salt_hex), iterations)
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False
