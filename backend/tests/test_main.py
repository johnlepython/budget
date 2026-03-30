import pytest
from httpx import AsyncClient
from main import app # Ton instance FastAPI

# backend/tests/test_main.py

def test_simple_assertion():
    """Un test tout simple pour vérifier que pytest fonctionne"""
    assert 1 + 1 == 2

def test_api_exists():
    """On vérifie juste que l'import ne crash pas"""
    try:
        import main
        assert True
    except ImportError:
        assert False, "Le fichier main.py n'a pas été trouvé dans le PYTHONPATH"