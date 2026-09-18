"""
PyLedger Database - SQLAlchemy Store (Phase 2)
Enterprise persistence: Postgres + SQLite via SQLAlchemy 2.0.

Design:
- ORM tables are the source of truth for cross-restart durability.
- Domain objects (Account/Ledger/JournalEntry) stay plain Python;
  this module maps them <-> ORM (no domain pollution).
- company_id enables multi-tenancy from day one.
- SequenceORM provides crash-safe document numbering.
- EntryORM has idempotency_key UNIQUE to allow safe retries.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

try:
    from sqlalchemy import (
        String, Numeric, DateTime, Boolean, Text, ForeignKey,
        UniqueConstraint,
    )
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
    _HAS_SA = True
except ImportError:  # pragma: no cover - optional dependency
    _HAS_SA = False


if _HAS_SA:
    class Base(DeclarativeBase):
        pass

    class AccountORM(Base):
        __tablename__ = "accounts"
        __table_args__ = (UniqueConstraint("company_id", "code", name="uq_company_code"),)

        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        company_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
        code: Mapped[str] = mapped_column(String(32), index=True)
        name: Mapped[str] = mapped_column(String(255))
        account_type: Mapped[str] = mapped_column(String(32))
        balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
        currency: Mapped[str] = mapped_column(String(8), default="USD")
        description: Mapped[str] = mapped_column(Text, default="")
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    class EntryORM(Base):
        __tablename__ = "journal_entries"

        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        company_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
        number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
        description: Mapped[str] = mapped_column(Text, default="")
        entry_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
        posted: Mapped[bool] = mapped_column(Boolean, default=False)
        idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

        lines: Mapped[list["LineORM"]] = relationship(back_populates="entry", cascade="all, delete-orphan")

    class LineORM(Base):
        __tablename__ = "entry_lines"

        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id"))
        account_code: Mapped[str] = mapped_column(String(32), index=True)
        side: Mapped[str] = mapped_column(String(8))  # debit | credit
        amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
        description: Mapped[str] = mapped_column(Text, default="")

        entry: Mapped["EntryORM"] = relationship(back_populates="lines")

    class SequenceORM(Base):
        __tablename__ = "sequences"

        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        company_id: Mapped[str] = mapped_column(String(64), default="default")
        doc_type: Mapped[str] = mapped_column(String(32))
        fiscal_year: Mapped[str] = mapped_column(String(8), default="")
        last_value: Mapped[int] = mapped_column(default=0)

        __table_args__ = (UniqueConstraint("company_id", "doc_type", "fiscal_year", name="uq_seq"),)

    def create_all(engine):
        Base.metadata.create_all(engine)

else:  # Fallback stubs so imports never crash without sqlalchemy
    Base = object
    AccountORM = EntryORM = LineORM = SequenceORM = None

    def create_all(engine):
        raise ImportError("sqlalchemy is required for SQLAlchemy store (pip install sqlalchemy)")
