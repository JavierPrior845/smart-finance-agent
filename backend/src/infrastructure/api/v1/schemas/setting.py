from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SettingResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class SettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None
