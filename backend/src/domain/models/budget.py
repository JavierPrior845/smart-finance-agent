from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class Budget(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    category_id: UUID
    monthly_limit: float
    period_month: int
    period_year: int
