"""
PyLedger Business Module - Business Engine
High-level abstraction for business operations
"""

from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING

from pyledger.core.ledger import Ledger
from pyledger.core.account import Account
from pyledger.core.journal import JournalEntry
from pyledger.business.defaults import SmartChartOfAccounts
from pyledger.business.operations import (
    record_sale, record_purchase, record_expense, record_payroll,
    buy_asset, record_depreciation, record_investment,
)
from pyledger.reports import (
    IncomeStatement, BalanceSheet, CashFlowStatement,
    EquityStatement, FinancialPeriod,
)
from pyledger.security.sanitizer import (
    sanitize_name, sanitize_description,
)
from pyledger.security.validator import (
    EntryValidator, DuplicateDetector, BusinessRuleError,
    validate_new_account,
)

if TYPE_CHECKING:  # quoted annotations only; runtime imports stay local (no cycles)
    from pyledger.reports.ratios import FinancialRatios
    from pyledger.accounting.tax_reports import VATReturn, CorporateTaxReport
    from pyledger.accounting.crm import Customer, Supplier
    from pyledger.accounting.assets import FixedAsset
    from pyledger.accounting.inventory import InventoryItem
    from pyledger.accounting.budget import Budget
    from pyledger.accounting.bank_reconciliation import BankReconciliation
    from pyledger.accounting.projects import Project
    from pyledger.accounting.deferred import DeferredRevenue, PrepaidExpense


