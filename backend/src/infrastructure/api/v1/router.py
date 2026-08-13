from fastapi import APIRouter

from .routers.accounts import router as accounts_router
from .routers.categories import router as categories_router
from .routers.budgets import router as budgets_router
from .routers.transactions import router as transactions_router
from .routers.analytics import router as analytics_router
from .routers.settings import router as settings_router
from .routers.investments import router as investments_router

api_router = APIRouter()

api_router.include_router(accounts_router)
api_router.include_router(categories_router)
api_router.include_router(budgets_router)
api_router.include_router(transactions_router)
api_router.include_router(analytics_router)
api_router.include_router(settings_router)
api_router.include_router(investments_router)

@api_router.get("/status")
async def status_check():
    return {
        "api_version": "v1",
        "status": "active"
    }

