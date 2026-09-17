"""
PyLedger Reports Module - Balance Sheet
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger


class BalanceSheet(BaseReport):
    """Balance Sheet / Statement of Financial Position"""

    ASSET_CURRENT_TYPES = ['cash', 'bank', 'receivable', 'inventory', 'prepaid']
    ASSET_NONCURRENT_TYPES = ['fixed_asset', 'intangible', 'investment', 'equipment']
    LIABILITY_CURRENT_TYPES = ['payable', 'accrued', 'short_term_loan']
    LIABILITY_NONCURRENT_TYPES = ['long_term_loan', 'deferred_tax']

    def __init__(self, ledger: Ledger, as_of_date: Optional[datetime] = None,
                 currency: Optional[str] = None, classify: bool = True):
        super().__init__(ledger, as_of_date=as_of_date, currency=currency)
        self.classify = classify

    def generate(self) -> dict:
        asset_accounts = self.ledger.get_accounts_by_type('asset')
        liability_accounts = self.ledger.get_accounts_by_type('liability')
        equity_accounts = self.ledger.get_accounts_by_type('equity')
        income_accounts = self.ledger.get_accounts_by_type('income')
        expense_accounts = self.ledger.get_accounts_by_type('expense')

        if self.classify:
            current_assets, noncurrent_assets = self._classify_accounts(asset_accounts)
            current_liabilities, noncurrent_liabilities = self._classify_accounts(liability_accounts)
        else:
            current_assets = asset_accounts
            noncurrent_assets = []
            current_liabilities = liability_accounts
            noncurrent_liabilities = []

        total_ca = sum((a.get_balance() for a in current_assets), Decimal('0'))
        total_nca = sum((a.get_balance() for a in noncurrent_assets), Decimal('0'))
        total_cl = sum((a.get_balance() for a in current_liabilities), Decimal('0'))
        total_ncl = sum((a.get_balance() for a in noncurrent_liabilities), Decimal('0'))
        total_income = sum((a.get_balance() for a in income_accounts), Decimal('0'))
        total_expenses = sum((a.get_balance() for a in expense_accounts), Decimal('0'))
        net_income = total_income - total_expenses
        total_equity = sum((a.get_balance() for a in equity_accounts), Decimal('0')) + net_income
        total_assets = total_ca + total_nca
        total_liab_eq = total_cl + total_ncl + total_equity

        return {
            'title': 'Balance Sheet',
            'assets': {
                'current': self._accounts_list(current_assets),
                'noncurrent': self._accounts_list(noncurrent_assets),
                'total_current': str(total_ca),
                'total_noncurrent': str(total_nca),
                'total': str(total_assets),
            },
            'total_assets': str(total_assets),
            'total_liabilities': str(total_cl + total_ncl),
            'total_equity': str(total_equity),
            'liabilities': {
                'current': self._accounts_list(current_liabilities),
                'noncurrent': self._accounts_list(noncurrent_liabilities),
                'total_current': str(total_cl),
                'total_noncurrent': str(total_ncl),
            },
            'equity': {
                'accounts': self._accounts_list(equity_accounts),
                'net_income': str(net_income) if net_income != 0 else None,
                'total': str(total_equity),
            },
            'liabilities_and_equity_total': str(total_liab_eq),
            'balanced': total_assets == total_liab_eq,
        }

    def _classify_accounts(self, accounts: list) -> tuple:
        current = []
        noncurrent = []
        for acc in accounts:
            code_lower = acc.code.lower()
            name_lower = acc.name.lower()
            if any(kw in code_lower or kw in name_lower for kw in self.ASSET_CURRENT_TYPES + self.LIABILITY_CURRENT_TYPES):
                current.append(acc)
            elif any(kw in code_lower or kw in name_lower for kw in self.ASSET_NONCURRENT_TYPES + self.LIABILITY_NONCURRENT_TYPES):
                noncurrent.append(acc)
            else:
                if acc.balance > 0:
                    current.append(acc)
                else:
                    noncurrent.append(acc)
        return current, noncurrent

    def _accounts_list(self, accounts: list) -> list:
        return [{'code': a.code, 'name': a.name, 'amount': str(a.get_balance())}
                for a in accounts if a.get_balance() != 0]

    def _format_text(self) -> str:
        data = self.generate()
        as_of = self.as_of_date.strftime('%Y-%m-%d')
        lines = []
        lines.extend(self._title_block("BALANCE SHEET", f"As of {as_of}"))

        lines.append("")
        lines.append(f"{'ASSETS':<40}")
        lines.append("-" * 68)
        if data['assets']['current']:
            lines.append(f"  {'Current Assets':<38}")
            for a in data['assets']['current']:
                lines.append(f"    {a['name']:<36} {self._format_amount(a['amount'])}")
            lines.append(f"  {'Total Current Assets':<46} {self._format_amount(data['assets']['total_current'])}")
            lines.append("")
        if data['assets']['noncurrent']:
            lines.append(f"  {'Non-Current Assets':<38}")
            for a in data['assets']['noncurrent']:
                lines.append(f"    {a['name']:<36} {self._format_amount(a['amount'])}")
            lines.append(f"  {'Total Non-Current Assets':<46} {self._format_amount(data['assets']['total_noncurrent'])}")
            lines.append("")
        lines.append(self._line(char='-'))
        lines.append(f"{'TOTAL ASSETS':<48} {self._format_amount(data['assets']['total'])}")

        lines.append("")
        lines.append(f"{'LIABILITIES & EQUITY':<40}")
        lines.append("-" * 68)
        if data['liabilities']['current']:
            lines.append(f"  {'Current Liabilities':<38}")
            for a in data['liabilities']['current']:
                lines.append(f"    {a['name']:<36} {self._format_amount(a['amount'])}")
            lines.append(f"  {'Total Current Liabilities':<46} {self._format_amount(data['liabilities']['total_current'])}")
            lines.append("")
        if data['liabilities']['noncurrent']:
            lines.append(f"  {'Non-Current Liabilities':<38}")
            for a in data['liabilities']['noncurrent']:
                lines.append(f"    {a['name']:<36} {self._format_amount(a['amount'])}")
            lines.append(f"  {'Total Non-Current Liabilities':<46} {self._format_amount(data['liabilities']['total_noncurrent'])}")
            lines.append("")
        if data['equity']['accounts']:
            lines.append(f"  {'Equity':<38}")
            for a in data['equity']['accounts']:
                lines.append(f"    {a['name']:<36} {self._format_amount(a['amount'])}")
            if data['equity'].get('net_income'):
                lines.append(f"    {'Net Income':<36} {self._format_amount(data['equity']['net_income'])}")
            lines.append(f"  {'Total Equity':<46} {self._format_amount(data['equity']['total'])}")

        lines.append(self._line(char='-'))
        lines.append(f"{'TOTAL LIABILITIES & EQUITY':<48} {self._format_amount(data['liabilities_and_equity_total'])}")
        balanced = data.get('balanced', True)
        if balanced:
            lines.append(self._line())
            lines.append(f"{'[BALANCED]':>68}")
        lines.append(self._line())
        return "\n".join(lines)
