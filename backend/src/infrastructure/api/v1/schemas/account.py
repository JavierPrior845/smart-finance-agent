from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class AccountCreate(BaseModel):
    name: str
    account_type: str
    currency: str = "EUR"
    initial_balance: float = 0.0
    is_main: bool = False

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    initial_balance: Optional[float] = None
    is_main: Optional[bool] = None

class AccountResponse(AccountCreate):
    id: UUID
    current_balance: float
    is_active: bool

    class Config:
        from_attributes = True
