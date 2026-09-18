"""
PyLedger Utilities Module - Currency Management
"""

from decimal import Decimal, ROUND_HALF_UP
from pyledger.utils.validators import SUPPORTED_CURRENCIES


class FXProvider:
    """Abstract FX rate source (Phase 1: enables live/static/cached providers)."""

    def get_rate(self, currency: str) -> Decimal:
        raise NotImplementedError

    def convert(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        raise NotImplementedError


class CurrencyConverter(FXProvider):
    """Handle currency conversion (static table; swap via FXProvider later)."""
    
    def __init__(self):
        # Exchange rates relative to USD (can be updated)
        self.exchange_rates = {
            'USD': Decimal('1.0'),
            'EUR': Decimal('0.92'),
            'GBP': Decimal('0.79'),
            'SAR': Decimal('3.75'),
            'AED': Decimal('3.67'),
            'EGP': Decimal('30.5'),
            'JOD': Decimal('0.71'),
            'KWD': Decimal('0.31'),
        }
    
    def convert(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount
        """
        return self.convert_amount(Decimal(str(amount)), from_currency, to_currency)

    def get_rate(self, currency: str) -> Decimal:
        currency = currency.upper()
        if currency not in self.exchange_rates:
            raise ValueError(f"Currency {currency} not supported")
        return self.exchange_rates[currency]

    def convert_amount(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in self.exchange_rates:
            raise ValueError(f"Currency {from_currency} not supported")
        if to_currency not in self.exchange_rates:
            raise ValueError(f"Currency {to_currency} not supported")
        
        # Convert to USD first, then to target currency
        usd_amount = amount / self.exchange_rates[from_currency]
        return usd_amount * self.exchange_rates[to_currency]
    
    def update_rate(self, currency: str, rate: Decimal):
        """Update exchange rate for a currency (must be > 0)"""
        currency = currency.upper()
        if currency not in self.exchange_rates:
            raise ValueError(f"Currency {currency} not supported")
        rate = Decimal(str(rate))
        if rate <= 0:
            raise ValueError(f"Exchange rate must be positive, got {rate}")
        self.exchange_rates[currency] = rate
    
    def get_symbol(self, currency: str) -> str:
        """Get currency symbol"""
        return SUPPORTED_CURRENCIES.get(currency.upper(), currency)


class Money:
    """Represents money with amount and currency - supports cross-currency ops"""

    _converter = None

    def __init__(self, amount, currency: str = 'USD'):
        self.amount = Decimal(str(amount))
        self.currency = currency.upper()
        if self.currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")

    @classmethod
    def _get_converter(cls) -> 'CurrencyConverter':
        if cls._converter is None:
            cls._converter = CurrencyConverter()
        return cls._converter

    def convert_to(self, target_currency: str) -> 'Money':
        if self.currency == target_currency.upper():
            return self
        converted = self._get_converter().convert(self.amount, self.currency, target_currency)
        return Money(converted, target_currency)

    def __str__(self) -> str:
        symbol = SUPPORTED_CURRENCIES.get(self.currency, self.currency)
        return f"{symbol}{self.amount:,.2f}"

    def __add__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return Money(self.amount + other.amount, self.currency)
            converted = other.convert_to(self.currency)
            return Money(self.amount + converted.amount, self.currency)
        return Money(self.amount + Decimal(str(other)), self.currency)

    def __sub__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return Money(self.amount - other.amount, self.currency)
            converted = other.convert_to(self.currency)
            return Money(self.amount - converted.amount, self.currency)
        return Money(self.amount - Decimal(str(other)), self.currency)

    def __mul__(self, other):
        return Money(self.amount * Decimal(str(other)), self.currency)

    def __truediv__(self, other):
        return Money(self.amount / Decimal(str(other)), self.currency)

    def __eq__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return self.amount == other.amount
            return self.amount == other.convert_to(self.currency).amount
        return self.amount == Decimal(str(other))

    def __lt__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return self.amount < other.amount
            return self.amount < other.convert_to(self.currency).amount
        return self.amount < Decimal(str(other))

    def __gt__(self, other):
        if isinstance(other, Money):
            if self.currency == other.currency:
                return self.amount > other.amount
            return self.amount > other.convert_to(self.currency).amount
        return self.amount > Decimal(str(other))

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return self == other or self > other

    def __neg__(self):
        return Money(-self.amount, self.currency)

    def __abs__(self):
        return Money(abs(self.amount), self.currency)

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"

    def quantize(self) -> 'Money':
        """Round to currency decimals (KWD/BHD/OMR use 3, others 2)."""
        places = 3 if self.currency in ('KWD', 'BHD', 'OMR', 'JOD') else 2
        q = Decimal(10) ** -places
        return Money(self.amount.quantize(q, rounding=ROUND_HALF_UP), self.currency)

    def allocate(self, ratios) -> list:
        """Split money by ratios without losing cents (enterprise split)."""
        total_ratio = sum(ratios)
        results = []
        allocated = Decimal('0')
        places = 3 if self.currency in ('KWD', 'BHD', 'OMR', 'JOD') else 2
        q = Decimal(10) ** -places
        for i, r in enumerate(ratios):
            if i == len(ratios) - 1:
                results.append(Money(self.amount - allocated, self.currency))
            else:
                share = (self.amount * Decimal(str(r)) / Decimal(str(total_ratio))).quantize(
                    q, rounding=ROUND_HALF_UP)
                allocated += share
                results.append(Money(share, self.currency))
        return results
