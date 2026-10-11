from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class AccountCreate(BaseModel):
    name: str
    account_type: str
    currency: str = "EUR"
    initial_balance: float = 0.0
    is_main: bool = False
    source_account_id: Optional[UUID] = None

class AccountTransfer(BaseModel):
    source_account_id: UUID
    destination_account_id: UUID
    amount: float
    description: Optional[str] = "Traspaso entre cuentas"

class AccountBalanceAdjust(BaseModel):
    amount: float
    mode: str = "SET"  # "SET" (fijar saldo exacto), "ADD" (añadir saldo), "SUBTRACT" (quitar saldo)
    description: Optional[str] = "Ajuste de saldo"

class AccountResponse(AccountCreate):
    id: UUID
    current_balance: float
    is_active: bool

    class Config:
        from_attributes = True
