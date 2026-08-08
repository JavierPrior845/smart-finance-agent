from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.infrastructure.api.dependencies import get_create_transaction_use_case
from src.application.use_cases.create_transaction import CreateTransactionUseCase
from src.infrastructure.api.v1.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    use_case: CreateTransactionUseCase = Depends(get_create_transaction_use_case)
):
    """Create a manual transaction and update account balances automatically."""
    try:
        transaction = await use_case.execute(
            amount=data.amount,
            description=data.description,
            source=data.source,
            transaction_date=data.transaction_date,
            account_id=data.account_id,
            transaction_type=data.type,
            destination_account_id=data.destination_account_id,
            category_id=data.category_id
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
