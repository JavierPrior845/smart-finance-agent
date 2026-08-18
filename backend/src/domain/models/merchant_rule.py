from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

class MerchantRule(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    pattern: str
    category_id: UUID
    priority: int = 1
    created_at: datetime | None = None
