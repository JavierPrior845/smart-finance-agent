from typing import List
from uuid import UUID
from src.application.ports.merchant_rule_repository import MerchantRuleRepository
from src.domain.models.merchant_rule import MerchantRule

class ManageMerchantRulesUseCase:
    def __init__(self, rule_repo: MerchantRuleRepository):
        self.rule_repo = rule_repo

    async def get_all_rules(self) -> List[MerchantRule]:
        return await self.rule_repo.get_all()

    async def create_rule(self, pattern: str, category_id: UUID, priority: int) -> MerchantRule:
        rule = MerchantRule(
            pattern=pattern,
            category_id=category_id,
            priority=priority
        )
        return await self.rule_repo.save(rule)

    async def delete_rule(self, rule_id: UUID) -> None:
        await self.rule_repo.delete(rule_id)
