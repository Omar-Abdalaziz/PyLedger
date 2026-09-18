"""
PyLedger Accounting Module - Invoice
Invoice management
"""

from decimal import Decimal
from datetime import datetime
from enum import Enum
from pyledger.utils.validators import format_amount
from pyledger.accounting.tax import Tax


def _sanitize_amount(*args, **kwargs):
    from pyledger.security.sanitizer import sanitize_amount
    return sanitize_amount(*args, **kwargs)


def _sanitize_quantity(*args, **kwargs):
    from pyledger.security.sanitizer import sanitize_quantity
    return sanitize_quantity(*args, **kwargs)


def _sanitize_text(*args, **kwargs):
    from pyledger.security.sanitizer import sanitize_text
    return sanitize_text(*args, **kwargs)


class InvoiceStatus(Enum):
    """Invoice status"""
    DRAFT = 'draft'
    ISSUED = 'issued'
    SENT = 'sent'
    PARTIALLY_PAID = 'partially_paid'
    PAID = 'paid'
    CANCELLED = 'cancelled'


class InvoiceItem:
    """Represents an invoice line item"""
    
    def __init__(self, description: str, quantity: Decimal, unit_price: Decimal):
        """
        Initialize an invoice item

        Args:
            description: Item description
            quantity: Quantity (must be > 0)
            unit_price: Unit price (must be >= 0; 0 = free item)
        """
        try:
            quantity = _sanitize_quantity(quantity)
        except ValueError as e:
            raise ValueError(f"Invalid item quantity: {e}")
        if quantity <= 0:
            raise ValueError(f"Item quantity must be positive, got {quantity}")
        try:
            unit_price = _sanitize_amount(unit_price, allow_negative=False)
        except ValueError as e:
            raise ValueError(f"Invalid item unit price: {e}")
        self.description = _sanitize_text(description)
        self.quantity = quantity
        self.unit_price = unit_price
    
    def get_total(self) -> Decimal:
        """Get item total (quantity * unit_price)"""
        return format_amount(self.quantity * self.unit_price)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'description': self.description,
            'quantity': str(self.quantity),
            'unit_price': str(self.unit_price),
            'total': str(self.get_total()),
        }


