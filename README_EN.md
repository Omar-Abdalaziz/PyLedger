# 📊 PyLedger - Professional Accounting Library for Python

## Overview

**PyLedger** is a professional and comprehensive Python library for building accounting and financial systems. It provides everything you need to create:

- 📊 **Advanced Accounting Systems**
- 📄 **Invoice Management Programs**
- 🏢 **Simple ERP Solutions**
- 💸 **Expense Management Applications**
- 📈 **Specialized Financial Systems**

**Without needing to write accounting logic from scratch!**

---

## ✨ Key Features

### 1. 📝 General Ledger Management
- Multiple account types with full support
- Complete ledger system
- Automatic transaction tracking
- Automatic balance verification

### 2. 📋 Journal Entries
- Recording accounting transactions
- Automatic balance verification
- Full transaction history
- Safe posting to ledger

### 3. 📄 Invoice Management
- Create and manage invoices
- Easy payment tracking
- Support for multiple taxes
- Handle paid balances

### 4. 💰 Tax Management
- VAT (Value Added Tax) calculation
- Multiple taxes in a single invoice
- Reverse tax calculations
- Flexible tax standards

### 5. 💱 Multi-Currency Support
- Support for 8 global currencies
- Easy currency conversion
- Safe mathematical operations
- Updateable exchange rates

### 6. 📊 Financial Reports
- **Income Statement** (Profit & Loss)
- **Balance Sheet**
- **Cash Flow Statement**
- **Trial Balance**

### 7. 🗄️ Database Support
- SQLite integration
- In-memory repository implementation
- Repository pattern for flexibility
- PostgreSQL & MySQL ready

### 8. ✅ Comprehensive Validation
- Account code format validation
- Amount validation
- Currency validation
- Tax rate validation

### 9. 🔒 Error Handling
- 10 custom exceptions
- Clear error messages
- Balance verification
- Protection against accounting errors

### 10. 🛠️ Helper Tools
- Formatter utility
- Validator functions
- Currency converter
- Money class for safe operations

---

## 🏗️ Project Structure

```
pyledger/
├── core/                          # Core Components
│   ├── __init__.py
│   ├── account.py                 # Account Management
│   ├── ledger.py                  # General Ledger
│   ├── transaction.py             # Transactions
│   └── journal.py                 # Journal Entries
│
├── accounting/                    # Accounting Operations
│   ├── __init__.py
│   ├── invoice.py                 # Invoice Management
│   ├── tax.py                     # Tax Calculation
│   └── payment.py                 # Payment Processing
│
├── reports/                       # Financial Reports
│   ├── __init__.py
│   ├── balance_sheet.py           # Balance Sheet, Income Statement, Cash Flow
│   ├── income_statement.py        # Income Statement
│   └── cash_flow.py               # Cash Flow Statement
│
├── database/                      # Database Layer
│   ├── __init__.py
│   ├── models.py                  # Data Models
│   └── repository.py              # Repository Pattern
│
├── utils/                         # Helper Tools
│   ├── __init__.py
│   ├── validators.py              # Validation Functions
│   ├── currency.py                # Currency Management
│   └── formatter.py               # Data Formatting
│
└── exceptions/                    # Custom Exceptions
    ├── __init__.py
    └── errors.py                  # Exception Definitions
```

---

## 🚀 Quick Start

### Installation

```bash
pip install pyledger
```

Or from source:
```bash
git clone <repository-url>
cd pyledger
pip install -e .
```

### Simple Example

```python
from pyledger import Ledger, Account, JournalEntry

# Create ledger
ledger = Ledger("My Business", currency="USD")

# Create accounts
cash = Account("Cash", "asset", "1000")
sales = Account("Sales", "income", "4000")

# Add accounts
ledger.add_account(cash)
ledger.add_account(sales)

# Record transaction
entry = JournalEntry("Daily sales")
entry.add_debit(cash, 1000)
entry.add_credit(sales, 1000)
entry.post()

ledger.record_entry(entry)

# Get trial balance
print(ledger.get_trial_balance())
```

