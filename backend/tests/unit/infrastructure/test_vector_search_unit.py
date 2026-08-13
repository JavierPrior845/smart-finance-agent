import pytest
from unittest.mock import MagicMock, patch
from src.infrastructure.adapters.ai.embeddings import LocalEmbedder
from src.infrastructure.adapters.ai.vector_search import VectorSearchAdapter

def test_local_embedder_mocked():
    with patch("src.infrastructure.adapters.ai.embeddings.SentenceTransformer") as mock_transformer_cls:
        mock_instance = MagicMock()
        # Mock encode to return a numpy-like object
        mock_instance.encode.return_value = MagicMock(tolist=lambda: [0.1] * 384)
        mock_transformer_cls.return_value = mock_instance
        
        # Reset any cached model
        LocalEmbedder._model = None
        
        embedding = LocalEmbedder.get_embedding("test description")
        assert len(embedding) == 384
        assert embedding[0] == 0.1
        mock_transformer_cls.assert_called_once_with('paraphrase-multilingual-MiniLM-L12-v2')
        mock_instance.encode.assert_called_once_with("test description")

@pytest.mark.asyncio
async def test_vector_search_adapter():
    mock_repo = MagicMock()
    # Mock get_nearest_neighbors to return async empty list
    async def mock_get_nearest(embedding, limit, threshold):
        return []
    mock_repo.get_nearest_neighbors = mock_get_nearest
    
    # Mock LocalEmbedder.get_embedding
    with patch("src.infrastructure.adapters.ai.embeddings.LocalEmbedder.get_embedding", return_value=[0.1] * 384) as mock_get_emb:
        adapter = VectorSearchAdapter(mock_repo)
        res = await adapter.find_similar_transactions("pizza", limit=3, threshold=0.9)
        assert res == []
        
        mock_get_emb.assert_called_once_with("pizza")
