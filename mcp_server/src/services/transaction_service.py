from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from src.client.http_client import http_client
from src.services.account_service import account_service
from src.services.category_service import category_service
from src.models.transaction import (
    CreateTransactionInput,
    ListTransactionsInput,
    ConfirmPendingTransactionInput,
    TransactionDTO,
    PendingTransactionDTO,
)

class TransactionService:
    """Business service for transactions orchestration."""

    async def create_transaction(self, input_data: CreateTransactionInput) -> Dict[str, Any]:
        """Creates a transaction with smart resolution of account and category names."""
        # 1. Resolve Account
        account_id: Optional[str] = None
        account_name_resolved: str = "Desconocida"

        if input_data.account_name:
            account = await account_service.find_account_by_name(input_data.account_name)
            if not account:
                summary = await account_service.list_accounts()
                available = ", ".join([f"'{a.name}'" for a in summary.accounts])
                raise ValueError(
                    f"No se encontró ninguna cuenta con el nombre '{input_data.account_name}'. "
                    f"Cuentas disponibles: {available}"
                )
            account_id = account.id
            account_name_resolved = account.name
        else:
            default_acc = await account_service.get_default_account()
            if default_acc:
                account_id = default_acc.id
                account_name_resolved = default_acc.name

        # 2. Resolve Category (if provided, otherwise backend hybrid classifier will assign one)
        category_id: Optional[str] = None
        category_name_resolved: Optional[str] = None

        if input_data.category_name:
            expected_type = "income" if input_data.is_income else "expense"
            category = await category_service.find_category_by_name(input_data.category_name, cat_type=expected_type)
            if category:
                category_id = category.id
                category_name_resolved = category.name
            else:
                category_name_resolved = f"{input_data.category_name} (se categorizará automáticamente)"

        # 3. Resolve Date
        if input_data.date:
            try:
                dt = datetime.strptime(input_data.date.strip(), "%Y-%m-%d")
                transaction_date = dt.replace(hour=12, minute=0, second=0).isoformat()
            except ValueError:
                raise ValueError(f"Formato de fecha inválido '{input_data.date}'. Debe ser YYYY-MM-DD.")
        else:
            transaction_date = datetime.now().isoformat()

        # 4. Prepare payload for FastAPI
        tx_type = "INCOME" if input_data.is_income else "EXPENSE"
        payload = {
            "account_id": account_id,
            "type": tx_type,
            "amount": float(input_data.amount),
            "currency": "EUR",
            "description": input_data.description.strip(),
            "category_id": category_id,
            "source": "mcp",
            "transaction_date": transaction_date,
        }

        # 5. Execute request
        created = await http_client.post("/transactions", json_data=payload)

        return {
            "success": True,
            "message": (
                f"Transacción registrada con éxito: {tx_type} de {input_data.amount:.2f}€ "
                f"en '{input_data.description}'. Cuenta: '{account_name_resolved}'."
            ),
            "transaction": {
                "id": str(created.get("id")),
                "type": tx_type,
                "amount": float(created.get("amount")),
                "description": created.get("description"),
                "date": str(created.get("transaction_date")),
                "category_id": created.get("category_id"),
                "is_anomalous": created.get("is_anomalous", False),
            },
        }

    async def list_transactions(self, input_data: ListTransactionsInput) -> Dict[str, Any]:
        """Lists transactions with filters."""
        params: Dict[str, Any] = {
            "limit": input_data.limit,
            "offset": 0,
        }

        if input_data.category_name:
            cat = await category_service.find_category_by_name(input_data.category_name)
            if cat:
                params["category_id"] = cat.id

        if input_data.account_name:
            acc = await account_service.find_account_by_name(input_data.account_name)
            if acc:
                params["account_id"] = acc.id

        response_data = await http_client.get("/transactions", params=params)
        items = response_data.get("items", [])
        total = response_data.get("total", len(items))

        transactions: List[TransactionDTO] = []
        for item in items:
            transactions.append(
                TransactionDTO(
                    id=str(item.get("id")),
                    amount=float(item.get("amount", 0.0)),
                    type=item.get("type", "EXPENSE"),
                    description=item.get("description", ""),
                    category=str(item.get("category_id")) if item.get("category_id") else None,
                    account=str(item.get("account_id")) if item.get("account_id") else None,
                    date=str(item.get("transaction_date", ""))[:10],
                    is_anomalous=item.get("is_anomalous", False),
                )
            )

        return {
            "total": total,
            "returned_count": len(transactions),
            "transactions": [t.model_dump() for t in transactions],
        }

    async def list_pending_transactions(self) -> List[PendingTransactionDTO]:
        """Lists all pending drafts in the inbox."""
        items = await http_client.get("/transactions/pending")
        result: List[PendingTransactionDTO] = []

        for item in items:
            result.append(
                PendingTransactionDTO(
                    id=str(item.get("id")),
                    amount=float(item.get("amount", 0.0)),
                    type=item.get("type", "EXPENSE"),
                    description=item.get("description", ""),
                    suggested_category=item.get("category_name"),
                    suggested_account=item.get("account_name"),
                    raw_text=item.get("raw_text"),
                )
            )

        return result

    async def confirm_pending_transaction(self, input_data: ConfirmPendingTransactionInput) -> Dict[str, Any]:
        """Confirms and persists a pending draft."""
        payload: Dict[str, Any] = {
            "type": "EXPENSE",
        }

        if input_data.amount:
            payload["amount"] = input_data.amount
        if input_data.description:
            payload["description"] = input_data.description

        if input_data.category_name:
            cat = await category_service.find_category_by_name(input_data.category_name)
            if cat:
                payload["category_id"] = cat.id

        if input_data.account_name:
            acc = await account_service.find_account_by_name(input_data.account_name)
            if acc:
                payload["account_id"] = acc.id

        confirmed = await http_client.post(
            f"/transactions/pending/{input_data.transaction_id}/confirm",
            json_data=payload,
        )

        return {
            "success": True,
            "message": f"Transacción borrador {input_data.transaction_id} confirmada y registrada en contabilidad.",
            "transaction_id": str(confirmed.get("id")),
        }

transaction_service = TransactionService()
