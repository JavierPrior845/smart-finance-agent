from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from src.infrastructure.api.dependencies import get_create_transaction_use_case, get_transaction_repo
from src.application.ports.transaction_repository import TransactionRepository
from src.application.use_cases.create_transaction import CreateTransactionUseCase
from src.infrastructure.api.v1.schemas.transaction import TransactionCreate, TransactionResponse, PaginatedTransactionsResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=PaginatedTransactionsResponse)
async def list_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    source: Optional[str] = None,
    repo: TransactionRepository = Depends(get_transaction_repo)
):
    """Get a paginated list of transactions with optional filters."""
    items, total = await repo.get_all_paginated(
        limit=limit,
        offset=offset,
        search=search,
        category_id=category_id,
        source=source
    )
    return {"items": items, "total": total}

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
