from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.domain.models.category import Category

class CategoryRepository(ABC):
    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Category | None:
        pass

    @abstractmethod
    async def get_all(self) -> List[Category]:
        pass

    @abstractmethod
    async def save(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def update(self, category: Category) -> Category:
        pass
