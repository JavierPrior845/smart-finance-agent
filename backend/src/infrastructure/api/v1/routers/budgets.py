from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.infrastructure.api.dependencies import get_manage_budget_use_case
from src.application.use_cases.manage_budget import ManageBudgetUseCase
from src.infrastructure.api.v1.schemas.budget import BudgetCreate, BudgetResponse, BudgetProgressResponse

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("", response_model=List[BudgetProgressResponse])
async def list_budgets(
    month: int,
    year: int,
    use_case: ManageBudgetUseCase = Depends(get_manage_budget_use_case)
):
    """Consult limits and consumed progress per category for a specific month/year."""
    return await use_case.get_budget_progress_for_month(month, year)

@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_budget(
    data: BudgetCreate,
    use_case: ManageBudgetUseCase = Depends(get_manage_budget_use_case)
):
    """Establish or update a monthly limit for a category."""
    try:
        budget = await use_case.set_monthly_budget(
            category_id=data.category_id,
            limit=data.monthly_limit,
            month=data.period_month,
            year=data.period_year
        )
        return budget
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
