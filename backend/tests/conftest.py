import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def mock_local_embedder(request):
    if "test_local_embedder_mocked" in request.node.name:
        yield
        return
    from unittest.mock import patch
    with patch("src.infrastructure.adapters.ai.embeddings.LocalEmbedder.get_embedding", return_value=[0.1] * 384):
        yield
