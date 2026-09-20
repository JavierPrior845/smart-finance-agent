import asyncio
import random
import uuid
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.db.session import AsyncSessionLocal, engine
from src.infrastructure.adapters.db.models.base import Base
from src.infrastructure.adapters.db.models.account import AccountORM
from src.infrastructure.adapters.db.models.category import CategoryORM
from src.infrastructure.adapters.db.models.transaction import TransactionORM
from src.infrastructure.adapters.db.models.budget import BudgetORM
from src.infrastructure.adapters.db.models.investment import (
    InvestmentAssetORM,
    InvestmentMovementORM,
    InvestmentSnapshotORM,
)
from src.infrastructure.adapters.db.models.merchant_rule import MerchantRuleORM
from src.infrastructure.adapters.db.models.setting import AppSettingORM


async def seed():
    print("Iniciando sembrado completo de base de datos...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # Sellar versión de Alembic para mantener integridad de migraciones
        await conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) PRIMARY KEY);"
            )
        )
        await conn.execute(
            text(
                "INSERT INTO alembic_version (version_num) VALUES ('1320dac35b2e') ON CONFLICT DO NOTHING;"
            )
        )
        print("Tablas recreadas y versión de Alembic sellada (1320dac35b2e).")

    async with AsyncSessionLocal() as session:
        # ==========================================
        # 1. Configuración Global (Settings)
        # ==========================================
        settings = [
            AppSettingORM(
                key="target_savings_rate",
                value="25.0",
                description="Tasa de ahorro mensual objetivo (%)",
            ),
            AppSettingORM(
                key="default_currency",
                value="EUR",
                description="Moneda principal del sistema",
            ),
        ]
        session.add_all(settings)
        await session.flush()
        print("Configuraciones del sistema creadas.")

        # ==========================================
        # 2. Cuentas Financieras (Accounts)
        # ==========================================
        acc_main = AccountORM(
            name="Cuenta Nómina BBVA",
            account_type="BANK",
            currency="EUR",
            initial_balance=2500.00,
            current_balance=4120.50,
            is_main=True,
            is_active=True,
        )
        acc_savings = AccountORM(
            name="Cuenta Ahorro / Emergencia",
            account_type="BANK",
            currency="EUR",
            initial_balance=6000.00,
            current_balance=8400.00,
            is_main=False,
            is_active=True,
        )
        acc_broker = AccountORM(
            name="Trade Republic Cash",
            account_type="INVESTMENT",
            currency="EUR",
            initial_balance=500.00,
            current_balance=1250.00,
            is_main=False,
            is_active=True,
        )
        acc_cash = AccountORM(
            name="Efectivo en Mano",
            account_type="CASH",
            currency="EUR",
            initial_balance=150.00,
            current_balance=95.00,
            is_main=False,
            is_active=True,
        )

        session.add_all([acc_main, acc_savings, acc_broker, acc_cash])
        await session.flush()
        print(f"Cuentas creadas: {acc_main.name}, {acc_savings.name}, {acc_broker.name}, {acc_cash.name}")

        # ==========================================
        # 3. Categorías (Gastos e Ingresos con límites/metas)
        # ==========================================
        cats_def = [
            # Gastos (EXPENSE)
            ("Vivienda", "#8a2be2", 950.0, "EXPENSE", "home"),
            ("Alimentación", "#00f5d4", 450.0, "EXPENSE", "shopping-cart"),
            ("Ocio y Restaurantes", "#ff007f", 250.0, "EXPENSE", "coffee"),
            ("Transporte", "#ffbe0b", 130.0, "EXPENSE", "truck"),
            ("Suscripciones & Tech", "#6366f1", 85.0, "EXPENSE", "cpu"),
            ("Salud y Bienestar", "#ec4899", 100.0, "EXPENSE", "activity"),
            ("Otros Gastos", "#9ca3af", 100.0, "EXPENSE", "help-circle"),
            # Ingresos (INCOME)
            ("Nómina Principal", "#22c55e", None, "INCOME", "dollar-sign"),
            ("Proyectos Freelance", "#10b981", 1200.0, "INCOME", "briefcase"), # Meta de ingreso Fase 4.5
            ("Inversiones & Dividendos", "#3b82f6", None, "INCOME", "trending-up"),
            ("Bizum & Reembolsos", "#14b8a6", None, "INCOME", "repeat"),
        ]

        categories = {}
        for name, color, limit, cat_type, icon in cats_def:
            cat = CategoryORM(
                name=name,
                color=color,
                default_budget_limit=limit,
                type=cat_type,
                icon=icon,
                is_budgetable=True,
                is_active=True,
            )
            session.add(cat)
            categories[name] = cat

        await session.flush()
        print(f"Categorías creadas ({len(categories)} categorías).")

        # ==========================================
        # 4. Reglas de Comerciantes (Merchant Rules)
        # ==========================================
        rules_data = [
            ("MERCADONA", categories["Alimentación"].id, 10),
            ("CARREFOUR", categories["Alimentación"].id, 10),
            ("LIDL", categories["Alimentación"].id, 10),
            ("SPOTIFY", categories["Suscripciones & Tech"].id, 10),
            ("NETFLIX", categories["Suscripciones & Tech"].id, 10),
            ("UBER", categories["Transporte"].id, 10),
            ("RENFE", categories["Transporte"].id, 10),
            ("RESTAURANTE", categories["Ocio y Restaurantes"].id, 5),
            ("NOMINA", categories["Nómina Principal"].id, 20),
        ]
        for pattern, cat_id, priority in rules_data:
            rule = MerchantRuleORM(
                pattern=pattern,
                category_id=cat_id,
                priority=priority
            )
            session.add(rule)
        await session.flush()
        print("Reglas de categorización automática registradas.")

        # ==========================================
        # 5. Presupuestos Mensuales (Budgets)
        # Historial de presupuestos para los últimos 6 meses
        # ==========================================
        now = datetime.now(timezone.utc)
        budgetable_cats = [
            ("Vivienda", 950.0),
            ("Alimentación", 450.0),
            ("Ocio y Restaurantes", 250.0),
            ("Transporte", 130.0),
            ("Suscripciones & Tech", 85.0),
            ("Salud y Bienestar", 100.0),
            ("Proyectos Freelance", 1200.0), # Meta de ingresos
        ]

        for offset in range(6):
            target_date = now - timedelta(days=30 * offset)
            m = target_date.month
            y = target_date.year

            for cat_name, limit in budgetable_cats:
                budget = BudgetORM(
                    category_id=categories[cat_name].id,
                    monthly_limit=limit,
                    period_month=m,
                    period_year=y,
                )
                session.add(budget)

        await session.flush()
        print("Presupuestos mensuales generados para los últimos 6 meses.")

        # ==========================================
        # 6. Historial de Transacciones (6 meses)
        # Probando: Gastos regulares, Nóminas, Freelance con costes netos,
        # Reembolsos Bizum (Fase 4.5), Transferencias y Anomalías
        # ==========================================
        for month_offset in range(5, -1, -1):
            target_date = now - timedelta(days=30 * month_offset)
            year = target_date.year
            month = target_date.month

            # 6.1 Nómina mensual (Día 1)
            payroll_date = datetime(year, month, 1, 9, 30, 0, tzinfo=timezone.utc)
            payroll_tx = TransactionORM(
                account_id=acc_main.id,
                type="INCOME",
                amount=2650.00,
                description="Ingreso Nómina mensual Empresa Tech S.L.",
                category_id=categories["Nómina Principal"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=True,
                is_anomalous=False,
                transaction_date=payroll_date,
            )
            session.add(payroll_tx)

            # 6.2 Alquiler vivienda (Día 5)
            rent_date = datetime(year, month, 5, 10, 0, 0, tzinfo=timezone.utc)
            rent_tx = TransactionORM(
                account_id=acc_main.id,
                type="EXPENSE",
                amount=-850.00,
                description="Transferencia Pago Alquiler Piso",
                category_id=categories["Vivienda"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=True,
                is_anomalous=False,
                transaction_date=rent_date,
            )
            session.add(rent_tx)

            # 6.3 Factura Suministros e Internet (Día 6)
            bills_date = datetime(year, month, 6, 12, 15, 0, tzinfo=timezone.utc)
            bills_tx = TransactionORM(
                account_id=acc_main.id,
                type="EXPENSE",
                amount=-75.50,
                description="Recibo Luz y Fibra Digi",
                category_id=categories["Vivienda"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=True,
                is_anomalous=False,
                transaction_date=bills_date,
            )
            session.add(bills_tx)

            # 6.4 Facturación Freelance (Fase 4.5: Ingreso en meta de ingresos)
            freelance_date = datetime(year, month, 8, 11, 0, 0, tzinfo=timezone.utc)
            freelance_tx = TransactionORM(
                account_id=acc_main.id,
                type="INCOME",
                amount=950.00 if month_offset != 1 else 1350.00,
                description="Factura #2026-F14 Proyecto Web E-Commerce",
                category_id=categories["Proyectos Freelance"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=False,
                is_anomalous=False,
                transaction_date=freelance_date,
            )
            session.add(freelance_tx)

            # 6.5 Coste derivado de Freelance (Fase 4.5: Gasto en categoría de ingreso -> resta del progreso neto)
            freelance_cost_date = datetime(year, month, 10, 16, 45, 0, tzinfo=timezone.utc)
            freelance_cost_tx = TransactionORM(
                account_id=acc_main.id,
                type="EXPENSE",
                amount=-120.00,
                description="Subcontratación diseño UI Figma Freelance",
                category_id=categories["Proyectos Freelance"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=False,
                is_anomalous=False,
                transaction_date=freelance_cost_date,
            )
            session.add(freelance_cost_tx)

            # 6.6 Traspaso mensual a Cuenta de Ahorro (TRANSFER entre cuentas)
            transfer_date = datetime(year, month, 7, 18, 0, 0, tzinfo=timezone.utc)
            transfer_tx = TransactionORM(
                account_id=acc_main.id,
                destination_account_id=acc_savings.id,
                type="TRANSFER",
                amount=-400.00,
                description="Traspaso mensual a Fondo de Emergencia",
                category_id=categories["Otros Gastos"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=True,
                is_anomalous=False,
                transaction_date=transfer_date,
            )
            session.add(transfer_tx)

            # 6.7 Suscripciones recurrentes (Spotify, Netflix)
            spot_date = datetime(year, month, 12, 8, 0, 0, tzinfo=timezone.utc)
            spot_tx = TransactionORM(
                account_id=acc_main.id,
                type="EXPENSE",
                amount=-10.99,
                description="SPOTIFY PREMIUM INDIVIDUAL",
                category_id=categories["Suscripciones & Tech"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=True,
                is_anomalous=False,
                transaction_date=spot_date,
            )
            session.add(spot_tx)

            netf_date = datetime(year, month, 15, 8, 0, 0, tzinfo=timezone.utc)
            netf_tx = TransactionORM(
                account_id=acc_main.id,
                type="EXPENSE",
                amount=-17.99,
                description="NETFLIX STANDARD PLAN",
                category_id=categories["Suscripciones & Tech"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=True,
                is_anomalous=False,
                transaction_date=netf_date,
            )
            session.add(netf_tx)

            # 6.8 Fase 4.5 Feedback: Cena con amigos y posterior Bizum de reembolso
            dinner_date = datetime(year, month, 14, 21, 30, 0, tzinfo=timezone.utc)
            dinner_tx = TransactionORM(
                account_id=acc_main.id,
                type="EXPENSE",
                amount=-85.00,
                description="Cena Restaurante Italiano Amigos",
                category_id=categories["Ocio y Restaurantes"].id,
                source="MANUAL",
                status="confirmed",
                is_recurring=False,
                is_anomalous=False,
                transaction_date=dinner_date,
            )
            session.add(dinner_tx)

            bizum_date = datetime(year, month, 15, 11, 20, 0, tzinfo=timezone.utc)
            bizum_tx = TransactionORM(
                account_id=acc_main.id,
                type="INCOME",
                amount=35.00,
                description="Bizum de Carlos parte de la cena",
                category_id=categories["Ocio y Restaurantes"].id, # Misma categoría de gasto para compensar flujo neto
                source="TELEGRAM",
                status="confirmed",
                is_recurring=False,
                is_anomalous=False,
                transaction_date=bizum_date,
            )
            session.add(bizum_tx)

            # 6.9 Gastos diarios de Alimentación, Transporte, Ocio (curva de Pacing)
            days_in_month = (now.day if month_offset == 0 else 28)
            for day in range(1, days_in_month + 1):
                if day in (1, 5, 6, 8, 10, 12, 14, 15):
                    continue

                # Alimentación frecuente
                if day % 3 == 0:
                    sup_amount = round(random.uniform(25.0, 75.0), 2)
                    sup_tx = TransactionORM(
                        account_id=acc_main.id,
                        type="EXPENSE",
                        amount=-sup_amount,
                        description=f"Compra supermercado {random.choice(['MERCADONA', 'CARREFOUR', 'LIDL'])}",
                        category_id=categories["Alimentación"].id,
                        source="MANUAL",
                        status="confirmed",
                        is_recurring=False,
                        is_anomalous=False,
                        transaction_date=datetime(year, month, day, 13, 10, 0, tzinfo=timezone.utc),
                    )
                    session.add(sup_tx)

                # Transporte ocasional
                if day % 5 == 0:
                    trans_amount = round(random.uniform(15.0, 40.0), 2)
                    trans_tx = TransactionORM(
                        account_id=acc_main.id,
                        type="EXPENSE",
                        amount=-trans_amount,
                        description=f"{random.choice(['Gasolina Repsol', 'UBER viaje ciudad', 'Bono Transporte RENFE'])}",
                        category_id=categories["Transporte"].id,
                        source="MANUAL",
                        status="confirmed",
                        is_recurring=False,
                        is_anomalous=False,
                        transaction_date=datetime(year, month, day, 9, 15, 0, tzinfo=timezone.utc),
                    )
                    session.add(trans_tx)

                # Ocio / Cafés
                if day % 4 == 0:
                    leisure_amount = round(random.uniform(12.0, 35.0), 2)
                    leisure_tx = TransactionORM(
                        account_id=acc_main.id,
                        type="EXPENSE",
                        amount=-leisure_amount,
                        description=f"{random.choice(['Cervezas Afterwork', 'Cine entradas fin de semana', 'Cafetería de especialidad'])}",
                        category_id=categories["Ocio y Restaurantes"].id,
                        source="MANUAL",
                        status="confirmed",
                        is_recurring=False,
                        is_anomalous=False,
                        transaction_date=datetime(year, month, day, 18, 45, 0, tzinfo=timezone.utc),
                    )
                    session.add(leisure_tx)

            # 6.10 Transacción Anómala (hace 2 meses) para alimentar el feed de anomalías
            if month_offset == 2:
                anom_date = datetime(year, month, 20, 17, 30, 0, tzinfo=timezone.utc)
                anom_tx = TransactionORM(
                    account_id=acc_main.id,
                    type="EXPENSE",
                    amount=-680.00,
                    description="Reparación urgente de caja de cambios Taller Auto",
                    category_id=categories["Transporte"].id,
                    source="MANUAL",
                    status="confirmed",
                    is_recurring=False,
                    is_anomalous=True, # Marcada como anómala
                    transaction_date=anom_date,
                )
                session.add(anom_tx)

        await session.flush()
        print("Transacciones de los últimos 6 meses generadas con éxito.")

        # ==========================================
        # 7. Inversiones Avanzadas (Fase 4.5: DCA, Ventas Parciales, PMP, Snapshots)
        # ==========================================
        
        # 7.1 Vanguard FTSE All-World UCITS ETF (VWCE) - Estrategia DCA mensual
        vwce_id = uuid.uuid4()
        asset_vwce = InvestmentAssetORM(
            id=vwce_id,
            name="Vanguard FTSE All-World ETF (VWCE)",
            ticker="VWCE.DE",
            asset_type="ETF",
            broker="Trade Republic",
            entry_date=now - timedelta(days=150),
            invested_amount=2170.00,
            units_qty=20.0,
            average_buy_price=108.50, # PMP resultante del DCA
            withdrawn_amount=0.00,
            realized_pnl=0.00,
            status="OPEN",
            source_account_id=acc_broker.id,
            created_at=now - timedelta(days=150),
        )
        session.add(asset_vwce)

        # Movimientos DCA de VWCE:
        # Mes -5: 10 unidades @ 105.00€ = 1050€
        # Mes -3: 5 unidades @ 110.00€ = 550€
        # Mes -1: 5 unidades @ 114.00€ = 570€
        vwce_mov1 = InvestmentMovementORM(
            asset_id=vwce_id,
            movement_type="BUY_MORE",
            amount=1050.00,
            units=10.0,
            unit_price=105.00,
            movement_date=now - timedelta(days=150),
            notes="Aportación inicial ETF Global",
        )
        vwce_mov2 = InvestmentMovementORM(
            asset_id=vwce_id,
            movement_type="BUY_MORE",
            amount=550.00,
            units=5.0,
            unit_price=110.00,
            movement_date=now - timedelta(days=90),
            notes="Aportación periódica DCA Trimestral",
        )
        vwce_mov3 = InvestmentMovementORM(
            asset_id=vwce_id,
            movement_type="BUY_MORE",
            amount=570.00,
            units=5.0,
            unit_price=114.00,
            movement_date=now - timedelta(days=30),
            notes="Aportación periódica DCA",
        )
        session.add_all([vwce_mov1, vwce_mov2, vwce_mov3])

        # 7.2 Apple Inc. (AAPL) - Compra, Venta Parcial y Dividendo
        aapl_id = uuid.uuid4()
        asset_aapl = InvestmentAssetORM(
            id=aapl_id,
            name="Apple Inc.",
            ticker="AAPL",
            asset_type="STOCK",
            broker="Trade Republic",
            entry_date=now - timedelta(days=120),
            invested_amount=1020.00, # 1700€ iniciales - 680€ coste proporcional vendido
            units_qty=6.0,           # 10 - 4 vendidas
            average_buy_price=170.00,# PMP conservado
            withdrawn_amount=840.00, # 4 vendidas @ 210€
            realized_pnl=160.00,     # 840€ venta - 680€ coste
            status="OPEN",
            source_account_id=acc_broker.id,
            created_at=now - timedelta(days=120),
        )
        session.add(asset_aapl)

        aapl_mov1 = InvestmentMovementORM(
            asset_id=aapl_id,
            movement_type="BUY_MORE",
            amount=1700.00,
            units=10.0,
            unit_price=170.00,
            movement_date=now - timedelta(days=120),
            notes="Compra de 10 acciones AAPL",
        )
        aapl_mov2 = InvestmentMovementORM(
            asset_id=aapl_id,
            movement_type="SELL",
            amount=840.00,
            units=4.0,
            unit_price=210.00,
            movement_date=now - timedelta(days=50),
            notes="Toma parcial de beneficios (4 acciones)",
        )
        aapl_mov3 = InvestmentMovementORM(
            asset_id=aapl_id,
            movement_type="DIVIDEND",
            amount=15.60,
            units=None,
            unit_price=None,
            movement_date=now - timedelta(days=20),
            notes="Cobro de dividendos Q3",
        )
        session.add_all([aapl_mov1, aapl_mov2, aapl_mov3])

        # 7.3 Bitcoin (BTC) - Criptoactivo con DCA
        btc_id = uuid.uuid4()
        asset_btc = InvestmentAssetORM(
            id=btc_id,
            name="Bitcoin",
            ticker="BTC",
            asset_type="CRYPTO",
            broker="Binance",
            entry_date=now - timedelta(days=90),
            invested_amount=3800.00,
            units_qty=0.065,
            average_buy_price=58461.54,
            withdrawn_amount=0.00,
            realized_pnl=0.00,
            status="OPEN",
            source_account_id=acc_main.id,
            created_at=now - timedelta(days=90),
        )
        session.add(asset_btc)

        btc_mov1 = InvestmentMovementORM(
            asset_id=btc_id,
            movement_type="BUY_MORE",
            amount=2600.00,
            units=0.045,
            unit_price=57777.77,
            movement_date=now - timedelta(days=90),
            notes="Compra inicial BTC",
        )
        btc_mov2 = InvestmentMovementORM(
            asset_id=btc_id,
            movement_type="BUY_MORE",
            amount=1200.00,
            units=0.020,
            unit_price=60000.00,
            movement_date=now - timedelta(days=35),
            notes="Compra DCA caída de mercado",
        )
        session.add_all([btc_mov1, btc_mov2])

        # 7.4 Posición Cerrada: Tesla Inc. (TSLA)
        tsla_id = uuid.uuid4()
        asset_tsla = InvestmentAssetORM(
            id=tsla_id,
            name="Tesla Inc.",
            ticker="TSLA",
            asset_type="STOCK",
            broker="Trade Republic",
            entry_date=now - timedelta(days=160),
            exit_date=now - timedelta(days=60),
            invested_amount=0.00,
            units_qty=0.0,
            average_buy_price=200.00,
            withdrawn_amount=1200.00,
            realized_pnl=200.00,
            status="CLOSED",
            source_account_id=acc_broker.id,
            created_at=now - timedelta(days=160),
        )
        session.add(asset_tsla)

        tsla_mov1 = InvestmentMovementORM(
            asset_id=tsla_id,
            movement_type="BUY_MORE",
            amount=1000.00,
            units=5.0,
            unit_price=200.00,
            movement_date=now - timedelta(days=160),
            notes="Compra Swing trade TSLA",
        )
        tsla_mov2 = InvestmentMovementORM(
            asset_id=tsla_id,
            movement_type="SELL",
            amount=1200.00,
            units=5.0,
            unit_price=240.00,
            movement_date=now - timedelta(days=60),
            notes="Cierre total de posición con +20% de beneficio",
        )
        session.add_all([tsla_mov1, tsla_mov2])

        # ==========================================
        # 8. Snapshots de Inversión Históricos (Evolución de Net Worth)
        # Snapshots periódicos para VWCE, AAPL y BTC para las gráficas
        # ==========================================
        snapshots_data = [
            # Mes -4
            (vwce_id, now - timedelta(days=120), 107.00, 10 * 107.00),
            (aapl_id, now - timedelta(days=120), 175.00, 10 * 175.00),
            # Mes -3
            (vwce_id, now - timedelta(days=90), 109.50, 15 * 109.50),
            (aapl_id, now - timedelta(days=90), 188.00, 10 * 188.00),
            (btc_id, now - timedelta(days=90), 58200.00, 0.045 * 58200.00),
            # Mes -2
            (vwce_id, now - timedelta(days=60), 112.00, 15 * 112.00),
            (aapl_id, now - timedelta(days=60), 205.00, 10 * 205.00),
            (btc_id, now - timedelta(days=60), 61000.00, 0.045 * 61000.00),
            # Mes -1
            (vwce_id, now - timedelta(days=30), 115.00, 20 * 115.00),
            (aapl_id, now - timedelta(days=30), 218.00, 6 * 218.00),
            (btc_id, now - timedelta(days=30), 63500.00, 0.065 * 63500.00),
            # Mes Actual
            (vwce_id, now - timedelta(days=2), 119.50, 20 * 119.50),
            (aapl_id, now - timedelta(days=2), 226.00, 6 * 226.00),
            (btc_id, now - timedelta(days=2), 65200.00, 0.065 * 65200.00),
        ]

        for asset_id, dt_val, price, total_val in snapshots_data:
            snap = InvestmentSnapshotORM(
                asset_id=asset_id,
                snapshot_date=dt_val.date(),
                price=price,
                total_value=round(total_val, 2),
                created_at=dt_val,
            )
            session.add(snap)

        await session.commit()
        print("Base de datos sembrada con éxito con datos realistas completos.")


if __name__ == "__main__":
    asyncio.run(seed())
