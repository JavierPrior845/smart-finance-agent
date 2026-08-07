import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from .base import Base
from .account import AccountORM
from .category import CategoryORM

class TransactionORM(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    destination_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(30), default="EXPENSE", nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    is_anomalous: Mapped[bool] = mapped_column(Boolean, default=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    embedding = mapped_column(Vector(384), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    account: Mapped["AccountORM"] = relationship("AccountORM", foreign_keys=[account_id])
    destination_account: Mapped["AccountORM | None"] = relationship(
        "AccountORM", foreign_keys=[destination_account_id]
    )
    category: Mapped["CategoryORM | None"] = relationship("CategoryORM")
