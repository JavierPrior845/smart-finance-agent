from uuid import UUID
from typing import List
from src.application.ports.account_repository import AccountRepository
from src.domain.models.account import Account

class ManageAccountUseCase:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    async def create_account(self, name: str, account_type: str, initial_balance: float = 0.0, is_main: bool = False, currency: str = "EUR") -> Account:
        # Business logic: if is_main is true, we should probably unset other main accounts, but for now we just create.
        account = Account(
            name=name,
            account_type=account_type,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            is_main=is_main,
            currency=currency
        )
        return await self.repository.save(account)

    async def get_all_active_accounts(self) -> List[Account]:
        return await self.repository.get_all_active()

    async def disable_account(self, account_id: UUID) -> Account:
        account = await self.repository.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        account.is_active = False
        return await self.repository.update(account)
