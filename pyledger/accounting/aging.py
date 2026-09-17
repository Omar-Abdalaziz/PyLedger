"""
PyLedger Accounting - Aging Reports
Accounts Receivable & Accounts Payable Aging
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger
from pyledger.accounting.crm import Customer, Supplier


class ReceivableAging(BaseReport):
    """Accounts Receivable Aging Report"""

    BRACKETS = [
        (0, 30, '0-30 Days'),
        (31, 60, '31-60 Days'),
        (61, 90, '61-90 Days'),
        (91, None, '90+ Days'),
    ]

    def __init__(self, ledger: Ledger, customers: List[Customer],
                 as_of_date: Optional[datetime] = None,
                 currency: Optional[str] = None):
        super().__init__(ledger, as_of_date=as_of_date, currency=currency)
        self.customers = customers

    def generate(self) -> dict:
        as_of = self.as_of_date
        total_by_bracket = {b[2]: Decimal('0') for b in self.BRACKETS}
        customer_details = []

        grand_total = Decimal('0')

        for cust in self.customers:
            balance = cust.get_balance()
            if balance == 0:
                continue
            bracket_totals = {b[2]: Decimal('0') for b in self.BRACKETS}
            customer_total = Decimal('0')

            for inv in cust.invoices:
                remaining = inv.total - inv.paid_amount
                if remaining <= 0:
                    continue
                due = inv.due_date
                if not due:
                    bracket_totals['0-30 Days'] += remaining
                    continue
                days_overdue = (as_of - due).days
                if days_overdue <= 0:
                    bracket_totals['0-30 Days'] += remaining
                elif days_overdue <= 30:
                    bracket_totals['0-30 Days'] += remaining
                elif days_overdue <= 60:
                    bracket_totals['31-60 Days'] += remaining
                elif days_overdue <= 90:
                    bracket_totals['61-90 Days'] += remaining
                else:
                    bracket_totals['90+ Days'] += remaining
                customer_total += remaining

            if customer_total > 0:
                customer_details.append({
                    'customer_id': cust.customer_id,
                    'name': cust.name,
                    'total': str(customer_total),
                    'brackets': {k: str(v) for k, v in bracket_totals.items()},
                })

                for bracket, amount in bracket_totals.items():
                    total_by_bracket[bracket] += amount
                grand_total += customer_total

        return {
            'title': 'Accounts Receivable Aging',
            'as_of_date': as_of.isoformat(),
            'customers': customer_details,
            'brackets': {k: str(v) for k, v in total_by_bracket.items()},
            'grand_total': str(grand_total),
            'total_customers': len(customer_details),
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("ACCOUNTS RECEIVABLE AGING",
                                       f"As of {data['as_of_date'][:10]}"))
        lines.append("")
        header = f"{'Customer':<30} {'Total':>12}"
        for b in self.BRACKETS:
            header += f" {b[2]:>12}"
        lines.append(header)
        lines.append("=" * 90)
        for c in data['customers']:
            row = f"{c['name']:<30} {self._format_amount(c['total'])}"
            for b in self.BRACKETS:
                row += f" {self._format_amount(c['brackets'][b[2]])}"
            lines.append(row)
        lines.append("=" * 90)
        total_row = f"{'TOTAL':<30} {self._format_amount(data['grand_total'])}"
        for b in self.BRACKETS:
            total_row += f" {self._format_amount(data['brackets'][b[2]])}"
        lines.append(total_row)
        lines.append(self._line())
        lines.append(f"Total Customers with Balance: {data['total_customers']}")
        lines.append(self._line())
        return "\n".join(lines)


class PayableAging(BaseReport):
    """Accounts Payable Aging Report"""

    BRACKETS = ReceivableAging.BRACKETS

    def __init__(self, ledger: Ledger, suppliers: List[Supplier],
                 as_of_date: Optional[datetime] = None,
                 currency: Optional[str] = None):
        super().__init__(ledger, as_of_date=as_of_date, currency=currency)
        self.suppliers = suppliers

    def generate(self) -> dict:
        as_of = self.as_of_date
        total_by_bracket = {b[2]: Decimal('0') for b in self.BRACKETS}
        supplier_details = []
        grand_total = Decimal('0')

        for supp in self.suppliers:
            balance = supp.get_balance()
            if balance == 0:
                continue
            bracket_totals = {b[2]: Decimal('0') for b in self.BRACKETS}
            supplier_total = Decimal('0')

            for inv in supp.purchases:
                remaining = inv.total - inv.paid_amount
                if remaining <= 0:
                    continue
                due = inv.due_date
                if not due:
                    bracket_totals['0-30 Days'] += remaining
                    continue
                days_overdue = (as_of - due).days
                if days_overdue <= 0:
                    bracket_totals['0-30 Days'] += remaining
                elif days_overdue <= 30:
                    bracket_totals['0-30 Days'] += remaining
                elif days_overdue <= 60:
                    bracket_totals['31-60 Days'] += remaining
                elif days_overdue <= 90:
                    bracket_totals['61-90 Days'] += remaining
                else:
                    bracket_totals['90+ Days'] += remaining
                supplier_total += remaining

            if supplier_total > 0:
                supplier_details.append({
                    'supplier_id': supp.supplier_id,
                    'name': supp.name,
                    'total': str(supplier_total),
                    'brackets': {k: str(v) for k, v in bracket_totals.items()},
                })
                for bracket, amount in bracket_totals.items():
                    total_by_bracket[bracket] += amount
                grand_total += supplier_total

        return {
            'title': 'Accounts Payable Aging',
            'as_of_date': as_of.isoformat(),
            'suppliers': supplier_details,
            'brackets': {k: str(v) for k, v in total_by_bracket.items()},
            'grand_total': str(grand_total),
            'total_suppliers': len(supplier_details),
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("ACCOUNTS PAYABLE AGING",
                                       f"As of {data['as_of_date'][:10]}"))
        lines.append("")
        header = f"{'Supplier':<30} {'Total':>12}"
        for b in self.BRACKETS:
            header += f" {b[2]:>12}"
        lines.append(header)
        lines.append("=" * 90)
        for c in data['suppliers']:
            row = f"{c['name']:<30} {self._format_amount(c['total'])}"
            for b in self.BRACKETS:
                row += f" {self._format_amount(c['brackets'][b[2]])}"
            lines.append(row)
        lines.append("=" * 90)
        total_row = f"{'TOTAL':<30} {self._format_amount(data['grand_total'])}"
        for b in self.BRACKETS:
            total_row += f" {self._format_amount(data['brackets'][b[2]])}"
        lines.append(total_row)
        lines.append(self._line())
        lines.append(f"Total Suppliers with Balance: {data['total_suppliers']}")
        lines.append(self._line())
        return "\n".join(lines)
