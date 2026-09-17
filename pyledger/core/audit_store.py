"""
PyLedger Core - Persistent, append-only Audit Store (Phase 4)
Extends in-memory AuditTrail with JSONL durability + tamper detection.
"""

import json
import os
from pyledger.core.immutable import AuditTrail


class PersistentAuditTrail(AuditTrail):
    """AuditTrail that can be snapshotted to append-only JSONL."""

    def save_jsonl(self, path: str) -> int:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for e in self.entries:
                f.write(json.dumps(e.to_dict(), default=str) + "\n")
        os.replace(tmp, path)
        return len(self.entries)

    @classmethod
    def load_jsonl(cls, path: str) -> "PersistentAuditTrail":
        from pyledger.core.immutable import AuditEntry
        trail = cls()
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                e = AuditEntry(
                    action=d["action"], entity_type=d.get("entity_type", ""),
                    entity_id=d.get("entity_id", ""),
                    before=d.get("before"), after=d.get("after"),
                    user=d.get("user", "system"), reason=d.get("reason", ""),
                    previous_hash=d.get("previous_hash"),
                )
                # Preserve original hash/timestamp for verification
                e.hash = d.get("hash", e.hash)
                from datetime import datetime
                try:
                    e.timestamp = datetime.fromisoformat(d["timestamp"])
                except Exception:
                    pass
                trail.entries.append(e)
        return trail
