# Opérations

## Tester l'application en local via Docker

Pour lancer l'application backend FastAPI et la base de données SQLite en local sur votre Mac via Docker, suivez les étapes suivantes :

1.  **Assurez-vous que Docker est installé et en cours d'exécution** sur votre machine.

2.  **Ouvrez un terminal** à la racine de votre projet (`/Users/john/Documents/budget`).

3.  **Construisez et lancez les conteneurs Docker** en exécutant la commande suivante :
    ```bash
    docker-compose up --build
    ```
    Cette commande va :
    *   Construire l'image Docker pour le backend FastAPI en se basant sur le `Dockerfile` situé dans le dossier `/backend`.
    *   Lancer le service `backend`, qui exposera l'API FastAPI sur le port `8000` de votre machine.
    *   Lancer le service `db` (SQLite Web), qui exposera une interface web pour gérer la base de données SQLite sur le port `8080` de votre machine.

4.  **Vérifiez que l'API FastAPI est accessible** en ouvrant votre navigateur et en allant à l'adresse : `http://localhost:8000`.
    Vous devriez voir la réponse `{"Hello": "World"}`.

5.  **Accédez à l'interface de gestion SQLite** (optionnel) en allant à l'adresse : `http://localhost:8080`.

6.  **Pour arrêter les conteneurs**, appuyez sur `Ctrl+C` dans le terminal où `docker-compose up` est en cours d'exécution. Pour les supprimer (ainsi que les volumes anonymes), utilisez :
    ```bash
    docker-compose down -v
    ```
