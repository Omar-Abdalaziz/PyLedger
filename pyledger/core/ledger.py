"""
PyLedger Core Module - Ledger
Represents a general ledger
"""

from decimal import Decimal
from datetime import datetime
from pyledger.core.account import Account
from pyledger.core.journal import JournalEntry
from pyledger.exceptions.errors import (
    AccountNotFoundError,
    DuplicateAccountError,
)


class Ledger:
    """
    Represents a general ledger containing accounts and journal entries
    
    Attributes:
        name: Ledger name
        currency: Base currency
        accounts: Dictionary of accounts by code
        journal_entries: List of journal entries
    """
    
    def __init__(self, name: str = 'Main Ledger', currency: str = 'USD',
                 company_id: str = 'default'):
        """
        Initialize a Ledger

        Args:
            name: Ledger name
            currency: Base currency
            company_id: Tenant identifier for multi-company isolation
        """
        self.name = name
        self.currency = currency
        self.company_id = company_id
        self.accounts = {}
        self.journal_entries = []
        self.created_date = datetime.now()
        self._tb_cache = None
        self._tb_version = 0
        self._entries_version = 0
    
    def add_account(self, account: Account) -> Account:
        """
        Add an account to the ledger
        
        Args:
            account: Account object
            
        Returns:
            The added account
            
        Raises:
            DuplicateAccountError: If account code already exists
        """
        if account.code in self.accounts:
            raise DuplicateAccountError(
                f"Account with code {account.code} already exists"
            )
        
        self.accounts[account.code] = account
        return account
    
    def get_account(self, code: str) -> Account:
        """
        Get an account by code
        
        Args:
            code: Account code
            
        Returns:
            Account object
            
        Raises:
            AccountNotFoundError: If account not found
        """
        if code not in self.accounts:
            raise AccountNotFoundError(f"Account {code} not found")
        
        return self.accounts[code]
    
    def account_exists(self, code: str) -> bool:
        """Check if account exists"""
        return code in self.accounts
    
    def get_accounts_by_type(self, account_type: str) -> list:
        """Get all accounts of a specific type"""
        return [
            acc for acc in self.accounts.values()
            if acc.type == account_type.lower()
        ]
    
    def transfer(self, from_account: Account, to_account: Account, amount) -> JournalEntry:
        """
        Transfer amount between two accounts
        
        Args:
            from_account: Source account
            to_account: Destination account
            amount: Amount to transfer
            
        Returns:
            Journal entry created for the transfer
        """
        entry = JournalEntry(
            f"Transfer from {from_account.name} to {to_account.name}"
        )
        entry.add_debit(to_account, amount, f"Transfer from {from_account.code}")
        entry.add_credit(from_account, amount, f"Transfer to {to_account.code}")
        entry.post()

        self.journal_entries.append(entry)
        self._entries_version += 1
        self._tb_cache = None
        return entry
    
    def record_entry(self, journal_entry: JournalEntry) -> bool:
        """
        Record a journal entry

        Args:
            journal_entry: JournalEntry object

        Returns:
            True if recorded successfully
        """
        if getattr(journal_entry, 'company_id', 'default') not in ('default', self.company_id):
            # Enforce tenant isolation (default entries are portable)
            raise ValueError(
                f"Entry company '{journal_entry.company_id}' != ledger '{self.company_id}'")
        journal_entry.validate()
        journal_entry.post()
        self.journal_entries.append(journal_entry)
        self._entries_version += 1
        self._tb_cache = None
        try:
            from pyledger.events import default_bus, ENTRY_POSTED
            default_bus.emit(ENTRY_POSTED, {"number": journal_entry.number,
                                            "company_id": self.company_id})
        except Exception:
            pass
        return True

    def bulk_record(self, entries: list) -> int:
        """Atomically validate + post many entries; rollback on any failure."""
        for e in entries:
            e.validate()
        posted = []
        try:
            for e in entries:
                e.post()
                posted.append(e)
        except Exception:
            # Roll back in-memory balances by reversing posted ones
            for e in posted:
                try:
                    rev = e.reverse(f"Rollback of {e.number}")
                    rev.post()
                    self.journal_entries.append(rev)
                except Exception:
                    pass
            raise
        self.journal_entries.extend(posted)
        self._entries_version += 1
        self._tb_cache = None
        return len(posted)

    def query_entries(self, limit: int = 100, offset: int = 0,
                      company_id: str = None, cost_center: str = None,
                      start_date=None, end_date=None) -> list:
        """Paginated + filtered entry access (scales beyond get_journal_entries)."""
        result = self.journal_entries
        if company_id:
            result = [e for e in result if getattr(e, 'company_id', 'default') == company_id]
        if cost_center:
            result = [e for e in result if getattr(e, 'cost_center', None) == cost_center]
        if start_date:
            result = [e for e in result if e.date >= start_date]
        if end_date:
            result = [e for e in result if e.date <= end_date]
        return result[offset:offset + limit]
    
    def get_trial_balance(self) -> dict:
        """
        Get trial balance (list of all accounts with debits and credits).

        String-based totals kept for backward compatibility / JSON export.
        Use trial_balance() for Decimal totals suitable for arithmetic.
        """
        data = self.trial_balance()
        return {
            'date': data['date'],
            'accounts': [
                {**a, 'debit': str(a['debit']), 'credit': str(a['credit'])}
                for a in data['accounts']
            ],
            'total_debits': str(data['total_debits']),
            'total_credits': str(data['total_credits']),
            'balanced': data['balanced'],
        }

    def trial_balance(self) -> dict:
        """Trial balance with Decimal totals + in-memory cache."""
        if self._tb_cache is not None and self._tb_cache.get('_v') == self._entries_version:
            return {k: v for k, v in self._tb_cache.items() if k != '_v'}
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        accounts_data = []

        for account in self.accounts.values():
            debit_balance = account.get_debit_balance()
            credit_balance = account.get_credit_balance()

            total_debits += debit_balance
            total_credits += credit_balance

            accounts_data.append({
                'code': account.code,
                'name': account.name,
                'type': account.type,
                'debit': debit_balance,
                'credit': credit_balance,
            })

        data = {
            'date': datetime.now().isoformat(),
            'accounts': accounts_data,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'balanced': total_debits == total_credits,
            '_v': self._entries_version,
        }
        self._tb_cache = data
        return {k: v for k, v in data.items() if k != '_v'}
    
    def get_account_balance(self, code: str) -> Decimal:
        """Get balance of specific account"""
        account = self.get_account(code)
        return account.get_balance()
    
    def get_total_assets(self) -> Decimal:
        """Get total assets"""
        assets = self.get_accounts_by_type('asset')
        return sum((acc.get_balance() for acc in assets), Decimal('0'))
    
    def get_total_liabilities(self) -> Decimal:
        """Get total liabilities"""
        liabilities = self.get_accounts_by_type('liability')
        return sum((acc.get_balance() for acc in liabilities), Decimal('0'))
    
    def get_total_equity(self) -> Decimal:
        """Get total equity"""
        equity = self.get_accounts_by_type('equity')
        return sum((acc.get_balance() for acc in equity), Decimal('0'))
    
    def get_total_income(self) -> Decimal:
        """Get total income"""
        income = self.get_accounts_by_type('income')
        return sum((acc.get_balance() for acc in income), Decimal('0'))
    
    def get_total_expenses(self) -> Decimal:
        """Get total expenses"""
        expenses = self.get_accounts_by_type('expense')
        return sum((acc.get_balance() for acc in expenses), Decimal('0'))
    
    def get_journal_entries(self, limit: int = None) -> list:
        """Get journal entries"""
        if limit:
            return self.journal_entries[-limit:]
        return self.journal_entries
    
    def __str__(self) -> str:
        return (
            f"Ledger: {self.name}\n"
            f"Accounts: {len(self.accounts)}\n"
            f"Currency: {self.currency}"
        )
    
    def to_dict(self) -> dict:
        """Convert ledger to dictionary"""
        return {
            'name': self.name,
            'currency': self.currency,
            'accounts': {code: acc.to_dict() for code, acc in self.accounts.items()},
            'total_accounts': len(self.accounts),
            'total_entries': len(self.journal_entries),
            'created_date': self.created_date.isoformat(),
        }
