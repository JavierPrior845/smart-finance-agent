from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.infrastructure.api.dependencies import get_manage_category_use_case
from src.application.use_cases.manage_category import ManageCategoryUseCase
from src.infrastructure.api.v1.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    use_case: ManageCategoryUseCase = Depends(get_manage_category_use_case)
):
    """List all categories and subcategories."""
    return await use_case.get_all_categories()

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    use_case: ManageCategoryUseCase = Depends(get_manage_category_use_case)
):
    """Create a new category."""
    try:
        category = await use_case.create_category(
            name=data.name,
            parent_id=data.parent_id,
            icon=data.icon,
            color=data.color,
            is_budgetable=data.is_budgetable
        )
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
