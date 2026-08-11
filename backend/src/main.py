import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.infrastructure.adapters.telegram.bot import get_bot, get_dispatcher
    
    bot = get_bot()
    dp = get_dispatcher()
    bot_task = None
    
    if bot:
        logger.info("Starting Telegram Bot Polling...")
        bot_task = asyncio.create_task(dp.start_polling(bot))
    else:
        logger.info("Telegram Bot will not start (no token provided).")
        
    yield
    
    if bot_task:
        logger.info("Stopping Telegram Bot...")
        await dp.stop_polling()
        try:
            await asyncio.wait_for(bot_task, timeout=5.0)
        except asyncio.TimeoutError:
            bot_task.cancel()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error while stopping bot task: {e}")
        await bot.session.close()

app = FastAPI(
    title="Smart Finance Agent API",
    description="Production-grade Personal Finance API featuring Hexagonal Architecture and AI Categorization.",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for Web Application frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.infrastructure.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "version": app.version,
    }

