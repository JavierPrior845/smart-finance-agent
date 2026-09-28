from mcp.server.fastmcp import FastMCP
from src.services.account_service import account_service

def register(mcp: FastMCP) -> None:
    """Registers account tools into FastMCP server."""

    @mcp.tool(
        name="get_accounts_balance",
        description="Consulta todas las cuentas bancarias registradas y calcula el balance total líquido consolidado.",
    )
    async def get_accounts_balance() -> str:
        try:
            summary = await account_service.list_accounts()
            if not summary.accounts:
                return "No hay cuentas bancarias registradas en el sistema."

            lines = [
                f"=== ESTADO GLOBAL DE CUENTAS ===",
                f"Balance Total Consolidado: {summary.total_balance:.2f} {summary.currency}",
                f"Cuentas activas ({summary.accounts_count}):",
            ]
            for acc in summary.accounts:
                lines.append(f"- {acc.name} ({acc.type}): {acc.balance:.2f} {acc.currency}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error al consultar el balance de cuentas: {str(e)}"
