from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.adapters.db.session import get_db_session

from src.infrastructure.adapters.db.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.adapters.db.repositories.category_repository import SQLAlchemyCategoryRepository
from src.infrastructure.adapters.db.repositories.budget_repository import SQLAlchemyBudgetRepository
from src.infrastructure.adapters.db.repositories.transaction_repository import SQLAlchemyTransactionRepository

from src.application.use_cases.manage_account import ManageAccountUseCase
from src.application.use_cases.manage_category import ManageCategoryUseCase
from src.application.use_cases.manage_budget import ManageBudgetUseCase
from src.application.use_cases.create_transaction import CreateTransactionUseCase


def get_account_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyAccountRepository:
    return SQLAlchemyAccountRepository(session)

def get_category_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyCategoryRepository:
    return SQLAlchemyCategoryRepository(session)

def get_transaction_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyTransactionRepository:
    return SQLAlchemyTransactionRepository(session)

def get_manage_account_use_case(repo: SQLAlchemyAccountRepository = Depends(get_account_repo)) -> ManageAccountUseCase:
    return ManageAccountUseCase(repo)

def get_manage_category_use_case(repo: SQLAlchemyCategoryRepository = Depends(get_category_repo)) -> ManageCategoryUseCase:
    return ManageCategoryUseCase(repo)

def get_manage_budget_use_case(
    session: AsyncSession = Depends(get_db_session)
) -> ManageBudgetUseCase:
    budget_repo = SQLAlchemyBudgetRepository(session)
    category_repo = SQLAlchemyCategoryRepository(session)
    return ManageBudgetUseCase(budget_repo, category_repo)

def get_create_transaction_use_case(
    transaction_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repo),
    account_repo: SQLAlchemyAccountRepository = Depends(get_account_repo),
    category_repo: SQLAlchemyCategoryRepository = Depends(get_category_repo)
) -> CreateTransactionUseCase:
    return CreateTransactionUseCase(transaction_repo, account_repo, category_repo)
