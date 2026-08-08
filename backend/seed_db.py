import asyncio
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.infrastructure.adapters.db.session import AsyncSessionLocal, engine
from src.infrastructure.adapters.db.models.base import Base
from src.infrastructure.adapters.db.models.account import AccountORM
from src.infrastructure.adapters.db.models.category import CategoryORM
from src.infrastructure.adapters.db.models.transaction import TransactionORM
from src.infrastructure.adapters.db.models.setting import AppSettingORM

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tablas recreadas.")

    async with AsyncSessionLocal() as session:
        # 0. Crear Setting
        setting = AppSettingORM(key="target_savings_rate", value="20.0", description="Tasa de ahorro objetivo (%)")
        session.add(setting)
        await session.flush()
        
        # 1. Crear Cuenta
        account = AccountORM(
            name="Cuenta Nómina",
            account_type="BANK",
            currency="EUR",
            initial_balance=1000.00,
            current_balance=4500.00,
            is_main=True
        )
        session.add(account)
        await session.flush()
        print("Cuenta creada.")

        # 2. Crear Categorías
        cats_data = [
            ("Vivienda", "#8a2be2", 1000.0),
            ("Alimentación", "#00f5d4", 400.0),
            ("Ocio", "#ff007f", 200.0),
            ("Transporte", "#ffbe0b", 150.0),
            ("Nómina", "#4ade80", None),
        ]
        
        categories = {}
        for name, color, limit in cats_data:
            cat = CategoryORM(name=name, color=color, default_budget_limit=limit)
            session.add(cat)
            categories[name] = cat
        
        await session.flush()
        print("Categorías creadas.")

        # 3. Generar Transacciones para los últimos 6 meses
        now = datetime.now(timezone.utc)
        
        for month_offset in range(6):
            target_date = now - timedelta(days=30 * month_offset)
            year = target_date.year
            month = target_date.month
            
            # Ingreso mensual
            income_date = datetime(year, month, 1, 10, 0, 0, tzinfo=timezone.utc)
            inc = TransactionORM(
                account_id=account.id,
                type="INCOME",
                amount=3000.00,
                description="Nómina Mensual",
                category_id=categories["Nómina"].id,
                source="SEED",
                transaction_date=income_date
            )
            session.add(inc)

            # Gastos (Alquiler el día 5)
            rent_date = datetime(year, month, 5, 10, 0, 0, tzinfo=timezone.utc)
            rent = TransactionORM(
                account_id=account.id,
                type="EXPENSE",
                amount=-850.00,
                description="Alquiler",
                category_id=categories["Vivienda"].id,
                source="SEED",
                transaction_date=rent_date
            )
            session.add(rent)

            # Gastos variables durante el mes (Pacing)
            # Para el mes actual y el anterior, generamos gastos casi todos los días
            days_in_month = (now.day if month_offset == 0 else 28)
            
            for day in range(1, days_in_month + 1):
                if day == 5: continue # Ya pagamos el alquiler
                
                # Probabilidad de gasto del 70%
                if random.random() < 0.7:
                    cat_name = random.choice(["Alimentación", "Ocio", "Transporte"])
                    amt = round(random.uniform(10, 80), 2)
                    
                    tx_date = datetime(year, month, day, 14, 0, 0, tzinfo=timezone.utc)
                    tx = TransactionORM(
                        account_id=account.id,
                        type="EXPENSE",
                        amount=-amt,
                        description=f"Gasto en {cat_name}",
                        category_id=categories[cat_name].id,
                        source="SEED",
                        transaction_date=tx_date
                    )
                    session.add(tx)

        await session.commit()
        print("Transacciones generadas y DB guardada con éxito.")

if __name__ == "__main__":
    asyncio.run(seed())
