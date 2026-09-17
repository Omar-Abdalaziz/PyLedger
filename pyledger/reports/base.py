"""
PyLedger Reports Module - Base Report
Abstract base class for all financial reports
"""

from decimal import Decimal
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pyledger.core.ledger import Ledger


class FinancialPeriod:
    """Represents a financial reporting period"""

    def __init__(self, start_date: datetime, end_date: datetime, label: str = None):
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")
        self.start_date = start_date
        self.end_date = end_date
        self.label = label or f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    @classmethod
    def monthly(cls, year: int, month: int) -> 'FinancialPeriod':
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)
        end = end.replace(hour=23, minute=59, second=59)
        return cls(start, end, f"{year}-{month:02d}")

    @classmethod
    def quarterly(cls, year: int, quarter: int) -> 'FinancialPeriod':
        start_month = (quarter - 1) * 3 + 1
        start = datetime(year, start_month, 1)
        if start_month + 3 > 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, start_month + 3, 1) - timedelta(days=1)
        end = end.replace(hour=23, minute=59, second=59)
        return cls(start, end, f"{year} Q{quarter}")

    @classmethod
    def annual(cls, year: int) -> 'FinancialPeriod':
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)
        return cls(start, end, str(year))

    @classmethod
    def year_to_date(cls, year: int, month: int) -> 'FinancialPeriod':
        start = datetime(year, 1, 1)
        end = datetime(year, month, 1)
        if month == 12:
            end = datetime(year, 12, 31, 23, 59, 59)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)
            end = end.replace(hour=23, minute=59, second=59)
        return cls(start, end, f"YTD {year}-{month:02d}")


class BaseReport(ABC):
    """Abstract base class for all financial reports"""

    def __init__(self, ledger: Ledger, period: Optional[FinancialPeriod] = None,
                 as_of_date: Optional[datetime] = None, currency: Optional[str] = None):
        self.ledger = ledger
        self.period = period
        self.as_of_date = as_of_date or datetime.now()
        self.currency = currency or ledger.currency
        self.generated_date = datetime.now()

    @abstractmethod
    def generate(self) -> dict:
        """Generate report data as dictionary"""

    def to_dict(self) -> dict:
        """Convert report to dictionary with metadata"""
        data = self.generate()
        data.update({
            'report_type': self.__class__.__name__,
            'generated_date': self.generated_date.isoformat(),
            'currency': self.currency,
        })
        if self.period:
            data['period'] = {
                'start': self.period.start_date.isoformat(),
                'end': self.period.end_date.isoformat(),
                'label': self.period.label,
            }
        if self.as_of_date:
            data['as_of_date'] = self.as_of_date.isoformat()
        return data

    def __str__(self) -> str:
        return self._format_text()

    @abstractmethod
    def _format_text(self) -> str:
        """Format report as text for console output"""

    def _format_amount(self, amount) -> str:
        """Format amount for display"""
        if isinstance(amount, str):
            amount = Decimal(amount)
        return f"{amount:>15,.2f}"

    def _line(self, char: str = '=', width: int = 68) -> str:
        return char * width

    def _title_block(self, title: str, subtitle: str = '') -> List[str]:
        lines = [self._line(), title.center(68)]
        if subtitle:
            lines.append(subtitle.center(68))
        lines.append(self._line())
        return lines
