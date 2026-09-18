"""
PyLedger Accounting Module - Tax
Tax calculation and management
"""

from decimal import Decimal
from pyledger.utils.validators import format_amount, validate_tax_rate


class Tax:
    """Handle tax calculations"""
    
    def __init__(self, name: str, rate: float):
        """
        Initialize a Tax
        
        Args:
            name: Tax name (e.g., 'VAT', 'Sales Tax')
            rate: Tax rate as percentage (0-100)
        """
        validate_tax_rate(rate)
        self.name = name
        self.rate = Decimal(str(rate))
    
    def calculate(self, amount) -> Decimal:
        """
        Calculate tax amount
        
        Args:
            amount: Base amount
            
        Returns:
            Tax amount
        """
        amount = format_amount(amount)
        tax_amount = amount * (self.rate / Decimal('100'))
        return format_amount(tax_amount)
    
    def calculate_total(self, amount) -> Decimal:
        """
        Calculate total amount including tax
        
        Args:
            amount: Base amount
            
        Returns:
            Total amount (base + tax)
        """
        amount = format_amount(amount)
        tax = self.calculate(amount)
        return format_amount(amount + tax)
    
    @staticmethod
    def calculate_vat(amount, rate: float) -> dict:
        """
        Calculate VAT (Value Added Tax)
        
        Args:
            amount: Base amount
            rate: VAT rate as percentage
            
        Returns:
            Dictionary with base, vat, and total
        """
        validate_tax_rate(rate)
        
        amount = format_amount(amount)
        vat_rate = Decimal(str(rate))
        vat_amount = amount * (vat_rate / Decimal('100'))
        vat_amount = format_amount(vat_amount)
        
        return {
            'base': amount,
            'vat_rate': vat_rate,
            'vat_amount': vat_amount,
            'total': format_amount(amount + vat_amount),
        }
    
    @staticmethod
    def reverse_calculate(total_with_tax, rate: float) -> dict:
        """
        Calculate original amount from total (including tax)
        
        Args:
            total_with_tax: Total amount including tax
            rate: Tax rate as percentage
            
        Returns:
            Dictionary with base, tax, and total
        """
        validate_tax_rate(rate)
        
        total = format_amount(total_with_tax)
        rate_decimal = Decimal(str(rate))
        
        # Formula: base = total / (1 + rate/100)
        base = total / (Decimal('1') + (rate_decimal / Decimal('100')))
        base = format_amount(base)
        
        tax_amount = format_amount(total - base)
        
        return {
            'base': base,
            'tax_rate': rate_decimal,
            'tax_amount': tax_amount,
            'total': total,
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.rate}%)"
    
    def __repr__(self) -> str:
        return f"Tax({self.name}, {self.rate}%)"


class TaxCalculator:
    """Calculate multiple taxes on an amount"""
    
    def __init__(self):
        self.taxes = {}
    
    def add_tax(self, name: str, rate: float) -> 'TaxCalculator':
        """Add a tax"""
        validate_tax_rate(rate)
        self.taxes[name] = Decimal(str(rate))
        return self
    
    def remove_tax(self, name: str):
        """Remove a tax"""
        if name in self.taxes:
            del self.taxes[name]
    
    def calculate_all(self, amount) -> dict:
        """
        Calculate all taxes on an amount
        
        Args:
            amount: Base amount
            
        Returns:
            Dictionary with breakdown of all taxes
        """
        amount = format_amount(amount)
        total_tax = Decimal('0')
        taxes_breakdown = {}
        
        for tax_name, rate in self.taxes.items():
            tax_amount = amount * (rate / Decimal('100'))
            tax_amount = format_amount(tax_amount)
            taxes_breakdown[tax_name] = {
                'rate': rate,
                'amount': tax_amount,
            }
            total_tax += tax_amount
        
        return {
            'base': amount,
            'taxes': taxes_breakdown,
            'total_tax': format_amount(total_tax),
            'total': format_amount(amount + total_tax),
        }
