"""
PyLedger Accounting - Customer & Supplier Management
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pyledger.utils.validators import format_amount


class Customer:
    def __init__(self, name: str, customer_id: str = None,
                 tax_id: str = '', credit_limit: Decimal = Decimal('0'),
                 payment_terms: str = 'net_30',
                 currency: str = 'USD', phone: str = '',
                 email: str = '', address: str = ''):
        self.name = name
        self.customer_id = customer_id or f"CUST-{id(self)}"
        self.tax_id = tax_id
        self.credit_limit = Decimal(str(credit_limit))
        self.payment_terms = payment_terms  # net_30, net_60, due_on_receipt
        self.currency = currency
        self.phone = phone
        self.email = email
        self.address = address
        self.invoices = []
        self.created_date = datetime.now()

    def add_invoice(self, invoice) -> None:
        self.invoices.append(invoice)

    def get_balance(self) -> Decimal:
        return sum(inv.total - inv.paid_amount for inv in self.invoices
                   if inv.status.value not in ('paid', 'cancelled'))

    def get_overdue_amount(self, as_of: datetime = None) -> Decimal:
        as_of = as_of or datetime.now()
        overdue = Decimal('0')
        for inv in self.invoices:
            if inv.due_date and inv.due_date < as_of:
                remaining = inv.total - inv.paid_amount
                if remaining > 0:
                    overdue += remaining
        return overdue

    def get_invoices_by_status(self, status: str) -> list:
        return [inv for inv in self.invoices if inv.status.value == status]

    def to_dict(self) -> dict:
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'tax_id': self.tax_id,
            'credit_limit': str(self.credit_limit),
            'payment_terms': self.payment_terms,
            'currency': self.currency,
            'balance': str(self.get_balance()),
            'overdue': str(self.get_overdue_amount()),
        }


class Supplier:
    def __init__(self, name: str, supplier_id: str = None,
                 tax_id: str = '', payment_terms: str = 'net_30',
                 currency: str = 'USD', phone: str = '',
                 email: str = '', address: str = ''):
        self.name = name
        self.supplier_id = supplier_id or f"SUPP-{id(self)}"
        self.tax_id = tax_id
        self.payment_terms = payment_terms
        self.currency = currency
        self.phone = phone
        self.email = email
        self.address = address
        self.purchases = []
        self.created_date = datetime.now()

    def get_balance(self) -> Decimal:
        from pyledger.accounting.invoice import InvoiceStatus
        total = Decimal('0')
        for inv in self.purchases:
            if inv.status.value not in ('paid', 'cancelled'):
                remaining = inv.total - inv.paid_amount
                total += remaining
        return total

    def to_dict(self) -> dict:
        return {
            'supplier_id': self.supplier_id,
            'name': self.name,
            'tax_id': self.tax_id,
            'payment_terms': self.payment_terms,
            'currency': self.currency,
            'balance': str(self.get_balance()),
        }
