from typing import Optional, List
from pydantic import BaseModel, Field

class BudgetStatusItemDTO(BaseModel):
    category_id: str
    category_name: str
    limit: float
    spent: float
    remaining: float
    percentage_spent: float
    is_exceeded: bool
    status: str  # "ok", "warning" (>80%), "danger" (>=100%)

class BudgetsOverviewDTO(BaseModel):
    month: int
    year: int
    total_budgeted: float
    total_spent: float
    overall_percentage: float
    budgets: List[BudgetStatusItemDTO]
