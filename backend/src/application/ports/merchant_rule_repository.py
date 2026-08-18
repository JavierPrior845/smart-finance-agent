from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.domain.models.merchant_rule import MerchantRule

class MerchantRuleRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[MerchantRule]:
        pass

    @abstractmethod
    async def save(self, rule: MerchantRule) -> MerchantRule:
        pass

    @abstractmethod
    async def delete(self, rule_id: UUID) -> None:
        pass
