import calendar
from typing import List, Dict, Any, Tuple
from src.client.http_client import http_client
from src.services.category_service import category_service
from src.models.analytics import (
    MonthlyReportInput,
    MonthlyReportDTO,
    CategorySpendingDTO,
    CompareMonthsInput,
    MonthComparisonDTO,
    CategoryVariationDTO,
    AnomalyDTO,
)

class AnalyticsService:
    """Business service for analytics, reports and month-to-month comparisons."""

    MONTH_NAMES_ES = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    async def _get_month_aggregated_data(self, year: int, month: int) -> Tuple[float, float, Dict[str, float], int]:
        """Fetches transactions for given month/year and aggregates income, expense, and category breakdown."""
        # Query up to 100 transactions for that specific month and year
        response = await http_client.get("/transactions", params={"year": year, "month": month, "limit": 100})
        items = response.get("items", []) if isinstance(response, dict) else []

        categories = await category_service.list_categories()
        cat_map = {c.id: c.name for c in categories}

        total_income = 0.0
        total_expenses = 0.0
        expenses_by_cat: Dict[str, float] = {}
        anomalies_count = 0

        for item in items:
            tx_type = str(item.get("type", "EXPENSE")).upper()
            amount = float(item.get("amount", 0.0))
            is_anomalous = bool(item.get("is_anomalous", False))
            if is_anomalous:
                anomalies_count += 1

            if tx_type == "INCOME":
                total_income += amount
            elif tx_type == "EXPENSE":
                total_expenses += amount
                cat_id = str(item.get("category_id", ""))
                cat_name = cat_map.get(cat_id, "Sin categoría")
                expenses_by_cat[cat_name] = expenses_by_cat.get(cat_name, 0.0) + amount

        return round(total_income, 2), round(total_expenses, 2), expenses_by_cat, anomalies_count

    async def get_monthly_report(self, input_data: MonthlyReportInput) -> MonthlyReportDTO:
        """Generates a comprehensive monthly report with savings rate and top categories."""
        month_name = self.MONTH_NAMES_ES[input_data.month]
        period = f"{month_name} {input_data.year}"

        income, expenses, cat_expenses, anomalies = await self._get_month_aggregated_data(
            input_data.year, input_data.month
        )

        net_savings = round(income - expenses, 2)
        savings_rate = round((net_savings / income * 100), 1) if income > 0 else 0.0

        # Sort top categories
        sorted_cats = sorted(cat_expenses.items(), key=lambda x: x[1], reverse=True)
        top_categories = [
            CategorySpendingDTO(
                category_name=name,
                amount=round(amount, 2),
                percentage=round((amount / expenses * 100), 1) if expenses > 0 else 0.0,
            )
            for name, amount in sorted_cats[:5]
        ]

        top_cats_str = ", ".join([f"{c.category_name} ({c.amount}€, {c.percentage}%)" for c in top_categories[:3]]) or "Sin gastos"
        summary = (
            f"Informe de {period}: Ingresos de {income:.2f}€ y gastos de {expenses:.2f}€. "
            f"Ahorro neto resultante: {net_savings:.2f}€ (Tasa de ahorro: {savings_rate}%). "
            f"Principales categorías de gasto: {top_cats_str}. "
            f"Gastos anómalos detectados: {anomalies}."
        )

        return MonthlyReportDTO(
            period=period,
            total_income=income,
            total_expenses=expenses,
            net_savings=net_savings,
            savings_rate_percentage=savings_rate,
            top_categories=top_categories,
            anomalies_count=anomalies,
            executive_summary=summary,
        )

    async def compare_months(self, input_data: CompareMonthsInput) -> MonthComparisonDTO:
        """Compares financial performance between two specific months."""
        m1_name = f"{self.MONTH_NAMES_ES[input_data.month1]} {input_data.year1}"
        m2_name = f"{self.MONTH_NAMES_ES[input_data.month2]} {input_data.year2}"

        inc1, exp1, cats1, _ = await self._get_month_aggregated_data(input_data.year1, input_data.month1)
        inc2, exp2, cats2, _ = await self._get_month_aggregated_data(input_data.year2, input_data.month2)

        sav1 = round(inc1 - exp1, 2)
        sav2 = round(inc2 - exp2, 2)

        rate1 = round((sav1 / inc1 * 100), 1) if inc1 > 0 else 0.0
        rate2 = round((sav2 / inc2 * 100), 1) if inc2 > 0 else 0.0

        income_delta = round(inc2 - inc1, 2)
        expenses_delta = round(exp2 - exp1, 2)
        savings_delta = round(sav2 - sav1, 2)

        # Compare per-category variations
        all_cats = set(cats1.keys()) | set(cats2.keys())
        variations: List[CategoryVariationDTO] = []

        for cat in all_cats:
            amt1 = cats1.get(cat, 0.0)
            amt2 = cats2.get(cat, 0.0)
            diff = round(amt2 - amt1, 2)
            pct = round((diff / amt1 * 100), 1) if amt1 > 0 else None

            if diff > 5.0:
                trend = "increased"
            elif diff < -5.0:
                trend = "decreased"
            else:
                trend = "stable"

            variations.append(
                CategoryVariationDTO(
                    category_name=cat,
                    month1_amount=round(amt1, 2),
                    month2_amount=round(amt2, 2),
                    delta_amount=diff,
                    delta_percentage=pct,
                    trend=trend,
                )
            )

        # Top increases (where you spent more in month 2)
        top_increases = sorted([v for v in variations if v.delta_amount > 0], key=lambda x: x.delta_amount, reverse=True)[:3]
        # Top savings (where you spent less in month 2, most negative delta)
        top_savings = sorted([v for v in variations if v.delta_amount < 0], key=lambda x: x.delta_amount)[:3]

        inc_str = ", ".join([f"{v.category_name} (+{v.delta_amount:.2f}€)" for v in top_increases]) or "Ninguna"
        sav_str = ", ".join([f"{v.category_name} ({v.delta_amount:.2f}€)" for v in top_savings]) or "Ninguna"

        analysis = (
            f"Comparativa entre {m1_name} y {m2_name}: "
            f"El gasto total varió en {expenses_delta:+.2f}€ ({exp1:.2f}€ -> {exp2:.2f}€). "
            f"El ahorro neto varió en {savings_delta:+.2f}€ ({sav1:.2f}€ -> {sav2:.2f}€). "
            f"Categorías con mayor incremento de gasto: {inc_str}. "
            f"Categorías con mayor reducción de gasto: {sav_str}."
        )

        return MonthComparisonDTO(
            period1=m1_name,
            period2=m2_name,
            income_period1=inc1,
            income_period2=inc2,
            income_delta=income_delta,
            expenses_period1=exp1,
            expenses_period2=exp2,
            expenses_delta=expenses_delta,
            savings_period1=sav1,
            savings_period2=sav2,
            savings_delta=savings_delta,
            savings_rate_period1=rate1,
            savings_rate_period2=rate2,
            top_increases=top_increases,
            top_savings=top_savings,
            executive_analysis=analysis,
        )

    async def get_expense_anomalies(self, limit: int = 10) -> List[AnomalyDTO]:
        """Retrieves anomalous transactions detected by statistical IQR engine."""
        data = await http_client.get("/analytics/anomalies", params={"limit": limit})
        categories = await category_service.list_categories()
        cat_map = {c.id: c.name for c in categories}
        anomalies: List[AnomalyDTO] = []

        for item in data:
            cat_id = str(item.get("category_id", ""))
            anomalies.append(
                AnomalyDTO(
                    transaction_id=str(item.get("id")),
                    date=str(item.get("transaction_date", ""))[:10],
                    description=item.get("description", "Sin descripción"),
                    amount=float(item.get("amount", 0.0)),
                    category_name=cat_map.get(cat_id, "Desconocida"),
                    account_name=str(item.get("account_id")),
                    reason="Importe significativamente superior al rango intercuartílico (IQR) habitual para esta categoría.",
                )
            )

        return anomalies

analytics_service = AnalyticsService()
