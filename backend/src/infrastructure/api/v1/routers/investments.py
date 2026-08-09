from fastapi import APIRouter, Depends, status
from src.infrastructure.api.dependencies import get_sync_investments_use_case
from src.application.use_cases.sync_investments import SyncInvestmentsUseCase

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
