"""
PyLedger Events - Lightweight EventBus (Phase 6)
Decouples domain (EntryPosted, ...) from adapters (webhooks, audit, cache).
stdlib-only; swap with Redis/Kafka adapter later without touching domain.
"""

from collections import defaultdict


class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, event_type: str, handler):
        self._subs[event_type].append(handler)
        return handler

    def emit(self, event_type: str, payload: dict = None):
        results = []
        for h in list(self._subs.get(event_type, [])):
            results.append(h(payload or {}))
        return results

    def unsubscribe(self, event_type: str, handler):
        if handler in self._subs.get(event_type, []):
            self._subs[event_type].remove(handler)


# Process-wide default bus (convenience; inject your own in large apps)
default_bus = EventBus()

ENTRY_POSTED = "EntryPosted"
INVOICE_ISSUED = "InvoiceIssued"
PERIOD_CLOSED = "PeriodClosed"
