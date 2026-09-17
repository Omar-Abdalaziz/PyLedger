"""
PyLedger - Comprehensive Test Suite
"""

import pytest
from decimal import Decimal
from datetime import datetime
from pyledger import (
    Account, Transaction, JournalEntry, Ledger,
    Tax, TaxCalculator, Invoice, InvoiceItem, InvoiceStatus,
    Payment, PaymentMethod, PaymentStatus, PaymentReceiver,
    Money, CurrencyConverter, Formatter,
    BusinessEngine, PyLedger, SmartChartOfAccounts,
    IncomeStatement, BalanceSheet, CashFlowStatement,
    EquityStatement, FinancialPeriod, BaseReport,
    ImmutableTransaction, AuditEntry, AuditTrail,
    ClosingEngine, FixedAsset, DepreciationEngine, DepreciationMethod,
    InventoryItem, InventoryManager, Customer, Supplier,
    Budget, BudgetVsActual, ConsolidationEngine, ConsolidatedReport,
    VATReturn, CorporateTaxReport, BudgetControl, BudgetExceededError,
    ComparativeIncomeStatement, ComparativeBalanceSheet, FinancialRatios,
    Config, config,
)
from pyledger.core.closing import PeriodClosedError
from pyledger.exceptions import (
    AccountNotFoundError, UnbalancedEntryError,
    InvalidAccountTypeError, InsufficientBalanceError,
    DuplicateAccountError, InvalidCurrencyError,
    InvalidTaxRateError,
)
from pyledger.accounting.tax import TaxCalculator as TaxCalc
from pyledger.security.sanitizer import (
    sanitize_text, sanitize_name, sanitize_account_code,
    sanitize_amount, sanitize_csv_field, sanitize_description,
    sanitize_email, sanitize_phone, sanitize_quantity, sanitize_percentage,
)
from pyledger.security.validator import (
    EntryValidator, DuplicateDetector, BusinessRuleError,
    validate_new_account, validate_invoice_items,
)
from pyledger.utils.validators import (
    validate_account_code, validate_account_type,
    validate_amount, validate_currency, validate_tax_rate,
    validate_date, format_amount, SUPPORTED_CURRENCIES,
)


# =============================================================================
# Core Tests
# =============================================================================

class TestAccount:
    def test_create_account(self):
        acc = Account('Cash', 'asset', '1000')
        assert acc.name == 'Cash'
        assert acc.type == 'asset'
        assert acc.code == '1000'
        assert acc.balance == Decimal('0')

    def test_invalid_account_type(self):
        with pytest.raises(InvalidAccountTypeError):
            Account('Test', 'invalid', '9999')

    def test_deposit(self):
        acc = Account('Cash', 'asset', '1000')
        acc.deposit(Decimal('1000'))
        assert acc.balance == Decimal('1000')

    def test_withdraw(self):
        acc = Account('Cash', 'asset', '1000', initial_balance=Decimal('1000'))
        acc.withdraw(Decimal('500'))
        assert acc.balance == Decimal('500')

    def test_insufficient_balance(self):
        acc = Account('Cash', 'asset', '1000')
        with pytest.raises(InsufficientBalanceError):
            acc.withdraw(Decimal('100'))

    def test_debit_credit_balance(self):
        acc = Account('Sales', 'income', '4000')
        acc.deposit(Decimal('5000'))
        assert acc.balance == Decimal('5000')

    def test_get_transactions(self):
        acc = Account('Cash', 'asset', '1000')
        acc.deposit(Decimal('100'))
        txns = acc.get_transactions()
        assert len(txns) == 1
        assert txns[0]['amount'] == Decimal('100')

    def test_get_balance_as_of(self):
        acc = Account('Cash', 'asset', '1000')
        acc.deposit(Decimal('200'))
        bal = acc.get_balance_as_of(datetime.now())
        assert bal == Decimal('200')

    def test_get_transactions_filtered(self):
        acc = Account('Cash', 'asset', '1000')
        acc.deposit(Decimal('300'))
        txns = acc.get_transactions(txn_type='deposit', limit=5)
        assert len(txns) == 1

    def test_to_dict(self):
        acc = Account('Cash', 'asset', '1000')
        d = acc.to_dict()
        assert d['code'] == '1000'
        assert d['type'] == 'asset'


class TestTransaction:
    def test_create_transaction(self):
        acc = Account('Cash', 'asset', '1000')
        txn = Transaction(acc, 'debit', Decimal('100'))
        assert txn.account.code == '1000'
        assert txn.type == 'debit'
        assert txn.amount == Decimal('100')

    def test_invalid_type(self):
        acc = Account('Cash', 'asset', '1000')
        with pytest.raises(ValueError):
            Transaction(acc, 'invalid', Decimal('100'))

    def test_to_dict(self):
        acc = Account('Cash', 'asset', '1000')
        txn = Transaction(acc, 'debit', Decimal('50'))
        d = txn.to_dict()
        assert d['type'] == 'debit'


class TestJournalEntry:
    def test_create_entry(self):
        entry = JournalEntry('Test entry')
        assert entry.description == 'Test entry'
        assert entry.number.startswith('JE-')

    def test_add_debit_credit(self):
        entry = JournalEntry('Test')
        cash = Account('Cash', 'asset', '1000')
        sales = Account('Sales', 'income', '4000')
        entry.add_debit(cash, Decimal('1000')).add_credit(sales, Decimal('1000'))
        assert entry.is_balanced()

    def test_unbalanced_entry_validation(self):
        entry = JournalEntry('Unbalanced')
        cash = Account('Cash', 'asset', '1000')
        entry.add_debit(cash, Decimal('500'))
        with pytest.raises(UnbalancedEntryError):
            entry.post()

    def test_post_entry(self):
        entry = JournalEntry('Post test')
        cash = Account('Cash', 'asset', '1000', initial_balance=Decimal('0'))
        sales = Account('Sales', 'income', '4000')
        entry.add_debit(cash, Decimal('2000')).add_credit(sales, Decimal('2000'))
        assert entry.post()
        assert entry.posted is True
        assert cash.balance == Decimal('2000')

    def test_to_dict(self):
        entry = JournalEntry('Dict test')
        d = entry.to_dict()
        assert 'number' in d
        assert 'debits' in d


