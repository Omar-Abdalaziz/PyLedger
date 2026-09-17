"""
PyLedger Core - Closing Engine
Period-end closing entries for financial periods
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pyledger.core.ledger import Ledger
from pyledger.core.journal import JournalEntry
from pyledger.core.account import Account
from pyledger.core.immutable import AuditTrail, AuditEntry
from pyledger.reports.base import FinancialPeriod
from pyledger.exceptions.errors import PyLedgerException


class PeriodClosedError(PyLedgerException):
    """Raised when trying to post to a closed period"""
    pass


class ClosingEngine:
    """Handle period-end closing entries"""

    def __init__(self, ledger: Ledger, audit_trail: AuditTrail = None):
        self.ledger = ledger
        self.audit = audit_trail or AuditTrail()
        self.closed_periods = []

    def close_month(self, year: int, month: int,
                    retained_earnings_code: str = '3100',
                    user: str = 'system') -> dict:
        """Close income/expense accounts for a month and transfer to retained earnings"""
        period = FinancialPeriod.monthly(year, month)
        return self._close_period(period, retained_earnings_code, user)

    def close_quarter(self, year: int, quarter: int,
                      retained_earnings_code: str = '3100',
                      user: str = 'system') -> dict:
        period = FinancialPeriod.quarterly(year, quarter)
        return self._close_period(period, retained_earnings_code, user)

    def close_year(self, year: int,
                   retained_earnings_code: str = '3100',
                   user: str = 'system') -> dict:
        period = FinancialPeriod.annual(year)
        return self._close_period(period, retained_earnings_code, user)

    def _close_period(self, period: FinancialPeriod,
                      re_code: str, user: str) -> dict:
        if period.label in self.closed_periods:
            raise PeriodClosedError(f"Period {period.label} is already closed")

        income_total = Decimal('0')
        expense_total = Decimal('0')
        closing_entries = []

        income_accounts = self.ledger.get_accounts_by_type('income')
        for acc in income_accounts:
            bal = acc.get_balance()
            if bal == 0:
                continue
            income_total += bal
            entry = JournalEntry(f"Close {acc.name} - {period.label}", date=period.end_date)
            entry.add_debit(acc, bal, f"Closing {acc.name}")
            closing_entries.append(entry)

        expense_accounts = self.ledger.get_accounts_by_type('expense')
        for acc in expense_accounts:
            bal = acc.get_balance()
            if bal == 0:
                continue
            expense_total += bal
            entry = JournalEntry(f"Close {acc.name} - {period.label}", date=period.end_date)
            entry.add_credit(acc, bal, f"Closing {acc.name}")
            closing_entries.append(entry)

        net_income = income_total - expense_total

        re_entry = JournalEntry(
            f"Transfer net income to retained earnings - {period.label}",
            date=period.end_date
        )

        re_account = self.ledger.get_account(re_code)
        if net_income >= 0:
            re_entry.add_debit(
                Account(f"Income Summary {period.label}", 'income', 'TEMPIS'),
                net_income
            ).add_credit(re_account, net_income, f"Net income {period.label}")
        else:
            re_entry.add_credit(
                Account(f"Income Summary {period.label}", 'income', 'TEMPIS'),
                abs(net_income)
            ).add_debit(re_account, abs(net_income), f"Net loss {period.label}")

        all_entries = closing_entries + [re_entry]
        for e in all_entries:
            e.post()
            self.ledger.journal_entries.append(e)

        self.closed_periods.append(period.label)

        self.audit.record(
            action='close_period',
            entity_type='period',
            entity_id=period.label,
            after={'closed': True, 'net_income': str(net_income),
                   'entries': len(all_entries)},
            user=user,
            reason=f"Close period {period.label}"
        )

        return {
            'period': period.label,
            'income_total': income_total,
            'expense_total': expense_total,
            'net_income': net_income,
            'entries_created': len(all_entries),
        }

    def is_period_closed(self, period: FinancialPeriod) -> bool:
        return period.label in self.closed_periods

    def get_closed_periods(self) -> list:
        return list(self.closed_periods)
