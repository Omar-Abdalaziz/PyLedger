"""
PyLedger Accounting Module - Payment
Payment processing
"""

from decimal import Decimal
from datetime import datetime
from enum import Enum
from pyledger.utils.validators import format_amount


def _strict_payment_amount(amount):
    from pyledger.security.sanitizer import sanitize_amount
    try:
        return sanitize_amount(amount, allow_zero=False, allow_negative=False)
    except ValueError as e:
        raise ValueError(f"Invalid payment amount: {e}")


class PaymentMethod(Enum):
    """Payment methods"""
    CASH = 'cash'
    CHECK = 'check'
    BANK_TRANSFER = 'bank_transfer'
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    PAYPAL = 'paypal'
    OTHER = 'other'


class PaymentStatus(Enum):
    """Payment status"""
    PENDING = 'pending'
    PROCESSED = 'processed'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class Payment:
    """
    Represents a payment
    
    Attributes:
        amount: Payment amount
        method: Payment method
        status: Payment status
        date: Payment date
        reference: Payment reference number
    """
    
    _payment_counter = 0
    
    def __init__(
        self,
        amount,
        party_or_method: str = 'cash',
        method: str = None,
        reference: str = None,
        date: datetime = None,
        unique_reference: bool = False,
    ):
        """
        Initialize a Payment

        Args:
            amount: Payment amount
            party_or_method: Customer/supplier id OR payment method.
                If it matches a known PaymentMethod value/name it is
                treated as method (backward compat); otherwise as party.
            method: Explicit payment method (overrides inference)
            reference: Payment reference number
            date: Payment date
        """
        from pyledger.core.sequences import next_payment_reference
        Payment._payment_counter += 1
        self.amount = _strict_payment_amount(amount)

        known_methods = {m.value for m in PaymentMethod} | {m.name for m in PaymentMethod}
        known_lower = {str(x).lower() for x in known_methods}

        party = None
        inferred_method = 'cash'
        token = str(party_or_method) if party_or_method is not None else 'cash'
        if method is not None:
            # Explicit method wins; first positional is party (unless it is
            # itself a method name and no real party was intended)
            inferred_method = method
            if token.lower() not in known_lower:
                party = token
        else:
            if token.lower() in known_lower:
                inferred_method = token
            else:
                party = token
                inferred_method = 'cash'

        self.party = party
        # Backward-compat aliases expected by older callers/tests
        self.payer = party
        self.customer = party
        if isinstance(inferred_method, str):
            key = inferred_method.upper()
            if key in PaymentMethod.__members__:
                self.method = PaymentMethod[key]
            else:
                # match by value (e.g. 'bank_transfer')
                self.method = PaymentMethod(inferred_method.lower())
        else:
            self.method = inferred_method
        self.reference = next_payment_reference(reference, unique=unique_reference)
        self.date = date or datetime.now()
        self.status = PaymentStatus.PENDING
        self.notes = ''
    
    def process(self) -> bool:
        """Process the payment (COMPLETED is canonical; PROCESSED kept as alias)."""
        if self.status == PaymentStatus.PENDING:
            self.status = PaymentStatus.COMPLETED
            return True
        return False

    @property
    def is_processed(self) -> bool:
        return self.status in (PaymentStatus.PROCESSED, PaymentStatus.COMPLETED)

    def fail(self, reason: str = ''):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        self.notes = reason

    def refund(self) -> bool:
        """Refund the payment"""
        if self.status in (PaymentStatus.PROCESSED, PaymentStatus.COMPLETED):
            self.status = PaymentStatus.REFUNDED
            return True
        return False
    
    def get_status(self) -> str:
        """Get payment status"""
        return self.status.value
    
    def __str__(self) -> str:
        return (
            f"Payment {self.reference}\n"
            f"Amount: {self.amount}\n"
            f"Method: {self.method.value}\n"
            f"Date: {self.date.strftime('%Y-%m-%d')}\n"
            f"Status: {self.status.value}"
        )
    
    def to_dict(self) -> dict:
        """Convert payment to dictionary"""
        return {
            'reference': self.reference,
            'amount': str(self.amount),
            'method': self.method.value,
            'date': self.date.isoformat(),
            'status': self.status.value,
            'notes': self.notes,
        }


class PaymentReceiver:
    """Handles payment collection and tracking"""

    def __init__(self, receiver_id: str = None):
        self.receiver_id = receiver_id
        self.payments = []
        self.total_received = Decimal('0')
    
    def receive_payment(
        self,
        amount,
        method: str = 'cash',
        reference: str = None
    ) -> Payment:
        """
        Record a payment received
        
        Args:
            amount: Payment amount
            method: Payment method
            reference: Payment reference
            
        Returns:
            Payment object
        """
        payment = Payment(amount, method, reference)
        payment.process()
        self.payments.append(payment)
        self.total_received = format_amount(
            self.total_received + payment.amount
        )
        return payment
    
    def get_total_received(self) -> Decimal:
        """Get total amount received"""
        return self.total_received
    
    def get_payment_by_reference(self, reference: str) -> Payment:
        """Get payment by reference"""
        for payment in self.payments:
            if payment.reference == reference:
                return payment
        return None
    
    def get_payments_by_method(self, method: str) -> list:
        """Get all payments by method"""
        return [
            p for p in self.payments
            if p.method.value == method.lower()
        ]