class BusinessEngine:
    """
    High-level business engine for non-accountant developers.
    
    Translates business operations into correct double-entry accounting entries
    without requiring accounting knowledge.
    
    Security: All inputs are automatically sanitized and validated.
    """

    def __init__(self, ledger: Ledger = None, company_name: str = 'My Company',
                 currency: str = 'USD', country: str = 'US',
                 industry: str = 'general', auto_setup: bool = True,
                 company: str = None):
        # 'company' is a convenience alias required by test-suite / facade
        if company is not None:
            company_name = company
        self.ledger = ledger or Ledger(company_name, currency)
        self.company_name = company_name
        # Alias for callers using .company
        self.company = company_name
        self.currency = currency
        self.country = country
        self.industry = industry
        self.entry_validator = EntryValidator(self.ledger)
        self.duplicate_detector = DuplicateDetector()

        if auto_setup:
            self._auto_setup()

    def _auto_setup(self):
        """Auto-setup chart of accounts"""
        chart = SmartChartOfAccounts(country=self.country, industry=self.industry)
        chart.add_to_ledger(self.ledger)

    def add_account(self, name: str, type: str, code: str = None,
                    description: str = '') -> Account:
        """Add a custom account (with security validation)"""
        if code is None:
            code = str(len(self.ledger.accounts) + 1000)
        errors = validate_new_account(name, type, code)
        if errors:
            raise BusinessRuleError('; '.join(errors))
        safe_name = sanitize_name(name)
        safe_desc = sanitize_description(description)
        account = Account(name=safe_name, account_type=type, code=code,
                          currency=self.currency, description=safe_desc)
        return self.ledger.add_account(account)

    def validate_entry(self, entry: JournalEntry) -> list:
        """Deep-validate a journal entry before posting"""
        return self.entry_validator.validate(entry)

    def post_entry(self, entry: JournalEntry) -> bool:
        """Post a journal entry with full security validation.

        Tolerates pre-posted entries (legacy post-then-record pattern):
        they are validated and recorded, never posted twice.
        """
        if self.duplicate_detector.check_entry(entry):
            raise BusinessRuleError("Duplicate entry detected")
        self.entry_validator.validate_and_raise(entry)
        result = True
        if not entry.posted:
            result = entry.post()
        self.duplicate_detector.mark_seen(entry)
        self.ledger.journal_entries.append(entry)
        return result

    def sell(self, items: list, customer: str,
             payment_method: str = 'credit',
             tax_rate: float = 0) -> dict:
        """Record a sale (products or services)"""
        return record_sale(
            self.ledger, items=items, customer=customer,
            payment_method=payment_method,
            tax_rate=Decimal(str(tax_rate)),
        )

    def buy(self, items: list, supplier: str,
            payment_method: str = 'credit',
            tax_rate: float = 0,
            is_inventory: bool = True) -> dict:
        """Record a purchase from a supplier"""
        return record_purchase(
            self.ledger, items=items, supplier=supplier,
            payment_method=payment_method,
            tax_rate=Decimal(str(tax_rate)),
            is_inventory=is_inventory,
        )

    def pay_expense(self, description: str, amount: float,
                    category: str = 'general',
                    payment_method: str = 'cash') -> dict:
        """Record an operating expense"""
        return record_expense(
            self.ledger, description=description,
            amount=Decimal(str(amount)),
            category=category, payment_method=payment_method,
        )

    def pay_salary(self, employee: str, gross_salary: float,
                   deductions: dict = None) -> dict:
        """Record payroll"""
        return record_payroll(
            self.ledger, employee=employee,
            gross_salary=Decimal(str(gross_salary)),
            deductions=deductions or {},
        )

    def buy_fixed_asset(self, name: str, cost: float,
                        useful_life: int = None,
                        down_payment: float = None) -> dict:
        """Record asset purchase"""
        dp = Decimal(str(down_payment)) if down_payment else None
        return buy_asset(
            self.ledger, asset_name=name,
            cost=Decimal(str(cost)),
            useful_life=useful_life,
            down_payment=dp,
        )

    def record_depreciation(self, asset_name: str, amount: float) -> dict:
        """Record depreciation on an asset"""
        return record_depreciation(
            self.ledger, asset_name=asset_name,
            amount=Decimal(str(amount)),
        )

    def add_investment(self, investor: str, amount: float) -> dict:
        """Record capital investment"""
        return record_investment(
            self.ledger, investor=investor,
            amount=Decimal(str(amount)),
        )

    def transfer(self, from_account: str, to_account: str,
                 amount: float, description: str = 'Transfer') -> JournalEntry:
        """Transfer money between accounts"""
        from_acc = self.ledger.get_account(from_account)
        to_acc = self.ledger.get_account(to_account)
        return self.ledger.transfer(from_acc, to_acc, Decimal(str(amount)))

    # --- Reports ---
    def income_statement(self, period: FinancialPeriod = None) -> IncomeStatement:
        """Get income statement"""
        return IncomeStatement(self.ledger, period=period)

    def balance_sheet(self, as_of: datetime = None) -> BalanceSheet:
        """Get balance sheet"""
        return BalanceSheet(self.ledger, as_of_date=as_of)

    def cash_flow(self, period: FinancialPeriod = None,
                  method: str = 'indirect') -> CashFlowStatement:
        """Get cash flow statement (indirect or direct)"""
        return CashFlowStatement(self.ledger, period=period, method=method)

    def equity_statement(self, period: FinancialPeriod = None) -> EquityStatement:
        """Get statement of changes in equity"""
        return EquityStatement(self.ledger, period=period)

    def financial_ratios(self, period: FinancialPeriod = None) -> 'FinancialRatios':
        """Get financial ratios"""
        from pyledger.reports.ratios import FinancialRatios
        return FinancialRatios(self.ledger, period=period)

    def vat_return(self, period: FinancialPeriod,
                   vat_rate: float = 15) -> 'VATReturn':
        """Get VAT return"""
        from pyledger.accounting.tax_reports import VATReturn
        return VATReturn(self.ledger, period,
                         vat_rate=Decimal(str(vat_rate)))

    def corporate_tax(self, period: FinancialPeriod,
                      country: str = None) -> 'CorporateTaxReport':
        """Get corporate tax report"""
        from pyledger.accounting.tax_reports import CorporateTaxReport
        return CorporateTaxReport(self.ledger, period,
                                  country=country or self.country)

    # --- Accounting Operations ---
    def create_customer(self, name: str, customer_id: str = None,
                        credit_limit: float = 0) -> 'Customer':
        from pyledger.accounting.crm import Customer
        return Customer(name, customer_id,
                        credit_limit=Decimal(str(credit_limit)))

    def create_supplier(self, name: str, supplier_id: str = None) -> 'Supplier':
        from pyledger.accounting.crm import Supplier
        return Supplier(name, supplier_id)

    def create_fixed_asset(self, name: str, cost: float, code: str,
                           useful_life: int,
                           method: str = 'straight_line') -> 'FixedAsset':
        from pyledger.accounting.assets import FixedAsset
        return FixedAsset(name, cost, code, useful_life,
                          depreciation_method=method)

    def create_inventory_item(self, sku: str, name: str) -> 'InventoryItem':
        from pyledger.accounting.inventory import InventoryItem
        return InventoryItem(sku, name)

    def create_budget(self, name: str, period: FinancialPeriod) -> 'Budget':
        from pyledger.accounting.budget import Budget
        return Budget(name, period)

    def bank_reconciliation(self, cash_account_code: str,
                            as_of: datetime = None) -> 'BankReconciliation':
        from pyledger.accounting.bank_reconciliation import BankReconciliation
        return BankReconciliation(self.ledger, cash_account_code, as_of)

    def create_project(self, project_id: str, name: str,
                       budget: float = 0) -> 'Project':
        from pyledger.accounting.projects import Project
        return Project(project_id, name, budget=Decimal(str(budget)))

    def create_deferred_revenue(self, description: str, total_amount: float,
                                start_date: datetime, end_date: datetime) -> 'DeferredRevenue':
        from pyledger.accounting.deferred import DeferredRevenue
        return DeferredRevenue(description, Decimal(str(total_amount)),
                               start_date, end_date)

    def create_prepaid_expense(self, description: str, total_amount: float,
                               start_date: datetime, end_date: datetime) -> 'PrepaidExpense':
        from pyledger.accounting.deferred import PrepaidExpense
        return PrepaidExpense(description, Decimal(str(total_amount)),
                              start_date, end_date)

    def export_csv(self, report) -> str:
        """Export any report to CSV string"""
        from pyledger.reports.export import ReportExporter
        return ReportExporter.to_csv(report)

    # --- PDF ---
    def to_pdf(self, filepath: str = 'report.pdf',
               reports: list = None):
        """Generate PDF report(s)"""
        from pyledger.pdf import PDFEngine
        pdf = PDFEngine(self.ledger)
        pdf.set_company(name=self.company_name)
        base_reports = reports or [
            self.income_statement(), self.balance_sheet(),
            self.cash_flow(), self.equity_statement(),
        ]
        for r in base_reports:
            pdf.add_report(r)
        pdf.save(filepath)
