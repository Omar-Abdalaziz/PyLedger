"""
PyLedger Accounting - Consolidation
Multi-entity consolidation with elimination entries
"""

from decimal import Decimal
from typing import Optional, List, Dict
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger
from pyledger.reports.income_statement import IncomeStatement
from pyledger.reports.balance_sheet import BalanceSheet


class ConsolidationEngine:
    """Combine multiple ledgers with inter-entity elimination"""

    def __init__(self, parent_ledger: Ledger, subsidiaries: List[Ledger] = None):
        self.parent = parent_ledger
        self.subsidiaries = subsidiaries or []
        self.elimination_entries = []

    def add_subsidiary(self, ledger: Ledger) -> 'ConsolidationEngine':
        self.subsidiaries.append(ledger)
        return self

    def add_elimination(self, debit_account: str, credit_account: str,
                        amount: Decimal, description: str = ''):
        self.elimination_entries.append({
            'debit': debit_account,
            'credit': credit_account,
            'amount': str(amount),
            'description': description,
        })
        return self

    def get_consolidated_balance(self, account_code: str) -> Decimal:
        total = Decimal('0')
        if self.parent.account_exists(account_code):
            total += self.parent.get_account(account_code).get_balance()
        for sub in self.subsidiaries:
            if sub.account_exists(account_code):
                total += sub.get_account(account_code).get_balance()
        for elim in self.elimination_entries:
            if elim['debit'] == account_code:
                total -= Decimal(elim['amount'])
            if elim['credit'] == account_code:
                total += Decimal(elim['amount'])
        return total

    def get_consolidated_ledger(self) -> dict:
        all_codes = set()
        for acc in self.parent.accounts.values():
            all_codes.add(acc.code)
        for sub in self.subsidiaries:
            for acc in sub.accounts.values():
                all_codes.add(acc.code)

        balances = {}
        for code in all_codes:
            total = Decimal('0')
            if self.parent.account_exists(code):
                total += self.parent.get_account(code).get_balance()
            for sub in self.subsidiaries:
                if sub.account_exists(code):
                    total += sub.get_account(code).get_balance()
            balances[code] = total

        for elim in self.elimination_entries:
            debit_code = elim['debit']
            credit_code = elim['credit']
            amt = Decimal(elim['amount'])
            balances[debit_code] = balances.get(debit_code, Decimal('0')) - amt
            balances[credit_code] = balances.get(credit_code, Decimal('0')) + amt

        accounts_data = {code: {'balance': str(bal)} for code, bal in balances.items()}

        return {
            'entity_count': 1 + len(self.subsidiaries),
            'accounts': accounts_data,
            'eliminations': self.elimination_entries,
        }

    def generate_consolidated_income(self, period: FinancialPeriod) -> dict:
        stmt = IncomeStatement(self.parent, period=period)
        data = stmt.generate()

        for sub in self.subsidiaries:
            sub_stmt = IncomeStatement(sub, period=period)
            sub_data = sub_stmt.generate()
            for item in sub_data.get('items', []):
                found = False
                for existing in data.get('items', []):
                    if existing['account'] == item['account']:
                        existing['amount'] = str(Decimal(existing['amount']) + Decimal(item['amount']))
                        found = True
                        break
                if not found:
                    data['items'].append(item)

        for elim in self.elimination_entries:
            debit_code = elim['debit']
            credit_code = elim['credit']
            amt = Decimal(elim['amount'])
            for item in data.get('items', []):
                if item['account'] == debit_code:
                    item['amount'] = str(Decimal(item['amount']) - amt)
                if item['account'] == credit_code:
                    item['amount'] = str(Decimal(item['amount']) + amt)

        return data

    def generate_consolidated_balance(self, period: FinancialPeriod) -> dict:
        data = {'title': 'Consolidated Balance Sheet', 'balanced': True}
        totals = {'assets': Decimal('0'), 'liabilities': Decimal('0'), 'equity': Decimal('0')}

        for ledger in [self.parent] + self.subsidiaries:
            bs = BalanceSheet(ledger, as_of_date=period.end_date)
            ld = bs.generate()
            totals['assets'] += Decimal(str(ld['assets']['total']))
            totals['liabilities'] += Decimal(str(ld['liabilities'].get('total', '0')))
            totals['equity'] += Decimal(str(ld['equity']['total']))

        for elim in self.elimination_entries:
            debit_code = elim['debit']
            credit_code = elim['credit']
            amt = Decimal(elim['amount'])
            if debit_code:
                totals['assets'] -= amt
            if credit_code:
                totals['liabilities'] += amt

        total_liab_eq = totals['liabilities'] + totals['equity']
        data['total_assets'] = str(totals['assets'])
        data['total_liabilities'] = str(totals['liabilities'])
        data['total_equity'] = str(totals['equity'])
        data['liabilities_and_equity_total'] = str(total_liab_eq)
        return data


class ConsolidatedReport(BaseReport):
    """Consolidated financial report wrapper"""

    def __init__(self, engine: ConsolidationEngine, period: FinancialPeriod,
                 currency: Optional[str] = None):
        super().__init__(engine.parent, period=period, currency=currency)
        self.engine = engine

    def generate(self) -> dict:
        return {
            'title': 'Consolidated Report',
            'entities': 1 + len(self.engine.subsidiaries),
            'income': self.engine.generate_consolidated_income(self.period),
            'balance': self.engine.generate_consolidated_balance(self.period),
            'eliminations': self.engine.elimination_entries,
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = []
        lines.extend(self._title_block("CONSOLIDATED REPORT",
                                       f"{data['entities']} entities"))
        lines.append("")
        lines.append(f"Income Statement: {data['income'].get('title', '')}")
        lines.append(f"Balance Sheet: {data['balance'].get('title', '')}")
        lines.append("")
        lines.append(f"Elimination Entries: {len(data['eliminations'])}")
        for elim in data['eliminations']:
            lines.append(f"  Dr {elim['debit']}  Cr {elim['credit']}  {elim['amount']}  {elim['description']}")
        lines.append(self._line())
        return "\n".join(lines)
