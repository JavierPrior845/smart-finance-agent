import pytest
from uuid import UUID, uuid4
from src.application.use_cases.manage_account import ManageAccountUseCase
from src.domain.models.account import Account

class MockAccountRepository:
    def __init__(self):
        self.db = {}

    async def get_by_id(self, account_id: UUID) -> Account | None:
        return self.db.get(account_id)

    async def get_all_active(self) -> list[Account]:
        return [acc for acc in self.db.values() if acc.is_active]

    async def save(self, account: Account) -> Account:
        self.db[account.id] = account
        return account

    async def update(self, account: Account) -> Account:
        self.db[account.id] = account
        return account

@pytest.mark.asyncio
async def test_create_account():
    repo = MockAccountRepository()
    use_case = ManageAccountUseCase(repo)
    
    account = await use_case.create_account(
        name="Mock Bank",
        account_type="BANK_ACCOUNT",
        initial_balance=500.0,
        currency="EUR"
    )
    
    assert account.id in repo.db
    assert account.name == "Mock Bank"
    assert account.initial_balance == 500.0
    assert account.current_balance == 500.0

@pytest.mark.asyncio
async def test_disable_account():
    repo = MockAccountRepository()
    use_case = ManageAccountUseCase(repo)
    
    account = await use_case.create_account("Test", "BANK")
    assert account.is_active is True
    
    updated = await use_case.disable_account(account.id)
    assert updated.is_active is False
    
    active_accounts = await use_case.get_all_active_accounts()
    assert len(active_accounts) == 0
