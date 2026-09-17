"""
PyLedger Accounting - Deferred Revenue & Prepaid Expenses
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger
from pyledger.core.journal import JournalEntry


class _MonthsMixin:
    @staticmethod
    def _diff_months(start: datetime, end: datetime) -> int:
        months = (end.year - start.year) * 12 + (end.month - start.month)
        if end.day > start.day:
            months += 1
        return max(1, months)

    @staticmethod
    def _add_months(dt: datetime, n: int) -> datetime:
        total_months = dt.year * 12 + dt.month - 1 + n
        year = total_months // 12
        month = total_months % 12 + 1
        from calendar import monthrange
        max_day = monthrange(year, month)[1]
        day = min(dt.day, max_day)
        return dt.replace(year=year, month=month, day=day)


class DeferredRevenue(_MonthsMixin):
    """Track deferred (unearned) revenue with amortization schedule"""

    def __init__(self, description: str, total_amount: Decimal,
                 recognition_start: datetime, recognition_end: datetime,
                 deferred_account: str = '2400',
                 revenue_account: str = '4000',
                 deferral_id: str = None):
        self.deferral_id = deferral_id or f"DEFR-{id(self)}"
        self.description = description
        self.total_amount = Decimal(str(total_amount))
        self.recognized_amount = Decimal('0')
        self.recognition_start = recognition_start
        self.recognition_end = recognition_end
        self.deferred_account = deferred_account
        self.revenue_account = revenue_account
        self.schedule = []
        self._schedule_map = {}
        self.created_at = datetime.now()

    def get_deferred_balance(self) -> Decimal:
        return self.total_amount - self.recognized_amount

    def get_months(self) -> int:
        return self._diff_months(self.recognition_start, self.recognition_end)

    def get_monthly_amount(self) -> Decimal:
        return (self.total_amount / Decimal(str(self.get_months()))).quantize(Decimal('0.01'))

    def generate_schedule(self) -> list:
        self.schedule = []
        self._schedule_map = {}
        monthly = self.get_monthly_amount()
        remaining = self.total_amount
        current = self.recognition_start

        for i in range(self.get_months()):
            amount = monthly if i < self.get_months() - 1 else remaining
            entry = {
                'period': current.strftime('%Y-%m'),
                'amount': str(amount),
                'running_deferred': str(remaining - amount),
                'status': 'pending',
            }
            self.schedule.append(entry)
            self._schedule_map[entry['period']] = entry
            remaining -= amount
            current = self._add_months(current, 1)
        return self.schedule

    def recognize(self, period: str, amount: Decimal = None) -> dict:
        if not self.schedule:
            self.generate_schedule()
        entry = self._schedule_map.get(period)
        if entry and entry['status'] == 'pending':
            amt = Decimal(str(amount)) if amount else Decimal(entry['amount'])
            entry['status'] = 'recognized'
            self.recognized_amount += amt
            return {
                'debit': self.deferred_account,
                'credit': self.revenue_account,
                'amount': str(amt),
                'period': period,
            }
        raise ValueError(f"No pending entry for period {period}")

    def to_dict(self) -> dict:
        return {
            'deferral_id': self.deferral_id,
            'description': self.description,
            'total': str(self.total_amount),
            'recognized': str(self.recognized_amount),
            'deferred': str(self.get_deferred_balance()),
            'schedule': self.schedule,
        }


class PrepaidExpense(_MonthsMixin):
    """Track prepaid expenses with amortization"""

    def __init__(self, description: str, total_amount: Decimal,
                 amortization_start: datetime, amortization_end: datetime,
                 prepaid_account: str = '1400',
                 expense_account: str = '5000',
                 prepaid_id: str = None):
        self.prepaid_id = prepaid_id or f"PRE-{id(self)}"
        self.description = description
        self.total_amount = Decimal(str(total_amount))
        self.amortized_amount = Decimal('0')
        self.amortization_start = amortization_start
        self.amortization_end = amortization_end
        self.prepaid_account = prepaid_account
        self.expense_account = expense_account
        self.schedule = []
        self._schedule_map = {}

    def get_prepaid_balance(self) -> Decimal:
        return self.total_amount - self.amortized_amount

    def get_months(self) -> int:
        return self._diff_months(self.amortization_start, self.amortization_end)

    def get_monthly_amount(self) -> Decimal:
        return (self.total_amount / Decimal(str(self.get_months()))).quantize(Decimal('0.01'))

    def generate_schedule(self) -> list:
        monthly = self.get_monthly_amount()
        remaining = self.total_amount
        current = self.amortization_start
        self.schedule = []
        self._schedule_map = {}
        for i in range(self.get_months()):
            amount = monthly if i < self.get_months() - 1 else remaining
            entry = {
                'period': current.strftime('%Y-%m'),
                'amount': str(amount),
                'running_prepaid': str(remaining - amount),
                'status': 'pending',
            }
            self.schedule.append(entry)
            self._schedule_map[entry['period']] = entry
            remaining -= amount
            current = self._add_months(current, 1)
        return self.schedule

    def amortize(self, period: str, amount: Decimal = None) -> dict:
        if not self.schedule:
            self.generate_schedule()
        entry = self._schedule_map.get(period)
        if entry and entry['status'] == 'pending':
            amt = Decimal(str(amount)) if amount else Decimal(entry['amount'])
            entry['status'] = 'amortized'
            self.amortized_amount += amt
            return {
                'debit': self.expense_account,
                'credit': self.prepaid_account,
                'amount': str(amt),
                'period': period,
            }
        raise ValueError(f"No pending entry for period {period}")

    def to_dict(self) -> dict:
        return {
            'prepaid_id': self.prepaid_id,
            'description': self.description,
            'total': str(self.total_amount),
            'amortized': str(self.amortized_amount),
            'prepaid': str(self.get_prepaid_balance()),
            'schedule': self.schedule,
        }
