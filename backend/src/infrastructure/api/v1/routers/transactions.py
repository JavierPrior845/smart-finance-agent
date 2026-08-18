from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
import json
from datetime import datetime, timezone

from src.infrastructure.adapters.redis.client import get_redis_pool
from src.infrastructure.api.dependencies import get_create_transaction_use_case, get_transaction_repo
from src.application.ports.transaction_repository import TransactionRepository
from src.application.use_cases.create_transaction import CreateTransactionUseCase
from src.infrastructure.api.v1.schemas.transaction import (
    TransactionCreate, 
    TransactionResponse, 
    PaginatedTransactionsResponse,
    PendingTransactionResponse,
    PendingTransactionConfirm
)

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

@router.get("/pending", response_model=List[PendingTransactionResponse])
async def list_pending_transactions():
    """Retrieve all pending transactions from Redis."""
    redis = await get_redis_pool()
    keys = await redis.keys("pending_tx:*")
    pending = []
    for key in keys:
        key_str = key.decode("utf-8") if isinstance(key, bytes) else key
        tx_id = key_str.split(":")[-1]
        val = await redis.get(key_str)
        if val:
            try:
                # val can be bytes or str
                val_str = val.decode("utf-8") if isinstance(val, bytes) else val
                data = json.loads(val_str)
                data["id"] = tx_id
                pending.append(data)
            except Exception:
                pass
    return pending

@router.post("/pending/{tx_id}/confirm", response_model=TransactionResponse)
async def confirm_pending_transaction(
    tx_id: str,
    data: PendingTransactionConfirm,
    use_case: CreateTransactionUseCase = Depends(get_create_transaction_use_case)
):
    """Confirm a pending transaction, saving it to the database."""
    redis = await get_redis_pool()
    key = f"pending_tx:{tx_id}"
    
    # Prevención de Race Conditions (Doble click en el frontend)
    lock_key = f"lock:{key}"
    acquired = await redis.set(lock_key, "locked", nx=True, ex=30)
    if not acquired:
        raise HTTPException(status_code=429, detail="La transacción ya se está procesando.")
    
    try:
        exists = await redis.exists(key)
        if not exists:
            raise HTTPException(status_code=404, detail="Borrador no encontrado o expirado.")
        
        transaction = await use_case.execute(
            amount=data.amount,
            description=data.description,
            source="telegram",
            transaction_date=datetime.now(timezone.utc),
            account_id=data.account_id,
            transaction_type=data.type,
            category_id=data.category_id
        )
        await redis.delete(key)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await redis.delete(lock_key)

@router.delete("/pending/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pending_transaction(tx_id: str):
    """Discard a pending transaction."""
    redis = await get_redis_pool()
    key = f"pending_tx:{tx_id}"
    exists = await redis.exists(key)
    if not exists:
        raise HTTPException(status_code=404, detail="Borrador no encontrado o expirado.")
    await redis.delete(key)
