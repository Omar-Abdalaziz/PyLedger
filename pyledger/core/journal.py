"""
PyLedger Core Module - Journal Entry
Represents a journal entry (accounting entry with debits and credits)
"""

from decimal import Decimal
from datetime import datetime
from pyledger.core.transaction import Transaction
from pyledger.utils.validators import format_amount
from pyledger.exceptions.errors import UnbalancedEntryError


class AlreadyPostedError(UnbalancedEntryError):
    """Raised when attempting to post an already-posted entry."""
    pass


class JournalEntry:
    """
    Represents a journal entry with debits and credits
    
    Attributes:
        number: Entry number (unique identifier)
        date: Entry date
        description: Entry description
        debits: List of debit transactions
        credits: List of credit transactions
    """
    
    _entry_counter = 0

    def __init__(
        self,
        description: str,
        date: datetime = None,
        entry_number: str = None,
        unique_number: bool = False,
        company_id: str = 'default',
        cost_center: str = None,
    ):
        """
        Initialize a Journal Entry

        Args:
            description: Entry description
            date: Entry date (default: now)
            entry_number: Entry number (auto-generated if not provided)
            unique_number: Use UUID-based globally unique number
            company_id: Tenant identifier (multi-company isolation)
            cost_center: Optional cost/profit center tag
        """
        from pyledger.core.sequences import next_journal_number
        self.number = next_journal_number(entry_number, unique=unique_number)
        JournalEntry._entry_counter += 1
        self.date = date or datetime.now()
        self.description = description
        self.company_id = company_id
        self.cost_center = cost_center
        self.debits = []
        self.credits = []
        self.posted = False
        self.posted_date = None
    
    def add_debit(self, account, amount, description: str = '') -> 'JournalEntry':
        """
        Add a debit transaction
        
        Args:
            account: Account object
            amount: Amount to debit
            description: Transaction description
            
        Returns:
            Self for method chaining
        """
        transaction = Transaction(account, 'debit', amount, self.date, description)
        self.debits.append(transaction)
        return self
    
    def add_credit(self, account, amount, description: str = '') -> 'JournalEntry':
        """
        Add a credit transaction
        
        Args:
            account: Account object
            amount: Amount to credit
            description: Transaction description
            
        Returns:
            Self for method chaining
        """
        transaction = Transaction(account, 'credit', amount, self.date, description)
        self.credits.append(transaction)
        return self
    
    def get_total_debits(self) -> Decimal:
        """Get total debits"""
        return sum((t.amount for t in self.debits), Decimal('0'))
    
    def get_total_credits(self) -> Decimal:
        """Get total credits"""
        return sum((t.amount for t in self.credits), Decimal('0'))
    
    def is_balanced(self) -> bool:
        """
        Check if entry is balanced (debits == credits)
        
        Returns:
            True if balanced, False otherwise
        """
        return self.get_total_debits() == self.get_total_credits()
    
    def validate(self) -> bool:
        """
        Validate entry before posting
        
        Raises:
            UnbalancedEntryError: If entry is not balanced
        """
        if not self.debits or not self.credits:
            raise UnbalancedEntryError("Entry must have both debits and credits")
        
        if not self.is_balanced():
            total_debits = self.get_total_debits()
            total_credits = self.get_total_credits()
            raise UnbalancedEntryError(
                f"Entry is unbalanced. Debits: {total_debits}, Credits: {total_credits}"
            )
        
        return True
    
    def post(self, ledger=None, validator=None) -> bool:
        """
        Post entry to ledger (idempotent guard + proper debit/credit rules).

        Args:
            ledger: Optional ledger to post to
            validator: Optional EntryValidator for deep validation

        Returns:
            True if posted successfully

        Raises:
            UnbalancedEntryError: If entry is not balanced
            AlreadyPostedError: If entry was already posted
            BusinessRuleError: If validation fails
        """
        if self.posted:
            raise AlreadyPostedError(f"Entry {self.number} is already posted")
        self.validate()
        if validator:
            from pyledger.security.validator import EntryValidator
            if isinstance(validator, EntryValidator):
                validator.validate_and_raise(self)
            else:
                validator(self)
        
        # Post using proper double-entry semantics via Account helpers.
        # GL accounts never block posting (normal-balance rules); cash-level
        # overdraft control belongs to CashAccount / BusinessEngine validators.
        for transaction in self.debits:
            transaction.account.apply_debit(transaction.amount, self.description)
            transaction.posted = True

        for transaction in self.credits:
            transaction.account.apply_credit(transaction.amount, self.description)
            transaction.posted = True
        
        self.posted = True
        self.posted_date = datetime.now()
        
        return True

    def reverse(self, description: str = None, date: datetime = None) -> 'JournalEntry':
        """Create an equal-and-opposite entry (never mutate a posted entry)."""
        rev = JournalEntry(
            description or f"Reversal of {self.number}",
            date=date,
        )
        for t in self.debits:
            rev.add_credit(t.account, t.amount, f"Reversal of {self.number}")
        for t in self.credits:
            rev.add_debit(t.account, t.amount, f"Reversal of {self.number}")
        return rev
    
    def __str__(self) -> str:
        return (
            f"Journal Entry {self.number} - {self.date.strftime('%Y-%m-%d')}\n"
            f"Description: {self.description}\n"
            f"Debits: {self.get_total_debits()}, Credits: {self.get_total_credits()}"
        )
    
    def __repr__(self) -> str:
        return f"JournalEntry({self.number}, {self.description}, balanced={self.is_balanced()})"
    
    def to_dict(self) -> dict:
        """Convert entry to dictionary"""
        return {
            'number': self.number,
            'date': self.date.isoformat(),
            'description': self.description,
            'company_id': self.company_id,
            'cost_center': self.cost_center,
            'debits': [t.to_dict() for t in self.debits],
            'credits': [t.to_dict() for t in self.credits],
            'total_debits': str(self.get_total_debits()),
            'total_credits': str(self.get_total_credits()),
            'balanced': self.is_balanced(),
            'posted': self.posted,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
        }
