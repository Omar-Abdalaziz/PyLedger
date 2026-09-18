"""
PyLedger Business Module - Purchase Operations
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pyledger.core.journal import JournalEntry
from pyledger.business.validation import BusinessGuard
from pyledger.security.sanitizer import (
    sanitize_description, sanitize_amount, sanitize_quantity, sanitize_text,
    normalize_tax_rate,
)


def record_purchase(ledger, items: list, supplier: str,
                    payment_method: str = 'credit',
                    tax_rate: Decimal = Decimal('0'),
                    date: Optional[datetime] = None,
                    cash_code: str = '1000',
                    payable_code: str = '2000',
                    inventory_code: str = '1200',
                    expense_code: str = '5000',
                    vat_receivable_code: str = '1300',
                    is_inventory: bool = True) -> dict:
    """Record a purchase from supplier (tax_rate is PERCENT, e.g. 15 for 15%)"""
    BusinessGuard.require_non_empty_items(items, 'purchase items')
    BusinessGuard.require_valid_customer(supplier)

    date = date or datetime.now()
    subtotal = Decimal('0')
    for item in items:
        qty = sanitize_quantity(item.get('qty', item.get('quantity', 0)))
        price = sanitize_amount(
            item.get('unit_price', item.get('price', 0)),
            allow_negative=False,
        )
        subtotal += qty * price
    if tax_rate:
        total_tax = (subtotal * normalize_tax_rate(tax_rate)).quantize(Decimal('0.01'))
    else:
        total_tax = Decimal('0')
    grand_total = subtotal + total_tax

    safe_supplier = sanitize_text(supplier)
    entry = JournalEntry(sanitize_description(f"Purchase from {safe_supplier}"), date=date)

    target_code = inventory_code if is_inventory else expense_code
    entry.add_debit(ledger.get_account(target_code), subtotal,
                    f"Purchase - {supplier}")

    if total_tax > 0:
        entry.add_debit(ledger.get_account(vat_receivable_code), total_tax,
                        f"Input VAT - {supplier}")

    if payment_method == 'cash':
        entry.add_credit(ledger.get_account(cash_code), grand_total,
                         f"Cash payment - {supplier}")
    else:
        entry.add_credit(ledger.get_account(payable_code), grand_total,
                         f"Credit purchase - {supplier}")

    entry.post()
    ledger.journal_entries.append(entry)

    return {
        'entry_number': entry.number,
        'supplier': supplier,
        'subtotal': subtotal,
        'tax': total_tax,
        'total': grand_total,
    }


def record_expense(ledger, description: str, amount,
                   category: str = 'general',
                   payment_method: str = 'cash',
                   tax_rate: Decimal = Decimal('0'),
                   date: Optional[datetime] = None,
                   cash_code: str = '1000',
                   payable_code: str = '2000',
                   vat_receivable_code: str = '1300') -> dict:
    """Record an operating expense (tax_rate is PERCENT, e.g. 15 for 15%)"""
    BusinessGuard.require_positive_amount(amount)

    expense_account_map = {
        'rent': '5200',
        'salary': '5100',
        'utilities': '5300',
        'office': '5400',
        'marketing': '5500',
        'travel': '5600',
        'general': '5100',
    }

    expense_code = expense_account_map.get(category, '5100')
    date = date or datetime.now()
    amt = sanitize_amount(amount, allow_negative=False)
    if tax_rate:
        total_tax = (amt * normalize_tax_rate(tax_rate)).quantize(Decimal('0.01'))
    else:
        total_tax = Decimal('0')
    grand_total = amt + total_tax

    entry = JournalEntry(sanitize_description(description), date=date)
    entry.add_debit(ledger.get_account(expense_code), amt, description)

    if total_tax > 0:
        entry.add_debit(ledger.get_account(vat_receivable_code), total_tax,
                        f"Input VAT - {description}")

    if payment_method == 'cash':
        entry.add_credit(ledger.get_account(cash_code), grand_total,
                         f"Paid - {description}")
    else:
        entry.add_credit(ledger.get_account(payable_code), grand_total,
                         f"Accrued - {description}")

    entry.post()
    ledger.journal_entries.append(entry)
    return {'entry_number': entry.number, 'amount': amt, 'description': description}


def record_payroll(ledger, employee: str, gross_salary,
                   deductions: dict = None,
                   employer_contributions: dict = None,
                   date: Optional[datetime] = None,
                   salary_code: str = '5100',
                   cash_code: str = '1000',
                   payable_code: str = '2100') -> dict:
    """Record payroll for an employee"""
    BusinessGuard.require_positive_amount(gross_salary)
    date = date or datetime.now()
    gross = sanitize_amount(gross_salary, allow_negative=False)
    deductions = deductions or {}
    employer_contrib = employer_contributions or {}

    total_deductions = sum(sanitize_amount(v, allow_negative=False) for v in deductions.values())
    net_pay = gross - total_deductions
    total_employer_cost = sum(sanitize_amount(v, allow_negative=False) for v in employer_contrib.values())

    safe_employee = sanitize_text(employee)
    entry = JournalEntry(sanitize_description(f"Payroll - {safe_employee}"), date=date)
    entry.add_debit(ledger.get_account(salary_code), gross + total_employer_cost,
                    f"Gross salary + employer cost - {employee}")

    for deduction_name, deduction_amt in deductions.items():
        ded_amt = Decimal(str(deduction_amt))
        for code, name in [('2100', 'Salary Payable'), ('2400', 'Tax Payable')]:
            if deduction_name.lower() in name.lower():
                entry.add_credit(ledger.get_account(code), ded_amt,
                                 f"{deduction_name} - {employee}")
                break
        else:
            entry.add_credit(ledger.get_account(payable_code), ded_amt,
                             f"{deduction_name} - {employee}")

    entry.add_credit(ledger.get_account(cash_code), net_pay,
                     f"Net pay - {employee}")

    entry.post()
    ledger.journal_entries.append(entry)

    return {
        'entry_number': entry.number,
        'employee': employee,
        'gross': gross,
        'deductions': total_deductions,
        'net_pay': net_pay,
        'employer_cost': total_employer_cost,
    }
