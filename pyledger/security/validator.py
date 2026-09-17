"""
PyLedger Security - Business Validator
Enforces business rules, duplicates detection, and security constraints
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List, Set, Tuple
from pyledger.core.ledger import Ledger
from pyledger.core.journal import JournalEntry
from pyledger.core.account import Account
from pyledger.core.closing import ClosingEngine
from pyledger.security.sanitizer import (
    sanitize_text, sanitize_account_code, sanitize_amount,
    sanitize_quantity, sanitize_percentage, sanitize_description,
    sanitize_name,
)


class ValidationError(Exception):
    pass


class DuplicateEntryError(ValidationError):
    pass


class BusinessRuleError(ValidationError):
    pass


class SecurityValidationError(ValidationError):
    pass


# ── Duplicate Detection ──────────────────────────────────────────


class DuplicateDetector:
    """Detect duplicate transactions, invoices, and entries"""

    def __init__(self):
        self._seen_signatures: Set[str] = set()
        self._window = timedelta(hours=24)

    def _signature(self, *args) -> str:
        return '|'.join(str(a) for a in args)

    def check_entry(self, entry: JournalEntry) -> bool:
        sig = self._signature(
            entry.description,
            str(entry.get_total_debits()),
            str(entry.get_total_credits()),
            entry.date.strftime('%Y-%m-%d %H') if entry.date else '',
        )
        return sig in self._seen_signatures

    def mark_seen(self, entry: JournalEntry):
        sig = self._signature(
            entry.description,
            str(entry.get_total_debits()),
            str(entry.get_total_credits()),
            entry.date.strftime('%Y-%m-%d %H') if entry.date else '',
        )
        self._seen_signatures.add(sig)

    def check_invoice(self, customer: str, items: list,
                      total: Decimal, date: datetime) -> bool:
        items_sig = ';'.join(
            f"{i.get('name', '')}_{i.get('quantity', 0)}_{i.get('price', 0)}"
            for i in items
        )
        sig = self._signature(customer, items_sig, str(total),
                              date.strftime('%Y-%m-%d'))
        return sig in self._seen_signatures

    def mark_invoice_seen(self, customer: str, items: list,
                          total: Decimal, date: datetime):
        items_sig = ';'.join(
            f"{i.get('name', '')}_{i.get('quantity', 0)}_{i.get('price', 0)}"
            for i in items
        )
        sig = self._signature(customer, items_sig, str(total),
                              date.strftime('%Y-%m-%d'))
        self._seen_signatures.add(sig)

    def clear(self):
        self._seen_signatures.clear()


# ── Entry Validator ──────────────────────────────────────────────


class EntryValidator:
    """Deep validation of journal entries before posting"""

    def __init__(self, ledger: Ledger, closing_engine: Optional[ClosingEngine] = None):
        self.ledger = ledger
        self.closing_engine = closing_engine

    def validate(self, entry: JournalEntry) -> List[str]:
        """Validate entry and return list of errors (empty = valid)"""
        errors = []

        errors.extend(self._validate_balance(entry))
        errors.extend(self._validate_accounts(entry))
        errors.extend(self._validate_amounts(entry))
        errors.extend(self._validate_period(entry))
        errors.extend(self._validate_description(entry))

        return errors

    def validate_and_raise(self, entry: JournalEntry):
        errors = self.validate(entry)
        if errors:
            raise BusinessRuleError('; '.join(errors))

    def _validate_balance(self, entry: JournalEntry) -> List[str]:
        errors = []
        if not entry.debits or not entry.credits:
            errors.append("Entry must have at least one debit and one credit")
        elif entry.get_total_debits() != entry.get_total_credits():
            errors.append(
                f"Unbalanced entry: debits={entry.get_total_debits()}, "
                f"credits={entry.get_total_credits()}"
            )
        return errors

    def _validate_accounts(self, entry: JournalEntry) -> List[str]:
        errors = []
        for txn in entry.debits + entry.credits:
            code = txn.account.code
            if not self.ledger.account_exists(code):
                errors.append(f"Account '{code}' does not exist in ledger")
        return errors

    def _validate_amounts(self, entry: JournalEntry) -> List[str]:
        errors = []
        for txn in entry.debits + entry.credits:
            try:
                sanitize_amount(txn.amount, allow_negative=False)
            except ValueError as e:
                errors.append(f"Invalid amount in {txn.account.code}: {e}")
        return errors

    def _validate_period(self, entry: JournalEntry) -> List[str]:
        errors = []
        if self.closing_engine and entry.date:
            period_label = entry.date.strftime('%Y-%m')
            if period_label in self.closing_engine.closed_periods:
                errors.append(f"Period '{period_label}' is closed")
        return errors

    def _validate_description(self, entry: JournalEntry) -> List[str]:
        errors = []
        if not entry.description or not entry.description.strip():
            errors.append("Entry description cannot be empty")
        return errors


# ── Account Validator ────────────────────────────────────────────


def validate_new_account(name: str, account_type: str, code: str) -> List[str]:
    """Validate new account parameters"""
    errors = []

    try:
        sanitize_name(name)
    except ValueError as e:
        errors.append(str(e))

    valid_types = ['asset', 'liability', 'equity', 'income', 'expense']
    if account_type not in valid_types:
        errors.append(f"Invalid account type '{account_type}'. Must be one of: {valid_types}")

    try:
        sanitize_account_code(code)
    except ValueError as e:
        errors.append(str(e))

    return errors


# ── Invoice Validator ────────────────────────────────────────────


def validate_invoice_items(items: list) -> List[str]:
    """Validate invoice items"""
    errors = []
    if not items:
        return ["Invoice must have at least one item"]

    for i, item in enumerate(items):
        try:
            qty = sanitize_quantity(item.get('quantity', 0), min_qty=1)
        except ValueError as e:
            errors.append(f"Item {i}: {e}")

        try:
            price = sanitize_amount(item.get('price', 0), allow_negative=False)
        except ValueError as e:
            errors.append(f"Item {i} price: {e}")

        name = item.get('name', '')
        if not name or not str(name).strip():
            errors.append(f"Item {i}: name is required")

    return errors


def validate_tax_rate(rate: float) -> List[str]:
    errors = []
    try:
        sanitize_percentage(Decimal(str(rate)))
    except ValueError as e:
        errors.append(str(e))
    return errors
