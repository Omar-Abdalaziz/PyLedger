"""
PyLedger Reports Module - Income Statement (P&L)
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger


class IncomeStatement(BaseReport):
    """Income Statement / Profit & Loss Statement"""

    def __init__(self, ledger: Ledger, period: Optional[FinancialPeriod] = None,
                 end_date: Optional[datetime] = None, currency: Optional[str] = None,
                 format_type: str = 'by_nature'):
        as_of_date = end_date
        super().__init__(ledger, period=period, as_of_date=as_of_date, currency=currency)
        self.format_type = format_type

    def generate(self) -> dict:
        income_accounts = self.ledger.get_accounts_by_type('income')
        expense_accounts = self.ledger.get_accounts_by_type('expense')

        income_items = []
        for acc in income_accounts:
            balance = self._filtered_balance(acc)
            if balance != 0:
                income_items.append({
                    'code': acc.code, 'name': acc.name,
                    'amount': str(balance)
                })

        expense_items = []
        for acc in expense_accounts:
            balance = self._filtered_balance(acc)
            if balance != 0:
                expense_items.append({
                    'code': acc.code, 'name': acc.name,
                    'amount': str(balance)
                })

        total_income = sum((Decimal(i['amount']) for i in income_items), Decimal('0'))
        total_expenses = sum((Decimal(i['amount']) for i in expense_items), Decimal('0'))
        net_income = total_income - total_expenses

        return {
            'title': 'Income Statement',
            'income': {'accounts': income_items, 'total': str(total_income)},
            'expenses': {'accounts': expense_items, 'total': str(total_expenses)},
            'items': income_items + expense_items,
            'total_income': str(total_income),
            'total_expenses': str(total_expenses),
            'net_income': str(net_income),
            'format_type': self.format_type,
        }

    def _filtered_balance(self, account) -> Decimal:
        if not self.period:
            return account.get_balance()
        total = Decimal('0')
        for txn in account.get_transactions():
            txn_time = txn.get('timestamp') if isinstance(txn, dict) else txn.get('timestamp')
            if txn_time and self.period.start_date <= txn_time <= self.period.end_date:
                amount = txn.get('amount') if isinstance(txn, dict) else txn.amount
                ttype = txn.get('type') if isinstance(txn, dict) else txn.type
                # Signed replay: sales returns (debit legs on revenue) reduce
                # revenue per IFRS 15 (net presentation).
                total += account.balance_effect(ttype, Decimal(str(amount)))
        return total

    def _format_text(self) -> str:
        data = self.generate()
        period_label = self.period.label if self.period else f"As of {self.as_of_date.strftime('%Y-%m-%d')}"
        lines = []
        lines.extend(self._title_block("INCOME STATEMENT", period_label))
        lines.append("")
        lines.append(f"{'REVENUE':<40}")
        lines.append("-" * 68)
        for acc in data['income']['accounts']:
            lines.append(f"  {acc['name']:<38} {self._format_amount(acc['amount'])}")
        lines.append("-" * 68)
        lines.append(f"{'Total Revenue':<48} {self._format_amount(data['income']['total'])}")
        lines.append("")
        lines.append(f"{'EXPENSES':<40}")
        lines.append("-" * 68)
        for acc in data['expenses']['accounts']:
            lines.append(f"  {acc['name']:<38} {self._format_amount(acc['amount'])}")
        lines.append("-" * 68)
        lines.append(f"{'Total Expenses':<48} {self._format_amount(data['expenses']['total'])}")
        lines.append("")
        lines.append(self._line())
        lines.append(f"{'NET INCOME':<48} {self._format_amount(data['net_income'])}")
        lines.append(self._line())
        return "\n".join(lines)
