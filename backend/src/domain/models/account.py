from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

class Account(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    account_type: str
    currency: str = "EUR"
    initial_balance: float = 0.0
    current_balance: float = 0.0
    is_main: bool = False
    is_active: bool = True
    created_at: datetime | None = None
