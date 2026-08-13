from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from datetime import datetime
from src.domain.models.transaction import Transaction

class TransactionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        pass

    @abstractmethod
    async def get_by_account(self, account_id: UUID, limit: int = 50, offset: int = 0) -> List[Transaction]:
        pass
        
    @abstractmethod
    async def get_recent(self, limit: int = 50) -> List[Transaction]:
        pass

    @abstractmethod
    async def get_all_paginated(
        self, 
        limit: int = 20, 
        offset: int = 0, 
        search: str | None = None,
        category_id: UUID | None = None,
        source: str | None = None
    ) -> tuple[List[Transaction], int]:
        pass

    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction:
        pass

    @abstractmethod
    async def delete(self, transaction_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_nearest_neighbors(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.88) -> List[Transaction]:
        pass
