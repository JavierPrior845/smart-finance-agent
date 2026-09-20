import pytest
import uuid
from datetime import datetime, timezone
from src.domain.models.investment import InvestmentAsset, InvestmentMovement
from src.application.use_cases.manage_investment import ManageInvestmentUseCase
from src.infrastructure.api.v1.schemas.investment import InvestmentCreate, InvestmentBuyMore, InvestmentSellPartial, InvestmentClose

class MockInvestmentRepository:
    def __init__(self):
        self.assets = {}
        self.movements = []

    async def get_all_assets(self):
        return list(self.assets.values())

    async def get_asset(self, asset_id: uuid.UUID):
        return self.assets.get(asset_id)

    async def create_asset(self, asset: InvestmentAsset):
        self.assets[asset.id] = asset
        return asset

    async def update_asset(self, asset: InvestmentAsset):
        self.assets[asset.id] = asset
        return asset

    async def create_movement(self, movement: InvestmentMovement):
        self.movements.append(movement)
        return movement

    async def get_movements_by_asset(self, asset_id: uuid.UUID):
        return [m for m in self.movements if m.asset_id == asset_id]

    async def get_active_assets(self):
        return [a for a in self.assets.values() if a.status == 'OPEN']

    async def get_latest_snapshot_date(self, asset_id):
        return None

    async def save_snapshot(self, snapshot):
        return snapshot

    async def save_snapshots_bulk(self, snapshots):
        pass

class MockCreateTransactionUseCase:
    async def execute(self, **kwargs):
        pass

@pytest.mark.asyncio
async def test_investment_initial_creation():
    repo = MockInvestmentRepository()
    use_case = ManageInvestmentUseCase(repo, MockCreateTransactionUseCase())

    data = InvestmentCreate(
        name="Apple Inc",
        ticker="AAPL",
        asset_type="ACCION",
        broker="Trade Republic",
        invested_amount=1000.0,
        units_qty=10.0,
        average_buy_price=100.0
    )

    asset = await use_case.create_investment(data)
    assert asset.invested_amount == 1000.0
    assert asset.units_qty == 10.0
    assert asset.average_buy_price == 100.0
    assert asset.status == "OPEN"

@pytest.mark.asyncio
async def test_investment_dca_buy_more_recalculates_pmp():
    repo = MockInvestmentRepository()
    use_case = ManageInvestmentUseCase(repo, MockCreateTransactionUseCase())

    # Compra 1: 10 u a 100€ (Coste 1000€)
    data = InvestmentCreate(
        name="Bitcoin",
        ticker="BTC",
        asset_type="CRIPTO",
        broker="Binance",
        invested_amount=1000.0,
        units_qty=10.0,
        average_buy_price=100.0
    )
    asset = await use_case.create_investment(data)

    # Compra 2 (DCA): 10 u a 200€ (Coste 2000€)
    buy_data = InvestmentBuyMore(units=10.0, unit_price=200.0, notes="DCA 2")
    updated_asset = await use_case.buy_more(asset.id, buy_data)

    # Total invertido: 3000€, Unidades: 20, Nuevo PMP: 3000 / 20 = 150€
    assert updated_asset.units_qty == 20.0
    assert updated_asset.invested_amount == 3000.0
    assert updated_asset.average_buy_price == 150.0

@pytest.mark.asyncio
async def test_investment_partial_sale_realized_pnl():
    repo = MockInvestmentRepository()
    use_case = ManageInvestmentUseCase(repo, MockCreateTransactionUseCase())

    # Compra: 20 u con PMP 150€ (Invertido 3000€)
    data = InvestmentCreate(
        name="Bitcoin",
        ticker="BTC",
        asset_type="CRIPTO",
        broker="Binance",
        invested_amount=3000.0,
        units_qty=20.0,
        average_buy_price=150.0
    )
    asset = await use_case.create_investment(data)

    # Venta parcial: 5 u a 300€ (Ingreso 1500€, Coste 5 * 150 = 750€ -> PnL +750€)
    sell_data = InvestmentSellPartial(units=5.0, unit_price=300.0, notes="Venta parcial")
    updated_asset = await use_case.sell_units(asset.id, sell_data)

    assert updated_asset.units_qty == 15.0
    assert updated_asset.invested_amount == 2250.0 # 3000 - 750
    assert updated_asset.withdrawn_amount == 1500.0
    assert updated_asset.realized_pnl == 750.0
    assert updated_asset.status == "OPEN"

@pytest.mark.asyncio
async def test_investment_full_sale_closes_position():
    repo = MockInvestmentRepository()
    use_case = ManageInvestmentUseCase(repo, MockCreateTransactionUseCase())

    data = InvestmentCreate(
        name="Ethereum",
        ticker="ETH",
        asset_type="CRIPTO",
        broker="Binance",
        invested_amount=1000.0,
        units_qty=2.0,
        average_buy_price=500.0
    )
    asset = await use_case.create_investment(data)

    # Venta total: 2 u a 600€
    sell_data = InvestmentSellPartial(units=2.0, unit_price=600.0)
    updated_asset = await use_case.sell_units(asset.id, sell_data)

    assert updated_asset.units_qty == 0.0
    assert updated_asset.invested_amount == 0.0
    assert updated_asset.status == "CLOSED"
    assert updated_asset.realized_pnl == 200.0
