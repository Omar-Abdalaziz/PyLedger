"""
PyLedger Exceptions Module
Custom exceptions for accounting operations
"""


class PyLedgerException(Exception):
    """Base exception for PyLedger"""


class AccountNotFoundError(PyLedgerException):
    """Raised when account is not found"""


class UnbalancedEntryError(PyLedgerException):
    """Raised when journal entry is not balanced"""


class InvalidAccountTypeError(PyLedgerException):
    """Raised when account type is invalid"""


class InsufficientBalanceError(PyLedgerException):
    """Raised when account has insufficient balance for withdrawal"""


class DuplicateAccountError(PyLedgerException):
    """Raised when trying to create duplicate account code"""


class InvalidCurrencyError(PyLedgerException):
    """Raised when currency is invalid"""


class InvalidTaxRateError(PyLedgerException):
    """Raised when tax rate is invalid"""


class InvoiceNotFoundError(PyLedgerException):
    """Raised when invoice is not found"""


class InvalidInvoiceStatusError(PyLedgerException):
    """Raised when invoice status transition is invalid"""
