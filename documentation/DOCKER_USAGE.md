# 🐳 Guide d'utilisation avec Docker

## Commandes essentielles

### Démarrer les services

```bash
docker compose up -d
```

### Arrêter les services

```bash
docker compose down
```

### Voir les logs

```bash
# Tous les services
docker compose logs -f

# Service API uniquement
docker compose logs -f api

# Service Studio uniquement
docker compose logs -f studio
```

### Rebuilder après changement de code

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 🔄 Migration des univers existants

### Méthode 1 : Script shell (recommandée)

```bash
# Migrer tous les univers
./migrate.sh

# Migrer un univers spécifique
./migrate.sh jungle
```

Le script :
- Vérifie que Docker est installé
- Démarre les services si nécessaire
- Exécute la migration dans le container API
- Affiche le résultat

### Méthode 2 : Commande Docker directe

```bash
# Migrer tous les univers
docker compose exec api python /app/migrate_to_drafts.py

# Migrer un univers spécifique
docker compose exec api python /app/migrate_to_drafts.py jungle
```

---

## 🧪 Tests dans Docker

### Test du workflow complet

```bash
# Option 1 : Via le script shell (à créer)
./test.sh

# Option 2 : Installer requests dans le host
pip3 install requests
python3 test_drafts_workflow.py

# Option 3 : Exécuter dans le container
docker compose exec api pip install requests
docker compose exec api python /app/test_drafts_workflow.py
```

---

## 🔧 Commandes utiles

### Accéder au shell du container API

```bash
docker compose exec api /bin/bash
```

Une fois dans le container, vous pouvez :
```bash
# Lister les fichiers
ls -la /app/storage/univers

# Voir les logs Python
python --version

# Vérifier les dépendances
pip list | grep -E "fastapi|supabase|replicate"
```

### Accéder au shell du container Studio

```bash
docker compose exec studio /bin/sh
```

### Copier des fichiers depuis/vers le container

```bash
# Copier depuis le container vers le host
docker compose cp api:/app/storage/univers ./univers_backup

# Copier depuis le host vers le container
docker compose cp ./new_file.txt api:/app/
```

### Vérifier l'utilisation des ressources

```bash
# Statistiques en temps réel
docker stats

# Espace disque utilisé
docker system df
```

---

## 🗑️ Nettoyage

### Supprimer les volumes (attention : perte de données)

```bash
# Arrêter et supprimer les volumes
docker compose down -v

# Rebuild complet
docker compose build --no-cache
docker compose up -d
```

### Nettoyer Docker complètement

```bash
# Supprimer les images inutilisées
docker image prune -a

# Nettoyer tout (images, containers, volumes)
docker system prune -a --volumes
```

---

## 🐛 Dépannage Docker

### Le service ne démarre pas

```bash
# Voir les logs détaillés
docker compose logs api

# Vérifier la configuration
docker compose config

# Vérifier les ports
lsof -i :8000  # API
lsof -i :8081  # Studio
```

### Erreur "port already in use"

```bash
# Trouver le processus qui utilise le port
lsof -ti :8000 | xargs kill -9  # API
lsof -ti :8081 | xargs kill -9  # Studio

# Ou changer le port dans docker-compose.yml
```

### Le volume n'est pas monté

```bash
# Vérifier les volumes
docker compose ps -v

# Recréer les volumes
docker compose down -v
docker compose up -d
```

### Erreur de build

```bash
# Nettoyer le cache
docker compose build --no-cache

# Vérifier le Dockerfile
cat api/Dockerfile
```

---

## 📦 Structure des volumes (Hot Reload activé ✅)

```
volumes:
  - ./storage:/app/storage          # Données persistantes (univers)
  - ./api:/app                       # Code API (hot reload Python)
  - ./projet:/app/projet             # Fonctions de génération
  - ./viewer:/usr/share/nginx/html   # Code viewer (hot reload HTML/JS)
```

### Hot Reload actif pour :

✅ **Univers** (`storage/univers/`)
- Création/modification d'univers → visible immédiatement
- Génération d'assets → fichiers disponibles sans redémarrage
- Pas besoin de rebuild ou restart

✅ **Code API** (`api/`)
- Modification de `routes/universes.py` → reload automatique
- Modification de `models.py` → reload automatique
- Modification de `services/` → reload automatique
- Grâce à `uvicorn.run(..., reload=True)`

✅ **Code Viewer** (`viewer/`)
- Modification HTML/CSS/JS → rafraîchir le navigateur
- Pas de rebuild nécessaire (nginx sert les fichiers statiques)

### Ce qui nécessite un restart :

⚠️ **Variables d'environnement** (`.env`)
```bash
docker compose restart api
```

⚠️ **Dépendances Python** (`requirements.txt`)
```bash
docker compose up -d --build
```

⚠️ **Dockerfile** ou **docker-compose.yml**
```bash
docker compose down
docker compose up -d --build
```

---

## 🚀 Workflow de développement

### 1. Modifier le code

Éditer les fichiers localement (VS Code, etc.)

### 2. Redémarrer si nécessaire

```bash
# Pour les changements Python (API)
docker compose restart api

# Pour les changements HTML/JS (Studio)
# Pas besoin de redémarrer, juste rafraîchir le navigateur
```

### 3. Voir les logs

```bash
docker compose logs -f api
```

### 4. Tester

```bash
# Via le Studio
open http://localhost:8081

# Via l'API
curl http://localhost:8000/api/universes
```

---

## 🔐 Variables d'environnement

Les variables d'environnement sont chargées depuis `.env` :

```bash
# Voir les variables dans le container
docker compose exec api env | grep -E "REPLICATE|SUPABASE"

# Modifier les variables
nano .env

# Redémarrer pour appliquer
docker compose restart api
```

---

## 📊 Monitoring

### Voir l'utilisation des ressources

```bash
# En temps réel
docker stats

# Espace disque
docker system df
```

### Vérifier la santé des services

```bash
# Status des containers
docker compose ps

# Logs récents
docker compose logs --tail=50

# Suivre les logs
docker compose logs -f
```

---

## 🎯 Commandes rapides

```bash
# Redémarrage complet
docker compose restart

# Rebuild et redémarrage
docker compose up -d --build

# Arrêter et nettoyer
docker compose down -v

# Voir les processus dans un container
docker compose top api

# Exécuter une commande ponctuelle
docker compose exec api python -c "print('Hello from Docker')"
```

---

## 📚 Liens utiles

- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Best practices Docker](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose CLI](https://docs.docker.com/compose/reference/)
