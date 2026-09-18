# PyLedger 📊

### Professional Double-Entry Accounting Library for Python

[![PyPI version](https://img.shields.io/pypi/v/pyledger.svg)](https://pypi.org/project/pyledger/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyledger.svg)](https://pypi.org/project/pyledger/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-214%20passing-brightgreen.svg)](test_pyledger.py)
[![Coverage](https://img.shields.io/badge/coverage-enterprise-blue.svg)](test_pyledger.py)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Build accounting systems, invoicing apps, mini-ERPs and fintech backends — without writing double-entry logic from scratch.**
> Non-accountant friendly: `app.sell(...)` generates correct debit/credit entries for you.

```python
from pyledger import PyLedger

app = PyLedger(company="Acme Corp", currency="USD")
app.add_investment("Owner", 100_000)
app.sell([{"name": "Consulting", "quantity": 10, "price": 500}], customer="C-1")
app.pay_expense("Office rent", 2_000, category="rent")

print(app.balance_sheet().generate()["total_assets"])   # 103000.00
print(app.income_statement().generate()["net_income"])  # 3000.00
```

**Docs:** English here · [العربية](README_AR.md) · [Quickstart](QUICKSTART.md) · [Advanced examples](EXAMPLES.md) · [Changelog](CHANGELOG.md)

---

## Table of Contents

1. [Why PyLedger?](#why-pyledger)
2. [Features](#features)
3. [Installation](#installation)
4. [Quickstart (5 minutes)](#quickstart-5-minutes)
5. [Core concepts](#core-concepts)
6. [API Reference](#api-reference)
   - [6.1 Core — Accounts](#61-core--accounts)
   - [6.2 Core — Transactions & Journal Entries](#62-core--transactions--journal-entries)
   - [6.3 Core — Ledger](#63-core--ledger)
   - [6.4 Core — Numbering](#64-core--numbering)
   - [6.5 Core — Period Closing](#65-core--period-closing)
   - [6.6 Core — Immutable Audit Trail](#66-core--immutable-audit-trail)
   - [6.7 Core — Security & RBAC](#67-core--security--rbac)
   - [6.8 Core — Approval Workflows](#68-core--approval-workflows)
   - [6.9 Core — Contracts & Notes](#69-core--contracts--notes)
   - [6.10 Accounting — Invoices](#610-accounting--invoices)
   - [6.11 Accounting — Tax](#611-accounting--tax)
   - [6.12 Accounting — Payments](#612-accounting--payments)
   - [6.13 Accounting — Fixed Assets & Depreciation](#613-accounting--fixed-assets--depreciation)
   - [6.14 Accounting — Inventory](#614-accounting--inventory)
   - [6.15 Accounting — CRM](#615-accounting--crm)
   - [6.16 Accounting — Aging Reports](#616-accounting--aging-reports)
   - [6.17 Accounting — Budgets & Budget Control](#617-accounting--budgets--budget-control)
   - [6.18 Accounting — Consolidation](#618-accounting--consolidation)
   - [6.19 Accounting — Tax Reports (VAT / Corporate Tax)](#619-accounting--tax-reports-vat--corporate-tax)
   - [6.20 Accounting — Bank Reconciliation](#620-accounting--bank-reconciliation)
   - [6.21 Accounting — Projects](#621-accounting--projects)
   - [6.22 Accounting — Deferred Revenue & Prepaid Expenses](#622-accounting--deferred-revenue--prepaid-expenses)
   - [6.23 Reports](#623-reports)
   - [6.24 Business Engine (high-level facade)](#624-business-engine-high-level-facade)
   - [6.25 Money & Currencies](#625-money--currencies)
   - [6.26 Validators, Formatting & PII](#626-validators-formatting--pii)
   - [6.27 Security Helpers](#627-security-helpers)
   - [6.28 Persistence (Repository / SQLAlchemy / Unit of Work)](#628-persistence-repository--sqlalchemy--unit-of-work)
   - [6.29 Events](#629-events)
   - [6.30 PDF Generation](#630-pdf-generation)
   - [6.31 CLI](#631-cli)
   - [6.32 Configuration](#632-configuration)
   - [6.33 Exceptions](#633-exceptions)
7. [Guides](#guides)
   - [Multi-company & cost centers](#multi-company--cost-centers)
   - [Durable persistence (SQLite / Postgres)](#durable-persistence-sqlite--postgres)
   - [REST API & idempotency](#rest-api--idempotency)
   - [Security hardening checklist](#security-hardening-checklist)
   - [Performance & benchmarks](#performance--benchmarks)
8. [Error handling](#error-handling)
9. [Testing](#testing)
10. [Project structure](#project-structure)
11. [Roadmap](#roadmap)
12. [Contributing](#contributing)
13. [Security](#security)
14. [FAQ](#faq)
15. [License](#license)

---

## Why PyLedger?

| You want… | PyLedger gives you… |
|---|---|
| Correct books without an accounting degree | `BusinessEngine.sell()/buy()/pay_salary()` → balanced entries automatically |
| Full control when you need it | `Account` + `JournalEntry` + `Ledger` double-entry core with `Decimal` everywhere |
| Real-world accounting | VAT/GST, aging, depreciation, inventory (FIFO/WA), budgets, consolidation, bank rec, deferred revenue |
| Production readiness | RBAC, hash-chained audit trail, input sanitizers, multi-tenancy, SQLAlchemy persistence, idempotency |
| Reports & documents | Income Statement, Balance Sheet, Cash Flow (direct/indirect), Equity, Comparatives, Ratios, CSV export, PDF (incl. Arabic) |

---

## Features

- 📒 **General ledger** — 5 account types, normal-balance rules, trial balance (cached)
- 📝 **Journal entries** — mandatory balancing, double-post guard, reversal entries, cost centers
- 🧾 **Invoices** — items, taxes, partial/full payments, status machine
- 💰 **Tax** — VAT/GST calc, reverse calc, multi-tax calculator, VAT returns, corporate tax per country (SA 20%, AE 9%…)
- 💳 **Payments** — methods, party tracking, process/fail/refund lifecycle
- 🏭 **Assets & inventory** — straight-line/declining depreciation, FIFO/weighted-average
- 🤝 **CRM-lite** — customers, suppliers, credit limits, overdue
- 📊 **Reports** — 8 report types + ratios + CSV export
- 💱 **Money** — 8 currencies (USD, EUR, GBP, SAR, AED, EGP, JOD, KWD), cross-currency ops, `allocate()` without losing cents
- 🗄️ **Persistence** — in-memory, raw SQLite, or SQLAlchemy (SQLite/Postgres) with Unit of Work
- 🔒 **Security** — sanitizers (XSS/SQLi/CSV-injection), RBAC, PBKDF2 passwords, append-only audit log, PII masking
- 🧩 **Integration** — EventBus, optional FastAPI server, Click CLI

---

## Installation

**Requirements:** Python 3.7+ (3.9+ recommended). Core has **zero mandatory dependencies**.

```bash
pip install pyledger
```

From source:

```bash
git clone https://github.com/<your-username>/pyledger.git
cd pyledger
pip install -e .
```

Optional extras:

```bash
pip install -e ".[database]"   # sqlalchemy, psycopg2-binary, pymysql
pip install -e ".[cli]"        # click
pip install -e ".[dev]"        # pytest, pytest-cov, black, flake8, mypy
pip install reportlab arabic_reshaper python-bidi  # PDF generation
pip install fastapi uvicorn pydantic               # REST API server
```

> Replace `<your-username>` with the actual GitHub owner when publishing.

---

## Quickstart (5 minutes)

### Option A — Business language (recommended for most apps)

```python
from pyledger import PyLedger
from pyledger.reports import FinancialPeriod

app = PyLedger(company="Acme Corp", currency="USD")

app.add_investment("Owner", 100_000)                                   # Dr Cash / Cr Capital
app.sell([{"name": "Widget", "quantity": 2, "price": 500}],            # Dr Cash/AR / Cr Sales
         customer="CUST-001", payment_method="cash", tax_rate=15)
app.pay_expense("Rent", 2_000, category="rent")                        # Dr Rent / Cr Cash
app.pay_salary("Layla", 5_000, deductions={"tax": 500})                # Dr Salary / Cr Cash+Payables
app.buy_fixed_asset("Server", 15_000, useful_life=5)                   # Dr Equipment / Cr Cash

print(app.income_statement().generate()["net_income"])
print(app.balance_sheet().generate()["total_assets"])
print(app.cash_flow(period=FinancialPeriod.monthly(2026, 9)).generate()["net_change"])
```

### Option B — Accountant language (full control)

```python
from decimal import Decimal
from pyledger import Ledger, Account, JournalEntry

ledger = Ledger("Main Ledger", currency="SAR")
cash  = Account("Cash", "asset", "1000-CASH")
sales = Account("Sales Revenue", "income", "4000-SALES")
ledger.add_account(cash)
ledger.add_account(sales)

entry = JournalEntry("First sale", cost_center="RIYADH-1")
entry.add_debit(cash, Decimal("1150"), "Cash received")
entry.add_credit(sales, Decimal("1150"), "Revenue recognized")
ledger.record_entry(entry)          # validates + posts atomically

print(ledger.trial_balance())       # Decimal totals
```

---

## Core concepts

Double-entry in 30 seconds: every transaction touches **≥2 accounts** and **total debits == total credits**.

- **Debit-normal** accounts (`asset`, `expense`) grow on the debit side.
- **Credit-normal** accounts (`liability`, `equity`, `income`) grow on the credit side.
- Money is always `Decimal`, never `float`.
- Posted entries are **immutable** — fix mistakes with a **reversing entry**, never by editing.

---

## API Reference

> All snippets assume `from pyledger import ...` works. Amounts accept `int`, `float`, `str` or `Decimal` and are normalized to `Decimal(0.01)`.

### 6.1 Core — Accounts

```python
from pyledger import Account, CashAccount, GLAccount
```

**`Account(name, account_type, code, currency='USD', description='', initial_balance=0, allow_negative=False)`**

`account_type` ∈ `asset | liability | equity | income | expense`. `code` must match `^[A-Z0-9-]{2,20}$`.

| Method | Signature | What it does + example |
|---|---|---|
| `deposit` | `(amount, description='') -> Decimal` | Cash-style increase. `acc.deposit(1000, "Opening")` |
| `withdraw` | `(amount, description='') -> Decimal` | Cash-style decrease; raises `InsufficientBalanceError` unless `allow_negative=True`. `acc.withdraw(200)` |
| `apply_debit` | `(amount, description='') -> Decimal` | Proper double-entry debit (never blocks). Used by `JournalEntry.post()` |
| `apply_credit` | `(amount, description='') -> Decimal` | Proper double-entry credit (never blocks) |
| `get_balance` | `(as_of_date=None) -> Decimal` | Current balance, or balance as of a datetime (replayed from history) |
| `get_balance_as_of` | `(as_of_date) -> Decimal` | Alias of `get_balance(as_of_date)` |
| `get_debit_balance` | `() -> Decimal` | Trial-balance debit column for this account |
| `get_credit_balance` | `() -> Decimal` | Trial-balance credit column |
| `get_transactions` | `(limit=None, start_date=None, end_date=None, txn_type=None) -> list` | History dicts (`type/amount/description/timestamp/balance_after`); filter e.g. `txn_type='deposit'` |
| `normal_balance` | `property -> 'debit' \| 'credit'` | `asset/expense → debit`, others → credit |
| `is_debit_normal` / `is_credit_normal` | `() -> bool` | Convenience predicates |
| `to_dict` | `() -> dict` | JSON-serializable snapshot |

**`CashAccount(name, code, currency='USD', description='', initial_balance=0)`** — an `asset` account with strict no-overdraft `withdraw()` (raises `InsufficientBalanceError`). Use for tills, safes, bank accounts.

**`GLAccount(name, account_type, code, ...)`** — general-ledger account that permits negative (contra/timing) balances.

```python
till = CashAccount("Main Till", "1000-TILL")
till.deposit(500)
till.withdraw(600)   # raises InsufficientBalanceError

# Any GL account knows its normal side:
print(Account("Sales", "income", "4000").normal_balance)  # 'credit'
print(till.get_transactions(limit=5, txn_type="deposit"))
```

### 6.2 Core — Transactions & Journal Entries

```python
from pyledger import Transaction, JournalEntry, AlreadyPostedError
```

**`Transaction(account, transaction_type, amount, date=None, description='')`** — one debit/credit leg. `transaction_type` ∈ `debit | credit`.
Methods: `get_amount()`, `is_debit()`, `is_credit()`, `to_dict()`.

**`JournalEntry(description, date=None, entry_number=None, unique_number=False, company_id='default', cost_center=None)`**

| Method | Example |
|---|---|
| `add_debit(account, amount, description='')` | `e.add_debit(cash, 500).add_debit(bank, 500)` (chainable) |
| `add_credit(account, amount, description='')` | `e.add_credit(sales, 1000)` |
| `get_total_debits() / get_total_credits()` | `e.get_total_debits()  # Decimal('1000')` |
| `is_balanced()` | `True` iff debits == credits |
| `validate()` | Raises `UnbalancedEntryError` if empty-sided or unbalanced |
| `post(ledger=None, validator=None)` | Posts once; second call raises `AlreadyPostedError` |
| `reverse(description=None, date=None)` | Returns equal-and-opposite entry (post it to cancel) |
| `to_dict()` | Full snapshot incl. `company_id`, `cost_center`, `posted_date` |

```python
e = JournalEntry("Sale #42", cost_center="JEDDAH")
e.add_debit(cash, 1150).add_credit(sales, 1000).add_credit(vat_payable, 150)
assert e.is_balanced()
ledger.record_entry(e)

oops = JournalEntry("Fix #42")
oops.add_debit(sales, 1150).add_credit(cash, 1150)   # or simply: e.reverse()
ledger.record_entry(oops)
```

### 6.3 Core — Ledger

```python
from pyledger import Ledger
ledger = Ledger("Main Ledger", currency="USD", company_id="acme")
```

| Method | Example |
|---|---|
| `add_account(account)` | Raises `DuplicateAccountError` on code clash |
| `get_account(code)` | Raises `AccountNotFoundError` if missing |
| `account_exists(code)` | `ledger.account_exists("1000")` |
| `get_accounts_by_type(type)` | `ledger.get_accounts_by_type("asset")` |
| `transfer(from, to, amount)` | Auto-builds + posts a balanced transfer entry |
| `record_entry(entry)` | Validates, posts, appends; enforces `company_id` isolation; emits `EntryPosted` |
| `bulk_record(entries)` | Validates all, then posts all; compensates on failure. Returns count |
| `query_entries(limit=100, offset=0, company_id=None, cost_center=None, start_date=None, end_date=None)` | Paginated/filtered access for millions of entries |
| `get_journal_entries(limit=None)` | Last-N entries (simple accessor) |
| `trial_balance()` | `{'accounts': [...], 'total_debits': Decimal, 'total_credits': Decimal, 'balanced': bool}` (cached) |
| `get_trial_balance()` | Same but stringified (JSON-friendly) |
| `get_account_balance(code)` | Shortcut |
| `get_total_assets/liabilities/equity/income/expenses()` | Type totals |
| `to_dict()` | Snapshot (name, currency, accounts, counts) |

```python
page2 = ledger.query_entries(limit=50, offset=50, cost_center="RIYADH-1")
tb = ledger.trial_balance()
assert tb["balanced"] and tb["total_debits"] == tb["total_credits"]
```

### 6.4 Core — Numbering

```python
from pyledger.core import SequenceService, next_journal_number
svc = SequenceService(prefix="JE")   # also next_invoice_number / next_payment_reference
svc.next()          # 'JE-000001' (thread-safe, per-process)
svc.next_unique()   # 'JE-202609-A1B2C3D4' (unique across restarts)
JournalEntry("x", unique_number=True)  # opt into globally-unique numbers
```

For crash-safe numbering across processes use `SqlAlchemyLedgerStore.next_sequence("JE")` (§6.28).

### 6.5 Core — Period Closing

```python
from pyledger.core.closing import ClosingEngine, PeriodClosedError
ce = ClosingEngine(ledger)
ce.close_month(2026, 9)     # -> {'period': '2026-09', ...}
ce.close_quarter(2026, 3)   # -> {'period': '2026 Q3', ...}
ce.close_year(2026)
ce.close_month(2026, 9)     # raises PeriodClosedError / ValueError (double close)
ce.is_period_closed(FinancialPeriod.monthly(2026, 9))
ce.get_closed_periods()
```

Closes zero-out income/expense into retained earnings (`retained_earnings_code`, default `'3100'`).

### 6.6 Core — Immutable Audit Trail

```python
from pyledger.core import ImmutableTransaction, AuditEntry, AuditTrail, PersistentAuditTrail

trail = AuditTrail()
trail.record("create", "entry", "JE-000001", user="admin")
trail.record("post", "entry", "JE-000001", user="admin")
trail.get_entries(entity_type="entry", entity_id="JE-000001", action="post", limit=10)
assert trail.verify_chain()   # SHA-256 hash chain tamper check

disk = PersistentAuditTrail()
disk.record("post", "entry", "JE-1", user="admin")
disk.save_jsonl("audit.jsonl")                       # atomic write
restored = PersistentAuditTrail.load_jsonl("audit.jsonl")
assert restored.verify_chain()
```

`ImmutableTransaction(account_code, account_name, transaction_type, amount, date, description, entry_number, sequence)` is a frozen dataclass — the tamper-evident view of a posting.

### 6.7 Core — Security & RBAC

```python
from pyledger.core.security import User, Role, Permission, SecurityManager

sm = SecurityManager()
sm.register_user("layla", Role.ACCOUNTANT, password="s3cure-pass!")
sm.authenticate("layla", password="s3cure-pass!")   # None on bad password
sm.require_permission(Permission.POST_ENTRIES)      # raises PermissionError if denied
sm.check_permission(Permission.CLOSE_PERIOD)        # bool, no raise
sm.get_users_by_role(Role.ACCOUNTANT)
sm.get_audit_log()   # [{'timestamp','user','action','detail'}]
```

Roles: `ADMIN` (all) · `ACCOUNTANT` (accounts, post, reports, export) · `MANAGER` (approve, reports) · `AUDITOR` (read + export) · `VIEWER` (read). `User.set_password()/check_password()` use PBKDF2-SHA256 (210k iterations, stdlib only); password-less users stay backward compatible.

### 6.8 Core — Approval Workflows

```python
from pyledger.core.workflow import WorkflowEngine, EntryStatus
we = WorkflowEngine()
e = we.create_entry("Server purchase", created_by="omar", amount=20000)
e.add_step("Manager approval").add_step("Finance approval").submit()  # PENDING_APPROVAL
e.approve(0, "sara"); e.approve(1, "layla")   # APPROVED
e.post()                                       # POSTED
e.reject(0, "sara", "over budget")             # -> REJECTED (alternative path)
we.get_pending(); we.get_by_status(EntryStatus.APPROVED); we.get_by_creator("omar")
```

### 6.9 Core — Contracts & Notes

```python
from pyledger.core.contracts import Contract, ContractManager, ContractType, ContractStatus
c = Contract("Office lease", ContractType.LEASE, "Landlord Co",
             datetime(2026,1,1), datetime(2028,12,31), Decimal("72000"))
c.activate(); c.is_active(); c.days_remaining(); c.complete()
mgr = ContractManager(); mgr.add(c)
mgr.get_active(); mgr.get_expiring_soon(60); mgr.get_by_party("Landlord Co"); mgr.get_total_value()

from pyledger.core.notes import NoteManager
notes = NoteManager()
n = notes.add("Called client, promised Sunday", author="sara", entity_type="invoice", entity_id="INV-1")
n.edit("...rescheduled to Monday")
notes.get_by_entity("invoice", "INV-1"); notes.get_by_author("sara"); notes.get_recent(5); notes.delete(n.note_id)
```

### 6.10 Accounting — Invoices

```python
from pyledger import Invoice, InvoiceItem, InvoiceStatus, Tax
inv = Invoice("Acme Corp", currency="SAR")          # number auto: INV-000001 (or unique_number=True)
inv.add_item("Consulting", quantity=10, unit_price=500)   # chainable
inv.add_item("License", 1, 2000).remove_item(0)
inv.add_tax(Tax("VAT", 15))        # or shortcut:
inv.apply_tax("VAT", 15)
inv.calculate_total()              # subtotal + tax
inv.issue()                        # DRAFT -> ISSUED
inv.record_payment(3000)           # or pay(3000, method='bank_transfer') -> PARTIALLY_PAID
inv.record_payment(4250)           # -> PAID
inv.get_remaining_balance(); inv.get_status()   # 'paid'
inv.cancel()                       # refused once PAID
inv.to_dict()                      # items, subtotal, tax_total, total, paid, remaining, status...
```

Lifecycle: `DRAFT → ISSUED → PARTIALLY_PAID → PAID` (or `CANCELLED`). `record_payment` auto-issues drafts — convenient for cash sales.

### 6.11 Accounting — Tax

```python
from pyledger import Tax, TaxCalculator
vat = Tax("VAT", 15)
vat.calculate(1000)        # Decimal('150.00')
vat.calculate_total(1000)  # Decimal('1150.00')
Tax.calculate_vat(1000, 15)       # {'base','vat_amount','total'}
Tax.reverse_calculate(1150, 15)   # back out base+tax from gross

calc = TaxCalculator().add_tax("VAT", 15).add_tax("Withholding", 5)
calc.calculate_all(1000)   # {'taxes': {...}, 'total_tax': ...}
calc.remove_tax("Withholding")
```

### 6.12 Accounting — Payments

```python
from pyledger import Payment, PaymentMethod, PaymentStatus, PaymentReceiver
p = Payment(500, "CUST-001")                 # 2nd arg = party id (or a method name)
p = Payment(500, "bank_transfer")            # ...or a method; party=None
p = Payment(500, "CUST-001", method="cash")  # explicit both
p.process()   # PENDING -> COMPLETED ; p.fail("NSF") ; p.refund() ; p.get_status()
p.party, p.method, p.reference, p.to_dict()

box = PaymentReceiver("TILL-1")
box.receive_payment(200, method="cash")      # auto-processed
box.get_total_received(); box.get_payment_by_reference("PAY-000001")
box.get_payments_by_method("cash")
```

`PaymentStatus`: `PENDING · COMPLETED (+ legacy PROCESSED alias) · FAILED · REFUNDED`.

### 6.13 Accounting — Fixed Assets & Depreciation

All globally used methods (IAS 16 / GAAP / US tax): `straight_line` · `declining_balance`
(with `rate_factor`: `2.0` = 200%/double, `1.5` = 150%) · `sum_of_years` ·
`units_of_production` (IAS 16.62) · `macrs` (IRS Pub. 946: `GDS-3/5/7/10/15/20`,
`GDS-27.5/39` realty mid-month). Plus `convention='half_year'` and full schedules.

```python
from pyledger.accounting.assets import FixedAsset, DepreciationEngine, DepreciationMethod
m = FixedAsset("CNC Machine", 100000, "FA-001", useful_life_years=5,
               depreciation_method=DepreciationMethod.STRAIGHT_LINE)
m.annual_depreciation()    # 20000.00
m.monthly_depreciation(); m.to_dict(); m.dispose(30000)

db150 = FixedAsset("Van", 100000, "FA-002", 5, DepreciationMethod.DECLINING_BALANCE,
                   rate_factor=1.5)
db150.annual_depreciation()   # 30000.00

truck = FixedAsset("Truck", 50000, "FA-003", 5, DepreciationMethod.UNITS_OF_PRODUCTION,
                   total_estimated_units=100000)
truck.record_production(20000)   # 10000.00, tracked in lifetime_produced

us_box = FixedAsset("Server", 10000, "FA-004", 0, DepreciationMethod.MACRS, macrs_class="GDS-5")
us_box.depreciation_schedule()   # 6 IRS rows summing to cost
bldg = FixedAsset("Office", 275000, "FA-005", 0, DepreciationMethod.MACRS,
                  macrs_class="GDS-27.5", placed_in_service_month=1)

eng = DepreciationEngine(ledger)
eng.register_asset(m); eng.get_asset("CNC Machine"); eng.get_all_assets()
eng.generate_schedule("CNC Machine")   # non-mutating planning table
eng.post_depreciation("CNC Machine")   # Dr Depreciation / Cr Accum. Depr.
eng.post_all_depreciation()
eng.dispose_asset("CNC Machine", disposal_price=30000)  # gain/loss computed
```

### 6.14 Accounting — Inventory

```python
from pyledger.accounting.inventory import InventoryItem, InventoryManager
it = InventoryItem("SKU-1", "Widget", valuation_method="fifo")  # or 'weighted_average', or 'lifo' (US GAAP only — banned by IAS 2)
it.receive(10, 100); it.receive(10, 200)
it.weighted_average_cost()   # 150.00
it.issue(3)                  # FIFO layers consumed; raises on insufficient stock
it.to_dict()                 # qty, available, value...

mgr = InventoryManager(); mgr.add_item(it)
mgr.receive("SKU-1", 5, 120); mgr.issue("SKU-1", 2)
mgr.get_inventory_value(); mgr.get_valuation_report(); mgr.get_movements(limit=20)
```

### 6.15 Accounting — CRM

```python
from pyledger.accounting.crm import Customer, Supplier
c = Customer("Acme", "C-1", tax_id="300123456700003", credit_limit=50000,
             email="a@acme.sa", phone="+966500000000")
c.add_invoice(inv); c.get_balance(); c.get_invoices_by_status("paid")
c.get_overdue_amount(); c.to_dict()
s = Supplier("Parts Co", "S-1"); s.get_balance(); s.to_dict()
```

### 6.16 Accounting — Aging Reports

```python
from pyledger.accounting.aging import ReceivableAging, PayableAging
r = ReceivableAging(ledger, [c]).generate()
# {'customers': [{'name','total','brackets': {'0-30 Days': ...}}], 'grand_total': ...}
PayableAging(ledger, [s]).generate()
```

### 6.17 Accounting — Budgets & Budget Control

```python
from pyledger.accounting.budget import Budget, BudgetVsActual
from pyledger.accounting.budget_control import BudgetControl
from pyledger.reports import FinancialPeriod
b = Budget("2026 Ops", FinancialPeriod.annual(2026))
b.set_amount("5000", 60000); b.get_amount("5000"); b.get_total(); b.to_dict()
BudgetVsActual(ledger, b, period=FinancialPeriod.monthly(2026, 9)).generate()

ctrl = BudgetControl(b, ledger)
ctrl.check_entry(entry)        # bool
ctrl.check_and_raise(entry)    # raises BudgetExceededError
ctrl.disable()/enable(); ctrl.get_violations(); ctrl.clear_violations()
```

### 6.18 Accounting — Consolidation

```python
from pyledger.accounting.consolidation import ConsolidationEngine, ConsolidatedReport
eng = ConsolidationEngine(parent_ledger, [sub1, sub2])
eng.add_subsidiary(sub3)
eng.add_elimination("1000", "2000", 5000, "Intercompany loan")
eng.get_consolidated_ledger()          # {'entity_count': 3, ...}
eng.get_consolidated_balance("1000")
eng.generate_consolidated_income(period); eng.generate_consolidated_balance(period)
ConsolidatedReport(eng, period).generate()
```

### 6.19 Accounting — Tax Reports (VAT / Corporate Tax)

```python
from pyledger.accounting.tax_reports import VATReturn, CorporateTaxReport
VATReturn(ledger, FinancialPeriod.monthly(2026, 9), vat_rate=15).generate()
# {'vat_payable','vat_receivable',...}
CorporateTaxReport(ledger, FinancialPeriod.annual(2026), country="SA").generate()
# SA → 20%, AE → 9% (built-in), or pass explicit tax_rate=
```

### 6.20 Accounting — Bank Reconciliation

```python
from pyledger.accounting.bank_reconciliation import BankReconciliation
br = BankReconciliation(ledger, "1000", as_of_date=datetime.now())
br.add_statement_line(datetime.now(), "Deposit", 5000, reference="STMT-1")
br.mark_cleared("STMT-1")
br.reconcile()   # {'ledger_balance','statement_balance','is_reconciled',...}
br.get_ledger_balance(); br.get_statement_balance()
br.get_outstanding_checks(); br.get_deposits_in_transit(); br.generate_report()
```

### 6.21 Accounting — Projects

```python
from pyledger.accounting.projects import Project, ProjectManager, ProjectProfitability
p = Project("PRJ-1", "Website", budget=50000)
p.add_transaction("Hosting", 5000, "5000")
p.get_total_cost(); p.get_budget_utilization(); p.get_remaining_budget(); p.is_over_budget()
pm = ProjectManager(); pm.add_project(p)
pm.get_project("PRJ-1"); pm.get_all(); pm.get_over_budget(); pm.get_by_status("active")
ProjectProfitability(ledger, pm).generate()
```

### 6.22 Accounting — Deferred Revenue & Prepaid Expenses

```python
from pyledger.accounting.deferred import DeferredRevenue, PrepaidExpense
sub = DeferredRevenue("Annual plan", 12000, datetime(2026,1,1), datetime(2026,12,31))
sub.generate_schedule()      # 12 monthly slices
sub.get_monthly_amount()     # 1000.00
sub.recognize("2026-01"); sub.get_deferred_balance()

ins = PrepaidExpense("Insurance", 6000, datetime(2026,1,1), datetime(2026,12,31))
ins.generate_schedule(); ins.amortize("2026-01"); ins.get_prepaid_balance()
```

### 6.23 Reports

```python
from pyledger.reports import (
    FinancialPeriod, IncomeStatement, BalanceSheet, CashFlowStatement,
    EquityStatement, ComparativeIncomeStatement, ComparativeBalanceSheet,
    FinancialRatios,
)
from pyledger.reports.export import ReportExporter

p = FinancialPeriod.monthly(2026, 9)     # or .quarterly(2026, 3) / .annual(2026) / .year_to_date(2026, 9)
IncomeStatement(ledger, period=p).generate()
# {'title','income':{'accounts','total'},'expenses':{...},'items',...,'net_income'}
BalanceSheet(ledger, as_of_date=datetime.now(), classify=True).generate()
# {'assets':{'current','noncurrent','total'}, 'total_assets', 'total_liabilities', ...}
CashFlowStatement(ledger, period=p, method="indirect").generate()  # or method='direct'
EquityStatement(ledger, period=p).generate()
ComparativeIncomeStatement(ledger, [p1, p2]).generate()
ComparativeBalanceSheet(ledger, [p1, p2]).generate()
FinancialRatios(ledger, period=p).generate()
# {'liquidity':{'current_ratio',...},'profitability':{...},'leverage':{...},'efficiency':{...}}
str(IncomeStatement(ledger))          # pretty text rendering
ReportExporter.to_csv(IncomeStatement(ledger))
ReportExporter.to_csv_file(BalanceSheet(ledger), "bs.csv")
ReportExporter.export_aging(aging_dict); ReportExporter.export_ratios(ratios_dict)
```

### 6.24 Business Engine (high-level facade)

`BusinessEngine(ledger=None, company_name='My Company', currency='USD', country='US', industry='general', auto_setup=True, company=None)` — `PyLedger` is a drop-in alias (`PyLedger(company=..., currency=...)`).

| Method | Example |
|---|---|
| `sell(items, customer, payment_method='credit', tax_rate=0)` | `app.sell([{'name':'Widget','quantity':2,'price':500}], 'C-1', 'cash', 15)` |
| `buy(items, supplier, payment_method='credit', tax_rate=0, is_inventory=True)` | `app.buy([...], 'S-1')` |
| `pay_expense(description, amount, category='general', payment_method='cash')` | `app.pay_expense('Rent', 2000, 'rent')` |
| `pay_salary(employee, gross_salary, deductions=None)` | `app.pay_salary('Layla', 5000, {'tax':500})` |
| `buy_fixed_asset(name, cost, useful_life=None, down_payment=None)` | `app.buy_fixed_asset('Server', 15000, 5)` |
| `record_depreciation(asset_name, amount)` | — |
| `add_investment(investor, amount)` | `app.add_investment('Owner', 100000)` |
| `transfer(from, to, amount, description='Transfer')` | Account-code to account-code transfer |
| `add_account(name, type, code=None, description='')` | Sanitized + validated |
| `validate_entry(entry)` / `post_entry(entry)` | Deep validation + duplicate detection |
| `income_statement(period)` / `balance_sheet(as_of)` / `cash_flow(period, method)` / `equity_statement(period)` | Report objects (call `.generate()`) |
| `financial_ratios(period)` / `vat_return(period, vat_rate)` / `corporate_tax(period, country)` | Advanced reports |
| `create_customer/supplier/fixed_asset/inventory_item/budget/project/deferred_revenue/prepaid_expense(...)` | Factories |
| `bank_reconciliation(code, as_of)` | — |
| `export_csv(report)` / `to_pdf(filepath, reports)` | Export |

Auto-setup installs a smart chart of accounts (`SmartChartOfAccounts(country, industry)` with `accounts`, `add_to_ledger(ledger)`, `get_by_type(type)`).

### 6.25 Money & Currencies

Supported: `USD $ · EUR € · GBP £ · SAR ﷼ · AED د.إ · EGP £ · JOD د.ا · KWD د.ك`

```python
from pyledger import Money, CurrencyConverter
fx = CurrencyConverter()
fx.convert(100, "USD", "EUR")        # Decimal
fx.convert_amount(100, "USD", "SAR")
fx.get_rate("SAR"); fx.get_symbol("SAR"); fx.update_rate("EUR", 0.90)

m = Money(100, "USD")
m + Money(50, "USD")                 # same-currency
m + Money(100, "EUR")                # auto-converted to USD
m - other; m * 2; m / 2; -m; abs(m)
m == Money(100, "USD"); m < Money(200, "USD")
m.convert_to("SAR"); m.quantize()    # 3 decimals for KWD/BHD/OMR/JOD, else 2
Money(100, "USD").allocate([1, 1, 1])  # [33.33, 33.33, 33.34] — never loses cents
```

### 6.26 Validators, Formatting & PII

```python
from pyledger import (validate_account_code, validate_account_type, validate_amount,
                      validate_currency, validate_currency_strict, validate_tax_rate,
                      validate_date, format_amount)
validate_account_code("1000-CASH")  # True
validate_account_type("asset")      # True
validate_amount(100)                # amount > 0 ?
validate_currency("XX")             # False (bool API)
validate_currency_strict("XX")      # raises InvalidCurrencyError
validate_tax_rate(15)               # True / raises InvalidTaxRateError
validate_date(datetime.now()); format_amount("1234.5")  # Decimal('1234.50')

from pyledger.utils.formatter import Formatter
Formatter.format_amount(1234.5, "$")      # '$1,234.50'
Formatter.format_date(datetime.now())    # '2026-09-17'
Formatter.format_percentage(12.345)      # '12.35%'
Formatter.format_table([["a", 1]], headers=["x", "y"])

from pyledger.utils.pii import mask_email, mask_phone, mask_iban, mask_dict
mask_email("omar@example.com")  # 'o***r@example.com'
```

### 6.27 Security Helpers

```python
from pyledger.security.sanitizer import (
    sanitize_text, sanitize_name, sanitize_account_code, sanitize_amount,
    sanitize_csv_field, sanitize_description, sanitize_email, sanitize_phone,
    sanitize_quantity, sanitize_percentage, sanitize_filepath, sanitize_ip_address,
)
sanitize_text('<script>x</script>Hello')  # 'Hello'
sanitize_csv_field("=SUM(A1:A10)")       # "'=SUM(A1:A10)" (injection-safe)
sanitize_amount("1000.50")               # Decimal, guards negatives/decimals/max
sanitize_account_code("fix-asset")       # 'FIX-ASSET' (raises on invalid)

from pyledger.security.passwords import hash_password, verify_password
h = hash_password("s3cure-pass!"); verify_password("s3cure-pass!", h)  # True

from pyledger.security.validator import EntryValidator, DuplicateDetector
v = EntryValidator(ledger); v.validate(entry)  # [errors]; v.validate_and_raise(entry)
d = DuplicateDetector(); d.mark_seen(entry); d.check_entry(entry)  # True if dup
d.check_invoice(customer, items, total, date); d.clear()
```

### 6.28 Persistence (Repository / SQLAlchemy / Unit of Work)

```python
from pyledger.database import InMemoryRepository, SQLiteConnection, SqlAlchemyLedgerStore

# 1) In-memory (tests, demos)
repo = InMemoryRepository()
repo.create(model); repo.read(id); repo.update(model); repo.delete(id); repo.get_all()

# 2) Raw SQLite helper
con = SQLiteConnection("ledger.db"); con.connect(); con.create_tables()
con.execute("SELECT * FROM accounts"); con.disconnect()

# 3) Enterprise: SQLAlchemy (SQLite → Postgres by URL swap)
store = SqlAlchemyLedgerStore("sqlite:///ledger.db", company_id="acme")
# store = SqlAlchemyLedgerStore("postgresql+psycopg2://user:pw@host/pyledger", company_id="acme")
store.save_ledger(ledger)                 # upsert accounts + append new entries
ledger2 = store.load_ledger("Main Ledger")
store.entry_count()
store.next_sequence("JE")                 # crash-safe numbering
with store.unit_of_work() as uow:         # atomic multi-step work
    n = uow.next_sequence("INV", fiscal_year="2026")
```

### 6.29 Events

```python
from pyledger.events import EventBus, default_bus, ENTRY_POSTED, INVOICE_ISSUED, PERIOD_CLOSED
bus = EventBus()
bus.subscribe(ENTRY_POSTED, lambda p: print("posted", p["number"]))
bus.emit(ENTRY_POSTED, {"number": "JE-000001"})
bus.unsubscribe(ENTRY_POSTED, handler)
# Ledger.record_entry() emits ENTRY_POSTED on default_bus automatically.
```

### 6.30 PDF Generation

```python
from pyledger.pdf import PDFEngine, CompanyInfo
pdf = PDFEngine(ledger)
pdf.set_company(name="Acme Corp")     # + address/phone/vat via CompanyInfo
pdf.add_report(IncomeStatement(ledger))
pdf.add_report(BalanceSheet(ledger))
pdf.save("report.pdf")
data: bytes = pdf.to_bytes()          # serve over HTTP
```

Arabic-capable (reportlab + arabic_reshaper + python-bidi).

### 6.31 CLI

```bash
pyledger init --company "Acme" --currency USD --country US -o ledger.json
pyledger run -f ops.json -l ledger.json -o ledger.json
pyledger report -l ledger.json --type income            # income | balance | cashflow | trial
pyledger vat -l ledger.json --period 2026-09
pyledger tax -l ledger.json --period 2026 --country SA
pyledger aging -l ledger.json
pyledger ratios -l ledger.json
pyledger ratios-export -l ledger.json -o ratios.csv
pyledger reconcile -l ledger.json --account 1000
```

(`python -m pyledger.cli ...` works too. Both `pyledger` and legacy `pyliger` entry points are installed.)

### 6.32 Configuration

```python
from pyledger import config, Config
config.get("DEFAULT_CURRENCY")     # 'USD'
config["DECIMAL_PLACES"]           # 2
config.set("DEFAULT_CURRENCY", "SAR")
config.update({...}); config.as_dict()
"DEFAULT_CURRENCY" in config
```

Precedence: `config.py` (repo root, optional) → built-in defaults → `PYLEDGER_*` env vars (e.g. `PYLEDGER_DEFAULT_CURRENCY=SAR`). Keys: `DEFAULT_CURRENCY`, `SUPPORTED_CURRENCIES`, `DECIMAL_PLACES`, `DATE_FORMAT`, `DATETIME_FORMAT`, `AUTO_BALANCE`, `STRICT_MODE`, `DEFAULT_TAX_RATES`, `INVOICE_CONFIG`, `DATABASE`, `VALIDATION`, `LOGGING`.

### 6.33 Exceptions

```python
from pyledger import (PyLedgerException, AccountNotFoundError, UnbalancedEntryError,
    InvalidAccountTypeError, InsufficientBalanceError, DuplicateAccountError,
    InvalidCurrencyError, InvalidTaxRateError, InvoiceNotFoundError, InvalidInvoiceStatusError)
from pyledger.core.journal import AlreadyPostedError
from pyledger.core.closing import PeriodClosedError
from pyledger.accounting.budget_control import BudgetExceededError
```

All inherit `PyLedgerException` — catch broadly or precisely:

```python
try:
    ledger.record_entry(entry)
except UnbalancedEntryError:
    print("Debits != credits — entry rejected, nothing posted")
except AlreadyPostedError:
    print("Idempotent retry — already posted")
```

---

## Guides

### Multi-company & cost centers

```python
a = Ledger("Acme", "USD", company_id="acme")
b = Ledger("Globex", "USD", company_id="globex")
e = JournalEntry("Sale", company_id="acme", cost_center="RIYADH-1")
a.record_entry(e)
b.record_entry(e)   # ValueError: tenant mismatch
a.query_entries(cost_center="RIYADH-1", limit=50)
```

### Durable persistence (SQLite / Postgres)

```python
store = SqlAlchemyLedgerStore("sqlite:///ledger.db", company_id="acme")
store.save_ledger(app.ledger)
restored = store.load_ledger("Acme Corp")
```

Postgres only changes the URL. Tables (`accounts`, `journal_entries`, `entry_lines`, `sequences`) are created automatically; `idempotency_key` is UNIQUE for safe retries.

### REST API & idempotency

```bash
pip install fastapi uvicorn pydantic
uvicorn pyledger.api:create_app --factory --port 8000
```

```bash
curl -X POST localhost:8000/entries -H 'X-Idempotency-Key: abc-1' \
  -H 'Content-Type: application/json' \
  -d '{"description":"Sale","lines":[{"account":"1000","side":"debit","amount":100},{"account":"4000","side":"credit","amount":100}]}'
# Retry with the same key -> 409, no double posting
```

### Security hardening checklist

1. `BusinessEngine.post_entry()` (validation + duplicate detection) instead of raw `post()`.
2. `SecurityManager` with passwords + `require_permission(POST_ENTRIES)` on write paths.
3. `sanitize_*` on every external string; `sanitize_csv_field` before CSV export.
4. `PersistentAuditTrail.save_jsonl()` after closes; alert if `verify_chain()` is False.
5. `mask_dict()` before logging customer data.

### Performance & benchmarks

- Trial balance is cached and invalidated on write; bulk-post with `bulk_record()` (~22k entries/sec on a laptop).
- Paginate reads: `query_entries(limit, offset, ...)`; aggregate in SQL (`SqlAlchemyLedgerStore`) for millions of rows.
- Run the gate: `python benchmarks/bench.py`.

```python
ledger.bulk_record([e1, e2, e3])   # all-or-nothing
```

---

## Error handling

See §6.33. Rules of thumb: `validate()` before `post()`; never edit posted entries — `reverse()` them; wrap `record_entry`/`bulk_record` in try/except; treat `AlreadyPostedError` as a successful retry.

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest test_pyledger.py -v          # 214 tests, full suite
pytest test_pyledger.py -k Invoice  # subset
python example.py                   # end-to-end demo
python benchmarks/bench.py          # perf gate
```

---

## Project structure

```
pyledger/
├── core/          account, ledger, journal, transaction, sequences,
│                  closing, immutable, audit_store, security, workflow,
│                  contracts, notes
├── accounting/    invoice, tax, tax_reports, payment, assets, inventory,
│                  crm, aging, budget, budget_control, consolidation,
│                  bank_reconciliation, projects, deferred
├── reports/       base, income_statement, balance_sheet, cash_flow,
│                  equity_statement, comparative, ratios, export
├── business/      engine (BusinessEngine/PyLedger), defaults, operations/
├── database/      models, repository, orm (SQLAlchemy), uow (Unit of Work)
├── utils/         currency (Money), validators, formatter, pii
├── security/      sanitizer, validator, passwords
├── pdf/           engine, branding, arabic, styles, elements
├── events.py      EventBus · api.py (FastAPI factory) · cli.py · config.py
└── exceptions/    10+ typed errors
```

---

## Roadmap

- [x] v2.1 — test-suite green (214/214), SQLAlchemy persistence, multi-tenancy, audit hardening
- [ ] v2.2 — Alembic migrations, ZATCA e-invoicing, XLSX export
- [ ] v2.3 — hosted docs, async adapters, Redis FX cache
- [ ] v3.0 — stable REST API + webhook signatures + multi-currency ledgers

Vote with 👍 on issues — roadmap follows demand.

---

## Contributing

We love contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow (fork → branch → tests → PR). By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

```bash
git clone https://github.com/<your-username>/pyledger.git && cd pyledger
pip install -r requirements-dev.txt
pytest test_pyledger.py -q
```

## Security

Found a vulnerability? **Do not open a public issue.** See [SECURITY.md](SECURITY.md) for how to report privately.

## FAQ

**Do I need to know accounting?** No — start with `PyLedger(...).sell(...)`. Learn the core later.
**Float or Decimal?** Always `Decimal`. Floats never touch money paths.
**Can I edit a posted entry?** No — post a `reverse()` entry. That's how real ledgers stay auditable.
**SQLite or Postgres?** Start SQLite, switch the SQLAlchemy URL when you grow. Zero code changes.
**Which Python?** 3.7+ supported, 3.9+ recommended.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE). © 2026 Omar Abd Al-Aziz & PyLedger Contributors.

**What this means for you:**
- ✅ Commercial use, modification, distribution and sublicensing — free of charge
- ✅ Express patent grant from all contributors
- 📌 You must keep the `LICENSE` and `NOTICE` attribution files in any distribution (see `NOTICE` for the credit line)
- 📌 Modified files must carry notices stating what you changed

Kindly keep the visible credit — `Built with PyLedger` — in docs or about pages. It keeps the project alive.

If PyLedger powers your project, please ⭐ star the repo — it keeps the project alive. And share your story in [Discussions](../../discussions)!
