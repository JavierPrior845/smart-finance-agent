import uuid
from datetime import datetime, timezone
from src.application.ports.investment_repository import InvestmentRepository
from src.domain.models.investment import InvestmentAsset, InvestmentMovement
from src.infrastructure.api.v1.schemas.investment import (
    InvestmentCreate, 
    InvestmentClose, 
    InvestmentBuyMore, 
    InvestmentSellPartial
)
from src.application.use_cases.create_transaction import CreateTransactionUseCase

class ManageInvestmentUseCase:
    def __init__(self, repository: InvestmentRepository, create_tx_use_case: CreateTransactionUseCase):
        self.repository = repository
        self.create_tx_use_case = create_tx_use_case

    async def create_investment(self, data: InvestmentCreate) -> InvestmentAsset:
        asset_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        
        # Calculate units or average buy price if missing
        units = data.units_qty
        buy_price = data.average_buy_price
        if units and not buy_price and units > 0:
            buy_price = data.invested_amount / units
        elif buy_price and not units and buy_price > 0:
            units = data.invested_amount / buy_price

        # 1. Create the Asset
        asset = InvestmentAsset(
            id=asset_id,
            name=data.name,
            asset_type=data.asset_type,
            broker=data.broker,
            entry_date=now,
            invested_amount=data.invested_amount,
            status='OPEN',
            ticker=data.ticker,
            units_qty=units,
            average_buy_price=buy_price,
            source_account_id=data.source_account_id,
            created_at=now
        )
        
        await self.repository.create_asset(asset)
        
        # 2. Create the initial buy movement
        movement = InvestmentMovement(
            id=uuid.uuid4(),
            asset_id=asset_id,
            movement_type='BUY_MORE',
            amount=data.invested_amount,
            movement_date=now,
            units=units,
            unit_price=buy_price,
            notes="Initial Purchase",
            created_at=now
        )
        
        await self.repository.create_movement(movement)
        
        # 3. Reflect the cash outflow from account if specified
        try:
            await self.create_tx_use_case.execute(
                amount=data.invested_amount,
                description=f"Compra de inversión: {asset.name} ({asset.ticker or 'N/A'})",
                source=f"Broker: {asset.broker}",
                transaction_date=now,
                account_id=data.source_account_id,
                transaction_type="EXPENSE"
            )
        except Exception as e:
            print(f"Warning: Failed to create cashflow transaction: {e}")
        
        return asset

    async def buy_more(self, asset_id: uuid.UUID, data: InvestmentBuyMore) -> InvestmentAsset:
        asset = await self.repository.get_asset(asset_id)
        if not asset:
            raise ValueError("Investment asset not found")

        now = datetime.now(timezone.utc)
        purchase_cost = data.units * data.unit_price

        old_units = asset.units_qty or 0.0
        old_invested = asset.invested_amount or 0.0

        new_units = old_units + data.units
        new_invested = old_invested + purchase_cost
        new_pmp = new_invested / new_units if new_units > 0 else data.unit_price

        asset.units_qty = new_units
        asset.invested_amount = new_invested
        asset.average_buy_price = new_pmp
        asset.status = 'OPEN'
        asset.exit_date = None

        await self.repository.update_asset(asset)

        # Movement record
        movement = InvestmentMovement(
            id=uuid.uuid4(),
            asset_id=asset_id,
            movement_type='BUY_MORE',
            amount=purchase_cost,
            movement_date=now,
            units=data.units,
            unit_price=data.unit_price,
            notes=data.notes or "DCA Additional Purchase",
            created_at=now
        )
        await self.repository.create_movement(movement)

        # Cashflow expense
        try:
            await self.create_tx_use_case.execute(
                amount=purchase_cost,
                description=f"Compra DCA ({data.units} u): {asset.name} ({asset.ticker or 'N/A'})",
                source=f"Broker: {asset.broker}",
                transaction_date=now,
                account_id=data.source_account_id or asset.source_account_id,
                transaction_type="EXPENSE"
            )
        except Exception as e:
            print(f"Warning: Failed to create cashflow transaction for buy_more: {e}")

        return asset

    async def sell_units(self, asset_id: uuid.UUID, data: InvestmentSellPartial) -> InvestmentAsset:
        asset = await self.repository.get_asset(asset_id)
        if not asset or asset.status != 'OPEN':
            raise ValueError("Asset not found or already closed")

        current_units = asset.units_qty or 0.0
        if current_units <= 0:
            raise ValueError("El activo no posee unidades registradas para vender")

        if data.units > current_units + 1e-9:
            raise ValueError(f"No puedes vender {data.units} unidades. Solo posees {current_units} unidades.")

        now = datetime.now(timezone.utc)
        pmp = asset.average_buy_price or (asset.invested_amount / current_units if current_units > 0 else 0.0)

        revenue = data.units * data.unit_price
        sold_cost = data.units * pmp
        realized_pnl = revenue - sold_cost

        new_units = max(0.0, current_units - data.units)
        new_invested = max(0.0, asset.invested_amount - sold_cost)

        asset.units_qty = new_units
        asset.invested_amount = new_invested
        asset.withdrawn_amount += revenue
        asset.realized_pnl += realized_pnl

        # Close asset if all units sold
        if new_units < 1e-8:
            asset.status = 'CLOSED'
            asset.exit_date = now
            asset.units_qty = 0.0
            asset.invested_amount = 0.0

        await self.repository.update_asset(asset)

        # Register sell movement
        movement = InvestmentMovement(
            id=uuid.uuid4(),
            asset_id=asset_id,
            movement_type='SELL',
            amount=revenue,
            movement_date=now,
            units=data.units,
            unit_price=data.unit_price,
            notes=data.notes or f"Venta de {data.units} u (PnL: €{realized_pnl:.2f})",
            created_at=now
        )
        await self.repository.create_movement(movement)

        # Cashflow income
        try:
            await self.create_tx_use_case.execute(
                amount=revenue,
                description=f"Venta de inversión ({data.units} u): {asset.name} ({asset.ticker or 'N/A'})",
                source=f"Broker: {asset.broker}",
                transaction_date=now,
                account_id=data.destination_account_id or asset.source_account_id,
                transaction_type="INCOME"
            )
        except Exception as e:
            print(f"Warning: Failed to create cashflow transaction for sell_units: {e}")

        return asset

    async def close_investment(self, asset_id: uuid.UUID, data: InvestmentClose) -> InvestmentAsset:
        asset = await self.repository.get_asset(asset_id)
        if not asset or asset.status != 'OPEN':
            raise ValueError("Asset not found or already closed")
            
        units_to_sell = asset.units_qty or 1.0
        unit_price = data.withdrawn_amount / units_to_sell if units_to_sell > 0 else data.withdrawn_amount
        
        sell_data = InvestmentSellPartial(
            units=units_to_sell,
            unit_price=unit_price,
            notes="Position Closed Fully"
        )
        return await self.sell_units(asset_id, sell_data)
