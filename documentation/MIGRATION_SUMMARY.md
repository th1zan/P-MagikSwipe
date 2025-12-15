# 🎉 Migration vers architecture Drafts - Résumé des changements

## ✅ Fichiers créés

### Structure de données
- `storage/prompts_defaults.yaml` - Templates de prompts par thème (remplace default_prompts.json)
- `storage/drafts/.gitkeep` - Dossier pour les brouillons

### Backend (API)
- `api/models.py` - Modèles Pydantic pour validation des données
- `api/routes/drafts.py` - Nouveaux endpoints pour gérer les drafts
- `api/services/supabase_service.py` - Service pour interactions avec Supabase
- `api/services/__init__.py` - Module d'initialisation des services

### Frontend (Viewer)
- `viewer/js/drafts_patch.js` - Patch pour adapter le viewer aux nouveaux endpoints

### Scripts utilitaires
- `migrate_to_drafts.py` - Migration des univers existants vers drafts
- `test_drafts_workflow.py` - Script de test du workflow complet
- `supabase_optimize.sql` - Optimisations et index pour Supabase

### Documentation
- `README_DRAFTS.md` - Documentation complète de la nouvelle architecture
- `.env.example` - Exemple de configuration

## 🔧 Fichiers modifiés

### Configuration
- `docker-compose.yml` - Simplifié (suppression service generator, renommage viewer → studio)
- `api/requirements.txt` - Ajout de pydantic et python-slugify

### API
- `api/main.py` - Ajout des routes drafts

### Viewer
- `viewer/index.html` - Inclusion du patch drafts

## 📦 Nouvelle structure

```
P-MagikSwipe/
├── storage/
│   ├── prompts_defaults.yaml    ✨ NOUVEAU
│   ├── drafts/                  ✨ NOUVEAU (brouillons locaux)
│   └── univers/                 📦 LEGACY (à migrer)
│
├── api/
│   ├── models.py                ✨ NOUVEAU
│   ├── services/                ✨ NOUVEAU
│   │   ├── __init__.py
│   │   └── supabase_service.py
│   ├── routes/
│   │   ├── drafts.py            ✨ NOUVEAU
│   │   ├── universes.py         📦 LEGACY (toujours disponible)
│   │   ├── generation.py        📦 LEGACY
│   │   └── prompts.py           📦 LEGACY
│   ├── main.py                  🔧 MODIFIÉ
│   └── requirements.txt         🔧 MODIFIÉ
│
├── viewer/
│   ├── js/
│   │   └── drafts_patch.js      ✨ NOUVEAU
│   └── index.html               🔧 MODIFIÉ
│
├── docker-compose.yml           🔧 MODIFIÉ
├── migrate_to_drafts.py         ✨ NOUVEAU
├── test_drafts_workflow.py      ✨ NOUVEAU
├── supabase_optimize.sql        ✨ NOUVEAU
├── README_DRAFTS.md             ✨ NOUVEAU
└── .env.example                 ✨ NOUVEAU
```

## 🚀 Étapes pour utiliser la nouvelle architecture

### 1. Mettre à jour les dépendances

```bash
cd /Users/thibault/Documents/P-MagikSwipe
docker compose down
docker compose build
```

### 2. Migrer les univers existants (optionnel, 1 minute)

```bash
# Via le script shell
./migrate.sh

# Ou via Docker
docker compose exec api python /app/migrate_to_drafts.py
```

### 3. Optimiser Supabase (recommandé)

Exécuter le script SQL dans Supabase SQL Editor :
```bash
cat supabase_optimize.sql
# Copier-coller dans https://app.supabase.com/project/YOUR_PROJECT/sql
```

### 4. Lancer les services

```bash
docker compose up -d
```

### 5. Tester le workflow

```bash
# Option 1: Via le Studio
open http://localhost:8081

# Option 2: Via le script de test
python3 test_drafts_workflow.py
```

## 🎯 Nouveaux endpoints disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/drafts` | Créer un draft |
| GET | `/api/drafts` | Liste des drafts |
| GET | `/api/drafts/{id}` | Détails d'un draft |
| GET | `/api/drafts/{id}/assets` | Assets d'un draft |
| GET | `/api/drafts/{id}/status` | Statut génération (polling) |
| POST | `/api/drafts/{id}/generate` | Lancer génération |
| PATCH | `/api/drafts/{id}/assets/{asset_id}/regenerate` | Régénérer asset |
| POST | `/api/drafts/{id}/publish` | Publier vers Supabase |
| DELETE | `/api/drafts/{id}` | Supprimer draft |

## 🔄 Workflow de création (avant/après)

### ❌ Avant (ancien système)

```
1. Créer univers → génère data.json + prompts.json
2. Générer tout d'un coup (pas de régénération individuelle)
3. Publish manuel via endpoint
4. Sync bidirectionnel (risque de conflits)
```

### ✅ Après (nouveau système)

```
1. Créer draft → génère metadata.json + assets_metadata.json
2. Générer assets (avec progression en temps réel)
3. Régénérer individuellement si besoin
4. Publier vers Supabase (unidirectionnel, pas de conflits)
```

## 📊 Avantages de la nouvelle architecture

| Fonctionnalité | Avant | Après |
|----------------|-------|-------|
| **Régénération individuelle** | ❌ Non | ✅ Oui |
| **Suivi de progression** | ❌ Non | ✅ Oui (polling) |
| **Prompts sauvegardés Supabase** | ❌ Non | ✅ Oui (nouvelles tables) |
| **Séparation draft/prod** | ❌ Non | ✅ Oui |
| **Risque de conflits sync** | ⚠️ Oui | ✅ Non |
| **Compatibilité ascendante** | - | ✅ Oui (anciens endpoints conservés) |

## ⚠️ Points d'attention

### Anciens endpoints toujours disponibles

Les endpoints legacy (`/api/universes`, `/api/generation`) sont conservés pour compatibilité, mais il est recommandé d'utiliser les nouveaux endpoints `/api/drafts`.

### Migration des données

Les univers dans `storage/univers/` ne sont PAS automatiquement migrés. Utiliser `migrate_to_drafts.py` si besoin.

### Configuration Supabase

Les nouvelles tables doivent exister dans Supabase :
- `univers_prompts`
- `univers_assets_prompts`

Elles sont créées automatiquement si vous avez exécuté le schéma fourni.

## 🧪 Checklist de vérification

- [ ] Services démarrent correctement (`docker compose ps`)
- [ ] API répond (`curl http://localhost:8000/api/drafts`)
- [ ] Studio accessible (`open http://localhost:8081`)
- [ ] Création de draft fonctionne
- [ ] Génération d'assets fonctionne
- [ ] Régénération individuelle fonctionne
- [ ] Publication vers Supabase fonctionne
- [ ] App mobile lit les données publiées

## 📚 Documentation

Pour plus de détails, voir `README_DRAFTS.md`.

## 🐛 En cas de problème

### Les services ne démarrent pas

```bash
docker compose logs -f
```

### Erreur "table does not exist"

Vérifier que les tables Supabase sont créées. Exécuter `supabase_optimize.sql`.

### Génération bloquée

Vérifier les logs API :
```bash
docker compose logs -f api
```

Vérifier le token Replicate :
```bash
docker compose exec api env | grep REPLICATE
```

## 🎉 C'est prêt !

Votre backend est maintenant migré vers la nouvelle architecture drafts. 

Profitez de :
- ✨ Régénération d'assets individuels
- 📊 Suivi de progression en temps réel
- 🔒 Séparation claire brouillon/production
- 💾 Sauvegarde complète des prompts dans Supabase

Bonne création d'univers ! 🚀