class TestLedger:
    def test_create_ledger(self):
        ledger = Ledger('My Company', 'USD')
        assert ledger.name == 'My Company'
        assert ledger.currency == 'USD'

    def test_add_and_get_account(self):
        ledger = Ledger()
        acc = Account('Cash', 'asset', '1000')
        ledger.add_account(acc)
        retrieved = ledger.get_account('1000')
        assert retrieved.code == '1000'

    def test_duplicate_account(self):
        ledger = Ledger()
        ledger.add_account(Account('Cash', 'asset', '1000'))
        with pytest.raises(DuplicateAccountError):
            ledger.add_account(Account('Cash2', 'asset', '1000'))

    def test_account_not_found(self):
        ledger = Ledger()
        with pytest.raises(AccountNotFoundError):
            ledger.get_account('9999')

    def test_transfer(self):
        ledger = Ledger()
        cash = Account('Cash', 'asset', '1000', initial_balance=Decimal('5000'))
        bank = Account('Bank', 'asset', '1100')
        ledger.add_account(cash)
        ledger.add_account(bank)
        entry = ledger.transfer(cash, bank, Decimal('1000'))
        assert entry.is_balanced()
        assert cash.balance == Decimal('4000')
        assert bank.balance == Decimal('1000')

    def test_trial_balance(self):
        ledger = Ledger()
        ledger.add_account(Account('Cash', 'asset', '1000'))
        tb = ledger.trial_balance()
        assert abs(tb['total_debits'] - tb['total_credits']) < Decimal('0.01')

    def test_get_accounts_by_type(self):
        ledger = Ledger()
        ledger.add_account(Account('Cash', 'asset', '1000'))
        ledger.add_account(Account('AP', 'liability', '2000'))
        assets = ledger.get_accounts_by_type('asset')
        assert len(assets) == 1
        assert assets[0].code == '1000'


class TestTax:
    def test_tax_creation(self):
        tax = Tax('VAT', 15)
        assert tax.name == 'VAT'
        assert tax.rate == Decimal('15')

    def test_calculate_tax(self):
        tax = Tax('VAT', 15)
        result = tax.calculate(Decimal('1000'))
        assert result == Decimal('150.00')

    def test_total_with_tax(self):
        tax = Tax('VAT', 15)
        total = tax.calculate_total(Decimal('1000'))
        assert total == Decimal('1150.00')

    def test_reverse_calculation(self):
        result = Tax.reverse_calculate(Decimal('1150'), 15)
        assert result['base'] == Decimal('1000.00')
        assert result['tax_amount'] == Decimal('150.00')

    def test_tax_calculator(self):
        calc = TaxCalculator()
        calc.add_tax('VAT', 15).add_tax('GST', 10)
        result = calc.calculate_all(Decimal('1000'))
        assert 'VAT' in result['taxes']
        assert 'GST' in result['taxes']
        assert result['total_tax'] == Decimal('250.00')


class TestInvoice:
    def test_create_invoice(self):
        inv = Invoice('CUST-001')
        assert inv.customer == 'CUST-001'
        assert inv.status == InvoiceStatus.DRAFT

    def test_add_item(self):
        inv = Invoice('CUST-001')
        inv.add_item('Item 1', 2, Decimal('100'))
        assert len(inv.items) == 1
        assert inv.subtotal == Decimal('200.00')

    def test_apply_tax(self):
        inv = Invoice('CUST-001')
        inv.add_item('Item', 1, Decimal('1000'))
        inv.apply_tax('VAT', 15)
        assert inv.tax_total == Decimal('150.00')
        assert inv.total == Decimal('1150.00')

    def test_payment(self):
        inv = Invoice('CUST-001')
        inv.add_item('Item', 1, Decimal('1000'))
        inv.issue()
        inv.record_payment(Decimal('400'))
        assert inv.paid_amount == Decimal('400')
        assert inv.status == InvoiceStatus.PARTIALLY_PAID

    def test_full_payment(self):
        inv = Invoice('CUST-001')
        inv.add_item('Item', 1, Decimal('1000'))
        inv.apply_tax('VAT', 15)
        inv.issue()
        inv.record_payment(Decimal('1150'))
        assert inv.status == InvoiceStatus.PAID

    def test_cancel(self):
        inv = Invoice('CUST-001')
        inv.cancel()
        assert inv.status == InvoiceStatus.CANCELLED


class TestPayment:
    def test_create_payment(self):
        pmt = Payment(Decimal('500'), 'CUST-001')
        assert pmt.amount == Decimal('500')
        assert pmt.status == PaymentStatus.PENDING

    def test_process_payment(self):
        pmt = Payment(Decimal('500'), 'CUST-001')
        pmt.process()
        assert pmt.status == PaymentStatus.COMPLETED

    def test_fail_payment(self):
        pmt = Payment(Decimal('500'), 'CUST-001')
        pmt.fail('Insufficient funds')
        assert pmt.status == PaymentStatus.FAILED

    def test_refund_payment(self):
        pmt = Payment(Decimal('100'), 'CUST-001')
        pmt.process()
        pmt.refund()
        assert pmt.status == PaymentStatus.REFUNDED

    def test_payment_receiver(self):
        rcvr = PaymentReceiver('SUPP-001')
        assert rcvr.receiver_id == 'SUPP-001'


class TestValidators:
    def test_account_code(self):
        assert validate_account_code('1000')
        assert not validate_account_code('')

    def test_account_type(self):
        assert validate_account_type('asset')
        assert validate_account_type('liability')
        assert not validate_account_type('invalid')

    def test_amount(self):
        assert validate_amount(100)
        assert validate_amount(Decimal('50.00'))
        assert not validate_amount(-100)

    def test_currency(self):
        assert validate_currency('USD')
        assert not validate_currency('INVALID')

    def test_tax_rate(self):
        assert validate_tax_rate(15)
        assert validate_tax_rate(0)
        with pytest.raises(InvalidTaxRateError):
            validate_tax_rate(-5)

    def test_date(self):
        assert validate_date(datetime.now())
        assert not validate_date('invalid')

    def test_format_amount(self):
        result = format_amount(Decimal('1234.5'))
        assert result == Decimal('1234.50')


class TestCurrency:
    def test_money_creation(self):
        m = Money(100, 'USD')
        assert m.amount == Decimal('100')
        assert m.currency == 'USD'

    def test_money_add(self):
        m1 = Money(100, 'USD')
        m2 = Money(50, 'USD')
        result = m1 + m2
        assert result.amount == Decimal('150')

    def test_money_cross_currency_add(self):
        usd = Money(100, 'USD')
        eur = Money(100, 'EUR')
        result = usd + eur
        assert result.currency == 'USD'
        assert float(result.amount) > 0

    def test_money_mul(self):
        m = Money(100, 'USD')
        result = m * 2
        assert result.amount == Decimal('200')

    def test_currency_converter(self):
        converter = CurrencyConverter()
        result = converter.convert(Decimal('100'), 'USD', 'EUR')
        assert float(result) > 0
        assert float(result) < 100

    def test_get_symbol(self):
        from pyledger.utils.currency import CurrencyConverter
        converter = CurrencyConverter()
        assert '$' in converter.get_symbol('USD')

    def test_money_conversion(self):
        m = Money(100, 'USD')
        converted = m.convert_to('EUR')
        assert converted.currency == 'EUR'
        assert float(converted.amount) > 0

    def test_money_equality_same_currency(self):
        m1 = Money(100, 'USD')
        m2 = Money(100, 'USD')
        assert m1 == m2

    def test_money_comparison(self):
        m1 = Money(100, 'USD')
        m2 = Money(200, 'USD')
        assert m1 < m2
        assert m2 > m1

    def test_money_negation(self):
        m = Money(100, 'USD')
        assert (-m).amount == Decimal('-100')

    def test_money_absolute(self):
        m = Money(-50, 'USD')
        assert abs(m).amount == Decimal('50')

    def test_money_repr(self):
        m = Money(100, 'USD')
        assert 'Money' in repr(m)

    def test_money_str(self):
        m = Money(100.50, 'USD')
        assert '$' in str(m)


