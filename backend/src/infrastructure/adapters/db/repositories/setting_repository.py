from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.infrastructure.adapters.db.models.setting import AppSettingORM

class SettingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_setting(self, key: str) -> Optional[AppSettingORM]:
        stmt = select(AppSettingORM).where(AppSettingORM.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_settings(self) -> List[AppSettingORM]:
        stmt = select(AppSettingORM)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_setting(self, key: str, value: str, description: Optional[str] = None) -> AppSettingORM:
        setting = await self.get_setting(key)
        if not setting:
            setting = AppSettingORM(key=key, value=value, description=description)
            self.session.add(setting)
        else:
            setting.value = value
            if description is not None:
                setting.description = description
            setting.updated_at = datetime.now(timezone.utc)
            
        await self.session.commit()
        await self.session.refresh(setting)
        return setting
