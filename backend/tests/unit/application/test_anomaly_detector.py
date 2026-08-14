import pytest
from uuid import UUID, uuid4
from datetime import datetime, timezone
from src.application.services.anomaly_detector import BudgetAnomalyDetector
from src.application.use_cases.create_transaction import CreateTransactionUseCase
from src.domain.models.account import Account
from src.domain.models.transaction import Transaction

class MockTransactionRepository:
    def __init__(self):
        self.transactions = []

    async def get_all_paginated(
        self, 
        limit: int = 20, 
        offset: int = 0, 
        search: str | None = None,
        category_id: UUID | None = None,
        source: str | None = None
    ) -> tuple[list[Transaction], int]:
        # Filter by category_id if provided
        items = self.transactions
        if category_id:
            items = [t for t in items if t.category_id == category_id]
        return items[:limit], len(items)

    async def save(self, transaction: Transaction) -> Transaction:
        self.transactions.append(transaction)
        return transaction


@pytest.mark.asyncio
async def test_anomaly_detector_insufficient_data():
    repo = MockTransactionRepository()
    detector = BudgetAnomalyDetector(repo)
    category_id = uuid4()
    
    # Empty repo, should return False
    is_anomalous, reason = await detector.evaluate(category_id, 100.0)
    assert is_anomalous is False
    assert reason is None

    # Only 4 transactions, still insufficient (needs >= 5)
    for i in range(4):
        tx = Transaction(
            account_id=uuid4(),
            type="EXPENSE",
            amount=-20.0,
            description="Expense",
            category_id=category_id,
            source="manual",
            status="confirmed",
            transaction_date=datetime.now(timezone.utc)
        )
        await repo.save(tx)

    is_anomalous, reason = await detector.evaluate(category_id, 100.0)
    assert is_anomalous is False
    assert reason is None


@pytest.mark.asyncio
async def test_anomaly_detector_typical_vs_outlier():
    repo = MockTransactionRepository()
    detector = BudgetAnomalyDetector(repo)
    category_id = uuid4()

    # Add 5 normal transactions of around 20-30 EUR
    normal_amounts = [20.0, 22.0, 25.0, 28.0, 30.0]
    for amt in normal_amounts:
        tx = Transaction(
            account_id=uuid4(),
            type="EXPENSE",
            amount=-amt,
            description="Expense",
            category_id=category_id,
            source="manual",
            status="confirmed",
            transaction_date=datetime.now(timezone.utc)
        )
        await repo.save(tx)

    # IQR calculation for [20, 22, 25, 28, 30]:
    # Sorted: 20, 22, 25, 28, 30
    # Median: 25
    # Q1: 22, Q3: 28. IQR = 6. Tukey fence: 28 + 1.5 * 6 = 37.0.

    # 1. Typical expense (35 EUR) <= Tukey upper fence (37.0 EUR) -> False
    is_anomalous, reason = await detector.evaluate(category_id, 35.0)
    assert is_anomalous is False
    assert reason is None

    # 2. Outlier expense (150 EUR) > Tukey upper fence (37.0 EUR) -> True
    is_anomalous, reason = await detector.evaluate(category_id, 150.0)
    assert is_anomalous is True
    assert "supera el límite superior de Tukey" in reason


class MockAccountRepository:
    def __init__(self):
        self.accounts = {}

    async def get_by_id(self, account_id: UUID) -> Account | None:
        return self.accounts.get(account_id)

    async def update(self, account: Account) -> Account:
        self.accounts[account.id] = account
        return account


class MockCategoryRepository:
    async def get_all(self) -> list:
        return []


@pytest.mark.asyncio
async def test_create_transaction_integration_with_anomaly():
    tx_repo = MockTransactionRepository()
    acc_repo = MockAccountRepository()
    cat_repo = MockCategoryRepository()
    
    account = Account(name="Bank", account_type="BANK", current_balance=1000.0)
    acc_repo.accounts[account.id] = account
    
    category_id = uuid4()
    
    # Seed 5 normal expenses
    for amt in [10.0, 12.0, 11.0, 14.0, 13.0]:
        tx = Transaction(
            account_id=account.id,
            type="EXPENSE",
            amount=-amt,
            description="Grocery",
            category_id=category_id,
            source="manual",
            status="confirmed",
            transaction_date=datetime.now(timezone.utc)
        )
        await tx_repo.save(tx)

    # Create transaction use case
    use_case = CreateTransactionUseCase(tx_repo, acc_repo, cat_repo)
    
    # 1. Create a normal expense (12 EUR) -> should not be marked as anomalous
    txn_normal = await use_case.execute(
        amount=12.0,
        description="Normal Grocery",
        source="manual",
        transaction_date=datetime.now(timezone.utc),
        account_id=account.id,
        transaction_type="EXPENSE",
        category_id=category_id
    )
    assert txn_normal.is_anomalous is False

    # 2. Create an anomalous expense (150 EUR) -> should be marked as anomalous
    txn_anomaly = await use_case.execute(
        amount=150.0,
        description="Huge Grocery",
        source="manual",
        transaction_date=datetime.now(timezone.utc),
        account_id=account.id,
        transaction_type="EXPENSE",
        category_id=category_id
    )
    assert txn_anomaly.is_anomalous is True
