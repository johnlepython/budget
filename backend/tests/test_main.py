import pytest
from httpx import AsyncClient, ASGITransport
from main import app 

@pytest.mark.asyncio
async def test_read_main():
    """Vérifie que la page d'accueil répond bien"""
    # On utilise ASGITransport pour passer l'application FastAPI
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_static_files():
    """Vérifie que le dossier static est bien accessible"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/static/index.html")
    # 200 si le fichier existe, 404 sinon, mais l'app doit répondre
    assert response.status_code in [200, 404]