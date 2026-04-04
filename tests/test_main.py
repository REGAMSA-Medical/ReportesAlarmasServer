import pytest

@pytest.mark.asyncio
async def test_root(async_client):
    """Test root api endpoint without lifespans"""
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {'message': 'Bienvenido a la API de REGAMSA Medical'}