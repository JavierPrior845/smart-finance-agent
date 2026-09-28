from datetime import datetime
from typing import List, Dict, Any
from src.client.http_client import http_client
from src.models.budget import BudgetStatusItemDTO, BudgetsOverviewDTO

class BudgetService:
    """Business service for budgets progress and status."""

    async def get_budget_status(self) -> BudgetsOverviewDTO:
        """Retrieves active budget progress per category."""
        data = await http_client.get("/budgets")
        now = datetime.now()

        budgets: List[BudgetStatusItemDTO] = []
        total_budgeted = 0.0
        total_spent = 0.0

        for item in data:
            cat_id = str(item.get("category_id", ""))
            cat_name = item.get("category_name", "Sin categoría")
            limit = float(item.get("limit", 0.0))
            spent = float(item.get("spent", 0.0))
            remaining = float(item.get("remaining", limit - spent))
            percentage = float(item.get("percentage", (spent / limit * 100) if limit > 0 else 0.0))

            is_exceeded = spent > limit
            if percentage >= 100:
                status = "danger"
            elif percentage >= 80:
                status = "warning"
            else:
                status = "ok"

            budgets.append(
                BudgetStatusItemDTO(
                    category_id=cat_id,
                    category_name=cat_name,
                    limit=round(limit, 2),
                    spent=round(spent, 2),
                    remaining=round(remaining, 2),
                    percentage_spent=round(percentage, 1),
                    is_exceeded=is_exceeded,
                    status=status,
                )
            )
            total_budgeted += limit
            total_spent += spent

        overall_pct = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0.0

        return BudgetsOverviewDTO(
            month=now.month,
            year=now.year,
            total_budgeted=round(total_budgeted, 2),
            total_spent=round(total_spent, 2),
            overall_percentage=round(overall_pct, 1),
            budgets=budgets,
        )

budget_service = BudgetService()