---

## 📚 Core Classes

### 1️⃣ Account

Represents an accounting account.

```python
account = Account(
    name="Cash",
    account_type="asset",
    code="1000",
    currency="USD",
    description="Company cash account"
)

# Operations
account.deposit(1000, "Cash deposit")
account.withdraw(500, "Cash withdrawal")
balance = account.get_balance()
```

**Account Types:**
- `asset` 💰 - Assets (cash, investments, property)
- `liability` 📊 - Liabilities (loans, accounts payable)
- `equity` 📈 - Owner's equity (capital)
- `income` 💵 - Income/Revenue (sales, interest)
- `expense` 📉 - Expenses (salaries, rent)

### 2️⃣ Ledger

Manages all accounts and transactions.

```python
ledger = Ledger("Main Ledger", currency="USD")

# Add account
ledger.add_account(account)

# Get account
account = ledger.get_account("1000")

# Transfer between accounts
ledger.transfer(from_account, to_account, 500)

# Get trial balance
trial_balance = ledger.get_trial_balance()

# Financial summaries
total_assets = ledger.get_total_assets()
total_expenses = ledger.get_total_expenses()
```

### 3️⃣ JournalEntry

Records a balanced accounting transaction.

```python
entry = JournalEntry("Sale transaction")

# Add debit (Debit side)
entry.add_debit(cash, 1000, "Cash receipt")

# Add credit (Credit side)
entry.add_credit(sales, 1000, "Revenue recognized")

# Verify balance
if entry.is_balanced():
    entry.post()

# Record in ledger
ledger.record_entry(entry)
```

### 4️⃣ Invoice

Complete invoice management.

```python
invoice = Invoice("Customer Name", currency="USD")

# Add items
invoice.add_item("Product", quantity=2, unit_price=100)
invoice.add_item("Service", quantity=1, unit_price=500)

# Add tax
vat = Tax("VAT", 15)
invoice.add_tax(vat)

# Issue and manage
invoice.issue()
invoice.pay(amount=2000, method='bank_transfer')

# Get information
print(f"Total: {invoice.total}")
print(f"Paid: {invoice.paid_amount}")
print(f"Remaining: {invoice.get_remaining_balance()}")
```

### 5️⃣ Tax

Tax calculation and management.

```python
# Create tax
vat = Tax("VAT", 15)

# Calculate tax amount
tax_amount = vat.calculate(1000)  # Returns 150

# Calculate total with tax
total = vat.calculate_total(1000)  # Returns 1150

# Calculate VAT directly
result = Tax.calculate_vat(1000, 15)
# {'base': 1000, 'vat_amount': 150, 'total': 1150}

# Reverse calculation
result = Tax.reverse_calculate(1150, 15)
# {'base': 1000, 'tax_amount': 150, 'total': 1150}
```

### 6️⃣ Reports

Generate financial statements.

```python
from pyledger import IncomeStatement, BalanceSheet

# Income Statement
income_stmt = IncomeStatement(ledger)
income_data = income_stmt.generate()
print(income_stmt)

# Balance Sheet
balance_sheet = BalanceSheet(ledger)
balance_data = balance_sheet.generate()
print(balance_sheet)
```

---

## 💡 Practical Examples

### Example 1: Simple Accounting System

```python
from pyledger import *

# Create ledger
ledger = Ledger("Example Company", currency="USD")

# Create accounts
accounts = {
    "1000": ("Cash", "asset"),
    "4000": ("Sales", "income"),
    "5000": ("Expenses", "expense"),
    "3000": ("Capital", "equity"),
}

for code, (name, acc_type) in accounts.items():
    account = Account(name, acc_type, code)
    ledger.add_account(account)

# Opening balance
opening = JournalEntry("Opening Balance")
opening.add_debit(ledger.get_account("1000"), 100000)
opening.add_credit(ledger.get_account("3000"), 100000)
opening.post()
ledger.record_entry(opening)

# Record sales
sales = JournalEntry("Sales")
sales.add_debit(ledger.get_account("1000"), 50000)
sales.add_credit(ledger.get_account("4000"), 50000)
sales.post()
ledger.record_entry(sales)

# Record expenses
expense = JournalEntry("Expenses")
expense.add_debit(ledger.get_account("5000"), 10000)
expense.add_credit(ledger.get_account("1000"), 10000)
expense.post()
ledger.record_entry(expense)
```

