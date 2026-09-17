"""
PyLedger Core - Sequence Service
Collision-free, injectable document numbering (JE, INV, PAY, ...).

Replaces fragile class-level _entry_counter / _invoice_counter which
reset on process restart and collide across ledgers/threads.
"""

import threading
import uuid
from datetime import datetime


class SequenceService:
    """Thread-safe in-memory sequence generator with UUID fallback."""

    def __init__(self, prefix: str = "DOC", width: int = 6):
        self.prefix = prefix
        self.width = width
        self._counter = 0
        self._lock = threading.Lock()

    def next(self, prefix: str = None) -> str:
        with self._lock:
            self._counter += 1
            n = self._counter
        p = prefix or self.prefix
        return f"{p}-{n:0{self.width}d}"

    def next_unique(self, prefix: str = None) -> str:
        """Globally unique number (safe across restarts/processes)."""
        p = prefix or self.prefix
        short = uuid.uuid4().hex[:8].upper()
        date = datetime.now().strftime("%Y%m")
        return f"{p}-{date}-{short}"

    def reset(self, value: int = 0):
        with self._lock:
            self._counter = value


# Shared default generators (backward compatible sequential style)
_journal_seq = SequenceService("JE")
_invoice_seq = SequenceService("INV")
_payment_seq = SequenceService("PAY")


def next_journal_number(entry_number: str = None, unique: bool = False) -> str:
    if entry_number:
        return entry_number
    if unique:
        return _journal_seq.next_unique()
    return _journal_seq.next()


def next_invoice_number(invoice_number: str = None, unique: bool = False) -> str:
    if invoice_number:
        return invoice_number
    if unique:
        return _invoice_seq.next_unique()
    return _invoice_seq.next()


def next_payment_reference(reference: str = None, unique: bool = False) -> str:
    if reference:
        return reference
    if unique:
        return _payment_seq.next_unique()
    return _payment_seq.next()
