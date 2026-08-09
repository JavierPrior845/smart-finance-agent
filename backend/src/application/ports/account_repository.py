from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.domain.models.account import Account

class AccountRepository(ABC):
    @abstractmethod
    async def get_by_id(self, account_id: UUID) -> Account | None:
        pass

    @abstractmethod
    async def get_all_active(self) -> List[Account]:
        pass
        
    @abstractmethod
    async def get_main_account(self) -> Account | None:
        pass

    @abstractmethod
    async def save(self, account: Account) -> Account:
        pass

    @abstractmethod
    async def update(self, account: Account) -> Account:
        pass
