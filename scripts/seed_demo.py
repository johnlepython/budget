# seed_demo.py
import asyncio
import httpx
from datetime import datetime, timedelta
import random

API_URL = "https://budget.jsdconsult.cloud"
DEMO_USER = {"email": "demo@jsdconsult.cloud", "password": "demo1234"}

async def seed_data():
    async with httpx.AsyncClient() as client:
        # 1. Login
        login_res = await client.post(f"{API_URL}/token", data={"username": DEMO_USER["email"], "password": DEMO_USER["password"]})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Nettoyage / Reset (Optionnel si tu as une route DELETE /all)
        
        # 3. Création de catégories Mockées
        categories = [
            {"name": "Loyer", "type": "Dépense"},
            {"name": "Salaire", "type": "Revenu"},
            {"name": "Courses", "type": "Dépense"},
            {"name": "Netflix", "type": "Dépense"}
        ]
        for cat in categories:
            await client.post(f"{API_URL}/categories/", json=cat, headers=headers)

        # 4. Génération de transactions sur 30 jours
        for i in range(20):
            date = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            await client.post(f"{API_URL}/transactions/", json={
                "category_id": random.randint(1, 4), # À adapter selon tes IDs
                "amount": random.uniform(10, 150),
                "description": f"Test Transaction {i}",
                "date": date
            }, headers=headers)
        
        print("✅ Demo account seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())