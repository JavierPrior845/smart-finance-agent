from typing import Optional, Literal
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

class TransactionExtraction(BaseModel):
    amount: float = Field(..., description="El coste o importe del gasto/ingreso en formato numérico")
    currency: str = Field("EUR", description="La moneda en la que se ha realizado la transacción, en código ISO de 3 letras (ej. EUR, USD)")
    description: str = Field(..., description="Descripción breve pero clara de la transacción")
    type: Literal["EXPENSE", "INCOME", "TRANSFER"] = Field("EXPENSE", description="Tipo de transacción: EXPENSE para gasto, INCOME para ingreso, TRANSFER para transferencia")
    account_name: Optional[str] = Field(None, description="Nombre de la cuenta o banco mencionado (ej. N26, Efectivo, BBVA). Dejar null si no se especifica")
    category_name: Optional[str] = Field(None, description="Categoría aproximada del gasto (ej. Supermercado, Gasolina, Restaurantes, Nómina). Dejar null si no se especifica")
    date_str: Optional[str] = Field(None, description="Fecha expresada o mencionada (ej. 'hoy', 'ayer', 'el lunes pasado'). Dejar null si es hoy")

# Configure Instructor with OpenAI client pointing to Ollama
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
instructor_client = instructor.from_openai(client, mode=instructor.Mode.JSON)

def extract_transaction_data(transcription_text: str) -> TransactionExtraction:
    """
    Uses a local LLM via Ollama to extract structured transaction data from natural language text.
    """
    response = instructor_client.chat.completions.create(
        model="qwen2.5-coder:1.5b",
        response_model=TransactionExtraction,
        messages=[
            {
                "role": "system", 
                "content": (
                    "Eres un asistente experto en finanzas personales. Se te dará una transcripción de voz de un usuario. "
                    "Tu objetivo es extraer el importe, la moneda, la descripción, el tipo (EXPENSE o INCOME), "
                    "y si es posible el nombre de la cuenta, la categoría y la fecha especificada. "
                    "Responde única y exclusivamente con el JSON estructurado según el esquema."
                )
            },
            {
                "role": "user", 
                "content": transcription_text
            },
        ],
    )
    
    return response
