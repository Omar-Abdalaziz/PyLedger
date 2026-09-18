"""
PyLedger Configuration Module
Library-wide settings with module-level integration
"""

import os
import importlib.util
from decimal import Decimal


def _load_root_config() -> dict:
    # Security: resolve config.py relative to the PROJECT ROOT (package
    # parent), never the process CWD — importing CWD code would execute
    # arbitrary files from wherever the library happens to run.
    try:
        from pathlib import Path
        root_config = Path(__file__).resolve().parent.parent / "config.py"
        if not root_config.is_file():
            return {}
        spec = importlib.util.spec_from_file_location(
            "pyledger_root_config", str(root_config))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return {
                k: v for k, v in vars(mod).items()
                if k.isupper() and not k.startswith('_')
            }
    except Exception:
        pass
    return {}


_defaults = _load_root_config()


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._data = dict(_defaults)
        self._env_prefix = 'PYLEDGER_'

        self._ensure('DEFAULT_CURRENCY', 'USD')
        self._ensure('SUPPORTED_CURRENCIES', ['USD', 'EUR', 'GBP', 'SAR', 'AED', 'EGP', 'JOD', 'KWD'])
        self._ensure('DECIMAL_PLACES', 2)
        self._ensure('DATE_FORMAT', '%Y-%m-%d')
        self._ensure('DATETIME_FORMAT', '%Y-%m-%d %H:%M:%S')
        self._ensure('AUTO_BALANCE', True)
        self._ensure('STRICT_MODE', False)
        self._ensure('DEFAULT_TAX_RATES', {'VAT': 15, 'GST': 10, 'Sales Tax': 8.5})

        inv = self._data.get('INVOICE_CONFIG', {})
        self._data['INVOICE_CONFIG'] = {
            'prefix': inv.get('prefix', 'INV'),
            'next_number': inv.get('next_number', 1000),
            'auto_increment': inv.get('auto_increment', True),
        }

        db = self._data.get('DATABASE', {})
        self._data['DATABASE'] = {
            'engine': db.get('engine', 'sqlite'),
            'path': db.get('path', 'ledger.db'),
        }

        valid = self._data.get('VALIDATION', {})
        self._data['VALIDATION'] = {
            'account_code_pattern': valid.get('account_code_pattern', r'^[A-Z0-9\-]{2,20}$'),
            'min_account_name_length': valid.get('min_account_name_length', 1),
            'max_account_name_length': valid.get('max_account_name_length', 255),
            'min_amount': valid.get('min_amount', 0),
        }

        log = self._data.get('LOGGING', {})
        self._data['LOGGING'] = {
            'level': log.get('level', 'INFO'),
            'file': log.get('file', 'pyledger.log'),
            'format': log.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        }

        self._apply_env_overrides()

    def _ensure(self, key: str, default):
        if key not in self._data:
            self._data[key] = default

    def _apply_env_overrides(self):
        prefix = self._env_prefix
        for key in list(self._data.keys()):
            env_key = prefix + key
            val = os.environ.get(env_key)
            if val is not None:
                existing = self._data[key]
                if isinstance(existing, bool):
                    self._data[key] = val.lower() in ('true', '1', 'yes')
                elif isinstance(existing, int):
                    self._data[key] = int(val)
                elif isinstance(existing, Decimal):
                    self._data[key] = Decimal(val)
                elif isinstance(existing, list):
                    self._data[key] = [x.strip() for x in val.split(',')]
                else:
                    self._data[key] = val

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def __getitem__(self, key: str):
        return self._data[key]

    def __setitem__(self, key: str, value):
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def set(self, key: str, value):
        self._data[key] = value
        return self

    def update(self, data: dict):
        self._data.update(data)

    def as_dict(self) -> dict:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Config({len(self._data)} keys)"


config = Config()