class TestFinancialPeriod:
    def test_monthly(self):
        p = FinancialPeriod.monthly(2026, 7)
        assert p.start_date.month == 7
        assert p.end_date.month == 7
        assert '2026-07' in p.label

    def test_quarterly(self):
        p = FinancialPeriod.quarterly(2026, 2)
        assert p.start_date.month == 4
        assert 'Q2' in p.label

    def test_annual(self):
        p = FinancialPeriod.annual(2026)
        assert p.start_date.year == 2026
        assert p.end_date.year == 2026

    def test_invalid_period(self):
        with pytest.raises(ValueError):
            FinancialPeriod(datetime(2026, 12, 31), datetime(2026, 1, 1))


class TestIncomeStatement:
    def test_generate(self):
        ledger = Ledger()
        ledger.add_account(Account('Sales', 'income', '4000'))
        stmt = IncomeStatement(ledger)
        data = stmt.generate()
        assert 'title' in data
        assert 'items' in data


class TestBalanceSheet:
    def test_generate(self):
        ledger = Ledger()
        ledger.add_account(Account('Cash', 'asset', '1000'))
        bs = BalanceSheet(ledger)
        data = bs.generate()
        assert 'assets' in data
        assert 'total_assets' in data


class TestCashFlowStatement:
    def test_generate(self):
        ledger = Ledger()
        ledger.add_account(Account('Cash', 'asset', '1000'))
        cf = CashFlowStatement(ledger)
        data = cf.generate()
        assert 'operating' in data


class TestEquityStatement:
    def test_generate(self):
        ledger = Ledger()
        ledger.add_account(Account('Equity', 'equity', '3000'))
        eq = EquityStatement(ledger)
        data = eq.generate()
        assert 'opening_balances' in data or 'closing_balances' in data


