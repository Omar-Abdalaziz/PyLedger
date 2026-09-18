"""
PyLedger API - FastAPI factory (Phase 6, optional dependency)
Does NOT import fastapi at module load; only inside create_app().

Run:
    pip install fastapi uvicorn
    uvicorn pyledger.api:create_app --factory --port 8000
"""

from collections import OrderedDict
from typing import List, Optional

MAX_IDEMPOTENCY_KEYS = 10_000  # bound replay memory (DoS resistance)


def create_app(ledger=None, company_id: str = "default"):
    try:
        from fastapi import FastAPI, Header, HTTPException
        from pydantic import BaseModel
    except ImportError as e:
        raise ImportError("pip install fastapi uvicorn pydantic to use the API") from e

    from pyledger import Ledger, JournalEntry
    from pyledger.exceptions.errors import AccountNotFoundError

    app = FastAPI(title="PyLedger API", version="2.1.0")
    state_ledger = ledger or Ledger("API Ledger", "USD", company_id=company_id)
    seen_keys: "OrderedDict[str, None]" = OrderedDict()

    class Line(BaseModel):
        account: str
        side: str  # debit | credit
        amount: float
        description: str = ""

    class EntryIn(BaseModel):
        description: str
        lines: List[Line]
        cost_center: Optional[str] = None

    def _remember(key: str):
        seen_keys[key] = None
        while len(seen_keys) > MAX_IDEMPOTENCY_KEYS:
            seen_keys.popitem(last=False)

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "2.1.0"}

    @app.get("/trial-balance")
    def trial_balance():
        return state_ledger.get_trial_balance()

    @app.post("/entries")
    def post_entry(payload: EntryIn, x_idempotency_key: Optional[str] = Header(default=None)):
        if x_idempotency_key and x_idempotency_key in seen_keys:
            raise HTTPException(status_code=409, detail="Duplicate idempotency key")
        if not payload.description or not payload.description.strip():
            raise HTTPException(status_code=422, detail="Description is required")
        if not payload.lines:
            raise HTTPException(status_code=422, detail="At least one line is required")
        entry = JournalEntry(payload.description.strip(), cost_center=payload.cost_center)
        for ln in payload.lines:
            if ln.side not in ("debit", "credit"):
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid side '{ln.side}': must be 'debit' or 'credit'",
                )
            try:
                acc = state_ledger.get_account(ln.account)
            except AccountNotFoundError:
                raise HTTPException(status_code=404, detail=f"Account {ln.account} not found")
            try:
                if ln.side == "debit":
                    entry.add_debit(acc, ln.amount, ln.description)
                else:
                    entry.add_credit(acc, ln.amount, ln.description)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
        try:
            state_ledger.record_entry(entry)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
        if x_idempotency_key:
            _remember(x_idempotency_key)
        return entry.to_dict()

    return app
