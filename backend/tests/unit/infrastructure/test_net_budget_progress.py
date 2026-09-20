import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from src.infrastructure.adapters.db.models.base import Base
from src.infrastructure.adapters.db.models.category import CategoryORM
from src.infrastructure.adapters.db.models.account import AccountORM
from src.infrastructure.adapters.db.models.transaction import TransactionORM
from src.infrastructure.adapters.db.models.budget import BudgetORM
from src.infrastructure.adapters.db.repositories.budget_repository import SQLAlchemyBudgetRepository


@pytest.fixture
async def in_memory_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_net_expense_budget_progress(in_memory_db: AsyncSession):
    # 1. Create an Expense Category with default budget 200€
    category = CategoryORM(
        id=uuid.uuid4(),
        name="Restauración",
        type="EXPENSE",
        is_budgetable=True,
        default_budget_limit=200.0,
        is_active=True
    )
    in_memory_db.add(category)

    account = AccountORM(
        id=uuid.uuid4(),
        name="Cuenta Test",
        account_type="BANK",
        current_balance=1000.0,
        currency="EUR"
    )
    in_memory_db.add(account)
    await in_memory_db.flush()

    # 2. Add an EXPENSE transaction of 50.0 (-50.0 in DB)
    now = datetime(2026, 9, 5, 12, 0, 0, tzinfo=timezone.utc)
    t_expense = TransactionORM(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount=-50.0,
        type="EXPENSE",
        transaction_date=now,
        description="Cena con amigos",
        source="MANUAL"
    )
    in_memory_db.add(t_expense)

    # 3. Add an INCOME transaction (refund/Bizum) of 20.0 (+20.0 in DB) in the SAME category
    t_refund = TransactionORM(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount=20.0,
        type="INCOME",
        transaction_date=now,
        description="Bizum parte de la cena",
        source="MANUAL"
    )
    in_memory_db.add(t_refund)
    await in_memory_db.commit()

    repo = SQLAlchemyBudgetRepository(in_memory_db)
    progress = await repo.get_progress_for_month(9, 2026)

    assert len(progress) == 1
    item = progress[0]
    assert item["category_name"] == "Restauración"
    assert item["monthly_limit"] == 200.0
    # Net spent should be 50.0 - 20.0 = 30.0
    assert item["spent"] == 30.0


@pytest.mark.asyncio
async def test_net_income_goal_progress(in_memory_db: AsyncSession):
    # 1. Create an Income Category with goal 1000€
    category = CategoryORM(
        id=uuid.uuid4(),
        name="Desarrollo Web",
        type="INCOME",
        is_budgetable=True,
        default_budget_limit=1000.0,
        is_active=True
    )
    in_memory_db.add(category)

    account = AccountORM(
        id=uuid.uuid4(),
        name="Cuenta Test",
        account_type="BANK",
        current_balance=1000.0,
        currency="EUR"
    )
    in_memory_db.add(account)
    await in_memory_db.flush()

    now = datetime(2026, 9, 5, 12, 0, 0, tzinfo=timezone.utc)
    
    # 2. Income of 500.0
    t_income = TransactionORM(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount=500.0,
        type="INCOME",
        transaction_date=now,
        description="Pago Cliente Proyecto",
        source="MANUAL"
    )
    in_memory_db.add(t_income)

    # 3. Cost/Subcontract expense of 200.0 (-200.0 in DB)
    t_cost = TransactionORM(
        id=uuid.uuid4(),
        account_id=account.id,
        category_id=category.id,
        amount=-200.0,
        type="EXPENSE",
        transaction_date=now,
        description="Pago Colaborador Freelance",
        source="MANUAL"
    )
    in_memory_db.add(t_cost)
    await in_memory_db.commit()

    repo = SQLAlchemyBudgetRepository(in_memory_db)
    progress = await repo.get_progress_for_month(9, 2026)

    assert len(progress) == 1
    item = progress[0]
    assert item["category_name"] == "Desarrollo Web"
    assert item["monthly_limit"] == 1000.0
    # Net earned should be 500.0 - 200.0 = 300.0
    assert item["spent"] == 300.0
