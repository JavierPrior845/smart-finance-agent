from uuid import UUID, uuid4
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

CategoryType = Literal['EXPENSE', 'INCOME']

class Category(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    type: CategoryType = 'EXPENSE'
    parent_id: UUID | None = None
    icon: str | None = None
    color: str | None = None
    is_budgetable: bool = True
    default_budget_limit: float | None = None
    is_active: bool = True
    created_at: datetime | None = None
