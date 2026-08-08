from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

class Category(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    parent_id: UUID | None = None
    icon: str | None = None
    color: str | None = None
    is_budgetable: bool = True
    created_at: datetime | None = None
