#!/usr/bin/env python
"""
PyLedger Quick Start Example
A complete working example of PyLedger functionality
"""

from pyledger import (
    Ledger, Account, JournalEntry,
    Invoice, Tax,
    IncomeStatement, BalanceSheet,
    CurrencyConverter, Formatter
)
from datetime import datetime, timedelta
import sys

if hasattr(sys.stdout, 'reconfigure'):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def main():
    """Main example function"""
    
    print("=" * 70)
    print("PyLedger - Professional Accounting Library".center(70))
    print("=" * 70)
    print()
    
    # Step 1: Create a Ledger
    print("📊 STEP 1: Creating Ledger...")
    ledger = Ledger(name="Demo Company", currency="EGP")
    print(f"✓ Ledger created: {ledger.name}")
    print()
    
    # Step 2: Create Accounts
    print("📋 STEP 2: Creating Accounts...")
    accounts_data = [
        ("Cash", "asset", "1000-CASH", "Company cash account"),
        ("Bank", "asset", "1010-BANK", "Bank account"),
        ("Equipment", "asset", "1020-EQUIP", "Office equipment"),
        ("Accounts Payable", "liability", "2000-AP", "Outstanding invoices"),
        ("Owner Capital", "equity", "3000-CAPITAL", "Owner equity"),
        ("Sales Revenue", "income", "4000-SALES", "Product and service sales"),
        ("Salaries Expense", "expense", "5000-SALARY", "Employee salaries"),
        ("Rent Expense", "expense", "5010-RENT", "Office rent"),
    ]
    
    for name, acc_type, code, description in accounts_data:
        account = Account(name, acc_type, code, description=description)
        ledger.add_account(account)
        print(f"✓ Created: {name} ({code})")
    
    print()
    
    # Step 3: Record Opening Balance
    print("📝 STEP 3: Recording Opening Balance...")
    opening_entry = JournalEntry("Opening Balance - Company Start")
    opening_entry.add_debit(ledger.get_account("1000-CASH"), 50000, "Initial cash")
    opening_entry.add_debit(ledger.get_account("1020-EQUIP"), 100000, "Initial equipment")
    opening_entry.add_credit(ledger.get_account("3000-CAPITAL"), 150000, "Owner investment")
    opening_entry.post()
    ledger.record_entry(opening_entry)
    print("✓ Opening entry recorded")
    print()
    
    # Step 4: Record Sales Transactions
    print("💰 STEP 4: Recording Sales Transactions...")
    sales_entry = JournalEntry("Sales Transaction - January")
    sales_entry.add_debit(ledger.get_account("1000-CASH"), 25000, "Cash sales")
    sales_entry.add_credit(ledger.get_account("4000-SALES"), 25000, "Revenue recognized")
    sales_entry.post()
    ledger.record_entry(sales_entry)
    print("✓ Sales transaction recorded")
    print()
    
    # Step 5: Record Expenses
    print("📉 STEP 5: Recording Expenses...")
    expense_entry = JournalEntry("Monthly Expenses")
    expense_entry.add_debit(ledger.get_account("5000-SALARY"), 10000, "Monthly salaries")
    expense_entry.add_debit(ledger.get_account("5010-RENT"), 5000, "Monthly rent")
    expense_entry.add_credit(ledger.get_account("1000-CASH"), 15000, "Cash payment")
    expense_entry.post()
    ledger.record_entry(expense_entry)
    print("✓ Expense transactions recorded")
    print()
    
    # Step 6: Create Invoice
    print("📄 STEP 6: Creating Invoice...")
    invoice = Invoice(
        customer="Ahmed Trading Company",
        invoice_number="INV-001",
        currency="EGP"
    )
    
    invoice.add_item("Consulting Services", quantity=10, unit_price=500)
    invoice.add_item("Software License", quantity=1, unit_price=5000)
    invoice.add_item("Support Package", quantity=1, unit_price=2000)
    
    # Add VAT
    vat = Tax("VAT", rate=15)
    invoice.add_tax(vat)
    
    invoice.issue()
    print(f"✓ Invoice {invoice.number} created")
    print(f"  Subtotal: £{invoice.subtotal}")
    print(f"  VAT (15%): £{invoice.tax_total}")
    print(f"  Total: £{invoice.total}")
    
    # Record payments
    invoice.pay(amount=5000, method='bank_transfer')
    invoice.pay(amount=5500, method='check')
    print(f"  Remaining Balance: £{invoice.get_remaining_balance()}")
    print()
    
    # Step 7: Display Trial Balance
    print("📊 STEP 7: Trial Balance")
    print("-" * 70)
    trial_balance = ledger.get_trial_balance()
    
    print(f"{'Account Code':<15} {'Account Name':<25} {'Debit':>12} {'Credit':>12}")
    print("-" * 70)
    
    for acc in trial_balance['accounts']:
        debit = acc['debit']
        credit = acc['credit']
        if acc['type'] == 'asset' or acc['type'] == 'expense':
            debit = acc['debit'] if acc['debit'] != '0' else ''
            credit = ''
        else:
            debit = ''
            credit = acc['credit'] if acc['credit'] != '0' else ''
        
        print(
            f"{acc['code']:<15} "
            f"{acc['name']:<25} "
            f"{debit:>12} "
            f"{credit:>12}"
        )
    
    print("-" * 70)
    print(f"{'TOTALS':<40} {trial_balance['total_debits']:>12} {trial_balance['total_credits']:>12}")
    print(f"Status: {'✓ BALANCED' if trial_balance['balanced'] else '✗ UNBALANCED'}")
    print()
    
    # Step 8: Generate Income Statement
    print("📈 STEP 8: Income Statement")
    print("-" * 70)
    income_stmt = IncomeStatement(ledger)
    print(income_stmt)
    print()
    
    # Step 9: Generate Balance Sheet
    print("📊 STEP 9: Balance Sheet")
    print("-" * 70)
    balance_sheet = BalanceSheet(ledger)
    print(balance_sheet)
    print()
    
    # Step 10: Summary
    print("=" * 70)
    print("FINANCIAL SUMMARY".center(70))
    print("=" * 70)
    
    formatter = Formatter()
    summary_data = [
        ("Total Assets", formatter.format_amount(ledger.get_total_assets(), "£")),
        ("Total Liabilities", formatter.format_amount(ledger.get_total_liabilities(), "£")),
        ("Total Equity", formatter.format_amount(ledger.get_total_equity(), "£")),
        ("Total Income", formatter.format_amount(ledger.get_total_income(), "£")),
        ("Total Expenses", formatter.format_amount(ledger.get_total_expenses(), "£")),
        ("Net Income", formatter.format_amount(
            ledger.get_total_income() - ledger.get_total_expenses(), "£"
        )),
    ]
    
    for label, value in summary_data:
        print(f"{label:<30} {value:>30}")
    
    print()
    print("=" * 70)
    print("PyLedger Example Completed Successfully! ✓".center(70))
    print("=" * 70)


if __name__ == "__main__":
    main()
