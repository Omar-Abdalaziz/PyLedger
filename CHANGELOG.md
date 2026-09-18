# PyLedger Changelog

## Version 2.1.0 (2026-09-17)

### Fixed (test-suite alignment, 17 failures -> 0)
- CLI entry point typo `pyliger` (kept as alias, added `pyledger`)
- `validate_currency` returns bool; added `validate_currency_strict`
- `Account.get_balance_as_of`, `get_transactions(txn_type=...)`
- `Ledger.trial_balance()` (Decimal totals) + cached `get_trial_balance()`
- `Invoice.apply_tax/record_payment`, fixed inverted `issue()`
- `Payment(party)` inference + `COMPLETED` status + `PaymentReceiver(id)`
- `InventoryItem.weighted_average_cost()` method API
- Reports compat keys (`items`, `total_assets`), `BusinessEngine(company=...)`

### Added (enterprise readiness)
- `SequenceService` UUID-based numbering (`core/sequences.py`)
- `CashAccount` / `GLAccount`, `normal_balance`, `apply_debit/credit`
- `JournalEntry` double-post guard (`AlreadyPostedError`) + `reverse()`
- `Money.quantize/allocate`, `FXProvider` abstraction
- SQLAlchemy persistence: `database/orm.py` + `SqlAlchemyLedgerStore` + UoW + sequences
- Multi-tenancy: `Ledger(company_id)`, `JournalEntry(company_id, cost_center)`, `query_entries`, `bulk_record`
- Security: PBKDF2 passwords, `PersistentAuditTrail` (JSONL), PII masking
- Events: `events.EventBus` + `ENTRY_POSTED` emission; `api.create_app()` (FastAPI, optional)
- Benchmarks: `benchmarks/bench.py`

### ⚖️ License change
- Relicensed from MIT to **Apache License 2.0** (commercial-friendly + patent grant)
- Added `NOTICE` attribution file: distributors must retain the PyLedger credit line

### 🛡️ Security hardening (audit 2026-09-18, bandit: 0 medium/high)

### 🧾 Accounting correctness audit (IFRS/GAAP, 2026-09-18)
- **Period cut-off fixed:** legs are stamped with the ENTRY date (was wall-clock),
  so period income/cash-flow/as-of balances work; added `Account.balance_effect()`
  (signed replay by normal side) used by `get_balance(as_of)`, income and cash-flow
  filters — sales returns now net revenue (IFRS 15), liability as-of fixed
- **Multi-tax invoices:** `add_tax` accumulates on subtotal + `taxes` breakdown
  in `to_dict()` (was overwriting)
- **Bank reconciliation:** deposits/outstanding derived from signed effects
  (was sign-blind: always 0 outstanding); bidirectional clear matching
- **Inventory:** `_total_cost` maintained for FIFO issues too (WAC consistency)
- **Aging:** no-due-date invoices counted in 0-30 bucket (were dropped)
- **Rounding:** HALF_UP on all posting-path quantization (tax/VAT standard)
- New `test_accounting_correctness.py`: 10 regression tests (224/224 green)

### 📚 Richness: full global depreciation + LIFO (2026-09-18)
- `FixedAsset` now supports every globally used method: `straight_line`
  (+`half_year` convention), `declining_balance` with `rate_factor`
  (200%/150%/any), `sum_of_years`, `units_of_production` (IAS 16.62,
  with `record_production` capping), `macrs` (IRS GDS-3/5/7/10/15/20 tables
  + GDS-27.5/39 realty mid-month)
- `depreciation_schedule()` (per-asset) + `DepreciationEngine.generate_schedule()`
  — non-mutating planning tables; `MACRS_TABLES`, `SUPPORTED_METHODS` exported
- Inventory adds `lifo` (US GAAP; flagged as IAS 2-prohibited)
- 8 new richness regression tests (232/232 green)

### 🧹 Quality, scale & docs review (2026-09-18)
- Lint-clean: autoflake + manual pass, `flake8 F401/F841/F821/E9` zero findings;
  quoted-annotation names now backed by `TYPE_CHECKING` imports
- `print()` removed from library code (`SQLiteConnection` uses stdlib logging)
- `DuplicateDetector` signatures bounded at 50k (FIFO eviction)
- Backward-compat fix: `record_entry`/`post_entry` tolerate pre-posted entries
  (legacy post-then-record pattern) — direct double `post()` still raises
- `example.py` runs green on Windows (UTF-8 stdout) — was crashing on emoji
- README hero example corrected to verified figures (was stale: 103000/3000)- **Money-sign guards:** `Transaction`, `deposit/withdraw`, `InvoiceItem/pay`, `Payment`,
  `Inventory receive/issue`, `FX update_rate` now reject negative (and non-positive
  where meaningless) amounts — negative legs could invert books while "balanced"
- **Tax convention fix (critical):** `sell/buy/expense tax_rate` is now PERCENT
  library-wide (`15` = 15%); previously `15` computed 1500%. New `normalize_tax_rate()`
