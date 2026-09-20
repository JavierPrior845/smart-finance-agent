from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class InvestmentCreate(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Bitcoin"})
    ticker: Optional[str] = Field(None, json_schema_extra={"example": "BTC-USD"})
    asset_type: str = Field(..., json_schema_extra={"example": "CRIPTO"})
    broker: str = Field(..., json_schema_extra={"example": "Binance"})
    invested_amount: float = Field(..., json_schema_extra={"example": 1000.0})
    units_qty: Optional[float] = Field(None, json_schema_extra={"example": 0.015})
    average_buy_price: Optional[float] = Field(None, json_schema_extra={"example": 66000.0})
    source_account_id: Optional[UUID] = None

class InvestmentBuyMore(BaseModel):
    units: float = Field(..., gt=0, json_schema_extra={"example": 0.01})
    unit_price: float = Field(..., gt=0, json_schema_extra={"example": 67000.0})
    notes: Optional[str] = None
    source_account_id: Optional[UUID] = None

class InvestmentSellPartial(BaseModel):
    units: float = Field(..., gt=0, json_schema_extra={"example": 0.005})
    unit_price: float = Field(..., gt=0, json_schema_extra={"example": 70000.0})
    notes: Optional[str] = None
    destination_account_id: Optional[UUID] = None

class InvestmentClose(BaseModel):
    withdrawn_amount: float = Field(..., json_schema_extra={"example": 1200.50})

class InvestmentMovementResponse(BaseModel):
    id: UUID
    asset_id: UUID
    movement_type: str
    amount: float
    units: Optional[float] = None
    unit_price: Optional[float] = None
    movement_date: datetime
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)
