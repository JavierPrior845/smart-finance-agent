from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