class Invoice:
    """
    Represents an invoice
    
    Attributes:
        number: Unique invoice number
        customer: Customer name or info
        date: Invoice date
        items: List of invoice items
        status: Invoice status
        total: Invoice total
        tax: Tax applied to invoice
    """
    
    _invoice_counter = 0
    
    def __init__(
        self,
        customer: str,
        invoice_number: str = None,
        date: datetime = None,
        currency: str = 'USD',
        unique_number: bool = False,
    ):
        """
        Initialize an Invoice
        
        Args:
            customer: Customer name
            invoice_number: Invoice number (auto-generated if not provided)
            date: Invoice date (default: now)
            currency: Invoice currency
            unique_number: Use UUID-based globally unique number
        """
        from pyledger.core.sequences import next_invoice_number
        Invoice._invoice_counter += 1
        self.number = next_invoice_number(invoice_number, unique=unique_number)
        self.customer = customer
        self.date = date or datetime.now()
        self.currency = currency
        self.items = []
        self.taxes = []
        self.status = InvoiceStatus.DRAFT
        self.subtotal = Decimal('0')
        self.tax_total = Decimal('0')
        self.total = Decimal('0')
        self.paid_amount = Decimal('0')
        self.notes = ''
        self.due_date = None
    
    def add_item(self, description: str, quantity, unit_price) -> 'Invoice':
        """
        Add an item to the invoice
        
        Args:
            description: Item description
            quantity: Quantity
            unit_price: Unit price
            
        Returns:
            Self for method chaining
        """
        item = InvoiceItem(description, quantity, unit_price)
        self.items.append(item)
        self._recalculate()
        return self
    
    def remove_item(self, index: int) -> 'Invoice':
        """Remove an item by index"""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self._recalculate()
        return self
    
    def _recalculate(self):
        """Recalculate subtotal and total"""
        self.subtotal = sum(
            (item.get_total() for item in self.items),
            Decimal('0')
        )
        self.total = format_amount(self.subtotal + self.tax_total)
    
    def add_tax(self, tax: Tax) -> 'Invoice':
        """Add a tax to the invoice.

        Multiple taxes ACCUMULATE on the subtotal (non-compound), matching
        the documented multi-tax support. Previously each call replaced
        the previous tax.
        """
        self.taxes.append(tax)
        self.tax_total = format_amount(
            sum((t.calculate(self.subtotal) for t in self.taxes), Decimal('0')))
        self._recalculate()
        return self

    def apply_tax(self, name: str, rate) -> 'Invoice':
        """Convenience: create Tax(name, rate) and apply it (test-suite API)."""
        return self.add_tax(Tax(name, rate))
    
    def calculate_total(self) -> Decimal:
        """Calculate invoice total"""
        self._recalculate()
        return self.total
    
    def get_remaining_balance(self) -> Decimal:
        """Get remaining balance to be paid"""
        return format_amount(self.total - self.paid_amount)
    
    def pay(self, amount, method: str = 'cash') -> bool:
        """
        Record a payment

        Args:
            amount: Payment amount (must be > 0)
            method: Payment method (cash, check, transfer, etc.)

        Returns:
            True if payment recorded
        """
        try:
            amount = _sanitize_amount(amount, allow_zero=False, allow_negative=False)
        except ValueError as e:
            raise ValueError(f"Invalid payment amount: {e}")
        self.paid_amount = format_amount(self.paid_amount + amount)
        
        remaining = self.get_remaining_balance()
        
        if remaining <= Decimal('0'):
            self.status = InvoiceStatus.PAID
        elif self.paid_amount > Decimal('0'):
            self.status = InvoiceStatus.PARTIALLY_PAID
        
        return True

    def record_payment(self, amount, method: str = 'cash') -> bool:
        """Alias for pay() - required by test suite."""
        # Auto-issue draft invoices on first payment (enterprise-friendly)
        if self.status == InvoiceStatus.DRAFT:
            self.issue()
        return self.pay(amount, method)
    
    def issue(self) -> bool:
        """Change status to issued (from draft/sent)."""
        if self.status in [InvoiceStatus.DRAFT, InvoiceStatus.SENT]:
            self.status = InvoiceStatus.ISSUED
            return True
        return self.status == InvoiceStatus.ISSUED
    
    def cancel(self) -> bool:
        """Cancel the invoice"""
        if self.status not in [InvoiceStatus.PAID]:
            self.status = InvoiceStatus.CANCELLED
            return True
        return False
    
    def get_status(self) -> str:
        """Get current status"""
        return self.status.value
    
    def __str__(self) -> str:
        return (
            f"Invoice {self.number}\n"
            f"Customer: {self.customer}\n"
            f"Date: {self.date.strftime('%Y-%m-%d')}\n"
            f"Subtotal: {self.subtotal}\n"
            f"Tax: {self.tax_total}\n"
            f"Total: {self.total}\n"
            f"Status: {self.status.value}"
        )
    
    def to_dict(self) -> dict:
        """Convert invoice to dictionary"""
        return {
            'number': self.number,
            'customer': self.customer,
            'date': self.date.isoformat(),
            'currency': self.currency,
            'items': [item.to_dict() for item in self.items],
            'taxes': [{'name': t.name, 'rate': str(t.rate),
                       'amount': str(t.calculate(self.subtotal))} for t in self.taxes],
            'subtotal': str(self.subtotal),
            'tax_total': str(self.tax_total),
            'total': str(self.total),
            'paid_amount': str(self.paid_amount),
            'remaining_balance': str(self.get_remaining_balance()),
            'status': self.status.value,
            'notes': self.notes,
            'due_date': self.due_date.isoformat() if self.due_date else None,
        }
