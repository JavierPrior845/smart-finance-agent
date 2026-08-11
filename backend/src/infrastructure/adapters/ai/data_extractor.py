from typing import Optional, Literal, List
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from src.config import settings

class TransactionExtraction(BaseModel):
    amount: float = Field(..., description="El coste o importe del gasto/ingreso en formato numérico")
    currency: str = Field("EUR", description="La moneda en la que se ha realizado la transacción, en código ISO de 3 letras (ej. EUR, USD)")
    description: str = Field(..., description="Descripción breve pero clara de la transacción")
    type: Literal["EXPENSE", "INCOME", "TRANSFER"] = Field("EXPENSE", description="Tipo de transacción: EXPENSE para gasto, INCOME para ingreso, TRANSFER para transferencia")
    account_name: Optional[str] = Field(None, description="Nombre exacto de la cuenta mencionada si coincide con la lista de cuentas. Si el usuario no menciona ninguna cuenta explícitamente, debe ser null")
    category_name: Optional[str] = Field(None, description="Nombre exacto de la categoría correspondiente de la lista de categorías válidas. Dejar null si no encaja ninguna")
    date_str: Optional[str] = Field(None, description="Fecha expresada o mencionada (ej. 'hoy', 'ayer', 'el lunes pasado'). Dejar null si es hoy")

# Configure Instructor with OpenAI client pointing to Ollama
client = OpenAI(base_url=settings.OLLAMA_URL, api_key="ollama")
instructor_client = instructor.from_openai(client, mode=instructor.Mode.JSON)

def extract_transaction_data(
    transcription_text: str,
    available_accounts: Optional[List[str]] = None,
    available_categories: Optional[List[str]] = None
) -> TransactionExtraction:
    """
    Uses a local LLM via Ollama to extract structured transaction data from natural language text,
    constrained by existing DB accounts and categories.
    """
    acc_text = f"Cuentas disponibles del usuario: {', '.join(available_accounts)}." if available_accounts else "No hay cuentas especificadas. Si el usuario no la nombra explícitamente, deja account_name como null."
    cat_text = f"Categorías válidas del usuario: {', '.join(available_categories)}." if available_categories else ""

    system_prompt = (
        "Eres un asistente experto en finanzas personales. Se te dará una transcripción de voz de un usuario.\n"
        "Tu objetivo es extraer el importe, la moneda, la descripción, el tipo (EXPENSE o INCOME), "
        "y mapear la cuenta y categoría a las opciones reales del usuario.\n\n"
        f"{acc_text}\n"
        f"{cat_text}\n\n"
        "REGLAS CRÍTICAS:\n"
        "1. Para `account_name`: SOLO asigna un nombre de cuenta si el usuario la menciona explícitamente y coincide con la lista de cuentas disponibles. Si no la menciona, pon null.\n"
        "2. Para `category_name`: Selecciona únicamente una categoría de la lista de categorías válidas que mejor se ajuste a la descripción. Si ninguna encaja, pon null.\n"
        "3. Responde única y exclusivamente con el JSON estructurado."
    )

    response = instructor_client.chat.completions.create(
        model=settings.OLLAMA_MODEL,
        response_model=TransactionExtraction,
        messages=[
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": transcription_text
            },
        ],
    )
    
    return response
