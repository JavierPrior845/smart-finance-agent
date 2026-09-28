from typing import Optional, Literal
from pydantic import BaseModel, Field

class CreateCategoryInput(BaseModel):
    name: str = Field(..., min_length=2, description="Nombre de la categoría (ej. 'Gimnasio', 'Cine', 'Dividendos')")
    type: Literal["expense", "income"] = Field("expense", description="Tipo de categoría: 'expense' (gasto) o 'income' (ingreso)")
    icon: Optional[str] = Field("tag", description="Nombre del icono (ej. 'shopping-cart', 'coffee', 'home')")
    color: Optional[str] = Field("#6366f1", description="Color en hexadecimal (ej. '#10b981')")
    default_budget_limit: Optional[float] = Field(None, gt=0, description="Límite presupuestario mensual por defecto en euros")

class CategoryDTO(BaseModel):
    id: str
    name: str
    type: str
    icon: Optional[str] = None
    color: Optional[str] = None
    is_budgetable: bool = True
