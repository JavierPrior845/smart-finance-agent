import uuid
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.application.ports.transaction_repository import TransactionRepository
from src.application.ports.account_repository import AccountRepository
from src.application.ports.category_repository import CategoryRepository
from src.domain.models.transaction import Transaction, TransactionType

class ManageTransactionUseCase:
    """
    Use case for updating and deleting existing transactions.
    Enforces business rules:
      - Only INCOME and EXPENSE transactions can be updated or deleted.
      - INVESTMENT_OUTFLOW, INVESTMENT_INFLOW, and TRANSFER are locked to maintain investment integrity.
      - Automatically reverses old account balance impacts and applies new balance impacts.
    """
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
        category_repo: CategoryRepository
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.category_repo = category_repo

    async def update_transaction(
        self,
        transaction_id: UUID,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        category_id: Optional[UUID] = None,
        account_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        transaction_date: Optional[datetime] = None
    ) -> Transaction:
        tx = await self.transaction_repo.get_by_id(transaction_id)
        if not tx:
            raise ValueError("Transacción no encontrada")

        if tx.type not in ('INCOME', 'EXPENSE'):
            raise ValueError(f"No se permite editar transacciones de tipo {tx.type}. Solo gastos e ingresos.")

        target_type = transaction_type or tx.type
        if target_type not in ('INCOME', 'EXPENSE'):
            raise ValueError("El tipo de transacción solo puede ser Gasto (EXPENSE) o Ingreso (INCOME)")

        target_account_id = account_id or tx.account_id
        old_account = await self.account_repo.get_by_id(tx.account_id) if tx.account_id else None
        new_account = (
            old_account 
            if (old_account and old_account.id == target_account_id) 
            else await self.account_repo.get_by_id(target_account_id)
        )

        if not new_account:
            raise ValueError("Cuenta destino no encontrada")

        # 1. Revert old transaction effect on old account
        if old_account:
            # tx.amount was negative for EXPENSE, positive for INCOME
            old_account.current_balance -= tx.amount
            if old_account.id != new_account.id:
                await self.account_repo.update(old_account)

        # 2. Compute new amount
        new_abs_amount = abs(amount) if amount is not None else abs(tx.amount)
        if target_type == 'EXPENSE':
            new_signed_amount = -new_abs_amount
        else:
            new_signed_amount = new_abs_amount

        # 3. Apply new transaction effect on new account
        new_account.current_balance += new_signed_amount
        await self.account_repo.update(new_account)

        # 4. Update transaction attributes
        tx.amount = new_signed_amount
        tx.type = target_type
        tx.account_id = target_account_id
        if description is not None:
            tx.description = description
        if category_id is not None:
            tx.category_id = category_id
        if transaction_date is not None:
            tx.transaction_date = transaction_date

        return await self.transaction_repo.update(tx)

    async def delete_transaction(self, transaction_id: UUID) -> None:
        tx = await self.transaction_repo.get_by_id(transaction_id)
        if not tx:
            raise ValueError("Transacción no encontrada")

        if tx.type not in ('INCOME', 'EXPENSE'):
            raise ValueError(f"No se permite eliminar transacciones de tipo {tx.type}. Solo gastos e ingresos.")

        # Revert account balance effect
        if tx.account_id:
            account = await self.account_repo.get_by_id(tx.account_id)
            if account:
                account.current_balance -= tx.amount
                await self.account_repo.update(account)

        await self.transaction_repo.delete(transaction_id)
