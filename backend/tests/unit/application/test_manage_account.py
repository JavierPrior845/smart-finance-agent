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

@pytest.mark.asyncio
async def test_transfer_funds():
    repo = MockAccountRepository()
    use_case = ManageAccountUseCase(repo)
    
    acc1 = await use_case.create_account("Cuenta 1", "BANK", initial_balance=500.0)
    acc2 = await use_case.create_account("Cuenta 2", "BANK", initial_balance=100.0)
    
    updated_dest = await use_case.transfer_funds(acc1.id, acc2.id, amount=200.0)
    assert updated_dest.current_balance == 300.0
    
    updated_src = await repo.get_by_id(acc1.id)
    assert updated_src.current_balance == 300.0

@pytest.mark.asyncio
async def test_adjust_balance():
    repo = MockAccountRepository()
    use_case = ManageAccountUseCase(repo)
    
    acc = await use_case.create_account("Cuenta 1", "BANK", initial_balance=500.0)
    
    # Mode SET
    res1 = await use_case.adjust_balance(acc.id, amount=600.0, mode="SET")
    assert res1.current_balance == 600.0
    
    # Mode ADD
    res2 = await use_case.adjust_balance(acc.id, amount=50.0, mode="ADD")
    assert res2.current_balance == 650.0
    
    # Mode SUBTRACT
    res3 = await use_case.adjust_balance(acc.id, amount=100.0, mode="SUBTRACT")
    assert res3.current_balance == 550.0
