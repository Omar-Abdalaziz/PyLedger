"""
PyLedger Business Module - Business Validation Rules
Ensures business operations are valid before execution
"""

from decimal import Decimal
from datetime import datetime


class BusinessValidationError(Exception):
    """Raised when a business operation validation fails"""


class BusinessGuard:
    """Guard rails that prevent common accounting mistakes"""

    @staticmethod
    def require_positive_amount(amount, field_name: str = 'amount'):
        if Decimal(str(amount)) <= 0:
            raise BusinessValidationError(
                f"{field_name} must be positive, got {amount}"
            )

    @staticmethod
    def require_non_empty_items(items: list, field_name: str = 'items'):
        if not items:
            raise BusinessValidationError(
                f"{field_name} cannot be empty"
            )

    @staticmethod
    def require_account_exists(ledger, code: str, name: str = 'Account'):
        if not ledger.account_exists(code):
            raise BusinessValidationError(
                f"{name} with code '{code}' not found in ledger"
            )

    @staticmethod
    def require_valid_date(date_obj, field_name: str = 'date'):
        if not isinstance(date_obj, datetime):
            try:
                datetime.fromisoformat(str(date_obj))
            except (ValueError, TypeError):
                raise BusinessValidationError(
                    f"{field_name} is not a valid date: {date_obj}"
                )

    @staticmethod
    def require_valid_customer(customer: str):
        if not customer or not customer.strip():
            raise BusinessValidationError(
                "Customer name cannot be empty"
            )
