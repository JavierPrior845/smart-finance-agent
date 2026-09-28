from typing import List, Optional, Dict, Any
from src.client.http_client import http_client
from src.models.category import CategoryDTO, CreateCategoryInput

class CategoryService:
    """Business service for categories management."""

    async def list_categories(self, type_filter: Optional[str] = None) -> List[CategoryDTO]:
        """Retrieves categories with optional 'expense'/'income' filter."""
        data = await http_client.get("/categories")
        categories: List[CategoryDTO] = []

        for item in data:
            cat_type = str(item.get("type", "EXPENSE")).lower()
            if type_filter and cat_type != type_filter.lower():
                continue

            categories.append(
                CategoryDTO(
                    id=str(item.get("id")),
                    name=item.get("name", "Sin categoría"),
                    type=cat_type,
                    icon=item.get("icon"),
                    color=item.get("color"),
                    is_budgetable=item.get("is_budgetable", True),
                )
            )

        return categories

    async def create_category(self, input_data: CreateCategoryInput) -> CategoryDTO:
        """Creates a new category via REST API."""
        payload = {
            "name": input_data.name.strip(),
            "type": input_data.type.upper(),
            "icon": input_data.icon or "tag",
            "color": input_data.color or "#6366f1",
            "is_budgetable": True,
            "default_budget_limit": input_data.default_budget_limit,
            "is_active": True,
        }

        data = await http_client.post("/categories", json_data=payload)
        return CategoryDTO(
            id=str(data.get("id")),
            name=data.get("name"),
            type=str(data.get("type")).lower(),
            icon=data.get("icon"),
            color=data.get("color"),
            is_budgetable=data.get("is_budgetable", True),
        )

    async def find_category_by_name(self, name: str, cat_type: Optional[str] = None) -> Optional[CategoryDTO]:
        """Case-insensitive search for a category by name."""
        categories = await self.list_categories(type_filter=cat_type)
        target = name.strip().lower()

        # Exact match
        for cat in categories:
            if cat.name.lower() == target:
                return cat

        # Partial match
        for cat in categories:
            if target in cat.name.lower() or cat.name.lower() in target:
                return cat

        return None

category_service = CategoryService()
