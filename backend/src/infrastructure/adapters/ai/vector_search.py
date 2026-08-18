from typing import List
from src.application.ports.transaction_repository import TransactionRepository
from src.infrastructure.adapters.ai.embeddings import LocalEmbedder
from src.domain.models.transaction import Transaction

class VectorSearchAdapter:
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    async def find_similar_transactions(self, description: str, limit: int = 5, threshold: float = 0.88) -> List[Transaction]:
        if not description:
            return []
        query_embedding = LocalEmbedder.get_embedding(description)
        return await self.transaction_repo.get_nearest_neighbors(query_embedding, limit, threshold)
