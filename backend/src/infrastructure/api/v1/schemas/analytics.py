from typing import List, Optional
from pydantic import BaseModel

class KPIsResponse(BaseModel):
    net_worth: float
    monthly_income: float
    monthly_expenses: float
    savings_rate: float

class CategoryDistribution(BaseModel):
    name: str
    value: float
    color: str

class DistributionResponse(BaseModel):
    data: List[CategoryDistribution]

class MonthlyCashflow(BaseModel):
    month: str
    ingresos: float
    gastos: float

class CashflowResponse(BaseModel):
    data: List[MonthlyCashflow]

class DailyPacing(BaseModel):
    day: int
    mesActual: Optional[float]
    mesAnterior: float

class PacingResponse(BaseModel):
    data: List[DailyPacing]
