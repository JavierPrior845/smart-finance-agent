from uuid import UUID
from datetime import datetime
from src.application.ports.transaction_repository import TransactionRepository
from src.application.ports.account_repository import AccountRepository
from src.domain.models.transaction import Transaction, TransactionType

class CreateTransactionUseCase:
    def __init__(self, transaction_repo: TransactionRepository, account_repo: AccountRepository):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo

    async def execute(self, 
                      amount: float, 
                      description: str, 
                      source: str, 
                      transaction_date: datetime, 
                      account_id: UUID | None = None,
                      transaction_type: TransactionType = 'EXPENSE',
                      destination_account_id: UUID | None = None,
                      category_id: UUID | None = None) -> Transaction:
        
        # 1. Resolver cuenta origen
        if account_id is None:
            main_account = await self.account_repo.get_main_account()
            if not main_account:
                raise ValueError("No account_id provided and no main account is configured.")
            resolved_account_id = main_account.id
        else:
            resolved_account_id = account_id

        # 2. Validar que la cuenta existe
        account = await self.account_repo.get_by_id(resolved_account_id)
        if not account:
            raise ValueError(f"Account {resolved_account_id} not found")

        # Convert amount to absolute value for safe math
        abs_amount = abs(amount)
        transaction_amount = abs_amount

        # 3. Lógica contable (Actualizar saldos de cuenta)
        if transaction_type == 'EXPENSE' or transaction_type == 'INVESTMENT_OUTFLOW':
            account.current_balance -= abs_amount
            transaction_amount = -abs_amount
        elif transaction_type == 'INCOME' or transaction_type == 'INVESTMENT_INFLOW':
            account.current_balance += abs_amount
        elif transaction_type == 'TRANSFER':
            if not destination_account_id:
                raise ValueError("TRANSFER requires a destination_account_id")
            dest_account = await self.account_repo.get_by_id(destination_account_id)
            if not dest_account:
                raise ValueError(f"Destination account {destination_account_id} not found")
            account.current_balance -= abs_amount
            dest_account.current_balance += abs_amount
            transaction_amount = -abs_amount
            await self.account_repo.update(dest_account)
        elif transaction_type == 'BALANCE_ADJUSTMENT':
            account.current_balance = amount  # En un ajuste, el monto reemplaza al balance

        # Guardar cambios en la cuenta (Note: in a real implementation, Unit of Work ensures this is atomic)
        await self.account_repo.update(account)

        # 4. Crear y guardar la transacción
        transaction = Transaction(
            account_id=resolved_account_id,
            destination_account_id=destination_account_id,
            type=transaction_type,
            amount=transaction_amount,
            description=description,
            category_id=category_id,
            source=source,
            transaction_date=transaction_date
        )
        return await self.transaction_repo.save(transaction)
