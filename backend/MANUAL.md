# Manuel de Formation : Développement Backend avec FastAPI, SQLAlchemy et Tâches Asynchrones

## MagikSwipe - Application d'Apprentissage pour Enfants Alimentée par IA

---

**Auteurs :** Équipe MagikSwipe  
**Version :** 2.0.0  
**Date :** Décembre 2025  
**Technologies :** FastAPI, SQLAlchemy, Python 3.11  

---

## Table des Matières

### [Introduction](#introduction)
- [Présentation du Projet](#présentation-du-projet)
- [Architecture Générale](#architecture-générale)
- [Prérequis Techniques](#prérequis-techniques)

### [Chapitre 1 : Concepts Fondamentaux](#chapitre-1--concepts-fondamentaux)
- [1.1 APIs REST](#11-apis-rest)
- [1.2 HTTP et Méthodes](#12-http-et-méthodes)
- [1.3 JSON et Sérialisation](#13-json-et-sérialisation)
- [1.4 Bases de Données Relationnelles](#14-bases-de-données-relationnelles)
- [1.5 Programmation Asynchrone](#15-programmation-asynchrone)

### [Chapitre 2 : FastAPI - Framework Moderne pour APIs](#chapitre-2--fastapi---framework-moderne-pour-apis)
- [2.1 Introduction à FastAPI](#21-introduction-à-fastapi)
- [2.2 Routage et Endpoints](#22-routage-et-endpoints)
- [2.3 Validation Automatique avec Pydantic](#23-validation-automatique-avec-pydantic)
- [2.4 Injection de Dépendances](#24-injection-de-dépendances)
- [2.5 Gestion d'Erreurs](#25-gestion-derreurs)
- [2.6 Middleware et CORS](#26-middleware-et-cors)
- [2.7 Documentation Automatique](#27-documentation-automatique)

### [Chapitre 3 : SQLAlchemy - ORM Python](#chapitre-3--sqlalchemy---orm-python)
- [3.1 Introduction aux ORM](#31-introduction-aux-orm)
- [3.2 Configuration de SQLAlchemy](#32-configuration-de-sqlalchemy)
- [3.3 Modèles de Données](#33-modèles-de-données)
- [3.4 Sessions et Transactions](#34-sessions-et-transactions)
- [3.5 Requêtes et Filtres](#35-requêtes-et-filtres)
- [3.6 Relations Entre Tables](#36-relations-entre-tables)
- [3.7 Migrations et Évolution](#37-migrations-et-évolution)

### [Chapitre 4 : Tâches Asynchrones et Jobs](#chapitre-4--tâches-asynchrones-et-jobs)
- [4.1 Programmation Asynchrone en Python](#41-programmation-asynchrone-en-python)
- [4.2 Architecture des Jobs](#42-architecture-des-jobs)
- [4.3 Gestion du Cycle de Vie](#43-gestion-du-cycle-de-vie)
- [4.4 Monitoring et Logging](#44-monitoring-et-logging)
- [4.5 Gestion d'Erreurs](#45-gestion-derreurs)
- [4.6 Performance et Scalabilité](#46-performance-et-scalabilité)

### [Chapitre 5 : Architecture du Projet](#chapitre-5--architecture-du-projet)
- [5.1 Structure des Dossiers](#51-structure-des-dossiers)
- [5.2 Services et Responsabilités](#52-services-et-responsabilités)
- [5.3 Configuration Centralisée](#53-configuration-centralisée)
- [5.4 Gestion des Erreurs](#54-gestion-des-erreurs)
- [5.5 Sécurité et Authentification](#55-sécurité-et-authentification)

### [Chapitre 6 : Exemples Pratiques du Code](#chapitre-6--exemples-pratiques-du-code)
- [6.1 Création d'un Univers](#61-création-dun-univers)
- [6.2 Génération de Contenu IA](#62-génération-de-contenu-ia)
- [6.3 Gestion des Jobs Asynchrones](#63-gestion-des-jobs-asynchrones)
- [6.4 Synchronisation avec Supabase](#64-synchronisation-avec-supabase)

### [Chapitre 7 : Bonnes Pratiques](#chapitre-7--bonnes-pratiques)
- [7.1 Patterns de Développement](#71-patterns-de-développement)
- [7.2 Optimisation des Performances](#72-optimisation-des-performances)
- [7.3 Tests et Qualité](#73-tests-et-qualité)
- [7.4 Déploiement et Monitoring](#74-déploiement-et-monitoring)

### [Annexes](#annexes)
- [Annexe A : Schémas de Base de Données](#annexe-a--schémas-de-base-de-données)
- [Annexe B : Endpoints API](#annexe-b--endpoints-api)
- [Annexe C : Configuration](#annexe-c--configuration)
- [Annexe D : Glossaire](#annexe-d--glossaire)

---

## Introduction

### Présentation du Projet

**MagikSwipe** est une application web éducative innovante conçue pour l'apprentissage des enfants, alimentée par l'intelligence artificielle. L'application permet aux éducateurs et parents de créer des univers thématiques personnalisés (animaux, espace, voitures, etc.) et de générer automatiquement du contenu multimédia adapté aux enfants.

#### Fonctionnalités Clés
- **Création d'Univers** : Espaces thématiques personnalisables
- **Génération IA** : Images, vidéos et musique générées automatiquement
- **Traduction Multi-langues** : Support français, anglais, espagnol, italien, allemand
- **Synchronisation Cloud** : Sauvegarde et partage via Supabase
- **Interface Web Moderne** : Viewer interactif avec diaporamas

#### Technologies Employées
- **Backend** : FastAPI (Python) pour l'API REST
- **Base de Données** : SQLite avec SQLAlchemy ORM
- **IA** : Intégration Replicate pour génération de contenu
- **Stockage** : Système de fichiers local + Supabase Storage
- **Interface Web** : Viewer HTML/CSS/JavaScript vanilla

### Architecture Générale

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Viewer        │────│   Backend       │────│   Services      │
│   (Interface)   │    │   (FastAPI)     │    │   Externes      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │   API REST      │    │   Replicate     │
│   Utilisateur   │    │   Endpoints     │    │   (IA)          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌─────────────────┐               │
│   SQLite        │    │   Supabase      │◄──────────────┘
│   (Local)       │    │   (Cloud)       │
└─────────────────┘    └─────────────────┘
```

### Prérequis Techniques

#### Connaissances Requises
- **Python** : Niveau intermédiaire (classes, fonctions, modules)
- **HTTP/REST** : Concepts de base des APIs web
- **Bases de Données** : SQL et concepts relationnels
- **Programmation Asynchrone** : Concepts de base (optionnel mais recommandé)

#### Environnement de Développement
- **Python 3.11+**
- **SQLite** (inclus avec Python)
- **Git** pour le contrôle de version
- **Docker** pour le déploiement (optionnel)

---

## Chapitre 1 : Concepts Fondamentaux

### 1.1 APIs REST

Les APIs REST (Representational State Transfer) constituent l'épine dorsale de la communication moderne entre applications web. Elles définissent un ensemble de conventions pour structurer les échanges de données sur le web.

#### Principes REST
- **Stateless** : Chaque requête contient toutes les informations nécessaires
- **Client-Server** : Séparation claire entre client et serveur
- **Cacheable** : Possibilité de mettre en cache les réponses
- **Uniform Interface** : Interface uniforme utilisant les méthodes HTTP

#### Ressources et Endpoints
Dans MagikSwipe, chaque "univers" est une ressource accessible via des endpoints :

```http
GET    /api/universes           # Lister tous les univers
POST   /api/universes           # Créer un nouvel univers
GET    /api/universes/{slug}    # Obtenir un univers spécifique
PUT    /api/universes/{slug}    # Modifier un univers
DELETE /api/universes/{slug}    # Supprimer un univers
```

### 1.2 HTTP et Méthodes

HTTP (HyperText Transfer Protocol) est le protocole de communication du web. Chaque requête HTTP contient :

- **Méthode** : Action à effectuer (GET, POST, PUT, DELETE, etc.)
- **URL** : Adresse de la ressource cible
- **Headers** : Métadonnées (Content-Type, Authorization, etc.)
- **Body** : Données de la requête (pour POST/PUT)

#### Méthodes HTTP Utilisées dans MagikSwipe

| Méthode | Usage | Exemple |
|---------|-------|---------|
| `GET` | Récupération de données | `GET /api/universes` |
| `POST` | Création de ressources | `POST /api/universes` |
| `PUT` | Modification complète | `PUT /api/universes/animals` |
| `PATCH` | Modification partielle | `PATCH /api/universes/animals` |
| `DELETE` | Suppression | `DELETE /api/universes/animals` |

#### Codes de Statut HTTP

Les réponses HTTP incluent un code de statut indiquant le résultat :

- **200-299** : Succès
- **300-399** : Redirection
- **400-499** : Erreur client (mauvaise requête)
- **500-599** : Erreur serveur

### 1.3 JSON et Sérialisation

JSON (JavaScript Object Notation) est le format standard pour l'échange de données dans les APIs REST modernes.

#### Structure JSON dans MagikSwipe

```json
{
  "id": "uuid-string",
  "name": "Animaux de la Forêt",
  "slug": "animaux-foret",
  "is_public": true,
  "created_at": "2025-12-17T10:30:00Z",
  "assets": [
    {
      "id": "asset-uuid",
      "display_name": "Renard",
      "image_name": "01_renard.png"
    }
  ]
}
```

#### Sérialisation Python ↔ JSON

FastAPI gère automatiquement la conversion entre objets Python et JSON grâce à Pydantic.

### 1.4 Bases de Données Relationnelles

Une base de données relationnelle organise les données en tables liées par des relations.

#### Concepts Clés
- **Tables** : Collections d'enregistrements similaires
- **Colonnes** : Attributs des enregistrements
- **Lignes** : Enregistrements individuels
- **Clés Primaires** : Identifiants uniques
- **Clés Étrangères** : Liens entre tables

#### Schéma MagikSwipe

```
┌─────────────────┐       ┌─────────────────┐
│   univers       │───────│   univers_assets│
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ univers_id (FK) │
│ slug            │       │ display_name    │
│ is_public       │       │ image_name      │
│ ...             │       │ sort_order      │
└─────────────────┘       └─────────────────┘
```

### 1.5 Programmation Asynchrone

L'asynchrone permet d'exécuter des tâches sans bloquer le programme principal.

#### Concepts Clés
- **Synchrone** : Une tâche à la fois, blocage du programme
- **Asynchrone** : Plusieurs tâches simultanément, non-bloquant
- **Threading** : Exécution parallèle dans des threads séparés
- **Asyncio** : Programmation asynchrone native Python

#### Pourquoi Asynchrone dans MagikSwipe ?

La génération IA peut prendre du temps (plusieurs minutes). L'asynchrone permet :
- De retourner immédiatement une réponse au client
- De traiter plusieurs générations simultanément
- D'éviter les timeouts côté client

---

## Chapitre 2 : FastAPI - Framework Moderne pour APIs

### 2.1 Introduction à FastAPI

FastAPI est un framework moderne pour construire des APIs REST avec Python. Il combine la simplicité de Flask avec les performances d'APIs typées.

#### Avantages de FastAPI
- **Performance** : Aussi rapide que NodeJS et Go
- **Sécurité de Type** : Validation automatique des données
- **Documentation** : OpenAPI/Swagger généré automatiquement
- **Développement Rapide** : Moins de code répétitif

#### Installation et Configuration

```bash
pip install fastapi uvicorn[standard]
```

#### Application de Base

```python
from fastapi import FastAPI

app = FastAPI(
    title="Mon API",
    description="Description de l'API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Hello World"}
```

### 2.2 Routage et Endpoints

FastAPI utilise des décorateurs pour définir les routes et organise le code avec des routeurs.

#### Structure des Routes dans MagikSwipe

```python
# backend/routes/universes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/universes", tags=["universes"])

@router.get("", response_model=UniversListResponse)
def list_universes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all universes with pagination."""
    # Logique métier ici
    pass

@router.post("", response_model=UniversResponse, status_code=201)
def create_universe(data: UniversCreate, db: Session = Depends(get_db)):
    """Create a new universe."""
    # Logique de création
    pass
```

#### Paramètres de Route

FastAPI supporte différents types de paramètres :

- **Paramètres de chemin** : `/users/{user_id}`
- **Paramètres de requête** : `?skip=0&limit=10`
- **Paramètres de corps** : JSON dans le body de la requête

### 2.3 Validation Automatique avec Pydantic

Pydantic fournit une validation automatique des données entrantes et sortantes.

#### Modèles Pydantic dans MagikSwipe

```python
# backend/schemas/__init__.py
from pydantic import BaseModel, Field
from typing import Optional

class UniversCreate(BaseModel):
    """Schéma pour créer un univers."""
    name: str = Field(..., min_length=1, max_length=100)
    is_public: bool = True
    background_color: Optional[str] = "#1a1a2e"

class UniversResponse(BaseModel):
    """Réponse complète d'un univers."""
    id: str
    name: str
    slug: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True  # Conversion depuis objets SQLAlchemy
```

#### Validation Automatique

```python
@app.post("/universes")
def create_universe(data: UniversCreate):
    # FastAPI valide automatiquement que :
    # - name est une string non-vide de 1-100 caractères
    # - is_public est un booléen
    # - background_color est optionnel et string si fourni
    return {"message": "Univers créé"}
```

### 2.4 Injection de Dépendances

L'injection de dépendances (Dependency Injection - DI) est un pattern de conception où les dépendances d'un objet (comme une session de base de données) sont fournies de l'extérieur plutôt que créées à l'intérieur de la classe ou fonction. Cela permet de gérer automatiquement les ressources partagées, rendant le code plus modulaire, testable et maintenable.

#### Concept Fondamental
Dans une API REST, chaque endpoint a besoin d'accéder à des ressources partagées comme :
- Sessions de base de données
- Services externes (cache, authentification)
- Configurations
- Autres dépendances transversales

Sans injection de dépendances, chaque fonction devrait créer ses propres ressources :
```python
# ❌ Code sans DI - difficile à tester
def list_universes():
    db = SessionLocal()  # Création manuelle
    try:
        return db.query(Univers).all()
    finally:
        db.close()  # Nettoyage manuel
```

Avec DI, les dépendances sont injectées automatiquement.

#### Fonctionnement dans MagikSwipe

##### La Fonction `get_db()` (backend/database/connection.py)
```python
def get_db():
    """Fournit une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Comment ça marche :**
- Utilise `yield` pour créer un générateur (coroutine)
- FastAPI capture le contexte `try/finally` automatiquement
- Garantit que la session DB est toujours fermée, même en cas d'erreur
- Chaque requête HTTP obtient sa propre session isolée

##### Utilisation dans les Routes (backend/routes/universes.py)
```python
@router.get("/universes")
def list_universes(db: Session = Depends(get_db)):
    # db est automatiquement injecté
    # et nettoyé après la requête
    universes = db.query(Univers).all()
    return universes
```

**Mécanisme FastAPI :**
1. Reçoit une requête HTTP sur `/universes`
2. Voit `db: Session = Depends(get_db)`
3. Appelle `get_db()` qui retourne un générateur
4. Exécute la fonction route avec `db` comme argument
5. À la fin de la requête, exécute le `finally` du générateur
6. Ferme automatiquement la session DB

#### Avantages Détaillés

##### **Réutilisabilité**
- Même logique de gestion DB partout dans l'application
- Un seul endroit pour modifier la configuration de base de données
- Cohérence dans toute l'API REST

##### **Testabilité**
```python
# ✅ Tests faciles avec injection mock
def test_list_universes():
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = [mock_univers]

    result = list_universes(db=mock_db)
    # Test sans vraie base de données !
```

##### **Nettoyage Automatique**
- Sessions DB toujours fermées (évite les fuites de connexions)
- Gestion automatique des erreurs et exceptions
- Ressources libérées même si l'endpoint lève une exception
- Pas de risque d'oublier de fermer une connexion

##### **Séparation des Responsabilités**
- Les routes se concentrent sur la logique métier
- La gestion des ressources est centralisée
- Plus facile à maintenir, déboguer et étendre

#### Pattern Étendu à d'Autres Dépendances

Le même pattern s'applique à toutes les dépendances transversales :

```python
# Injection d'utilisateur authentifié
def get_current_user(token: str = Depends(get_token)):
    """Valide et retourne l'utilisateur actuel."""
    # Logique de validation JWT
    return user

@router.get("/protected")
def protected_route(user: User = Depends(get_current_user)):
    # Utilisateur automatiquement validé et injecté
    return {"user": user.name}

# Injection de services
def get_generation_service():
    """Fournit le service de génération IA."""
    return GenerationService()

@router.post("/generate")
def generate_content(
    data: GenerateRequest,
    gen_service = Depends(get_generation_service)
):
    # Service injecté automatiquement
    return gen_service.generate(data)
```

#### Bonnes Pratiques

- **Toujours utiliser `Depends()`** pour les ressources partagées
- **Préférer les générateurs** (`yield`) pour les ressources nécessitant un nettoyage
- **Nommer clairement** les fonctions de dépendance (`get_db`, `get_user`, etc.)
- **Tester avec des mocks** pour isoler les unités de code
- **Éviter les dépendances circulaires** entre services

Cette approche rend MagikSwipe plus robuste, testable et maintenable, suivant les meilleures pratiques modernes du développement FastAPI.

### 2.5 Gestion d'Erreurs

FastAPI fournit des mécanismes robustes pour gérer les erreurs.

#### Exceptions HTTP

```python
from fastapi import HTTPException

@router.get("/universes/{slug}")
def get_universe(slug: str, db: Session = Depends(get_db)):
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(
            status_code=404, 
            detail=f"Univers '{slug}' non trouvé"
        )
    
    return univers
```

#### Gestionnaires d'Erreurs Globaux

```python
# backend/main.py
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Données invalides", "errors": exc.errors()}
    )
```

### 2.6 Middleware et CORS

Le middleware est un composant logiciel qui s'insère entre le serveur web et l'application, permettant d'intercepter, analyser et modifier les requêtes HTTP entrantes et les réponses sortantes. C'est comme un "filtre" ou un "intercepteur" qui peut ajouter des fonctionnalités transversales (logging, sécurité, performance, etc.).

#### Qu'est-ce que le Middleware ?

Le middleware fonctionne selon le pattern "chaîne de responsabilité" :
- Chaque middleware reçoit la requête
- Il peut la modifier ou ajouter des informations
- Il passe la requête au middleware suivant (ou à l'application finale)
- Il reçoit la réponse du middleware suivant
- Il peut modifier la réponse avant de la retourner

```
Requête HTTP → [Middleware 1] → [Middleware 2] → [Middleware 3] → Application → [Middleware 3] → [Middleware 2] → [Middleware 1] → Réponse HTTP
```

#### CORS (Cross-Origin Resource Sharing)

CORS est un mécanisme de sécurité des navigateurs qui contrôle les requêtes cross-origin. Par défaut, les navigateurs bloquent les requêtes AJAX vers un domaine différent de celui qui a servi la page.

##### Pourquoi CORS est Nécessaire dans MagikSwipe ?

MagikSwipe utilise une architecture web moderne où le **Viewer** (interface HTML/CSS/JS) s'exécute dans le navigateur et communique avec le **Backend FastAPI** via des requêtes HTTP. Même si les deux composants sont servis depuis le même domaine en développement, CORS est nécessaire pour :

- Les appels API AJAX depuis JavaScript
- La gestion des credentials et cookies
- La compatibilité avec différents environnements de déploiement
- Les futures évolutions (PWA, API séparée, etc.)

Sans CORS, le navigateur bloque les appels API depuis le Viewer.

##### Erreur CORS Typique

```
Access to XMLHttpRequest at 'http://localhost:8000/api/universes' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

#### Configuration CORS dans MagikSwipe

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

##### Options de Configuration Détaillées

| Option | Description | Valeur MagikSwipe | Recommandation Production |
|--------|-------------|-------------------|---------------------------|
| `allow_origins` | Domaines autorisés | `["*"]` (tous) | `["https://magikswipe.com", "https://app.magikswipe.com"]` |
| `allow_credentials` | Autoriser cookies/auth | `True` | `True` pour auth, `False` sinon |
| `allow_methods` | Méthodes HTTP autorisées | `["*"]` (toutes) | `["GET", "POST", "PUT", "DELETE", "PATCH"]` |
| `allow_headers` | Headers autorisés | `["*"]` (tous) | `["Content-Type", "Authorization", "X-API-Key"]` |

##### Configuration par Environnement

```python
# backend/config.py
class Settings(BaseSettings):
    # Configuration CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # En production
    if not DEBUG:
        CORS_ORIGINS = ["https://magikswipe.com"]

# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
```

#### Middleware Personnalisé

FastAPI permet de créer des middlewares personnalisés pour ajouter des fonctionnalités spécifiques à MagikSwipe.

##### Syntaxe de Base

```python
@app.middleware("http")
async def nom_middleware(request: Request, call_next):
    # Code avant traitement de la requête
    # Peut modifier request

    response = await call_next(request)  # Passe au middleware suivant

    # Code après traitement de la réponse
    # Peut modifier response

    return response
```

##### Exemple : Middleware de Métriques de Performance

```python
from fastapi import Request, Response
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Middleware pour mesurer et logger les performances."""
    start_time = time.time()

    # Log de la requête entrante
    logger.info(f"→ {request.method} {request.url.path}")

    try:
        # Traitement de la requête
        response = await call_next(request)

        # Calcul du temps de traitement
        process_time = time.time() - start_time

        # Ajout d'headers de métriques
        response.headers["X-Process-Time"] = ".2f"
        response.headers["X-API-Version"] = "2.0.0"

        # Log de la réponse
        logger.info(f"← {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")

        return response

    except Exception as e:
        # Log des erreurs
        process_time = time.time() - start_time
        logger.error(f"✗ {request.method} {request.url.path} - ERROR - {process_time:.2f}s - {str(e)}")
        raise
```

##### Exemple : Middleware de Sécurité

```python
from fastapi import HTTPException
import re

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Middleware de sécurité basique."""

    # Protection contre les attaques par injection de path
    if ".." in request.url.path or "//" in request.url.path:
        raise HTTPException(status_code=400, detail="Invalid path")

    # Vérification des headers malicieux
    user_agent = request.headers.get("user-agent", "")
    if re.search(r"(sqlmap|nikto|dirbuster)", user_agent, re.IGNORECASE):
        logger.warning(f"Suspicious User-Agent blocked: {user_agent}")
        raise HTTPException(status_code=403, detail="Access denied")

    # Rate limiting simple (par IP)
    client_ip = request.client.host
    # Logique de rate limiting...

    response = await call_next(request)

    # Ajout de headers de sécurité
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response
```

##### Exemple : Middleware de Logging Structuré

```python
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware pour logging structuré des requêtes."""

    # Collecte des informations de contexte
    request_id = str(uuid.uuid4())[:8]
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    # Ajout d'un ID de requête pour tracer
    request.state.request_id = request_id

    # Log structuré
    logger.info("request_started", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "query": str(request.url.query),
        "client_ip": client_ip,
        "user_agent": user_agent[:100]  # Tronquer si trop long
    })

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Log de la réponse
    logger.info("request_completed", extra={
        "request_id": request_id,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "response_size": len(response.body) if hasattr(response, 'body') else 0
    })

    # Ajout de l'ID de requête dans la réponse
    response.headers["X-Request-ID"] = request_id

    return response
```

#### Ordre d'Exécution des Middlewares

L'ordre d'ajout des middlewares est important :

```python
# backend/main.py
app.add_middleware(CORSMiddleware, ...)      # 1. CORS (toujours en premier)
app.add_middleware(TrustedHostMiddleware, ...)  # 2. Sécurité
app.add_middleware(performance_middleware)   # 3. Métriques (custom)
app.add_middleware(logging_middleware)       # 4. Logging (custom)
```

#### Bonnes Pratiques

- **CORS** : Restreindre `allow_origins` en production
- **Performance** : Éviter les opérations coûteuses dans les middlewares
- **Logging** : Utiliser un format structuré (JSON) pour l'analyse
- **Sécurité** : Valider les entrées et ajouter des headers de protection
- **Test** : Tester les middlewares isolément avec des mocks
- **Monitoring** : Surveiller les métriques ajoutées par les middlewares

Les middlewares rendent MagikSwipe plus sûr, observable et performant tout en gardant le code des routes propre et focalisé sur la logique métier.

### 2.7 Documentation Automatique

FastAPI génère automatiquement la documentation OpenAPI.

#### Accès à la Documentation
- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`
- **OpenAPI JSON** : `http://localhost:8000/openapi.json`

#### Métadonnées dans MagikSwipe

```python
# backend/main.py
app = FastAPI(
    title="MagikSwipe Backend",
    description="""
    Backend API for MagikSwipe - AI-powered children's learning app.
    
    Features:
    - Universe management
    - AI content generation
    - Multi-language support
    - Cloud synchronization
    """,
    version="2.0.0",
    contact={
        "name": "MagikSwipe Team",
        "url": "https://github.com/magikswipe",
    }
)
```

---

## Chapitre 3 : SQLAlchemy - ORM Python

### 3.1 Introduction aux ORM

Un ORM (Object-Relational Mapping) fait le lien entre le monde objet et les bases de données relationnelles.

#### Avantages des ORM
- **Productivité** : Moins de code SQL
- **Sécurité** : Prévention des injections SQL
- **Maintenance** : Code plus lisible et maintenable
- **Portabilité** : Changement de SGBD plus facile

#### SQLAlchemy vs Autres ORM
- **Django ORM** : Couplé à Django, moins flexible
- **SQLAlchemy** : Indépendant, très flexible, "l'ORM des ORM"
- **Peewee** : Plus simple, moins de fonctionnalités

### 3.2 Configuration de SQLAlchemy

SQLAlchemy nécessite une configuration précise pour fonctionner correctement.

#### Configuration dans MagikSwipe

```python
# backend/database/connection.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de connexion SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.DB_PATH}"

# Configuration du moteur
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Requis pour SQLite
    echo=settings.DEBUG  # Log des requêtes SQL en debug
)

# Activation des clés étrangères SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
`````

##### Pourquoi cette Configuration est Nécessaire

**Qu'est-ce qu'une Clé Étrangère ?**
Une clé étrangère (foreign key) est une contrainte d'intégrité référentielle qui lie deux tables. Elle garantit que :

- Une valeur dans une colonne d'une table doit exister dans une colonne d'une autre table
- Elle empêche les "orphelins" : pas de références vers des enregistrements inexistants
- Elle maintient la cohérence des données

**Exemple dans MagikSwipe :**
```sql
-- Table univers_assets
CREATE TABLE univers_assets (
    id TEXT PRIMARY KEY,
    univers_id INTEGER NOT NULL,  -- Clé étrangère
    display_name TEXT NOT NULL,

    FOREIGN KEY (univers_id) REFERENCES univers (id) ON DELETE CASCADE
);
```
Ici, `univers_id` doit toujours référencer un `id` existant dans la table `univers`.

**Pourquoi SQLite Désactive les Clés Étrangères par Défaut ?**
- **Performance** : La vérification des contraintes coûte cher en CPU
- **Compatibilité** : Certains anciens outils ne supportent pas les FK
- **Historique** : SQLite a été conçu pour être simple et rapide

**Conséquences sans `PRAGMA foreign_keys=ON` :**
- ❌ Insertion d'assets avec `univers_id` inexistant possible
- ❌ Suppression d'univers laisse des assets orphelins
- ❌ Corruption silencieuse de l'intégrité des données
- ❌ Bugs difficiles à déboguer

**Que fait `PRAGMA foreign_keys=ON` ?**
- Active la vérification des contraintes de clés étrangères
- Génère des erreurs si l'intégrité est violée
- Assure la cohérence des données MagikSwipe
- Doit être activé à chaque connexion (d'où l'event listener)

**Configuration par Connexion :**
Le décorateur `@event.listens_for(engine, "connect")` garantit que chaque nouvelle connexion SQLite active automatiquement les clés étrangères. Sans cela, chaque connexion devrait le faire manuellement.

# Fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

##### Comprendre la Fabrique de Sessions

**Qu'est-ce qu'un SessionMaker ?**
Un `sessionmaker` est une **fabrique** (factory) qui crée des objets `Session` SQLAlchemy. Au lieu de créer manuellement des sessions partout dans le code, on utilise cette fabrique pour obtenir des sessions configurées de manière cohérente.

**Analogie :**
```python
# Comme une fabrique de voitures
CarFactory = carmaker(model="Tesla", color="red", autopilot=True)

# Chaque appel crée une nouvelle voiture configurée
car1 = CarFactory()
car2 = CarFactory()
```

**Pourquoi une Fabrique ?**
- **Configuration centralisée** : Tous les paramètres de session au même endroit
- **Cohérence** : Toutes les sessions ont le même comportement
- **Maintenance** : Changement facile de la configuration globale

##### Paramètres Détaillés

**`bind=engine`**
- **Rôle** : Lie la session à notre moteur de base de données
- **Pourquoi nécessaire** : La session doit savoir quelle DB utiliser
- **Conséquence** : Toutes les requêtes passent par notre SQLite configuré

**`autocommit=False`** (CRUCIAL pour FastAPI)
- **Comportement** : Les changements ne sont PAS automatiquement sauvegardés
- **Contrôle manuel** : On décide quand faire `db.commit()`
- **Pourquoi important** :
  - Évite les commits accidentels
  - Permet les rollbacks en cas d'erreur
  - Contrôle transactionnel précis
  - Essentiel pour la gestion d'erreurs FastAPI

**`autoflush=False`**
- **Comportement** : SQLAlchemy ne fait PAS de requêtes automatiques pour synchroniser les objets
- **Avantages** :
  - Performance : Moins de requêtes inutiles
  - Contrôle : On déclenche les flushs manuellement si besoin
  - Debugging : Plus facile de comprendre quand les requêtes sont exécutées

##### Configuration Alternative pour Développement

```python
# En développement (avec logging)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    # Log toutes les requêtes SQL
    echo=True
)

# En production
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    # Pool de connexions optimisé
    pool_pre_ping=True,
    pool_recycle=300
)
```

##### Comment l'Utiliser

```python
# Créer une session
db = SessionLocal()

try:
    # Utiliser la session
    user = db.query(User).first()

    # Commit explicite requis
    db.commit()

except Exception as e:
    # Rollback en cas d'erreur
    db.rollback()
    raise

finally:
    # Toujours fermer
    db.close()
```

##### Pourquoi ces Valeurs pour FastAPI ?

- **`autocommit=False`** : FastAPI gère les transactions explicitement
- **`autoflush=False`** : Évite les requêtes surprises pendant la validation Pydantic
- **`bind=engine`** : Utilise notre configuration SQLite optimisée

Cette configuration garantit un comportement prévisible et performant dans un environnement web avec gestion d'erreurs appropriée.

# Classe de base pour les modèles
Base = declarative_base()


#### Fonction de Dépendance

```python
def get_db():
    """Fournit une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3.3 Modèles de Données

Les modèles SQLAlchemy définissent la structure des tables et leurs relations.

#### Exemple de Modèle dans MagikSwipe

```python
# backend/database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .connection import Base

class Univers(Base):
    """Modèle représentant un univers thématique."""
    __tablename__ = "univers"
    
    # Colonnes
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
    thumbnail_url = Column(String)
    is_public = Column(Boolean, default=True)
    owner_id = Column(String(36))  # UUID utilisateur
    background_music = Column(String)
    background_color = Column(String)

    # Relations
    assets = relationship("UniversAsset", back_populates="univers")
    translations = relationship("UniversTranslation", back_populates="univers")
    prompts = relationship("UniversPrompts", back_populates="univers")
    music_prompts = relationship("UniversMusicPrompts", back_populates="univers")
```

#### Types de Colonnes SQLAlchemy

| Type Python | Type SQLAlchemy | Usage |
|-------------|-----------------|-------|
| `str` | `String` | Texte court |
| `int` | `Integer` | Nombres entiers |
| `bool` | `Boolean` | Vrai/Faux |
| `datetime` | `DateTime` | Dates et heures |
| `float` | `Float` | Nombres décimaux |

### 3.4 Sessions et Transactions

Les sessions gèrent le cycle de vie des objets et les transactions.

#### Utilisation des Sessions

```python
# Création d'une session
db = SessionLocal()

try:
    # Création d'un univers
    univers = Univers(name="Animaux", slug="animaux")
    db.add(univers)
    
    # Flush pour obtenir l'ID généré
    db.flush()
    
    # Création d'un asset lié
    asset = UniversAsset(
        univers_id=univers.id,
        display_name="Lion",
        image_name="lion.png"
    )
    db.add(asset)
    
    # Commit de la transaction
    db.commit()
    
except Exception as e:
    # Rollback en cas d'erreur
    db.rollback()
    raise
finally:
    db.close()
```

#### Gestion Automatique avec FastAPI

```python
@app.post("/universes")
def create_universe(data: UniversCreate, db: Session = Depends(get_db)):
    # db est géré automatiquement par Depends()
    univers = Univers(**data.dict())  # Conversion Pydantic → SQLAlchemy
    db.add(univers)
    db.commit()
    db.refresh(univers)
    return univers
```

##### Conversion Automatique Pydantic → SQLAlchemy

La ligne `univers = Univers(**data.dict())` effectue une **conversion automatique** entre les modèles :

**1. Validation Pydantic** (côté API)
```python
data = UniversCreate(name="Test", is_public=True)  # Données validées
```

**2. Conversion en Dictionnaire**
```python
data_dict = data.dict()  # {'name': 'Test', 'is_public': True}
```

**3. Création SQLAlchemy** (côté Base de Données)
```python
univers = Univers(**data_dict)  # Univers(name='Test', is_public=True)
```

**Avantages :**
- ✅ **Sécurité** : Données validées avant insertion
- ✅ **Simplicité** : Pas de mapping manuel
- ✅ **Maintenance** : Un seul schéma pour API et DB

### 3.5 Requêtes et Filtres

SQLAlchemy fournit une API fluide pour construire des requêtes.

#### Requêtes de Base

```python
# Sélection simple
universes = db.query(Univers).all()

# Filtrage
public_universes = db.query(Univers).filter(Univers.is_public == True).all()

# Tri
recent_universes = db.query(Univers).order_by(Univers.created_at.desc()).all()

# Pagination
paginated = db.query(Univers)\
    .order_by(Univers.created_at.desc())\
    .offset(skip)\
    .limit(limit)\
    .all()
```

#### Jointures et Relations

```python
# Chargement des relations
univers = db.query(Univers)\
    .options(joinedload(Univers.assets))\
    .filter(Univers.slug == "animaux")\
    .first()

# Accès aux données liées
for asset in univers.assets:
    print(f"Asset: {asset.display_name}")
```

#### Requêtes Avancées

```python
# Comptage
total = db.query(Univers).count()

# Agrégations
from sqlalchemy import func
stats = db.query(
    func.count(Univers.id).label('total_universes'),
    func.avg(func.length(Univers.name)).label('avg_name_length')
).first()

# Sous-requêtes
subquery = db.query(UniversAsset.univers_id)\
    .group_by(UniversAsset.univers_id)\
    .having(func.count(UniversAsset.id) > 5)\
    .subquery()

univers_with_many_assets = db.query(Univers)\
    .filter(Univers.id.in_(subquery))\
    .all()
```

### 3.6 Relations Entre Tables

SQLAlchemy gère automatiquement les relations entre tables.

#### Rappel Théorique : Types de Relations

Les relations entre tables définissent comment les données sont liées. Voici les types principaux :

##### **One-to-One (Un-à-Un)**
- **Définition** : Un enregistrement d'une table correspond exactement à un enregistrement d'une autre table
- **Exemple** : Un utilisateur a exactement un profil détaillé
- **Implémentation** : Clé étrangère unique des deux côtés

##### **One-to-Many (Un-à-Plusieurs)**
- **Définition** : Un enregistrement d'une table peut correspondre à plusieurs enregistrements d'une autre table
- **Exemple** : Un univers peut avoir plusieurs assets (images, vidéos)
- **Implémentation** : Clé étrangère côté "plusieurs"

##### **Many-to-One (Plusieurs-à-Un)**
- **Définition** : L'inverse d'une relation One-to-Many
- **Exemple** : Plusieurs assets appartiennent à un seul univers
- **Implémentation** : Clé étrangère pointant vers la table "un"

##### **Many-to-Many (Plusieurs-à-Plusieurs)**
- **Définition** : Plusieurs enregistrements d'une table peuvent correspondre à plusieurs enregistrements d'une autre
- **Exemple** : Un étudiant suit plusieurs cours, chaque cours a plusieurs étudiants
- **Implémentation** : Table d'association (junction table) avec deux clés étrangères

##### **Exemples dans MagikSwipe**
- **Univers → Assets** : One-to-Many (un univers, plusieurs assets)
- **Assets → Univers** : Many-to-One (plusieurs assets, un univers)
- **Univers → Translations** : One-to-Many (un univers, plusieurs langues)

#### Types de Relations (Implémentation)

```python
class Univers(Base):
    # One-to-Many avec assets
    assets = relationship("UniversAsset", back_populates="univers")
    
    # One-to-Many avec translations  
    translations = relationship("UniversTranslation", back_populates="univers")

class UniversAsset(Base):
    # Many-to-One avec univers
    univers_id = Column(Integer, ForeignKey("univers.id"))
    univers = relationship("Univers", back_populates="assets")
    
    # One-to-Many avec prompts
    prompts = relationship("UniversAssetPrompts", back_populates="asset")
```

##### Comprendre `back_populates`

Le paramètre `back_populates` crée des **relations bidirectionnelles** entre les modèles :

```python
class Univers(Base):
    # One-to-Many : un univers → plusieurs assets
    assets = relationship("UniversAsset", back_populates="univers")

class UniversAsset(Base):
    # Many-to-One : plusieurs assets → un univers
    univers_id = Column(Integer, ForeignKey("univers.id"))
    univers = relationship("Univers", back_populates="assets")
```

**Comment ça marche :**
1. `Univers.assets` fait référence à `UniversAsset.univers`
2. `UniversAsset.univers` fait référence à `Univers.assets`
3. SQLAlchemy crée automatiquement les liens dans les deux sens

**Sans `back_populates` :**
```python
# ❌ Relations unidirectionnelles seulement
univers = db.query(Univers).first()
assets = univers.assets  # ✅ Marche

asset = db.query(UniversAsset).first()
parent_univers = asset.univers  # ❌ ERREUR : pas défini
```

**Avec `back_populates` :**
```python
# ✅ Relations bidirectionnelles
univers = db.query(Univers).first()
assets = univers.assets  # ✅ Marche

asset = db.query(UniversAsset).first()
parent_univers = asset.univers  # ✅ Marche aussi !
```

**Règles importantes :**
- Les noms dans `back_populates` doivent correspondre exactement
- Utiliser le nom de l'attribut, pas le nom de la classe
- Nécessaire pour les relations bidirectionnelles

**Alternative : `backref`**
```python
# backref crée automatiquement l'attribut inverse
class Univers(Base):
    assets = relationship("UniversAsset", backref="univers")

# Équivalent automatique à :
# UniversAsset.univers = relationship("Univers", ...)
```

#### Chargement des Relations

```python
# Chargement eager (immédiat)
univers = db.query(Univers)\
    .options(joinedload(Univers.assets))\
    .filter(Univers.slug == "animaux")\
    .first()

# Chargement lazy (à la demande)
assets = univers.assets  # Requête SQL exécutée ici

# Chargement select (optimisé)
univers = db.query(Univers)\
    .options(selectinload(Univers.assets))\
    .filter(Univers.slug == "animaux")\
    .first()
```

### 3.7 Migrations et Évolution

SQLAlchemy gère l'évolution du schéma de base de données.

#### Création Automatique des Tables

```python
# backend/database/connection.py
def init_db():
    """Initialise les tables de la base de données."""
    from . import models  # Importe tous les modèles
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de données initialisée: {settings.DB_PATH}")
```

#### Gestion des Changements

Pour les changements de schéma en production, on utilise Alembic :

```bash
# Installation
pip install alembic

# Initialisation
alembic init alembic

# Création d'une migration
alembic revision --autogenerate -m "Ajout colonne description"

# Application de la migration
alembic upgrade head
```

---

## Chapitre 4 : Tâches Asynchrones et Jobs

### Concepts Fondamentaux : Jobs, Tasks et Threads

Avant d'explorer l'implémentation, clarifions les concepts clés utilisés dans ce chapitre :

#### **Task (Tâche)**
Une **tâche** est une **unité de travail** à exécuter. Elle peut être :
- Synchrone : bloque l'exécution jusqu'à completion
- Asynchrone : s'exécute en parallèle sans bloquer

**Exemples dans MagikSwipe :**
- Générer une image via Replicate (longue, I/O-bound)
- Calculer des statistiques (CPU-bound)
- Sauvegarder des fichiers (I/O-bound)

#### **Thread (Fil d'Exécution)**
Un **thread** est un **fil d'exécution léger** dans un processus. Plusieurs threads partagent la mémoire du processus.

**Caractéristiques :**
- **Partage de mémoire** : variables globales accessibles
- **Contexte-switching** : système d'exploitation alterne entre threads
- **GIL en Python** : limite la parallélisation CPU (mais pas pour I/O)

#### **Process (Processus)**
Un **processus** est un **programme en exécution** avec sa propre mémoire. Les processus ne partagent pas la mémoire.

**Avantages :**
- Isolation complète (crash d'un process n'affecte pas les autres)
- Vrai parallélisme CPU (contourne le GIL Python)
**Inconvénients :**
- Plus lourd (création, communication inter-processus)

#### **Job (Travail Planifié)**
Un **job** est une **tâche asynchrone persistante** avec métadonnées :
- **Suivi d'état** : pending, running, completed, failed
- **Progression** : pourcentage d'avancement
- **Persistance** : stocké en base de données
- **Monitoring** : consultable via API

**Pourquoi des Jobs dans MagikSwipe ?**
- Génération IA prend du temps (minutes)
- Interface utilisateur reste réactive
- Suivi de progression en temps réel
- Gestion d'erreurs et retry automatique

#### **Synchrone vs Asynchrone**

**Synchrone (bloquant) :**
```python
# ❌ L'utilisateur attend 30 secondes
@app.post("/generate")
def generate_image():
    time.sleep(30)  # Bloque le thread serveur
    return {"status": "done"}
```

**Asynchrone (non-bloquant) :**
```python
# ✅ Réponse immédiate, travail en arrière-plan
@app.post("/generate")
def generate_image():
    job = job_service.run_async(generate_task)
    return {"job_id": job.id, "status": "started"}
```



### 4.1 Programmation Asynchrone en Python

Python supporte plusieurs approches pour l'asynchrone : threading, multiprocessing, et asyncio.

#### Threading dans MagikSwipe

MagikSwipe utilise le threading pour les tâches longues (génération IA).

```python
import threading
import time

def long_running_task(job_id, data):
    """Tâche exécutée dans un thread séparé."""
    # Simulation d'une tâche longue
    time.sleep(30)  # 30 secondes
    
    # Mise à jour du statut du job
    update_job_status(job_id, "completed")

# Lancement dans un thread
thread = threading.Thread(target=long_running_task, args=(job_id, data))
thread.start()
```

#### Avantages du Threading
- **Non-bloquant** : Le serveur reste réactif
- **Simple** : API familière
- **Ressources** : Partage de la mémoire entre threads

### 4.2 Architecture des Jobs

MagikSwipe utilise un système de jobs persistants pour suivre les tâches asynchrones.

#### Modèle Job

```python
# backend/database/models.py
class Job(Base):
    """Modèle pour les tâches asynchrones."""
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)  # "generate_images", "sync_pull", etc.
    univers_slug = Column(String)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    current_step = Column(Integer, default=0)
    message = Column(Text)
    error = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
```

#### Service Job

```python
# backend/services/job_service.py
class JobService:
    """Gestionnaire des tâches asynchrones."""
    
    def run_async(self, db, job_type, task_func, univers_slug=None, total_steps=0):
        """Lance une tâche asynchrone et retourne le job."""
        
        # Création du job en base
        job = self.create_job(db, job_type, univers_slug, total_steps)
        
        # Définition de la fonction wrapper
        def run_task():
            try:
                # Mise à jour statut
                self.update_job(job.id, status=JobStatus.RUNNING)
                
                # Exécution de la tâche
                result = task_func(job.id)
                
                # Succès
                self.update_job(
                    job.id, 
                    status=JobStatus.COMPLETED,
                    progress=100,
                    result=str(result)
                )
                
            except Exception as e:
                # Échec
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                self.update_job(
                    job.id,
                    status=JobStatus.FAILED,
                    error=error_msg
                )
        
        # Lancement dans un thread
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        
        return job
```

### 4.3 Gestion du Cycle de Vie

Les jobs traversent différents états avec des transitions contrôlées.

#### États des Jobs

```python
class JobStatus(str, Enum):
    PENDING = "pending"      # En attente
    RUNNING = "running"      # En cours d'exécution
    COMPLETED = "completed"  # Terminé avec succès
    FAILED = "failed"        # Échec
```

#### Transitions d'État

```
PENDING ────▶ RUNNING ────▶ COMPLETED
    │              │
    │              └────────▶ FAILED
    │
    └────────────────────────▶ FAILED (timeout)
```

#### Mise à Jour du Progrès

```python
def update_job_progress(job_id, current_step, total_steps, message=""):
    """Met à jour la progression d'un job."""
    progress = int((current_step / total_steps) * 100) if total_steps > 0 else 0
    
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.current_step = current_step
            job.progress = progress
            job.message = message
            db.commit()
    finally:
        db.close()
```

### 4.4 Monitoring et Logging

Le système de jobs fournit un monitoring complet des tâches.

#### API de Monitoring

```python
# backend/routes/jobs.py
@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Récupère le statut d'un job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse.from_orm(job)

@router.get("", response_model=List[JobResponse])
def list_jobs(
    univers_slug: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Liste les jobs avec filtres."""
    query = db.query(Job)
    
    if univers_slug:
        query = query.filter(Job.univers_slug == univers_slug)
    
    if status:
        query = query.filter(Job.status == status)
    
    jobs = query.order_by(Job.created_at.desc()).all()
    return [JobResponse.from_orm(job) for job in jobs]
```

#### Logging des Tâches

```python
# Dans le service de génération
def generate_images(slug, concepts, prompts, job_id, theme_context):
    """Génération d'images avec logging."""
    
    total = len(concepts)
    for i, (concept, prompt) in enumerate(zip(concepts, prompts)):
        try:
            print(f"🎨 Génération image {i+1}/{total}: {concept}")
            
            # Génération via Replicate
            image_data = replicate.run(MODELS["image"], input={
                "prompt": prompt,
                "size": "1024x1024"
            })
            
            # Sauvegarde du fichier
            storage_service.save_image(slug, f"{i:02d}_{concept}.png", image_data)
            
            # Mise à jour progression
            update_job_progress(job_id, i+1, total, f"Généré: {concept}")
            
        except Exception as e:
            print(f"❌ Erreur génération {concept}: {e}")
            update_job_progress(job_id, i+1, total, f"Échec: {concept}")
            raise
    
    print(f"✅ Génération terminée pour {slug}")
    return {"images_generated": total}
```

### 4.5 Gestion d'Erreurs

Les erreurs dans les tâches asynchrones doivent être gérées soigneusement.

#### Gestion d'Erreurs Robuste

```python
def run_task():
    try:
        # Héritage des variables d'environnement
        import os
        from config import settings
        
        # Variables critiques pour les jobs IA
        if hasattr(settings, 'REPLICATE_API_TOKEN'):
            os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
            
        self.update_job(job.id, status=JobStatus.RUNNING)
        
        result = task_func(job.id, **kwargs)
        
        self.update_job(job.id, status=JobStatus.COMPLETED, result=str(result))
        
    except Exception as e:
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ Job {job.id} échoué: {error_details}")
        
        self.update_job(
            job.id,
            status=JobStatus.FAILED,
            error=error_details
        )
```

#### Retry Logic

```python
def execute_with_retry(func, max_retries=3, delay=1):
    """Exécute une fonction avec retry automatique."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Tentative {attempt + 1} échouée, retry dans {delay}s")
            time.sleep(delay)
            delay *= 2  # Backoff exponentiel
```

### 4.6 Performance et Scalabilité

Considérations pour les tâches longues et nombreuses.

#### Limitation de la Concurrence

```python
class JobService:
    def __init__(self):
        self._semaphore = threading.Semaphore(3)  # Max 3 jobs simultanés
        
    def run_async(self, db, job_type, task_func, **kwargs):
        def run_with_limit():
            with self._semaphore:
                return self._run_task(task_func, **kwargs)
        
        thread = threading.Thread(target=run_with_limit)
        thread.start()
```

#### Optimisation Mémoire

```python
# Nettoyage périodique des jobs anciens
def cleanup_old_jobs():
    """Supprime les jobs terminés de plus de 7 jours."""
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    db = SessionLocal()
    try:
        deleted = db.query(Job)\
            .filter(Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED]))\
            .filter(Job.completed_at < cutoff_date)\
            .delete()
        
        db.commit()
        print(f"Nettoyé {deleted} jobs anciens")
    finally:
        db.close()
```

---

## Chapitre 5 : Architecture du Projet

### 5.1 Structure des Dossiers

```
backend/
├── config.py              # Configuration centralisée
├── main.py                # Point d'entrée FastAPI
├── requirements.txt       # Dépendances Python
├── pytest.ini            # Configuration tests
├── run_tests.py          # Script d'exécution tests
├── seed_supabase_test_data.py  # Script seeding
│
├── database/             # Couche base de données
│   ├── __init__.py
│   ├── connection.py     # Configuration SQLAlchemy
│   └── models.py         # Modèles de données
│
├── routes/               # Endpoints API
│   ├── __init__.py
│   ├── universes.py      # CRUD univers + assets
│   ├── generation.py     # Génération IA
│   ├── sync.py           # Synchronisation Supabase
│   └── jobs.py           # Monitoring jobs
│
├── schemas/              # Schémas Pydantic
│   ├── __init__.py       # Tous les schémas
│
├── services/             # Logique métier
│   ├── __init__.py
│   ├── generation_service.py    # IA & génération
│   ├── job_service.py           # Gestion jobs async
│   ├── storage_service.py       # Fichiers locaux
│   └── supabase_service.py      # Cloud sync
│
└── tests/                # Tests unitaires/intégration
    ├── conftest.py       # Configuration tests
    ├── test_*.py         # Tests par module
    └── test_replicate_integration.py  # Tests IA
```

### 5.2 Services et Responsabilités

#### Service de Génération (`generation_service.py`)

**Responsabilités :**
- Intégration avec APIs IA (Replicate)
- Génération de contenu (images, vidéos, musique, concepts)
- Traduction multilingue
- Validation des prompts

**Interface :**
```python
class GenerationService:
    def generate_concepts(self, theme, count, language) -> List[str]
    def generate_image(self, prompt, size) -> bytes
    def generate_music(self, slug, language, style) -> str
    def translate_text(self, text, source, target) -> str
```

#### Service de Jobs (`job_service.py`)

**Responsabilités :**
- Gestion du cycle de vie des tâches asynchrones
- Persistance des jobs en base
- Monitoring et progression
- Gestion d'erreurs et logging

#### Service de Stockage (`storage_service.py`)

**Responsabilités :**
- Gestion des fichiers locaux
- Organisation par univers
- URLs de fichiers
- Synchronisation fichiers

#### Service Supabase (`supabase_service.py`)

**Responsabilités :**
- Synchronisation données cloud
- Authentification utilisateurs
- Stockage fichiers distant
- Backup et restauration

### 5.3 Configuration Centralisée

```python
# config.py
class Settings(BaseSettings):
    # Chemins de stockage
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", "/tmp/storage"))
    DB_PATH: Path = STORAGE_PATH / "db" / "local.db"
    BUCKETS_PATH: Path = STORAGE_PATH / "buckets"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # IA
    REPLICATE_API_TOKEN: str = ""
    
    # Application
    DEBUG: bool = True
```

### 5.4 Gestion des Erreurs

#### Gestion Globale d'Erreurs

```python
# main.py
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Gestion des erreurs de validation Pydantic."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Données de requête invalides",
            "errors": exc.errors()
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Gestion des erreurs HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

#### Logging Structuré

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 5.5 Sécurité et Authentification

#### Middleware de Sécurité

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.magikswipe.com"]
)
```

#### Gestion des Secrets

```python
# Variables d'environnement uniquement
# Jamais de secrets en dur dans le code
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not REPLICATE_API_TOKEN:
    logger.warning("REPLICATE_API_TOKEN non configuré - génération IA désactivée")
```

---

## Chapitre 6 : Exemples Pratiques du Code

### 6.1 Création d'un Univers

```python
# backend/routes/universes.py
@router.post("", response_model=UniversResponse, status_code=201)
def create_universe(
    data: UniversCreate,
    db: Session = Depends(get_db)
):
    """Créer un nouvel univers."""
    
    # Générer un slug unique
    slug = data.slug or slugify(data.name)
    
    # Vérifier l'unicité
    existing = db.query(Univers).filter(Univers.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Univers avec slug '{slug}' existe déjà"
        )
    
    # Créer l'univers
    univers = Univers(
        name=data.name,
        slug=slug,
        background_color=data.background_color,
        is_public=data.is_public
    )
    db.add(univers)
    db.flush()  # Obtenir l'ID généré
    
    # Créer les prompts par défaut
    if data.default_image_prompt or data.default_video_prompt:
        prompts = UniversPrompts(
            univers_id=univers.id,
            default_image_prompt=data.default_image_prompt,
            default_video_prompt=data.default_video_prompt
        )
        db.add(prompts)
    
    # Créer les traductions
    if data.translations:
        for lang, name in data.translations.items():
            trans = UniversTranslation(
                univers_id=univers.id,
                language=lang,
                name=name
            )
            db.add(trans)
    
    # Créer le dossier de stockage
    storage_service.create_universe_folder(slug)
    
    db.commit()
    db.refresh(univers)
    
    return _build_univers_response(univers)
```

### 6.2 Génération de Contenu IA

```python
# backend/routes/generation.py
@router.post("/{slug}/images", response_model=JobResponse)
def generate_images(
    slug: str,
    data: GenerateImagesRequest = GenerateImagesRequest(),
    db: Session = Depends(get_db)
):
    """Générer des images pour les assets (job asynchrone)."""
    
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    if not univers:
        raise HTTPException(status_code=404, detail=f"Univers '{slug}' introuvable")
    
    if not generation_service.is_available:
        raise HTTPException(status_code=503, detail="Génération IA non disponible")
    
    # Récupérer les assets à générer
    if data.asset_ids:
        assets = db.query(UniversAsset)\
            .filter(UniversAsset.univers_id == univers.id)\
            .filter(UniversAsset.id.in_(data.asset_ids))\
            .order_by(UniversAsset.sort_order)\
            .all()
    else:
        assets = univers.assets
    
    if not assets:
        raise HTTPException(status_code=400, detail="Aucun asset à générer")
    
    # Préparer les données pour le job
    concepts = [a.display_name for a in assets]
    prompts = []
    for a in assets:
        # Utiliser le prompt personnalisé ou celui par défaut
        if a.prompts and a.prompts.custom_image_prompt:
            prompts.append(a.prompts.custom_image_prompt)
        elif univers.prompts and univers.prompts.default_image_prompt:
            prompts.append(
                univers.prompts.default_image_prompt.replace("{concept}", a.display_name)
            )
        else:
            prompts.append(None)
    
    # Créer et lancer le job
    def task(job_id):
        return generation_service.generate_all_images(
            slug=slug,
            concepts=concepts,
            prompts=prompts,
            job_id=job_id,
            theme_context=univers.name
        )
    
    job = job_service.run_async(
        db=db,
        job_type="generate_images",
        task_func=task,
        univers_slug=slug,
        total_steps=len(assets)
    )
    
    return JobResponse(
        id=job.id,
        type=job.type,
        univers_slug=job.univers_slug,
        status=job.status,
        progress=job.progress,
        total_steps=job.total_steps,
        current_step=job.current_step,
        message=job.message,
        created_at=job.created_at
    )
```

### 6.3 Gestion des Jobs Asynchrones

```python
# backend/services/job_service.py
def run_async(
    self,
    db: Session,
    job_type: str,
    task_func: Callable,
    univers_slug: Optional[str] = None,
    total_steps: int = 0
) -> Job:
    """
    Lance une tâche asynchrone et retourne le job créé.
    
    Args:
        db: Session de base de données
        job_type: Type de job ("generate_images", "sync_pull", etc.)
        task_func: Fonction à exécuter (reçoit job_id comme paramètre)
        univers_slug: Slug de l'univers concerné (optionnel)
        total_steps: Nombre total d'étapes pour le suivi de progression
    
    Returns:
        Objet Job créé
    """
    # Créer le job en base
    job = self.create_job(db, job_type, univers_slug, total_steps)
    
    def run_task():
        """Wrapper pour l'exécution de la tâche avec gestion d'erreurs."""
        try:
            # Hériter les variables d'environnement critiques
            import os
            from config import settings
            
            # Token Replicate pour les jobs IA
            if hasattr(settings, 'REPLICATE_API_TOKEN') and settings.REPLICATE_API_TOKEN:
                os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
            
            # Clés Supabase pour les jobs de sync
            if hasattr(settings, 'SUPABASE_URL'):
                os.environ["SUPABASE_URL"] = settings.SUPABASE_URL
            if hasattr(settings, 'SUPABASE_SERVICE_ROLE_KEY'):
                os.environ["SUPABASE_SERVICE_ROLE_KEY"] = settings.SUPABASE_SERVICE_ROLE_KEY
            
            # Marquer le job comme en cours
            self.update_job(job.id, status=JobStatus.RUNNING, message="Démarrage...")
            
            # Exécuter la tâche métier
            result = task_func(job.id)
            
            # Marquer comme terminé
            self.update_job(
                job.id,
                status=JobStatus.COMPLETED,
                progress=100,
                message="Terminé avec succès",
                result=str(result)
            )
            
        except Exception as e:
            # Gérer les erreurs
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"❌ Job {job.id} échoué: {error_msg}")
            
            self.update_job(
                job.id,
                status=JobStatus.FAILED,
                error=error_msg,
                message=f"Échec: {str(e)}"
            )
    
    # Lancer dans un thread séparé
    thread = threading.Thread(target=run_task, daemon=True)
    thread.start()
    
    return job
```

### 6.4 Synchronisation avec Supabase

```python
# backend/routes/sync.py
@router.post("/pull/{slug}", response_model=JobResponse)
def sync_pull_universe(slug: str, data: SyncPullRequest = SyncPullRequest(), db: Session = Depends(get_db)):
    """Synchroniser un univers depuis Supabase (job asynchrone)."""
    
    if not supabase_service.is_connected:
        raise HTTPException(status_code=503, detail="Service Supabase non disponible")
    
    def task(job_id):
        """Tâche de synchronisation pull."""
        try:
            result = sync_service.pull_universe(db, slug, force=data.force)
            
            if not result.success:
                if "not found" in result.message.lower():
                    raise HTTPException(status_code=404, detail=result.message)
                else:
                    raise HTTPException(status_code=500, detail=result.message)
            
            return {
                "status": "success",
                "message": f"Synchronisation pull terminée pour {slug}",
                "files_downloaded": result.files_downloaded,
                "data_updated": result.data_updated
            }
            
        except Exception as e:
            logger.error(f"Erreur sync pull {slug}: {str(e)}")
            raise
    
    # Créer le job
    job = job_service.run_async(
        db=db,
        job_type="sync_pull",
        task_func=task,
        univers_slug=slug,
        total_steps=10  # Estimation des étapes
    )
    
    return JobResponse.from_orm(job)
```

---

## Chapitre 7 : Bonnes Pratiques

### 7.1 Patterns de Développement

#### Séparation des Responsabilités

```python
# ✅ BON : Chaque service a une responsabilité claire
class GenerationService:
    """Gère uniquement la génération IA."""
    pass

class JobService:
    """Gère uniquement les tâches asynchrones."""  
    pass

class StorageService:
    """Gère uniquement le stockage des fichiers."""
    pass
```

#### Injection de Dépendances

```python
# ✅ BON : Dépendances explicites et testables
def create_universe(data: UniversCreate, db: Session = Depends(get_db)):
    # db est injecté automatiquement
    pass

# Pour les tests
def test_create_universe():
    mock_db = MagicMock()
    result = create_universe(test_data, db=mock_db)
    # Testable facilement
```

#### Gestion d'Erreurs Hiérarchique

```python
# ✅ BON : Erreurs spécifiques et informatives
try:
    # Opération risquée
    result = replicate.run(model, input=prompt)
except replicate.exceptions.ReplicateError as e:
    # Erreur spécifique à Replicate
    raise HTTPException(503, f"Service IA indisponible: {e}")
except Exception as e:
    # Erreur générique
    raise HTTPException(500, f"Erreur interne: {e}")
```

### 7.2 Optimisation des Performances

#### Mise en Cache

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_universe_response(univers_id: int):
    """Cache les réponses d'univers fréquemment consultés."""
    # Logique de récupération avec cache
    pass
```

#### Pagination Efficace

```python
@router.get("/universes")
def list_universes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Pagination côté base de données
    query = db.query(Univers).order_by(Univers.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}
```

#### Lazy Loading

```python
# ✅ BON : Chargement à la demande
univers = db.query(Univers).first()
assets = univers.assets  # Requête exécutée ici seulement

# ❌ MAUVAIS : Chargement eager systématique
univers = db.query(Univers).options(joinedload(Univers.assets)).first()
# Charge toujours les assets même si non utilisés
```

### 7.3 Tests et Qualité

#### Tests Pyramidaux

```python
# Tests unitaires (base de la pyramide)
def test_slugify():
    assert slugify("Hello World!") == "hello-world"

# Tests d'intégration (milieu)
def test_create_universe_integration(client, test_db):
    response = client.post("/universes", json={"name": "Test"})
    assert response.status_code == 201

# Tests end-to-end (sommet)
def test_full_generation_workflow(client):
    # Créer univers → Générer contenu → Vérifier résultats
    pass
```

#### Fixtures Réutilisables

```python
# tests/conftest.py
@pytest.fixture
def test_universe(client):
    """Crée un univers de test."""
    response = client.post("/universes", json={
        "name": "Test Universe",
        "is_public": True
    })
    return response.json()

@pytest.fixture  
def test_db():
    """Session de base de données de test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Mocking Approprié

```python
# ✅ BON : Mock des services externes
@patch('services.generation_service.replicate.run')
def test_generation_success(mock_replicate, client):
    mock_replicate.return_value = mock_image_data
    response = client.post("/generate/test/images")
    assert response.status_code == 200

# ❌ MAUVAIS : Mock de tout
@patch('fastapi.BackgroundTasks.add_task')
@patch('sqlalchemy.orm.Session.commit')
def test_with_too_many_mocks(mock_commit, mock_bg, client):
    # Difficile à maintenir et comprendre
    pass
```

### 7.4 Déploiement et Monitoring

#### Variables d'Environnement

```bash
# .env.production
STORAGE_PATH=/app/storage
REPLICATE_API_TOKEN=sk-...
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DEBUG=false
```

#### Health Checks

```python
@app.get("/health")
def health_check():
    """Vérification complète de l'état du service."""
    checks = {
        "database": check_database_connection(),
        "supabase": supabase_service.is_connected,
        "replicate": generation_service.is_available,
        "storage": check_storage_access(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "version": "2.0.0"
    }
```

#### Logging Structuré

```python
import logging

# Configuration centralisée
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Utilisation dans le code
logger.info(f"Univers créé: {univers.name}")
logger.error(f"Erreur génération IA: {str(e)}", exc_info=True)
```

#### Métriques et Monitoring

```python
from fastapi import Request, Response
import time

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Métriques de performance
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.2f}s")
    
    # Headers de monitoring
    response.headers["X-Process-Time"] = str(duration)
    response.headers["X-API-Version"] = "2.0.0"
    
    return response
```

---

## Annexes

### Annexe A : Schémas de Base de Données

#### Table `univers`
```sql
CREATE TABLE univers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    thumbnail_url TEXT,
    is_public BOOLEAN DEFAULT 1,
    owner_id TEXT,
    background_music TEXT,
    background_color TEXT DEFAULT '#1a1a2e',
    supabase_id TEXT,
    last_synced_at DATETIME
);
```

#### Table `univers_assets`
```sql
CREATE TABLE univers_assets (
    id TEXT PRIMARY KEY,
    univers_id INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    image_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (univers_id) REFERENCES univers (id) ON DELETE CASCADE
);
```

#### Table `jobs`
```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    univers_slug TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    current_step INTEGER DEFAULT 0,
    message TEXT,
    error TEXT,
    result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME
);
```

### Annexe B : Endpoints API

#### Univers
- `GET /api/universes` - Lister les univers
- `POST /api/universes` - Créer un univers
- `GET /api/universes/{slug}` - Détails d'un univers
- `PATCH /api/universes/{slug}` - Modifier un univers
- `DELETE /api/universes/{slug}` - Supprimer un univers

#### Assets
- `GET /api/universes/{slug}/assets` - Lister les assets
- `POST /api/universes/{slug}/assets` - Créer un asset
- `GET /api/universes/{slug}/assets/{id}` - Détails d'un asset
- `PATCH /api/universes/{slug}/assets/{id}` - Modifier un asset
- `DELETE /api/universes/{slug}/assets/{id}` - Supprimer un asset

#### Génération
- `POST /api/generate/{slug}/concepts` - Générer des concepts
- `POST /api/generate/{slug}/images` - Générer des images
- `POST /api/generate/{slug}/videos` - Générer des vidéos
- `POST /api/generate/{slug}/music` - Générer de la musique
- `POST /api/generate/{slug}/all` - Génération complète

#### Synchronisation
- `POST /api/sync/push/{slug}` - Pousser vers Supabase
- `POST /api/sync/pull/{slug}` - Tirer depuis Supabase

#### Jobs
- `GET /api/jobs` - Lister les jobs
- `GET /api/jobs/{id}` - Détails d'un job

### Annexe C : Configuration

#### Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `STORAGE_PATH` | Chemin de stockage local | `/app/storage` |
| `REPLICATE_API_TOKEN` | Token API Replicate | `r8_...` |
| `SUPABASE_URL` | URL Supabase | `https://...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Clé service Supabase | `eyJ...` |
| `DEBUG` | Mode debug | `true`/`false` |

#### Configuration Docker

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
    environment:
      - STORAGE_PATH=/app/storage
      - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

### Annexe D : Glossaire

#### Concepts Clés

**API REST** : Interface de programmation permettant la communication entre applications via HTTP.

**ORM** : Technique de programmation qui permet de convertir des données entre systèmes incompatibles.

**FastAPI** : Framework Python moderne pour créer des APIs REST avec validation automatique.

**SQLAlchemy** : Bibliothèque Python pour l'accès aux bases de données via un ORM.

**Pydantic** : Bibliothèque pour la validation et sérialisation de données Python.

**Middleware** : Logiciel qui agit comme pont entre applications, traitant les requêtes/réponses.

**Injection de Dépendances** : Pattern où les dépendances sont fournies plutôt que créées à l'intérieur.

**Job Asynchrone** : Tâche exécutée en arrière-plan sans bloquer l'interface utilisateur.

**Sérialisation** : Conversion d'objets en format transmissible (JSON, XML, etc.).

---

*Ce manuel constitue une référence complète pour comprendre et développer avec la stack technologique de MagikSwipe. Il combine théorie et pratique pour offrir une compréhension approfondie des concepts modernes de développement backend Python.*