class TestBusinessEngine:
    def test_create_engine(self):
        app = BusinessEngine(company_name='Test Co', currency='USD')
        assert app.company_name == 'Test Co'

    def test_add_investment(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        result = app.add_investment('Owner', 10000)
        assert result is not None

    def test_record_sale(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        result = app.sell(
            items=[{'name': 'Product', 'quantity': 1, 'price': 500}],
            customer='CUST-001',
            payment_method='cash',
        )
        assert result is not None

    def test_record_expense(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        result = app.pay_expense('Rent', 2000, category='rent')
        assert result is not None

    def test_pay_salary(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        result = app.pay_salary('John', 5000, deductions={'tax': 500})
        assert result is not None

    def test_buy_fixed_asset(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        result = app.buy_fixed_asset('Server', 15000, useful_life=5)
        assert result is not None

    def test_full_accounting_cycle(self):
        app = BusinessEngine(company_name='Test Co', currency='USD')
        app.add_investment('Owner', 100000)
        app.sell([{'name': 'Service', 'quantity': 1, 'price': 5000}], 'C-1', 'cash')
        app.pay_expense('Rent', 2000, 'rent')
        app.buy_fixed_asset('Equipment', 30000, 10)
        is_balanced = app.ledger.trial_balance()
        assert abs(is_balanced['total_debits'] - is_balanced['total_credits']) < Decimal('0.01')

    def test_pyledger_facade(self):
        app = PyLedger(company="Test Corp", currency="USD")
        assert isinstance(app, BusinessEngine)


class TestPDFEngine:
    def test_generate_pdf(self):
        from pyledger.pdf import PDFEngine
        from pyledger.pdf.branding import CompanyInfo
        pdf = PDFEngine(Ledger('Test'))
        pdf.add_report(IncomeStatement(Ledger()))
        pdf_bytes = pdf.to_bytes()
        assert len(pdf_bytes) > 0

    def test_pdf_company_info(self):
        from pyledger.pdf import CompanyInfo
        ci = CompanyInfo(name='Test Corp', vat_number='12345')
        assert ci.name == 'Test Corp'


class TestSmartChartOfAccounts:
    def test_create_chart(self):
        chart = SmartChartOfAccounts()
        assert len(chart.accounts) > 10
        assert chart.industry == 'general'

    def test_add_to_ledger(self):
        chart = SmartChartOfAccounts()
        ledger = Ledger()
        chart.add_to_ledger(ledger)
        assert len(ledger.accounts) > 10

    def test_get_by_type(self):
        chart = SmartChartOfAccounts()
        assets = chart.get_by_type('asset')
        assert all(a.type == 'asset' for a in assets)
        assert len(assets) > 5


class TestImmutableAndAudit:
    def test_immutable_txn(self):
        txn = ImmutableTransaction('1000', 'Cash', 'debit', Decimal('500'),
                                    datetime(2026, 1, 15), 'test', 'JE-1', 1)
        assert txn.account_code == '1000'
        assert txn.amount == Decimal('500')
        import dataclasses
        assert dataclasses.fields(txn)

    def test_audit_trail(self):
        trail = AuditTrail()
        trail.record('create', 'entry', 'JE-1', user='admin')
        trail.record('post', 'entry', 'JE-1', user='admin')
        assert len(trail.get_entries()) == 2
        assert trail.verify_chain()

    def test_audit_filters(self):
        trail = AuditTrail()
        trail.record('create', 'entry', '1', user='admin')
        trail.record('create', 'account', '1000', user='admin')
        assert len(trail.get_entries(entity_type='entry')) == 1
        assert len(trail.get_entries(entity_type='account')) == 1

    def test_audit_entity_id_filter(self):
        trail = AuditTrail()
        trail.record('create', 'entry', 'JE-1', user='admin')
        trail.record('update', 'entry', 'JE-2', user='admin')
        assert len(trail.get_entries(entity_id='JE-1')) == 1


class TestClosingEngine:
    def test_close_month(self):
        ledger = Ledger('Test', 'USD')
        ledger.add_account(Account('Sales', 'income', '4000'))
        ledger.add_account(Account('Expenses', 'expense', '5000'))
        ledger.add_account(Account('Retained Earnings', 'equity', '3100'))
        ce = ClosingEngine(ledger)
        result = ce.close_month(2026, 1)
        assert result['period'] == '2026-01'

    def test_double_close_raises(self):
        ledger = Ledger('Test', 'USD')
        ledger.add_account(Account('Sales', 'income', '4000'))
        ledger.add_account(Account('Expenses', 'expense', '5000'))
        ledger.add_account(Account('Retained Earnings', 'equity', '3100'))
        ce = ClosingEngine(ledger)
        ce.close_month(2026, 1)
        with pytest.raises((ValueError, PeriodClosedError)):
            ce.close_month(2026, 1)

    def test_close_quarter(self):
        ledger = Ledger('Test', 'USD')
        ledger.add_account(Account('Sales', 'income', '4000'))
        ledger.add_account(Account('Expenses', 'expense', '5000'))
        ledger.add_account(Account('Retained Earnings', 'equity', '3100'))
        ce = ClosingEngine(ledger)
        result = ce.close_quarter(2026, 1)
        assert result['period'] == '2026 Q1'


class TestFixedAsset:
    def test_straight_line(self):
        asset = FixedAsset('Machine', 100000, 'FA-001', 5,
                            DepreciationMethod.STRAIGHT_LINE)
        dep = asset.annual_depreciation()
        assert dep == Decimal('20000.00')

    def test_declining_balance(self):
        asset = FixedAsset('Machine', 100000, 'FA-002', 5,
                            DepreciationMethod.DECLINING_BALANCE)
        dep = asset.annual_depreciation()
        assert dep == Decimal('40000.00')

    def test_net_book_value(self):
        asset = FixedAsset('Machine', 100000, 'FA-003', 5,
                            DepreciationMethod.STRAIGHT_LINE)
        asset.accumulated_depreciation = Decimal('40000')
        assert asset.net_book_value == Decimal('60000.00')


class TestInventoryItem:
    def test_receive_fifo(self):
        item = InventoryItem('SKU-001', 'Widget')
        item.receive(10, Decimal('100'))
        assert item.current_qty == 10

    def test_weighted_average(self):
        item = InventoryItem('SKU-002', 'Gadget')
        item.receive(10, Decimal('100'))
        item.receive(10, Decimal('200'))
        wac = item.weighted_average_cost()
        assert wac == Decimal('150.00')

    def test_issue_reduces_qty(self):
        item = InventoryItem('SKU-003', 'Thing')
        item.receive(10, Decimal('100'))
        item.issue(3)
        assert item.current_qty == 7

    def test_issue_insufficient(self):
        item = InventoryItem('SKU-004', 'Gizmo')
        item.receive(5, Decimal('100'))
        with pytest.raises(ValueError):
            item.issue(10)


class TestCRM:
    def test_customer_creation(self):
        c = Customer('Acme Corp', 'CUST-001', tax_id='12345')
        assert c.name == 'Acme Corp'
        assert c.customer_id == 'CUST-001'

    def test_supplier_creation(self):
        s = Supplier('Vendor Inc', 'SUPP-001')
        assert s.name == 'Vendor Inc'
        assert s.supplier_id == 'SUPP-001'

    def test_customer_get_balance(self):
        c = Customer('Test', 'C-1')
        assert c.get_balance() == Decimal('0')


class TestAgingReport:
    def test_receivable_aging_structure(self):
        from pyledger.accounting.aging import ReceivableAging
        ledger = Ledger()
        r = ReceivableAging(ledger, [])
        data = r.generate()
        assert 'customers' in data
        assert 'brackets' in data
        assert data['grand_total'] == '0'

    def test_payable_aging_structure(self):
        from pyledger.accounting.aging import PayableAging
        ledger = Ledger()
        r = PayableAging(ledger, [])
        data = r.generate()
        assert 'suppliers' in data
        assert 'brackets' in data


class TestBudget:
    def test_budget_amounts(self):
        p = FinancialPeriod.monthly(2026, 7)
        b = Budget('Test Budget', p)
        b.set_amount('4000', Decimal('10000'))
        b.set_amount('5000', Decimal('5000'))
        assert b.get_amount('4000') == Decimal('10000')
        assert b.get_amount('5000') == Decimal('5000')
        assert b.get_total() == Decimal('15000')

    def test_budget_to_dict(self):
        p = FinancialPeriod.monthly(2026, 7)
        b = Budget('B', p)
        d = b.to_dict()
        assert d['name'] == 'B'

    def test_budget_vs_actual_structure(self):
        ledger = Ledger()
        ledger.add_account(Account('Sales', 'income', '4000'))
        ledger.add_account(Account('Expenses', 'expense', '5000'))
        p = FinancialPeriod.monthly(2026, 7)
        b = Budget('B', p)
        b.set_amount('4000', Decimal('5000'))
        r = BudgetVsActual(ledger, b, period=p)
        data = r.generate()
        assert 'lines' in data
        assert 'total_budget' in data


class TestConsolidation:
    def test_consolidation_engine(self):
        l1 = Ledger('Parent', 'USD')
        l2 = Ledger('Sub', 'USD')
        l1.add_account(Account('Cash', 'asset', '1000'))
        l2.add_account(Account('Cash', 'asset', '1000'))
        engine = ConsolidationEngine(l1, [l2])
        result = engine.get_consolidated_ledger()
        assert result['entity_count'] == 2

    def test_elimination_entry(self):
        l1 = Ledger('P', 'USD')
        l2 = Ledger('S', 'USD')
        engine = ConsolidationEngine(l1, [l2])
        engine.add_elimination('1000', '2000', Decimal('500'), 'Intercompany loan')
        assert len(engine.elimination_entries) == 1

    def test_consolidated_report(self):
        l1 = Ledger('P', 'USD')
        l2 = Ledger('S', 'USD')
        engine = ConsolidationEngine(l1, [l2])
        p = FinancialPeriod.monthly(2026, 1)
        r = ConsolidatedReport(engine, p)
        data = r.generate()
        assert data['entities'] == 2


class TestTaxReports:
    def test_vat_return_structure(self):
        ledger = Ledger()
        ledger.add_account(Account('Sales', 'income', '4000'))
        p = FinancialPeriod.monthly(2026, 7)
        vat = VATReturn(ledger, p)
        data = vat.generate()
        assert 'vat_payable' in data
        assert 'vat_receivable' in data

    def test_corporate_tax_structure(self):
        ledger = Ledger()
        ledger.add_account(Account('Sales', 'income', '4000'))
        p = FinancialPeriod.monthly(2026, 7)
        ct = CorporateTaxReport(ledger, p)
        data = ct.generate()
        assert 'total_income' in data

    def test_corporate_tax_different_countries(self):
        ledger = Ledger()
        p = FinancialPeriod.monthly(2026, 7)
        ct_sa = CorporateTaxReport(ledger, p, country='SA')
        ct_ae = CorporateTaxReport(ledger, p, country='AE')
        assert ct_sa.tax_rate == Decimal('20')
        assert ct_ae.tax_rate == Decimal('9')

    def test_vat_return_text_format(self):
        ledger = Ledger()
        p = FinancialPeriod.monthly(2026, 7)
        vat = VATReturn(ledger, p)
        text = str(vat)
        assert 'VAT' in text

    def test_corporate_tax_text_format(self):
        ledger = Ledger()
        p = FinancialPeriod.monthly(2026, 7)
        ct = CorporateTaxReport(ledger, p)
        text = str(ct)
        assert 'TAX' in text.upper()


class TestComparativeReports:
    def test_comparative_income_structure(self):
        ledger = Ledger('Test', 'USD')
        ledger.add_account(Account('Sales', 'income', '4000'))
        p1 = FinancialPeriod.monthly(2026, 1)
        p2 = FinancialPeriod.monthly(2026, 2)
        r = ComparativeIncomeStatement(ledger, [p1, p2])
        data = r.generate()
        assert 'periods' in data
        assert len(data['periods']) == 2

    def test_comparative_balance_sheet_structure(self):
        ledger = Ledger('Test', 'USD')
        p1 = FinancialPeriod.monthly(2026, 1)
        p2 = FinancialPeriod.monthly(2026, 2)
        r = ComparativeBalanceSheet(ledger, [p1, p2])
        data = r.generate()
        assert 'periods' in data
        assert len(data['columns']) == 2


class TestFinancialRatios:
    def test_ratios_generation(self):
        ledger = Ledger('Test', 'USD')
        ledger.add_account(Account('Cash', 'asset', '1000'))
        ledger.add_account(Account('AP', 'liability', '2000'))
        p = FinancialPeriod.monthly(2026, 7)
        r = FinancialRatios(ledger, period=p)
        data = r.generate()
        assert 'liquidity' in data
        assert 'profitability' in data
        assert 'leverage' in data
        assert 'efficiency' in data

    def test_ratios_text_format(self):
        ledger = Ledger()
        ledger.add_account(Account('Cash', 'asset', '1000'))
        p = FinancialPeriod.monthly(2026, 7)
        r = FinancialRatios(ledger, period=p)
        text = str(r)
        assert 'RATIOS' in text.upper()

    def test_safe_division_by_zero(self):
        ledger = Ledger()
        p = FinancialPeriod.monthly(2026, 7)
        r = FinancialRatios(ledger, period=p)
        data = r.generate()
        assert data['liquidity']['current_ratio'] is not None


class TestConfig:
    def test_config_defaults(self):
        assert config.get('DEFAULT_CURRENCY') == 'USD'
        assert config.get('DECIMAL_PLACES') == 2

    def test_config_set_get(self):
        config.set('TEST_KEY', 'value')
        assert config['TEST_KEY'] == 'value'

    def test_config_contains(self):
        assert 'DEFAULT_CURRENCY' in config


class TestSecurity:
    def test_user_creation(self):
        from pyledger.core.security import User, Role
        u = User('admin', Role.ADMIN, 'Admin User')
        assert u.username == 'admin'
        assert u.role == Role.ADMIN

    def test_permission_check(self):
        from pyledger.core.security import User, Role, Permission
        admin = User('admin', Role.ADMIN)
        viewer = User('viewer', Role.VIEWER)
        assert admin.has_permission(Permission.CLOSE_PERIOD)
        assert not viewer.has_permission(Permission.CLOSE_PERIOD)

    def test_security_manager(self):
        from pyledger.core.security import SecurityManager, Role, Permission
        sm = SecurityManager()
        sm.register_user('admin', Role.ADMIN)
        sm.authenticate('admin')
        assert sm.check_permission(Permission.MANAGE_USERS)

    def test_require_permission_raises(self):
        from pyledger.core.security import SecurityManager, Role, Permission
        sm = SecurityManager()
        sm.register_user('viewer', Role.VIEWER)
        sm.authenticate('viewer')
        with pytest.raises(PermissionError):
            sm.require_permission(Permission.CLOSE_PERIOD)

    def test_audit_log(self):
        from pyledger.core.security import SecurityManager, Role
        sm = SecurityManager()
        sm.register_user('admin', Role.ADMIN)
        sm.authenticate('admin')
        log = sm.get_audit_log()
        assert len(log) == 1
        assert log[0]['action'] == 'LOGIN'


class TestWorkflow:
    def test_workflow_entry_creation(self):
        from pyledger.core.workflow import WorkflowEngine, EntryStatus
        we = WorkflowEngine()
        entry = we.create_entry('Test entry', 'admin', Decimal('5000'))
        assert entry.status == EntryStatus.DRAFT

    def test_full_approval_flow(self):
        from pyledger.core.workflow import WorkflowEngine, EntryStatus
        we = WorkflowEngine()
        entry = we.create_entry('Test', 'admin', Decimal('1000'))
        entry.add_step('Manager Approval')
        entry.add_step('Director Approval')
        entry.submit()
        assert entry.status == EntryStatus.PENDING_APPROVAL
        entry.approve(0, 'manager')
        assert entry.status == EntryStatus.PENDING_APPROVAL
        entry.approve(1, 'director')
        assert entry.status == EntryStatus.APPROVED
        entry.post()
        assert entry.status == EntryStatus.POSTED

    def test_rejection(self):
        from pyledger.core.workflow import WorkflowEngine, EntryStatus
        we = WorkflowEngine()
        entry = we.create_entry('Test', 'user', Decimal('500'))
        entry.add_step('Approve').submit()
        entry.reject(0, 'manager', 'Not approved')
        assert entry.status == EntryStatus.REJECTED

    def test_get_pending(self):
        from pyledger.core.workflow import WorkflowEngine
        we = WorkflowEngine()
        we.create_entry('E1', 'user1', Decimal('100')).add_step('A').submit()
        we.create_entry('E2', 'user2', Decimal('200')).add_step('A').submit()
        assert len(we.get_pending()) == 2


class TestContracts:
    def test_contract_creation(self):
        from pyledger.core.contracts import Contract, ContractType
        c = Contract('Lease', ContractType.LEASE, 'Vendor',
                      datetime(2026, 1, 1), datetime(2028, 12, 31), Decimal('24000'))
        assert c.title == 'Lease'
        assert c.value == Decimal('24000')

    def test_activate_and_check(self):
        from pyledger.core.contracts import Contract, ContractType, ContractStatus
        c = Contract('Svc', ContractType.SERVICE, 'Client',
                      datetime(2025, 1, 1), datetime(2030, 12, 31))
        c.activate()
        assert c.status == ContractStatus.ACTIVE
        assert c.is_active()

    def test_contract_manager(self):
        from pyledger.core.contracts import Contract, ContractManager, ContractType
        cm = ContractManager()
        c = Contract('L1', ContractType.LEASE, 'V1',
                      datetime(2026, 1, 1), datetime(2028, 12, 31))
        c.activate()
        cm.add(c)
        assert len(cm.get_active()) == 1

    def test_days_remaining(self):
        from pyledger.core.contracts import Contract, ContractType
        c = Contract('L', ContractType.LEASE, 'V',
                      datetime(2025, 1, 1), datetime(2030, 12, 31))
        c.activate()
        assert c.days_remaining() > 0

    def test_contract_status_transitions(self):
        from pyledger.core.contracts import Contract, ContractType, ContractStatus
        c = Contract('T', ContractType.OTHER, 'P',
                      datetime(2026, 1, 1), datetime(2026, 12, 31))
        c.activate()
        assert c.status == ContractStatus.ACTIVE
        c.complete()
        assert c.status == ContractStatus.COMPLETED


class TestNotes:
    def test_note_creation(self):
        from pyledger.core.notes import NoteManager
        nm = NoteManager()
        note = nm.add('Test note', 'admin', 'invoice', 'INV-001')
        assert note.content == 'Test note'

    def test_get_by_entity(self):
        from pyledger.core.notes import NoteManager
        nm = NoteManager()
        nm.add('Note 1', 'admin', 'invoice', 'INV-001')
        nm.add('Note 2', 'user', 'invoice', 'INV-001')
        assert len(nm.get_by_entity('invoice', 'INV-001')) == 2

    def test_get_recent(self):
        from pyledger.core.notes import NoteManager
        nm = NoteManager()
        for i in range(5):
            nm.add(f'Note {i}', 'admin', 'invoice', f'INV-{i}')
        assert len(nm.get_recent(limit=3)) == 3

    def test_delete_note(self):
        from pyledger.core.notes import NoteManager
        nm = NoteManager()
        note = nm.add('Delete me', 'admin')
        assert nm.delete(note.note_id) is True

    def test_edit_note(self):
        from pyledger.core.notes import NoteManager
        nm = NoteManager()
        note = nm.add('Original', 'admin')
        note.edit('Updated')
        assert note.content == 'Updated'


class TestEnhancedCashFlow:
    def test_indirect_method(self):
        ledger = Ledger()
        ledger.add_account(Account('Sales', 'income', '4000'))
        ledger.add_account(Account('Expenses', 'expense', '5000'))
        p = FinancialPeriod.monthly(2026, 7)
        cf = CashFlowStatement(ledger, period=p, method='indirect')
        data = cf.generate()
        assert data['method'] == 'indirect'

    def test_direct_method(self):
        ledger = Ledger()
        ledger.add_account(Account('Sales', 'income', '4000'))
        ledger.add_account(Account('Cogs', 'expense', '5000'))
        p = FinancialPeriod.monthly(2026, 7)
        cf = CashFlowStatement(ledger, period=p, method='direct')
        data = cf.generate()
        assert data['method'] == 'direct'

    def test_invalid_method(self):
        ledger = Ledger()
        with pytest.raises(ValueError):
            CashFlowStatement(ledger, method='invalid')

    def test_text_output(self):
        ledger = Ledger()
        p = FinancialPeriod.monthly(2026, 7)
        cf = CashFlowStatement(ledger, period=p)
        text = str(cf)
        assert 'CASH FLOW' in text.upper()


class TestBankReconciliation:
    def test_reconciliation_structure(self):
        from pyledger.accounting.bank_reconciliation import BankReconciliation
        ledger = Ledger()
        br = BankReconciliation(ledger, '1000')
        data = br.reconcile()
        assert 'ledger_balance' in data
        assert 'statement_balance' in data
        assert 'is_reconciled' in data

    def test_report_text(self):
        from pyledger.accounting.bank_reconciliation import BankReconciliation
        ledger = Ledger()
        br = BankReconciliation(ledger, '1000')
        text = br.generate_report()
        assert 'RECONCILIATION' in text.upper()

    def test_add_statement_line(self):
        from pyledger.accounting.bank_reconciliation import BankReconciliation
        ledger = Ledger()
        br = BankReconciliation(ledger, '1000')
        br.add_statement_line(datetime.now(), 'Deposit', Decimal('5000'))
        assert len(br.bank_statement_lines) == 1


class TestProjectAccounting:
    def test_project_creation(self):
        from pyledger.accounting.projects import Project
        p = Project('PRJ-001', 'Website', budget=Decimal('50000'))
        assert p.name == 'Website'
        assert p.budget == Decimal('50000')

    def test_add_transaction(self):
        from pyledger.accounting.projects import Project
        p = Project('PRJ-001', 'Project')
        p.add_transaction('Server cost', Decimal('5000'), '5000')
        assert len(p.transactions) == 1
        assert p.get_total_cost() == Decimal('5000')

    def test_budget_utilization(self):
        from pyledger.accounting.projects import Project
        p = Project('P1', 'P', budget=Decimal('10000'))
        p.add_transaction('Cost', Decimal('2500'), '5000')
        assert p.get_budget_utilization() == 25.0
        assert not p.is_over_budget()
        p.add_transaction('More', Decimal('8000'), '5000')
        assert p.is_over_budget()

    def test_project_manager(self):
        from pyledger.accounting.projects import Project, ProjectManager
        pm = ProjectManager()
        pm.add_project(Project('P1', 'Project 1'))
        pm.add_project(Project('P2', 'Project 2'))
        assert len(pm.get_all()) == 2

    def test_project_profitability(self):
        from pyledger.accounting.projects import Project, ProjectManager, ProjectProfitability
        ledger = Ledger()
        pm = ProjectManager()
        p = Project('P1', 'P')
        p.add_transaction('Revenue', Decimal('10000'), '4000', 'income')
        p.add_transaction('Cost', Decimal('6000'), '5000', 'expense')
        pm.add_project(p)
        pr = ProjectProfitability(ledger, pm)
        data = pr.generate()
        assert len(data['projects']) == 1
        assert Decimal(data['projects'][0]['profit']) == Decimal('4000')

    def test_project_to_dict(self):
        from pyledger.accounting.projects import Project
        p = Project('P1', 'Project')
        d = p.to_dict()
        assert d['project_id'] == 'P1'


class TestDeferredRevenue:
    def test_creation(self):
        from pyledger.accounting.deferred import DeferredRevenue
        dr = DeferredRevenue('Subscription', Decimal('12000'),
                              datetime(2026, 1, 1), datetime(2026, 12, 31))
        assert dr.total_amount == Decimal('12000')
        assert dr.get_deferred_balance() == Decimal('12000')

    def test_monthly_recognition(self):
        from pyledger.accounting.deferred import DeferredRevenue
        dr = DeferredRevenue('Sub', Decimal('1200'),
                              datetime(2026, 1, 1), datetime(2026, 12, 31))
        assert dr.get_monthly_amount() == Decimal('100.00')

    def test_generate_schedule(self):
        from pyledger.accounting.deferred import DeferredRevenue
        dr = DeferredRevenue('Sub', Decimal('1200'),
                              datetime(2026, 1, 1), datetime(2026, 12, 31))
        sched = dr.generate_schedule()
        assert len(sched) == 12

    def test_recognize(self):
        from pyledger.accounting.deferred import DeferredRevenue
        dr = DeferredRevenue('Sub', Decimal('1200'),
                              datetime(2026, 1, 1), datetime(2026, 12, 31))
        dr.generate_schedule()
        result = dr.recognize('2026-01')
        assert result['period'] == '2026-01'
        assert dr.recognized_amount == Decimal('100.00')

    def test_full_recognition(self):
        from pyledger.accounting.deferred import DeferredRevenue
        dr = DeferredRevenue('Sub', Decimal('1200'),
                              datetime(2026, 1, 1), datetime(2026, 12, 31))
        dr.generate_schedule()
        for i in range(1, 13):
            dr.recognize(f'2026-{i:02d}')
        assert dr.recognized_amount == Decimal('1200.00')
        assert dr.get_deferred_balance() == Decimal('0')


class TestPrepaidExpense:
    def test_creation(self):
        from pyledger.accounting.deferred import PrepaidExpense
        pe = PrepaidExpense('Insurance', Decimal('6000'),
                             datetime(2026, 1, 1), datetime(2026, 12, 31))
        assert pe.total_amount == Decimal('6000')

    def test_amortize(self):
        from pyledger.accounting.deferred import PrepaidExpense
        pe = PrepaidExpense('Insurance', Decimal('1200'),
                             datetime(2026, 1, 1), datetime(2026, 12, 31))
        pe.generate_schedule()
        result = pe.amortize('2026-01')
        assert result['period'] == '2026-01'

    def test_schedule_length(self):
        from pyledger.accounting.deferred import PrepaidExpense
        pe = PrepaidExpense('Ins', Decimal('600'),
                             datetime(2026, 1, 1), datetime(2026, 6, 30))
        sched = pe.generate_schedule()
        assert len(sched) == 6  # Jan to Jun


class TestBudgetControl:
    def test_creation(self):
        p = FinancialPeriod.monthly(2026, 7)
        from pyledger.core.ledger import Ledger
        bc = BudgetControl(Budget('B', p), Ledger())
        assert bc.enabled is True

    def test_disable(self):
        p = FinancialPeriod.monthly(2026, 7)
        from pyledger.core.ledger import Ledger
        bc = BudgetControl(Budget('B', p), Ledger())
        bc.disable()
        assert bc.enabled is False

    def test_budget_exceeded_error(self):
        err = BudgetExceededError("Over budget")
        assert str(err) == "Over budget"


class TestCSVExport:
    def test_export_income_statement(self):
        from pyledger.reports.export import ReportExporter
        ledger = Ledger()
        ledger.add_account(Account('Sales', 'income', '4000'))
        stmt = IncomeStatement(ledger)
        csv_data = ReportExporter.to_csv(stmt)
        assert csv_data is not None

    def test_export_aging(self):
        from pyledger.reports.export import ReportExporter
        data = {
            'title': 'Aging Report', 'as_of_date': '2026-07-11',
            'customers': [{'name': 'C1', 'total': '1000',
                           'brackets': {'0-30 Days': '1000'}}],
            'grand_total': '1000',
        }
        csv_data = ReportExporter.export_aging(data)
        assert 'C1' in csv_data

    def test_export_ratios(self):
        from pyledger.reports.export import ReportExporter
        data = {'title': 'Ratios', 'liquidity': {'current_ratio': '1.5'}}
        csv_data = ReportExporter.export_ratios(data)
        assert 'current_ratio' in csv_data


class TestBusinessEngineIntegration:
    def test_new_report_methods_exist(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        assert hasattr(app, 'financial_ratios')
        assert hasattr(app, 'vat_return')
        assert hasattr(app, 'corporate_tax')
        assert hasattr(app, 'create_customer')
        assert hasattr(app, 'create_supplier')
        assert hasattr(app, 'create_fixed_asset')
        assert hasattr(app, 'create_inventory_item')
        assert hasattr(app, 'create_budget')
        assert hasattr(app, 'bank_reconciliation')
        assert hasattr(app, 'create_project')
        assert hasattr(app, 'create_deferred_revenue')
        assert hasattr(app, 'create_prepaid_expense')
        assert hasattr(app, 'export_csv')

    def test_cash_flow_with_method(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        p = FinancialPeriod.monthly(2026, 1)
        cf = app.cash_flow(period=p, method='direct')
        data = cf.generate()
        assert data['method'] == 'direct'

    def test_create_customer_via_engine(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        c = app.create_customer('Acme', 'C-1')
        assert c.name == 'Acme'

    def test_integration_create_and_report(self):
        app = BusinessEngine(company_name='Test', auto_setup=True)
        p = FinancialPeriod.monthly(2026, 7)
        r = app.financial_ratios(period=p)
        data = r.generate()
        assert 'liquidity' in data


# ═══════════════════════════════════════════════════════════════
# SECURITY / VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════


class TestSanitizer:
    def test_sanitize_text_removes_html(self):
        result = sanitize_text('<script>alert("xss")</script>Hello')
        assert 'alert' not in result
        assert 'Hello' in result
        assert '<script>' not in result

    def test_sanitize_text_truncates_long(self):
        long = 'A' * 1000
        result = sanitize_text(long, max_length=50)
        assert len(result) == 50

    def test_sanitize_name_removes_sql_keywords(self):
        result = sanitize_name("Account; DROP TABLE users")
        assert 'DROP' not in result.upper()

    def test_sanitize_account_code_valid(self):
        assert sanitize_account_code('1000') == '1000'
        assert sanitize_account_code('fix-asset') == 'FIX-ASSET'

    def test_sanitize_account_code_invalid_raises(self):
        with pytest.raises(ValueError):
            sanitize_account_code('')
        with pytest.raises(ValueError):
            sanitize_account_code('toolong_account_code_12345')
        with pytest.raises(ValueError):
            sanitize_account_code('invalid chars!')

    def test_sanitize_amount_valid(self):
        result = sanitize_amount('1000.50')
        assert result == Decimal('1000.50')

    def test_sanitize_amount_negative_not_allowed(self):
        with pytest.raises(ValueError):
            sanitize_amount('-100', allow_negative=False)

    def test_sanitize_amount_negative_allowed(self):
        result = sanitize_amount('-100', allow_negative=True)
        assert result == Decimal('-100.00')

    def test_sanitize_amount_zero_not_allowed(self):
        with pytest.raises(ValueError):
            sanitize_amount('0', allow_zero=False)

    def test_sanitize_amount_too_many_decimals(self):
        with pytest.raises(ValueError):
            sanitize_amount('100.12345')

    def test_sanitize_amount_exceeds_max(self):
        with pytest.raises(ValueError):
            sanitize_amount('1_000_000_000_001')

    def test_sanitize_csv_field_formula_injection(self):
        assert sanitize_csv_field('=SUM(A1:A10)').startswith("'")
        assert sanitize_csv_field('+cmd|').startswith("'")
        assert sanitize_csv_field('-1+1').startswith("'")
        assert sanitize_csv_field('@SUM').startswith("'")

    def test_sanitize_csv_field_normal(self):
        assert sanitize_csv_field('1000') == '1000'
        assert sanitize_csv_field('Hello') == 'Hello'

    def test_sanitize_quantity_valid(self):
        assert sanitize_quantity(10) == Decimal('10')

    def test_sanitize_quantity_negative(self):
        with pytest.raises(ValueError):
            sanitize_quantity(-1)

    def test_sanitize_quantity_exceeds_max(self):
        with pytest.raises(ValueError):
            sanitize_quantity(9_999_999)

    def test_sanitize_percentage_valid(self):
        assert sanitize_percentage(15) == Decimal('15.00')

    def test_sanitize_percentage_over_100(self):
        with pytest.raises(ValueError):
            sanitize_percentage(150)

    def test_sanitize_percentage_negative(self):
        with pytest.raises(ValueError):
            sanitize_percentage(-5)

    def test_sanitize_description(self):
        result = sanitize_description('<b>Hello</b>')
        assert '<b>' not in result
        assert 'Hello' in result

    def test_sanitize_email_valid(self):
        assert sanitize_email('Test@Example.COM') == 'test@example.com'

    def test_sanitize_email_invalid(self):
        with pytest.raises(ValueError):
            sanitize_email('not-email')

    def test_sanitize_phone_cleans(self):
        result = sanitize_phone('+1 (555) 123-4567')
        assert '+' in result or '(' in result


class TestDuplicateDetector:
    def test_detect_duplicate_entry(self):
        dd = DuplicateDetector()
        entry1 = JournalEntry('Test entry', date=datetime(2026, 1, 1))
        cash = Account('Cash', 'asset', '1000')
        sales = Account('Sales', 'income', '4000')
        entry1.add_debit(cash, Decimal('500')).add_credit(sales, Decimal('500'))
        assert not dd.check_entry(entry1)
        dd.mark_seen(entry1)
        assert dd.check_entry(entry1)

    def test_different_entries_not_duplicate(self):
        dd = DuplicateDetector()
        e1 = JournalEntry('Sale', date=datetime(2026, 1, 1))
        e2 = JournalEntry('Purchase', date=datetime(2026, 1, 1))
        e1.add_debit(Account('C', 'asset', '1000'), Decimal('500'))
        e1.add_credit(Account('S', 'income', '4000'), Decimal('500'))
        e2.add_debit(Account('I', 'asset', '1200'), Decimal('300'))
        e2.add_credit(Account('P', 'liability', '2000'), Decimal('300'))
        dd.mark_seen(e1)
        assert not dd.check_entry(e2)

    def test_clear(self):
        dd = DuplicateDetector()
        entry = JournalEntry('Test', date=datetime(2026, 1, 1))
        entry.add_debit(Account('C', 'asset', '1000'), Decimal('100'))
        entry.add_credit(Account('S', 'income', '4000'), Decimal('100'))
        dd.mark_seen(entry)
        dd.clear()
        assert not dd.check_entry(entry)


class TestEntryValidator:
    def test_valid_entry(self):
        ledger = Ledger()
        ledger.add_account(Account('Cash', 'asset', '1000'))
        ledger.add_account(Account('Sales', 'income', '4000'))
        entry = JournalEntry('Sale', date=datetime(2026, 1, 1))
        entry.add_debit(ledger.get_account('1000'), Decimal('500'))
        entry.add_credit(ledger.get_account('4000'), Decimal('500'))
        validator = EntryValidator(ledger)
        errors = validator.validate(entry)
        assert len(errors) == 0

    def test_unbalanced_entry(self):
        ledger = Ledger()
        entry = JournalEntry('Unbalanced', date=datetime(2026, 1, 1))
        entry.add_debit(Account('C', 'asset', '1000'), Decimal('500'))
        validator = EntryValidator(ledger)
        errors = validator.validate(entry)
        assert len(errors) > 0

    def test_account_not_in_ledger(self):
        ledger = Ledger()
        entry = JournalEntry('Test', date=datetime(2026, 1, 1))
        entry.add_debit(Account('Fake', 'asset', '9999'), Decimal('100'))
        entry.add_credit(Account('Fake2', 'income', '8888'), Decimal('100'))
        validator = EntryValidator(ledger)
        errors = validator.validate(entry)
        assert any('9999' in e for e in errors)

    def test_empty_description(self):
        ledger = Ledger()
        ledger.add_account(Account('C', 'asset', '1000'))
        ledger.add_account(Account('S', 'income', '4000'))
        entry = JournalEntry('', date=datetime(2026, 1, 1))
        entry.add_debit(ledger.get_account('1000'), Decimal('100'))
        entry.add_credit(ledger.get_account('4000'), Decimal('100'))
        validator = EntryValidator(ledger)
        errors = validator.validate(entry)
        assert any('empty' in e.lower() for e in errors)

    def test_no_debits(self):
        ledger = Ledger()
        entry = JournalEntry('Test', date=datetime(2026, 1, 1))
        validator = EntryValidator(ledger)
        errors = validator.validate(entry)
        assert len(errors) > 0

    def test_validate_and_raise(self):
        ledger = Ledger()
        entry = JournalEntry('', date=datetime(2026, 1, 1))
        validator = EntryValidator(ledger)
        with pytest.raises(BusinessRuleError):
            validator.validate_and_raise(entry)


class TestNewAccountValidation:
    def test_valid_account(self):
        errors = validate_new_account('Cash', 'asset', '1000')
        assert len(errors) == 0

    def test_invalid_type(self):
        errors = validate_new_account('Test', 'invalid', '1000')
        assert len(errors) > 0

    def test_invalid_code(self):
        errors = validate_new_account('Test', 'asset', '')
        assert len(errors) > 0


class TestInvoiceItemValidation:
    def test_empty_items(self):
        errors = validate_invoice_items([])
        assert len(errors) > 0

    def test_valid_item(self):
        items = [{'name': 'Product', 'quantity': 1, 'price': 100}]
        errors = validate_invoice_items(items)
        assert len(errors) == 0

    def test_zero_quantity(self):
        items = [{'name': 'P', 'quantity': 0, 'price': 100}]
        errors = validate_invoice_items(items)
        assert len(errors) > 0

    def test_negative_price(self):
        items = [{'name': 'P', 'quantity': 1, 'price': -10}]
        errors = validate_invoice_items(items)
        assert len(errors) > 0


class TestBusinessEngineValidation:
    def test_validate_entry_on_engine(self):
        from pyledger import BusinessEngine
        app = BusinessEngine(company_name='Test', auto_setup=True)
        entry = JournalEntry('Test sale', date=datetime(2026, 1, 1))
        cash = app.ledger.get_account('1000')
        sales = app.ledger.get_account('4000')
        entry.add_debit(cash, Decimal('500')).add_credit(sales, Decimal('500'))
        errors = app.validate_entry(entry)
        assert len(errors) == 0

    def test_post_entry_security_check(self):
        from pyledger import BusinessEngine
        app = BusinessEngine(company_name='Test', auto_setup=True)
        entry = JournalEntry('Test sale', date=datetime(2026, 1, 1))
        cash = app.ledger.get_account('1000')
        sales = app.ledger.get_account('4000')
        entry.add_debit(cash, Decimal('500')).add_credit(sales, Decimal('500'))
        result = app.post_entry(entry)
        assert result is True

    def test_post_duplicate_raises(self):
        from pyledger import BusinessEngine
        app = BusinessEngine(company_name='Test', auto_setup=True)
        entry = JournalEntry('Duplicate', date=datetime(2026, 1, 1))
        cash = app.ledger.get_account('1000')
        sales = app.ledger.get_account('4000')
        entry.add_debit(cash, Decimal('500')).add_credit(sales, Decimal('500'))
        app.post_entry(entry)
        duplicate = JournalEntry('Duplicate', date=datetime(2026, 1, 1))
        duplicate.add_debit(cash, Decimal('500')).add_credit(sales, Decimal('500'))
        with pytest.raises(BusinessRuleError):
            app.post_entry(duplicate)

    def test_add_account_validates(self):
        from pyledger import BusinessEngine
        app = BusinessEngine(company_name='Test', auto_setup=True)
        acc = app.add_account('New Account', 'asset', '9999')
        assert acc.code == '9999'

    def test_add_account_invalid_raises(self):
        from pyledger import BusinessEngine
        app = BusinessEngine(company_name='Test', auto_setup=True)
        with pytest.raises(BusinessRuleError):
            app.add_account('', 'invalid', '!!')
