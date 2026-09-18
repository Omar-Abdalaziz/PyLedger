"""
PyLedger Business Module - Default Chart of Accounts
Pre-built chart of accounts for common business types
"""

from pyledger.core.account import Account


SMART_ACCOUNT_TEMPLATES = {
    'asset_current': {
        'prefix': '1',
        'accounts': [
            ('1000', 'Cash', 'Current asset'),
            ('1010', 'Petty Cash', 'Current asset'),
            ('1100', 'Accounts Receivable', 'Current asset'),
            ('1200', 'Inventory', 'Current asset'),
            ('1300', 'Prepaid Expenses', 'Current asset'),
        ]
    },
    'asset_noncurrent': {
        'prefix': '1',
        'accounts': [
            ('1500', 'Equipment', 'Fixed asset'),
            ('1510', 'Machinery', 'Fixed asset'),
            ('1520', 'Vehicles', 'Fixed asset'),
            ('1530', 'Furniture & Fixtures', 'Fixed asset'),
            ('1600', 'Buildings', 'Fixed asset'),
            ('1700', 'Land', 'Fixed asset'),
            ('1800', 'Intangible Assets', 'Intangible asset'),
            ('1900', 'Accumulated Depreciation', 'Contra asset'),
        ]
    },
    'liability_current': {
        'prefix': '2',
        'accounts': [
            ('2000', 'Accounts Payable', 'Current liability'),
            ('2100', 'Accrued Expenses', 'Current liability'),
            ('2200', 'Short-Term Loans', 'Current liability'),
            ('2300', 'Tax Payable', 'Current liability'),
            ('2400', 'VAT Payable', 'Current liability'),
        ]
    },
    'liability_noncurrent': {
        'prefix': '2',
        'accounts': [
            ('2500', 'Long-Term Loans', 'Non-current liability'),
            ('2600', 'Deferred Tax Liability', 'Non-current liability'),
        ]
    },
    'equity': {
        'prefix': '3',
        'accounts': [
            ('3000', 'Owner\'s Capital', 'Equity'),
            ('3100', 'Retained Earnings', 'Equity'),
            ('3200', 'Dividends', 'Equity'),
        ]
    },
    'income': {
        'prefix': '4',
        'accounts': [
            ('4000', 'Sales Revenue', 'Operating income'),
            ('4100', 'Service Revenue', 'Operating income'),
            ('4200', 'Interest Income', 'Other income'),
            ('4300', 'Other Revenue', 'Other income'),
        ]
    },
    'expense': {
        'prefix': '5',
        'accounts': [
            ('5000', 'Cost of Goods Sold', 'COGS'),
            ('5100', 'Salaries & Wages', 'Operating expense'),
            ('5200', 'Rent Expense', 'Operating expense'),
            ('5300', 'Utilities Expense', 'Operating expense'),
            ('5400', 'Office Supplies', 'Operating expense'),
            ('5500', 'Marketing Expense', 'Operating expense'),
            ('5600', 'Travel Expense', 'Operating expense'),
            ('5700', 'Depreciation Expense', 'Operating expense'),
            ('5800', 'Interest Expense', 'Finance cost'),
            ('5900', 'Tax Expense', 'Tax'),
        ]
    },
}


class SmartChartOfAccounts:
    """Generate a pre-built chart of accounts"""

    def __init__(self, country: str = 'US', industry: str = 'general',
                 include_all: bool = True):
        self.country = country
        self.industry = industry
        self.accounts = {}
        if include_all:
            self._build_default()

    def _build_default(self):
        for category, config in SMART_ACCOUNT_TEMPLATES.items():
            for code, name, desc in config['accounts']:
                acc_type = category.split('_')[0]
                if acc_type == 'asset':
                    acc_type = 'asset'
                elif acc_type == 'liability':
                    acc_type = 'liability'
                account = Account(
                    name=name,
                    account_type=acc_type,
                    code=code,
                    description=desc,
                )
                self.accounts[code] = account

    def add_to_ledger(self, ledger, account_codes: list = None):
        """Add accounts to a ledger"""
        codes = account_codes or list(self.accounts.keys())
        for code in codes:
            if code in self.accounts and not ledger.account_exists(code):
                ledger.add_account(self.accounts[code])

    def get_by_type(self, account_type: str) -> list:
        """Get accounts by type"""
        return [a for a in self.accounts.values() if a.type == account_type]
