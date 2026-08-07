import uuid
from sqlalchemy import Numeric, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .category import CategoryORM

class BudgetORM(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    monthly_limit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)

    category: Mapped["CategoryORM"] = relationship("CategoryORM")

    __table_args__ = (
        UniqueConstraint("category_id", "period_month", "period_year", name="uq_budget_category_period"),
    )
