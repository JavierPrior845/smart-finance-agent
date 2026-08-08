from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.infrastructure.api.dependencies import get_db
from src.infrastructure.adapters.db.repositories.analytics_repository import AnalyticsRepository
from src.infrastructure.api.v1.schemas.analytics import KPIsResponse, DistributionResponse, CashflowResponse, PacingResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/kpis", response_model=KPIsResponse)
async def get_dashboard_kpis(db: AsyncSession = Depends(get_db)):
    repo = AnalyticsRepository(db)
    return await repo.get_kpis()

@router.get("/distribution", response_model=DistributionResponse)
async def get_dashboard_distribution(db: AsyncSession = Depends(get_db)):
    repo = AnalyticsRepository(db)
    now = datetime.now()
    # By default, last 30 days
    start_date = now - timedelta(days=30)
    data = await repo.get_expense_distribution(start_date=start_date, end_date=now)
    return DistributionResponse(data=data)

@router.get("/cashflow", response_model=CashflowResponse)
async def get_dashboard_cashflow(db: AsyncSession = Depends(get_db)):
    repo = AnalyticsRepository(db)
    data = await repo.get_historical_cashflow(months=6)
    return CashflowResponse(data=data)

@router.get("/pacing", response_model=PacingResponse)
async def get_dashboard_pacing(db: AsyncSession = Depends(get_db)):
    repo = AnalyticsRepository(db)
    data = await repo.get_pacing()
    return PacingResponse(data=data)
