from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
import re

from src.application.ports.merchant_rule_repository import MerchantRuleRepository
from src.infrastructure.adapters.ai.vector_search import VectorSearchAdapter

class CategorizationStep(ABC):
    @abstractmethod
    async def categorize(self, text: str) -> Optional[UUID]:
        pass

class RegexCategorizationStep(CategorizationStep):
    def __init__(self, rule_repository: MerchantRuleRepository):
        self.rule_repository = rule_repository

    async def categorize(self, text: str) -> Optional[UUID]:
        if not text:
            return None
        rules = await self.rule_repository.get_all()
        for rule in rules:
            try:
                if re.search(rule.pattern, text, re.IGNORECASE):
                    return rule.category_id
            except re.error:
                continue
        return None

class VectorCategorizationStep(CategorizationStep):
    def __init__(self, vector_search_adapter: VectorSearchAdapter):
        self.vector_search_adapter = vector_search_adapter

    async def categorize(self, text: str) -> Optional[UUID]:
        if not text:
            return None
        similar = await self.vector_search_adapter.find_similar_transactions(text, limit=1, threshold=0.88)
        if similar:
            return similar[0].category_id
        return None

class CategorizationPipeline:
    def __init__(self, steps: List[CategorizationStep]):
        self.steps = steps

    async def categorize(self, text: str) -> Optional[UUID]:
        for step in self.steps:
            category_id = await step.categorize(text)
            if category_id:
                return category_id
        return None
