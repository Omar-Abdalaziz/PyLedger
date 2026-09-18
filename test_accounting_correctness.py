"""
PyLedger - Accounting Correctness Regression Tests (IFRS/GAAP).

Guards the invariants reviewed in the 2026-09-18 accounting audit:
equation integrity, period cut-off, signed replay, multi-tax,
bankrec signs, inventory layers, aging buckets, HALF_UP rounding.
"""

from decimal import Decimal
from datetime import datetime

from pyledger import Ledger, Account, JournalEntry, Invoice, Tax
from pyledger.reports import FinancialPeriod, IncomeStatement
from pyledger.accounting.assets import FixedAsset, DepreciationMethod, DepreciationEngine
from pyledger.accounting.bank_reconciliation import BankReconciliation
from pyledger.accounting.inventory import InventoryItem
from pyledger.accounting.aging import ReceivableAging
from pyledger.accounting.crm import Customer
from pyledger.utils.validators import format_amount


def _cycle_ledger():
    l = Ledger('Audit', 'USD')
    for n, t, c in [('Cash', 'asset', '1000'), ('AR', 'asset', '1100'),
                    ('AP', 'liability', '2000'), ('Capital', 'equity', '3000'),
                    ('Sales', 'income', '4000'), ('Rent', 'expense', '5000')]:
        l.add_account(Account(n, t, c))

    def post(desc, dr, cr, amt, date):
        e = JournalEntry(desc, date=date)
        e.add_debit(l.get_account(dr), amt)
        e.add_credit(l.get_account(cr), amt)
        l.record_entry(e)

    post('invest', '1000', '3000', 10000, datetime(2026, 1, 5))
    post('sale', '1100', '4000', 5000, datetime(2026, 2, 5))
    post('rent', '5000', '1000', 1000, datetime(2026, 2, 10))
    post('refund', '4000', '1100', 500, datetime(2026, 2, 20))
    post('buy', '5000', '2000', 500, datetime(2026, 3, 1))
    return l


class TestAccountingEquation:
    def test_assets_equal_liab_plus_equity_plus_earnings(self):
        l = _cycle_ledger()
        assert (l.get_total_assets()
                == l.get_total_liabilities() + l.get_total_equity()
                + l.get_total_income() - l.get_total_expenses())

    def test_trial_balance_balanced(self):
        tb = _cycle_ledger().trial_balance()
        assert tb['balanced'] and tb['total_debits'] == tb['total_credits']


class TestPeriodCutoff:
    def test_february_income_nets_sales_return(self):
        l = _cycle_ledger()
        p = FinancialPeriod(datetime(2026, 2, 1), datetime(2026, 2, 28), label='2026-02')
        assert Decimal(IncomeStatement(l, period=p).generate()['net_income']) == Decimal('3500.00')

    def test_entry_date_stamped_not_wallclock(self):
        l = _cycle_ledger()
        txns = l.get_account('4000').get_transactions()
        assert all(t['timestamp'].month == 2 for t in txns)

    def test_liability_as_of_before_and_after(self):
        l = _cycle_ledger()
        ap = l.get_account('2000')
        assert ap.get_balance_as_of(datetime(2026, 2, 15)) == Decimal('0')
        assert ap.get_balance_as_of(datetime(2026, 3, 15)) == Decimal('500.00')


class TestSections:
    def test_multi_tax_accumulates(self):
        inv = Invoice('C')
        inv.add_item('s', 1, 1000)
        inv.apply_tax('VAT', 15)
        inv.apply_tax('WHT', 5)
        assert inv.total == Decimal('1200.00')
        assert len(inv.taxes) == 2

    def test_bankrec_signs(self):
        l = Ledger()
        l.add_account(Account('Cash', 'asset', '1000'))
        c = l.get_account('1000')
        c.deposit(5000)
        c.withdraw(1200)
        br = BankReconciliation(l, '1000')
        assert len(br.get_outstanding_checks()) == 1
        assert len(br.get_deposits_in_transit()) == 1

    def test_fifo_layers_and_weighted_cost(self):
        it = InventoryItem('SKU', 'W')
        it.receive(10, 100)
        it.receive(10, 200)
        it.issue(15)
        assert it.inventory_value == Decimal('1000')
        assert it.weighted_average_cost() == Decimal('200.00')

    def test_aging_counts_no_due_date_invoices(self):
        l = Ledger()
        c = Customer('Acme', 'C-1')
        inv = Invoice('Acme')
        inv.add_item('x', 1, 1000)
        inv.issue()
        c.add_invoice(inv)
        data = ReceivableAging(l, [c]).generate()
        assert data['total_customers'] == 1
        assert data['grand_total'] == '1000.00'

    def test_half_up_rounding(self):
        assert format_amount(Decimal('0.025')) == Decimal('0.03')


