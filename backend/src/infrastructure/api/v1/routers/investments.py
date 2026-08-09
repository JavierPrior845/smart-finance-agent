from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from uuid import UUID
from src.infrastructure.api.dependencies import get_sync_investments_use_case, get_manage_investment_use_case, get_investment_repo
from src.application.use_cases.sync_investments import SyncInvestmentsUseCase
from src.application.use_cases.manage_investment import ManageInvestmentUseCase
from src.application.ports.investment_repository import InvestmentRepository
from src.infrastructure.api.v1.schemas.investment import InvestmentCreate, InvestmentResponse, InvestmentClose

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

@router.post("/{asset_id}/close", response_model=InvestmentResponse, status_code=status.HTTP_200_OK)
async def close_investment(
    asset_id: UUID,
    data: InvestmentClose,
    use_case: ManageInvestmentUseCase = Depends(get_manage_investment_use_case)
):
    """Closes an open investment position and registers the withdrawn amount."""
    try:
        asset = await use_case.close_investment(asset_id, data)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
