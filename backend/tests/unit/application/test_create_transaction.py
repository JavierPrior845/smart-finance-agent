import pytest
from uuid import UUID, uuid4
from datetime import datetime, timezone
from src.application.use_cases.create_transaction import CreateTransactionUseCase
from src.domain.models.account import Account
from src.domain.models.transaction import Transaction

class MockAccountRepository:
    def __init__(self):
        self.db = {}
        self.main_account = None

    async def get_by_id(self, account_id: UUID) -> Account | None:
        return self.db.get(account_id)
        
    async def get_main_account(self) -> Account | None:
        return self.main_account

    async def save(self, account: Account) -> Account:
        self.db[account.id] = account
        if account.is_main:
            self.main_account = account
        return account

    async def update(self, account: Account) -> Account:
        self.db[account.id] = account
        return account

class MockTransactionRepository:
    def __init__(self):
        self.db = {}

    async def save(self, transaction: Transaction) -> Transaction:
        self.db[transaction.id] = transaction
        return transaction

@pytest.mark.asyncio
async def test_create_expense_deducts_balance():
    account_repo = MockAccountRepository()
    transaction_repo = MockTransactionRepository()
    use_case = CreateTransactionUseCase(transaction_repo, account_repo)
    
    # Setup account
    account = Account(name="Test", account_type="BANK", initial_balance=100.0, current_balance=100.0)
    await account_repo.save(account)
    
    # Execute transaction
    txn = await use_case.execute(
        amount=20.0,
        description="Coffee",
        source="manual",
        transaction_date=datetime.now(timezone.utc),
        account_id=account.id,
        transaction_type="EXPENSE"
    )
    
    # Assert transaction created
    assert txn.id in transaction_repo.db
    assert txn.amount == 20.0
    
    # Assert balance deducted
    updated_acc = await account_repo.get_by_id(account.id)
    assert updated_acc.current_balance == 80.0

@pytest.mark.asyncio
async def test_create_transfer_adjusts_both_balances():
    account_repo = MockAccountRepository()
    transaction_repo = MockTransactionRepository()
    use_case = CreateTransactionUseCase(transaction_repo, account_repo)
    
    acc_from = Account(name="From", account_type="BANK", current_balance=100.0)
    acc_to = Account(name="To", account_type="BANK", current_balance=50.0)
    await account_repo.save(acc_from)
    await account_repo.save(acc_to)
    
    await use_case.execute(
        amount=30.0,
        description="Transfer",
        source="manual",
        transaction_date=datetime.now(timezone.utc),
        account_id=acc_from.id,
        transaction_type="TRANSFER",
        destination_account_id=acc_to.id
    )
    
    assert acc_from.current_balance == 70.0
    assert acc_to.current_balance == 80.0
