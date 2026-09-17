# PyLedger Examples 📚

Collection of practical examples for using PyLedger library.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Invoicing System](#invoicing-system)
3. [Multi-Currency Operations](#multi-currency-operations)
4. [Tax Calculations](#tax-calculations)
5. [Advanced Reports](#advanced-reports)
6. [Complete ERP Example](#complete-erp-example)

---

## Basic Usage

### Simple Accounting Entry

```python
from pyledger import Ledger, Account, JournalEntry

# Create ledger
ledger = Ledger("My Business", currency="USD")

# Create accounts
cash = Account("Cash", "asset", "1000")
bank = Account("Bank Account", "asset", "1010")
sales = Account("Sales Revenue", "income", "4000")

# Add accounts to ledger
ledger.add_account(cash)
ledger.add_account(bank)
ledger.add_account(sales)

# Create journal entry (cash receipt from sale)
entry = JournalEntry("Daily sales")
entry.add_debit(cash, 1000, "Cash sales today")
entry.add_credit(sales, 1000, "Revenue recognized")

# Post entry to ledger
entry.post()
ledger.record_entry(entry)

# Check trial balance
trial_balance = ledger.get_trial_balance()
print(trial_balance)
```

---

## Invoicing System

### Create and Manage Invoices

```python
from pyledger import Invoice, Tax, PaymentReceiver
from datetime import datetime, timedelta

# Create invoice
invoice = Invoice(
    customer="Ahmed Trading Company",
    currency="SAR"
)

# Add line items
invoice.add_item("Office Supplies", quantity=5, unit_price=100)
invoice.add_item("Stationery Pack", quantity=2, unit_price=250)
invoice.add_item("Consulting Services", quantity=10, unit_price=500)

# Calculate subtotal
invoice.calculate_total()

# Add VAT (15%)
vat = Tax("VAT", 15)
invoice.add_tax(vat)

# Set due date
invoice.due_date = datetime.now() + timedelta(days=30)

# Issue invoice
invoice.issue()

# Record payment
invoice.pay(2500, method='bank_transfer')
invoice.pay(750, method='cash')

# Print invoice
print(invoice)

# Get invoice details
print(f"Status: {invoice.get_status()}")
print(f"Remaining Balance: {invoice.get_remaining_balance()}")
```

### Payment Management

```python
from pyledger import PaymentReceiver

receiver = PaymentReceiver()

# Record payments
payment1 = receiver.receive_payment(500, method='cash')
payment2 = receiver.receive_payment(300, method='bank_transfer')
payment3 = receiver.receive_payment(200, method='check')

# Get statistics
total = receiver.get_total_received()
cash_payments = receiver.get_payments_by_method('cash')

print(f"Total Received: {total}")
print(f"Cash Payments: {len(cash_payments)}")
```

---

## Multi-Currency Operations

### Currency Conversion

```python
from pyledger import CurrencyConverter, Money

converter = CurrencyConverter()

# Convert currency
amount_usd = 100
amount_eur = converter.convert(amount_usd, 'USD', 'EUR')
amount_sar = converter.convert(amount_usd, 'USD', 'SAR')

print(f"${amount_usd} USD = €{amount_eur} EUR")
print(f"${amount_usd} USD = ﷼{amount_sar} SAR")

# Update exchange rate
converter.update_rate('GBP', 0.79)

# Work with Money objects
money1 = Money(100, 'USD')
money2 = Money(50, 'USD')

total = money1 + money2
print(f"Total: {total}")

# Get currency symbol
print(converter.get_symbol('SAR'))  # ﷼
```

---

## Tax Calculations

### Different Tax Types

```python
from pyledger import Tax, TaxCalculator

# Simple tax calculation
vat = Tax("VAT", 15)
base_amount = 1000

tax_amount = vat.calculate(base_amount)
total = vat.calculate_total(base_amount)

print(f"Base: {base_amount}")
print(f"VAT (15%): {tax_amount}")
print(f"Total: {total}")

# Multiple taxes
calculator = TaxCalculator()
calculator.add_tax("VAT", 15)
calculator.add_tax("Municipal Tax", 5)

result = calculator.calculate_all(1000)
print(result)
# {
#     'base': 1000,
#     'taxes': {
#         'VAT': {'rate': 15, 'amount': 150},
#         'Municipal Tax': {'rate': 5, 'amount': 50}
#     },
#     'total_tax': 200,
#     'total': 1200
# }

# Calculate base from total (reverse calculation)
result = Tax.reverse_calculate(1150, 15)
# Finds the base amount from total including tax
print(result['base'])  # 1000
```

---

## Advanced Reports

### Complete Financial Reporting

```python
from pyledger import (
    Ledger, Account, JournalEntry,
    IncomeStatement, BalanceSheet, CashFlowStatement
)

# Setup complete ledger
ledger = Ledger("Financial Co.", currency="USD")

# Assets
cash = Account("Cash", "asset", "1000")
accounts_receivable = Account("AR", "asset", "1100")
equipment = Account("Equipment", "asset", "1200")

# Liabilities
accounts_payable = Account("AP", "liability", "2000")
short_term_debt = Account("ST Debt", "liability", "2100")

# Equity
capital = Account("Capital", "equity", "3000")
retained_earnings = Account("Retained Earnings", "equity", "3100")

# Income
sales = Account("Sales", "income", "4000")
service_revenue = Account("Services", "income", "4100")

# Expenses
cost_of_goods = Account("COGS", "expense", "5000")
salaries = Account("Salaries", "expense", "5100")
rent = Account("Rent", "expense", "5200")
utilities = Account("Utilities", "expense", "5300")

# Add all accounts
for acc in [cash, accounts_receivable, equipment, accounts_payable,
            short_term_debt, capital, retained_earnings, sales, 
            service_revenue, cost_of_goods, salaries, rent, utilities]:
    ledger.add_account(acc)

# Record transactions
# Opening balance
entry1 = JournalEntry("Opening Balance")
entry1.add_debit(cash, 50000)
entry1.add_debit(equipment, 100000)
entry1.add_credit(capital, 150000)
entry1.post()
ledger.record_entry(entry1)

# Sales transaction
entry2 = JournalEntry("Sales - January")
entry2.add_debit(cash, 25000)
entry2.add_credit(sales, 25000)
entry2.post()
ledger.record_entry(entry2)

# Service revenue
entry3 = JournalEntry("Services - January")
entry3.add_debit(accounts_receivable, 15000)
entry3.add_credit(service_revenue, 15000)
entry3.post()
ledger.record_entry(entry3)

# Expenses
expense_entry = JournalEntry("Monthly Expenses")
expense_entry.add_debit(salaries, 10000, "January salaries")
expense_entry.add_debit(rent, 5000, "January rent")
expense_entry.add_debit(utilities, 1000, "Utilities")
expense_entry.add_credit(cash, 16000)
expense_entry.post()
ledger.record_entry(expense_entry)

# COGS
cogs_entry = JournalEntry("Cost of Goods Sold")
cogs_entry.add_debit(cost_of_goods, 10000)
cogs_entry.add_credit(cash, 10000)
cogs_entry.post()
ledger.record_entry(cogs_entry)

# Generate reports
print("=" * 70)
income_stmt = IncomeStatement(ledger)
print(income_stmt)

print("\n" + "=" * 70)
balance_sheet = BalanceSheet(ledger)
print(balance_sheet)

print("\n" + "=" * 70)
cash_flow = CashFlowStatement(ledger)
result = cash_flow.generate()
print(f"Cash Flow Statement - {result['generated_date']}")
```

---

## Complete ERP Example

### Full Accounting System

```python
from pyledger import *
from datetime import datetime, timedelta

class SimpleERP:
    """Simple ERP system using PyLedger"""
    
    def __init__(self, company_name, currency="USD"):
        self.ledger = Ledger(company_name, currency)
        self.invoices = []
        self.setup_chart_of_accounts()
    
    def setup_chart_of_accounts(self):
        """Setup standard chart of accounts"""
        
        # Assets
        accounts = {
            '1000': ('Cash', 'asset'),
            '1010': ('Bank', 'asset'),
            '1100': ('Accounts Receivable', 'asset'),
            
            # Liabilities
            '2000': ('Accounts Payable', 'liability'),
            '2100': ('Loans Payable', 'liability'),
            
            # Equity
            '3000': ('Owner Capital', 'equity'),
            '3100': ('Retained Earnings', 'equity'),
            
            # Income
            '4000': ('Product Sales', 'income'),
            '4100': ('Service Revenue', 'income'),
            
            # Expenses
            '5000': ('Cost of Goods', 'expense'),
            '5100': ('Salaries', 'expense'),
            '5200': ('Rent', 'expense'),
        }
        
        for code, (name, acc_type) in accounts.items():
            account = Account(name, acc_type, code, self.ledger.currency)
            self.ledger.add_account(account)
    
    def record_sale(self, amount, is_cash=True):
        """Record a sale"""
        entry = JournalEntry(f"Sale - {datetime.now().strftime('%Y-%m-%d')}")
        
        if is_cash:
            entry.add_debit(self.ledger.get_account('1000'), amount)
        else:
            entry.add_debit(self.ledger.get_account('1100'), amount)
        
        entry.add_credit(self.ledger.get_account('4000'), amount)
        entry.post()
        self.ledger.record_entry(entry)
    
    def record_expense(self, expense_account, amount, description=""):
        """Record an expense"""
        entry = JournalEntry(f"Expense - {description}")
        entry.add_debit(self.ledger.get_account(expense_account), amount)
        entry.add_credit(self.ledger.get_account('1000'), amount)
        entry.post()
        self.ledger.record_entry(entry)
    
    def create_invoice(self, customer, items):
        """Create and track invoice"""
        invoice = Invoice(customer, currency=self.ledger.currency)
        
        for item in items:
            invoice.add_item(
                item['name'],
                item['quantity'],
                item['unit_price']
            )
        
        self.invoices.append(invoice)
        return invoice
    
    def get_financial_summary(self):
        """Get financial summary"""
        return {
            'total_assets': self.ledger.get_total_assets(),
            'total_liabilities': self.ledger.get_total_liabilities(),
            'total_equity': self.ledger.get_total_equity(),
            'total_income': self.ledger.get_total_income(),
            'total_expenses': self.ledger.get_total_expenses(),
        }

# Usage
erp = SimpleERP("Tech Solutions Inc", "USD")

# Record initial capital
entry = JournalEntry("Opening Balance")
entry.add_debit(erp.ledger.get_account('1000'), 100000)
entry.add_credit(erp.ledger.get_account('3000'), 100000)
entry.post()
erp.ledger.record_entry(entry)

# Record sales
erp.record_sale(5000, is_cash=True)
erp.record_sale(3000, is_cash=False)

# Record expenses
erp.record_expense('5100', 2000, 'Monthly Salaries')
erp.record_expense('5200', 1000, 'Office Rent')

# Create invoice
invoice = erp.create_invoice(
    "ABC Trading",
    [
        {'name': 'Product A', 'quantity': 2, 'unit_price': 500},
        {'name': 'Product B', 'quantity': 1, 'unit_price': 1000},
    ]
)
invoice.issue()
invoice.pay(1500)

# Get summary
summary = erp.get_financial_summary()
print(f"Total Assets: ${summary['total_assets']}")
print(f"Total Liabilities: ${summary['total_liabilities']}")
print(f"Total Equity: ${summary['total_equity']}")

# Generate financial reports
print("\n" + "=" * 70)
bs = BalanceSheet(erp.ledger)
print(bs)

print("\n" + "=" * 70)
is_stmt = IncomeStatement(erp.ledger)
print(is_stmt)
```

---

## Best Practices

1. **Always validate inputs** - Use provided validators
2. **Handle exceptions** - Catch specific PyLedger exceptions
3. **Journal entries must balance** - Always ensure debits equal credits
4. **Use meaningful account codes** - Follow standardized numbering
5. **Record transactions immediately** - Don't delay posting entries
6. **Keep audit trail** - All transactions are tracked
7. **Regular reconciliation** - Verify trial balance regularly

---

Happy accounting! 📊
