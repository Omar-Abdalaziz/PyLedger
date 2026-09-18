"""
PyLedger Accounting - Fixed Assets Register
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from pyledger.core.journal import JournalEntry
from pyledger.core.ledger import Ledger


class DepreciationMethod:
    """All globally used depreciation methods (IAS 16 / GAAP / US tax)."""
    STRAIGHT_LINE = 'straight_line'
    DECLINING_BALANCE = 'declining_balance'
    SUM_OF_YEARS = 'sum_of_years'
    UNITS_OF_PRODUCTION = 'units_of_production'
    MACRS = 'macrs'


# IRS MACRS GDS percentage tables (half-year convention, % of basis).
# Realty classes use straight-line mid-month computed on the fly.
MACRS_TABLES = {
    'GDS-3': [33.33, 44.45, 14.81, 7.41],
    'GDS-5': [20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
    'GDS-7': [14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
    'GDS-10': [10.00, 18.00, 14.40, 11.52, 9.22, 7.37, 6.55, 6.55, 6.56, 6.55, 3.28],
    'GDS-15': [5.00, 7.70, 6.93, 6.23, 5.90, 5.90, 5.91, 5.90, 5.91, 5.90, 5.91, 5.90, 5.91, 5.90, 2.95],
    'GDS-20': [3.75, 7.219, 6.677, 6.177, 5.713, 5.285, 5.285, 5.286, 5.285, 5.286,
               5.285, 5.286, 5.285, 5.286, 5.285, 5.286, 5.285, 5.286, 5.285, 1.314],
}
# (years, mid-month SL): residential rental / nonresidential real property.
MACRS_REALTY = {'GDS-27.5': 27.5, 'GDS-39': 39.0}

SUPPORTED_METHODS = [
    DepreciationMethod.STRAIGHT_LINE,
    DepreciationMethod.DECLINING_BALANCE,
    DepreciationMethod.SUM_OF_YEARS,
    DepreciationMethod.UNITS_OF_PRODUCTION,
    DepreciationMethod.MACRS,
]


class FixedAsset:
    """Represents a fixed asset with depreciation tracking"""

    def __init__(self, name: str, cost, asset_code: str,
                 useful_life_years: int,
                 depreciation_method: str = DepreciationMethod.STRAIGHT_LINE,
                 residual_value: Decimal = Decimal('0'),
                 acquisition_date: datetime = None,
                 category: str = 'general',
                 description: str = '',
                 rate_factor: float = 2.0,
                 total_estimated_units=None,
                 macrs_class: str = None,
                 placed_in_service_month: int = None,
                 convention: str = 'full'):
        """
        Args:
            rate_factor: declining-balance multiplier (2.0 = double/200%,
                1.5 = 150% as used in several tax regimes).
            total_estimated_units: lifetime output for UNITS_OF_PRODUCTION
                (machine hours, mileage, units mined...).
            macrs_class: for MACRS, e.g. 'GDS-5', 'GDS-7', 'GDS-27.5', 'GDS-39'.
            placed_in_service_month: 1-12, required for realty mid-month.
            convention: 'full' (full year) or 'half_year' (half in first and
                last year; US GAAP/tax style) for straight-line personalty.
        """
        if depreciation_method not in SUPPORTED_METHODS:
            raise ValueError(
                f"Unknown depreciation method '{depreciation_method}'. "
                f"Supported: {SUPPORTED_METHODS}")
        if depreciation_method == DepreciationMethod.UNITS_OF_PRODUCTION \
                and not total_estimated_units:
            raise ValueError("UNITS_OF_PRODUCTION requires total_estimated_units")
        if depreciation_method == DepreciationMethod.MACRS and not macrs_class:
            raise ValueError("MACRS requires macrs_class (e.g. 'GDS-5', 'GDS-27.5')")
        self.name = name
        self.cost = Decimal(str(cost))
        self.asset_code = asset_code
        self.useful_life = useful_life_years
        self.depreciation_method = depreciation_method
        self.residual_value = Decimal(str(residual_value))
        self.acquisition_date = acquisition_date or datetime.now()
        self.category = category
        self.description = description
        self.rate_factor = Decimal(str(rate_factor))
        self.total_estimated_units = (Decimal(str(total_estimated_units))
                                      if total_estimated_units else None)
        self.lifetime_produced = Decimal('0')
        self.macrs_class = macrs_class
        self.placed_in_service_month = placed_in_service_month
        self.convention = convention
        self.accumulated_depreciation = Decimal('0')
        self.disposal_date = None
        self.disposal_price = None
        self.disposed = False

    @property
    def net_book_value(self) -> Decimal:
        return (self.cost - self.accumulated_depreciation).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def depreciable_amount(self) -> Decimal:
        return (self.cost - self.residual_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _days_in_year(self, year: int) -> int:
        from calendar import isleap
        return 366 if isleap(year) else 365

    def annual_depreciation(self, year: int = None, units=None) -> Decimal:
        """Charge for one year.

        Args:
            year: 0-based elapsed year (0 = first year). Existing first-year
                semantics for SL/DB/SYD are unchanged.
            units: output this year (UNITS_OF_PRODUCTION only).
        """
        if self.useful_life == 0 and self.depreciation_method != DepreciationMethod.MACRS:
            return Decimal('0')

        if self.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            base = (self.depreciable_amount / Decimal(str(self.useful_life))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if self.convention == 'half_year' and year is not None \
                    and year in (0, self.useful_life - 1):
                return (base / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return base

        elif self.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
            rate = self.rate_factor / Decimal(str(self.useful_life))
            nbv = self.net_book_value
            depr = (nbv * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if (nbv - depr) < self.residual_value:
                depr = nbv - self.residual_value
            return max(depr, Decimal('0'))

        elif self.depreciation_method == DepreciationMethod.SUM_OF_YEARS:
            remaining = self.useful_life - (year or 0)
            if remaining <= 0:
                return Decimal('0')
            syd_sum = self.useful_life * (self.useful_life + 1) // 2
            return (self.depreciable_amount * Decimal(str(remaining)) / Decimal(str(syd_sum))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        elif self.depreciation_method == DepreciationMethod.UNITS_OF_PRODUCTION:
            return self.units_charge(Decimal(str(units or 0)))

        elif self.depreciation_method == DepreciationMethod.MACRS:
            return self.macrs_annual(year or 0)

        return Decimal('0')

    # ── Units of production (IAS 16.62) ──────────────────────────

    def units_charge(self, units) -> Decimal:
        """Depreciation for a given output, capped at depreciable amount."""
        units = Decimal(str(units))
        if units <= 0 or not self.total_estimated_units:
            return Decimal('0')
        remaining_units = self.total_estimated_units - self.lifetime_produced
        units = min(units, max(remaining_units, Decimal('0')))
        charge = (self.depreciable_amount * units / self.total_estimated_units).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
        remaining_book = self.net_book_value - self.residual_value
        return max(min(charge, max(remaining_book, Decimal('0'))), Decimal('0'))

    def record_production(self, units) -> Decimal:
        """Record output and return the depreciation charge for it."""
        charge = self.units_charge(units)
        self.lifetime_produced += Decimal(str(units))
        return charge

    # ── MACRS (US tax, IRS Pub. 946) ─────────────────────────────

    def macrs_annual(self, elapsed_year: int = 0) -> Decimal:
        """IRS table charge for a 0-based elapsed year (tax books: no salvage)."""
        if self.macrs_class in MACRS_TABLES:
            table = MACRS_TABLES[self.macrs_class]
            if elapsed_year >= len(table):
                return Decimal('0')
            return (self.cost * Decimal(str(table[elapsed_year])) / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
        if self.macrs_class in MACRS_REALTY:
            return self._macrs_realty_annual(elapsed_year)
        raise ValueError(f"Unknown MACRS class '{self.macrs_class}'")

    def _macrs_realty_annual(self, elapsed_year: int) -> Decimal:
        """Straight-line mid-month for 27.5/39-year real property."""
        total_months = int(MACRS_REALTY[self.macrs_class] * 12)
        month = self.placed_in_service_month or self.acquisition_date.month
        if not 1 <= month <= 12:
            raise ValueError("placed_in_service_month must be 1-12 for realty MACRS")
        first_year_months = Decimal(str(12 - month)) + Decimal('0.5')
        monthly = self.cost / Decimal(str(total_months))
        if elapsed_year == 0:
            months = first_year_months
        else:
            elapsed_before = first_year_months + Decimal(str(12 * (elapsed_year - 1)))
            months = min(Decimal('12'),
                         max(Decimal(str(total_months)) - elapsed_before, Decimal('0')))
        return (monthly * months).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # ── Full schedule (all methods, non-mutating) ────────────────

    def depreciation_schedule(self, years: int = None, units_per_year: list = None) -> list:
        """Year-by-year {year, depreciation, accumulated, book_value} table."""
        if years is None:
            if self.macrs_class in MACRS_TABLES:
                years = len(MACRS_TABLES[self.macrs_class])
            elif self.macrs_class in MACRS_REALTY:
                years = int(MACRS_REALTY[self.macrs_class]) + 1
            else:
                years = self.useful_life or 1
        rows, accum = [], Decimal('0')
        saved_accum, saved_produced = self.accumulated_depreciation, self.lifetime_produced
        try:
            for i in range(years):
                if self.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
                    self.accumulated_depreciation = accum
                    charge = self.annual_depreciation()
                elif self.depreciation_method == DepreciationMethod.UNITS_OF_PRODUCTION:
                    u = (units_per_year[i] if units_per_year and i < len(units_per_year)
                         else Decimal('0'))
                    charge = self.units_charge(u)
                    self.lifetime_produced += Decimal(str(u))
                else:
                    charge = self.annual_depreciation(year=i)
                floor = (Decimal('0') if self.depreciation_method == DepreciationMethod.MACRS
                         else self.residual_value)
                charge = min(charge, max(self.cost - accum - floor, Decimal('0')))
                accum += charge
                rows.append({'year': i + 1, 'depreciation': charge,
                             'accumulated': accum, 'book_value': self.cost - accum})
                if self.cost - accum <= floor:
                    break
        finally:
            self.accumulated_depreciation, self.lifetime_produced = saved_accum, saved_produced
        return rows

    def monthly_depreciation(self, month_date: datetime = None) -> Decimal:
        date = month_date or datetime.now()
        year = date.year
        days_in_year = self._days_in_year(year)
        annual = self.annual_depreciation(year=0)
        day_frac = Decimal(str(self._days_in_month(date))) / Decimal(str(days_in_year))
        return (annual * day_frac).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

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
            'rate_factor': str(self.rate_factor),
            'total_estimated_units': str(self.total_estimated_units) if self.total_estimated_units else None,
            'lifetime_produced': str(self.lifetime_produced),
            'macrs_class': self.macrs_class,
            'convention': self.convention,
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

    def generate_schedule(self, asset_name: str, years: int = None,
                          units_per_year: list = None) -> list:
        """Full depreciation table without posting (planning/disclosure)."""
        asset = self.get_asset(asset_name)
        if not asset:
            raise ValueError(f"Asset '{asset_name}' not found")
        return asset.depreciation_schedule(years=years, units_per_year=units_per_year)

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