### Example 2: Invoice System

```python
# Create invoice
invoice = Invoice("ABC Trading Company", currency="USD")

# Add items
items = [
    ("Consulting", 10, 500),
    ("Software", 1, 5000),
    ("Support", 5, 200),
]

for item_name, qty, price in items:
    invoice.add_item(item_name, qty, price)

# Add tax
vat = Tax("VAT", 15)
invoice.add_tax(vat)

# Process payments
invoice.issue()
invoice.pay(5000, method='bank_transfer')
invoice.pay(3000, method='check')

# Get details
print(f"Total: {invoice.total}")
print(f"Paid: {invoice.paid_amount}")
print(f"Remaining: {invoice.get_remaining_balance()}")
```

### Example 3: Multi-Currency Operations

```python
from pyledger import Money, CurrencyConverter

# Work with Money
money1 = Money(100, 'USD')
money2 = Money(50, 'USD')
total = money1 + money2
print(f"Total: {total}")

# Currency conversion
converter = CurrencyConverter()
amount_eur = converter.convert(100, 'USD', 'EUR')
amount_gbp = converter.convert(100, 'USD', 'GBP')

# Update exchange rates
converter.update_rate('GBP', 0.79)
```

---

## 🧪 Testing

```bash
# Run example
python example.py

# Run tests
python test_pyledger.py

# Quick test
python -c "from pyledger import *; print('✓ Library works!')"
```

---

## 📖 Documentation

| File | Size | Purpose |
|------|------|---------|
| **README_EN.md** | This file | Complete documentation |
| **QUICKSTART.md** | 200+ lines | Quick start guide |
| **EXAMPLES.md** | 600+ lines | Advanced examples |
| **README.md** | 400+ lines | Arabic documentation |

---

## 🔒 Error Handling

```python
from pyledger import *

try:
    # Try to get non-existent account
    account = ledger.get_account("INVALID")
except AccountNotFoundError:
    print("Account not found")

try:
    # Try to withdraw more than balance
    account.withdraw(10000)
except InsufficientBalanceError:
    print("Insufficient balance")

try:
    # Unbalanced entry
    entry = JournalEntry("Transaction")
    entry.add_debit(account1, 100)
    entry.add_credit(account2, 50)  # Not equal!
    entry.post()
except UnbalancedEntryError:
    print("Entry is not balanced")
```

## 🌍 Supported Currencies

| Code | Currency | Countries |
|------|----------|-----------|
| USD | US Dollar | United States |
| EUR | Euro | Europe |
| GBP | British Pound | United Kingdom |
| SAR | Saudi Riyal | Saudi Arabia |
| AED | UAE Dirham | United Arab Emirates |
| EGP | Egyptian Pound | Egypt |
| JOD | Jordanian Dinar | Jordan |
| KWD | Kuwaiti Dinar | Kuwait |

---

## ✅ Best Practices

1. ✓ Validate data before input
2. ✓ Ensure journal entries are balanced before posting
3. ✓ Use meaningful account codes
4. ✓ Record transactions immediately
5. ✓ Review financial reports regularly
6. ✓ Maintain complete audit trail
7. ✓ Use descriptive transaction names

---

## 📋 Custom Exceptions

