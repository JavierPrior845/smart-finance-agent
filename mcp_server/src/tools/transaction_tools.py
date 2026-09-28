from typing import Optional
from mcp.server.fastmcp import FastMCP
from src.models.transaction import (
    CreateTransactionInput,
    ListTransactionsInput,
    ConfirmPendingTransactionInput,
)
from src.services.transaction_service import transaction_service

def register(mcp: FastMCP) -> None:
    """Registers transaction tools into FastMCP server."""

    @mcp.tool(
        name="create_transaction",
        description="Registra un nuevo gasto o ingreso en el gestor de finanzas. Permite indicar nombres amigables de categoría y cuenta sin necesidad de conocer sus UUIDs.",
    )
    async def create_transaction(
        amount: float,
        description: str,
        is_income: bool = False,
        category_name: Optional[str] = None,
        account_name: Optional[str] = None,
        date: Optional[str] = None,
    ) -> str:
        """Args:
            amount: Importe monetario positivo en euros (ej. 24.50).
            description: Concepto o descripción del movimiento (ej. 'Compra Mercadona').
            is_income: True si es un ingreso (nómina, transferencia), False si es un gasto.
            category_name: Nombre de la categoría (ej. 'Alimentación', 'Ocio'). Si se omite, se clasifica automáticamente.
            account_name: Nombre de la cuenta bancaria (ej. 'Cuenta Nómina', 'Revolut'). Si se omite, usa la principal.
            date: Fecha en formato YYYY-MM-DD. Si se omite, se utiliza la fecha actual.
        """
        try:
            input_data = CreateTransactionInput(
                amount=amount,
                description=description,
                is_income=is_income,
                category_name=category_name,
                account_name=account_name,
                date=date,
            )
            result = await transaction_service.create_transaction(input_data)
            return result["message"]
        except Exception as e:
            return f"Error al registrar transacción: {str(e)}"

    @mcp.tool(
        name="list_transactions",
        description="Consulta transacciones registradas con filtros opcionales por categoría, cuenta y rango de fechas.",
    )
    async def list_transactions(
        limit: int = 15,
        category_name: Optional[str] = None,
        account_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        """Args:
            limit: Número máximo de transacciones a devolver (1 a 100).
            category_name: Filtrar por nombre de categoría.
            account_name: Filtrar por nombre de cuenta bancaria.
            start_date: Fecha inicial (YYYY-MM-DD).
            end_date: Fecha final (YYYY-MM-DD).
        """
        try:
            input_data = ListTransactionsInput(
                limit=limit,
                category_name=category_name,
                account_name=account_name,
                start_date=start_date,
                end_date=end_date,
            )
            res = await transaction_service.list_transactions(input_data)
            items = res.get("transactions", [])
            if not items:
                return "No se encontraron transacciones para los filtros indicados."

            lines = [f"Se han encontrado {res['returned_count']} de {res['total']} transacciones:"]
            for t in items:
                sign = "+" if t["type"] == "INCOME" else "-"
                anom = " ⚠️ [ANOMALÍA]" if t.get("is_anomalous") else ""
                lines.append(f"- [{t['date']}] {sign}{t['amount']:.2f}€ | '{t['description']}'{anom}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error al listar transacciones: {str(e)}"

    @mcp.tool(
        name="get_pending_transactions",
        description="Obtiene la lista de recibos o borradores de transacciones pendientes de revisión en el Inbox.",
    )
    async def get_pending_transactions() -> str:
        try:
            items = await transaction_service.list_pending_transactions()
            if not items:
                return "No hay transacciones pendientes en la bandeja de entrada."

            lines = [f"Hay {len(items)} transacciones pendientes de confirmar:"]
            for p in items:
                sug_cat = p.suggested_category or "Sin categoría asignada"
                sug_acc = p.suggested_account or "Sin cuenta asignada"
                lines.append(
                    f"- ID: {p.id} | {p.amount:.2f}€ | '{p.description}' | Sugerida: [{sug_cat}] en [{sug_acc}]"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error al consultar transacciones pendientes: {str(e)}"

    @mcp.tool(
        name="confirm_pending_transaction",
        description="Confirma y registra definitivamente un borrador de transacción pendiente del Inbox.",
    )
    async def confirm_pending_transaction(
        transaction_id: str,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        category_name: Optional[str] = None,
        account_name: Optional[str] = None,
    ) -> str:
        """Args:
            transaction_id: ID del borrador a confirmar.
            description: Ajuste opcional de la descripción.
            amount: Ajuste opcional del importe en euros.
            category_name: Nombre de la categoría definitiva.
            account_name: Nombre de la cuenta bancaria de cargo.
        """
        try:
            input_data = ConfirmPendingTransactionInput(
                transaction_id=transaction_id,
                description=description,
                amount=amount,
                category_name=category_name,
                account_name=account_name,
            )
            res = await transaction_service.confirm_pending_transaction(input_data)
            return res["message"]
        except Exception as e:
            return f"Error al confirmar borrador de transacción: {str(e)}"
