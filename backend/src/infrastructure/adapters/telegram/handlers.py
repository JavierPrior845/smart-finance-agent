import json
import logging
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from src.infrastructure.adapters.redis.client import get_redis_pool
from src.infrastructure.adapters.db.session import AsyncSessionLocal
from src.infrastructure.adapters.db.repositories.transaction_repository import SQLAlchemyTransactionRepository
from src.infrastructure.adapters.db.repositories.account_repository import SQLAlchemyAccountRepository
from src.infrastructure.adapters.db.repositories.category_repository import SQLAlchemyCategoryRepository
from src.application.use_cases.create_transaction import CreateTransactionUseCase

logger = logging.getLogger(__name__)
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

@router.callback_query(F.data.startswith("cancel_tx:"))
async def cancel_transaction_handler(callback: CallbackQuery) -> None:
    tx_id = callback.data.split(":")[1]
    redis = await get_redis_pool()
    await redis.delete(f"pending_tx:{tx_id}")
    
    await callback.answer("Transacción cancelada")
    if callback.message:
        await callback.message.edit_text("❌ <b>Registro de transacción cancelado.</b>", parse_mode="HTML")

@router.callback_query(F.data.startswith("confirm_tx:"))
async def confirm_transaction_handler(callback: CallbackQuery) -> None:
    tx_id = callback.data.split(":")[1]
    redis = await get_redis_pool()
    draft_raw = await redis.get(f"pending_tx:{tx_id}")
    
    if not draft_raw:
        await callback.answer("⚠️ El borrador ha expirado o ya fue procesado.", show_alert=True)
        return
        
    draft = json.loads(draft_raw)
    
    try:
        async with AsyncSessionLocal() as session:
            tx_repo = SQLAlchemyTransactionRepository(session)
            acc_repo = SQLAlchemyAccountRepository(session)
            cat_repo = SQLAlchemyCategoryRepository(session)
            use_case = CreateTransactionUseCase(tx_repo, acc_repo, cat_repo)
            
            # Resolve account_id by fuzzy name match if provided
            account_id = None
            if draft.get("account_name"):
                all_accounts = await acc_repo.get_all()
                match = next((a for a in all_accounts if draft["account_name"].lower() in a.name.lower()), None)
                if match:
                    account_id = match.id
                    
            # Resolve category_id by fuzzy name match if provided
            category_id = None
            if draft.get("category_name"):
                all_categories = await cat_repo.get_all()
                match = next((c for c in all_categories if draft["category_name"].lower() in c.name.lower()), None)
                if match:
                    category_id = match.id
                    
            # Execute creation
            created_tx = await use_case.execute(
                amount=draft["amount"],
                description=draft["description"],
                source="telegram",
                transaction_date=datetime.now(timezone.utc),
                account_id=account_id,
                transaction_type=draft.get("type", "EXPENSE"),
                category_id=category_id
            )
            await session.commit()
            
        await redis.delete(f"pending_tx:{tx_id}")
        await callback.answer("¡Transacción registrada!")
        
        if callback.message:
            account_str = "Cuenta Principal" if not account_id else draft.get("account_name")
            await callback.message.edit_text(
                f"✅ <b>Transacción Guardada Exitosamente</b>\n\n"
                f"💰 <b>Importe:</b> {draft['amount']} {draft['currency']}\n"
                f"📝 <b>Concepto:</b> {draft['description']}\n"
                f"🏦 <b>Cuenta:</b> {account_str}\n\n"
                f"<i>Registrado en la base de datos PostgreSQL.</i>",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error saving transaction: {e}")
        await callback.answer("❌ Error al guardar la transacción", show_alert=True)
