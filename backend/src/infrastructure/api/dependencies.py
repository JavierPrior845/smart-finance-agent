from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.adapters.db.session import get_db_session

from src.infrastructure.adapters.db.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.adapters.db.repositories.category_repository import SQLAlchemyCategoryRepository
from src.infrastructure.adapters.db.repositories.budget_repository import SQLAlchemyBudgetRepository
from src.infrastructure.adapters.db.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.adapters.db.repositories.investment_repository import SQLAlchemyInvestmentRepository

from src.application.use_cases.manage_account import ManageAccountUseCase
from src.application.use_cases.manage_category import ManageCategoryUseCase
from src.application.use_cases.manage_budget import ManageBudgetUseCase
from src.application.use_cases.create_transaction import CreateTransactionUseCase
from src.application.use_cases.sync_investments import SyncInvestmentsUseCase
from src.application.use_cases.manage_investment import ManageInvestmentUseCase


def get_account_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyAccountRepository:
    return SQLAlchemyAccountRepository(session)

def get_category_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyCategoryRepository:
    return SQLAlchemyCategoryRepository(session)

def get_transaction_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyTransactionRepository:
    return SQLAlchemyTransactionRepository(session)

def get_investment_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyInvestmentRepository:
    return SQLAlchemyInvestmentRepository(session)

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

def get_sync_investments_use_case(
    investment_repo: SQLAlchemyInvestmentRepository = Depends(get_investment_repo)
) -> SyncInvestmentsUseCase:
    return SyncInvestmentsUseCase(investment_repo)

def get_manage_investment_use_case(
    investment_repo: SQLAlchemyInvestmentRepository = Depends(get_investment_repo),
    create_transaction_use_case: CreateTransactionUseCase = Depends(get_create_transaction_use_case)
) -> ManageInvestmentUseCase:
    return ManageInvestmentUseCase(investment_repo, create_transaction_use_case)

from src.infrastructure.adapters.db.repositories.merchant_rule_repository import SQLAlchemyMerchantRuleRepository
from src.application.use_cases.manage_merchant_rules import ManageMerchantRulesUseCase
from src.infrastructure.adapters.db.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.adapters.auth.security import decode_access_token
from src.infrastructure.adapters.db.models.user import UserORM
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_merchant_rule_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyMerchantRuleRepository:
    return SQLAlchemyMerchantRuleRepository(session)

def get_manage_merchant_rules_use_case(
    repo: SQLAlchemyMerchantRuleRepository = Depends(get_merchant_rule_repo)
) -> ManageMerchantRulesUseCase:
    return ManageMerchantRulesUseCase(repo)

def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo)
) -> UserORM:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Token no proporcionado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuario inválido en el token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )
    return user
