from uuid import UUID, uuid4
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

TransactionType = Literal['EXPENSE', 'INCOME', 'TRANSFER', 'BALANCE_ADJUSTMENT', 'INVESTMENT_OUTFLOW', 'INVESTMENT_INFLOW']

class Transaction(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    account_id: UUID
    destination_account_id: UUID | None = None
    type: TransactionType = 'EXPENSE'
    amount: float
    currency: str = "EUR"
    raw_text: str | None = None
    description: str
    category_id: UUID | None = None
    source: str
    status: str = 'confirmed'
    is_recurring: bool = False
    is_anomalous: bool = False
    transaction_date: datetime
    embedding: list[float] | None = None
    created_at: datetime | None = None
