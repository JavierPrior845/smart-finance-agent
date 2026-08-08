from uuid import UUID
from typing import List
from src.application.ports.category_repository import CategoryRepository
from src.domain.models.category import Category

class ManageCategoryUseCase:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def create_category(self, name: str, parent_id: UUID | None = None, icon: str | None = None, color: str | None = None, is_budgetable: bool = True) -> Category:
        if parent_id:
            parent = await self.repository.get_by_id(parent_id)
            if not parent:
                raise ValueError(f"Parent category with id {parent_id} does not exist.")
                
        category = Category(
            name=name,
            parent_id=parent_id,
            icon=icon,
            color=color,
            is_budgetable=is_budgetable
        )
        return await self.repository.save(category)

    async def get_all_categories(self) -> List[Category]:
        return await self.repository.get_all()
