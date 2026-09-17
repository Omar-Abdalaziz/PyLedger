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
    try:
        algo, it, salt_hex, hash_hex = stored.split("$")
        assert algo == "pbkdf2"
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(),
                                 bytes.fromhex(salt_hex), int(it))
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False
