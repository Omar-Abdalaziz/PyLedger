"""
PyLedger Accounting - Budgeting
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger


class Budget:
    def __init__(self, name: str, period: FinancialPeriod):
        self.name = name
        self.period = period
        self.lines = {}

    def set_amount(self, account_code: str, amount) -> 'Budget':
        self.lines[account_code] = Decimal(str(amount))
        return self

    def get_amount(self, account_code: str) -> Decimal:
        return self.lines.get(account_code, Decimal('0'))

    def get_total(self) -> Decimal:
        return sum(self.lines.values(), Decimal('0'))

    def get_by_type(self, account_type: str, ledger: Ledger) -> Decimal:
        total = Decimal('0')
        for code in self.lines:
            try:
                acc = ledger.get_account(code)
                if acc.type == account_type:
                    total += self.lines[code]
            except Exception:
                pass
        return total

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'period': self.period.label,
            'lines': {k: str(v) for k, v in self.lines.items()},
        }


class BudgetVsActual(BaseReport):
    """Budget vs Actual comparison report"""

    def __init__(self, ledger: Ledger, budget: Budget,
                 period: Optional[FinancialPeriod] = None,
                 currency: Optional[str] = None):
        super().__init__(ledger, period=period or budget.period, currency=currency)
        self.budget = budget

    def generate(self) -> dict:
        lines = []
        total_budget = Decimal('0')
        total_actual = Decimal('0')

        for code, budgeted in self.budget.lines.items():
            budgeted = Decimal(str(budgeted))
            total_budget += budgeted

            actual = Decimal('0')
            try:
                acc = self.ledger.get_account(code)
                if self.period:
                    actual = self._filtered_balance(acc)
                else:
                    actual = acc.get_balance()
            except Exception:
                pass

            total_actual += actual
            variance = actual - budgeted
            variance_pct = (variance / budgeted * 100).quantize(Decimal('0.01')) if budgeted != 0 else Decimal('0')

            lines.append({
                'account_code': code,
                'budgeted': str(budgeted),
                'actual': str(actual),
                'variance': str(variance),
                'variance_percentage': str(variance_pct),
            })

        return {
            'title': 'Budget vs Actual',
            'period': self.period.label if self.period else '',
            'budget_name': self.budget.name,
            'lines': lines,
            'total_budget': str(total_budget),
            'total_actual': str(total_actual),
            'total_variance': str(total_actual - total_budget),
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
        lines.extend(self._title_block("BUDGET VS ACTUAL", f"{data['budget_name']} - {data['period']}"))
        lines.append("")
        lines.append(f"{'Account':<30} {'Budget':>12} {'Actual':>12} {'Var':>12} {'Var%':>8}")
        lines.append("-" * 74)
        for l in data['lines']:
            name = l['account_code']
            lines.append(f"{name:<30} {self._format_amount(l['budgeted'])} {self._format_amount(l['actual'])} {self._format_amount(l['variance'])} {l['variance_percentage']:>8}")
        lines.append("-" * 74)
        lines.append(f"{'TOTAL':<30} {self._format_amount(data['total_budget'])} {self._format_amount(data['total_actual'])} {self._format_amount(data['total_variance'])}")
        lines.append(self._line())
        return "\n".join(lines)
