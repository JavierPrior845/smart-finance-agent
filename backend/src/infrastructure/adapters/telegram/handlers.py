from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from src.infrastructure.adapters.redis.client import get_redis_pool

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    name = message.from_user.full_name if message.from_user else "Usuario"
    await message.answer(f"¡Hola {name}! 👋\n\nSoy tu asistente financiero. Puedes enviarme notas de voz o tickets para registrar tus gastos.")

@router.message(F.voice)
async def voice_message_handler(message: Message) -> None:
    """
    Handles incoming voice notes, enqueues them for processing.
    """
    if not message.voice:
        return
        
    file_id = message.voice.file_id
    
    # 1. Send immediate response
    processing_msg = await message.reply("🎙️ <i>Descargando y procesando nota de voz...</i>", parse_mode="HTML")
    
    # 2. Enqueue task in ARQ
    redis = await get_redis_pool()
    await redis.enqueue_job(
        "process_voice_task", 
        message.chat.id, 
        processing_msg.message_id, 
        file_id
    )
