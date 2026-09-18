"""
PyLedger Utilities Module - Validators
Data validation functions for accounting operations
"""

import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pyledger.exceptions.errors import InvalidCurrencyError, InvalidTaxRateError


# Supported currencies
SUPPORTED_CURRENCIES = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'SAR': '﷼',
    'AED': 'د.إ',
    'EGP': '£',
    'JOD': 'د.ا',
    'KWD': 'د.ك',
}


def validate_account_code(code: str) -> bool:
    """
    Validate account code format
    Code should be alphanumeric with hyphens
    """
    pattern = r'^[A-Z0-9\-]{2,20}$'
    return bool(re.match(pattern, code))


def validate_account_type(account_type: str) -> bool:
    """Validate account type"""
    valid_types = ['asset', 'liability', 'equity', 'income', 'expense']
    return account_type.lower() in valid_types


def validate_amount(amount) -> bool:
    """Validate amount is positive number"""
    try:
        decimal_amount = Decimal(str(amount))
        return decimal_amount > 0
    except:
        return False


def validate_currency(currency: str) -> bool:
    """Validate currency code - returns False for unsupported codes."""
    try:
        if currency is None:
            return False
        return currency.upper() in SUPPORTED_CURRENCIES
    except Exception:
        return False


def validate_currency_strict(currency: str) -> bool:
    """Strict version that raises InvalidCurrencyError for unsupported codes."""
    if not validate_currency(currency):
        raise InvalidCurrencyError(
            f"Currency {currency} not supported. "
            f"Supported: {', '.join(SUPPORTED_CURRENCIES.keys())}"
        )
    return True


def validate_tax_rate(rate: float) -> bool:
    """Validate tax rate (should be between 0 and 100)"""
    try:
        rate_float = float(rate)
        if not (0 <= rate_float <= 100):
            raise InvalidTaxRateError(f"Tax rate must be between 0 and 100, got {rate_float}")
        return True
    except (ValueError, TypeError):
        raise InvalidTaxRateError(f"Invalid tax rate: {rate}")


def validate_date(date_obj) -> bool:
    """Validate date format"""
    if isinstance(date_obj, datetime):
        return True
    try:
        datetime.fromisoformat(str(date_obj))
        return True
    except:
        return False


def format_amount(amount, decimals: int = 2) -> Decimal:
    """Convert and format amount to Decimal.

    Uses ROUND_HALF_UP (the accounting/tax standard: 2.5% of 1.00 is 0.03,
    not 0.02 as banker's rounding would give).
    """
    try:
        return Decimal(str(amount)).quantize(Decimal(10) ** -decimals,
                                             rounding=ROUND_HALF_UP)
    except:
        raise ValueError(f"Invalid amount: {amount}")
