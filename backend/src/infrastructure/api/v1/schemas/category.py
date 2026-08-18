from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    type: Literal['EXPENSE', 'INCOME'] = 'EXPENSE'
    parent_id: Optional[UUID] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_budgetable: bool = True
    default_budget_limit: Optional[float] = None
    is_active: bool = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[Literal['EXPENSE', 'INCOME']] = None
    parent_id: Optional[UUID] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_budgetable: Optional[bool] = None
    default_budget_limit: Optional[float] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryCreate):
    id: UUID

    class Config:
        from_attributes = True
