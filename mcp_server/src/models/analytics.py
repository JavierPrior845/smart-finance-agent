from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class MonthlyReportInput(BaseModel):
    year: int = Field(..., ge=2000, le=2100, description="Año a consultar (ej. 2026)")
    month: int = Field(..., ge=1, le=12, description="Mes a consultar (1 a 12)")

class CompareMonthsInput(BaseModel):
    year1: int = Field(..., ge=2000, le=2100, description="Año del primer mes de referencia (ej. 2026)")
    month1: int = Field(..., ge=1, le=12, description="Mes del primer mes de referencia (1 a 12)")
    year2: int = Field(..., ge=2000, le=2100, description="Año del segundo mes a comparar (ej. 2026)")
    month2: int = Field(..., ge=1, le=12, description="Mes del segundo mes a comparar (1 a 12)")

class CategorySpendingDTO(BaseModel):
    category_name: str
    amount: float
    percentage: float

class MonthlyReportDTO(BaseModel):
    period: str
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate_percentage: float
    top_categories: List[CategorySpendingDTO]
    anomalies_count: int
    executive_summary: str

class CategoryVariationDTO(BaseModel):
    category_name: str
    month1_amount: float
    month2_amount: float
    delta_amount: float
    delta_percentage: Optional[float] = None
    trend: str  # "increased", "decreased", "stable"

class MonthComparisonDTO(BaseModel):
    period1: str
    period2: str
    income_period1: float
    income_period2: float
    income_delta: float
    expenses_period1: float
    expenses_period2: float
    expenses_delta: float
    savings_period1: float
    savings_period2: float
    savings_delta: float
    savings_rate_period1: float
    savings_rate_period2: float
    top_increases: List[CategoryVariationDTO]
    top_savings: List[CategoryVariationDTO]
    executive_analysis: str

class AnomalyDTO(BaseModel):
    transaction_id: str
    date: str
    description: str
    amount: float
    category_name: Optional[str] = None
    account_name: Optional[str] = None
    reason: str
