from typing import List
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.transaction_repository import TransactionRepository
from src.domain.models.transaction import Transaction
from src.infrastructure.adapters.db.models.transaction import TransactionORM

class SQLAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: TransactionORM) -> Transaction:
        # Convert numpy array or Vector to list of floats if needed
        emb = None
        if orm.embedding is not None:
            if hasattr(orm.embedding, "tolist"):
                emb = orm.embedding.tolist()
            else:
                emb = list(orm.embedding)
        return Transaction(
            id=orm.id,
            account_id=orm.account_id,
            destination_account_id=orm.destination_account_id,
            type=orm.type,
            amount=float(orm.amount),
            currency=orm.currency,
            raw_text=orm.raw_text,
            description=orm.description,
            category_id=orm.category_id,
            source=orm.source,
            status=orm.status,
            is_recurring=orm.is_recurring,
            is_anomalous=orm.is_anomalous,
            transaction_date=orm.transaction_date,
            embedding=emb,
            created_at=orm.created_at
        )

    def _to_orm(self, domain: Transaction) -> TransactionORM:
        return TransactionORM(
            id=domain.id,
            account_id=domain.account_id,
            destination_account_id=domain.destination_account_id,
            type=domain.type,
            amount=domain.amount,
            currency=domain.currency,
            raw_text=domain.raw_text,
            description=domain.description,
            category_id=domain.category_id,
            source=domain.source,
            status=domain.status,
            is_recurring=domain.is_recurring,
            is_anomalous=domain.is_anomalous,
            transaction_date=domain.transaction_date,
            embedding=domain.embedding,
            created_at=domain.created_at
        )

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        stmt = select(TransactionORM).where(TransactionORM.id == transaction_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_account(self, account_id: UUID, limit: int = 50, offset: int = 0) -> List[Transaction]:
        stmt = select(TransactionORM).where(
            (TransactionORM.account_id == account_id) | 
            (TransactionORM.destination_account_id == account_id)
        ).order_by(TransactionORM.transaction_date.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_recent(self, limit: int = 50) -> List[Transaction]:
        stmt = select(TransactionORM).order_by(TransactionORM.transaction_date.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_all_paginated(
        self, 
        limit: int = 20, 
        offset: int = 0, 
        search: str | None = None,
        category_id: UUID | None = None,
        source: str | None = None
    ) -> tuple[List[Transaction], int]:
        
        conditions = []
        if search:
            conditions.append(TransactionORM.description.ilike(f"%{search}%"))
        if category_id:
            conditions.append(TransactionORM.category_id == category_id)
        if source:
            conditions.append(TransactionORM.source == source)
            
        base_stmt = select(TransactionORM)
        count_stmt = select(func.count(TransactionORM.id))
        
        if conditions:
            base_stmt = base_stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)
            
        # Get total count
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()
        
        # Get items
        stmt = base_stmt.order_by(TransactionORM.transaction_date.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        items = [self._to_domain(orm) for orm in result.scalars().all()]
        
        return items, total

    async def save(self, transaction: Transaction) -> Transaction:
        orm = self._to_orm(transaction)
        self.session.add(orm)
        await self.session.flush()
        return self._to_domain(orm)

    async def delete(self, transaction_id: UUID) -> None:
        orm = await self.session.get(TransactionORM, transaction_id)
        if orm:
            await self.session.delete(orm)
            await self.session.flush()

    async def get_nearest_neighbors(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.88) -> List[Transaction]:
        distance_threshold = 1.0 - threshold
        stmt = (
            select(TransactionORM)
            .where(
                (TransactionORM.embedding.cosine_distance(query_embedding) <= distance_threshold) &
                (TransactionORM.status == "confirmed")
            )
            .order_by(TransactionORM.embedding.cosine_distance(query_embedding).asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_anomalous(self, limit: int = 50) -> List[Transaction]:
        stmt = (
            select(TransactionORM)
            .where(TransactionORM.is_anomalous == True)
            .order_by(TransactionORM.transaction_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]
