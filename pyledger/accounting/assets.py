"""
PyLedger Accounting - Fixed Assets Register
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import Optional, List
from pyledger.core.account import Account
from pyledger.core.journal import JournalEntry
from pyledger.core.ledger import Ledger


class DepreciationMethod:
    STRAIGHT_LINE = 'straight_line'
    DECLINING_BALANCE = 'declining_balance'
    SUM_OF_YEARS = 'sum_of_years'


class FixedAsset:
    """Represents a fixed asset with depreciation tracking"""

    def __init__(self, name: str, cost, asset_code: str,
                 useful_life_years: int,
                 depreciation_method: str = DepreciationMethod.STRAIGHT_LINE,
                 residual_value: Decimal = Decimal('0'),
                 acquisition_date: datetime = None,
                 category: str = 'general',
                 description: str = ''):
        self.name = name
        self.cost = Decimal(str(cost))
        self.asset_code = asset_code
        self.useful_life = useful_life_years
        self.depreciation_method = depreciation_method
        self.residual_value = Decimal(str(residual_value))
        self.acquisition_date = acquisition_date or datetime.now()
        self.category = category
        self.description = description
        self.accumulated_depreciation = Decimal('0')
        self.disposal_date = None
        self.disposal_price = None
        self.disposed = False

    @property
    def net_book_value(self) -> Decimal:
        return (self.cost - self.accumulated_depreciation).quantize(Decimal('0.01'))

    @property
    def depreciable_amount(self) -> Decimal:
        return (self.cost - self.residual_value).quantize(Decimal('0.01'))

    def _days_in_year(self, year: int) -> int:
        from calendar import isleap
        return 366 if isleap(year) else 365

    def annual_depreciation(self, year: int = None) -> Decimal:
        if self.useful_life == 0:
            return Decimal('0')

        if self.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            return (self.depreciable_amount / Decimal(str(self.useful_life))).quantize(Decimal('0.01'))

        elif self.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
            rate = Decimal('2') / Decimal(str(self.useful_life))
            nbv = self.net_book_value
            depr = (nbv * rate).quantize(Decimal('0.01'))
            if (nbv - depr) < self.residual_value:
                depr = nbv - self.residual_value
            return max(depr, Decimal('0'))

        elif self.depreciation_method == DepreciationMethod.SUM_OF_YEARS:
            remaining = self.useful_life - (year or 0)
            if remaining <= 0:
                return Decimal('0')
            syd_sum = self.useful_life * (self.useful_life + 1) // 2
            return (self.depreciable_amount * Decimal(str(remaining)) / Decimal(str(syd_sum))).quantize(Decimal('0.01'))

        return Decimal('0')

    def monthly_depreciation(self, month_date: datetime = None) -> Decimal:
        date = month_date or datetime.now()
        year = date.year
        days_in_year = self._days_in_year(year)
        annual = self.annual_depreciation(year=0)
        day_frac = Decimal(str(self._days_in_month(date))) / Decimal(str(days_in_year))
        return (annual * day_frac).quantize(Decimal('0.01'))

    @staticmethod
    def _days_in_month(dt: datetime) -> int:
        from calendar import monthrange
        return monthrange(dt.year, dt.month)[1]

    def dispose(self, disposal_price, date: datetime = None) -> dict:
        self.disposed = True
        self.disposal_date = date or datetime.now()
        self.disposal_price = Decimal(str(disposal_price))
        gain_loss = self.disposal_price - self.net_book_value
        return {
            'asset': self.name,
            'net_book_value': self.net_book_value,
            'disposal_price': self.disposal_price,
            'gain_loss': gain_loss,
        }

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'cost': str(self.cost),
            'asset_code': self.asset_code,
            'useful_life': self.useful_life,
            'depreciation_method': self.depreciation_method,
            'residual_value': str(self.residual_value),
            'accumulated_depreciation': str(self.accumulated_depreciation),
            'net_book_value': str(self.net_book_value),
            'category': self.category,
            'disposed': self.disposed,
            'acquisition_date': self.acquisition_date.isoformat() if self.acquisition_date else None,
        }


class DepreciationEngine:
    """Manage depreciation postings for fixed assets"""

    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.assets = {}

    def register_asset(self, asset: FixedAsset):
        self.assets[asset.name] = asset

    def get_asset(self, name: str) -> FixedAsset:
        return self.assets.get(name)

    def get_all_assets(self) -> list:
        return list(self.assets.values())

    def post_depreciation(self, asset_name: str, amount=None,
                          depr_expense_code: str = '5700',
                          accum_depr_code: str = '1900',
                          date: datetime = None) -> dict:
        asset = self.get_asset(asset_name)
        if not asset:
            raise ValueError(f"Asset '{asset_name}' not found")

        date = date or datetime.now()
        amount = amount or asset.monthly_depreciation(date)
        amt = Decimal(str(amount))

        entry = JournalEntry(f"Depreciation - {asset_name}", date=date)
        entry.add_debit(self.ledger.get_account(depr_expense_code), amt,
                        f"Depreciation {asset_name}")
        entry.add_credit(self.ledger.get_account(accum_depr_code), amt,
                         f"Accumulated depreciation {asset_name}")
        entry.post()
        self.ledger.journal_entries.append(entry)

        asset.accumulated_depreciation += amt

        return {
            'entry_number': entry.number,
            'asset': asset_name,
            'depreciation': amt,
            'accumulated': asset.accumulated_depreciation,
            'net_book_value': asset.net_book_value,
        }

    def post_all_depreciation(self, date: datetime = None) -> list:
        results = []
        for name in self.assets:
            asset = self.assets[name]
            if not asset.disposed:
                result = self.post_depreciation(name, date=date)
                results.append(result)
        return results

    def dispose_asset(self, asset_name: str, disposal_price,
                      asset_code: str = '1500',
                      accum_depr_code: str = '1900',
                      gain_loss_code: str = '4200',
                      cash_code: str = '1000',
                      date: datetime = None) -> dict:
        asset = self.get_asset(asset_name)
        if not asset:
            raise ValueError(f"Asset '{asset_name}' not found")

        date = date or datetime.now()
        result = asset.dispose(disposal_price, date)
        price = Decimal(str(disposal_price))

        entry = JournalEntry(f"Disposal of {asset_name}", date=date)
        entry.add_debit(self.ledger.get_account(cash_code), price,
                        f"Sale proceeds - {asset_name}")
        entry.add_credit(self.ledger.get_account(asset_code), asset.cost,
                         f"Remove asset cost - {asset_name}")
        entry.add_debit(self.ledger.get_account(accum_depr_code),
                        asset.accumulated_depreciation,
                        f"Remove accum depr - {asset_name}")

        if result['gain_loss'] > 0:
            entry.add_credit(self.ledger.get_account(gain_loss_code),
                             result['gain_loss'],
                             f"Gain on sale - {asset_name}")
        elif result['gain_loss'] < 0:
            entry.add_debit(self.ledger.get_account('5800'),
                            abs(result['gain_loss']),
                            f"Loss on sale - {asset_name}")

        entry.post()
        self.ledger.journal_entries.append(entry)
        result['entry_number'] = entry.number
        return result
