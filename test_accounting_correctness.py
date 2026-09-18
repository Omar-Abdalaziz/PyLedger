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
