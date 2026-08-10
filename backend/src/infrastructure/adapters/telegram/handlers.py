from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    name = message.from_user.full_name if message.from_user else "Usuario"
    await message.answer(f"¡Hola {name}! 👋\n\nSoy tu asistente financiero. Puedes enviarme notas de voz o tickets para registrar tus gastos.")
