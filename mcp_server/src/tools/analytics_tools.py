from mcp.server.fastmcp import FastMCP
from src.models.analytics import MonthlyReportInput, CompareMonthsInput
from src.services.analytics_service import analytics_service

def register(mcp: FastMCP) -> None:
    """Registers analytics tools into FastMCP server."""

    @mcp.tool(
        name="get_monthly_report",
        description="Genera un informe financiero mensual completo (ingresos, gastos, ahorro neto, tasa de ahorro y desglose de principales gastos).",
    )
    async def get_monthly_report(
        year: int,
        month: int,
    ) -> str:
        """Args:
            year: Año a consultar (ej. 2026).
            month: Mes numérico del 1 al 12 (ej. 8 para agosto, 9 para septiembre).
        """
        try:
            input_data = MonthlyReportInput(year=year, month=month)
            report = await analytics_service.get_monthly_report(input_data)

            lines = [
                f"=== INFORME FINANCIERO MENSUAL: {report.period.upper()} ===",
                f"📈 Ingresos Totales:  {report.total_income:.2f}€",
                f"📉 Gastos Totales:    {report.total_expenses:.2f}€",
                f"💰 Ahorro Neto:       {report.net_savings:+.2f}€",
                f"🎯 Tasa de Ahorro:    {report.savings_rate_percentage:.1f}%",
                f"⚠️ Gastos Anómalos:   {report.anomalies_count}",
                "",
                "Top Categorías de Gasto:",
            ]

            if report.top_categories:
                for cat in report.top_categories:
                    lines.append(f"- {cat.category_name}: {cat.amount:.2f}€ ({cat.percentage:.1f}%)")
            else:
                lines.append("- Sin gastos registrados este período.")

            lines.append("")
            lines.append(f"Resumen Ejecutivo:\n{report.executive_summary}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error al generar informe mensual: {str(e)}"

    @mcp.tool(
        name="compare_months",
        description="Compara el rendimiento financiero entre dos meses distintos, calculando variaciones en gasto, ahorro y qué categorías subieron o bajaron.",
    )
    async def compare_months(
        year1: int,
        month1: int,
        year2: int,
        month2: int,
    ) -> str:
        """Args:
            year1: Año del primer mes de referencia (ej. 2026).
            month1: Mes del primer mes de referencia (1 a 12).
            year2: Año del segundo mes a contrastar (ej. 2026).
            month2: Mes del segundo mes a contrastar (1 a 12).
        """
        try:
            input_data = CompareMonthsInput(
                year1=year1,
                month1=month1,
                year2=year2,
                month2=month2,
            )
            comp = await analytics_service.compare_months(input_data)

            lines = [
                f"=== COMPARATIVA: {comp.period1.upper()} vs {comp.period2.upper()} ===",
                f"Ingresos:  {comp.income_period1:.2f}€ -> {comp.income_period2:.2f}€ (Variación: {comp.income_delta:+.2f}€)",
                f"Gastos:    {comp.expenses_period1:.2f}€ -> {comp.expenses_period2:.2f}€ (Variación: {comp.expenses_delta:+.2f}€)",
                f"Ahorro:    {comp.savings_period1:.2f}€ -> {comp.savings_period2:.2f}€ (Variación: {comp.savings_delta:+.2f}€)",
                f"Tasa Ahorro: {comp.savings_rate_period1:.1f}% -> {comp.savings_rate_period2:.1f}%",
                "",
                "📈 Categorías con Mayor Incremento de Gasto:",
            ]

            if comp.top_increases:
                for v in comp.top_increases:
                    lines.append(f"- {v.category_name}: +{v.delta_amount:.2f}€ ({v.month1_amount:.2f}€ -> {v.month2_amount:.2f}€)")
            else:
                lines.append("- Ningún incremento relevante.")

            lines.append("")
            lines.append("📉 Categorías con Mayor Reducción de Gasto (Ahorro):")
            if comp.top_savings:
                for v in comp.top_savings:
                    lines.append(f"- {v.category_name}: {v.delta_amount:.2f}€ ({v.month1_amount:.2f}€ -> {v.month2_amount:.2f}€)")
            else:
                lines.append("- Ninguna reducción relevante.")

            lines.append("")
            lines.append(f"Conclusión Analítica:\n{comp.executive_analysis}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error al comparar meses: {str(e)}"

    @mcp.tool(
        name="get_expense_anomalies",
        description="Consulta los gastos atípicos o anomalías detectadas por el algoritmo estadístico IQR.",
    )
    async def get_expense_anomalies(
        limit: int = 10,
    ) -> str:
        """Args:
            limit: Número máximo de anomalías recientes a recuperar (1 a 50).
        """
        try:
            anomalies = await analytics_service.get_expense_anomalies(limit=limit)
            if not anomalies:
                return "No se han detectado gastos anómalos pendientes en el sistema."

            lines = [f"Gastos anómalos detectados ({len(anomalies)}):"]
            for a in anomalies:
                lines.append(
                    f"- [{a.date}] {a.amount:.2f}€ | '{a.description}' | Categoría: {a.category_name} (ID: {a.transaction_id})"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error al consultar anomalías: {str(e)}"
