"""
PyLedger Core Module - Account
Represents a general ledger account
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pyledger.utils.validators import (
    validate_account_code,
    validate_account_type,
    format_amount,
)
from pyledger.exceptions.errors import (
    InvalidAccountTypeError,
    InsufficientBalanceError,
)


def _sanitize_amount(*args, **kwargs):
    # Deferred import: pyledger.security.__init__ pulls validator -> ledger
    # -> account (circular at module load). Resolved lazily at call time.
    from pyledger.security.sanitizer import sanitize_amount
    return sanitize_amount(*args, **kwargs)
from pyledger.exceptions.errors import (
    InvalidAccountTypeError,
    InsufficientBalanceError,
)


class Account:
    """
    Represents a general ledger account.

    Accounting semantics:
    - GL accounts follow normal-balance rules and MAY go negative in
      ledger terms (e.g. contra situations, timing). Use CashAccount
      when strict no-overdraft behaviour is required.
    - deposit()/withdraw() are cash-style helpers kept for backward
      compatibility; JournalEntry.post() applies proper debit/credit
      rules via apply_debit()/apply_credit().

    Attributes:
        code: Unique account identifier
        name: Account name
        type: Account type (asset, liability, equity, income, expense)
        balance: Current account balance
        currency: Account currency
        description: Account description
    """

    VALID_TYPES = ['asset', 'liability', 'equity', 'income', 'expense']

    # Normal balance side per type (Phase 1 fix)
    NORMAL_BALANCE = {
        'asset': 'debit',
        'expense': 'debit',
        'liability': 'credit',
        'equity': 'credit',
        'income': 'credit',
    }

    def __init__(
        self,
        name: str,
        account_type: str,
        code: str,
        currency: str = 'USD',
        description: str = '',
        initial_balance: Decimal = Decimal('0'),
        allow_negative: bool = False,
    ):
        """
        Initialize an Account
        
        Args:
            name: Account name
            account_type: Type of account (asset, liability, equity, income, expense)
            code: Unique account code
            currency: Account currency (default: USD)
            description: Account description
            initial_balance: Initial account balance
        """
        if not validate_account_type(account_type):
            raise InvalidAccountTypeError(
                f"Invalid account type: {account_type}. "
                f"Valid types: {', '.join(self.VALID_TYPES)}"
            )
        
        if not validate_account_code(code):
            raise ValueError(
                "Invalid account code. Must be 2-20 alphanumeric characters with hyphens"
            )
        
        self.code = code
        self.name = name
        self.type = account_type.lower()
        self.currency = currency
        self.description = description
        self.balance = format_amount(initial_balance)
        self.created_date = datetime.now()
        self.transactions = []  # History of transactions
        self.allow_negative = allow_negative

    @property
    def normal_balance(self) -> str:
        """Return 'debit' or 'credit' normal side for this account type."""
        return self.NORMAL_BALANCE.get(self.type, 'debit')

    def is_debit_normal(self) -> bool:
        return self.normal_balance == 'debit'

    def is_credit_normal(self) -> bool:
        return self.normal_balance == 'credit'

    def apply_debit(self, amount, description: str = '') -> Decimal:
        """Apply debit per double-entry rules (always succeeds for GL)."""
        amount = format_amount(amount)
        if self.is_debit_normal():
            self.balance += amount
        else:
            self.balance -= amount
        self.balance = format_amount(self.balance)
        self.transactions.append({
            'type': 'debit',
            'amount': amount,
            'description': description,
            'timestamp': datetime.now(),
            'balance_after': self.balance
        })
        return self.balance

    def apply_credit(self, amount, description: str = '') -> Decimal:
        """Apply credit per double-entry rules (always succeeds for GL)."""
        amount = format_amount(amount)
        if self.is_credit_normal():
            self.balance += amount
        else:
            self.balance -= amount
        self.balance = format_amount(self.balance)
        self.transactions.append({
            'type': 'credit',
            'amount': amount,
            'description': description,
            'timestamp': datetime.now(),
            'balance_after': self.balance
        })
        return self.balance
    
    def deposit(self, amount, description: str = '') -> Decimal:
        """
        Add money to the account

        Args:
            amount: Amount to deposit (must be >= 0)
            description: Transaction description

        Returns:
            New balance
        """
        try:
            amount = _sanitize_amount(amount, allow_zero=True, allow_negative=False)
        except ValueError as e:
            raise ValueError(f"Invalid deposit amount: {e}")
        self.balance += amount
        self.transactions.append({
            'type': 'deposit',
            'amount': amount,
            'description': description,
            'timestamp': datetime.now(),
            'balance_after': self.balance
        })
        return self.balance
    
    def withdraw(self, amount, description: str = '') -> Decimal:
        """
        Remove money from the account
        
        Args:
            amount: Amount to withdraw
            description: Transaction description
            
        Returns:
            New balance
            
        Raises:
            ValueError: If amount is not positive
            InsufficientBalanceError: If balance is insufficient
        """
        try:
            amount = _sanitize_amount(amount, allow_zero=False, allow_negative=False)
        except ValueError as e:
            raise ValueError(f"Invalid withdrawal amount: {e}")

        if not self.allow_negative and self.balance < amount:
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: {self.balance}, Requested: {amount}"
            )
        
        self.balance -= amount
        self.transactions.append({
            'type': 'withdrawal',
            'amount': amount,
            'description': description,
            'timestamp': datetime.now(),
            'balance_after': self.balance
        })
        return self.balance
    
    def get_balance(self, as_of_date: Optional[datetime] = None) -> Decimal:
        """Get account balance, optionally as of a specific date"""
        if as_of_date is None:
            return self.balance
        total = Decimal('0')
        for txn in self.transactions:
            if txn['timestamp'] <= as_of_date:
                if txn['type'] in ('deposit', 'debit'):
                    total += txn['amount']
                else:
                    total -= txn['amount']
        return format_amount(total)

    def get_balance_as_of(self, as_of_date: datetime) -> Decimal:
        """Alias for get_balance(as_of_date) - required by test suite."""
        return self.get_balance(as_of_date)

    def get_debit_balance(self) -> Decimal:
        """
        Get debit balance for trial balance
        Debit accounts: assets, expenses
        """
        if self.type in ['asset', 'expense']:
            return self.balance if self.balance > 0 else Decimal('0')
        # Credit-normal accounts with negative balance appear as debits
        return -self.balance if self.balance < 0 else Decimal('0')

    def get_credit_balance(self) -> Decimal:
        """
        Get credit balance for trial balance
        Credit accounts: liabilities, equity, income
        """
        if self.type in ['liability', 'equity', 'income']:
            return self.balance if self.balance > 0 else Decimal('0')
        # Debit-normal accounts with negative balance appear as credits
        return -self.balance if self.balance < 0 else Decimal('0')

    def get_transactions(self, limit: Optional[int] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         txn_type: Optional[str] = None) -> list:
        """Get transaction history with optional date/type filtering"""
        txns = self.transactions
        if txn_type:
            txns = [t for t in txns if t.get('type') == txn_type]
        if start_date:
            txns = [t for t in txns if t['timestamp'] >= start_date]
        if end_date:
            txns = [t for t in txns if t['timestamp'] <= end_date]
        if limit:
            return txns[-limit:]
        return txns
    
    def __str__(self) -> str:
        return f"{self.code} - {self.name} ({self.type}): {self.balance} {self.currency}"
    
    def __repr__(self) -> str:
        return f"Account({self.code}, {self.name}, {self.type}, {self.balance})"
    
    def to_dict(self) -> dict:
        """Convert account to dictionary"""
        return {
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'balance': str(self.balance),
            'currency': self.currency,
            'description': self.description,
            'created_date': self.created_date.isoformat(),
        }


class CashAccount(Account):
    """
    Cash/bank account with strict no-overdraft semantics.

    Use this when InsufficientBalanceError behaviour is required.
    Plain Account (GL) allows negative balances per normal accounting.
    """

    def __init__(self, name: str, code: str, currency: str = 'USD',
                 description: str = '', initial_balance: Decimal = Decimal('0')):
        super().__init__(name, 'asset', code, currency, description,
                         initial_balance, allow_negative=False)


class GLAccount(Account):
    """
    General-ledger account that permits negative (contra/timing) balances.

    Direct withdraw() will NOT raise; postings go through
    apply_debit()/apply_credit() which never block.
    """

    def __init__(self, name: str, account_type: str, code: str,
                 currency: str = 'USD', description: str = '',
                 initial_balance: Decimal = Decimal('0')):
        super().__init__(name, account_type, code, currency, description,
                         initial_balance, allow_negative=True)
