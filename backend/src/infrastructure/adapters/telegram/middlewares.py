from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from src.config import settings

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id and user_id not in settings.TELEGRAM_ALLOWED_USER_IDS:
            if isinstance(event, Message):
                await event.answer("⛔ No estás autorizado para usar este bot.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Acceso denegado.", show_alert=True)
            return # Drop the update
            
        return await handler(event, data)
