"""
PyLedger Core - Immutable Transaction & Audit Trail
"""

from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
import hashlib
import json


@dataclass(frozen=True)
class ImmutableTransaction:
    account_code: str
    account_name: str
    transaction_type: str
    amount: Decimal
    date: datetime
    description: str
    entry_number: str
    sequence: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        d = asdict(self)
        d['amount'] = str(d['amount'])
        d['date'] = d['date'].isoformat()
        d['timestamp'] = d['timestamp'].isoformat()
        return d


class AuditEntry:
    def __init__(self, action: str, entity_type: str, entity_id: str,
                 before: dict = None, after: dict = None,
                 user: str = 'system', reason: str = '',
                 previous_hash: str = None):
        self.timestamp = datetime.now()
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.before = before or {}
        self.after = after or {}
        self.user = user
        self.reason = reason
        self.previous_hash = previous_hash or ('0' * 64)
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        raw = json.dumps({
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'entity_id': self.entity_id,
            'before': {k: str(v) for k, v in self.before.items()},
            'after': {k: str(v) for k, v in self.after.items()},
            'user': self.user,
        }, default=str, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'before': self.before,
            'after': self.after,
            'user': self.user,
            'reason': self.reason,
            'previous_hash': self.previous_hash,
            'hash': self.hash,
        }


class AuditTrail:
    def __init__(self):
        self.entries = []

    def record(self, action: str, entity_type: str, entity_id: str,
               before: dict = None, after: dict = None,
               user: str = 'system', reason: str = '') -> AuditEntry:
        previous_hash = self.entries[-1].hash if self.entries else None
        entry = AuditEntry(action, entity_type, entity_id, before, after,
                           user, reason, previous_hash=previous_hash)
        self.entries.append(entry)
        return entry

    def get_entries(self, entity_type: str = None, entity_id: str = None,
                    action: str = None, limit: int = None) -> list:
        result = self.entries
        if entity_type:
            result = [e for e in result if e.entity_type == entity_type]
        if entity_id:
            result = [e for e in result if e.entity_id == entity_id]
        if action:
            result = [e for e in result if e.action == action]
        if limit:
            return result[-limit:]
        return result

    def verify_chain(self) -> bool:
        for i in range(len(self.entries)):
            entry = self.entries[i]
            expected_prev = self.entries[i - 1].hash if i > 0 else ('0' * 64)
            if entry.previous_hash != expected_prev:
                return False
            recomputed = entry._compute_hash()
            if entry.hash != recomputed:
                return False
        return True
