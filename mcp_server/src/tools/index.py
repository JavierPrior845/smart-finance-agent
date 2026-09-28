from typing import List, Callable
from mcp.server.fastmcp import FastMCP

from src.tools.transaction_tools import register as register_transactions
from src.tools.category_tools import register as register_categories
from src.tools.account_tools import register as register_accounts
from src.tools.budget_tools import register as register_budgets
from src.tools.analytics_tools import register as register_analytics

# Array ordenado de registradores de tools
TOOL_REGISTRARS: List[Callable[[FastMCP], None]] = [
    register_transactions,
    register_categories,
    register_accounts,
    register_budgets,
    register_analytics,
]

def register_all_tools(mcp: FastMCP) -> None:
    """Inyecta secuencialmente todas las herramientas en la instancia de FastMCP."""
    for register_tool in TOOL_REGISTRARS:
        register_tool(mcp)
