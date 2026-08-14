from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class MerchantRuleCreate(BaseModel):
    pattern: str = Field(..., max_length=100)
    category_id: UUID
    priority: int = 1

class MerchantRuleUpdate(BaseModel):
    pattern: str | None = Field(None, max_length=100)
    category_id: UUID | None = None
    priority: int | None = None

class MerchantRuleResponse(BaseModel):
    id: UUID
    pattern: str
    category_id: UUID
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True
