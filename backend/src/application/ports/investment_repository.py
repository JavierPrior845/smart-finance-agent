from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from datetime import date
from src.domain.models.investment import InvestmentAsset, InvestmentSnapshot, InvestmentMovement

class InvestmentRepository(ABC):
    @abstractmethod
    async def get_all_assets(self) -> List[InvestmentAsset]:
        pass

    @abstractmethod
    async def get_asset(self, asset_id: UUID) -> InvestmentAsset | None:
        pass

    @abstractmethod
    async def update_asset(self, asset: InvestmentAsset) -> InvestmentAsset:
        pass

    @abstractmethod
    async def create_asset(self, asset: InvestmentAsset) -> InvestmentAsset:
        pass

    @abstractmethod
    async def create_movement(self, movement: InvestmentMovement) -> InvestmentMovement:
        pass
    @abstractmethod
    async def get_active_assets(self) -> List[InvestmentAsset]:
        pass

    @abstractmethod
    async def get_latest_snapshot_date(self, asset_id: UUID) -> date | None:
        pass

    @abstractmethod
    async def save_snapshot(self, snapshot: InvestmentSnapshot) -> InvestmentSnapshot:
        pass

    @abstractmethod
    async def save_snapshots_bulk(self, snapshots: List[InvestmentSnapshot]) -> None:
        pass
