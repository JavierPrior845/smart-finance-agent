from typing import List, Optional, Dict, Any
from src.client.http_client import http_client
from src.models.account import AccountDTO, AccountsSummaryDTO

class AccountService:
    """Business service for accounts management."""

    async def list_accounts(self) -> AccountsSummaryDTO:
        """Retrieves all accounts and calculates total balance."""
        data = await http_client.get("/accounts")
        accounts: List[AccountDTO] = []
        total_balance = 0.0

        for item in data:
            acc = AccountDTO(
                id=str(item.get("id")),
                name=item.get("name", "Sin nombre"),
                type=item.get("type", "CHECKING"),
                balance=float(item.get("balance", 0.0)),
                currency=item.get("currency", "EUR"),
                is_active=item.get("is_active", True),
            )
            accounts.append(acc)
            total_balance += acc.balance

        return AccountsSummaryDTO(
            total_balance=round(total_balance, 2),
            currency="EUR",
            accounts_count=len(accounts),
            accounts=accounts,
        )

    async def find_account_by_name(self, name: str) -> Optional[AccountDTO]:
        """Case-insensitive search for an account by name."""
        summary = await self.list_accounts()
        target = name.strip().lower()

        # Exact match first
        for acc in summary.accounts:
            if acc.name.lower() == target:
                return acc

        # Partial match
        for acc in summary.accounts:
            if target in acc.name.lower():
                return acc

        return None

    async def get_default_account(self) -> Optional[AccountDTO]:
        """Gets default primary checking account, or first active account."""
        summary = await self.list_accounts()
        if not summary.accounts:
            return None

        # Look for checking / corriente / principal
        for acc in summary.accounts:
            name_lower = acc.name.lower()
            if any(k in name_lower for k in ("principal", "corriente", "nómina", "nomina", "checking")):
                return acc

        return summary.accounts[0]

account_service = AccountService()
