"""
PyLedger Core Module - Transaction
Represents a single ledger transaction
"""

from decimal import Decimal
from datetime import datetime


def _strict_amount(amount):
    # Deferred import (circular): security.__init__ -> validator -> ledger.
    from pyledger.security.sanitizer import sanitize_amount
    try:
        return sanitize_amount(amount, allow_zero=True, allow_negative=False)
    except ValueError as e:
        raise ValueError(f"Invalid transaction amount: {e}")


class Transaction:
    """
    Represents a transaction (debit or credit to an account)
    
    Attributes:
        account: Account object
        type: 'debit' or 'credit'
        amount: Transaction amount
        date: Transaction date
        description: Transaction description
    """
    
    def __init__(
        self,
        account,
        transaction_type: str,
        amount,
        date: datetime = None,
        description: str = ''
    ):
        """
        Initialize a Transaction
        
        Args:
            account: Account object
            transaction_type: 'debit' or 'credit'
            amount: Transaction amount
            date: Transaction date (default: now)
            description: Transaction description
        """
        if transaction_type.lower() not in ['debit', 'credit']:
            raise ValueError("Transaction type must be 'debit' or 'credit'")

        # Security: legs must be non-negative. A negative leg would invert
        # double-entry economics while staying "balanced". Zero is allowed
        # (no-op postings, e.g. zero-balance period closes).
        amount = _strict_amount(amount)

        self.account = account
        self.type = transaction_type.lower()
        self.amount = amount
        self.date = date or datetime.now()
        self.description = description
        self.posted = False
    
    def get_amount(self) -> Decimal:
        """Get transaction amount"""
        return self.amount
    
    def is_debit(self) -> bool:
        """Check if transaction is debit"""
        return self.type == 'debit'
    
    def is_credit(self) -> bool:
        """Check if transaction is credit"""
        return self.type == 'credit'
    
    def __str__(self) -> str:
        return f"{self.type.upper()}: {self.account.code} - {self.amount} ({self.description})"
    
    def __repr__(self) -> str:
        return f"Transaction({self.account.code}, {self.type}, {self.amount})"
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary"""
        return {
            'account_code': self.account.code,
            'type': self.type,
            'amount': str(self.amount),
            'date': self.date.isoformat(),
            'description': self.description,
            'posted': self.posted,
        }
