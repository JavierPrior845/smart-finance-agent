import uuid
from datetime import datetime, timezone
from src.application.ports.investment_repository import InvestmentRepository
from src.domain.models.investment import InvestmentAsset, InvestmentMovement
from src.infrastructure.api.v1.schemas.investment import InvestmentCreate, InvestmentClose
from src.application.use_cases.create_transaction import CreateTransactionUseCase

class ManageInvestmentUseCase:
    def __init__(self, repository: InvestmentRepository, create_tx_use_case: CreateTransactionUseCase):
        self.repository = repository
        self.create_tx_use_case = create_tx_use_case

    async def create_investment(self, data: InvestmentCreate) -> InvestmentAsset:
        asset_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        
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
            units_qty=data.units_qty,
            average_buy_price=data.average_buy_price,
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
            units=data.units_qty,
            unit_price=data.average_buy_price,
            notes="Initial Purchase",
            created_at=now
        )
        
        await self.repository.create_movement(movement)
        
        # 3. Reflect the cash outflow from the main account
        try:
            await self.create_tx_use_case.execute(
                amount=data.invested_amount,
                description=f"Compra de inversión: {asset.name} ({asset.ticker or 'N/A'})",
                source=f"Broker: {asset.broker}",
                transaction_date=now,
                transaction_type="EXPENSE"
            )
        except Exception as e:
            # For MVP, log and continue if transaction fails (e.g., no main account)
            print(f"Warning: Failed to create cashflow transaction: {e}")
        
        return asset

    async def close_investment(self, asset_id: uuid.UUID, data: InvestmentClose) -> InvestmentAsset:
        asset = await self.repository.get_asset(asset_id)
        if not asset or asset.status != 'OPEN':
            raise ValueError("Asset not found or already closed")
            
        now = datetime.now(timezone.utc)
        
        # Calculate PnL
        pnl = data.withdrawn_amount - asset.invested_amount
        
        # Update asset
        asset.status = 'CLOSED'
        asset.exit_date = now
        asset.withdrawn_amount = data.withdrawn_amount
        asset.realized_pnl = pnl
        
        await self.repository.update_asset(asset)
        
        # Create sell movement
        movement = InvestmentMovement(
            id=uuid.uuid4(),
            asset_id=asset_id,
            movement_type='SELL',
            amount=data.withdrawn_amount,
            movement_date=now,
            notes="Position Closed",
            created_at=now
        )
        
        await self.repository.create_movement(movement)
        
        # Reflect cash inflow into the main account
        try:
            await self.create_tx_use_case.execute(
                amount=data.withdrawn_amount,
                description=f"Venta de inversión: {asset.name} ({asset.ticker or 'N/A'})",
                source=f"Broker: {asset.broker}",
                transaction_date=now,
                transaction_type="INCOME"
            )
        except Exception as e:
            print(f"Warning: Failed to create cashflow transaction for sale: {e}")
            
        return asset
