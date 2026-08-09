import pytest
from httpx import AsyncClient
from uuid import uuid4
from src.main import app
from src.infrastructure.api.dependencies import get_manage_account_use_case
from src.domain.models.account import Account

class MockManageAccountUseCase:
    async def get_all_active_accounts(self):
        return [
            Account(id=uuid4(), name="Mock 1", account_type="BANK", current_balance=100.0),
            Account(id=uuid4(), name="Mock 2", account_type="CASH", current_balance=50.0)
        ]

    async def create_account(self, name, account_type, initial_balance, is_main, currency):
        return Account(
            id=uuid4(),
            name=name,
            account_type=account_type,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            is_main=is_main,
            currency=currency
        )

app.dependency_overrides[get_manage_account_use_case] = lambda: MockManageAccountUseCase()

@pytest.mark.asyncio
async def test_get_accounts(async_client: AsyncClient):
    response = await async_client.get("/api/v1/accounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Mock 1"
    assert data[1]["name"] == "Mock 2"

@pytest.mark.asyncio
async def test_create_account_api(async_client: AsyncClient):
    payload = {
        "name": "New Bank",
        "account_type": "BANK",
        "currency": "EUR",
        "initial_balance": 1000.0,
        "is_main": True
    }
    response = await async_client.post("/api/v1/accounts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Bank"
    assert data["current_balance"] == 1000.0
    assert "id" in data
