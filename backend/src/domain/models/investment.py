from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class InvestmentAsset:
    id: UUID
    name: str
    asset_type: str
    broker: str
    entry_date: datetime
    invested_amount: float
    status: str
    ticker: Optional[str] = None
    units_qty: Optional[float] = None
    average_buy_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    withdrawn_amount: float = 0.00
    realized_pnl: float = 0.00
    source_account_id: Optional[UUID] = None
    created_at: Optional[datetime] = None

@dataclass
class InvestmentSnapshot:
    id: UUID
    asset_id: UUID
    snapshot_date: datetime
    price: float
    total_value: float
    created_at: Optional[datetime] = None

@dataclass
class InvestmentMovement:
    id: UUID
    asset_id: UUID
    movement_type: str
    amount: float
    movement_date: datetime
    transaction_id: Optional[UUID] = None
    units: Optional[float] = None
    unit_price: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
