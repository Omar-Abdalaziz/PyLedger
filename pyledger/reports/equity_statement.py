"""
PyLedger Reports Module - Statement of Changes in Equity
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger


class EquityStatement(BaseReport):
    """Statement of Changes in Equity (IFRS-compliant)"""

    def __init__(self, ledger: Ledger, period: Optional[FinancialPeriod] = None,
                 currency: Optional[str] = None):
        super().__init__(ledger, period=period, currency=currency)

    def generate(self) -> dict:
        equity_accounts = self.ledger.get_accounts_by_type('equity')
        income_accounts = self.ledger.get_accounts_by_type('income')
        expense_accounts = self.ledger.get_accounts_by_type('expense')

        total_income = sum((self._filtered_balance(a) for a in income_accounts), Decimal('0'))
        total_expenses = sum((self._filtered_balance(a) for a in expense_accounts), Decimal('0'))
        net_income = total_income - total_expenses

        opening_balances = []
        changes = []
        closing_balances = []

        opening_total = Decimal('0')
        closing_total = Decimal('0')

        for acc in equity_accounts:
            current_bal = self._filtered_balance(acc)
            if current_bal == 0:
                continue

            opening_bal = self._opening_balance(acc)
            change = current_bal - opening_bal

            opening_total += opening_bal
            closing_total += current_bal

            opening_balances.append({'name': acc.name, 'amount': str(opening_bal)})
            changes.append({'name': acc.name, 'amount': str(change)})
            closing_balances.append({'name': acc.name, 'amount': str(current_bal)})

        retained_earnings = any('retained' in a.name.lower() or 'retained' in a.code.lower()
                                for a in equity_accounts)

        return {
            'title': 'Statement of Changes in Equity',
            'opening_balances': opening_balances,
            'net_income': str(net_income) if retained_earnings else '0',
            'other_changes': changes,
            'closing_balances': closing_balances,
            'opening_total': str(opening_total),
            'closing_total': str(closing_total),
        }

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

    def _opening_balance(self, account) -> Decimal:
        if not self.period:
            return account.get_balance()
        total = Decimal('0')
        for txn in account.get_transactions():
            txn_time = txn.get('timestamp') if isinstance(txn, dict) else None
            if txn_time and txn_time < self.period.start_date:
                amount = txn.get('amount') if isinstance(txn, dict) else txn.amount
                if txn.get('type') == 'deposit':
                    total += Decimal(str(amount))
                else:
                    total -= Decimal(str(amount))
        return total

    def _format_text(self) -> str:
        data = self.generate()
        period_label = self.period.label if self.period else "Period"
        lines = []
        lines.extend(self._title_block("STATEMENT OF CHANGES IN EQUITY", period_label))
        lines.append("")
        changes_list = data.get('other_changes', [])
        lines.append(f"{'':<30} {'Opening':>12} {'Changes':>12} {'Closing':>12}")
        lines.append("-" * 68)
        max_rows = max(len(data['opening_balances']), len(data['closing_balances']))
        for i in range(max_rows):
            name = ""
            open_amt = ""
            change_amt = ""
            close_amt = ""
            if i < len(data['opening_balances']):
                name = data['opening_balances'][i]['name']
                open_amt = data['opening_balances'][i]['amount']
            if i < len(changes_list):
                change_amt = changes_list[i]['amount']
            if i < len(data['closing_balances']):
                close_amt = data['closing_balances'][i]['amount']
            lines.append(f"{name:<30} {self._format_amount(open_amt)} {self._format_amount(change_amt)} {self._format_amount(close_amt)}")
        lines.append("-" * 68)
        if data['net_income'] != '0':
            lines.append(f"{'Net Income':<30} {'':>12} {self._format_amount(data['net_income']):>12} {'':>12}")
        lines.append(self._line())
        lines.append(f"{'Total Equity':<30} {self._format_amount(data['opening_total'])} {'':>12} {self._format_amount(data['closing_total'])}")
        lines.append(self._line())
        return "\n".join(lines)
