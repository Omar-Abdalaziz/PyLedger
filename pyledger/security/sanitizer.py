"""
PyLedger Security - Input Sanitizer
Prevents injection attacks across all text/CSV/HTML inputs
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


# ── Pattern Definitions ──────────────────────────────────────────

# CSV Formula Injection: cells starting with =, +, -, @
CSV_FORMULA_PATTERN = re.compile(r'^[\=\+\-\@\t\r]')

# HTML/XML tags (XSS)
HTML_TAG_PATTERN = re.compile(r'<[^>]*>')

# Script injection patterns
SCRIPT_PATTERN = re.compile(
    r'(<script|javascript:|onerror=|onload=|onclick=|onmouseover=|'
    r'alert\(|prompt\(|confirm\()',
    re.IGNORECASE
)

# SQL-like keywords in unexpected places (defense in depth)
SQL_KEYWORD_PATTERN = re.compile(
    r'(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bALTER\b|'
    r'\bEXEC\b|\bUNION\b|\b--\b|\b#\b)',
    re.IGNORECASE
)

# Account code validation pattern (must match config/validators)
ACCOUNT_CODE_PATTERN = re.compile(r'^[A-Z0-9\-]{2,20}$')

# Path traversal patterns
PATH_TRAVERSAL_PATTERN = re.compile(r'\.\.[/\\\\]|~')

# ── Public Sanitizers ────────────────────────────────────────────


def sanitize_text(text: Any, max_length: int = 500) -> str:
    """Sanitize text input: strip HTML, remove script tags, limit length"""
    if not isinstance(text, str):
        text = str(text)
    text = HTML_TAG_PATTERN.sub('', text)
    text = SCRIPT_PATTERN.sub('', text)
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text


def sanitize_description(text: Any, max_length: int = 500) -> str:
    """Sanitize a free-text description field"""
    return sanitize_text(text, max_length)


def sanitize_name(text: Any, max_length: int = 255) -> str:
    """Sanitize account/entity name"""
    text = sanitize_text(text, max_length)
    text = SQL_KEYWORD_PATTERN.sub('', text)
    return text


def sanitize_account_code(code: str) -> str:
    """Validate and sanitize account code — raises ValueError if invalid"""
    if not isinstance(code, str):
        raise ValueError("Account code must be a string")
    code = code.strip().upper()
    if not ACCOUNT_CODE_PATTERN.match(code):
        raise ValueError(
            f"Invalid account code '{code}'. "
            f"Must be 2-20 uppercase alphanumeric characters with hyphens."
        )
    return code


def sanitize_filepath(path: str) -> str:
    """Prevent path traversal attacks"""
    sanitized = PATH_TRAVERSAL_PATTERN.sub('', path)
    # Also block absolute paths on Windows (e.g., C:\)
    sanitized = re.sub(r'^[A-Za-z]:[/\\\\]', '', sanitized)
    return sanitized


def sanitize_csv_field(value: Any) -> str:
    """Prevent CSV formula injection by prefixing with tab"""
    text = str(value)
    if CSV_FORMULA_PATTERN.match(text):
        return "'" + text
    return text


def sanitize_amount(amount: Any, allow_zero: bool = True,
                    allow_negative: bool = False,
                    max_abs: Decimal = Decimal('1_000_000_000_000')) -> Decimal:
    """Validate and sanitize a monetary amount"""
    try:
        val = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid amount: {amount}")

    if not allow_zero and val == 0:
        raise ValueError("Amount cannot be zero")

    if val < 0 and not allow_negative:
        raise ValueError(f"Amount cannot be negative: {val}")

    if abs(val) > max_abs:
        raise ValueError(f"Amount exceeds maximum ({max_abs}): {val}")

    if val.as_tuple().exponent < -4:
        raise ValueError(f"Amount has too many decimal places: {val}")

    return val.quantize(Decimal('0.01'))


def sanitize_quantity(qty: Any, min_qty: int = 0, max_qty: int = 1_000_000) -> Decimal:
    """Validate quantity/value"""
    try:
        val = Decimal(str(qty))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid quantity: {qty}")
    if val < min_qty:
        raise ValueError(f"Quantity below minimum ({min_qty}): {val}")
    if val > max_qty:
        raise ValueError(f"Quantity exceeds maximum ({max_qty}): {val}")
    return val


def sanitize_percentage(pct: Any) -> Decimal:
    """Validate a percentage (0-100)"""
    try:
        val = Decimal(str(pct))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid percentage: {pct}")
    if val < 0 or val > 100:
        raise ValueError(f"Percentage out of range (0-100): {val}")
    return val.quantize(Decimal('0.01'))


def sanitize_email(email: str) -> str:
    """Basic email sanitization"""
    email = sanitize_text(email, 254)
    if '@' not in email or '.' not in email.split('@')[-1]:
        raise ValueError(f"Invalid email: {email}")
    return email.strip().lower()


def sanitize_phone(phone: str) -> str:
    """Allow only digits, +, -, space, (,)"""
    phone = sanitize_text(phone, 30)
    cleaned = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
    return cleaned.strip()


def sanitize_ip_address(ip: str) -> str:
    """Basic IP validation (for audit logging)"""
    ip = ip.strip()
    ipv4 = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)
    if not ipv4:
        raise ValueError(f"Invalid IP address: {ip}")
    parts = [int(p) for p in ip.split('.')]
    if any(p > 255 for p in parts):
        raise ValueError(f"Invalid IP address: {ip}")
    return ip
