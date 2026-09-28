from mcp.server.fastmcp import FastMCP
from src.services.budget_service import budget_service

def register(mcp: FastMCP) -> None:
    """Registers budget tools into FastMCP server."""

    @mcp.tool(
        name="get_budget_status",
        description="Consulta el estado de ejecución y cumplimiento de los presupuestos mensuales por categoría.",
    )
    async def get_budget_status() -> str:
        try:
            overview = await budget_service.get_budget_status()
            if not overview.budgets:
                return "No hay presupuestos activos configurados para este mes."

            lines = [
                f"=== ESTADO DE PRESUPUESTOS (Mes {overview.month}/{overview.year}) ===",
                f"Presupuesto Total: {overview.total_budgeted:.2f}€ | Gastado: {overview.total_spent:.2f}€ ({overview.overall_percentage:.1f}%)",
                "",
                "Detalle por Categoría:",
            ]

            for b in overview.budgets:
                indicator = "🟢"
                if b.status == "danger":
                    indicator = "🔴 [EXCEDIDO]"
                elif b.status == "warning":
                    indicator = "🟡 [ALERTA >80%]"

                lines.append(
                    f"{indicator} {b.category_name}: Gastado {b.spent:.2f}€ de {b.limit:.2f}€ "
                    f"({b.percentage_spent:.1f}%) | Restante: {b.remaining:.2f}€"
                )

            return "\n".join(lines)
        except Exception as e:
            return f"Error al consultar estado de presupuestos: {str(e)}"
