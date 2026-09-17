"""
PyLedger Core - Workflow
Approval workflows for journal entries
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class EntryStatus(Enum):
    DRAFT = 'draft'
    PENDING_APPROVAL = 'pending_approval'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    POSTED = 'posted'


class WorkflowStep:
    def __init__(self, name: str, required_approvers: int = 1):
        self.name = name
        self.required_approvers = required_approvers
        self.approvals = []
        self.completed = False

    def approve(self, approver: str, comment: str = '') -> bool:
        if self.completed:
            return False
        self.approvals.append({
            'approver': approver,
            'comment': comment,
            'timestamp': datetime.now().isoformat(),
        })
        if len(self.approvals) >= self.required_approvers:
            self.completed = True
        return self.completed

    def reject(self, approver: str, reason: str = '') -> bool:
        self.approvals.append({
            'approver': approver,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'rejected': True,
        })
        self.completed = True
        return True


class WorkflowEntry:
    def __init__(self, description: str, created_by: str,
                 amount: Decimal = Decimal('0')):
        self.description = description
        self.created_by = created_by
        self.amount = Decimal(str(amount))
        self.status = EntryStatus.DRAFT
        self.steps = []
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.notes = ''

    def add_step(self, name: str, required_approvers: int = 1) -> 'WorkflowEntry':
        self.steps.append(WorkflowStep(name, required_approvers))
        return self

    def submit(self) -> 'WorkflowEntry':
        if self.status != EntryStatus.DRAFT:
            raise ValueError("Only draft entries can be submitted")
        self.status = EntryStatus.PENDING_APPROVAL
        self.updated_at = datetime.now()
        return self

    def approve(self, step_index: int, approver: str,
                comment: str = '') -> bool:
        if self.status != EntryStatus.PENDING_APPROVAL:
            return False
        if step_index >= len(self.steps):
            return False
        step = self.steps[step_index]
        completed = step.approve(approver, comment)
        if completed and step_index == len(self.steps) - 1:
            self.status = EntryStatus.APPROVED
        self.updated_at = datetime.now()
        return completed

    def reject(self, step_index: int, approver: str,
               reason: str = '') -> bool:
        if self.status != EntryStatus.PENDING_APPROVAL:
            return False
        if step_index >= len(self.steps):
            return False
        step = self.steps[step_index]
        step.reject(approver, reason)
        self.status = EntryStatus.REJECTED
        self.updated_at = datetime.now()
        return True

    def post(self) -> bool:
        if self.status != EntryStatus.APPROVED:
            return False
        self.status = EntryStatus.POSTED
        self.updated_at = datetime.now()
        return True

    def to_dict(self) -> dict:
        return {
            'description': self.description,
            'created_by': self.created_by,
            'amount': str(self.amount),
            'status': self.status.value,
            'steps': [{
                'name': s.name,
                'required_approvers': s.required_approvers,
                'approvals': s.approvals,
                'completed': s.completed,
            } for s in self.steps],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class WorkflowEngine:
    """Manage approval workflows"""

    def __init__(self):
        self.entries = []

    def create_entry(self, description: str, created_by: str,
                     amount: Decimal = Decimal('0')) -> WorkflowEntry:
        entry = WorkflowEntry(description, created_by, amount)
        self.entries.append(entry)
        return entry

    def get_pending(self) -> List[WorkflowEntry]:
        return [e for e in self.entries if e.status == EntryStatus.PENDING_APPROVAL]

    def get_by_status(self, status: EntryStatus) -> List[WorkflowEntry]:
        return [e for e in self.entries if e.status == status]

    def get_by_creator(self, username: str) -> List[WorkflowEntry]:
        return [e for e in self.entries if e.created_by == username]

    def to_dict(self) -> list:
        return [e.to_dict() for e in self.entries]
