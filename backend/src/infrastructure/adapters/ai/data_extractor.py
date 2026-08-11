from typing import Optional, Literal, List
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from src.config import settings

class TransactionExtraction(BaseModel):
    amount: float = Field(..., description="El importe del gasto o ingreso en número decimal")
    currency: str = Field("EUR", description="Código ISO de 3 letras de la moneda (ej. EUR, USD)")
    description: str = Field(..., description="Concepto limpio, corto y sustantivo de la transacción (ej. 'Cine', 'Gasolina', 'Café'). NUNCA copiar la frase completa del usuario ni incluir verbos como 'gasté', 'pagué' o 'compré'.")
    type: Literal["EXPENSE", "INCOME", "TRANSFER"] = Field("EXPENSE", description="EXPENSE para gasto, INCOME para ingreso, TRANSFER para transferencia")
    account_name: Optional[str] = Field(None, description="Nombre exacto de la cuenta mencionada solo si coincide con la lista de cuentas disponibles. Si no se nombra ninguna, debe ser null")
    category_name: Optional[str] = Field(None, description="Nombre exacto de la categoría correspondiente solo si encaja de forma lógica con la lista de categorías válidas. Dejar null si no hay coincidencia clara")
    date_str: Optional[str] = Field(None, description="Fecha mencionada (ej. 'hoy', 'ayer'). Dejar null si es hoy")

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
    acc_text = f"Cuentas disponibles del usuario: {', '.join(available_accounts)}." if available_accounts else "No se especifica lista de cuentas. Deja account_name como null si no la nombra."
    cat_text = f"Categorías válidas del usuario: {', '.join(available_categories)}." if available_categories else "No hay categorías."

    system_prompt = (
        "Eres un asistente experto en finanzas personales especializado en estructurar gastos e ingresos.\n"
        "Se te dará una frase o mensaje de un usuario y debes extraer sus campos de forma precisa.\n\n"
        f"{acc_text}\n"
        f"{cat_text}\n\n"
        "REGLAS ESTRUCTURALES:\n"
        "1. `description`: Extrae SOLO el concepto o comercio en 1 a 3 palabras clave (ej. 'Gasté 18 euros en cine' -> 'Cine', 'Pago de 50€ en gasolina' -> 'Gasolina'). Elimina la paja y los verbos de la frase.\n"
        "2. `account_name`: Solo asigna una cuenta si el usuario la menciona explícitamente y está en la lista. Si no, pon null.\n"
        "3. `category_name`: Revisa la lista de categorías válidas. Asigna una categoría ÚNICAMENTE si existe una relación directa y obvia con el concepto. Si ninguna categoría se ajusta claramente (ej. 'Cine' y las categorías son 'Alimentación' y 'Transporte'), debes poner null OBLIGATORIAMENTE."
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
