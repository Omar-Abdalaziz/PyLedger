"""
PyLedger - Professional Accounting Library for Python

A comprehensive accounting library for building:
- Accounting systems
- Invoice management systems
- ERP solutions
- Expense management systems
- Financial systems

Features:
- General ledger management
- Journal entries with automatic balancing
- Invoice and payment tracking
- Tax calculation (VAT, GST, etc.)
- Multi-currency support
- Financial reports (Balance Sheet, Income Statement, Cash Flow)
- Database support (SQLite, PostgreSQL, MySQL)
- Data validation and error handling
"""

from pyledger.core import (
    Account,
    CashAccount,
    GLAccount,
    Transaction,
    JournalEntry,
    AlreadyPostedError,
    Ledger,
    SequenceService,
    ImmutableTransaction,
    AuditEntry,
    AuditTrail,
    ClosingEngine,
    User,
    Role,
    Permission,
    SecurityManager,
    WorkflowEntry,
    WorkflowEngine,
    EntryStatus,
    Contract,
    ContractManager,
    ContractStatus,
    ContractType,
    Note,
    NoteManager,
)

from pyledger.accounting import (
    Tax,
    TaxCalculator,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    PaymentReceiver,
    FixedAsset,
    DepreciationMethod,
    DepreciationEngine,
    InventoryItem,
    InventoryManager,
    Customer,
    Supplier,
    ReceivableAging,
    PayableAging,
    Budget,
    BudgetVsActual,
    BudgetControl,
    BudgetExceededError,
    ConsolidationEngine,
    ConsolidatedReport,
    VATReturn,
    CorporateTaxReport,
)

from pyledger.reports import (
    BaseReport,
    FinancialPeriod,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    EquityStatement,
    ComparativeIncomeStatement,
    ComparativeBalanceSheet,
    FinancialRatios,
)

from pyledger.utils import (
    validate_account_code,
    validate_account_type,
    validate_amount,
    validate_currency,
    validate_currency_strict,
    validate_tax_rate,
    validate_date,
    format_amount,
    SUPPORTED_CURRENCIES,
    CurrencyConverter,
    Money,
    Formatter,
)

from pyledger.database import (
    AccountModel,
    JournalEntryModel,
    InvoiceModel,
    TransactionModel,
    InMemoryRepository,
    SQLiteConnection,
    SqlAlchemyLedgerStore,
)

from pyledger.business import (
    BusinessEngine,
    SmartChartOfAccounts,
)

from pyledger.pdf import (
    PDFEngine,
    CompanyInfo,
)

from pyledger.exceptions import (
    PyLedgerException,
    AccountNotFoundError,
    UnbalancedEntryError,
    InvalidAccountTypeError,
    InsufficientBalanceError,
    DuplicateAccountError,
    InvalidCurrencyError,
    InvalidTaxRateError,
    InvoiceNotFoundError,
    InvalidInvoiceStatusError,
)

from pyledger.config import config, Config

__version__ = '2.1.0'
__author__ = 'Omar Abd Al-Aziz'
__copyright__ = 'Copyright (c) 2026 Omar Abd Al-Aziz'
__description__ = 'Professional Accounting Library for Python'


class PyLedger(BusinessEngine):
    """
    Ultra-high-level facade for non-accountant programmers.
    
    Usage:
        app = PyLedger(company="My Business", currency="USD")
        app.sell(...)
        app.balance_sheet()
    """
    pass

__all__ = [
    # Core
    'Account',
    'CashAccount',
    'GLAccount',
    'Transaction',
    'JournalEntry',
    'AlreadyPostedError',
    'Ledger',
    'SequenceService',
    'ImmutableTransaction',
    'AuditEntry',
    'AuditTrail',
    'ClosingEngine',
    'User',
    'Role',
    'Permission',
    'SecurityManager',
    'WorkflowEntry',
    'WorkflowEngine',
    'EntryStatus',
    'Contract',
    'ContractManager',
    'ContractStatus',
    'ContractType',
    'Note',
    'NoteManager',
    
    # Accounting
    'Tax',
    'TaxCalculator',
    'Invoice',
    'InvoiceItem',
    'InvoiceStatus',
    'Payment',
    'PaymentMethod',
    'PaymentStatus',
    'PaymentReceiver',
    'FixedAsset',
    'DepreciationMethod',
    'DepreciationEngine',
    'InventoryItem',
    'InventoryManager',
    'Customer',
    'Supplier',
    'ReceivableAging',
    'PayableAging',
    'Budget',
    'BudgetVsActual',
    'BudgetControl',
    'BudgetExceededError',
    'ConsolidationEngine',
    'ConsolidatedReport',
    'VATReturn',
    'CorporateTaxReport',
    
    # Reports
    'BaseReport',
    'FinancialPeriod',
    'IncomeStatement',
    'BalanceSheet',
    'CashFlowStatement',
    'EquityStatement',
    'ComparativeIncomeStatement',
    'ComparativeBalanceSheet',
    'FinancialRatios',
    
    # Utils
    'validate_account_code',
    'validate_account_type',
    'validate_amount',
    'validate_currency',
    'validate_currency_strict',
    'validate_tax_rate',
    'validate_date',
    'format_amount',
    'SUPPORTED_CURRENCIES',
    'CurrencyConverter',
    'Money',
    'Formatter',
    
    # Config
    'config',
    'Config',
    
    # Database
    'AccountModel',
    'JournalEntryModel',
    'InvoiceModel',
    'TransactionModel',
    'InMemoryRepository',
    'SQLiteConnection',
    'SqlAlchemyLedgerStore',
    
    # Business
    'BusinessEngine',
    'SmartChartOfAccounts',

    # PDF
    'PDFEngine',
    'CompanyInfo',

    # Exceptions
    'PyLedgerException',
    'AccountNotFoundError',
    'UnbalancedEntryError',
    'InvalidAccountTypeError',
    'InsufficientBalanceError',
    'DuplicateAccountError',
    'InvalidCurrencyError',
    'InvalidTaxRateError',
    'InvoiceNotFoundError',
    'InvalidInvoiceStatusError',
]
