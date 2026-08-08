import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone
from src.main import app
from src.infrastructure.api.dependencies import get_create_transaction_use_case
from src.domain.models.transaction import Transaction

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
