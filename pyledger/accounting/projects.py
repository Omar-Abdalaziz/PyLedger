"""
PyLedger Accounting - Project / Departmental Accounting
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger
from pyledger.core.journal import JournalEntry


class Project:
    def __init__(self, project_id: str, name: str, manager: str = '',
                 budget: Decimal = Decimal('0'),
                 start_date: datetime = None, end_date: datetime = None):
        self.project_id = project_id
        self.name = name
        self.manager = manager
        self.budget = Decimal(str(budget))
        self.start_date = start_date or datetime.now()
        self.end_date = end_date
        self.transactions = []
        self.status = 'active'  # active | completed | on_hold

    def add_transaction(self, description: str, amount: Decimal,
                        account_code: str, txn_type: str = 'expense',
                        date: datetime = None) -> dict:
        txn = {
            'date': (date or datetime.now()).isoformat(),
            'description': description,
            'amount': str(amount),
            'account_code': account_code,
            'type': txn_type,
        }
        self.transactions.append(txn)
        return txn

    def get_total_cost(self) -> Decimal:
        return sum(Decimal(t['amount']) for t in self.transactions)

    def get_remaining_budget(self) -> Decimal:
        return self.budget - self.get_total_cost()

    def get_budget_utilization(self) -> float:
        if self.budget == 0:
            return 0.0
        return float(self.get_total_cost() / self.budget * 100)

    def is_over_budget(self) -> bool:
        return self.get_total_cost() > self.budget

    def to_dict(self) -> dict:
        return {
            'project_id': self.project_id,
            'name': self.name,
            'manager': self.manager,
            'budget': str(self.budget),
            'total_cost': str(self.get_total_cost()),
            'remaining': str(self.get_remaining_budget()),
            'utilization_pct': round(self.get_budget_utilization(), 2),
            'status': self.status,
            'transactions': self.transactions,
        }


class ProjectManager:
    def __init__(self):
        self.projects = {}

    def add_project(self, project: Project) -> 'ProjectManager':
        self.projects[project.project_id] = project
        return self

    def get_project(self, project_id: str) -> Optional[Project]:
        return self.projects.get(project_id)

    def get_all(self) -> List[Project]:
        return list(self.projects.values())

    def get_by_status(self, status: str) -> List[Project]:
        return [p for p in self.projects.values() if p.status == status]

    def get_over_budget(self) -> List[Project]:
        return [p for p in self.projects.values() if p.is_over_budget()]

    def to_dict(self) -> list:
        return [p.to_dict() for p in self.projects.values()]


class ProjectProfitability(BaseReport):
    """Project profitability report"""

    def __init__(self, ledger: Ledger, project_manager: ProjectManager,
                 period: Optional[FinancialPeriod] = None,
                 currency: Optional[str] = None):
        super().__init__(ledger, period=period, currency=currency)
        self.pm = project_manager

    def generate(self) -> dict:
        projects_data = []
        total_revenue = Decimal('0')
        total_cost = Decimal('0')

        for proj in self.pm.get_all():
            revenue = Decimal('0')
            cost = Decimal('0')
            for txn in proj.transactions:
                amount = Decimal(txn['amount'])
                if txn['type'] == 'income':
                    revenue += amount
                else:
                    cost += amount
            total_revenue += revenue
            total_cost += cost
            profit = revenue - cost
            margin = (profit / revenue * 100).quantize(Decimal('0.01')) if revenue != 0 else Decimal('0')

            projects_data.append({
                'project_id': proj.project_id,
                'name': proj.name,
                'revenue': str(revenue),
                'cost': str(cost),
                'profit': str(profit),
                'margin_pct': str(margin),
                'status': proj.status,
            })

        total_profit = total_revenue - total_cost
        overall_margin = (total_profit / total_revenue * 100).quantize(Decimal('0.01')) if total_revenue != 0 else Decimal('0')

        return {
            'title': 'Project Profitability Report',
            'projects': projects_data,
            'total_revenue': str(total_revenue),
            'total_cost': str(total_cost),
            'total_profit': str(total_profit),
            'overall_margin_pct': str(overall_margin),
        }

    def _format_text(self) -> str:
        data = self.generate()
        lines = ['=' * 80, 'PROJECT PROFITABILITY'.center(80), '=' * 80, '']
        header = f"{'Project':<25} {'Revenue':>12} {'Cost':>12} {'Profit':>12} {'Margin':>8} {'Status':>10}"
        lines.append(header)
        lines.append('-' * 80)
        for p in data['projects']:
            lines.append(f"{p['name']:<25} {self._format_amount(p['revenue'])} {self._format_amount(p['cost'])} {self._format_amount(p['profit'])} {p['margin_pct']:>8} {p['status']:>10}")
        lines.append('-' * 80)
        lines.append(f"{'TOTAL':<25} {self._format_amount(data['total_revenue'])} {self._format_amount(data['total_cost'])} {self._format_amount(data['total_profit'])} {data['overall_margin_pct']:>8}")
        return '\n'.join(lines)
