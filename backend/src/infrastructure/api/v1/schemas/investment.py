from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class InvestmentCreate(BaseModel):
    name: str = Field(..., example="Bitcoin")
    ticker: Optional[str] = Field(None, example="BTC-USD")
    asset_type: str = Field(..., example="CRIPTO")
    broker: str = Field(..., example="Binance")
    invested_amount: float = Field(..., example=1000.0)
    units_qty: Optional[float] = Field(None, example=0.015)
    average_buy_price: Optional[float] = Field(None, example=66000.0)
    source_account_id: Optional[UUID] = None

class InvestmentClose(BaseModel):
    withdrawn_amount: float = Field(..., example=1200.50)

class InvestmentResponse(BaseModel):
    id: UUID
    name: str
    ticker: Optional[str]
    asset_type: str
    broker: str
    entry_date: datetime
    invested_amount: float
    units_qty: Optional[float]
    average_buy_price: Optional[float]
    status: str
    current_price: Optional[float] = None
    total_value: Optional[float] = None
    withdrawn_amount: float = 0.0
    realized_pnl: float = 0.0
    exit_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
