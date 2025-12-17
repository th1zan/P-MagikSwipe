# MagikSwipe Backend API v2.1

Backend FastAPI avec SQLite local mirrorant Supabase, synchronisation bidirectionnelle, génération IA multilingue via Replicate et **⭐ musique personnalisée par langue**.

## 📁 Structure du Projet

```
/backend/
├── Dockerfile                    # Image Python 3.11
├── requirements.txt              # Dépendances
├── main.py                       # Point d'entrée FastAPI
├── config.py                     # Configuration (env vars)
├── database/
│   ├── __init__.py
│   ├── connection.py             # SQLite + SQLAlchemy engine
│   └── models.py                 # 7 tables ORM (6 Supabase + jobs)
├── schemas/
│   └── __init__.py               # Modèles Pydantic (request/response)
├── services/
│   ├── __init__.py
│   ├── storage_service.py        # Bucket local /storage/buckets/univers/
│   ├── supabase_service.py       # Client Supabase DB + Storage
│   ├── sync_service.py           # Sync bidirectionnelle (pull/push)
│   ├── generation_service.py     # Replicate AI (images, vidéos, musique)
│   └── job_service.py            # Jobs persistés en SQLite
├── routes/
│   ├── __init__.py
│   ├── universes.py              # CRUD univers + assets
│   ├── generation.py             # Génération IA
│   ├── sync.py                   # Endpoints sync + /sync/init
│   └── jobs.py                   # Suivi des jobs
└── utils/
    └── __init__.py               # Utilitaires
```

## 🔌 API Endpoints

### Universes (CRUD)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/universes` | Liste des univers |
| POST | `/api/universes` | Créer un univers |
| GET | `/api/universes/{slug}` | Détails d'un univers |
| PATCH | `/api/universes/{slug}` | Modifier un univers |
| DELETE | `/api/universes/{slug}` | Supprimer un univers |
| GET | `/api/universes/{slug}/assets` | Liste des assets |
| POST | `/api/universes/{slug}/assets` | Créer un asset |
| GET | `/api/universes/{slug}/assets/{id}` | Détails d'un asset |
| PATCH | `/api/universes/{slug}/assets/{id}` | Modifier un asset |
| DELETE | `/api/universes/{slug}/assets/{id}` | Supprimer un asset |
| **⭐ Musique Multilingue** | | |
| GET | `/api/universes/{slug}/music-prompts` | Liste prompts musique par langue |
| POST | `/api/universes/{slug}/music-prompts` | Créer prompt musique |
| GET | `/api/universes/{slug}/music-prompts/{lang}` | Prompt musique d'une langue |
| PATCH | `/api/universes/{slug}/music-prompts/{lang}` | Modifier prompt musique |
| DELETE | `/api/universes/{slug}/music-prompts/{lang}` | Supprimer prompt musique |

### Generation (IA)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/generate/{slug}/concepts` | Générer concepts IA |
| POST | `/api/generate/{slug}/concepts/apply` | Appliquer concepts (créer assets) |
| POST | `/api/generate/{slug}/images` | Générer images (async) |
| POST | `/api/generate/{slug}/videos` | Générer vidéos (async) |
| POST | `/api/generate/{slug}/music` | Générer musique (async) |
| POST | `/api/generate/{slug}/all` | Pipeline complet (async) |

### Sync (Supabase)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sync/status` | État connexion Supabase |
| POST | `/api/sync/init` | ⭐ Initialiser depuis Supabase |
| POST | `/api/sync/pull/{slug}` | Pull un univers |
| POST | `/api/sync/push/{slug}` | Push un univers |
| POST | `/api/sync/pull-all` | Pull tous les univers |

### Jobs (Async)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/jobs` | Liste des jobs |
| GET | `/api/jobs/{id}` | Statut d'un job |
| DELETE | `/api/jobs/cleanup` | Nettoyer vieux jobs |

## 🗄️ Structure SQLite (miroir Supabase)

```
local.db
├── univers                      # Univers principaux
├── univers_prompts              # Prompts par défaut
├── univers_translations         # Traductions du nom
├── univers_music_prompts        # ⭐ Prompts et paroles musique (fr,en,es,it,de)
├── univers_assets               # Assets (images/vidéos)
├── univers_assets_prompts       # Prompts custom par asset
├── univers_assets_translations  # Traductions des noms d'assets
└── jobs                         # Jobs asynchrones (local uniquement)
```

### Champs additionnels (SQLite uniquement)

