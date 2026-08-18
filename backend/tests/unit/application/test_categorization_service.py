import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.domain.models.merchant_rule import MerchantRule
from src.domain.models.transaction import Transaction
from src.application.services.categorization_service import (
    RegexCategorizationStep,
    VectorCategorizationStep,
    CategorizationPipeline
)

@pytest.mark.asyncio
async def test_regex_categorization_step_match():
    # Arrange
    category_id = uuid4()
    rule = MerchantRule(pattern="(?i)mercadona", category_id=category_id, priority=1)
    
    mock_repo = MagicMock()
    mock_repo.get_all = AsyncMock(return_value=[rule])
    
    step = RegexCategorizationStep(mock_repo)
    
    # Act
    result = await step.categorize("Compra en Mercadona de 30 euros")
    
    # Assert
    assert result == category_id
    mock_repo.get_all.assert_called_once()

@pytest.mark.asyncio
async def test_regex_categorization_step_no_match():
    # Arrange
    category_id = uuid4()
    rule = MerchantRule(pattern="(?i)netflix", category_id=category_id, priority=1)
    
    mock_repo = MagicMock()
    mock_repo.get_all = AsyncMock(return_value=[rule])
    
    step = RegexCategorizationStep(mock_repo)
    
    # Act
    result = await step.categorize("Compra en Mercadona de 30 euros")
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_vector_categorization_step_match():
    # Arrange
    category_id = uuid4()
    tx = MagicMock(spec=Transaction)
    tx.category_id = category_id
    
    mock_adapter = MagicMock()
    mock_adapter.find_similar_transactions = AsyncMock(return_value=[tx])
    
    step = VectorCategorizationStep(mock_adapter)
    
    # Act
    result = await step.categorize("Mercadona")
    
    # Assert
    assert result == category_id
    mock_adapter.find_similar_transactions.assert_called_once_with("Mercadona", limit=1, threshold=0.88)

@pytest.mark.asyncio
async def test_vector_categorization_step_no_match():
    # Arrange
    mock_adapter = MagicMock()
    mock_adapter.find_similar_transactions = AsyncMock(return_value=[])
    
    step = VectorCategorizationStep(mock_adapter)
    
    # Act
    result = await step.categorize("Desconocido")
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_pipeline_cascading():
    # Arrange
    step1_id = uuid4()
    step2_id = uuid4()
    
    step1 = MagicMock()
    step1.categorize = AsyncMock(return_value=None)
    
    step2 = MagicMock()
    step2.categorize = AsyncMock(return_value=step2_id)
    
    pipeline = CategorizationPipeline([step1, step2])
    
    # Act
    result = await pipeline.categorize("Test text")
    
    # Assert
    assert result == step2_id
    step1.categorize.assert_called_once_with("Test text")
    step2.categorize.assert_called_once_with("Test text")

@pytest.mark.asyncio
async def test_pipeline_stops_at_first_match():
    # Arrange
    step1_id = uuid4()
    
    step1 = MagicMock()
    step1.categorize = AsyncMock(return_value=step1_id)
    
    step2 = MagicMock()
    step2.categorize = AsyncMock()
    
    pipeline = CategorizationPipeline([step1, step2])
    
    # Act
    result = await pipeline.categorize("Test text")
    
    # Assert
    assert result == step1_id
    step1.categorize.assert_called_once_with("Test text")
    step2.categorize.assert_not_called()

from unittest.mock import patch

@pytest.mark.asyncio
async def test_run_categorization_and_extraction_with_pipeline_match():
    from src.infrastructure.adapters.tasks.worker import run_categorization_and_extraction
    from src.domain.models.category import Category
    
    category_id = uuid4()
    mock_cat = MagicMock(spec=Category)
    mock_cat.name = "Alimentación"
    
    with patch("src.infrastructure.adapters.tasks.worker.SQLAlchemyMerchantRuleRepository") as mock_rule_repo_cls, \
         patch("src.infrastructure.adapters.tasks.worker.SQLAlchemyTransactionRepository") as mock_tx_repo_cls, \
         patch("src.infrastructure.adapters.tasks.worker.SQLAlchemyCategoryRepository") as mock_cat_repo_cls, \
         patch("src.infrastructure.adapters.tasks.worker.VectorSearchAdapter") as mock_vector_adapter_cls, \
         patch("src.infrastructure.adapters.tasks.worker.extract_transaction_data") as mock_extract_fn:
        
        mock_rule_repo = mock_rule_repo_cls.return_value
        mock_rule_repo.get_all = AsyncMock(return_value=[])
        
        mock_tx_repo = mock_tx_repo_cls.return_value
        
        mock_vector_adapter = mock_vector_adapter_cls.return_value
        mock_tx = MagicMock()
        mock_tx.category_id = category_id
        mock_vector_adapter.find_similar_transactions = AsyncMock(return_value=[mock_tx])
        
        mock_cat_repo = mock_cat_repo_cls.return_value
        mock_cat_repo.get_by_id = AsyncMock(return_value=mock_cat)
        
        mock_data = MagicMock()
        mock_data.category_name = None
        mock_extract_fn.return_value = mock_data
        
        session = MagicMock()
        result = await run_categorization_and_extraction(session, "Mercadona", ["Principal"], ["Alimentación"])
        
        assert result.category_name == "Alimentación"
        mock_extract_fn.assert_called_once_with("Mercadona", ["Principal"], None)

@pytest.mark.asyncio
async def test_run_categorization_and_extraction_fallback_to_llm():
    from src.infrastructure.adapters.tasks.worker import run_categorization_and_extraction
    
    with patch("src.infrastructure.adapters.tasks.worker.SQLAlchemyMerchantRuleRepository") as mock_rule_repo_cls, \
         patch("src.infrastructure.adapters.tasks.worker.SQLAlchemyTransactionRepository") as mock_tx_repo_cls, \
         patch("src.infrastructure.adapters.tasks.worker.SQLAlchemyCategoryRepository") as mock_cat_repo_cls, \
         patch("src.infrastructure.adapters.tasks.worker.VectorSearchAdapter") as mock_vector_adapter_cls, \
         patch("src.infrastructure.adapters.tasks.worker.extract_transaction_data") as mock_extract_fn:
        
        mock_rule_repo_cls.return_value.get_all = AsyncMock(return_value=[])
        mock_vector_adapter_cls.return_value.find_similar_transactions = AsyncMock(return_value=[])
        
        mock_data = MagicMock()
        mock_data.category_name = "Otros"
        mock_extract_fn.return_value = mock_data
        
        session = MagicMock()
        result = await run_categorization_and_extraction(session, "Mercadona", ["Principal"], ["Alimentación"])
        
        assert result.category_name == "Otros"
        mock_extract_fn.assert_called_once_with("Mercadona", ["Principal"], ["Alimentación"])
