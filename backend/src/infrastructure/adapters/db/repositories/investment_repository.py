from typing import List
from uuid import UUID
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.investment_repository import InvestmentRepository
from src.domain.models.investment import InvestmentAsset, InvestmentSnapshot, InvestmentMovement
from src.infrastructure.adapters.db.models.investment import InvestmentAssetORM, InvestmentSnapshotORM, InvestmentMovementORM

class SQLAlchemyInvestmentRepository(InvestmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _asset_to_domain(self, orm: InvestmentAssetORM) -> InvestmentAsset:
        return InvestmentAsset(
            id=orm.id,
            name=orm.name,
            asset_type=orm.asset_type,
            broker=orm.broker,
            entry_date=orm.entry_date,
            invested_amount=float(orm.invested_amount),
            status=orm.status,
            ticker=orm.ticker,
            units_qty=float(orm.units_qty) if orm.units_qty is not None else None,
            average_buy_price=float(orm.average_buy_price) if orm.average_buy_price is not None else None,
            exit_date=orm.exit_date,
            withdrawn_amount=float(orm.withdrawn_amount),
            realized_pnl=float(orm.realized_pnl),
            source_account_id=orm.source_account_id,
            created_at=orm.created_at
        )

    def _snapshot_to_orm(self, domain: InvestmentSnapshot) -> InvestmentSnapshotORM:
        return InvestmentSnapshotORM(
            id=domain.id,
            asset_id=domain.asset_id,
            snapshot_date=domain.snapshot_date,
            price=domain.price,
            total_value=domain.total_value,
            created_at=domain.created_at
        )

    def _snapshot_to_domain(self, orm: InvestmentSnapshotORM) -> InvestmentSnapshot:
        return InvestmentSnapshot(
            id=orm.id,
            asset_id=orm.asset_id,
            snapshot_date=orm.snapshot_date,
            price=float(orm.price),
            total_value=float(orm.total_value),
            created_at=orm.created_at
        )

    def _asset_to_orm(self, domain: InvestmentAsset) -> InvestmentAssetORM:
        return InvestmentAssetORM(
            id=domain.id,
            name=domain.name,
            asset_type=domain.asset_type,
            broker=domain.broker,
            entry_date=domain.entry_date,
            invested_amount=domain.invested_amount,
            status=domain.status,
            ticker=domain.ticker,
            units_qty=domain.units_qty,
            average_buy_price=domain.average_buy_price,
            exit_date=domain.exit_date,
            withdrawn_amount=domain.withdrawn_amount,
            realized_pnl=domain.realized_pnl,
            source_account_id=domain.source_account_id,
            created_at=domain.created_at
        )

    def _movement_to_orm(self, domain: InvestmentMovement) -> InvestmentMovementORM:
        return InvestmentMovementORM(
            id=domain.id,
            asset_id=domain.asset_id,
            movement_type=domain.movement_type,
            amount=domain.amount,
            movement_date=domain.movement_date,
            transaction_id=domain.transaction_id,
            units=domain.units,
            unit_price=domain.unit_price,
            notes=domain.notes,
            created_at=domain.created_at
        )

    def _movement_to_domain(self, orm: InvestmentMovementORM) -> InvestmentMovement:
        return InvestmentMovement(
            id=orm.id,
            asset_id=orm.asset_id,
            movement_type=orm.movement_type,
            amount=float(orm.amount),
            movement_date=orm.movement_date,
            transaction_id=orm.transaction_id,
            units=float(orm.units) if orm.units is not None else None,
            unit_price=float(orm.unit_price) if orm.unit_price is not None else None,
            notes=orm.notes,
            created_at=orm.created_at
        )

    async def get_active_assets(self) -> List[InvestmentAsset]:
        stmt = select(InvestmentAssetORM).where(InvestmentAssetORM.status == 'OPEN')
        result = await self.session.execute(stmt)
        return [self._asset_to_domain(orm) for orm in result.scalars().all()]

    async def get_latest_snapshot_date(self, asset_id: UUID) -> date | None:
        stmt = select(func.max(InvestmentSnapshotORM.snapshot_date)).where(InvestmentSnapshotORM.asset_id == asset_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def save_snapshot(self, snapshot: InvestmentSnapshot) -> InvestmentSnapshot:
        orm = self._snapshot_to_orm(snapshot)
        self.session.add(orm)
        await self.session.flush()
        return snapshot

    async def save_snapshots_bulk(self, snapshots: List[InvestmentSnapshot]) -> None:
        if not snapshots:
            return
        orms = [self._snapshot_to_orm(s) for s in snapshots]
        self.session.add_all(orms)
        await self.session.flush()

    async def get_all_assets(self) -> List[InvestmentAsset]:
        stmt = select(InvestmentAssetORM)
        result = await self.session.execute(stmt)
        return [self._asset_to_domain(orm) for orm in result.scalars().all()]

    async def get_asset(self, asset_id: UUID) -> InvestmentAsset | None:
        stmt = select(InvestmentAssetORM).where(InvestmentAssetORM.id == asset_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm:
            return self._asset_to_domain(orm)
        return None

    async def update_asset(self, asset: InvestmentAsset) -> InvestmentAsset:
        orm = self._asset_to_orm(asset)
        await self.session.merge(orm)
        await self.session.flush()
        return asset

    async def create_asset(self, asset: InvestmentAsset) -> InvestmentAsset:
        orm = self._asset_to_orm(asset)
        self.session.add(orm)
        await self.session.flush()
        return asset

    async def create_movement(self, movement: InvestmentMovement) -> InvestmentMovement:
        orm = self._movement_to_orm(movement)
        self.session.add(orm)
        await self.session.flush()
        return movement
