from typing import Optional, List
from pydantic import BaseModel, Field

class CreateTransactionInput(BaseModel):
    amount: float = Field(..., gt=0, description="Importe monetario positivo (ej. 24.50)")
    description: str = Field(..., min_length=1, description="Concepto o descripción (ej. 'Compra semanal en Mercadona')")
    is_income: bool = Field(False, description="True si es un ingreso (nómina, venta), False si es un gasto")
    category_name: Optional[str] = Field(None, description="Nombre de la categoría (ej. 'Alimentación', 'Transporte')")
    account_name: Optional[str] = Field(None, description="Nombre de la cuenta bancaria (ej. 'Cuenta Nómina', 'Revolut')")
    date: Optional[str] = Field(None, description="Fecha de la transacción en formato YYYY-MM-DD (por defecto hoy)")

class ListTransactionsInput(BaseModel):
    limit: int = Field(20, ge=1, le=100, description="Número máximo de transacciones a recuperar")
    start_date: Optional[str] = Field(None, description="Fecha inicial en formato YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="Fecha final en formato YYYY-MM-DD")
    category_name: Optional[str] = Field(None, description="Filtrar por nombre de categoría")
    account_name: Optional[str] = Field(None, description="Filtrar por nombre de cuenta bancaria")

class ConfirmPendingTransactionInput(BaseModel):
    transaction_id: str = Field(..., description="ID del borrador o transacción pendiente a confirmar")
    description: Optional[str] = Field(None, description="Nueva descripción o ajuste")
    amount: Optional[float] = Field(None, gt=0, description="Ajuste del importe si fuese erróneo")
    category_name: Optional[str] = Field(None, description="Asignar o cambiar categoría")
    account_name: Optional[str] = Field(None, description="Asignar o cambiar cuenta bancaria")

class TransactionDTO(BaseModel):
    id: str
    amount: float
    type: str
    description: str
    category: Optional[str] = None
    account: Optional[str] = None
    date: str
    is_anomalous: bool = False

class PendingTransactionDTO(BaseModel):
    id: str
    amount: float
    type: str
    description: str
    suggested_category: Optional[str] = None
    suggested_account: Optional[str] = None
    raw_text: Optional[str] = None
