from uuid import UUID
from typing import List
from src.application.ports.budget_repository import BudgetRepository
from src.application.ports.category_repository import CategoryRepository
from src.domain.models.budget import Budget

class ManageBudgetUseCase:
    def __init__(self, budget_repo: BudgetRepository, category_repo: CategoryRepository):
        self.budget_repo = budget_repo
        self.category_repo = category_repo

    async def set_monthly_budget(self, category_id: UUID, limit: float, month: int, year: int) -> Budget:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category with id {category_id} not found.")
        
        if not category.is_budgetable:
            raise ValueError(f"Category {category.name} is not budgetable.")

        existing = await self.budget_repo.get_by_category_and_period(category_id, month, year)
        if existing:
            existing.monthly_limit = limit
            return await self.budget_repo.update(existing)

        budget = Budget(
            category_id=category_id,
            monthly_limit=limit,
            period_month=month,
            period_year=year
        )
        return await self.budget_repo.save(budget)

    async def get_budgets_for_month(self, month: int, year: int) -> List[Budget]:
        return await self.budget_repo.get_all_for_period(month, year)