class TestDepreciationRichness:
    def test_declining_balance_factor(self):
        a = FixedAsset('M', 100000, 'FA', 5, DepreciationMethod.DECLINING_BALANCE,
                       rate_factor=1.5)
        assert a.annual_depreciation() == Decimal('30000.00')
        d = FixedAsset('M2', 100000, 'FB', 5, DepreciationMethod.DECLINING_BALANCE)
        assert d.annual_depreciation() == Decimal('40000.00')

    def test_straight_line_half_year_convention(self):
        b = FixedAsset('B', 100000, 'FC', 5, convention='half_year')
        assert b.annual_depreciation(year=0) == Decimal('10000.00')
        assert b.annual_depreciation(year=2) == Decimal('20000.00')
        assert b.annual_depreciation(year=4) == Decimal('10000.00')

    def test_units_of_production(self):
        c = FixedAsset('T', 50000, 'FD', 5, DepreciationMethod.UNITS_OF_PRODUCTION,
                       total_estimated_units=100000)
        assert c.record_production(20000) == Decimal('10000.00')
        assert c.lifetime_produced == Decimal('20000')
        # Schedule covers remaining units only (20000 already claimed)
        sched = c.depreciation_schedule(units_per_year=[20000] * 5)
        assert sum((r['depreciation'] for r in sched), Decimal('0')) == Decimal('40000.00')
        fresh = FixedAsset('T2', 50000, 'FD2', 5, DepreciationMethod.UNITS_OF_PRODUCTION,
                           total_estimated_units=100000)
        full = fresh.depreciation_schedule(units_per_year=[20000] * 5)
        assert sum((r['depreciation'] for r in full), Decimal('0')) == Decimal('50000.00')

    def test_units_of_production_requires_estimate(self):
        import pytest
        with pytest.raises(ValueError):
            FixedAsset('T', 50000, 'FD', 5, DepreciationMethod.UNITS_OF_PRODUCTION)

    def test_macrs_5year_sums_to_cost(self):
        d = FixedAsset('S', 10000, 'FE', 0, DepreciationMethod.MACRS, macrs_class='GDS-5')
        sched = d.depreciation_schedule()
        assert len(sched) == 6
        assert sum((r['depreciation'] for r in sched), Decimal('0')) == Decimal('10000.00')

    def test_macrs_realty_mid_month(self):
        e = FixedAsset('Bld', 275000, 'FF', 0, DepreciationMethod.MACRS,
                       macrs_class='GDS-27.5', placed_in_service_month=1)
        assert e.macrs_annual(0) == Decimal('9583.33')

    def test_schedule_terminates_at_residual(self):
        f = FixedAsset('X', 100000, 'FG', 5, residual_value=10000)
        rows = f.depreciation_schedule()
        assert rows[-1]['book_value'] == Decimal('10000.00')

    def test_engine_schedule_and_lifo(self):
        l = Ledger()
        eng = DepreciationEngine(l)
        eng.register_asset(FixedAsset('S', 10000, 'FH', 0, DepreciationMethod.MACRS,
                                      macrs_class='GDS-5'))
        assert len(eng.generate_schedule('S')) == 6
        it = InventoryItem('SKU', 'W', valuation_method='lifo')
        it.receive(10, 100)
        it.receive(10, 200)
        assert it.issue(5)['total_cost'] == Decimal('1000')
        assert it.inventory_value == Decimal('2000')
