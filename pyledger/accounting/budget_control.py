"""
PyLedger Accounting - Budget Control
Prevent posting entries that exceed budget limits
"""

from decimal import Decimal
from pyledger.accounting.budget import Budget
from pyledger.core.journal import JournalEntry
from pyledger.core.ledger import Ledger


class BudgetControl:
    """Enforce budget limits on journal entries"""

    def __init__(self, budget: Budget, ledger: Ledger,
                 tolerance_pct: Decimal = Decimal('10')):
        self.budget = budget
        self.ledger = ledger
        self.tolerance_pct = Decimal(str(tolerance_pct))
        self.violations = []
        self.enabled = True

    def enable(self) -> 'BudgetControl':
        self.enabled = True
        return self

    def disable(self) -> 'BudgetControl':
        self.enabled = False
        return self

    def check_entry(self, entry: JournalEntry) -> bool:
        if not self.enabled:
            return True

        all_ok = True
        for txn in entry.debits + entry.credits:
            code = txn.account.code
            amount = txn.amount
            budgeted = self.budget.get_amount(code)

            if budgeted > 0:
                actual_so_far = self._get_spent_so_far(code)
                tolerance = budgeted * self.tolerance_pct / Decimal('100')
                remaining = budgeted - actual_so_far

                if amount > remaining + tolerance:
                    self.violations.append({
                        'account_code': code,
                        'entry_number': entry.number,
                        'amount': str(amount),
                        'budgeted': str(budgeted),
                        'spent_so_far': str(actual_so_far),
                        'remaining': str(remaining),
                        'excess': str(amount - remaining),
                    })
                    all_ok = False
        return all_ok

    def _get_spent_so_far(self, account_code: str) -> Decimal:
        if not self.ledger.account_exists(account_code):
            return Decimal('0')
        return self.ledger.get_account(account_code).get_balance()

    def check_and_raise(self, entry: JournalEntry):
        if not self.check_entry(entry):
            v = self.violations[-1]
            raise BudgetExceededError(
                f"Budget exceeded for account {v['account_code']}: "
                f"attempted {v['amount']}, remaining {v['remaining']}"
            )

    def get_violations(self) -> list:
        return list(self.violations)

    def clear_violations(self) -> 'BudgetControl':
        self.violations = []
        return self


class BudgetExceededError(Exception):
    pass
