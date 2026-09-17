"""
PyLedger Reports - Financial Ratios
Key financial metrics and ratios
"""

from decimal import Decimal
from typing import Optional
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger


class FinancialRatios(BaseReport):
    """Calculate key financial ratios"""

    def __init__(self, ledger: Ledger, period: Optional[FinancialPeriod] = None,
                 currency: Optional[str] = None):
        super().__init__(ledger, period=period, currency=currency)
        self._balance_cache = {}

    def _balance(self, account_type: str) -> Decimal:
        if account_type in self._balance_cache:
            return self._balance_cache[account_type]
        total = Decimal('0')
        for acc in self.ledger.get_accounts_by_type(account_type):
            total += self._filtered_balance(acc)
        self._balance_cache[account_type] = total
        return total

    def _filtered_balance(self, account) -> Decimal:
        if not self.period:
            return account.get_balance()
        total = Decimal('0')
        for txn in account.get_transactions():
            txn_time = txn.get('timestamp') if isinstance(txn, dict) else None
            if txn_time and self.period.start_date <= txn_time <= self.period.end_date:
                amount = txn.get('amount') if isinstance(txn, dict) else txn.amount
                total += Decimal(str(amount))
        return total

    def _accounts_matching(self, keywords: list, type_filter: str = None) -> list:
        accounts = self.ledger.get_accounts_by_type(type_filter) if type_filter else self.ledger.accounts
        return [a for a in accounts
                if any(kw in a.code.lower() or kw in a.name.lower() for kw in keywords)]

    def _sum_accounts(self, accounts: list) -> Decimal:
        total = Decimal('0')
        for acc in accounts:
            total += self._filtered_balance(acc)
        return total

    def _precompute(self) -> dict:
        ca = self._accounts_matching(
            ['cash', 'bank', 'receivable', 'inventory', 'prepaid', 'short_term'], 'asset')
        cl = self._accounts_matching(
            ['payable', 'accrued', 'unearned', 'short_term_debt'], 'liability')
        inv = self._accounts_matching(['inventory', 'stock'], 'asset')
        rev = self._accounts_matching(
            ['sales', 'revenue', 'service_income', 'fee_income'], 'income')
        cogs = self._accounts_matching(
            ['cogs', 'cost_of_goods', 'cost_of_sales', 'purchase'], 'expense')

        return {
            'current_assets': self._sum_accounts(ca),
            'current_liabilities': self._sum_accounts(cl),
            'inventory': self._sum_accounts(inv),
            'total_assets': self._balance('asset'),
            'total_liabilities': self._balance('liability'),
            'total_equity': self._balance('equity'),
            'net_income': self._balance('income') - self._balance('expense'),
            'revenue': self._sum_accounts(rev),
            'cogs': self._sum_accounts(cogs),
        }

    def generate(self) -> dict:
        p = self._precompute()

        def _safe_div(n: Decimal, d: Decimal) -> Decimal:
            return (n / d).quantize(Decimal('0.01')) if d != 0 else Decimal('0')

        def _pct(n: Decimal, d: Decimal) -> str:
            return str(round(float(_safe_div(n, d) * 100), 2))

        current_ratio = _safe_div(p['current_assets'], p['current_liabilities'])
        quick_assets = p['current_assets'] - p['inventory']
        quick_ratio = _safe_div(quick_assets, p['current_liabilities'])

        gross_profit = p['revenue'] - p['cogs']
        gross_margin = _pct(gross_profit, p['revenue'])
        net_margin = _pct(p['net_income'], p['revenue'])

        debt_to_equity = _safe_div(p['total_liabilities'], p['total_equity'])

        roa = _pct(p['net_income'], p['total_assets'])
        roe = _pct(p['net_income'], p['total_equity'])

        asset_turnover = _safe_div(p['revenue'], p['total_assets'])

        return {
            'title': 'Financial Ratios',
            'period': self.period.label if self.period else '',
            'liquidity': {
                'current_ratio': str(current_ratio),
                'quick_ratio': str(quick_ratio),
                'current_assets': str(p['current_assets']),
                'current_liabilities': str(p['current_liabilities']),
                'inventory': str(p['inventory']),
            },
            'profitability': {
                'gross_margin_pct': gross_margin,
                'net_margin_pct': net_margin,
                'gross_profit': str(gross_profit),
                'net_income': str(p['net_income']),
                'revenue': str(p['revenue']),
            },
            'leverage': {
                'debt_to_equity': str(debt_to_equity),
                'total_liabilities': str(p['total_liabilities']),
                'total_equity': str(p['total_equity']),
            },
            'efficiency': {
                'roa_pct': roa,
                'roe_pct': roe,
                'asset_turnover': str(asset_turnover),
                'total_assets': str(p['total_assets']),
            },
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("FINANCIAL RATIOS", data['period']))
        lines.append("")

        sections = [
            ('LIQUIDITY RATIOS', 'liquidity', [
                ('Current Ratio', 'current_ratio'),
                ('Quick Ratio', 'quick_ratio'),
            ]),
            ('PROFITABILITY RATIOS', 'profitability', [
                ('Gross Margin', 'gross_margin_pct', '%'),
                ('Net Margin', 'net_margin_pct', '%'),
                ('Gross Profit', 'gross_profit'),
                ('Net Income', 'net_income'),
            ]),
            ('LEVERAGE RATIOS', 'leverage', [
                ('Debt-to-Equity', 'debt_to_equity'),
            ]),
            ('EFFICIENCY RATIOS', 'efficiency', [
                ('ROA', 'roa_pct', '%'),
                ('ROE', 'roe_pct', '%'),
                ('Asset Turnover', 'asset_turnover'),
            ]),
        ]

        for title, key, items in sections:
            lines.append(f"{title}:")
            lines.append("-" * 48)
            for item in items:
                label = item[0]
                field = item[1]
                suffix = item[2] if len(item) > 2 else ''
                val = data[key].get(field, '0')
                if suffix == '%':
                    lines.append(f"  {label:<30} {val:>10}%")
                else:
                    lines.append(f"  {label:<30} {self._format_amount(val)}")
            lines.append("")

        lines.append(self._line())
        return "\n".join(lines)
