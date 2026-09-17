"""
PyLedger Database Module __init__
"""

from pyledger.database.models import (
    BaseModel,
    AccountModel,
    JournalEntryModel,
    InvoiceModel,
    TransactionModel,
)
from pyledger.database.repository import (
    Repository,
    InMemoryRepository,
    DatabaseConnection,
    SQLiteConnection,
)

try:
    from pyledger.database.uow import SqlAlchemyLedgerStore
    _HAS_SQL_STORE = True
except Exception:
    SqlAlchemyLedgerStore = None
    _HAS_SQL_STORE = False

__all__ = [
    'BaseModel',
    'AccountModel',
    'JournalEntryModel',
    'InvoiceModel',
    'TransactionModel',
    'Repository',
    'InMemoryRepository',
    'DatabaseConnection',
    'SQLiteConnection',
    'SqlAlchemyLedgerStore',
]
