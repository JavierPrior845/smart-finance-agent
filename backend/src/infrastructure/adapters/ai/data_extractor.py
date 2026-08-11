import instructor
from groq import Groq
from pydantic import BaseModel, Field
from src.config import settings

class TransactionExtraction(BaseModel):
    amount: float = Field(..., description="El coste o importe del gasto/ingreso en formato numérico")
    currency: str = Field(..., description="La moneda en la que se ha realizado la transacción, en código ISO de 3 letras (ej. EUR, USD)")
    description: str = Field(..., description="Descripción breve pero clara de la transacción")

# Configure Instructor with Groq client
client = Groq(api_key=settings.GROQ_API_KEY)
instructor_client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

def extract_transaction_data(transcription_text: str) -> TransactionExtraction:
    """
    Uses an LLM via Groq to extract structured transaction data from natural language text.
    """
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing. Cannot extract data.")
        
    response = instructor_client.chat.completions.create(
        model="llama3-70b-8192",
        response_model=TransactionExtraction,
        messages=[
            {
                "role": "system", 
                "content": "Eres un asistente experto en finanzas. Se te dará una transcripción de voz de un usuario indicando un gasto. Tu objetivo es extraer el importe exacto, la moneda (asume EUR si no se especifica) y un concepto descriptivo. Responde única y exclusivamente con el JSON estructurado."
            },
            {
                "role": "user", 
                "content": transcription_text
            },
        ],
    )
    
    return response
