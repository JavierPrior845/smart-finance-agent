from uuid import UUID
from typing import List
from src.application.ports.category_repository import CategoryRepository
from src.domain.models.category import Category

class ManageCategoryUseCase:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def create_category(self, name: str, parent_id: UUID | None = None, icon: str | None = None, color: str | None = None, is_budgetable: bool = True, default_budget_limit: float | None = None, is_active: bool = True) -> Category:
        if parent_id:
            parent = await self.repository.get_by_id(parent_id)
            if not parent:
                raise ValueError(f"Parent category with id {parent_id} does not exist.")
                
        category = Category(
            name=name,
            parent_id=parent_id,
            icon=icon,
            color=color,
            is_budgetable=is_budgetable,
            default_budget_limit=default_budget_limit,
            is_active=is_active
        )
        return await self.repository.save(category)

    async def update_category(self, category_id: UUID, name: str | None = None, parent_id: UUID | None = None, icon: str | None = None, color: str | None = None, is_budgetable: bool | None = None, default_budget_limit: float | None = None, is_active: bool | None = None) -> Category:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category with id {category_id} not found.")

        if name is not None:
            category.name = name
        if parent_id is not None:
            category.parent_id = parent_id
        if icon is not None:
            category.icon = icon
        if color is not None:
            category.color = color
        if is_budgetable is not None:
            category.is_budgetable = is_budgetable
        if default_budget_limit is not None:
            category.default_budget_limit = default_budget_limit
        if is_active is not None:
            category.is_active = is_active
            
        return await self.repository.update(category)

    async def get_all_categories(self) -> List[Category]:
        return await self.repository.get_all()
