from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from src.domain.models.transaction import TransactionType

class TransactionCreate(BaseModel):
    account_id: Optional[UUID] = None
    destination_account_id: Optional[UUID] = None
    type: TransactionType = 'EXPENSE'
    amount: float
    currency: str = "EUR"
    description: str
    category_id: Optional[UUID] = None
    source: str = "manual"
    transaction_date: datetime

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    transaction_date: Optional[datetime] = None

class TransactionResponse(TransactionCreate):
    id: UUID

class PaginatedTransactionsResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    status: str
    is_recurring: bool
    is_anomalous: bool

    class Config:
        from_attributes = True
