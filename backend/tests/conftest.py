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


@pytest.fixture(autouse=True)
def mock_auth_user():
    from unittest.mock import MagicMock
    from uuid import uuid4
    from src.infrastructure.api.dependencies import get_current_user

    mock_user = MagicMock()
    mock_user.id = uuid4()
    mock_user.email = "admin@example.com"
    mock_user.role = "admin"
    mock_user.is_active = True

    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield mock_user
    app.dependency_overrides.pop(get_current_user, None)
