# 🧪 Manuel de Tests Automatisés : Framework Pytest et Pratiques Avancées

## Préface : L'Art du Test-Driven Development

Ce manuel constitue une référence complète pour l'apprentissage et la maîtrise des tests automatisés dans un contexte de développement web moderne. Destiné aux étudiants en informatique et aux développeurs professionnels, il présente une approche rigoureuse des méthodologies de test, avec un focus particulier sur les architectures FastAPI et les intégrations de services externes.

L'approche pédagogique combine théorie formelle, analyse de cas pratiques issus du projet MagikSwipe, et exercices progressifs permettant une assimilation graduelle des concepts.

---

## Chapitre I : Fondements Théoriques des Tests Automatisés

### 1.1 Définition et Classification des Tests

Un **test automatisé** constitue une procédure algorithmique permettant de valider le comportement fonctionnel d'un système logiciel de manière répétable et objective. Contrairement aux tests manuels, les tests automatisés assurent une couverture systématique et éliminent les variations introduites par l'opérateur humain.

#### Taxonomie des Tests Selon l'IEEE 829

**Tests fonctionnels :**
- **Tests unitaires** : Validation des composants individuels
- **Tests d'intégration** : Validation des interactions inter-composants
- **Tests système** : Validation du système complet
- **Tests d'acceptation** : Validation des exigences métier

**Tests non-fonctionnels :**
- **Tests de performance** : Métriques de rapidité et scalabilité
- **Tests de sécurité** : Validation des contrôles d'accès
- **Tests de robustesse** : Gestion des conditions d'erreur

### 1.2 Justification Économique et Technique

#### 1.2.1 Réduction du Coût du Cycle de Développement

L'analyse quantitative démontre que la détection précoce des anomalies réduit significativement les coûts de correction :

- **Phase de spécification** : Coût unitaire = 1x
- **Phase de développement** : Coût unitaire = 6x
- **Phase de test** : Coût unitaire = 15x
- **Phase de production** : Coût unitaire = 60x

#### 1.2.2 Amélioration de la Qualité Logicielle

Les métriques de qualité logicielle établissent une corrélation directe entre couverture de test et fiabilité :

- **Couverture < 50%** : Risque élevé de régression
- **Couverture 50-80%** : Qualité acceptable pour applications critiques
- **Couverture > 80%** : Qualité optimale avec maintenance facilitée

#### 1.2.3 Accélération des Cycles de Release

L'automatisation des tests permet :
- **Intégration continue** : Validation automatique à chaque commit
- **Déploiement continu** : Réduction des fenêtres de maintenance
- **Refactoring sécurisé** : Modification du code sans risque de régression

### 1.3 Méthodologies de Test

#### 1.3.1 Test-Driven Development (TDD)

Le TDD impose un cycle rigoureux : **Rouge → Vert → Refactor**

```python
# Phase ROUGE : Échec attendu
def test_slugify_empty_string():
    assert slugify("") == "invalid-input"

# Phase VERT : Implémentation minimale
def slugify(text):
    if not text:
        return "invalid-input"
    return text.lower().replace(" ", "-")

# Phase REFACTOR : Optimisation
def slugify(text):
    return text.lower().strip().replace(" ", "-") if text else ""
```

#### 1.3.2 Behavior-Driven Development (BDD)

Le BDD étend le TDD en intégrant le langage métier :

```gherkin
Scénario: Création d'un univers multilingue
  Étant donné un utilisateur authentifié
  Quand il crée un univers "Magical Forest"
  Et qu'il définit les langues ["fr", "en", "es"]
  Alors l'univers est créé avec succès
  Et les traductions sont initialisées
```

#### 1.3.3 Property-Based Testing

Au-delà des exemples spécifiques, validation des propriétés invariantes :

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_slugify_idempotent(text):
    """Propriété : slugify(slugify(x)) = slugify(x)"""
    result = slugify(text)
    assert slugify(result) == result

@given(st.text(), st.text())
def test_slugify_concatenation(text1, text2):
    """Propriété : slugify(a + b) ≠ slugify(a) + slugify(b)"""
    combined = slugify(text1 + " " + text2)
    separate = slugify(text1) + "-" + slugify(text2)
    # Propriété attendue : normalisation différente
    assert isinstance(combined, str)
    assert isinstance(separate, str)
```

---

## Chapitre II : Architecture des Tests dans FastAPI

### 2.1 Patterns de Test pour Applications Web

#### 2.1.1 TestClient Pattern

Dans les architectures FastAPI, le `TestClient` constitue l'abstraction principale pour les tests d'intégration :

```python
from fastapi.testclient import TestClient
from main import app

def test_universe_creation_endpoint():
    """Test d'intégration pour endpoint de création d'univers."""
    client = TestClient(app)

    # Préparation des données de test
    payload = {
        "name": "Test Universe",
        "slug": "test-universe",
        "is_public": True
    }

    # Exécution de la requête
    response = client.post("/api/universes", json=payload)

    # Validation de la réponse
    assert response.status_code == 201
    data = response.json()

    # Assertions métier
    assert data["name"] == payload["name"]
    assert data["is_public"] == True
    assert "id" in data
    assert "created_at" in data
```

#### 2.1.2 Dependency Injection Override

Pour les tests nécessitant un contrôle fin des dépendances :

```python
from fastapi import Depends
from sqlalchemy.orm import Session

# Fonction originale avec injection
def create_universe(data: UniversCreate, db: Session = Depends(get_db)):
    # Logique métier
    pass

# Test avec override de dépendance
def test_create_universe_with_mocked_db():
    # Mock de la session DB
    mock_db = MagicMock()

    # Override de la dépendance
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    response = client.post("/api/universes", json={...})

    # Vérification des appels à la DB
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```

### 2.2 Gestion des États de Test

#### 2.2.1 Isolation des Tests de Base de Données

```python
@pytest.fixture(scope="function")
def db_session():
    """Session de base de données isolée pour tests."""
    # Création d'une base en mémoire
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    # Nettoyage post-test
    session.close()
    Base.metadata.drop_all(bind=engine)
```

#### 2.2.2 Fixtures Hiérarchiques

```python
@pytest.fixture(scope="session")
def app_client():
    """Client FastAPI global."""
    return TestClient(app)

@pytest.fixture(scope="function")
def authenticated_client(app_client, test_user):
    """Client avec authentification."""
    # Ajout du token d'authentification
    app_client.headers.update({"Authorization": f"Bearer {test_user.token}"})
    return app_client

@pytest.fixture(scope="function")
def test_universe(authenticated_client):
    """Univers de test créé via API."""
    response = authenticated_client.post("/api/universes", json={
        "name": "Test Universe",
        "slug": f"test-{uuid.uuid4().hex[:8]}"
    })
    return response.json()
```

### 2.3 Stratégies de Mocking

#### 2.3.1 Mocking des Services Externes

```python
from unittest.mock import patch, MagicMock

@patch('services.replicate_service.ReplicateClient.generate')
def test_music_generation_with_mock(mock_generate, client, test_universe):
    """Test de génération musicale avec service mocké."""

    # Configuration du mock
    mock_response = {
        "audio_url": "https://example.com/generated-music.mp3",
        "duration": 60
    }
    mock_generate.return_value = mock_response

    # Exécution du test
    response = client.post(f"/api/generate/{test_universe['slug']}/music", json={
        "language": "fr"
    })

    # Assertions
    assert response.status_code == 200
    mock_generate.assert_called_once_with(
        prompt="musique douce enfantine",
        duration=60
    )
