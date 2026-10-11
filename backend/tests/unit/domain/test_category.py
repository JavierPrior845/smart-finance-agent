import pytest
from uuid import UUID
from pydantic import ValidationError
from src.domain.models.category import Category

def test_category_creation_defaults():
    cat = Category(name="Comida")
    assert isinstance(cat.id, UUID)
    assert cat.name == "Comida"
    assert cat.type == "EXPENSE"
    assert cat.is_budgetable is True
    assert cat.is_active is True

def test_category_creation_investment_type():
    cat = Category(name="Fondos Indexados", type="INVESTMENT", color="#10b981")
    assert cat.type == "INVESTMENT"
    assert cat.color == "#10b981"

def test_category_invalid_type():
    with pytest.raises(ValidationError):
        Category(name="Invalida", type="UNKNOWN_TYPE")
