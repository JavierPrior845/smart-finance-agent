from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.merchant_rule_repository import MerchantRuleRepository
from src.domain.models.merchant_rule import MerchantRule
from src.infrastructure.adapters.db.models.merchant_rule import MerchantRuleORM

class SQLAlchemyMerchantRuleRepository(MerchantRuleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: MerchantRuleORM) -> MerchantRule:
        return MerchantRule(
            id=orm.id,
            pattern=orm.pattern,
            category_id=orm.category_id,
            priority=orm.priority,
            created_at=orm.created_at
        )

    def _to_orm(self, domain: MerchantRule) -> MerchantRuleORM:
        return MerchantRuleORM(
            id=domain.id,
            pattern=domain.pattern,
            category_id=domain.category_id,
            priority=domain.priority,
            created_at=domain.created_at
        )

    async def get_all(self) -> List[MerchantRule]:
        stmt = select(MerchantRuleORM).order_by(MerchantRuleORM.priority.desc(), MerchantRuleORM.created_at.desc())
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def save(self, rule: MerchantRule) -> MerchantRule:
        orm = self._to_orm(rule)
        self.session.add(orm)
        await self.session.flush()
        return self._to_domain(orm)

    async def delete(self, rule_id: UUID) -> None:
        orm = await self.session.get(MerchantRuleORM, rule_id)
        if orm:
            await self.session.delete(orm)
            await self.session.flush()
