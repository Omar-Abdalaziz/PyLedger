"""
PyLedger Accounting - Bank Reconciliation
"""

from decimal import Decimal
from datetime import datetime
from pyledger.core.ledger import Ledger


class BankTransaction:
    def __init__(self, date: datetime, description: str, amount: Decimal,
                 reference: str = '', bank_stmt_id: str = ''):
        self.date = date
        self.description = description
        self.amount = Decimal(str(amount))
        self.reference = reference
        self.bank_stmt_id = bank_stmt_id

    def to_dict(self) -> dict:
        return {
            'date': self.date.isoformat(),
            'description': self.description,
            'amount': str(self.amount),
            'reference': self.reference,
        }


class BankReconciliation:
    """Reconcile ledger cash account with bank statement"""

    def __init__(self, ledger: Ledger, cash_account_code: str,
                 as_of_date: datetime = None):
        self.ledger = ledger
        self.cash_account_code = cash_account_code
        self.as_of_date = as_of_date or datetime.now()
        self.bank_statement_lines = []
        self._cleared = []

    def add_statement_line(self, date: datetime, description: str,
                           amount: Decimal, reference: str = '') -> 'BankReconciliation':
        self.bank_statement_lines.append(
            BankTransaction(date, description, amount, reference))
        return self

    def get_ledger_balance(self) -> Decimal:
        try:
            acc = self.ledger.get_account(self.cash_account_code)
            return acc.get_balance()
        except Exception:
            return Decimal('0')

    def get_statement_balance(self) -> Decimal:
        return sum(t.amount for t in self.bank_statement_lines)

    def _signed(self, txn: dict) -> Decimal:
        try:
            acc = self.ledger.get_account(self.cash_account_code)
            return acc.balance_effect(txn.get('type', 'deposit'), txn.get('amount', 0))
        except Exception:
            amt = Decimal(str(txn.get('amount', 0)))
            return -amt if txn.get('type') in ('withdrawal', 'credit') else amt

    def get_deposits_in_transit(self) -> list:
        ledger_txns = self._get_cash_transactions()
        deposits = []
        for txn in ledger_txns:
            if self._signed(txn) > 0 and not self._is_cleared(txn):
                deposits.append(txn)
        return deposits

    def get_outstanding_checks(self) -> list:
        ledger_txns = self._get_cash_transactions()
        checks = []
        for txn in ledger_txns:
            if self._signed(txn) < 0 and not self._is_cleared(txn):
                checks.append(txn)
        return checks

    def _get_cash_transactions(self) -> list:
        try:
            acc = self.ledger.get_account(self.cash_account_code)
            return acc.get_transactions()
        except Exception:
            return []

    def _is_cleared(self, txn: dict) -> bool:
        ref = str(txn.get('description', '') or '')
        if not ref:
            return False
        return any(st.reference and (ref in st.reference or st.reference in ref)
                   for st in self._cleared)

    def mark_cleared(self, reference: str) -> 'BankReconciliation':
        self._cleared.append(BankTransaction(datetime.now(), '', Decimal('0'), reference))
        return self

    def reconcile(self) -> dict:
        ledger_bal = self.get_ledger_balance()
        stmt_bal = self.get_statement_balance()

        deposits = self.get_deposits_in_transit()
        outstanding = self.get_outstanding_checks()

        adjusted_ledger_bal = ledger_bal
        adjusted_stmt_bal = stmt_bal

        for d in deposits:
            adjusted_stmt_bal += Decimal(str(d.get('amount', 0)))
        for c in outstanding:
            adjusted_stmt_bal += Decimal(str(c.get('amount', 0)))

        return {
            'as_of_date': self.as_of_date.isoformat(),
            'ledger_balance': str(ledger_bal),
            'statement_balance': str(stmt_bal),
            'deposits_in_transit': len(deposits),
            'outstanding_checks': len(outstanding),
            'adjusted_ledger_balance': str(adjusted_ledger_bal),
            'adjusted_statement_balance': str(adjusted_stmt_bal),
            'difference': str(adjusted_stmt_bal - adjusted_ledger_bal),
            'is_reconciled': adjusted_ledger_bal == adjusted_stmt_bal,
        }

    def generate_report(self) -> str:
        data = self.reconcile()
        lines = ['=' * 60, 'BANK RECONCILIATION'.center(60), '=' * 60]
        lines.append(f"As of: {data['as_of_date'][:10]}")
        lines.append('')
        lines.append(f"Ledger Balance:          {data['ledger_balance']:>15}")
        lines.append(f"Statement Balance:       {data['statement_balance']:>15}")
        lines.append(f"Deposits in Transit:     {data['deposits_in_transit']:>15}")
        lines.append(f"Outstanding Checks:      {data['outstanding_checks']:>15}")
        lines.append('-' * 60)
        lines.append(f"Adjusted Ledger Balance: {data['adjusted_ledger_balance']:>15}")
        lines.append(f"Adjusted Stmt Balance:   {data['adjusted_statement_balance']:>15}")
        lines.append('-' * 60)
        status = 'RECONCILED' if data['is_reconciled'] else 'NOT RECONCILED'
        lines.append(f"{'STATUS: ' + status:^60}")
        lines.append('=' * 60)
        return '\n'.join(lines)
