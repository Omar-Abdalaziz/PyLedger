# PyLedger Quick Reference Guide

## Installation

```bash
pip install pyledger
```

Or from source:
```bash
git clone https://github.com/yourusername/pyledger.git
cd pyledger
pip install -e .
```

## Quick Start

```python
from pyledger import Ledger, Account, JournalEntry

# Create ledger
ledger = Ledger("My Business")

# Create accounts
cash = Account("Cash", "asset", "1000")
sales = Account("Sales", "income", "4000")

# Add to ledger
ledger.add_account(cash)
ledger.add_account(sales)

# Record transaction
entry = JournalEntry("First sale")
entry.add_debit(cash, 1000)
entry.add_credit(sales, 1000)
entry.post()

ledger.record_entry(entry)
```

## Core Classes

### Account
```python
Account(name, account_type, code, currency='USD', description='')

# Methods
account.deposit(amount, description)
account.withdraw(amount, description)
account.get_balance()
account.get_transactions()
```

**Account Types:** asset, liability, equity, income, expense

### JournalEntry
```python
JournalEntry(description, date=None, entry_number=None)

# Methods
entry.add_debit(account, amount, description)
entry.add_credit(account, amount, description)
entry.is_balanced()
entry.validate()
entry.post()
```

### Ledger
```python
Ledger(name='Ledger', currency='USD')

# Methods
ledger.add_account(account)
ledger.get_account(code)
ledger.transfer(from_account, to_account, amount)
ledger.record_entry(journal_entry)
ledger.get_trial_balance()
ledger.get_total_assets()
ledger.get_total_liabilities()
ledger.get_total_equity()
```

### Invoice
```python
Invoice(customer, invoice_number=None, date=None, currency='USD')

# Methods
invoice.add_item(description, quantity, unit_price)
invoice.add_tax(tax)
invoice.calculate_total()
invoice.pay(amount, method)
invoice.issue()
invoice.get_remaining_balance()
```

### Tax
```python
Tax(name, rate)  # rate as percentage

# Static methods
Tax.calculate_vat(amount, rate)
Tax.reverse_calculate(total_with_tax, rate)
```

### Payment
```python
Payment(amount, method='cash', reference=None)

# Methods
payment.process()
payment.fail(reason)
payment.refund()
```

## Reports

```python
from pyledger import IncomeStatement, BalanceSheet, CashFlowStatement

# Income Statement (P&L)
stmt = IncomeStatement(ledger)
stmt.generate()
print(stmt)

# Balance Sheet
bs = BalanceSheet(ledger)
bs.generate()
print(bs)

# Cash Flow
cf = CashFlowStatement(ledger)
cf.generate()
```

## Utilities

### Validation
```python
from pyledger import (
    validate_account_code,
    validate_account_type,
    validate_amount,
    validate_currency,
    validate_tax_rate
)
```

### Currency
```python
from pyledger import Money, CurrencyConverter

# Money operations
money = Money(100, 'USD')
result = money + Money(50, 'USD')

# Currency conversion
converter = CurrencyConverter()
amount_eur = converter.convert(100, 'USD', 'EUR')
converter.update_rate('USD', 1.0)
```

### Formatting
```python
from pyledger import Formatter

formatter = Formatter()
formatted = formatter.format_amount(1000, '$')
```

## Error Handling

```python
from pyledger import (
    AccountNotFoundError,
    UnbalancedEntryError,
    InsufficientBalanceError,
    DuplicateAccountError,
    InvalidCurrencyError,
    InvalidTaxRateError,
)

try:
    ledger.get_account("INVALID")
except AccountNotFoundError:
    print("Account not found")

try:
    account.withdraw(10000)
except InsufficientBalanceError:
    print("Insufficient balance")

try:
    entry.post()
except UnbalancedEntryError:
    print("Entry not balanced")
```

## Supported Currencies

USD, EUR, GBP, SAR, AED, EGP, JOD, KWD

## Configuration

See `config.py` for configurable settings:
- Database settings
- Default currency
- Tax rates
- Date formats
- Validation rules

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest test_pyledger.py -v
```

## Full Example

See `example.py` for a complete working example:
```bash
python example.py
```

## Database Integration

### SQLite (Default)
```python
from pyledger import SQLiteConnection

db = SQLiteConnection('ledger.db')
db.connect()
db.create_tables()
```

### In-Memory Repository
```python
from pyledger import InMemoryRepository

repo = InMemoryRepository()
```

## Common Patterns

### Account Balance Checking
```python
cash = ledger.get_account("1000-CASH")
balance = cash.get_balance()
```

### Multi-Currency Transactions
```python
from pyledger import CurrencyConverter

converter = CurrencyConverter()
amount_in_eur = converter.convert(1000, 'USD', 'EUR')
```

### Tax Calculation on Invoice
```python
vat = Tax("VAT", 15)
invoice.add_tax(vat)
total = invoice.calculate_total()
```

### Generate Multiple Reports
```python
income_stmt = IncomeStatement(ledger)
balance_sheet = BalanceSheet(ledger)
cash_flow = CashFlowStatement(ledger)

# Get all data
income_data = income_stmt.generate()
balance_data = balance_sheet.generate()
cash_flow_data = cash_flow.generate()
```

## Best Practices

1. ✅ Always create accounts before using them
2. ✅ Ensure journal entries are balanced before posting
3. ✅ Use meaningful account codes
4. ✅ Validate inputs before processing
5. ✅ Record transactions immediately
6. ✅ Handle exceptions appropriately
7. ✅ Generate reports regularly for verification
8. ✅ Keep detailed descriptions for audit trails

## Troubleshooting

**UnbalancedEntryError**: Ensure debits equal credits
```python
if entry.is_balanced():
    entry.post()
```

**AccountNotFoundError**: Check account code
```python
if ledger.account_exists("1000-CASH"):
    account = ledger.get_account("1000-CASH")
```

**InsufficientBalanceError**: Check available balance
```python
if account.get_balance() >= amount:
    account.withdraw(amount)
```

---

For more details, see README.md and EXAMPLES.md