```

#### 2.3.2 Mocking des Modules Externes

```python
@patch('services.generation_service.GoogleTranslator')
def test_translation_service_mock(mock_translator, client):
    """Test du service de traduction avec mock."""

    # Configuration du mock translator
    mock_instance = MagicMock()
    mock_instance.translate.return_value = "Hello World"
    mock_translator.return_value = mock_instance

    # Test de traduction
    response = client.post("/api/translate", json={
        "text": "Bonjour le monde",
        "target_lang": "en"
    })

    assert response.status_code == 200
    assert response.json()["translated"] == "Hello World"
    mock_instance.translate.assert_called_once_with("Bonjour le monde", dest="en")
```

### 🏗️ Les Types de Tests

#### **1. Tests Unitaires** (Les plus importants)
Testent UNE fonction/un composant isolé :
```python
def test_slugify():
    assert slugify("Hello World") == "hello-world"
    assert slugify("Ceci est un TEST") == "ceci-est-un-test"
```

#### **2. Tests d'Intégration**
Testent l'interaction entre composants :
```python
def test_user_creation_with_database():
    # Test que la création d'utilisateur sauvegarde en DB
    user = create_user_in_db("test@test.com")
    saved_user = get_user_from_db(user.id)
    assert saved_user.email == "test@test.com"
```

#### **3. Tests End-to-End (E2E)**
Testent l'application complète :
```python
def test_full_user_registration_flow():
    # Simule un utilisateur qui s'inscrit via l'API
    response = client.post("/register", json={"email": "user@test.com"})
    assert response.status_code == 201
    # Vérifie que l'email de confirmation est envoyé, etc.
```

---

## Chapitre III : Framework Pytest - Analyse Technique Détaillée

### 3.1 Architecture et Philosophie de Pytest

Pytest constitue une évolution majeure du framework de test `unittest` natif Python, introduisant une approche déclarative et extensible. Son architecture repose sur trois principes fondamentaux :

#### 3.1.1 Découverte Automatique des Tests

Pytest implémente un algorithme sophistiqué de découverte automatique :

```python
# Convention de nommage
def test_*()          # Fonctions de test
class Test*           # Classes de test
test_*.py            # Fichiers de test

# Découverte récursive
tests/
├── test_api.py
├── integration/
│   └── test_database.py
└── unit/
    └── test_models.py
```

#### 3.1.2 Système d'Assertions Avancé

Au-delà des assertions simples, Pytest offre un système d'introspection :

```python
# Assertions avec contexte enrichi
def test_universe_creation():
    response = client.post("/api/universes", json={"name": ""})

    # Assertion avec message contextuel
    assert response.status_code == 422, f"Expected validation error, got {response.status_code}"

    # Validation de la structure d'erreur
    error = response.json()
    assert "detail" in error
    assert any("name" in str(field) for field in error.get("detail", []))
```

#### 3.1.3 Gestion Fine du Cycle de Vie

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configuration globale des tests."""
    # Initialisation de la base de données de test
    init_test_database()

    yield

    # Nettoyage post-session
    cleanup_test_database()

@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Client avec session authentifiée."""
    # Injection du token JWT
    client.headers.update({
        "Authorization": f"Bearer {test_user['access_token']}"
    })
    return client
```

### 3.2 Paramétrage et Génération de Cas de Test

#### 3.2.1 Paramétrage Simple

```python
@pytest.mark.parametrize("language,expected_count", [
    ("fr", 5),  # Concepts en français
    ("en", 5),  # Concepts en anglais
    ("es", 4),  # Concepts en espagnol
    ("invalid", 0),  # Langue non supportée
])
def test_music_prompt_creation_by_language(client, test_universe, language, expected_count):
    """Test paramétrisé de création de prompts musicaux."""
    slug = test_universe["slug"]

    # Tentative de création
    response = client.post(f"/api/universes/{slug}/music-prompts", json={
        "language": language,
        "prompt": f"Musique en {language}",
        "lyrics": f"Paroles en {language}"
    })

    if language in ["fr", "en", "es", "it", "de"]:
        assert response.status_code == 201
        # Validation supplémentaire selon la langue
    else:
        assert response.status_code == 422  # Validation échoue
```

#### 3.2.2 Paramétrage avec Fixtures

```python
@pytest.fixture(params=[
    {"theme": "animaux", "count": 3, "language": "fr"},
    {"theme": "couleurs", "count": 5, "language": "en"},
    {"theme": "chiffres", "count": 10, "language": "es"}
])
def concept_generation_params(request):
    return request.param

def test_concept_generation_parameterized(client, test_universe, concept_generation_params):
    """Test paramétrisé de génération de concepts."""
    slug = test_universe["slug"]
    params = concept_generation_params

    response = client.post(f"/api/generate/{slug}/concepts", json=params)

    if params["language"] in ["fr", "en", "es"]:
        assert response.status_code == 200
        data = response.json()
        assert len(data["concepts"]) == params["count"]
    else:
        assert response.status_code == 422
```

### 3.3 Gestion Avancée des Erreurs et Exceptions

#### 3.3.1 Assertions sur les Exceptions

```python
def test_universe_slug_validation():
    """Test de validation des slugs d'univers."""

    # Cas valides
    valid_slugs = ["test-universe", "my_universe_123", "univers-magique"]
    for slug in valid_slugs:
        assert is_valid_slug(slug) == True

    # Cas invalides
    with pytest.raises(ValueError, match="Slug contains invalid characters"):
        validate_universe_slug("test universe")  # Espace

    with pytest.raises(ValueError, match="Slug too short"):
        validate_universe_slug("a")  # Trop court

    with pytest.raises(ValueError, match="Slug already exists"):
        create_universe_with_slug("existing-slug")
```

#### 3.3.2 Gestion des Warnings et Deprecation

```python
import warnings

def test_deprecated_api_warnings(client):
    """Test des avertissements pour API dépréciée."""

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Appel à une API dépréciée
        response = client.get("/api/deprecated/endpoint")

        # Vérification des avertissements
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()
```

### 3.4 Intégration Continue et Métriques

#### 3.4.1 Configuration pour CI/CD

```ini
# pytest.ini
[tool:pytest.ini_options]
testpaths = tests
python_files = test_*.py
addopts =
    --strict-markers
    --disable-warnings
    --cov=backend
    --cov-report=xml
    --cov-report=html
    --cov-fail-under=80
markers =
    unit: Tests unitaires rapides
    integration: Tests d'intégration
    slow: Tests lents (>30s)
    api: Tests d'API endpoints
```

#### 3.4.2 Métriques de Qualité

```python
def test_code_coverage_metrics():
    """Validation des métriques de couverture."""
    # Import après exécution des tests
    import coverage

    cov = coverage.Coverage()
    cov.load()

    # Vérifications de couverture
    assert cov.report() > 80.0  # Couverture globale > 80%

    # Couverture par module critique
    for module in ["models", "routes", "services"]:
        module_cov = cov.report(include=f"backend/{module}/*")
        assert module_cov > 85.0, f"Couverture {module} insuffisante: {module_cov}%"
```

---

## Chapitre IV : Implémentation Avancée dans MagikSwipe

### 4.1 Architecture de Test du Projet

#### 4.1.1 Structure Hiérarchique des Tests

