from typing import List
from uuid import UUID
from sqlalchemy import select, func, and_
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.infrastructure.adapters.db.models.category import CategoryORM
from src.infrastructure.adapters.db.models.transaction import TransactionORM

from src.application.ports.budget_repository import BudgetRepository
from src.domain.models.budget import Budget
from src.infrastructure.adapters.db.models.budget import BudgetORM

class SQLAlchemyBudgetRepository(BudgetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: BudgetORM) -> Budget:
        return Budget(
            id=orm.id,
            category_id=orm.category_id,
            monthly_limit=float(orm.monthly_limit),
            period_month=orm.period_month,
            period_year=orm.period_year
        )

    def _to_orm(self, domain: Budget) -> BudgetORM:
        return BudgetORM(
            id=domain.id,
            category_id=domain.category_id,
            monthly_limit=domain.monthly_limit,
            period_month=domain.period_month,
            period_year=domain.period_year
        )

    async def get_by_id(self, budget_id: UUID) -> Budget | None:
        stmt = select(BudgetORM).where(BudgetORM.id == budget_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_category_and_period(self, category_id: UUID, month: int, year: int) -> Budget | None:
        stmt = select(BudgetORM).where(
            BudgetORM.category_id == category_id,
            BudgetORM.period_month == month,
            BudgetORM.period_year == year
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_all_for_period(self, month: int, year: int) -> List[Budget]:
        stmt = select(BudgetORM).where(
            BudgetORM.period_month == month,
            BudgetORM.period_year == year
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_progress_for_month(self, month: int, year: int) -> List[dict]:
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        # Handle December edge case
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        end_date = datetime(next_year, next_month, 1, tzinfo=timezone.utc)

        # Build subquery to get total spent per category in that month
        # Notice we take abs(amount) because expenses are stored as negative in DB (as we set up before)
        spent_subq = select(
            TransactionORM.category_id,
            func.sum(func.abs(TransactionORM.amount)).label("spent")
        ).where(
            and_(
                TransactionORM.type == 'EXPENSE',
                TransactionORM.transaction_date >= start_date,
                TransactionORM.transaction_date < end_date,
                TransactionORM.category_id.isnot(None)
            )
        ).group_by(TransactionORM.category_id).subquery()

        # Subquery for budget overrides for the current month
        budget_subq = select(
            BudgetORM.category_id,
            BudgetORM.id.label("budget_id"),
            BudgetORM.monthly_limit.label("override_limit")
        ).where(
            BudgetORM.period_month == month,
            BudgetORM.period_year == year
        ).subquery()

        # Effective limit is the override if it exists, else the default
        effective_limit = func.coalesce(budget_subq.c.override_limit, CategoryORM.default_budget_limit)

        stmt = select(
            func.coalesce(budget_subq.c.budget_id, CategoryORM.id).label("id"), # return some ID for the frontend (budget id or category id as fallback)
            CategoryORM.id.label("category_id"),
            effective_limit.label("monthly_limit"),
            func.cast(month, sqlalchemy.Integer).label("period_month"),
            func.cast(year, sqlalchemy.Integer).label("period_year"),
            CategoryORM.name.label("category_name"),
            CategoryORM.color.label("category_color"),
            func.coalesce(spent_subq.c.spent, 0).label("spent")
        ).select_from(CategoryORM).outerjoin(
            budget_subq, CategoryORM.id == budget_subq.c.category_id
        ).outerjoin(
            spent_subq, CategoryORM.id == spent_subq.c.category_id
        ).where(
            and_(
                CategoryORM.is_active == True,
                effective_limit > 0
            )
        )

        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    async def save(self, budget: Budget) -> Budget:
        orm = self._to_orm(budget)
        self.session.add(orm)
        await self.session.flush()
        return self._to_domain(orm)

    async def update(self, budget: Budget) -> Budget:
        orm = await self.session.get(BudgetORM, budget.id)
        if orm:
            orm.category_id = budget.category_id
            orm.monthly_limit = budget.monthly_limit
            orm.period_month = budget.period_month
            orm.period_year = budget.period_year
            await self.session.flush()
            return self._to_domain(orm)
        return budget
