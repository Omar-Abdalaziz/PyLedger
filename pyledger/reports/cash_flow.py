"""
PyLedger Reports Module - Cash Flow Statement
Supports both indirect (default) and direct methods
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger


class CashFlowStatement(BaseReport):
    """Cash Flow Statement with indirect and direct method support"""

    def __init__(self, ledger: Ledger, period: Optional[FinancialPeriod] = None,
                 currency: Optional[str] = None, method: str = 'indirect'):
        super().__init__(ledger, period=period, currency=currency)
        if method not in ('indirect', 'direct'):
            raise ValueError("method must be 'indirect' or 'direct'")
        self.method = method

    def generate(self) -> dict:
        if self.method == 'direct':
            return self._generate_direct()
        return self._generate_indirect()

    def _get_net_income(self) -> Decimal:
        total_income = sum(
            (self._filtered_balance(acc) for acc in self.ledger.get_accounts_by_type('income')),
            Decimal('0')
        )
        total_expenses = sum(
            (self._filtered_balance(acc) for acc in self.ledger.get_accounts_by_type('expense')),
            Decimal('0')
        )
        return total_income - total_expenses

    def _filtered_balance(self, account, as_of_date: datetime = None) -> Decimal:
        if self.period and as_of_date is None:
            return self._balance_up_to(account, self.period.end_date)
        if as_of_date is not None:
            return self._balance_up_to(account, as_of_date)
        return account.get_balance()

    def _balance_up_to(self, account, cutoff: datetime) -> Decimal:
        total = Decimal('0')
        for txn in account.get_transactions():
            txn_time = txn.get('timestamp') if isinstance(txn, dict) else None
            if txn_time and txn_time <= cutoff:
                amount = txn.get('amount') if isinstance(txn, dict) else txn.amount
                ttype = txn.get('type') if isinstance(txn, dict) else txn.type
                total += account.balance_effect(ttype, Decimal(str(amount)))
        return total

    def _accounts_matching(self, keywords: List[str], type_filter: str = None) -> list:
        accounts = self.ledger.get_accounts_by_type(type_filter) if type_filter else self.ledger.accounts
        return [a for a in accounts
                if any(kw in a.code.lower() or kw in a.name.lower() for kw in keywords)]

    def _change_in(self, account) -> Decimal:
        if not self.period:
            return Decimal('0')
        end_balance = self._filtered_balance(account, as_of_date=self.period.end_date)
        start_date = self.period.start_date - timedelta(days=1)
        start_balance = self._filtered_balance(account, as_of_date=start_date)
        return end_balance - start_balance

    def _calc_operating_indirect(self, net_income: Decimal) -> dict:
        labels = ['Net Income']
        items = [str(net_income)]

        depr_accounts = self._accounts_matching(
            ['depreciation', 'amortization', 'depletion'], 'expense')
        for acc in depr_accounts:
            bal = self._filtered_balance(acc)
            if bal != 0:
                labels.append(f"Depreciation/Amortization")
                items.append(str(abs(bal)))

        gain_loss = self._accounts_matching(['gain', 'loss'], 'income')
        for acc in gain_loss:
            bal = self._filtered_balance(acc)
            if bal != 0:
                is_gain = 'gain' in acc.code.lower() or 'gain' in acc.name.lower()
                labels.append(f"{'Loss' if not is_gain else 'Gain'} on {acc.name}")
                items.append(str(bal if not is_gain else -bal))

        ar_accounts = self._accounts_matching(
            ['receivable', 'receivables', 'trade_receivable'], 'asset')
        for acc in ar_accounts:
            bal = self._change_in(acc)
            if bal != 0:
                labels.append(f"Change in {acc.name}")
                items.append(str(-bal))

        inventory_accounts = self._accounts_matching(
            ['inventory', 'stock'], 'asset')
        for acc in inventory_accounts:
            bal = self._change_in(acc)
            if bal != 0:
                labels.append(f"Change in {acc.name}")
                items.append(str(-bal))

        ap_accounts = self._accounts_matching(
            ['payable', 'payables', 'trade_payable', 'creditors'], 'liability')
        for acc in ap_accounts:
            bal = self._change_in(acc)
            if bal != 0:
                labels.append(f"Change in {acc.name}")
                items.append(str(bal))

        other_current = self._accounts_matching(
            ['prepaid', 'accrued', 'deferred', 'unearned'], 'asset') + \
            self._accounts_matching(['prepaid', 'accrued', 'deferred', 'unearned'], 'liability')
        for acc in other_current:
            bal = self._change_in(acc)
            if bal != 0:
                sign = 1 if acc.type == 'liability' else -1
                labels.append(f"Change in {acc.name}")
                items.append(str(bal * sign))

        return {'labels': labels, 'items': items}

    # ── Indirect Method ──────────────────────────────────────────

    def _generate_indirect(self) -> dict:
        net_income = self._get_net_income()
        operating = self._calc_operating_indirect(net_income)
        investing = self._calc_investing()
        financing = self._calc_financing()

        net_cash_operating = sum(Decimal(v) for v in operating['items'])
        net_cash_investing = sum(Decimal(v) for v in investing['items'])
        net_cash_financing = sum(Decimal(v) for v in financing['items'])
        net_change = net_cash_operating + net_cash_investing + net_cash_financing

        return {
            'title': 'Cash Flow Statement',
            'method': 'indirect',
            'operating': {
                'items': operating['items'],
                'labels': operating['labels'],
                'total': str(net_cash_operating),
            },
            'investing': {
                'items': investing['items'],
                'labels': investing['labels'],
                'total': str(net_cash_investing),
            },
            'financing': {
                'items': financing['items'],
                'labels': financing['labels'],
                'total': str(net_cash_financing),
            },
            'net_change': str(net_change),
        }

    # ── Direct Method ────────────────────────────────────────────

    def _generate_direct(self) -> dict:
        labels = []
        items = []

        income_accounts = self.ledger.get_accounts_by_type('income')

        collections = Decimal('0')
        for acc in income_accounts:
            bal = self._filtered_balance(acc)
            if 'sales' in acc.code.lower() or 'revenue' in acc.code.lower() or 'service' in acc.code.lower():
                collections += bal
        labels.append('Cash Collections from Customers')
        items.append(str(collections))

        paid_to_suppliers = Decimal('0')
        paid_to_employees = Decimal('0')
        interest_paid = Decimal('0')
        tax_paid = Decimal('0')
        other_op = Decimal('0')

        expense_accounts = self.ledger.get_accounts_by_type('expense')
        for acc in expense_accounts:
            bal = self._filtered_balance(acc)
            name_lower = (acc.code + ' ' + acc.name).lower()
            if any(kw in name_lower for kw in ['cogs', 'cost_of_goods', 'purchase', 'inventory']):
                paid_to_suppliers += bal
            elif any(kw in name_lower for kw in ['salary', 'wage', 'employee']):
                paid_to_employees += bal
            elif any(kw in name_lower for kw in ['interest']):
                interest_paid += bal
            elif any(kw in name_lower for kw in ['tax']):
                tax_paid += bal
            else:
                other_op += bal

        labels.append('Cash Paid to Suppliers')
        items.append(str(-paid_to_suppliers))
        labels.append('Cash Paid to Employees')
        items.append(str(-paid_to_employees))
        labels.append('Interest Paid')
        items.append(str(-interest_paid))
        labels.append('Tax Paid')
        items.append(str(-tax_paid))

        if other_op != 0:
            labels.append('Other Operating Payments')
            items.append(str(-other_op))

        net_cash_operating = collections - paid_to_suppliers - paid_to_employees - interest_paid - tax_paid - other_op

        operating = {
            'labels': labels,
            'items': items,
            'total': str(net_cash_operating),
        }

        investing = self._calc_investing()
        financing = self._calc_financing()

        net_cash_investing = sum(Decimal(v) for v in investing['items'])
        net_cash_financing = sum(Decimal(v) for v in financing['items'])
        net_change = net_cash_operating + net_cash_investing + net_cash_financing

        return {
            'title': 'Cash Flow Statement',
            'method': 'direct',
            'operating': operating,
            'investing': investing,
            'financing': financing,
            'net_change': str(net_change),
        }

    # ── Shared Sections ──────────────────────────────────────────

    def _calc_investing(self) -> dict:
        labels = []
        items = []
        keywords = ['fixed', 'equipment', 'machinery', 'building', 'land',
                    'intangible', 'goodwill', 'investment', 'property']
        investing_accounts = self._accounts_matching(keywords, 'asset')
        for acc in investing_accounts:
            bal = self._filtered_balance(acc)
            if bal > 0:
                labels.append(f"Purchase of {acc.name}")
                items.append(str(-bal))
            elif bal < 0:
                labels.append(f"Sale of {acc.name}")
                items.append(str(abs(bal)))
        if not labels:
            labels.append("Purchase of Fixed Assets")
            items.append("0")
        return {'labels': labels, 'items': items}

    def _calc_financing(self) -> dict:
        labels = []
        items = []
        loan_kw = ['loan', 'debt', 'borrow', 'note_payable', 'bank_loan']
        loan_accounts = self._accounts_matching(loan_kw, 'liability')
        for acc in loan_accounts:
            bal = self._filtered_balance(acc)
            if bal > 0:
                labels.append(f"Proceeds from {acc.name}")
                items.append(str(bal))
            elif bal < 0:
                labels.append(f"Repayment of {acc.name}")
                items.append(str(bal))

        for acc in self.ledger.get_accounts_by_type('equity'):
            bal = self._filtered_balance(acc)
            name_lower = (acc.code + ' ' + acc.name).lower()
            if 'dividend' in name_lower:
                if bal > 0:
                    labels.append(f"{acc.name}")
                    items.append(str(-bal))
            elif 'capital' in name_lower or 'contributed' in name_lower:
                if bal > 0:
                    labels.append(f"Issuance of {acc.name}")
                    items.append(str(bal))

        if not labels:
            labels.append("Financing Activities")
            items.append("0")
        return {'labels': labels, 'items': items}

    # ── Formatting ───────────────────────────────────────────────

    def _format_text(self) -> str:
        data = self.generate()
        period_label = self.period.label if self.period else "Period"
        lines = []
        lines.extend(self._title_block("CASH FLOW STATEMENT", period_label))
        lines.append(f"{'Method: ' + data['method'].title():^68}")
        lines.append("")

        sections = [
            ('OPERATING ACTIVITIES', 'operating'),
            ('INVESTING ACTIVITIES', 'investing'),
            ('FINANCING ACTIVITIES', 'financing'),
        ]

        for section_title, key in sections:
            lines.append("")
            lines.append(f"{section_title:<40}")
            lines.append("-" * 68)
            section = data[key]
            for i in range(len(section['labels'])):
                lines.append(f"  {section['labels'][i]:<38} {self._format_amount(section['items'][i])}")
            lines.append("-" * 68)
            lines.append(f"  {'Net Cash':<38} {self._format_amount(section['total'])}")

        lines.append("")
        lines.append(self._line())
        lines.append(f"{'NET CHANGE IN CASH':<48} {self._format_amount(data['net_change'])}")
        lines.append(self._line())
        return "\n".join(lines)
