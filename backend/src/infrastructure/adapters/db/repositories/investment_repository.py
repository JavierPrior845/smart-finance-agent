from typing import List
from uuid import UUID
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.investment_repository import InvestmentRepository
from src.domain.models.investment import InvestmentAsset, InvestmentSnapshot
from src.infrastructure.adapters.db.models.investment import InvestmentAssetORM, InvestmentSnapshotORM

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
