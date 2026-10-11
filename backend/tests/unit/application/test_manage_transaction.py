import pytest
from uuid import uuid4
from datetime import datetime, timezone
from src.application.use_cases.manage_transaction import ManageTransactionUseCase
from src.domain.models.transaction import Transaction
from src.domain.models.account import Account

class MockTxRepo:
    def __init__(self):
        self.db = {}

    async def get_by_id(self, tx_id):
        return self.db.get(tx_id)

    async def update(self, tx):
        self.db[tx.id] = tx
        return tx

    async def delete(self, tx_id):
        if tx_id in self.db:
            del self.db[tx_id]

class MockAccRepo:
    def __init__(self):
        self.db = {}

    async def get_by_id(self, acc_id):
        return self.db.get(acc_id)

    async def update(self, acc):
        self.db[acc.id] = acc
        return acc

@pytest.mark.asyncio
async def test_update_expense_transaction_updates_account_balance():
    tx_repo = MockTxRepo()
    acc_repo = MockAccRepo()
    use_case = ManageTransactionUseCase(tx_repo, acc_repo, None)

    acc = Account(id=uuid4(), name="Bank", account_type="BANK", initial_balance=1000.0, current_balance=950.0)
    acc_repo.db[acc.id] = acc

    tx = Transaction(
        id=uuid4(),
        account_id=acc.id,
        type="EXPENSE",
        amount=-50.0,
        description="Dinner",
        source="MANUAL",
        transaction_date=datetime.now(timezone.utc)
    )
    tx_repo.db[tx.id] = tx

    # Update amount from 50 to 80 (should decrement account by additional 30 -> 920.0)
    updated_tx = await use_case.update_transaction(
        transaction_id=tx.id,
        amount=80.0,
        description="Dinner with drinks"
    )

    assert updated_tx.amount == -80.0
    assert updated_tx.description == "Dinner with drinks"
    assert acc.current_balance == 920.0

@pytest.mark.asyncio
async def test_delete_expense_reverts_account_balance():
    tx_repo = MockTxRepo()
    acc_repo = MockAccRepo()
    use_case = ManageTransactionUseCase(tx_repo, acc_repo, None)

    acc = Account(id=uuid4(), name="Bank", account_type="BANK", initial_balance=1000.0, current_balance=950.0)
    acc_repo.db[acc.id] = acc

    tx = Transaction(
        id=uuid4(),
        account_id=acc.id,
        type="EXPENSE",
        amount=-50.0,
        description="Dinner",
        source="MANUAL",
        transaction_date=datetime.now(timezone.utc)
    )
    tx_repo.db[tx.id] = tx

    await use_case.delete_transaction(tx.id)

    assert tx.id not in tx_repo.db
    # Account should be back to 1000.0
    assert acc.current_balance == 1000.0

@pytest.mark.asyncio
async def test_cannot_update_or_delete_investment_transaction():
    tx_repo = MockTxRepo()
    acc_repo = MockAccRepo()
    use_case = ManageTransactionUseCase(tx_repo, acc_repo, None)

    tx = Transaction(
        id=uuid4(),
        account_id=uuid4(),
        type="INVESTMENT_OUTFLOW",
        amount=-500.0,
        description="Buy BTC",
        source="MANUAL",
        transaction_date=datetime.now(timezone.utc)
    )
    tx_repo.db[tx.id] = tx

    with pytest.raises(ValueError, match="No se permite editar"):
        await use_case.update_transaction(tx.id, amount=600.0)

    with pytest.raises(ValueError, match="No se permite eliminar"):
        await use_case.delete_transaction(tx.id)
