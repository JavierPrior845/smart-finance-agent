from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.db.models.transaction import TransactionORM
from src.infrastructure.adapters.db.models.account import AccountORM
from src.infrastructure.adapters.db.models.category import CategoryORM
from src.infrastructure.adapters.db.models.setting import AppSettingORM

class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_kpis(self) -> Dict[str, Any]:
        """Calculates global KPIs: Total Net Worth (liquid), Monthly Income, Monthly Expenses."""
        now = datetime.now(timezone.utc)
        start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        # 1. Total Liquid Net Worth (Sum of all account balances)
        stmt_nw = select(func.sum(AccountORM.current_balance))
        result_nw = await self.session.execute(stmt_nw)
        net_worth = result_nw.scalar_one_or_none() or 0.0

        # 2. Monthly Income
        stmt_income = select(func.sum(TransactionORM.amount)).where(
            and_(
                TransactionORM.type == "INCOME",
                TransactionORM.transaction_date >= start_of_month
            )
        )
        result_income = await self.session.execute(stmt_income)
        monthly_income = result_income.scalar_one_or_none() or 0.0

        # 3. Monthly Expenses
        stmt_expenses = select(func.sum(TransactionORM.amount)).where(
            and_(
                TransactionORM.type == "EXPENSE",
                TransactionORM.transaction_date >= start_of_month
            )
        )
        result_expenses = await self.session.execute(stmt_expenses)
        monthly_expenses = abs(result_expenses.scalar_one_or_none() or 0.0)

        # 4. Savings Rate
        savings_rate = 0.0
        if monthly_income > 0:
            savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100
        
        # Calculate previous month limits
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        start_of_prev_month = datetime(prev_year, prev_month, 1, tzinfo=timezone.utc)
        
        # 5. Previous Monthly Income
        stmt_prev_inc = select(func.sum(TransactionORM.amount)).where(
            and_(
                TransactionORM.type == "INCOME",
                TransactionORM.transaction_date >= start_of_prev_month,
                TransactionORM.transaction_date < start_of_month
            )
        )
        prev_income = (await self.session.execute(stmt_prev_inc)).scalar_one_or_none() or 0.0
        
        # 6. Previous Monthly Expenses
        stmt_prev_exp = select(func.sum(TransactionORM.amount)).where(
            and_(
                TransactionORM.type == "EXPENSE",
                TransactionORM.transaction_date >= start_of_prev_month,
                TransactionORM.transaction_date < start_of_month
            )
        )
        prev_expenses = abs((await self.session.execute(stmt_prev_exp)).scalar_one_or_none() or 0.0)

        # 7. Calculate Trends
        income_trend = None
        if prev_income > 0:
            income_trend = ((float(monthly_income) - float(prev_income)) / float(prev_income)) * 100
            
        expenses_trend = None
        if prev_expenses > 0:
            expenses_trend = ((float(monthly_expenses) - float(prev_expenses)) / float(prev_expenses)) * 100

        # 8. Target Savings Rate
        stmt_target = select(AppSettingORM).where(AppSettingORM.key == "target_savings_rate")
        target_setting = (await self.session.execute(stmt_target)).scalar_one_or_none()
        target_savings_rate = float(target_setting.value) if target_setting else 50.0
        
        return {
            "net_worth": float(net_worth),
            "monthly_income": float(monthly_income),
            "monthly_expenses": float(monthly_expenses),
            "savings_rate": float(savings_rate),
            "income_trend": income_trend,
            "expenses_trend": expenses_trend,
            "net_worth_trend": None,
            "target_savings_rate": target_savings_rate
        }

    async def get_expense_distribution(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Returns expenses grouped by category for the given period."""
        stmt = (
            select(
                CategoryORM.name,
                CategoryORM.color,
                func.sum(TransactionORM.amount).label("total")
            )
            .join(TransactionORM, TransactionORM.category_id == CategoryORM.id)
            .where(
                and_(
                    TransactionORM.type == "EXPENSE",
                    TransactionORM.transaction_date >= start_date,
                    TransactionORM.transaction_date <= end_date
                )
            )
            .group_by(CategoryORM.id)
            .order_by(func.sum(TransactionORM.amount).asc())
        )
        result = await self.session.execute(stmt)
        
        distribution = []
        for row in result:
            distribution.append({
                "name": row.name,
                "value": abs(float(row.total)),
                "color": row.color or "#cccccc"
            })
        return distribution

    async def get_historical_cashflow(self, months: int = 6) -> List[Dict[str, Any]]:
        """Returns monthly income and expenses for the last N months."""
        # Note: A real implementation might require a calendar table to guarantee all months are returned,
        # but here we aggregate by year/month of existing transactions.
        
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=30 * months)
        
        stmt = (
            select(
                extract('year', TransactionORM.transaction_date).label('year'),
                extract('month', TransactionORM.transaction_date).label('month'),
                TransactionORM.type,
                func.sum(TransactionORM.amount).label('total')
            )
            .where(TransactionORM.transaction_date >= start_date)
            .group_by('year', 'month', TransactionORM.type)
            .order_by('year', 'month')
        )
        
        result = await self.session.execute(stmt)
        
        # Aggregate in Python for easy formatting
        monthly_data = {}
        month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        for row in result:
            key = f"{int(row.year)}-{int(row.month):02d}"
            if key not in monthly_data:
                monthly_data[key] = {
                    "month": f"{month_names[int(row.month)-1]}",
                    "sort_key": key,
                    "ingresos": 0.0,
                    "gastos": 0.0
                }
                
            val = float(row.total)
            if row.type == "INCOME":
                monthly_data[key]["ingresos"] += val
            elif row.type == "EXPENSE":
                monthly_data[key]["gastos"] += abs(val)
                
        # Sort and remove the sort_key
        sorted_data = sorted(monthly_data.values(), key=lambda x: x["sort_key"])
        return [{"month": d["month"], "ingresos": d["ingresos"], "gastos": d["gastos"]} for d in sorted_data]

    async def get_pacing(self) -> List[Dict[str, Any]]:
        """Returns cumulative daily spending for the current month vs previous month."""
        now = datetime.now(timezone.utc)
        
        # Current month limits
        curr_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        
        # Previous month limits
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        prev_start = datetime(prev_year, prev_month, 1, tzinfo=timezone.utc)
        prev_end = curr_start - timedelta(seconds=1)
        
        # Fetch current month expenses
        stmt_curr = select(extract('day', TransactionORM.transaction_date).label('day'), func.sum(TransactionORM.amount))\
            .where(and_(TransactionORM.type == 'EXPENSE', TransactionORM.transaction_date >= curr_start))\
            .group_by('day').order_by('day')
            
        # Fetch prev month expenses
        stmt_prev = select(extract('day', TransactionORM.transaction_date).label('day'), func.sum(TransactionORM.amount))\
            .where(and_(TransactionORM.type == 'EXPENSE', TransactionORM.transaction_date >= prev_start, TransactionORM.transaction_date <= prev_end))\
            .group_by('day').order_by('day')

        curr_res = await self.session.execute(stmt_curr)
        prev_res = await self.session.execute(stmt_prev)
        
        curr_daily = {int(row[0]): abs(float(row[1])) for row in curr_res}
        prev_daily = {int(row[0]): abs(float(row[1])) for row in prev_res}
        
        # Build cumulative array up to 31 days
        pacing_data = []
        cum_curr = 0.0
        cum_prev = 0.0
        
        for day in range(1, 32):
            # Only add to current cumulative if day <= today
            if day <= now.day:
                cum_curr += curr_daily.get(day, 0.0)
                
            cum_prev += prev_daily.get(day, 0.0)
            
            pacing_data.append({
                "day": day,
                "mesActual": round(cum_curr, 2) if day <= now.day else None,
                "mesAnterior": round(cum_prev, 2)
            })
            
        return pacing_data
