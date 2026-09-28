# 🤖 Smart Finance - Servidor MCP (Model Context Protocol)

Servidor oficial de integración **Model Context Protocol (MCP)** para el Gestor de Finanzas. Permite que Agentes de Inteligencia Artificial (Claude Desktop, Cursor, Antigravity IDE, etc.) interactúen de forma segura y natural con tus finanzas personales.

---

## 🏗️ Arquitectura Desacoplada

El servidor MCP opera como un **cliente externo de la API REST**:
* **Cero invasión:** No se conecta directamente a la base de datos PostgreSQL ni altera los contenedores Docker en ejecución.
* **Seguridad y Reglas de Negocio:** Todas las operaciones pasan por los endpoints de FastAPI (`http://localhost:8000/api/v1`), validando esquemas Pydantic y respetando la autenticación JWT.
* **Transporte Estándar:** Utiliza `stdio` (entrada y salida estándar) mediante el framework `FastMCP`.

---

## 🛠️ Herramientas Expuestas (Tools Catalog)

| Herramienta | Descripción | Parámetros Clave |
|---|---|---|
| `create_transaction` | Registra un nuevo gasto o ingreso con resolución inteligente de nombres de cuenta y categoría. | `amount`, `description`, `is_income`, `category_name`, `account_name`, `date` |
| `list_transactions` | Consulta movimientos contables con filtros opcionales. | `limit`, `category_name`, `account_name`, `start_date`, `end_date` |
| `get_pending_transactions` | Lista los borradores y recibos pendientes de revisión en el Inbox. | - |
| `confirm_pending_transaction` | Confirma y asienta un borrador del Inbox. | `transaction_id`, `category_name`, `account_name`, `amount`, `description` |
| `list_categories` | Lista todas las categorías registradas con icono y tipo. | `category_type` ('expense' / 'income') |
| `create_category` | Crea una nueva categoría de gastos o ingresos al vuelo. | `name`, `type`, `icon`, `color`, `default_budget_limit` |
| `get_accounts_balance` | Consulta el saldo consolidado y desglose de todas las cuentas bancarias. | - |
| `get_budget_status` | Evalúa el progreso y salud de los presupuestos mensuales. | - |
| `get_monthly_report` | Genera un informe financiero mensual completo con desglose y tasa de ahorro. | `year`, `month` |
| `compare_months` | Compara el rendimiento financiero entre dos meses con análisis delta por categoría. | `year1`, `month1`, `year2`, `month2` |
| `get_expense_anomalies` | Lista los gastos atípicos detectados por el modelo estadístico IQR. | `limit` |

---

## 🚀 Instalación y Configuración

### 1. Crear entorno virtual e instalar dependencias
```bash
cd mcp_server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copia la plantilla `.env.example`:
```bash
cp .env.example .env
```
Configura tus credenciales en `.env`:
```env
SMART_FINANCE_API_BASE_URL=http://localhost:8000/api/v1
SMART_FINANCE_EMAIL=tu_usuario@ejemplo.com
SMART_FINANCE_PASSWORD=tu_contraseña
```

---

## 🧪 Pruebas y Validación Visual (MCP Inspector & Herramientas de Test)

Para probar el servidor de forma interactiva y visual sin necesidad de abrir Claude Desktop o Antigravity, dispones de dos herramientas estándar:

### Opción A: MCP Inspector Oficial (Interfaz Web Interactiva)
Anthropic y el equipo de MCP proporcionan el **MCP Inspector**, una herramienta gráfica que levanta un panel en tu navegador para ver las herramientas, rellenar formularios y probar la ejecución en tiempo real:

1. Asegúrate de tener Node.js instalado (`npx`).
2. Con tu entorno virtual activo y desde la carpeta `mcp_server`:
   ```bash
   npx @modelcontextprotocol/inspector .venv/bin/python main.py
   ```
   *(O indicando la ruta absoluta si ejecutas desde fuera)*:
   ```bash
   npx @modelcontextprotocol/inspector /home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/mcp_server/.venv/bin/python /home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/mcp_server/main.py
   ```
3. Se abrirá automáticamente una interfaz web (habitualmente en `http://localhost:5173` o el puerto mostrado en terminal).
4. **¿Qué puedes hacer en el Inspector?**
   * **Pestaña "Tools":** Verás el listado de todas las herramientas (`create_transaction`, `compare_months`, etc.) con sus esquemas JSON generados.
   * **Ejecución Interactiva:** Rellena campos como `amount: 25.50` y `description: "Prueba Inspector"` y haz clic en **Run Tool** para ver la respuesta real devuelta por la API.
   * **Inspección de Mensajes JSON-RPC:** Permite verificar la traza exacta de comunicación entre el cliente y el servidor.

---

### Opción B: CLI de Desarrollo FastMCP (`mcp dev`)
El paquete `mcp` incluye comandos CLI integrados:
```bash
source .venv/bin/activate
mcp dev main.py
```
Este comando enlaza automáticamente tu servidor con el inspector en modo desarrollo y recarga en caliente los cambios de código.

---

## 🔌 Configuración en Clientes de IA

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "smart-finance": {
      "command": "/home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/mcp_server/.venv/bin/python",
      "args": [
        "/home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/mcp_server/main.py"
      ]
    }
  }
}
```

### Antigravity IDE (`mcp_config.json`)
```json
{
  "smart-finance": {
    "command": "/home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/mcp_server/.venv/bin/python",
    "args": ["main.py"],
    "cwd": "/home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/mcp_server"
  }
}
```
