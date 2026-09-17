"""
PyLedger API - FastAPI factory (Phase 6, optional dependency)
Does NOT import fastapi at module load; only inside create_app().

Run:
    pip install fastapi uvicorn
    uvicorn pyledger.api:create_app --factory --port 8000
"""

def create_app(ledger=None, company_id: str = "default"):
    try:
        from fastapi import FastAPI, Header, HTTPException
        from pydantic import BaseModel
    except ImportError as e:
        raise ImportError("pip install fastapi uvicorn pydantic to use the API") from e

    from pyledger import Ledger, Account, JournalEntry

    app = FastAPI(title="PyLedger API", version="2.1.0")
    state_ledger = ledger or Ledger("API Ledger", "USD", company_id=company_id)
    seen_keys = set()

    class Line(BaseModel):
        account: str
        side: str  # debit | credit
        amount: float
        description: str = ""

    class EntryIn(BaseModel):
        description: str
        lines: list[Line]
        cost_center: str | None = None

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "2.1.0"}

    @app.get("/trial-balance")
    def trial_balance():
        return state_ledger.get_trial_balance()

    @app.post("/entries")
    def post_entry(payload: EntryIn, x_idempotency_key: str | None = Header(default=None)):
        if x_idempotency_key and x_idempotency_key in seen_keys:
            raise HTTPException(status_code=409, detail="Duplicate idempotency key")
        entry = JournalEntry(payload.description, cost_center=payload.cost_center)
        for ln in payload.lines:
            try:
                acc = state_ledger.get_account(ln.account)
            except Exception:
                raise HTTPException(status_code=404, detail=f"Account {ln.account} not found")
            if ln.side == "debit":
                entry.add_debit(acc, ln.amount, ln.description)
            else:
                entry.add_credit(acc, ln.amount, ln.description)
        try:
            state_ledger.record_entry(entry)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
        if x_idempotency_key:
            seen_keys.add(x_idempotency_key)
        return entry.to_dict()

    return app
