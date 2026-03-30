# Règles de Développement (Mode Éco)

1. **Brièveté** : Ne réécris jamais un fichier complet. Donne uniquement les fonctions modifiées ou les "diffs".
2. **Imports** : Utilise des imports absolus (`from models import...`) car le projet tourne dans `/app` sous Docker. Pas d'imports relatifs (`.models`).
3. **Sécurité** : 
   - Utilise `passlib[bcrypt]` pour les mots de passe.
   - Utilise `python-jose[cryptography]` pour les tokens JWT.
4. **Volume** : Ne touche jamais au dossier `data/` pendant le code, c'est géré par Docker.
5. **Logs** : Si une erreur survient, demande-moi d'exécuter `docker compose logs` avant de tenter une correction au hasard.