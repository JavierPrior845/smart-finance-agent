from fastapi import APIRouter, Depends

from src.infrastructure.api.dependencies import get_current_user
from .routers.accounts import router as accounts_router
from .routers.categories import router as categories_router
from .routers.budgets import router as budgets_router
from .routers.transactions import router as transactions_router
from .routers.analytics import router as analytics_router
from .routers.settings import router as settings_router
from .routers.investments import router as investments_router
from .routers.merchant_rules import router as merchant_rules_router
from .routers.auth import router as auth_router

api_router = APIRouter()

# 1. Rutas públicas (Registro, Login, Status del sistema)
api_router.include_router(auth_router)

@api_router.get("/status")
async def status_check():
    return {
        "api_version": "v1",
        "status": "active"
    }

# 2. Rutas de negocio securizadas: Requieren obligatoriamente Bearer Token válido
protected_router = APIRouter(dependencies=[Depends(get_current_user)])

protected_router.include_router(accounts_router)
protected_router.include_router(categories_router)
protected_router.include_router(budgets_router)
protected_router.include_router(transactions_router)
protected_router.include_router(analytics_router)
protected_router.include_router(merchant_rules_router)
protected_router.include_router(settings_router)
protected_router.include_router(investments_router)

api_router.include_router(protected_router)
