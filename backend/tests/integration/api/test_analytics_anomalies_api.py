import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone
from src.main import app
from src.infrastructure.api.dependencies import get_transaction_repo
from src.domain.models.transaction import Transaction

class MockTransactionRepoAnomalies:
    def __init__(self):
        self.anomalous_id = uuid4()
        self.is_anomalous = True

    async def get_anomalous(self, limit=50):
        if self.is_anomalous:
            return [
                Transaction(
                    id=self.anomalous_id,
                    account_id=uuid4(),
                    type="EXPENSE",
                    amount=500.0,
                    description="Unusual Big Expense",
                    source="manual",
                    currency="EUR",
                    transaction_date=datetime.now(timezone.utc),
                    is_anomalous=True
                )
            ]
        return []

    async def dismiss_anomaly(self, transaction_id):
        if transaction_id == self.anomalous_id:
            self.is_anomalous = False
            return True
        return False

@pytest.fixture
def override_repo():
    mock_repo = MockTransactionRepoAnomalies()
    app.dependency_overrides[get_transaction_repo] = lambda: mock_repo
    yield mock_repo
    app.dependency_overrides.pop(get_transaction_repo, None)

@pytest.mark.asyncio
async def test_get_and_dismiss_anomalies(async_client: AsyncClient, override_repo):
    # 1. Fetch anomalies - should contain 1 item
    res = await async_client.get("/api/v1/analytics/anomalies")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["id"] == str(override_repo.anomalous_id)

    # 2. Dismiss anomaly via DELETE
    dismiss_res = await async_client.delete(f"/api/v1/analytics/anomalies/{override_repo.anomalous_id}")
    assert dismiss_res.status_code == 200
    assert dismiss_res.json()["status"] == "success"

    # 3. Fetch anomalies again - should now be empty
    res2 = await async_client.get("/api/v1/analytics/anomalies")
    assert res2.status_code == 200
    assert len(res2.json()) == 0

@pytest.mark.asyncio
async def test_dismiss_nonexistent_anomaly(async_client: AsyncClient, override_repo):
    random_id = uuid4()
    res = await async_client.delete(f"/api/v1/analytics/anomalies/{random_id}")
    assert res.status_code == 404
