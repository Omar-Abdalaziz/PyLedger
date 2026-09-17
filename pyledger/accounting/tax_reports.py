"""
PyLedger Accounting - Tax Reports
VAT Return & Corporate Tax Report
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger
from pyledger.utils.validators import format_amount


class VATReturn(BaseReport):
    """VAT/GST Return report"""

    def __init__(self, ledger: Ledger, period: FinancialPeriod,
                 vat_rate: Decimal = Decimal('15'),
                 vat_payable_code: str = '2400',
                 vat_receivable_code: str = '1300',
                 currency: Optional[str] = None):
        super().__init__(ledger, period=period, currency=currency)
        self.vat_rate = Decimal(str(vat_rate))
        self.vat_payable_code = vat_payable_code
        self.vat_receivable_code = vat_receivable_code

    def generate(self) -> dict:
        vat_payable = Decimal('0')
        vat_receivable = Decimal('0')

        for entry in self.ledger.journal_entries:
            if self.period and not (self.period.start_date <= entry.date <= self.period.end_date):
                continue
            for txn in entry.credits:
                if txn.account.code == self.vat_payable_code:
                    vat_payable += txn.amount
            for txn in entry.debits:
                if txn.account.code == self.vat_receivable_code:
                    vat_receivable += txn.amount

        net_vat_due = vat_payable - vat_receivable
        vat_rate_pct = self.vat_rate / Decimal('100')

        return {
            'title': 'VAT Return',
            'period': self.period.label if self.period else '',
            'vat_rate': str(self.vat_rate),
            'vat_payable': str(vat_payable),
            'vat_receivable': str(vat_receivable),
            'net_vat_due': str(net_vat_due),
            'net_vat_due_abs': str(abs(net_vat_due)),
            'is_payable': net_vat_due >= 0,
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("VAT RETURN", data['period']))
        lines.append("")
        lines.append(f"VAT Rate:                  {data['vat_rate']}%")
        lines.append(f"Output VAT (Sales):        {self._format_amount(data['vat_payable'])}")
        lines.append(f"Input VAT (Purchases):     {self._format_amount(data['vat_receivable'])}")
        lines.append("-" * 68)
        lines.append(f"Net VAT {'Payable' if data['is_payable'] else 'Receivable'}:       {self._format_amount(data['net_vat_due_abs'])}")
        lines.append(self._line())
        return "\n".join(lines)


class CorporateTaxReport(BaseReport):
    """Corporate Income Tax report"""

    TAX_RATES = {
        'US': Decimal('21'),
        'UK': Decimal('25'),
        'SA': Decimal('20'),
        'AE': Decimal('9'),
        'EG': Decimal('22.5'),
    }

    def __init__(self, ledger: Ledger, period: FinancialPeriod,
                 country: str = 'US',
                 tax_rate: Decimal = None,
                 currency: Optional[str] = None):
        super().__init__(ledger, period=period, currency=currency)
        self.country = country
        self.tax_rate = tax_rate or self.TAX_RATES.get(country, Decimal('20'))

    def generate(self) -> dict:
        total_income = Decimal('0')
        total_expenses = Decimal('0')

        for acc in self.ledger.get_accounts_by_type('income'):
            if self.period:
                total_income += self._filtered_balance(acc)
            else:
                total_income += acc.get_balance()

        for acc in self.ledger.get_accounts_by_type('expense'):
            if self.period:
                total_expenses += self._filtered_balance(acc)
            else:
                total_expenses += acc.get_balance()

        net_profit_before_tax = total_income - total_expenses
        estimated_tax = (net_profit_before_tax * self.tax_rate / Decimal('100')).quantize(Decimal('0.01'))
        net_profit_after_tax = (net_profit_before_tax - estimated_tax).quantize(Decimal('0.01'))

        return {
            'title': 'Corporate Tax Report',
            'country': self.country,
            'tax_rate': str(self.tax_rate),
            'total_income': str(total_income),
            'total_expenses': str(total_expenses),
            'net_profit_before_tax': str(net_profit_before_tax),
            'estimated_tax': str(estimated_tax),
            'effective_rate': str(round(float(estimated_tax / net_profit_before_tax * 100), 2)) if net_profit_before_tax != 0 else '0',
            'net_profit_after_tax': str(net_profit_after_tax),
        }

    def _filtered_balance(self, account) -> Decimal:
        if not self.period:
            return account.get_balance()
        total = Decimal('0')
        for txn in account.get_transactions():
            txn_time = txn.get('timestamp')
            if txn_time and self.period.start_date <= txn_time <= self.period.end_date:
                amount = txn.get('amount')
                total += Decimal(str(amount))
        return total

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("CORPORATE TAX REPORT", f"{data['country']} - {self.period.label if self.period else ''}"))
        lines.append("")
        lines.append(f"Tax Rate:                  {data['tax_rate']}%")
        lines.append(f"Total Income:              {self._format_amount(data['total_income'])}")
        lines.append(f"Total Expenses:            {self._format_amount(data['total_expenses'])}")
        lines.append("-" * 68)
        lines.append(f"Net Profit Before Tax:     {self._format_amount(data['net_profit_before_tax'])}")
        lines.append(f"Estimated Tax ({data['tax_rate']}%):       {self._format_amount(data['estimated_tax'])}")
        lines.append("-" * 68)
        lines.append(f"Net Profit After Tax:      {self._format_amount(data['net_profit_after_tax'])}")
        lines.append(self._line())
        return "\n".join(lines)
