from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.infrastructure.api.dependencies import get_manage_account_use_case
from src.application.use_cases.manage_account import ManageAccountUseCase
from src.infrastructure.api.v1.schemas.account import (
    AccountCreate, 
    AccountResponse, 
    AccountTransfer, 
    AccountBalanceAdjust
)

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
    """Create a new financial account (with optional funding from another account)."""
    account = await use_case.create_account(
        name=data.name,
        account_type=data.account_type,
        initial_balance=data.initial_balance,
        is_main=data.is_main,
        currency=data.currency,
        source_account_id=data.source_account_id
    )
    return account

@router.post("/transfer", response_model=AccountResponse)
async def transfer_between_accounts(
    data: AccountTransfer,
    use_case: ManageAccountUseCase = Depends(get_manage_account_use_case)
):
    """Transfer funds neutrally between two accounts."""
    try:
        dest_account = await use_case.transfer_funds(
            source_account_id=data.source_account_id,
            destination_account_id=data.destination_account_id,
            amount=data.amount,
            description=data.description or "Traspaso entre cuentas"
        )
        return dest_account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{account_id}/balance", response_model=AccountResponse)
async def adjust_account_balance(
    account_id: UUID,
    data: AccountBalanceAdjust,
    use_case: ManageAccountUseCase = Depends(get_manage_account_use_case)
):
    """Directly adjust, add, or subtract balance from an account."""
    try:
        updated = await use_case.adjust_balance(
            account_id=account_id,
            amount=data.amount,
            mode=data.mode,
            description=data.description or "Ajuste de saldo"
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
