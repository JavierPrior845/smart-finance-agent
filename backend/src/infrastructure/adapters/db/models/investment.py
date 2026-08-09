import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .account import AccountORM
from .transaction import TransactionORM

class InvestmentAssetORM(Base):
    __tablename__ = "investment_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ticker: Mapped[str | None] = mapped_column(String(20), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(30), nullable=False)
    broker: Mapped[str] = mapped_column(String(50), nullable=False)
    
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invested_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    units_qty: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    average_buy_price: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    
    exit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    realized_pnl: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
    
    source_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    source_account: Mapped["AccountORM | None"] = relationship("AccountORM")

class InvestmentMovementORM(Base):
    __tablename__ = "investment_movements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investment_assets.id", ondelete="CASCADE"), nullable=False
    )
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True
    )
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    units: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    unit_price: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    movement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    asset: Mapped["InvestmentAssetORM"] = relationship("InvestmentAssetORM")
    transaction: Mapped["TransactionORM | None"] = relationship("TransactionORM")

class InvestmentSnapshotORM(Base):
    __tablename__ = "investment_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investment_assets.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    total_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    asset: Mapped["InvestmentAssetORM"] = relationship("InvestmentAssetORM")