- **CSV injection:** `ReportExporter` neutralizes `= + - @`-leading cells
- **PDF markup:** `prepare_text` XML-escapes (`R&D <Ltd>` safe)
- **Passwords:** `verify_password` fail-closed parsing (no `assert`), iteration bounds
- **Config:** root `config.py` resolved from project root, never CWD (code-exec guard)
- **Notes:** content/author/entity sanitized on add/edit
- **API:** strict `debit|credit` sides, required description, narrow 404s, capped
  idempotency memory, Python 3.7-compatible typing
- **CLI:** clean errors on corrupt ledgers/periods (no tracebacks), output paths sanitized
- **DoS bounds:** audit log capped at 10k entries, idempotency keys capped at 10k
- **Imports:** `pyledger.security` validator exports are lazy (PEP 562) — fixes
  circular import while keeping `from pyledger.security import EntryValidator` working

## Version 1.0.0 (2026-03-14)

### Initial Release

#### ✨ Features

**Core Accounting**
- Account management with multiple account types
- Journal entry recording with automatic balancing
- General ledger management
- Trial balance reporting
- Multi-account transfers

**Invoicing & Payments**
- Invoice creation and management
- Line item tracking
- Payment recording and status tracking
- Payment receiver for managing collections
- Multiple payment methods support

**Tax Management**
- Tax calculation and tracking
- VAT/GST support
- Multiple tax rates
- Reverse tax calculation
- Tax calculator for multiple taxes

**Financial Reporting**
- Balance Sheet generation
- Income Statement (P&L) generation
- Cash Flow Statement generation
- Trial balance reports

**Multi-Currency Support**
- Support for multiple currencies (USD, EUR, GBP, SAR, AED, EGP, JOD, KWD)
- Currency conversion
- Money class for currency arithmetic
- Exchange rate management

**Validation & Error Handling**
- Comprehensive input validation
- Custom exceptions for accounting operations
- Account code validation
- Amount validation
- Currency validation
- Tax rate validation

**Database Support**
- SQLite integration
- In-memory repository implementation
- Extensible repository pattern
- Database connection pooling ready
- Support for PostgreSQL and MySQL (future versions)

**Utilities**
- Data formatting utilities
- Account code validation
- Amount formatting
- Currency symbol support
- Transaction history tracking

#### 🏗️ Project Structure

```
pyledger/
├── core/               # Core accounting components
│   ├── account.py     # Account management
│   ├── journal.py     # Journal entries
│   ├── ledger.py      # General ledger
│   └── transaction.py # Transactions
├── accounting/         # Accounting operations
│   ├── invoice.py     # Invoice management
│   ├── payment.py     # Payment processing
│   └── tax.py         # Tax calculations
├── reports/           # Financial reports
│   ├── balance_sheet.py  # Balance sheet & income statement
│   └── cash_flow.py      # Cash flow statement
├── database/          # Database layer
│   ├── models.py      # Data models
│   └── repository.py  # Repository pattern
├── utils/             # Utility functions
│   ├── validators.py  # Validation functions
│   ├── currency.py    # Currency management
│   └── formatter.py   # Formatting utilities
└── exceptions/        # Custom exceptions
    └── errors.py      # Exception definitions
```

#### 📚 Documentation

- Comprehensive README with usage examples
- Detailed API documentation
- Multiple code examples
- Installation instructions
- Configuration guide

#### 🧪 Testing

- Comprehensive test suite with pytest
- Unit tests for all major components
- Example test cases

#### 🔒 Validation

- Account code format validation
- Account type validation
- Amount validation
- Currency validation
- Tax rate validation
- Date validation

#### ⚠️ Custom Exceptions

- `PyLedgerException` - Base exception
- `AccountNotFoundError` - Account not found
- `UnbalancedEntryError` - Journal entry not balanced
- `InvalidAccountTypeError` - Invalid account type
- `InsufficientBalanceError` - Insufficient balance
- `DuplicateAccountError` - Duplicate account code
- `InvalidCurrencyError` - Invalid currency
- `InvalidTaxRateError` - Invalid tax rate
- `InvoiceNotFoundError` - Invoice not found
- `InvalidInvoiceStatusError` - Invalid invoice status

### ✅ What's Included

✓ Complete accounting system
✓ Invoice management
✓ Multi-currency support
✓ Tax calculations
✓ Financial reports
✓ Database integration ready
✓ Comprehensive error handling
✓ Data validation
✓ Transaction tracking
✓ Payment management
✓ Formatting utilities
✓ Currency conversion

### 📝 Notes

- This is a professional-grade accounting library suitable for:
  - Accounting software development
  - ERP systems
  - Invoice management systems
  - Expense tracking systems
  - Financial analysis tools

### 🚀 Future Roadmap

- ORM integration (SQLAlchemy)
- REST API integration (FastAPI/Django)
- Advanced financial ratios
- Budget management
- Audit trails
- Multi-company support
- Bank reconciliation
- Cost centers
- Profit centers
- Advanced reporting
- PDF invoice generation
- Email integration
- Webhook support

### 📄 License

MIT License - See LICENSE file for details

---

**Version 1.0.0** - Initial Release
**Release Date:** March 14, 2026
