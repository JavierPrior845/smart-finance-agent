import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings
from src.infrastructure.adapters.telegram.middlewares import AuthMiddleware
from src.infrastructure.adapters.telegram.handlers import router as main_router

logger = logging.getLogger(__name__)

def get_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    
    # Register middlewares
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Register routers
    dp.include_router(main_router)
    
    return dp

def get_bot() -> Bot | None:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set. Telegram bot will not be started.")
        return None
        
    return Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
