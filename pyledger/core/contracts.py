"""
PyLedger Core - Contracts
Contract management for vendors and customers
"""

from decimal import Decimal
from datetime import datetime
from enum import Enum


class ContractStatus(Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    TERMINATED = 'terminated'
    CANCELLED = 'cancelled'


class ContractType(Enum):
    SALES = 'sales'
    PURCHASE = 'purchase'
    SERVICE = 'service'
    LEASE = 'lease'
    OTHER = 'other'


class Contract:
    def __init__(self, title: str, contract_type: ContractType,
                 party_name: str, start_date: datetime, end_date: datetime,
                 value: Decimal = Decimal('0'),
                 contract_id: str = None):
        self.contract_id = contract_id or f"CTR-{id(self)}"
        self.title = title
        self.contract_type = contract_type
        self.party_name = party_name
        self.start_date = start_date
        self.end_date = end_date
        self.value = Decimal(str(value))
        self.status = ContractStatus.DRAFT
        self.terms = ''
        self.notes = ''
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def activate(self) -> 'Contract':
        self.status = ContractStatus.ACTIVE
        self.updated_at = datetime.now()
        return self

    def complete(self) -> 'Contract':
        self.status = ContractStatus.COMPLETED
        self.updated_at = datetime.now()
        return self

    def terminate(self) -> 'Contract':
        self.status = ContractStatus.TERMINATED
        self.updated_at = datetime.now()
        return self

    def cancel(self) -> 'Contract':
        self.status = ContractStatus.CANCELLED
        self.updated_at = datetime.now()
        return self

    def is_active(self) -> bool:
        now = datetime.now()
        return (self.status == ContractStatus.ACTIVE and
                self.start_date <= now <= self.end_date)

    def days_remaining(self) -> int:
        if not self.is_active():
            return 0
        delta = self.end_date - datetime.now()
        return max(0, delta.days)

    def to_dict(self) -> dict:
        return {
            'contract_id': self.contract_id,
            'title': self.title,
            'type': self.contract_type.value,
            'party': self.party_name,
            'value': str(self.value),
            'status': self.status.value,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'terms': self.terms,
            'notes': self.notes,
        }


class ContractManager:
    def __init__(self):
        self.contracts = []

    def add(self, contract: Contract) -> 'ContractManager':
        self.contracts.append(contract)
        return self

    def get_active(self) -> list:
        return [c for c in self.contracts if c.is_active()]

    def get_by_status(self, status: ContractStatus) -> list:
        return [c for c in self.contracts if c.status == status]

    def get_by_party(self, party: str) -> list:
        return [c for c in self.contracts if c.party_name == party]

    def get_total_value(self, status: ContractStatus = None) -> Decimal:
        filtered = self.contracts if status is None else self.get_by_status(status)
        return sum(c.value for c in filtered)

    def get_expiring_soon(self, days: int = 30) -> list:
        return [c for c in self.contracts
                if c.is_active() and c.days_remaining() <= days]

    def to_dict(self) -> list:
        return [c.to_dict() for c in self.contracts]
