from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.category_repository import CategoryRepository
from src.domain.models.category import Category
from src.infrastructure.adapters.db.models.category import CategoryORM

class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: CategoryORM) -> Category:
        return Category(
            id=orm.id,
            name=orm.name,
            parent_id=orm.parent_id,
            icon=orm.icon,
            color=orm.color,
            is_budgetable=orm.is_budgetable,
            default_budget_limit=float(orm.default_budget_limit) if orm.default_budget_limit is not None else None,
            is_active=orm.is_active,
            created_at=orm.created_at
        )

    def _to_orm(self, domain: Category) -> CategoryORM:
        return CategoryORM(
            id=domain.id,
            name=domain.name,
            parent_id=domain.parent_id,
            icon=domain.icon,
            color=domain.color,
            is_budgetable=domain.is_budgetable,
            default_budget_limit=domain.default_budget_limit,
            is_active=domain.is_active,
            created_at=domain.created_at
        )

    async def get_by_id(self, category_id: UUID) -> Category | None:
        stmt = select(CategoryORM).where(CategoryORM.id == category_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_all(self) -> List[Category]:
        # Solo devolver las activas para no ensuciar la interfaz, o podemos devolver todas
        stmt = select(CategoryORM).where(CategoryORM.is_active == True)
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def save(self, category: Category) -> Category:
        orm = self._to_orm(category)
        self.session.add(orm)
        await self.session.flush()
        return self._to_domain(orm)

    async def update(self, category: Category) -> Category:
        orm = await self.session.get(CategoryORM, category.id)
        if orm:
            orm.name = category.name
            orm.parent_id = category.parent_id
            orm.icon = category.icon
            orm.color = category.color
            orm.is_budgetable = category.is_budgetable
            orm.default_budget_limit = category.default_budget_limit
            orm.is_active = category.is_active
            await self.session.flush()
            return self._to_domain(orm)
        return category
