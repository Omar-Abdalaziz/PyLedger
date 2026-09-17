"""
PyLedger Database - Unit of Work + Ledger Store (Phase 2)

Usage:
    from pyledger.database.uow import SqlAlchemyLedgerStore

    store = SqlAlchemyLedgerStore("sqlite:///ledger.db", company_id="acme")
    store.save_ledger(ledger)          # persist accounts + entries
    ledger2 = store.load_ledger("Main Ledger")
    with store.unit_of_work() as uow:
        n = uow.next_sequence("JE")    # crash-safe numbering
"""

from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal

from pyledger.database.orm import (
    _HAS_SA, create_all, AccountORM, EntryORM, LineORM, SequenceORM,
)


class SqlAlchemyLedgerStore:
    """Persist Ledger <-> SQLAlchemy (SQLite + Postgres)."""

    def __init__(self, url: str = "sqlite:///ledger.db", company_id: str = "default"):
        if not _HAS_SA:
            raise ImportError("pip install sqlalchemy to use SqlAlchemyLedgerStore")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.url = url
        self.company_id = company_id
        self.engine = create_engine(url, future=True)
        create_all(self.engine)
        self._Session = sessionmaker(bind=self.engine, future=True)

    @contextmanager
    def unit_of_work(self):
        session = self._Session()
        try:
            yield _UnitOfWork(session, self.company_id)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def next_sequence(self, doc_type: str, fiscal_year: str = "") -> int:
        with self.unit_of_work() as uow:
            return uow.next_sequence(doc_type, fiscal_year)

    # --- Ledger persistence ---
    def save_ledger(self, ledger, idempotency_prefix: str = "") -> int:
        """Upsert accounts + append new journal entries. Returns entry count."""
        from sqlalchemy import select
        count = 0
        with self._Session() as s:
            for acc in ledger.accounts.values():
                row = s.execute(
                    select(AccountORM).where(
                        AccountORM.company_id == self.company_id,
                        AccountORM.code == acc.code,
                    )
                ).scalar_one_or_none()
                if row is None:
                    s.add(AccountORM(
                        company_id=self.company_id, code=acc.code,
                        name=acc.name, account_type=acc.type,
                        balance=Decimal(str(acc.get_balance())),
                        currency=acc.currency, description=acc.description or "",
                    ))
                else:
                    row.name = acc.name
                    row.account_type = acc.type
                    row.balance = Decimal(str(acc.get_balance()))
                    row.currency = acc.currency
            for e in ledger.journal_entries:
                exists = s.execute(
                    select(EntryORM).where(EntryORM.number == e.number)
                ).scalar_one_or_none()
                if exists is not None:
                    continue
                orm = EntryORM(
                    company_id=self.company_id, number=e.number,
                    description=e.description, entry_date=e.date,
                    posted=e.posted,
                    idempotency_key=f"{idempotency_prefix}{e.number}" or None,
                )
                for t in list(e.debits) + list(e.credits):
                    orm.lines.append(LineORM(
                        account_code=t.account.code, side=t.type,
                        amount=Decimal(str(t.amount)), description=t.description or "",
                    ))
                s.add(orm)
                count += 1
            s.commit()
        return count

    def load_ledger(self, name: str = "Main Ledger", currency: str = "USD"):
        """Rebuild an in-memory Ledger from stored rows (accounts + balances)."""
        from sqlalchemy import select
        from pyledger.core.ledger import Ledger
        from pyledger.core.account import Account
        ledger = Ledger(name, currency)
        with self._Session() as s:
            rows = s.execute(
                select(AccountORM).where(AccountORM.company_id == self.company_id)
            ).scalars().all()
            for r in rows:
                ledger.add_account(Account(
                    name=r.name, account_type=r.account_type, code=r.code,
                    currency=r.currency, description=r.description or "",
                    initial_balance=Decimal(str(r.balance)),
                ))
        return ledger

    def entry_count(self) -> int:
        from sqlalchemy import select, func
        with self._Session() as s:
            return s.execute(
                select(func.count()).select_from(EntryORM).where(
                    EntryORM.company_id == self.company_id)
            ).scalar() or 0


class _UnitOfWork:
    def __init__(self, session, company_id: str):
        self.session = session
        self.company_id = company_id

    def next_sequence(self, doc_type: str, fiscal_year: str = "") -> int:
        from sqlalchemy import select
        row = self.session.execute(
            select(SequenceORM).where(
                SequenceORM.company_id == self.company_id,
                SequenceORM.doc_type == doc_type,
                SequenceORM.fiscal_year == fiscal_year,
            )
        ).scalar_one_or_none()
        if row is None:
            row = SequenceORM(company_id=self.company_id, doc_type=doc_type,
                              fiscal_year=fiscal_year, last_value=0)
            self.session.add(row)
            self.session.flush()
        row.last_value += 1
        self.session.flush()
        return row.last_value
