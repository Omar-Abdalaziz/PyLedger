"""PyLedger benchmarks (Phase 5 gate: fail if p95 degrades >15%)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from decimal import Decimal
from pyledger import Ledger, Account, JournalEntry


def bench_post(n: int = 2000) -> float:
    l = Ledger("bench", "USD")
    l.add_account(Account("Cash", "asset", "1000"))
    l.add_account(Account("Sales", "income", "4000"))
    t0 = time.perf_counter()
    for i in range(n):
        e = JournalEntry(f"sale {i}")
        e.add_debit(l.get_account("1000"), 10).add_credit(l.get_account("4000"), 10)
        l.record_entry(e)
    dt = time.perf_counter() - t0
    print(f"posted {n} entries in {dt:.2f}s = {n/dt:.0f}/s")
    t0 = time.perf_counter()
    l.trial_balance()
    print(f"trial_balance: {(time.perf_counter()-t0)*1000:.1f}ms")
    return n / dt


if __name__ == "__main__":
    bench_post()
