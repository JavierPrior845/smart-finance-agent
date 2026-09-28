from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP
from src.models.category import CreateCategoryInput
from src.services.category_service import category_service

def register(mcp: FastMCP) -> None:
    """Registers category tools into FastMCP server."""

    @mcp.tool(
        name="list_categories",
        description="Lista las categorías existentes de gastos e ingresos registradas en el sistema.",
    )
    async def list_categories(
        category_type: Optional[Literal["expense", "income"]] = None,
    ) -> str:
        """Args:
            category_type: Filtrar por 'expense' (gasto) o 'income' (ingreso). Si se omite, devuelve todas.
        """
        try:
            categories = await category_service.list_categories(type_filter=category_type)
            if not categories:
                return "No se encontraron categorías."

            lines = [f"Categorías registradas ({len(categories)}):"]
            for c in categories:
                lines.append(f"- {c.name} ({c.type.upper()}) | Icono: {c.icon or 'tag'}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error al listar categorías: {str(e)}"

    @mcp.tool(
        name="create_category",
        description="Crea una nueva categoría para organizar gastos o ingresos.",
    )
    async def create_category(
        name: str,
        type: Literal["expense", "income"] = "expense",
        icon: Optional[str] = "tag",
        color: Optional[str] = "#6366f1",
        default_budget_limit: Optional[float] = None,
    ) -> str:
        """Args:
            name: Nombre de la nueva categoría (ej. 'Gimnasio', 'Cursos Online').
            type: 'expense' para gastos o 'income' para ingresos.
            icon: Icono identificador (ej. 'fitness', 'book', 'wallet').
            color: Color en hexadecimal (ej. '#10b981').
            default_budget_limit: Límite presupuestario mensual opcional en euros.
        """
        try:
            input_data = CreateCategoryInput(
                name=name,
                type=type,
                icon=icon,
                color=color,
                default_budget_limit=default_budget_limit,
            )
            created = await category_service.create_category(input_data)
            return f"Categoría '{created.name}' creada exitosamente con tipo {created.type.upper()}."
        except Exception as e:
            return f"Error al crear categoría: {str(e)}"
