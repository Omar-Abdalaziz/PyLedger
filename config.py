"""
PyLedger Configuration File
"""

# Database Configuration
DATABASE = {
    'engine': 'sqlite',
    'path': 'ledger.db',
}

# Alternatively, use PostgreSQL
# DATABASE = {
#     'engine': 'postgresql',
#     'host': 'localhost',
#     'port': 5432,
#     'database': 'pyledger',
#     'user': 'user',
#     'password': 'password',
# }

# Or MySQL
# DATABASE = {
#     'engine': 'mysql',
#     'host': 'localhost',
#     'port': 3306,
#     'database': 'pyledger',
#     'user': 'user',
#     'password': 'password',
# }

# Default Currency
DEFAULT_CURRENCY = 'USD'

# Supported Currencies
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'SAR', 'AED', 'EGP', 'JOD', 'KWD']

# Default Tax Rates
DEFAULT_TAX_RATES = {
    'VAT': 15,
    'GST': 10,
    'Sales Tax': 8.5,
}

# Account Types
ACCOUNT_TYPES = {
    'asset': 'Debit',
    'liability': 'Credit',
    'equity': 'Credit',
    'income': 'Credit',
    'expense': 'Debit',
}

# Date Format
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Number Format
DECIMAL_PLACES = 2

# Invoice Configuration
INVOICE_CONFIG = {
    'prefix': 'INV',
    'next_number': 1000,
    'auto_increment': True,
}

# Logging
LOGGING = {
    'level': 'INFO',
    'file': 'pyledger.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# Validation Rules
VALIDATION = {
    'account_code_pattern': r'^[A-Z0-9\-]{2,20}$',
    'min_account_name_length': 1,
    'max_account_name_length': 255,
    'min_amount': 0,
}
