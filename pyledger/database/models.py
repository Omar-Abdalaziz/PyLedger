"""
PyLedger Database Models
Data models for persistence
"""

from datetime import datetime
from decimal import Decimal


class BaseModel:
    """Base model for all database entities"""
    
    def __init__(self):
        self.id = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        raise NotImplementedError
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create model from dictionary"""
        raise NotImplementedError


class AccountModel(BaseModel):
    """Account database model"""
    
    def __init__(
        self,
        code: str,
        name: str,
        account_type: str,
        balance: Decimal = Decimal('0'),
        currency: str = 'USD',
        description: str = ''
    ):
        super().__init__()
        self.code = code
        self.name = name
        self.account_type = account_type
        self.balance = Decimal(str(balance))
        self.currency = currency
        self.description = description
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'account_type': self.account_type,
            'balance': str(self.balance),
            'currency': self.currency,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class JournalEntryModel(BaseModel):
    """Journal entry database model"""
    
    def __init__(
        self,
        number: str,
        description: str,
        entry_date: datetime = None
    ):
        super().__init__()
        self.number = number
        self.description = description
        self.entry_date = entry_date or datetime.now()
        self.debits = []
        self.credits = []
        self.posted = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'description': self.description,
            'entry_date': self.entry_date.isoformat(),
            'debits': self.debits,
            'credits': self.credits,
            'posted': self.posted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class InvoiceModel(BaseModel):
    """Invoice database model"""
    
    def __init__(
        self,
        number: str,
        customer: str,
        invoice_date: datetime = None
    ):
        super().__init__()
        self.number = number
        self.customer = customer
        self.invoice_date = invoice_date or datetime.now()
        self.items = []
        self.subtotal = Decimal('0')
        self.tax_total = Decimal('0')
        self.total = Decimal('0')
        self.status = 'draft'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'customer': self.customer,
            'invoice_date': self.invoice_date.isoformat(),
            'items': self.items,
            'subtotal': str(self.subtotal),
            'tax_total': str(self.tax_total),
            'total': str(self.total),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class TransactionModel(BaseModel):
    """Transaction database model"""
    
    def __init__(
        self,
        account_code: str,
        transaction_type: str,
        amount: Decimal,
        transaction_date: datetime = None,
        description: str = ''
    ):
        super().__init__()
        self.account_code = account_code
        self.transaction_type = transaction_type
        self.amount = Decimal(str(amount))
        self.transaction_date = transaction_date or datetime.now()
        self.description = description
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'account_code': self.account_code,
            'transaction_type': self.transaction_type,
            'amount': str(self.amount),
            'transaction_date': self.transaction_date.isoformat(),
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
