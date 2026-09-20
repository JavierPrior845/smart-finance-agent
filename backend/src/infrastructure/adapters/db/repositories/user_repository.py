from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.db.models.user import UserORM


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserORM | None:
        stmt = select(UserORM).where(func.lower(UserORM.email) == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_users(self) -> int:
        stmt = select(func.count(UserORM.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def create_user(
        self,
        name: str,
        email: str,
        hashed_password: str,
        role: str = "admin",
    ) -> UserORM:
        user = UserORM(
            name=name.strip(),
            email=email.lower().strip(),
            hashed_password=hashed_password,
            role=role,
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_token(self, user_id: UUID, token: str | None) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(
                current_token=token,
                last_login_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def list_all(self) -> list[UserORM]:
        stmt = select(UserORM).order_by(UserORM.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_user(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True
