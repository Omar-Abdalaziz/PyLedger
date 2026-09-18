"""
PyLedger Business Module - Sales Operations
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Optional
from pyledger.core.journal import JournalEntry
from pyledger.business.validation import BusinessGuard
from pyledger.security.sanitizer import (
    sanitize_description, sanitize_amount, sanitize_quantity, sanitize_text,
    normalize_tax_rate,
)


def record_sale(ledger, items: list, customer: str,
                payment_method: str = 'credit',
                tax_rate: Decimal = Decimal('0'),
                date: Optional[datetime] = None,
                cash_account_code: str = '1000',
                receivable_code: str = '1100',
                revenue_code: str = '4000',
                vat_payable_code: str = '2400',
                inventory_code: str = '1200',
                cogs_code: str = '5000',
                track_inventory: bool = False) -> dict:
    """
    Record a sale to a customer.
    
    Args:
        items: List of dict with keys: [name, qty, unit_price, (optional) cost]
        customer: Customer name
        payment_method: 'cash', 'credit', or 'mixed'
        tax_rate: VAT/GST rate as PERCENT (e.g. 15 for 15%)

    Returns:
        Dict with invoice info and journal entry
    """
    BusinessGuard.require_non_empty_items(items, 'sale items')
    BusinessGuard.require_valid_customer(customer)

    date = date or datetime.now()
    subtotal = Decimal('0')
    total_tax = Decimal('0')

    item_lines = []
    for item in items:
        qty = sanitize_quantity(item.get('qty', item.get('quantity', 0)))
        price = sanitize_amount(
            item.get('unit_price', item.get('price', 0)),
            allow_negative=False,
        )
        name = sanitize_text(item.get('name', ''))
        line_total = qty * price
        subtotal += line_total
        item_lines.append({
            'description': name,
            'qty': qty,
            'unit_price': price,
            'total': line_total,
        })

    if tax_rate:
        fraction = normalize_tax_rate(tax_rate)
        total_tax = (subtotal * fraction).quantize(Decimal('0.01'),
                                                     rounding=ROUND_HALF_UP)

    grand_total = subtotal + total_tax
    description = sanitize_description(f"Sale to {customer}")

    safe_customer = sanitize_text(customer)
    entry = JournalEntry(description, date=date)
    entry.add_credit(
        ledger.get_account(revenue_code), subtotal,
        sanitize_description(f"Revenue - {safe_customer}")
    )

    if payment_method == 'cash':
        entry.add_debit(
            ledger.get_account(cash_account_code), grand_total,
            sanitize_description(f"Cash sale - {safe_customer}")
        )
    else:
        entry.add_debit(
            ledger.get_account(receivable_code), grand_total,
            sanitize_description(f"Credit sale - {safe_customer}")
        )

    if total_tax > 0:
        entry.add_credit(
            ledger.get_account(vat_payable_code), total_tax,
            sanitize_description(f"VAT on sale - {safe_customer}")
        )

    entry.post()
    ledger.journal_entries.append(entry)

    # Inventory tracking
    if track_inventory:
        total_cost = Decimal('0')
        for item in items:
            if 'cost' in item:
                cost = sanitize_amount(item['cost'], allow_negative=False) * sanitize_quantity(item.get('qty', item.get('quantity', 1)))
                total_cost += cost
        if total_cost > 0:
            inv_entry = JournalEntry(sanitize_description(f"COGS - Sale to {safe_customer}"), date=date)
            inv_entry.add_debit(ledger.get_account(cogs_code), total_cost)
            inv_entry.add_credit(ledger.get_account(inventory_code), total_cost)
            inv_entry.post()
            ledger.journal_entries.append(inv_entry)

    return {
        'entry_number': entry.number,
        'customer': customer,
        'subtotal': subtotal,
        'tax': total_tax,
        'total': grand_total,
        'items': item_lines,
    }