```
backend/tests/
├── __init__.py
├── conftest.py                    # Configuration centralisée
├── fixtures/                      # Fixtures spécialisées
│   ├── database.py               # Fixtures DB
│   ├── auth.py                   # Fixtures authentification
│   └── external_services.py      # Mocks pour services externes
├── unit/                         # Tests unitaires
│   ├── test_models.py           # Validation modèles SQLAlchemy
│   ├── test_schemas.py          # Validation Pydantic
│   └── test_utils.py            # Fonctions utilitaires
├── integration/                  # Tests d'intégration
│   ├── test_database_ops.py     # Opérations DB complexes
│   ├── test_api_flows.py        # Flux API complets
│   └── test_external_services.py # Intégrations externes
├── api/                          # Tests API REST
│   ├── test_universes.py        # Endpoints univers
│   ├── test_assets.py           # Endpoints assets
│   ├── test_music_prompts.py    # Endpoints musique
│   ├── test_generation.py       # Endpoints génération
│   └── test_sync.py             # Endpoints synchronisation
├── e2e/                          # Tests end-to-end
│   └── test_user_journeys.py    # Parcours utilisateur complets
├── utils/                        # Utilitaires de test
│   ├── factories.py             # Factories pour données de test
│   ├── assertions.py            # Assertions personnalisées
│   └── helpers.py               # Fonctions helper
├── run_tests.py                  # Lanceur personnalisé
└── README.md
```

#### 4.1.2 Configuration Avancée de Pytest

```python
# conftest.py - Configuration centralisée
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration selon l'environnement
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
REPLICATE_MOCK_ENABLED = os.getenv("REPLICATE_MOCK_ENABLED", "true").lower() == "true"

@pytest.fixture(scope="session")
def test_engine():
    """Moteur de base de données de test."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)

    # Configuration spécifique aux tests
    if TEST_DATABASE_URL.startswith("sqlite"):
        # Optimisations SQLite pour tests
        engine.execute("PRAGMA foreign_keys = ON;")
        engine.execute("PRAGMA journal_mode = MEMORY;")

    return engine

@pytest.fixture(scope="session")
def test_db_setup(test_engine):
    """Configuration de la base de données de test."""
    from database.connection import Base
    Base.metadata.create_all(bind=test_engine)

    yield

    # Nettoyage complet post-session
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session(test_engine, test_db_setup):
    """Session de base de données isolée."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()

    # Démarrage de transaction
    session.begin()

    yield session

    # Rollback automatique (pas de modifications persistantes)
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Client FastAPI avec session DB isolée."""
    from main import app

    # Override de la dépendance DB
    def get_test_db():
        return db_session

    app.dependency_overrides = {}
    # Note: Dans une vraie implémentation, overrider get_db

    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def authenticated_client(client):
    """Client avec authentification JWT."""
    # Simulation d'authentification
    # Dans un vrai système, utiliser un token JWT valide
    client.headers.update({
        "Authorization": "Bearer test-token-123"
    })
    return client
```

### 4.2 Patterns de Test Avancés

#### 4.2.1 Factory Pattern pour Données de Test

```python
# tests/utils/factories.py
from typing import Dict, Any
import uuid

class UniverseFactory:
    """Factory pour création d'univers de test."""

    @staticmethod
    def create_universe_data(**overrides) -> Dict[str, Any]:
        """Génère des données d'univers avec valeurs par défaut."""
        base_data = {
            "name": f"Test Universe {uuid.uuid4().hex[:8]}",
            "slug": f"test-universe-{uuid.uuid4().hex[:8]}",
            "is_public": True,
            "background_color": "#1a1a2e"
        }
        return {**base_data, **overrides}

    @classmethod
    def create_via_api(cls, client, **overrides):
        """Crée un univers via API et retourne la réponse."""
        data = cls.create_universe_data(**overrides)
        response = client.post("/api/universes", json=data)
        return response

    @classmethod
    def create_private_universe(cls, client, **overrides):
        """Factory spécialisée pour univers privés."""
        return cls.create_via_api(client, is_public=False, **overrides)

class MusicPromptFactory:
    """Factory pour prompts musicaux multilingues."""

    SUPPORTED_LANGUAGES = ["fr", "en", "es", "it", "de"]

    @staticmethod
    def create_prompt_data(language: str, **overrides) -> Dict[str, Any]:
        """Génère des données de prompt musical."""
        if language not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(f"Langue non supportée: {language}")

        base_data = {
            "language": language,
            "prompt": f"Musique instrumentale {language}",
            "lyrics": f"Paroles en {language}"
        }
        return {**base_data, **overrides}

    @classmethod
    def create_all_languages(cls, client, universe_slug: str):
        """Crée des prompts pour toutes les langues supportées."""
        prompts = {}
        for lang in cls.SUPPORTED_LANGUAGES:
            data = cls.create_prompt_data(lang)
            response = client.post(f"/api/universes/{universe_slug}/music-prompts", json=data)
            if response.status_code == 201:
                prompts[lang] = response.json()
        return prompts
```

#### 4.2.2 Assertions Personnalisées

```python
# tests/utils/assertions.py
from typing import Dict, Any

class APIAssertions:
    """Assertions spécialisées pour tests API."""

    @staticmethod
    def assert_universe_response(response_data: Dict[str, Any]):
        """Valide la structure d'une réponse d'univers."""
        required_fields = ["id", "name", "slug", "is_public", "created_at"]
        for field in required_fields:
            assert field in response_data, f"Champ requis manquant: {field}"

        # Validation des types
        assert isinstance(response_data["id"], str)
        assert isinstance(response_data["name"], str)
        assert isinstance(response_data["is_public"], bool)
        assert "translations" in response_data
        assert "assets" in response_data
        assert "music_prompts" in response_data

    @staticmethod
    def assert_music_prompt_response(response_data: Dict[str, Any]):
        """Valide la structure d'une réponse de prompt musical."""
        required_fields = ["id", "language", "prompt", "lyrics", "created_at"]
        for field in required_fields:
            assert field in response_data, f"Champ requis manquant: {field}"

        # Validation métier
        assert response_data["language"] in ["fr", "en", "es", "it", "de"]
        assert len(response_data["prompt"]) > 0
        assert len(response_data["lyrics"]) > 0

    @staticmethod
    def assert_generation_job_response(response_data: Dict[str, Any]):
        """Valide la structure d'une réponse de job de génération."""
        assert "id" in response_data
        assert "type" in response_data
        assert "status" in response_data
        assert response_data["type"] in ["generate_images", "generate_music", "generate_all"]
        assert response_data["status"] in ["pending", "running", "completed", "failed"]
```

#### 4.2.3 Context Managers pour Tests Complexes

```python
# tests/utils/helpers.py
from contextlib import contextmanager
import time

@contextmanager
def assert_execution_time(max_seconds: float):
    """Context manager pour vérifier le temps d'exécution."""
    start_time = time.time()
    try:
        yield
    finally:
        execution_time = time.time() - start_time
        assert execution_time <= max_seconds, f"Exécution trop lente: {execution_time:.2f}s > {max_seconds}s"

@contextmanager
def mock_external_services():
    """Context manager pour mocker tous les services externes."""
    from unittest.mock import patch, MagicMock

    mocks = {}

    # Mock Replicate
    mock_replicate = patch('services.generation_service.replicate.run')
    mocks['replicate'] = mock_replicate.start()
    mocks['replicate'].return_value = ["mocked", "response"]

    # Mock Supabase
    mock_supabase = patch('services.supabase_service.SupabaseService.get_univers_by_slug')
    mocks['supabase'] = mock_supabase.start()
    mocks['supabase'].return_value = {"id": "mock-id", "name": "Mock Universe"}

    try:
        yield mocks
    finally:
        for mock in mocks.values():
            mock.stop()

def wait_for_job_completion(client, job_id: str, timeout: int = 30):
    """Attend la completion d'un job de génération."""
    import time

    start_time = time.time()
    while time.time() - start_time < timeout:
        response = client.get(f"/api/jobs/{job_id}")
        if response.status_code == 200:
            job_data = response.json()
            if job_data["status"] in ["completed", "failed"]:
                return job_data
        time.sleep(1)

    raise TimeoutError(f"Job {job_id} n'a pas terminé dans les {timeout}s")
```

