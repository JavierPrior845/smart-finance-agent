import pytest
from httpx import AsyncClient
from uuid import uuid4
import json
from datetime import datetime, timezone
from src.main import app
from src.infrastructure.api.dependencies import get_create_transaction_use_case
from src.infrastructure.adapters.redis.client import get_redis_pool
from src.domain.models.transaction import Transaction

class MockRedis:
    def __init__(self):
        self.store = {}
    async def keys(self, pattern):
        return list(self.store.keys())
    async def get(self, key):
        return self.store.get(key)
    async def set(self, key, val, ex=None):
        self.store[key] = val
    async def delete(self, key):
        self.store.pop(key, None)
    async def exists(self, key):
        return key in self.store

mock_redis = MockRedis()

async def get_mock_redis_pool():
    return mock_redis

import src.infrastructure.adapters.redis.client
src.infrastructure.adapters.redis.client.get_redis_pool = get_mock_redis_pool

import src.infrastructure.api.v1.routers.transactions
src.infrastructure.api.v1.routers.transactions.get_redis_pool = get_mock_redis_pool

class MockCreateTransactionUseCase:
    async def execute(self, amount, description, source, transaction_date, account_id, transaction_type, destination_account_id=None, category_id=None):
        return Transaction(
            id=uuid4(),
            account_id=account_id or uuid4(),
            type=transaction_type,
            amount=amount,
            description=description,
            source=source,
            transaction_date=transaction_date,
            currency="EUR"
        )

app.dependency_overrides[get_create_transaction_use_case] = lambda: MockCreateTransactionUseCase()
app.dependency_overrides[get_redis_pool] = lambda: mock_redis

@pytest.mark.asyncio
async def test_create_transaction_api(async_client: AsyncClient):
    payload = {
        "account_id": str(uuid4()),
        "type": "EXPENSE",
        "amount": 45.5,
        "description": "Dinner",
        "source": "manual",
        "transaction_date": datetime.now(timezone.utc).isoformat()
    }
    response = await async_client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 45.5
    assert data["description"] == "Dinner"
    assert "id" in data

@pytest.mark.asyncio
async def test_pending_transactions_flow(async_client: AsyncClient):
    # 1. Preset a pending transaction in mock redis
    tx_id = "test-tx-123"
    draft_data = {
        "amount": 100.0,
        "currency": "EUR",
        "type": "INCOME",
        "description": "Salary draft",
        "account_name": "Cuenta Principal",
        "category_name": "Nómina",
        "raw_text": "Salary payment details..."
    }
    await mock_redis.set(f"pending_tx:{tx_id}", json.dumps(draft_data))

    # 2. Get pending list
    response = await async_client.get("/api/v1/transactions/pending")
    assert response.status_code == 200
    pending_list = response.json()
    assert len(pending_list) == 1
    assert pending_list[0]["id"] == tx_id
    assert pending_list[0]["description"] == "Salary draft"

    # 3. Confirm pending transaction
    confirm_payload = {
        "amount": 100.0,
        "type": "INCOME",
        "description": "Salary final",
        "account_id": str(uuid4()),
        "category_id": str(uuid4())
    }
    response = await async_client.post(f"/api/v1/transactions/pending/{tx_id}/confirm", json=confirm_payload)
    assert response.status_code == 200
    tx_res = response.json()
    assert tx_res["amount"] == 100.0
    assert tx_res["description"] == "Salary final"

    # 4. Check deleted from redis
    response = await async_client.get("/api/v1/transactions/pending")
    assert response.status_code == 200
    assert len(response.json()) == 0

