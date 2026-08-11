import logging
import os
import json
import uuid
from arq.connections import RedisSettings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import settings
from src.infrastructure.adapters.telegram.bot import get_bot
from src.infrastructure.adapters.ai.local_stt import transcribe_audio
from src.infrastructure.adapters.ai.data_extractor import extract_transaction_data
from src.infrastructure.adapters.redis.client import get_redis_pool

logger = logging.getLogger(__name__)

async def startup(ctx):
    logger.info("Worker startup...")
    ctx['bot'] = get_bot()

async def shutdown(ctx):
    logger.info("Worker shutdown...")
    if ctx.get('bot'):
        await ctx['bot'].session.close()

async def process_voice_task(ctx, chat_id: int, message_id: int, file_id: str):
    logger.info(f"Processing voice task for file {file_id}")
    bot = ctx['bot']
    
    # 1. Download file
    file_info = await bot.get_file(file_id)
    file_path = f"/tmp/{file_id}.ogg"
    
    await bot.download_file(file_info.file_path, destination=file_path)
    
    try:
        # 2. Transcribe Audio
        logger.info("Transcribing audio...")
        transcription = transcribe_audio(file_path)
        logger.info(f"Transcription: {transcription}")
        
        # 3. Extract Data
        logger.info("Extracting data...")
        data = extract_transaction_data(transcription)
        
        # 4. Save Draft in Redis
        tx_id = str(uuid.uuid4())
        draft_dict = data.model_dump()
        draft_dict["raw_text"] = transcription
        
        redis = await get_redis_pool()
        await redis.set(f"pending_tx:{tx_id}", json.dumps(draft_dict), ex=3600)
        
        # 5. Build Inline Keyboards
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirmar", callback_data=f"confirm_tx:{tx_id}"),
                InlineKeyboardButton(text="❌ Cancelar", callback_data=f"cancel_tx:{tx_id}")
            ]
        ])
        
        response_text = (
            f"🎙️ <b>Transcripción:</b> <i>\"{transcription}\"</i>\n\n"
            f"📌 <b>Borrador de Transacción:</b>\n"
            f"💰 <b>Importe:</b> {data.amount} {data.currency}\n"
            f"📊 <b>Tipo:</b> {data.type}\n"
            f"📝 <b>Concepto:</b> {data.description}\n"
            f"🏦 <b>Cuenta:</b> {data.account_name or 'Principal (Defecto)'}\n"
            f"📁 <b>Categoría:</b> {data.category_name or 'General'}\n\n"
            f"¿Deseas confirmar el registro en la base de datos?"
        )
        
        await bot.edit_message_text(
            text=response_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error processing voice task: {e}")
        await bot.edit_message_text(
            text=f"❌ Error al procesar la nota de voz: {str(e)}",
            chat_id=chat_id,
            message_id=message_id
        )
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

class WorkerSettings:
    functions = [process_voice_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
