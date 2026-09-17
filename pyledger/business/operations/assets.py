"""
PyLedger Business Module - Asset & Investment Operations
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from pyledger.core.journal import JournalEntry
from pyledger.business.validation import BusinessGuard
from pyledger.security.sanitizer import (
    sanitize_description, sanitize_amount, sanitize_text,
)


def buy_asset(ledger, asset_name: str, cost, asset_code: str = '1500',
              payment_method: str = 'cash', down_payment: Decimal = None,
              loan_code: str = '2500', cash_code: str = '1000',
              useful_life: int = None, date: Optional[datetime] = None) -> dict:
    """Record purchase of a fixed asset"""
    BusinessGuard.require_positive_amount(cost)
    date = date or datetime.now()
    cost_decimal = sanitize_amount(cost, allow_negative=False)
    safe_asset = sanitize_text(asset_name)

    entry = JournalEntry(sanitize_description(f"Purchase of {safe_asset}"), date=date)
    entry.add_debit(ledger.get_account(asset_code), cost_decimal,
                    f"Cost of {asset_name}")

    if down_payment:
        dp = sanitize_amount(down_payment, allow_negative=False)
        entry.add_credit(ledger.get_account(cash_code), dp,
                         sanitize_description(f"Down payment - {safe_asset}"))
        remaining = cost_decimal - dp
        if remaining > 0:
            entry.add_credit(ledger.get_account(loan_code), remaining,
                             sanitize_description(f"Loan - {safe_asset}"))
    else:
        if payment_method == 'cash':
            entry.add_credit(ledger.get_account(cash_code), cost_decimal,
                             sanitize_description(f"Paid - {safe_asset}"))
        else:
            entry.add_credit(ledger.get_account('2000'), cost_decimal,
                             sanitize_description(f"Credit - {safe_asset}"))

    entry.post()
    ledger.journal_entries.append(entry)

    result = {
        'entry_number': entry.number,
        'asset': asset_name,
        'cost': cost_decimal,
    }

    if useful_life:
        result['useful_life'] = useful_life
        result['annual_depreciation'] = cost_decimal / Decimal(str(useful_life))

    return result


def record_depreciation(ledger, asset_name: str, amount,
                        asset_code: str = '1500',
                        accum_depr_code: str = '1900',
                        depr_expense_code: str = '5700',
                        date: Optional[datetime] = None) -> dict:
    """Record depreciation expense"""
    BusinessGuard.require_positive_amount(amount)
    date = date or datetime.now()
    amt = sanitize_amount(amount, allow_negative=False)
    safe_asset = sanitize_text(asset_name)

    entry = JournalEntry(sanitize_description(f"Depreciation - {safe_asset}"), date=date)
    entry.add_debit(ledger.get_account(depr_expense_code), amt,
                    sanitize_description(f"Depreciation expense - {safe_asset}"))
    entry.add_credit(ledger.get_account(accum_depr_code), amt,
                     sanitize_description(f"Accumulated depreciation - {safe_asset}"))

    entry.post()
    ledger.journal_entries.append(entry)

    return {
        'entry_number': entry.number,
        'asset': asset_name,
        'depreciation': amt,
    }


def record_investment(ledger, investor: str, amount,
                      equity_code: str = '3000',
                      cash_code: str = '1000',
                      date: Optional[datetime] = None) -> dict:
    """Record capital investment"""
    BusinessGuard.require_positive_amount(amount)
    BusinessGuard.require_valid_customer(investor)
    date = date or datetime.now()
    amt = sanitize_amount(amount, allow_negative=False)
    safe_investor = sanitize_text(investor)

    entry = JournalEntry(sanitize_description(f"Capital investment - {safe_investor}"), date=date)
    entry.add_debit(ledger.get_account(cash_code), amt,
                    sanitize_description(f"Cash from {safe_investor}"))
    entry.add_credit(ledger.get_account(equity_code), amt,
                     sanitize_description(f"Capital - {safe_investor}"))

    entry.post()
    ledger.journal_entries.append(entry)

    return {
        'entry_number': entry.number,
        'investor': investor,
        'amount': amt,
    }
