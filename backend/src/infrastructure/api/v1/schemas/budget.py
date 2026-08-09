from uuid import UUID
from pydantic import BaseModel

class BudgetCreate(BaseModel):
    category_id: UUID
    monthly_limit: float
    period_month: int
    period_year: int

class BudgetResponse(BudgetCreate):
    id: UUID

    class Config:
        from_attributes = True

class BudgetProgressResponse(BudgetResponse):
    spent: float
    category_name: str
    category_color: str | None = None
