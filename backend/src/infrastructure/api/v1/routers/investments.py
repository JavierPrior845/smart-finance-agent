from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Optional
from uuid import UUID
import asyncio
import yfinance as yf
from pydantic import BaseModel
from src.infrastructure.api.dependencies import get_sync_investments_use_case, get_manage_investment_use_case, get_investment_repo
from src.application.use_cases.sync_investments import SyncInvestmentsUseCase
from src.application.use_cases.manage_investment import ManageInvestmentUseCase
from src.application.ports.investment_repository import InvestmentRepository
from src.infrastructure.api.v1.schemas.investment import (
    InvestmentCreate, 
    InvestmentResponse, 
    InvestmentClose,
    InvestmentBuyMore,
    InvestmentSellPartial,
    InvestmentMovementResponse
)

router = APIRouter(prefix="/investments", tags=["Investments"])

@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_investments(
    use_case: SyncInvestmentsUseCase = Depends(get_sync_investments_use_case)
):
    """
    Synchronizes investment asset prices using yfinance.
    Fills in any missing historical snapshots up to today.
    """
    await use_case.execute()
    return {"message": "Investments synced successfully"}

class InvestmentQuoteResponse(BaseModel):
    ticker: str
    price: Optional[float] = None
    currency: Optional[str] = "EUR"
    name: Optional[str] = None

@router.get("/quote", response_model=InvestmentQuoteResponse)
async def get_investment_quote(ticker: str):
    """
    Fetches real-time / current market quote and metadata for a ticker using yfinance.
    Useful for auto-filling current price and computing units/invested amounts.
    """
    clean_ticker = ticker.strip().upper()
    loop = asyncio.get_running_loop()
    try:
        def fetch():
            t = yf.Ticker(clean_ticker)
            price = t.fast_info.get("lastPrice") or getattr(t.fast_info, "last_price", None)
            curr = getattr(t.fast_info, "currency", "EUR")
            short_name = t.info.get("shortName") or t.info.get("name") or clean_ticker
            return {
                "ticker": clean_ticker,
                "price": float(price) if price is not None else None,
                "currency": curr,
                "name": short_name
            }
        data = await loop.run_in_executor(None, fetch)
        return InvestmentQuoteResponse(**data)
    except Exception as e:
        return InvestmentQuoteResponse(ticker=clean_ticker, price=None, currency="EUR", name=clean_ticker)

@router.get("", response_model=List[InvestmentResponse])
async def get_investments(
    repo: InvestmentRepository = Depends(get_investment_repo)
):
    """List all active investment assets."""
    assets = await repo.get_all_assets()
    return assets

@router.post("", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
async def create_investment(
    data: InvestmentCreate,
    use_case: ManageInvestmentUseCase = Depends(get_manage_investment_use_case)
):
    """Create a new investment asset and its initial buy movement."""
    asset = await use_case.create_investment(data)
    return asset

@router.post("/{asset_id}/buy", response_model=InvestmentResponse, status_code=status.HTTP_200_OK)
async def buy_more_investment(
    asset_id: UUID,
    data: InvestmentBuyMore,
    use_case: ManageInvestmentUseCase = Depends(get_manage_investment_use_case)
):
    """Register an additional purchase (DCA) of an investment asset."""
    try:
        asset = await use_case.buy_more(asset_id, data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{asset_id}/sell", response_model=InvestmentResponse, status_code=status.HTTP_200_OK)
async def sell_investment_units(
    asset_id: UUID,
    data: InvestmentSellPartial,
    use_case: ManageInvestmentUseCase = Depends(get_manage_investment_use_case)
):
    """Register a partial or total sale of units from an investment position."""
    try:
        asset = await use_case.sell_units(asset_id, data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{asset_id}/close", response_model=InvestmentResponse, status_code=status.HTTP_200_OK)
async def close_investment(
    asset_id: UUID,
    data: InvestmentClose,
    use_case: ManageInvestmentUseCase = Depends(get_manage_investment_use_case)
):
    """Closes an open investment position completely."""
    try:
        asset = await use_case.close_investment(asset_id, data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{asset_id}/movements", response_model=List[InvestmentMovementResponse])
async def get_investment_movements(
    asset_id: UUID,
    repo: InvestmentRepository = Depends(get_investment_repo)
):
    """Retrieve the movement timeline (buys and sells) for a specific asset."""
    movements = await repo.get_movements_by_asset(asset_id)
    return movements
