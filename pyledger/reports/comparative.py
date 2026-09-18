"""
PyLedger Reports - Comparative Financial Reports
Period-over-period and year-over-year comparisons
"""

from decimal import Decimal
from typing import Optional, List
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.reports.income_statement import IncomeStatement
from pyledger.reports.balance_sheet import BalanceSheet
from pyledger.core.ledger import Ledger


class ComparativeIncomeStatement(BaseReport):
    """Income Statement with period-over-period comparison"""

    def __init__(self, ledger: Ledger,
                 periods: List[FinancialPeriod],
                 currency: Optional[str] = None):
        super().__init__(ledger, period=periods[0] if periods else None,
                         currency=currency)
        self.periods = periods

    def generate(self) -> dict:
        columns = []
        all_accounts = set()
        period_data = []

        for i, period in enumerate(self.periods):
            stmt = IncomeStatement(self.ledger, period=period, currency=self.currency)
            data = stmt.generate()
            period_data.append(data)
            for item in data.get('items', []):
                all_accounts.add(item['account'])

        for data in period_data:
            col = {}
            for item in data.get('items', []):
                col[item['account']] = item['amount']
            columns.append(col)

        rows = []
        sorted_accounts = sorted(all_accounts)
        for acct in sorted_accounts:
            row = {'account': acct}
            amounts = []
            for col in columns:
                amt = col.get(acct, '0')
                amounts.append(amt)
            row['amounts'] = amounts
            if len(amounts) >= 2:
                diff = Decimal(amounts[-1]) - Decimal(amounts[0])
                row['change'] = str(diff)
                if Decimal(amounts[0]) != 0:
                    pct = (diff / Decimal(amounts[0]) * 100).quantize(Decimal('0.01'))
                    row['change_percentage'] = str(pct)
                else:
                    row['change_percentage'] = 'N/A'
            rows.append(row)

        return {
            'title': 'Comparative Income Statement',
            'periods': [p.label for p in self.periods],
            'rows': rows,
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("COMPARATIVE INCOME STATEMENT",
                                       " | ".join(data['periods'])))
        lines.append("")
        header = f"{'Account':<30}"
        for p in data['periods']:
            header += f" {p:>15}"
        if len(data['periods']) >= 2:
            header += f" {'Change':>15} {'%':>8}"
        lines.append(header)
        lines.append("=" * (30 + 23 * len(data['periods'])))
        for row in data['rows']:
            line = f"{row['account']:<30}"
            for amt in row['amounts']:
                line += f" {self._format_amount(amt)}"
            if 'change' in row:
                line += f" {self._format_amount(row['change'])}"
                line += f" {row['change_percentage']:>8}"
            lines.append(line)
        lines.append(self._line())
        return "\n".join(lines)


class ComparativeBalanceSheet(BaseReport):
    """Balance Sheet with period-over-period comparison"""

    def __init__(self, ledger: Ledger,
                 periods: List[FinancialPeriod],
                 currency: Optional[str] = None):
        super().__init__(ledger, period=periods[0] if periods else None,
                         currency=currency)
        self.periods = periods

    def generate(self) -> dict:
        columns = []
        for period in self.periods:
            bs = BalanceSheet(self.ledger, as_of_date=period.end_date, currency=self.currency)
            columns.append(bs.generate())

        return {
            'title': 'Comparative Balance Sheet',
            'periods': [p.label for p in self.periods],
            'columns': columns,
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("COMPARATIVE BALANCE SHEET",
                                       " | ".join(data['periods'])))
        lines.append("")
        for idx, col in enumerate(data['columns']):
            lines.append(f"--- As of {data['periods'][idx]} ---")
            lines.append(f"Total Assets:    {self._format_amount(col.get('total_assets', '0'))}")
            lines.append(f"Total Liabilities: {self._format_amount(col.get('total_liabilities', '0'))}")
            lines.append(f"Total Equity:    {self._format_amount(col.get('total_equity', '0'))}")
            lines.append("")
        lines.append(self._line())
        return "\n".join(lines)
