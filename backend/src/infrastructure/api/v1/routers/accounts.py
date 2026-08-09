from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.infrastructure.api.dependencies import get_manage_account_use_case
from src.application.use_cases.manage_account import ManageAccountUseCase
from src.infrastructure.api.v1.schemas.account import AccountCreate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("", response_model=List[AccountResponse])
async def list_accounts(
    use_case: ManageAccountUseCase = Depends(get_manage_account_use_case)
):
    """List all active accounts and their balances."""
    accounts = await use_case.get_all_active_accounts()
    return accounts

@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    use_case: ManageAccountUseCase = Depends(get_manage_account_use_case)
):
    """Create a new financial account."""
    account = await use_case.create_account(
        name=data.name,
        account_type=data.account_type,
        initial_balance=data.initial_balance,
        is_main=data.is_main,
        currency=data.currency
    )
    return account

@router.delete("/{account_id}", response_model=AccountResponse)
async def deactivate_account(
    account_id: UUID,
    use_case: ManageAccountUseCase = Depends(get_manage_account_use_case)
):
    """Deactivate an account."""
    try:
        account = await use_case.disable_account(account_id)
        return account
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
