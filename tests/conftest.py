import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch
from app.main import app

@pytest.fixture(scope="function")
async def async_client():
    """Create an async client with ALL lifespan dependencies mocked."""
    with patch('app.main.get_db') as mock_get_db, \
         patch('app.main.insertAreasPipeline') as mock_insert_areas, \
         patch('app.main.insertStagesPipeline') as mock_insert_stages, \
         patch('app.main.end_db') as mock_end_db:
        
        mock_db_session = AsyncMock()
        mock_get_db.return_value.__anext__.return_value = mock_db_session
        mock_insert_areas.return_value = AsyncMock()
        mock_insert_stages.return_value = AsyncMock()
        
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as client:
            yield client