```python
# Dans la table 'univers' (pour tracking sync)
supabase_id = Column(BigInteger)      # ID correspondant dans Supabase
last_synced_at = Column(DateTime)     # Timestamp dernière sync
```

## 🪣 Structure Storage Local

```
⭐ Structure plate (pas de sous-dossiers)
/storage/
├── db/
│   └── local.db                  # Base SQLite
└── buckets/
    └── univers/            # Miroir du bucket Supabase
        └── {slug}/               # Structure plate
            ├── 00_concept.png    # Images assets
            ├── 00_concept.mp4    # Vidéos assets
            ├── fr.mp3            # Musique française
            ├── en.mp3            # Musique anglaise
            ├── es.mp3            # Musique espagnole
            ├── it.mp3            # Musique italienne
            ├── de.mp3            # Musique allemande
            └── thumbnail.jpg     # Miniature univers
```

## 🚀 Démarrage

### Avec Docker

```bash
# Construire et lancer
docker-compose up --build backend

# Accéder à l'API
open http://localhost:8000/docs
```

### En local (développement)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Initialiser depuis Supabase

```bash
# Télécharger toutes les données de Supabase
curl -X POST http://localhost:8000/api/sync/init
```

## 📋 Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```env
# Replicate (génération IA)
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxx

# Supabase (sync)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxxxxxxxxxxxx
```

## 🔄 Stratégie de Synchronisation

**Mode : "Last Write Wins"**

- `POST /api/sync/pull/{slug}` : Supabase → Local (écrase local)
- `POST /api/sync/push/{slug}` : Local → Supabase (écrase distant)
- `POST /api/sync/init` : Supabase → Local pour TOUS les univers

## 🤖 Génération IA (Replicate)

### Langues supportées

**⭐ Multilingue** : `fr`, `en`, `es`, `it`, `de`

### Modèles utilisés

| Type | Modèle |
|------|--------|
| LLM (concepts + traductions) | `meta/meta-llama-3-70b-instruct` |
| Images | `recraft-ai/recraft-v3` |
| Vidéos | `wan-video/wan-2.1-i2v-480p` |
| **⭐ Musique multilingue** | `minimax/music-01` |

### Workflow typique

1. **Créer un univers** : `POST /api/universes`
2. **⭐ Configurer prompts musique** : `POST /api/universes/{slug}/music-prompts` (par langue)
3. **Générer des concepts** : `POST /api/generate/{slug}/concepts`
4. **Appliquer les concepts** : `POST /api/generate/{slug}/concepts/apply`
5. **Générer les images** : `POST /api/generate/{slug}/images`
6. **Générer les vidéos** : `POST /api/generate/{slug}/videos`
7. **⭐ Générer la musique** : `POST /api/generate/{slug}/music` (utilise prompts stockés)
8. **Publier sur Supabase** : `POST /api/sync/push/{slug}`

### ⭐ Exemples d'utilisation musique multilingue

```bash
# Créer un prompt musique français
curl -X POST http://localhost:8000/api/universes/christmas/music-prompts \
  -H "Content-Type: application/json" \
  -d '{
    "language": "fr",
    "prompt": "musique de Noël festive, mélodie entraînante",
    "lyrics": "Noël approche, les cadeaux sont là..."
  }'

# Générer la musique française (utilise le prompt stocké)
curl -X POST http://localhost:8000/api/generate/christmas/music \
  -H "Content-Type: application/json" \
  -d '{"language": "fr"}'

# Accéder au fichier généré
curl http://localhost:8000/storage/buckets/univers/christmas/fr.mp3
```

### ⭐ Fonctionnalités musique multilingue

- **Prompts personnalisés** par langue dans `univers_music_prompts`
- **Paroles synchronisées** avec la génération musicale
- **Génération automatique** utilisant les prompts stockés
- **URLs directes** : `/storage/buckets/univers/{slug}/{lang}.mp3`
- **Sync bidirectionnelle** : Prompts synchronisés avec Supabase

## 📝 Notes

- **⭐ Nouvelle table** : `univers_music_prompts` pour musique multilingue
- **⭐ Structure plate** : Fichiers directement dans `{slug}/` (pas de sous-dossiers)
- **⭐ Nommage cohérent** : `XX_nom.png` pour les assets (ex: `00_snowflake.png`)
- L'ancien dossier `/api` est conservé comme archive
- Les jobs sont persistés en SQLite et survivent aux redémarrages
- Les fichiers média sont servis via `/storage/buckets/...`
- Aucune modification des tables Supabase n'est requise
