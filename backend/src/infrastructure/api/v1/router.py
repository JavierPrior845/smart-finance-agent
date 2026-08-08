from fastapi import APIRouter

from .routers.accounts import router as accounts_router
from .routers.categories import router as categories_router
from .routers.budgets import router as budgets_router
from .routers.transactions import router as transactions_router

api_router = APIRouter()

api_router.include_router(accounts_router)
api_router.include_router(categories_router)
api_router.include_router(budgets_router)
api_router.include_router(transactions_router)