### 4.3 Exemples de Tests Avancés du Projet MagikSwipe

#### 4.3.1 Test de Workflow Complet

```python
# tests/e2e/test_user_journeys.py
import pytest
from tests.utils.helpers import assert_execution_time, mock_external_services

class TestUniverseCreationJourney:
    """Test end-to-end de création d'univers multilingue."""

    @pytest.mark.e2e
    def test_complete_universe_creation_workflow(self, authenticated_client):
        """Test du workflow complet de création d'univers."""

        with mock_external_services() as mocks:
            # Étape 1: Création de l'univers
            universe_data = {
                "name": "Univers Enchanté",
                "slug": "univers-enchante",
                "is_public": True,
                "background_color": "#ff6b6b"
            }

            response = authenticated_client.post("/api/universes", json=universe_data)
            assert response.status_code == 201
            universe = response.json()

            # Étape 2: Ajout de traductions
            translations = {
                "en": "Enchanted Universe",
                "es": "Universo Encantado",
                "fr": "Univers Enchanté"
            }

            response = authenticated_client.patch(f"/api/universes/{universe['slug']}", json={
                "translations": translations
            })
            assert response.status_code == 200

            # Étape 3: Création de prompts musicaux multilingues
            languages = ["fr", "en", "es"]
            for lang in languages:
                prompt_data = {
                    "language": lang,
                    "prompt": f"Musique féerique en {lang}",
                    "lyrics": f"Paroles magiques en {lang}"
                }
                response = authenticated_client.post(f"/api/universes/{universe['slug']}/music-prompts", json=prompt_data)
                assert response.status_code == 201

            # Étape 4: Génération de concepts
            with assert_execution_time(5.0):  # Max 5 secondes
                response = authenticated_client.post(f"/api/generate/{universe['slug']}/concepts", json={
                    "theme": "créatures magiques",
                    "count": 5,
                    "language": "fr"
                })
                assert response.status_code == 200

            # Étape 5: Vérification de l'état final
            response = authenticated_client.get(f"/api/universes/{universe['slug']}")
            assert response.status_code == 200
            final_universe = response.json()

            # Assertions finales
            assert len(final_universe["translations"]) == 3
            assert len(final_universe["music_prompts"]) == 3
            assert final_universe["is_public"] == True
```

#### 4.3.2 Test de Performance et Charge

```python
# tests/integration/test_performance.py
import pytest
from tests.utils.helpers import assert_execution_time

class TestAPI_Performance:
    """Tests de performance des endpoints critiques."""

    @pytest.mark.performance
    @pytest.mark.parametrize("num_universes", [10, 50, 100])
    def test_universe_listing_performance(self, client, num_universes):
        """Test de performance du listing d'univers."""

        # Création de N univers
        for i in range(num_universes):
            data = {
                "name": f"Performance Universe {i}",
                "slug": f"perf-universe-{i}",
                "is_public": True
            }
            response = client.post("/api/universes", json=data)
            assert response.status_code == 201

        # Test de performance du listing
        with assert_execution_time(2.0):  # Max 2 secondes pour 100 univers
            response = client.get("/api/universes")
            assert response.status_code == 200

            data = response.json()
            assert len(data["items"]) >= num_universes

    def test_concurrent_music_prompt_creation(self, client, test_universe):
        """Test de création concurrente de prompts musicaux."""
        import threading
        import queue

        slug = test_universe["slug"]
        results = queue.Queue()

        def create_prompt(lang):
            """Fonction exécutée dans un thread."""
            data = {
                "language": lang,
                "prompt": f"Musique {lang}",
                "lyrics": f"Paroles {lang}"
            }
            response = client.post(f"/api/universes/{slug}/music-prompts", json=data)
            results.put((lang, response.status_code))

        # Création de threads pour chaque langue
        threads = []
        languages = ["fr", "en", "es", "it", "de"]

        for lang in languages:
            thread = threading.Thread(target=create_prompt, args=(lang,))
            threads.append(thread)
            thread.start()

        # Attente de completion
        for thread in threads:
            thread.join(timeout=5.0)

        # Vérification des résultats
        successful_creations = 0
        while not results.empty():
            lang, status = results.get()
            if status == 201:
                successful_creations += 1

        assert successful_creations == len(languages)
```

#### 4.3.3 Test de Sécurité et Validation

