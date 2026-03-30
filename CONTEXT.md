# État du Projet : Budget App

## Architecture
- **Backend** : FastAPI (Python 3.9-slim)
- **Base de données** : SQLite via SQLModel
- **Frontend** : HTML/JS Vanilla + Tailwind CSS (via CDN) + Chart.js
- **Infrastructure** : Docker Compose (backend + volume data)

## Chemins Critiques
- **Database Host** : `/app/data/budget.db`
- **Database Local** : `./data/budget.db`
- **Static Files** : `backend/static/`

## État Actuel
- Le dashboard fonctionne (formulaire + graphiques).
- La persistance des données dans Docker est OK (24Ko SQLite).
- Les routes GET/POST de base pour les transactions sont implémentées.

## Objectif Suivant
- Implémenter l'authentification (JWT + Bcrypt).
- Creer une budgetisation mensuelle avec saisie des depenses previsionelles pour chaque categorie