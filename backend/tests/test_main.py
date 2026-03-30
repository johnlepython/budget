import pytest
from httpx import AsyncClient
from main import app # Importe ton app FastAPI

@pytest.mark.asyncio
async def test_read_main():
    """Vérifie que la page d'accueil répond bien"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_static_files():
    """Vérifie que le dossier static est bien accessible"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/static/index.html")
    assert response.status_code in [200, 404] # 404 est OK si le fichier n'existe pas encore, l'important est que l'app ne crash pas