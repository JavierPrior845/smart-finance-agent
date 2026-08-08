from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.db.session import get_db_session
from src.infrastructure.adapters.db.repositories.setting_repository import SettingRepository
from src.infrastructure.api.v1.schemas.setting import SettingResponse, SettingUpdate

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=List[SettingResponse])
async def get_all_settings(db: AsyncSession = Depends(get_db_session)):
    repo = SettingRepository(db)
    return await repo.get_all_settings()

@router.get("/{key}", response_model=SettingResponse)
async def get_setting(key: str, db: AsyncSession = Depends(get_db_session)):
    repo = SettingRepository(db)
    setting = await repo.get_setting(key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/{key}", response_model=SettingResponse)
async def update_setting(key: str, data: SettingUpdate, db: AsyncSession = Depends(get_db_session)):
    repo = SettingRepository(db)
    setting = await repo.update_setting(key, data.value, data.description)
    return setting
