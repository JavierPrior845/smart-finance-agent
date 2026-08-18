from uuid import UUID
from typing import Tuple
from src.application.ports.transaction_repository import TransactionRepository

class BudgetAnomalyDetector:
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    async def evaluate(self, category_id: UUID, amount: float) -> Tuple[bool, str | None]:
        """
        Evaluates an expense transaction for anomalies using the Median and IQR method.
        Only runs if there are at least 5 historical expenses for this category.
        """
        if not category_id:
            return False, None
            
        # Get last 30 transactions of this category
        items, _ = await self.transaction_repo.get_all_paginated(
            limit=30,
            category_id=category_id
        )
        
        # Filter to confirmed expenses
        expenses = [float(abs(t.amount)) for t in items if t.status == 'confirmed' and t.type == 'EXPENSE']
        
        if len(expenses) < 5:
            return False, None
            
        # Calculate percentiles (Q1, Q3)
        sorted_expenses = sorted(expenses)
        n = len(sorted_expenses)
        
        def get_percentile(data, p):
            idx = (n - 1) * p
            floor_idx = int(idx)
            ceil_idx = floor_idx + 1 if floor_idx < n - 1 else floor_idx
            return data[floor_idx] + (data[ceil_idx] - data[floor_idx]) * (idx - floor_idx)

        q1 = get_percentile(sorted_expenses, 0.25)
        q3 = get_percentile(sorted_expenses, 0.75)
        iqr = q3 - q1
        
        # Tukey's fence: Q3 + 1.5 * IQR
        upper_fence = q3 + 1.5 * iqr
        
        if abs(amount) > upper_fence:
            return True, f"El importe ({abs(amount):.2f} EUR) supera el límite superior de Tukey ({upper_fence:.2f} EUR, IQR: {iqr:.2f} EUR)"
            
        return False, None
