from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List

from src.infrastructure.adapters.db.session import get_db_session
from src.infrastructure.adapters.db.repositories.analytics_repository import AnalyticsRepository
from src.infrastructure.api.v1.schemas.analytics import KPIsResponse, DistributionResponse, CashflowResponse, PacingResponse, NetWorthHistoryResponse
from src.infrastructure.api.dependencies import get_transaction_repo
from src.application.ports.transaction_repository import TransactionRepository
from src.infrastructure.api.v1.schemas.transaction import TransactionResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/kpis", response_model=KPIsResponse)
async def get_dashboard_kpis(db: AsyncSession = Depends(get_db_session)):
    repo = AnalyticsRepository(db)
    return await repo.get_kpis()

@router.get("/distribution", response_model=DistributionResponse)
async def get_dashboard_distribution(db: AsyncSession = Depends(get_db_session)):
    repo = AnalyticsRepository(db)
    now = datetime.now()
    # By default, last 30 days
    start_date = now - timedelta(days=30)
    data = await repo.get_expense_distribution(start_date=start_date, end_date=now)
    return DistributionResponse(data=data)

@router.get("/cashflow", response_model=CashflowResponse)
async def get_dashboard_cashflow(db: AsyncSession = Depends(get_db_session)):
    repo = AnalyticsRepository(db)
    data = await repo.get_historical_cashflow(months=6)
    return CashflowResponse(data=data)

@router.get("/pacing", response_model=PacingResponse)
async def get_dashboard_pacing(db: AsyncSession = Depends(get_db_session)):
    repo = AnalyticsRepository(db)
    data = await repo.get_pacing()
    return PacingResponse(data=data)

@router.get("/networth", response_model=NetWorthHistoryResponse)
async def get_dashboard_networth(db: AsyncSession = Depends(get_db_session)):
    repo = AnalyticsRepository(db)
    data = await repo.get_networth_history(months=6)
    return NetWorthHistoryResponse(data=data)

@router.get("/anomalies", response_model=List[TransactionResponse])
async def get_dashboard_anomalies(
    limit: int = Query(10, ge=1, le=100),
    repo: TransactionRepository = Depends(get_transaction_repo)
):
    """Retrieve recent anomalous transactions."""
    return await repo.get_anomalous(limit=limit)
