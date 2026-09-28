from typing import Optional, List
from pydantic import BaseModel

class AccountDTO(BaseModel):
    id: str
    name: str
    type: str
    balance: float
    currency: str = "EUR"
    is_active: bool = True

class AccountsSummaryDTO(BaseModel):
    total_balance: float
    currency: str = "EUR"
    accounts_count: int
    accounts: List[AccountDTO]
