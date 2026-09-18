"""
PyLedger Security Module - Input Validation & Injection Prevention

Note: validator names are exposed LAZILY (PEP 562). validator.py imports
core.ledger, so importing it eagerly here would create a circular import
(core -> reports -> security -> validator -> core). Leaf modules
(sanitizer, passwords) are safe to import eagerly.
"""

from pyledger.security.sanitizer import (
    sanitize_text, sanitize_description, sanitize_name,
    sanitize_account_code, sanitize_amount, sanitize_quantity,
    sanitize_percentage, sanitize_csv_field, sanitize_email,
    sanitize_phone, sanitize_filepath, normalize_tax_rate,
)
from pyledger.security.passwords import hash_password, verify_password

_LAZY_VALIDATOR_NAMES = frozenset({
    'EntryValidator', 'DuplicateDetector',
    'ValidationError', 'DuplicateEntryError',
    'BusinessRuleError', 'SecurityValidationError',
    'validate_new_account', 'validate_invoice_items', 'validate_tax_rate',
})


def __getattr__(name: str):
    if name in _LAZY_VALIDATOR_NAMES:
        from pyledger.security import validator as _validator
        return getattr(_validator, name)
    raise AttributeError(f"module 'pyledger.security' has no attribute {name!r}")


__all__ = [
    'sanitize_text', 'sanitize_description', 'sanitize_name',
    'sanitize_account_code', 'sanitize_amount', 'sanitize_quantity',
    'sanitize_percentage', 'sanitize_csv_field', 'sanitize_email',
    'sanitize_phone', 'sanitize_filepath', 'normalize_tax_rate',
    'hash_password', 'verify_password',
    'EntryValidator', 'DuplicateDetector',
    'ValidationError', 'DuplicateEntryError',
    'BusinessRuleError', 'SecurityValidationError',
    'validate_new_account', 'validate_invoice_items', 'validate_tax_rate',
]
