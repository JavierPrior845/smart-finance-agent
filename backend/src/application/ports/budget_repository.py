from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.domain.models.budget import Budget

class BudgetRepository(ABC):
    @abstractmethod
    async def get_by_id(self, budget_id: UUID) -> Budget | None:
        pass

    @abstractmethod
    async def get_by_category_and_period(self, category_id: UUID, month: int, year: int) -> Budget | None:
        pass
        
    @abstractmethod
    async def get_all_for_period(self, month: int, year: int) -> List[Budget]:
        pass

    @abstractmethod
    async def save(self, budget: Budget) -> Budget:
        pass

    @abstractmethod
    async def update(self, budget: Budget) -> Budget:
        pass
