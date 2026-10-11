from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
from src.application.ports.account_repository import AccountRepository
from src.domain.models.account import Account
from src.application.use_cases.create_transaction import CreateTransactionUseCase

class ManageAccountUseCase:
    def __init__(
        self, 
        repository: AccountRepository,
        create_tx_use_case: Optional[CreateTransactionUseCase] = None
    ):
        self.repository = repository
        self.create_tx_use_case = create_tx_use_case

    async def create_account(
        self, 
        name: str, 
        account_type: str, 
        initial_balance: float = 0.0, 
        is_main: bool = False, 
        currency: str = "EUR",
        source_account_id: Optional[UUID] = None
    ) -> Account:
        """
        Creates a new account. If source_account_id is provided and initial_balance > 0,
        the initial funds are transferred from source_account, preventing artificial net worth inflation.
        """
        account = Account(
            name=name,
            account_type=account_type,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            is_main=is_main,
            currency=currency
        )
        saved_account = await self.repository.save(account)

        if source_account_id and initial_balance > 0 and self.create_tx_use_case:
            # Transfer the initial funds from the existing source account to the new account
            try:
                await self.create_tx_use_case.execute(
                    amount=initial_balance,
                    description=f"Fondeo inicial: {name}",
                    source="system",
                    transaction_date=datetime.now(timezone.utc),
                    account_id=source_account_id,
                    transaction_type="TRANSFER",
                    destination_account_id=saved_account.id
                )
            except Exception as e:
                print(f"Warning: Failed to create transfer transaction for account initial funding: {e}")

        return saved_account

    async def transfer_funds(
        self,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: float,
        description: str = "Traspaso entre cuentas"
    ) -> Account:
        """
        Executes a neutral transfer between two accounts.
        """
        if amount <= 0:
            raise ValueError("El importe a traspasar debe ser mayor que 0")
        if source_account_id == destination_account_id:
            raise ValueError("La cuenta de origen y destino no pueden ser la misma")

        if not self.create_tx_use_case:
            # Fallback direct balance adjustment if use case not injected
            source_acc = await self.repository.get_by_id(source_account_id)
            dest_acc = await self.repository.get_by_id(destination_account_id)
            if not source_acc or not dest_acc:
                raise ValueError("Cuenta no encontrada")
            source_acc.current_balance -= amount
            dest_acc.current_balance += amount
            await self.repository.update(source_acc)
            return await self.repository.update(dest_acc)

        await self.create_tx_use_case.execute(
            amount=amount,
            description=description,
            source="manual",
            transaction_date=datetime.now(timezone.utc),
            account_id=source_account_id,
            transaction_type="TRANSFER",
            destination_account_id=destination_account_id
        )

        updated_dest = await self.repository.get_by_id(destination_account_id)
        if not updated_dest:
            raise ValueError("Cuenta destino no encontrada")
        return updated_dest

    async def adjust_balance(
        self,
        account_id: UUID,
        amount: float,
        mode: str = "SET",
        description: str = "Ajuste de saldo"
    ) -> Account:
        """
        Adjusts an account's balance directly.
        Modes:
          - 'SET': Overwrites current_balance to amount.
          - 'ADD': Increments current_balance by amount.
          - 'SUBTRACT': Decrements current_balance by amount.
        """
        account = await self.repository.get_by_id(account_id)
        if not account:
            raise ValueError("Cuenta no encontrada")

        target_balance = account.current_balance
        if mode == "SET":
            target_balance = amount
        elif mode == "ADD":
            target_balance += abs(amount)
        elif mode == "SUBTRACT":
            target_balance -= abs(amount)
        else:
            raise ValueError(f"Modo no válido: {mode}")

        account.current_balance = target_balance
        return await self.repository.update(account)

    async def get_all_active_accounts(self) -> List[Account]:
        return await self.repository.get_all_active()

    async def disable_account(self, account_id: UUID) -> Account:
        account = await self.repository.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        account.is_active = False
        return await self.repository.update(account)
