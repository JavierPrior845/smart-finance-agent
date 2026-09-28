import sys
from pathlib import Path

# Add mcp_server root to sys.path to allow clean imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP
from src.tools.index import register_all_tools

# 1. Inicialización del Servidor FastMCP
mcp = FastMCP("smart-finance-mcp")

# 2. Inyección de las tools desde el índice
register_all_tools(mcp)

# 3. Punto de entrada por stdio (estándar para Claude Desktop / Antigravity / Cursor)
if __name__ == "__main__":
    mcp.run(transport="stdio")