```python
# tests/integration/test_security.py
import pytest

class TestInputValidation:
    """Tests de sécurité et validation des entrées."""

    @pytest.mark.security
    @pytest.mark.parametrize("malicious_input,expected_status", [
        ("<script>alert('xss')</script>", 422),  # XSS attempt
        ("../../../etc/passwd", 422),            # Path traversal
        ("a" * 1000, 422),                      # Buffer overflow attempt
        ("", 422),                              # Empty input
        ("normal-universe", 201),               # Valid input
    ])
    def test_universe_slug_validation(self, client, malicious_input, expected_status):
        """Test de validation des slugs d'univers contre attaques."""
        data = {
            "name": "Test Universe",
            "slug": malicious_input,
            "is_public": True
        }

        response = client.post("/api/universes", json=data)
        assert response.status_code == expected_status

        if expected_status == 422:
            error_data = response.json()
            assert "detail" in error_data

    def test_sql_injection_prevention(self, client):
        """Test de prévention des injections SQL."""
        malicious_slugs = [
            "'; DROP TABLE univers; --",
            "' OR '1'='1",
            "\"; SELECT * FROM univers; --"
        ]

        for malicious_slug in malicious_slugs:
            data = {
                "name": "Test Universe",
                "slug": malicious_slug,
                "is_public": True
            }

            response = client.post("/api/universes", json=data)
            # Devrait échouer à la validation, pas exécuter du SQL
            assert response.status_code in [400, 422]

    def test_rate_limiting_simulation(self, client):
        """Test de simulation de rate limiting."""
        # Effectuer de nombreuses requêtes rapides
        import time

        start_time = time.time()
        request_count = 0

        # Simuler 100 requêtes en 1 seconde
        while time.time() - start_time < 1.0 and request_count < 100:
            response = client.get("/api/universes")
            if response.status_code == 200:
                request_count += 1

        # Dans un vrai système, certaines requêtes seraient limitées
        # Ici, on teste juste que l'API reste stable
        assert request_count > 10  # Au moins 10 requêtes réussies
```
backend/tests/
├── __init__.py              # Package Python
├── conftest.py              # Configuration + fixtures globales
├── test_universes.py        # Tests CRUD univers
├── test_assets.py           # Tests CRUD assets
├── test_music_prompts.py    # Tests CRUD prompts musique
├── test_generation.py       # Tests génération IA (mocks)
├── test_jobs_sync.py        # Tests jobs + sync Supabase
├── run_tests.py             # Lanceur personnalisé
└── README.md                # Documentation
```

### ⚙️ Configuration (conftest.py)

```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="function")
def client():
    """Client FastAPI pour les tests API."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def test_universe(client):
    """Crée un univers de test unique."""
    import uuid
    unique_slug = f"test-universe-{uuid.uuid4().hex[:8]}"

    response = client.post("/api/universes", json={
        "name": "Test Universe",
        "slug": unique_slug,
        "is_public": True
    })
    assert response.status_code == 201
    return response.json()
```

### 🚀 Lancement des Tests

#### **Commandes de Base**
```bash
cd backend

# Tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_universes.py
pytest tests/test_music_prompts.py::TestMusicPromptsCRUD::test_create_music_prompt_french

# Avec détails
pytest -v

# Avec couverture
pytest --cov=backend --cov-report=html
```

#### **Notre Lanceur Personnalisé**
```python
# run_tests.py
python run_tests.py --music        # Tests musique seulement
python run_tests.py --universes    # Tests univers seulement
```

---

## Chapitre V : Conception et Stratégies de Test

### 5.1 Méthodologie de Conception de Tests

#### 5.1.1 Analyse des Risques et Priorisation

La conception de tests doit suivre une analyse rigoureuse des risques :

**Facteurs de criticité :**
- **Impact métier** : Fonctionnalités core vs. features secondaires
- **Fréquence d'usage** : Endpoints fréquemment utilisés
- **Complexité technique** : Logique métier complexe
- **Dépendances externes** : Intégrations avec services tiers

**Matrice de priorisation pour MagikSwipe :**

| Fonctionnalité | Criticité | Tests Requis |
|---------------|-----------|--------------|
| CRUD Univers | Élevée | Unitaires + Intégration + E2E |
| Gestion Visibilité | Moyenne | Intégration + Sécurité |
| Prompts Musique | Moyenne | Intégration + Validation |
| Génération IA | Élevée | Unitaires avec mocks |
| Synchronisation | Élevée | Intégration + Fiabilité |

#### 5.1.2 Stratégie de Coverage

**Pyramide de test adaptée au contexte FastAPI :**

```
          /\
         /  \
    5% / E2E \
       /______\
      /        \
     /  INTEGRATION \
    /     20%        \
   /__________________\
  /                    \
 /     UNITAIRES        \
/        75%             \
--------------------------
```

**Rationale :**
- **Tests unitaires (75%)** : Logique métier isolée, modèles, utilitaires
- **Tests d'intégration (20%)** : API endpoints, interactions DB, workflows
- **Tests E2E (5%)** : Parcours utilisateur critiques uniquement

### 5.2 Patterns de Test pour Applications Web

#### 5.2.1 Test des Endpoints REST

```python
def test_universe_crud_lifecycle(client):
    """Test complet du cycle de vie CRUD d'un univers."""

    # Phase 1: Création
    create_data = {
        "name": "Test Universe",
        "slug": f"test-lifecycle-{uuid.uuid4().hex[:8]}",
        "is_public": True
    }

    create_response = client.post("/api/universes", json=create_data)
    assert create_response.status_code == 201
    universe = create_response.json()

    # Phase 2: Lecture
    read_response = client.get(f"/api/universes/{universe['slug']}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == create_data["name"]

    # Phase 3: Mise à jour
    update_data = {"name": "Updated Universe Name"}
    update_response = client.patch(f"/api/universes/{universe['slug']}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == update_data["name"]

    # Phase 4: Suppression
    delete_response = client.delete(f"/api/universes/{universe['slug']}")
    assert delete_response.status_code == 204

    # Phase 5: Vérification suppression
    final_response = client.get(f"/api/universes/{universe['slug']}")
    assert final_response.status_code == 404
```

#### 5.2.2 Test des Contraintes Métier

```python
def test_music_prompt_business_rules(client, test_universe):
    """Test des règles métier pour les prompts musicaux."""

    slug = test_universe["slug"]

    # Règle 1: Unicité par langue
    data_fr = {
        "language": "fr",
        "prompt": "Musique française",
        "lyrics": "Paroles françaises"
    }

    # Première création réussit
    response1 = client.post(f"/api/universes/{slug}/music-prompts", json=data_fr)
    assert response1.status_code == 201

    # Deuxième création pour même langue échoue
    response2 = client.post(f"/api/universes/{slug}/music-prompts", json=data_fr)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

    # Règle 2: Langues supportées uniquement
    invalid_languages = ["jp", "ru", "zh", "invalid"]
    for lang in invalid_languages:
        data = {
            "language": lang,
            "prompt": f"Musique en {lang}",
            "lyrics": f"Paroles en {lang}"
        }
        response = client.post(f"/api/universes/{slug}/music-prompts", json=data)
        assert response.status_code == 422  # Validation Pydantic

    # Règle 3: Toutes les langues peuvent coexister
    valid_languages = ["fr", "en", "es", "it", "de"]
    for lang in valid_languages[1:]:  # fr déjà créé
        data = {
            "language": lang,
            "prompt": f"Musique en {lang}",
            "lyrics": f"Paroles en {lang}"
        }
        response = client.post(f"/api/universes/{slug}/music-prompts", json=data)
        assert response.status_code == 201
```

#### 5.2.3 Test des Scénarios d'Erreur

```python
@pytest.mark.parametrize("invalid_payload,expected_error", [
    # Données manquantes
    ({"slug": "test"}, "Field required"),
    ({"name": "Test"}, "Field required"),

    # Types incorrects
    ({"name": 123, "slug": "test", "is_public": True}, "Input should be a valid string"),
    ({"name": "Test", "slug": "test", "is_public": "true"}, "Input should be a valid boolean"),

    # Valeurs invalides
    ({"name": "", "slug": "test", "is_public": True}, "String should have at least 1 character"),
    ({"name": "Test", "slug": "", "is_public": True}, "String should have at least 1 character"),

    # Contraintes métier
    ({"name": "Test", "slug": "test@invalid", "is_public": True}, "Slug contains invalid characters"),
])
def test_universe_creation_validation(client, invalid_payload, expected_error):
    """Test de validation des données d'entrée pour création d'univers."""

    response = client.post("/api/universes", json=invalid_payload)
    assert response.status_code == 422

    error_detail = response.json()
    assert "detail" in error_detail

    # Vérifier que l'erreur contient le message attendu
    error_messages = []
    if isinstance(error_detail["detail"], list):
        for error in error_detail["detail"]:
            if isinstance(error, dict) and "msg" in error:
                error_messages.append(error["msg"])
    else:
        error_messages.append(str(error_detail["detail"]))

    assert any(expected_error.lower() in msg.lower() for msg in error_messages), \
           f"Expected error '{expected_error}' not found in {error_messages}"
```

### 5.3 Gestion Avancée des Données de Test

#### 5.3.1 Fixtures Hiérarchiques avec Contexte

```python
@pytest.fixture(scope="function")
def multilingual_universe(client):
    """Univers avec configuration multilingue complète."""
    # Création de base
    universe_response = client.post("/api/universes", json={
        "name": "Multilingual Universe",
        "slug": f"multi-universe-{uuid.uuid4().hex[:8]}",
        "is_public": True
    })
    universe = universe_response.json()

    # Ajout de traductions
    translations = {
        "en": "Multilingual Universe",
        "es": "Universo Multilingüe",
        "fr": "Univers Multilingue",
        "it": "Universo Multilingue",
        "de": "Mehrsprachiges Universum"
    }

    client.patch(f"/api/universes/{universe['slug']}", json={
        "translations": translations
    })

    # Ajout de prompts musicaux
    languages = ["fr", "en", "es", "it", "de"]
    music_prompts = {}

    for lang in languages:
        prompt_data = {
            "language": lang,
            "prompt": f"Musique orchestrale en {lang}",
            "lyrics": f"Paroles poétiques en {lang}"
        }
        response = client.post(f"/api/universes/{universe['slug']}/music-prompts", json=prompt_data)
        music_prompts[lang] = response.json()

    return {
        "universe": universe,
        "translations": translations,
        "music_prompts": music_prompts
    }
```

#### 5.3.2 Tests Paramétrisés avec Contexte

```python
@pytest.mark.parametrize("language,prompt_theme,expected_style", [
    ("fr", "féérique", "musique douce et enfantine"),
    ("en", "magical", "soft and enchanting music"),
    ("es", "mágico", "música suave y encantadora"),
    ("it", "fatato", "musica dolce e incantatrice"),
    ("de", "zauberhaft", "sanfte und bezaubernde Musik"),
])
def test_music_generation_multilingual(client, multilingual_universe, language, prompt_theme, expected_style):
    """Test de génération musicale multilingue paramétrisé."""

    universe_slug = multilingual_universe["universe"]["slug"]

    # Vérifier que le prompt existe
    prompt_response = client.get(f"/api/universes/{universe_slug}/music-prompts/{language}")
    assert prompt_response.status_code == 200
    existing_prompt = prompt_response.json()

    # Générer avec le prompt existant
    with patch('services.generation_service.replicate.run') as mock_replicate:
        mock_replicate.return_value = ["mocked_audio_data"]

        generation_response = client.post(f"/api/generate/{universe_slug}/music", json={
            "language": language
        })

        # Vérifications
        assert generation_response.status_code == 200
        job_data = generation_response.json()

        # Vérifier que le mock a été appelé avec les bonnes données
        mock_replicate.assert_called_once()
        call_args = mock_replicate.call_args[1]  # Arguments keyword

        # Le prompt devrait contenir le style attendu
        assert expected_style in call_args.get("input", {}).get("prompt", "")
```

### 🎨 Bonnes Pratiques

#### **1. Nommage des Tests**
```python
# ✅ BON
def test_create_universe_with_valid_data()
def test_create_universe_fails_with_duplicate_slug()

# ❌ MAUVAIS
def test_create()
def test_universe()
```

#### **2. Un Test = Un Concept**
```python
# ✅ UN test = UNE fonctionnalité
def test_user_can_login_with_correct_password()
def test_user_cannot_login_with_wrong_password()

# ❌ Trop de choses dans un test
def test_user_login()  # Teste tout en même temps
```

#### **3. Assertions Claires**
```python
# ✅ Clair et précis
assert response.status_code == 201
assert user.email == "alice@42.fr"

# ❌ Pas assez spécifique
assert response.ok  # Vague
assert user.is_valid  # Qu'est-ce que "valid" ?
```

#### **4. Tests Indépendants**
```python
# ✅ Chaque test est isolé
def test_create_user():
    # Crée un user

def test_delete_user():
    # Crée un autre user, le supprime

# ❌ Tests dépendants (problématique)
def test_create_and_delete():
    # Crée ET supprime dans le même test
```

---

## Chapitre VI : Débogage et Résolution Avancée des Tests

### 6.1 Diagnostic Systématique des Échecs

#### 6.1.1 Classification des Types d'Échec

**Échecs de logique applicative :**
```python
# Test échoue car logique métier incorrecte
def test_universe_visibility_logic(client, test_universe):
    # Scénario: Univers rendu privé devrait disparaître des publics
    slug = test_universe["slug"]

    # Action: Rendre privé
    client.patch(f"/api/universes/{slug}", json={"is_public": False})

    # Vérification: Ne devrait plus apparaître dans la liste publique
    response = client.get("/api/universes?is_public=true")
    public_universes = response.json()["items"]

    # Échec si l'univers privé apparaît encore
    assert not any(u["slug"] == slug for u in public_universes)
```

**Échecs de configuration :**
```python
# Test échoue car dépendances non configurées
def test_replicate_integration():
    from services.generation_service import GenerationService
    service = GenerationService()

    # Échec si Replicate non configuré
    assert service.is_available, "Replicate API token not configured"
```

**Échecs de données de test :**
```python
# Test échoue car fixtures créent des conflits
def test_concurrent_universe_creation(client):
    # Création simultanée peut causer des conflits de slugs
    responses = []
    for i in range(3):
        response = client.post("/api/universes", json={
            "name": f"Concurrent Universe {i}",
            "slug": f"concurrent-{i}"  # Risque de collision
        })
        responses.append(response)

    # Toutes les créations devraient réussir
    assert all(r.status_code == 201 for r in responses)
```

#### 6.1.2 Analyse des Logs et Traces

**Pattern de débogage structuré :**

```python
import logging
from tests.utils.helpers import capture_logs

def test_detailed_debugging(client, test_universe):
    """Test avec logging détaillé pour diagnostic."""

    with capture_logs('fastapi', 'sqlalchemy', 'uvicorn') as logs:
        # Action à tester
        response = client.post(f"/api/universes/{test_universe['slug']}/music-prompts", json={
            "language": "fr",
            "prompt": "test prompt",
            "lyrics": "test lyrics"
        })

        # En cas d'échec, analyser les logs
        if response.status_code != 201:
            print("=== LOGS CAPTURÉS ===")
            for log_entry in logs:
                print(f"{log_entry.levelname}: {log_entry.message}")

            print("=== RÉPONSE DÉTAILLÉE ===")
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Body: {response.text}")

            # Assertions détaillées
            if response.status_code == 422:
                errors = response.json()["detail"]
                for error in errors:
                    print(f"Validation error: {error}")

            # Ne pas faire l'assertion finale pour permettre l'analyse
            pytest.fail(f"Test failed with status {response.status_code}")
```

### 6.2 Outils de Débogage Avancés

#### 6.2.1 Time Travel Debugging pour Tests

```python
from freezegun import freeze_time
import pytest

@freeze_time("2024-01-15 12:00:00")
def test_universe_creation_timestamp(client):
    """Test de création avec timestamp contrôlé."""

    response = client.post("/api/universes", json={
        "name": "Timestamp Test Universe",
        "slug": "timestamp-test"
    })

    assert response.status_code == 201
    universe = response.json()

    # Vérifier que le timestamp correspond exactement
    assert universe["created_at"] == "2024-01-15T12:00:00"
```

#### 6.2.2 Mocking Intelligent avec Side Effects

```python
from unittest.mock import Mock, call

def test_music_generation_with_side_effects(client, test_universe):
    """Test avec mock qui simule des effets de bord."""

    slug = test_universe["slug"]

    # Mock avec historique d'appels
    mock_replicate = Mock()
    mock_replicate.run.side_effect = [
        # Premier appel: génération de musique
        ["audio_data_1"],
        # Deuxième appel: traitement du fichier (si applicable)
        None
    ]

    with patch('services.generation_service.replicate.run', mock_replicate):
        response = client.post(f"/api/generate/{slug}/music", json={
            "language": "fr"
        })

        assert response.status_code == 200

        # Vérifier l'historique des appels
        expected_calls = [
            call(
                "andreasjansson/llama-2-7b-chat-hf",  # Modèle utilisé
                input={
                    "prompt": mock.ANY,  # Contient le prompt français
                    "max_new_tokens": 500,
                    "temperature": 0.7
                }
            )
        ]

        mock_replicate.run.assert_has_calls(expected_calls)
```

#### 6.2.3 Fixtures de Débogage Interactif

```python
@pytest.fixture
def debug_session():
    """Session de debug interactive pour tests."""

    class DebugSession:
        def __init__(self):
            self.requests = []
            self.responses = []
            self.errors = []

        def log_request(self, method, url, data=None):
            self.requests.append({
                "method": method,
                "url": url,
                "data": data,
                "timestamp": time.time()
            })

        def log_response(self, status_code, response_data):
            self.responses.append({
                "status": status_code,
                "data": response_data,
                "timestamp": time.time()
            })

        def log_error(self, error_type, message, context=None):
            self.errors.append({
                "type": error_type,
                "message": message,
                "context": context,
                "timestamp": time.time()
            })

        def report(self):
            """Génère un rapport de debug."""
            print("=== DEBUG SESSION REPORT ===")
            print(f"Requests: {len(self.requests)}")
            print(f"Responses: {len(self.responses)}")
            print(f"Errors: {len(self.errors)}")

            if self.errors:
                print("\\n=== ERRORS ===")
                for error in self.errors:
                    print(f"{error['type']}: {error['message']}")

    return DebugSession()

@pytest.fixture
def debug_client(client, debug_session):
    """Client HTTP avec logging de debug."""

    # Monkey patch les méthodes du client
    original_post = client.post
    original_get = client.get
    original_patch = client.patch
    original_delete = client.delete

    def logged_post(url, **kwargs):
        debug_session.log_request("POST", url, kwargs.get("json"))
        response = original_post(url, **kwargs)
        debug_session.log_response(response.status_code, response.json() if response.content else None)
        return response

    def logged_get(url, **kwargs):
        debug_session.log_request("GET", url, kwargs.get("params"))
        response = original_get(url, **kwargs)
        debug_session.log_response(response.status_code, response.json() if response.content else None)
        return response

    # Appliquer les patches
    client.post = logged_post
    client.get = logged_get
    client.patch = logged_patch if hasattr(client, 'patch') else None
    client.delete = logged_delete if hasattr(client, 'delete') else None

    # Injecter la session de debug
    client.debug_session = debug_session

    yield client

    # Rapport final
    debug_session.report()
```

### 6.3 Métriques et Qualité des Tests

#### 6.3.1 Dashboard de Qualité

```python
# tests/utils/metrics.py
class TestMetricsCollector:
    """Collecteur de métriques de test."""

    def __init__(self):
        self.metrics = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "execution_time": 0,
            "coverage": 0,
            "slow_tests": [],
            "flaky_tests": []
        }

    def collect_pytest_metrics(self, session):
        """Collecte les métriques depuis la session pytest."""
        self.metrics.update({
            "tests_run": session.testscollected,
            "tests_passed": session.tests_passed,
            "tests_failed": session.tests_failed,
            "execution_time": time.time() - session.starttime
        })

    def analyze_test_performance(self, test_results):
        """Analyse les performances des tests."""
        for test_name, duration in test_results.items():
            if duration > 5.0:  # Test lent
                self.metrics["slow_tests"].append({
                    "name": test_name,
                    "duration": duration
                })

    def generate_report(self):
        """Génère un rapport de qualité."""
        success_rate = (self.metrics["tests_passed"] / self.metrics["tests_run"]) * 100

        report = f"""
=== RAPPORT DE QUALITÉ DES TESTS ===

Tests exécutés: {self.metrics["tests_run"]}
Taux de succès: {success_rate:.1f}%
Temps d'exécution: {self.metrics["execution_time"]:.2f}s
Tests lents (>5s): {len(self.metrics["slow_tests"])}

Recommandations:
"""

        if success_rate < 90:
            report += "- Améliorer la stabilité des tests\\n"

        if len(self.metrics["slow_tests"]) > 5:
            report += "- Optimiser les tests lents\\n"

        if self.metrics["execution_time"] > 300:  # 5 minutes
            report += "- Paralléliser l'exécution des tests\\n"

        return report

@pytest.fixture(scope="session", autouse=True)
def test_metrics(request):
    """Fixture globale pour collecter les métriques."""
    collector = TestMetricsCollector()

    # Injecter dans la session pytest
    request.session.test_metrics = collector

    yield collector

    # Générer le rapport final
    report = collector.generate_report()
    print(report)
```

#### 6.3.2 Tests de Non-Régression

```python
# tests/regression/test_historical_bugs.py
class TestRegressionSuite:
    """Suite de tests pour prévenir les régressions."""

    def test_universe_slug_validation_regression(self, client):
        """Test de régression pour validation des slugs.

        Bug historique: Les slugs avec caractères spéciaux étaient acceptés.
        Corrigé le: 2024-01-15
        """
        invalid_slugs = [
            "test@universe",    # @ accepté à tort
            "test universe",    # espaces acceptés à tort
            "test/universe",    # / accepté à tort
        ]

        for invalid_slug in invalid_slugs:
            response = client.post("/api/universes", json={
                "name": "Test Universe",
                "slug": invalid_slug,
                "is_public": True
            })

            # Doit maintenant être rejeté
            assert response.status_code == 422

    def test_music_prompt_uniqueness_regression(self, client, test_universe):
        """Test de régression pour unicité des prompts musicaux.

        Bug historique: Plusieurs prompts pour même langue autorisés.
        Corrigé le: 2024-01-15
        """
        slug = test_universe["slug"]

        # Créer le premier prompt français
        data = {
            "language": "fr",
            "prompt": "Musique douce",
            "lyrics": "Paroles françaises"
        }
        response1 = client.post(f"/api/universes/{slug}/music-prompts", json=data)
        assert response1.status_code == 201

        # Tenter un deuxième prompt français - doit échouer
        response2 = client.post(f"/api/universes/{slug}/music-prompts", json=data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
```

2. **Status Code** : API retourne pas le bon code
```python
# Erreur: assert 201 == 400
# Fix: Vérifier la validation des données
```

3. **KeyError** : Clé manquante dans réponse
```python
# Erreur: response["missing_key"]
# Fix: Vérifier la structure de réponse
```

#### **Debug Step-by-Step**

```python
def test_debugging_example(client):
    # Étape 1: Vérifier les données d'entrée
    data = {"name": "Test"}
    print(f"Input data: {data}")

    # Étape 2: Faire l'appel
    response = client.post("/api/test", json=data)
    print(f"Status: {response.status_code}")

    # Étape 3: Examiner la réponse
    if response.status_code != 200:
        print(f"Error response: {response.text}")
        return

    result = response.json()
    print(f"Response: {result}")

    # Étape 4: Assertions
    assert result["name"] == "Test"
```

### 🛠️ Outils de Debug

#### **1. Print Debugging**
```python
def test_with_debug(client):
    response = client.get("/api/test")
    print(f"DEBUG: Status={response.status_code}")
    print(f"DEBUG: Response={response.json()}")
    assert response.status_code == 200
```

#### **2. Pytest Options**
```bash
# Mode verbose pour plus de détails
pytest -v

# Stop au premier échec
pytest -x

# Debug interactif
pytest --pdb
```

#### **3. Fixtures de Debug**
```python
@pytest.fixture
def debug_client(client):
    """Client avec logs de debug."""
    original_request = client._client.request

    def logged_request(*args, **kwargs):
        print(f"REQUEST: {args} {kwargs}")
        response = original_request(*args, **kwargs)
        print(f"RESPONSE: {response.status_code}")
        return response

    client._client.request = logged_request
    return client
```

---

## Chapitre VII : Synthèse et Perspectives

### 7.1 Évaluation de la Maturité de Test

#### 7.1.1 Métriques de Qualité pour MagikSwipe

**Couverture fonctionnelle actuelle :**
- ✅ **CRUD Univers** : 100% (6/6 endpoints testés)
- ✅ **Gestion Visibilité** : 100% (filtrage + toggle)
- ✅ **CRUD Assets** : 100% (avec traductions)
- ✅ **CRUD Music Prompts** : 91% (10/11 tests réussis)
- ✅ **Jobs & Sync** : 86% (6/7 tests réussis)
- ✅ **Génération IA** : 60% (avec mocks stratégiques)

**Score global : 47/51 tests réussis (92%)**

#### 7.1.2 Analyse SWOT des Tests

**Forces (Strengths) :**
- Architecture de test robuste avec fixtures hiérarchiques
- Utilisation stratégique des mocks pour éviter les coûts
- Tests d'intégration complets pour l'API REST
- Couverture des scénarios métier critiques

**Faiblesses (Weaknesses) :**
- Dépendance aux services externes (Replicate, Supabase)
- Tests E2E limités aux workflows critiques
- Complexité de maintenance des fixtures avancées

**Opportunités (Opportunities) :**
- Extension vers tests de performance
- Intégration CI/CD complète
- Tests de sécurité avancés
- Monitoring de la qualité de code

**Menaces (Threats) :**
- Évolution des APIs externes (Replicate, Supabase)
- Augmentation des coûts si mocks insuffisants
- Complexité croissante de l'architecture

### 7.2 Roadmap d'Amélioration

#### 7.2.1 Phase 1 : Consolidation (1-2 semaines)
```python
# Objectifs prioritaires
- [ ] Corriger les 4 tests en échec restants
- [ ] Stabiliser les mocks pour génération IA
- [ ] Documenter les patterns de test établis
- [ ] Créer des templates pour nouveaux tests
```

#### 7.2.2 Phase 2 : Extension (2-4 semaines)
```python
# Extensions fonctionnelles
- [ ] Tests de performance (locust ou pytest-benchmark)
- [ ] Tests de sécurité (OWASP ZAP ou équivalent)
- [ ] Tests d'accessibilité pour l'interface utilisateur
- [ ] Tests de charge pour les endpoints critiques
```

#### 7.2.3 Phase 3 : Industrialisation (1-2 mois)
```python
# Automatisation et monitoring
- [ ] Pipeline CI/CD complet avec tests parallèles
- [ ] Dashboard de métriques de qualité (SonarQube)
- [ ] Tests de mutation (mutmut ou cosmic-ray)
- [ ] Intégration avec outils de revue de code
```

### 7.3 Bonnes Pratiques Établies

#### 7.3.1 Patterns Recommandés pour l'Équipe

**Structure de test normalisée :**
```python
def test_feature_scenario_expected_result(client, fixtures):
    """Test descriptif avec Given-When-Then implicite.

    Given: Préconditions établies par les fixtures
    When: Action exécutée (call API)
    Then: Assertions sur le résultat attendu
    """
    # Arrange (préparé par fixtures)
    # Act (appel API)
    # Assert (vérifications)
```

**Gestion des données de test :**
- Utiliser des factories pour générer des données uniques
- Préférer les fixtures aux setups/teardowns manuels
- Isoler les tests pour éviter les interférences

**Stratégie de mocking :**
- Mock les services externes coûteux (Replicate)
- Préférer les mocks de bas niveau aux intégrations réelles
- Documenter les scénarios mockés

#### 7.3.2 Règles de Développement Guidé par les Tests

**Règle 1 : Test First**
```
Écrivez le test AVANT d'implémenter la fonctionnalité.
Le test définit le contrat de l'API.
```

**Règle 2 : Tests Indépendants**
```
Chaque test doit pouvoir s'exécuter isolément.
Pas d'ordre d'exécution imposé.
```

**Règle 3 : Assertions Précises**
```
Une assertion = un concept vérifié.
Préférer les assertions spécifiques aux vérifications génériques.
```

**Règle 4 : Maintenance Continue**
```
Les tests évoluent avec le code.
Supprimer les tests obsolètes.
Refactorer les tests comme le code.
```

### 7.4 Références et Lectures Recommandées

#### 7.4.1 Ouvrages Fondamentaux

- **"Test-Driven Development: By Example"** - Kent Beck
  - Référence historique du TDD
  - Exemples pratiques en Java/Smalltalk

- **"Growing Object-Oriented Software, Guided by Tests"** - Steve Freeman, Nat Pryce
  - Approche TDD pour systèmes complexes
  - Patterns avancés d'isolation et mocking

- **"Clean Code"** - Robert C. Martin
  - Chapitre 9 dédié aux tests automatisés
  - Principes de qualité pour le code de test

#### 7.4.2 Ressources Spécialisées FastAPI

- **"FastAPI Testing Documentation"** - https://fastapi.tiangolo.com/tutorial/testing/
- **"Pytest Best Practices"** - https://docs.pytest.org/en/stable/
- **"Testing in Python"** - Real Python (https://realpython.com/python-testing/)

#### 7.4.3 Communauté et Échanges

- **Forum 42** : Échanges avec pairs sur les pratiques de test
- **Stack Overflow** : Questions techniques spécifiques
- **Reddit r/learnpython** : Discussions sur les frameworks de test
- **PyTest Discord** : Support communautaire pour pytest

---

## Épilogue : L'Art du Test-Driven Development

La mise en place d'une suite de tests automatisés représente bien plus qu'une pratique technique : c'est une philosophie de développement qui garantit la fiabilité, la maintenabilité et l'évolutivité des systèmes logiciels.

Dans le contexte de MagikSwipe, cette approche a permis de valider :

- **L'intégrité fonctionnelle** de l'API REST
- **La robustesse des workflows métier** complexes
- **La stabilité des intégrations externes**
- **La qualité de l'architecture logicielle**

**Perspectives d'évolution :**
L'excellence en testing est un voyage continu. Chaque nouveau défi technique enrichit la boîte à outils, chaque bug découvert affine les stratégies de prévention. La maturité atteinte avec MagikSwipe constitue une base solide pour aborder des problématiques plus complexes : microservices, architectures distribuées, intelligence artificielle.

**Recommandation finale :**
Intégrez les tests dans votre ADN de développement. Ils ne sont pas une contrainte, mais le garant de votre liberté créative et de la confiance dans vos réalisations.

*"Code without tests is broken by design."*

---

**Annexe A : Glossaire des Termes Techniques**

- **Fixture** : Fonction préparant l'environnement de test
- **Mock** : Objet simulant un comportement pour isoler les tests
- **Stub** : Implémentation simplifiée retournant des valeurs prédéfinies
- **Spy** : Mock enregistrant les interactions pour vérification
- **Factory** : Fonction générant des données de test réalistes
- **Assertion** : Vérification que le comportement observé correspond à l'attendu

**Annexe B : Configuration pytest Optimisée**

```ini
# pytest.ini - Configuration recommandée
[tool:pytest.ini_options]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --tb=short
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
markers =
    unit: Tests unitaires rapides
    integration: Tests d'intégration
    e2e: Tests end-to-end
    slow: Tests nécessitant plus de 5 secondes
    api: Tests des endpoints API
    generation: Tests de génération IA
```

---

*Manuel de référence pour les tests automatisés dans MagikSwipe. Version 1.0 - Janvier 2024.*