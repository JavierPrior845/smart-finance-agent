import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone
from src.main import app
from src.infrastructure.api.dependencies import get_manage_merchant_rules_use_case
from src.domain.models.merchant_rule import MerchantRule

class MockManageMerchantRulesUseCase:
    def __init__(self):
        self.rules = []

    async def get_all_rules(self):
        return self.rules

    async def create_rule(self, pattern, category_id, priority):
        rule = MerchantRule(
            id=uuid4(),
            pattern=pattern,
            category_id=category_id,
            priority=priority,
            created_at=datetime.now(timezone.utc)
        )
        self.rules.append(rule)
        return rule

    async def delete_rule(self, rule_id):
        self.rules = [r for r in self.rules if r.id != rule_id]

mock_use_case = MockManageMerchantRulesUseCase()
app.dependency_overrides[get_manage_merchant_rules_use_case] = lambda: mock_use_case

@pytest.mark.asyncio
async def test_merchant_rules_crud(async_client: AsyncClient):
    # 1. List rules (should be empty initially)
    response = await async_client.get("/api/v1/settings/merchant-rules")
    assert response.status_code == 200
    assert response.json() == []

    # 2. Create a rule
    cat_id = str(uuid4())
    payload = {
        "pattern": "netflix",
        "category_id": cat_id,
        "priority": 5
    }
    response = await async_client.post("/api/v1/settings/merchant-rules", json=payload)
    assert response.status_code == 201
    created_rule = response.json()
    assert created_rule["pattern"] == "netflix"
    assert created_rule["category_id"] == cat_id
    assert created_rule["priority"] == 5
    assert "id" in created_rule

    # 3. List rules (should have 1 item)
    response = await async_client.get("/api/v1/settings/merchant-rules")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) == 1
    assert rules[0]["id"] == created_rule["id"]

    # 4. Delete the rule
    rule_id = created_rule["id"]
    response = await async_client.delete(f"/api/v1/settings/merchant-rules/{rule_id}")
    assert response.status_code == 204

    # 5. List rules (should be empty again)
    response = await async_client.get("/api/v1/settings/merchant-rules")
    assert response.status_code == 200
    assert response.json() == []