```python
PyLedgerException              # Base exception
AccountNotFoundError           # Account not found
UnbalancedEntryError           # Journal entry not balanced
InvalidAccountTypeError        # Invalid account type
InsufficientBalanceError       # Insufficient balance
DuplicateAccountError          # Duplicate account code
InvalidCurrencyError           # Invalid currency
InvalidTaxRateError            # Invalid tax rate
InvoiceNotFoundError           # Invoice not found
InvalidInvoiceStatusError      # Invalid invoice status
```

---

## 🎯 Use Cases

This library is perfect for:
- ✅ Small accounting systems
- ✅ Simple ERP solutions
- ✅ Invoice management systems
- ✅ Financial applications
- ✅ Personal accounting
- ✅ Web applications
- ✅ API development

---

## 🔐 Security

PyLedger implements strict security measures:
- ✅ Decimal arithmetic for financial precision
- ✅ Input validation for all operations
- ✅ Comprehensive error handling
- ✅ Clear and specific exceptions
- ✅ Prevention of unbalanced operations
- ✅ Protection against common accounting errors

---

## 📊 Project Statistics

### Code
```
Total Lines of Code:        3500+
Documentation Lines:        2000+
Test Lines:                  600+
Example Lines:               180+
────────────────────────────────
Total:                      6280+ lines
```

### Content
```
Main Classes:               25+
Exceptions:                 10
Methods & Properties:       150+
Validation Functions:       12
Supported Currencies:        8
```

---

## 📄 License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) and NOTICE files for details.

**Copyright © 2026 Omar Abd Al-Aziz**

You are free to:
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute modifications
- ✅ Use privately

You must:
- ✅ Keep the license
- ✅ Document changes
- ✅ Credit the original author

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the project
2. Create a feature branch
3. Send a Pull Request

---

## 📞 Support

For questions or issues:
- 📧 Email: support@pyledger.dev
- 🐛 GitHub Issues: [Report a bug](https://github.com/yourusername/pyledger/issues)
- 📚 Documentation: [Read the docs](./README.md)

---

## 🚀 Roadmap

- ✅ v1.0.0: Core features (Completed)
- 🔄 v1.1.0: ORM support (In development)
- 📋 v1.2.0: REST API (Planned)
- 📋 v1.3.0: PDF invoices (Planned)
- 📋 v2.0.0: Budget management (Planned)

---

## 💡 Key Highlights

1. **Professional Quality** - Real accounting standards
2. **Secure** - Safe financial data handling
3. **Well Documented** - 2000+ lines of documentation
4. **Fully Tested** - 40+ test cases
5. **Easy to Use** - Simple and clear API
6. **Flexible** - Easy to extend
7. **Global Ready** - Multi-currency support
8. **Open Source** - Apache-2.0 licensed
9. **Maintained** - Active development
10. **Production Ready** - Used in real systems

---

## ✨ What Makes PyLedger Special

- **Zero External Dependencies** - Pure Python implementation
- **Accounting Standards** - Follows real accounting principles
- **Balance Verification** - Automatic balance checking
- **Error Prevention** - Protects against common mistakes
- **Flexible Design** - Works with any database
- **Clean Architecture** - Well-organized code structure
- **Extensive Examples** - Learn by doing
- **Arabic Support** - Full Arabic documentation available

---

## 🎉 Getting Started

1. **Read** the [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. **Run** `python example.py` (2 minutes)
3. **Code** your first example (10 minutes)
4. **Explore** [EXAMPLES.md](EXAMPLES.md) (30 minutes)

---

## 📝 Version Info

- **Version:** 1.0.0
- **Released:** March 14, 2026
- **License:** Apache-2.0
- **Author:** Omar Abd Al-Aziz
- **Status:** ✅ Production Ready

---

## 🙏 Acknowledgments

PyLedger is built with care to provide:
- A professional accounting solution
- High-quality code
- Comprehensive documentation
- Excellent user experience

Thank you for using PyLedger! 🎉

---

**Made with ❤️ by Omar Abd Al-Aziz**

**[Arabic Documentation](./README.md) | [Quick Start](./QUICKSTART.md) | [Examples](./EXAMPLES.md)**
