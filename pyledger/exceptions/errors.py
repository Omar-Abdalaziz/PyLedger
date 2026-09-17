"""
PyLedger Exceptions Module
Custom exceptions for accounting operations
"""


class PyLedgerException(Exception):
    """Base exception for PyLedger"""
    pass


class AccountNotFoundError(PyLedgerException):
    """Raised when account is not found"""
    pass


class UnbalancedEntryError(PyLedgerException):
    """Raised when journal entry is not balanced"""
    pass


class InvalidAccountTypeError(PyLedgerException):
    """Raised when account type is invalid"""
    pass


class InsufficientBalanceError(PyLedgerException):
    """Raised when account has insufficient balance for withdrawal"""
    pass


class DuplicateAccountError(PyLedgerException):
    """Raised when trying to create duplicate account code"""
    pass


class InvalidCurrencyError(PyLedgerException):
    """Raised when currency is invalid"""
    pass


class InvalidTaxRateError(PyLedgerException):
    """Raised when tax rate is invalid"""
    pass


class InvoiceNotFoundError(PyLedgerException):
    """Raised when invoice is not found"""
    pass


class InvalidInvoiceStatusError(PyLedgerException):
    """Raised when invoice status transition is invalid"""
    pass
