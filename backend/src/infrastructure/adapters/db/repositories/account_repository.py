from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.account_repository import AccountRepository
from src.domain.models.account import Account
from src.infrastructure.adapters.db.models.account import AccountORM

class SQLAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: AccountORM) -> Account:
        return Account(
            id=orm.id,
            name=orm.name,
            account_type=orm.account_type,
            currency=orm.currency,
            initial_balance=float(orm.initial_balance),
            current_balance=float(orm.current_balance),
            is_main=orm.is_main,
            is_active=orm.is_active,
            created_at=orm.created_at
        )

    def _to_orm(self, domain: Account) -> AccountORM:
        return AccountORM(
            id=domain.id,
            name=domain.name,
            account_type=domain.account_type,
            currency=domain.currency,
            initial_balance=domain.initial_balance,
            current_balance=domain.current_balance,
            is_main=domain.is_main,
            is_active=domain.is_active,
            created_at=domain.created_at
        )

    async def get_by_id(self, account_id: UUID) -> Account | None:
        stmt = select(AccountORM).where(AccountORM.id == account_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_all_active(self) -> List[Account]:
        stmt = select(AccountORM).where(AccountORM.is_active == True)
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_main_account(self) -> Account | None:
        stmt = select(AccountORM).where(AccountORM.is_main == True, AccountORM.is_active == True)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def save(self, account: Account) -> Account:
        orm = self._to_orm(account)
        self.session.add(orm)
        await self.session.flush()
        return self._to_domain(orm)

    async def update(self, account: Account) -> Account:
        orm = await self.session.get(AccountORM, account.id)
        if orm:
            orm.name = account.name
            orm.account_type = account.account_type
            orm.currency = account.currency
            orm.initial_balance = account.initial_balance
            orm.current_balance = account.current_balance
            orm.is_main = account.is_main
            orm.is_active = account.is_active
            await self.session.flush()
            return self._to_domain(orm)
        return account
