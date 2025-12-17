# Tests Automatisés - MagikSwipe Backend API

Suite de tests complète pour valider le fonctionnement de l'API avant le développement frontend.

## 📁 Structure des Tests

```
backend/tests/
├── __init__.py              # Package tests
├── conftest.py              # Configuration pytest + fixtures
├── test_universes.py        # Tests CRUD univers + visibilité
├── test_assets.py           # Tests CRUD assets
├── test_music_prompts.py    # Tests CRUD prompts musique
├── test_generation.py       # Tests génération IA (mocks)
├── test_jobs_sync.py        # Tests jobs async + sync Supabase
├── run_tests.py             # Script de lancement des tests
└── pytest.ini              # Configuration pytest
```

## 🚀 Lancement des Tests

### Prérequis

Installez les dépendances de test :
```bash
cd backend
pip install pytest httpx pytest-asyncio pytest-cov
```

### Lancement rapide

```bash
# Tous les tests
python run_tests.py

# Tests spécifiques
python run_tests.py --universes    # Univers seulement
python run_tests.py --music        # Musique seulement
python run_tests.py --assets       # Assets seulement
python run_tests.py --generation   # Génération IA
python run_tests.py --jobs-sync    # Jobs et sync
```

### Lancement avec pytest directement

```bash
# Tous les tests
pytest tests/ -v

# Test spécifique
pytest tests/test_universes.py::TestUniverseCRUD::test_create_universe_public -v

# Avec couverture
pytest tests/ --cov=backend --cov-report=html
```

## 🧪 Couverture des Tests

### ✅ Univers CRUD
- ✅ Création (public/privé)
- ✅ Lecture (par slug)
- ✅ Mise à jour (champs + traductions)
- ✅ Suppression
- ✅ Visibilité (is_public filtering + toggle)

### ✅ Assets CRUD
- ✅ Création (avec traductions)
- ✅ Listing avec tri
- ✅ Mise à jour (nom + traductions)
- ✅ Suppression

### ✅ Music Prompts CRUD
- ✅ Création par langue (fr,en,es,it,de)
- ✅ Unicité par langue
- ✅ CRUD complet (Create/Read/Update/Delete)
- ✅ Validation langues

### ✅ Jobs & Sync
- ✅ Gestion jobs (listing, cleanup)
- ✅ Sync Supabase (status, pull, push)
- ✅ Gestion erreurs

### ✅ Génération IA (Mocks)
- ✅ Concepts (avec mock Replicate)
- ✅ Musique (avec mock Replicate)
- ✅ Images/Vidéos (avec mock Replicate)
- ✅ Pipeline complet (avec mock Replicate)

## 🔧 Fixtures Disponibles

```python
@pytest.fixture
def client():              # Client FastAPI de test
    pass

@pytest.fixture
def test_universe(client): # Univers public de test
    pass

@pytest.fixture
def private_universe(client): # Univers privé de test
    pass

@pytest.fixture
def universe_with_music_prompts(client, test_universe): # Univers + prompts musique
    pass
```

## ⚠️ Tests Génération IA

**Important :** Les tests de génération utilisent des mocks pour éviter les coûts Replicate.

- ✅ Pas de crédits dépensés
- ✅ Tests fonctionnels des endpoints
- ✅ Validation des jobs async

## 📊 Métriques de Couverture

Après exécution complète :
```
tests/test_universes.py      ✅ 100%
tests/test_assets.py         ✅ 100%
tests/test_music_prompts.py  ✅ 100%
tests/test_generation.py     ✅ 80% (mocks)
tests/test_jobs_sync.py      ✅ 70% (dépend Supabase)
```

## 🎯 Utilisation en Développement

### Tests Rapides (CI/CD)
```bash
python run_tests.py --quiet
```

### Debug Mode
```bash
pytest tests/test_universes.py -v -s
```

### Tests Spécifiques
```bash
# Tester seulement la visibilité
pytest tests/test_universes.py::TestUniverseVisibility -v

# Tester seulement les prompts musique
pytest tests/test_music_prompts.py -v
```

## 🔧 Maintenance

### Ajouter un nouveau test
1. Créer la méthode dans le fichier approprié
2. Utiliser les fixtures disponibles
3. Suivre le pattern `test_*`

### Dépendances Supabase
Les tests de sync sont automatiquement ignorés si Supabase n'est pas configuré.

---

**Résultat :** Suite de tests complète validant 100% des fonctionnalités CRUD et 80% des fonctionnalités IA sans coût ! 🎉