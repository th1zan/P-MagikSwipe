# Manuel de Formation : Implémentation de Semantic Release et GitHub Actions

## MagikSwipe - Application d'Apprentissage pour Enfants Alimentée par IA

---

**Auteurs :** Équipe MagikSwipe  
**Version :** 1.0.0  
**Date :** Décembre 2025  
**Technologies :** Semantic Release, GitHub Actions, Python, Conventional Commits  

---

## Table des Matières

### [Introduction](#introduction)
- [Présentation du Projet](#présentation-du-projet)
- [Objectifs du Manuel](#objectifs-du-manuel)
- [Prérequis Techniques](#prérequis-techniques)

### [Chapitre 1 : Conventional Commits](#chapitre-1--conventional-commits)
- [1.1 Qu'est-ce qu'un Conventional Commit ?](#11-qu'est-ce-qu'un-conventional-commit-)
- [1.2 Structure d'un Commit Conventionnel](#12-structure-d'un-commit-conventionnel)
- [1.3 Types de Commits](#13-types-de-commits)
- [1.4 Scopes dans MagikSwipe](#14-scopes-dans-magikswipe)
- [1.5 Breaking Changes](#15-breaking-changes)
- [1.6 Exemples Pratiques](#16-exemples-pratiques)
- [1.7 Outils et Validation](#17-outils-et-validation)

### [Chapitre 2 : Semantic Release - Principes Fondamentaux](#chapitre-2--semantic-release---principes-fondamentaux)
- [2.1 Qu'est-ce que Semantic Release ?](#21-qu'est-ce-que-semantic-release-)
- [2.2 Comment ça Marche](#22-comment-ça-marche)
- [2.3 Avantages pour MagikSwipe](#23-avantages-pour-magikswipe)
- [2.4 Configuration de Base](#24-configuration-de-base)
- [2.5 Versionnement Sémantique](#25-versionnement-sémantique)

### [Chapitre 3 : Configuration de Semantic Release](#chapitre-3--configuration-de-semantic-release)
- [3.1 pyproject.toml - Configuration Centrale](#31-pyprojecttoml---configuration-centrale)
- [3.2 Version Stamping](#32-version-stamping)
- [3.3 Changelog Generation](#33-changelog-generation)
- [3.4 Branches et Releases](#34-branches-et-releases)
- [3.5 Plugins et Extensions](#35-plugins-et-extensions)

### [Chapitre 4 : GitHub Actions - Automatisation CI/CD](#chapitre-4--github-actions---automatisation-cicd)
- [4.1 Introduction à GitHub Actions](#41-introduction-à-github-actions)
- [4.2 Structure d'un Workflow](#42-structure-d'un-workflow)
- [4.3 Triggers et Events](#43-triggers-et-events)
- [4.4 Jobs et Steps](#44-jobs-et-steps)
- [4.5 Environnements et Secrets](#45-environnements-et-secrets)
- [4.6 Actions Réutilisables](#46-actions-réutilisables)

### [Chapitre 5 : Pipeline CI/CD pour MagikSwipe](#chapitre-5--pipeline-cicd-pour-magikswipe)
- [5.1 Architecture du Pipeline](#51-architecture-du-pipeline)
- [5.2 Workflow de Release](#52-workflow-de-release)
- [5.3 Tests Automatisés](#53-tests-automatis)
- [5.4 Build et Packaging](#54-build-et-packaging)
- [5.5 Déploiement](#55-déploiement)
- [5.6 Monitoring et Alertes](#56-monitoring-et-alertes)

### [Chapitre 6 : Pratiques de Développement avec Semantic Release](#chapitre-6--pratiques-de-développement-avec-semantic-release)
- [6.1 Workflow de Développement](#61-workflow-de-développement)
- [6.2 Gestion des Branches](#62-gestion-des-branches)
- [6.3 Pull Requests](#63-pull-requests)
- [6.4 Code Reviews](#64-code-reviews)
- [6.5 Release Management](#65-release-management)
- [6.6 Rollbacks et Hotfixes](#66-rollbacks-et-hotfixes)

### [Chapitre 7 : Dépannage et Bonnes Pratiques](#chapitre-7--dépannage-et-bonnes-pratiques)
- [7.1 Problèmes Courants](#71-problèmes-courants)
- [7.2 Debugging Semantic Release](#72-debugging-semantic-release)
- [7.3 Optimisations](#73-optimisations)
- [7.4 Sécurité](#74-sécurité)
- [7.5 Maintenance](#75-maintenance)

### [Annexes](#annexes)
- [Annexe A : Configuration Complète](#annexe-a--configuration-complète)
- [Annexe B : Scripts Utiles](#annexe-b--scripts-utiles)
- [Annexe C : Glossaire](#annexe-c--glossaire)
- [Annexe D : Ressources](#annexe-d--ressources)

---

## Introduction

### Présentation du Projet

**MagikSwipe** est une application web éducative innovante conçue pour l'apprentissage des enfants, alimentée par l'intelligence artificielle. L'application permet aux éducateurs et parents de créer des univers thématiques personnalisés et de générer automatiquement du contenu multimédia adapté aux enfants.

Dans ce manuel, nous nous concentrons sur l'implémentation d'un système de gestion de versions et de releases automatisées utilisant Semantic Release et GitHub Actions. Ce système permet de maintenir un historique de versions propre, de générer des changelogs automatiquement, et de déployer de manière fiable.

### Objectifs du Manuel

Ce manuel a pour objectif de vous former à l'implémentation et à l'utilisation de Semantic Release dans le contexte de MagikSwipe. À la fin de ce manuel, vous serez capable de :

- Comprendre et utiliser les Conventional Commits
- Configurer Semantic Release pour un projet Python
- Créer des workflows GitHub Actions pour l'automatisation
- Gérer les releases et versions de manière professionnelle
- Dépanner les problèmes courants
- Maintenir et optimiser le système

### Prérequis Techniques

#### Connaissances Requises
- **Git** : Commandes de base (commit, push, pull, merge)
- **Python** : Niveau intermédiaire
- **YAML** : Syntaxe pour GitHub Actions
- **Command Line** : Utilisation du terminal

#### Environnements
- **GitHub Account** : Avec un repository configuré
- **Python 3.8+** : Pour Semantic Release
- **Git** : Version récente
- **Text Editor** : VS Code recommandé

---

## Chapitre 1 : Conventional Commits

### 1.1 Qu'est-ce qu'un Conventional Commit ?

Les Conventional Commits sont une convention pour formater les messages de commit Git. Cette convention permet d'automatiser la génération de changelogs et le versionnement sémantique.

#### Pourquoi Conventional Commits ?

- **Automatisation** : Permet de générer automatiquement des changelogs et versions
- **Clarté** : Messages structurés et lisibles
- **Outils** : Intégration avec de nombreux outils de développement
- **Équipe** : Cohérence dans les messages de commit

#### Histoire
La spécification Conventional Commits a été créée en 2017 par des développeurs travaillant sur Angular. Elle a depuis été adoptée par de nombreux projets open source et entreprises.

### 1.2 Structure d'un Commit Conventionnel

Un commit conventionnel suit cette structure :

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Composants Détaillés

##### Type (Obligatoire)
Le type décrit la nature du changement :
- `feat` : Nouvelle fonctionnalité
- `fix` : Correction de bug
- `docs` : Changement de documentation
- `style` : Changement de style (formatage, etc.)
- `refactor` : Refactorisation du code
- `test` : Ajout ou modification de tests
- `chore` : Tâche de maintenance

##### Scope (Optionnel)
Le scope précise la partie du code affectée :
- `backend` : Changements backend
- `viewer` : Changements interface
- `api` : Changements API
- `db` : Changements base de données

##### Description (Obligatoire)
Une description concise du changement :
- Commence par une minuscule
- Pas de point final
- Impératif présent (e.g., "add", "fix", "update")

##### Body (Optionnel)
Description détaillée du changement :
- Explique le pourquoi et le comment
- Peut contenir plusieurs paragraphes

##### Footer (Optionnel)
Informations supplémentaires :
- Breaking changes
- Issues fermées
- Références

### 1.3 Types de Commits

#### feat - Nouvelle Fonctionnalité
Utilisé pour ajouter une nouvelle fonctionnalité à l'application.

**Exemples :**
```
feat: add user authentication system
feat(backend): implement music generation endpoint
feat(viewer): add gallery slideshow feature
```

#### fix - Correction de Bug
Utilisé pour corriger un bug existant.

**Exemples :**
```
fix: resolve memory leak in image generation
fix(viewer): fix gallery loading on mobile devices
fix(backend): correct SQL query for universe assets
```

#### docs - Documentation
Utilisé pour les changements de documentation.

**Exemples :**
```
docs: update API documentation for music endpoints
docs: add installation guide for developers
docs(README): update project description
```

#### style - Style de Code
Utilisé pour les changements qui n'affectent pas la logique (formatage, etc.).

**Exemples :**
```
style: format code with black
style: remove trailing whitespace
style(backend): consistent import ordering
```

#### refactor - Refactorisation
Utilisé pour restructurer le code sans changer son comportement.

**Exemples :**
```
refactor(backend): extract database logic to separate service
refactor: simplify job status management
refactor(viewer): optimize DOM manipulation
```

#### test - Tests
Utilisé pour ajouter ou modifier des tests.

**Exemples :**
```
test: add unit tests for music generation
test(backend): integration tests for API endpoints
test: add e2e tests for viewer gallery
```

#### chore - Maintenance
Utilisé pour les tâches de maintenance diverses.

**Exemples :**
```
chore: update dependencies
chore(shared): configure linting tools
chore: setup CI/CD pipeline
```

### 1.4 Scopes dans MagikSwipe

Pour MagikSwipe, nous utilisons les scopes suivants pour organiser les changements :

#### backend - Backend Python/FastAPI
Tous les changements liés au serveur backend :
- API endpoints
- Base de données
- Services métier
- Configuration

**Exemples :**
```
feat(backend): add music generation with Replicate
fix(backend): resolve SQL injection vulnerability
refactor(backend): extract validation logic to Pydantic models
```

#### viewer - Interface Web
Tous les changements liés à l'interface utilisateur :
- HTML/CSS/JavaScript
- Interface utilisateur
- Interactions frontend
- Affichage du contenu

**Exemples :**
```
feat(viewer): add drag-and-drop for asset upload
fix(viewer): fix responsive layout on tablets
style(viewer): update color scheme for better accessibility
```

#### shared - Code Commun
Changements affectant plusieurs composants :
- Configuration commune
- Scripts de build
- Docker setup
- Documentation racine

**Exemples :**
```
chore(shared): update Docker base images
docs(shared): add deployment guide
refactor(shared): move common utilities to shared module
```

#### test - Tests
Changements spécifiques aux tests :
- Tests unitaires
- Tests d'intégration
- Scripts de test
- Configuration de test

**Exemples :**
```
test: add performance tests for AI generation
test(backend): mock external API calls in integration tests
```

#### ci - Intégration Continue
Changements liés à l'automatisation :
- GitHub Actions workflows
- Scripts de déploiement
- Configuration CI/CD

**Exemples :**
```
ci: add semantic release workflow
ci: update test coverage reporting
chore(ci): configure automated dependency updates
```

### 1.5 Breaking Changes

Un breaking change est un changement qui nécessite une action de la part des utilisateurs (mise à jour manuelle, changement de configuration, etc.).

#### Comment Marquer un Breaking Change

**Option 1 : Type BREAKING CHANGE**
```
feat: change API response format

BREAKING CHANGE: The response now includes a new 'metadata' field
```

**Option 2 : ! après le type**
```
feat!: change API response format

The response now includes a new 'metadata' field
```

#### Exemples dans MagikSwipe
```
feat(backend)!: migrate from SQLite to PostgreSQL

BREAKING CHANGE: Database schema changes require data migration
```

```
fix(viewer)!: remove deprecated jQuery dependency

BREAKING CHANGE: Custom jQuery plugins must be updated
```

### 1.6 Exemples Pratiques

#### Développement d'une Nouvelle Fonctionnalité

**Scénario :** Ajouter la génération de musique multilingue

```
feat(backend): add multilingual music generation

Add support for generating music in French, English, Spanish,
Italian, and German. Each language has customizable prompts
stored in univers_music_prompts table.

- Add language parameter to music generation endpoint
- Update Replicate integration for multilingual support
- Store language-specific prompts in database
- Add validation for supported languages

Closes #123
```

#### Correction d'un Bug

**Scénario :** Résoudre un problème de chargement d'images

```
fix(viewer): resolve gallery image loading failure

Images were not displaying due to incorrect path resolution
in the viewer. The issue was caused by a mismatch between
the API response format and the frontend expectations.

- Fix image URL construction in gallery.js
- Add error handling for missing images
- Update image loading to use absolute paths
```

#### Refactorisation

**Scénario :** Réorganiser la logique de génération IA

```
refactor(backend): extract AI generation to dedicated service

The generation logic was scattered across multiple route handlers.
This refactor consolidates all AI interactions into a single,
reusable service class.

- Create GenerationService class in services/
- Move Replicate API calls to service methods
- Update route handlers to use service
- Add proper error handling and logging
```

### 1.7 Outils et Validation

#### Outils de Validation

##### commitizen
Outil interactif pour créer des commits conventionnels.

**Installation :**
```bash
pip install commitizen
```

**Utilisation :**
```bash
cz commit
```

##### commitlint
Validation automatique des messages de commit.

**Configuration dans .commitlintrc.js :**
```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [2, 'always', ['backend', 'viewer', 'shared', 'test', 'ci']],
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
  }
};
```

##### pre-commit hooks
Validation avant commit.

**Configuration dans .pre-commit-config.yaml :**
```yaml
repos:
  - repo: https://github.com/alexander-gabriel/Commitizen
    rev: v2.42.0
    hooks:
      - id: commitizen
```

#### Intégration dans l'Éditeur

##### VS Code Extension
- **Conventional Commits** : Extension pour assister la création de commits

##### Git Template
Configuration globale de Git pour inclure des hooks.

```bash
git config --global init.templatedir ~/.git-templates
```

---

## Chapitre 2 : Semantic Release - Principes Fondamentaux

### 2.1 Qu'est-ce que Semantic Release ?

Semantic Release est un outil qui automatise le processus de versionnement et de release d'un projet logiciel. Il analyse les messages de commit conventionnels pour déterminer automatiquement le numéro de version suivant et générer un changelog.

#### Origines
Semantic Release a été créé pour résoudre les problèmes de versionnement manuel :
- Versions inconsistantes
- Changelogs oubliés
- Releases manuelles fastidieuses
- Erreurs humaines dans le versionnement

### 2.2 Comment ça Marche

#### Processus Automatique

1. **Analyse des Commits** : Examine tous les commits depuis la dernière release
2. **Détermination de Version** : Calcule la nouvelle version basée sur les types de commits
3. **Génération du Changelog** : Crée un changelog formaté avec les changements
4. **Mise à Jour des Fichiers** : Modifie les fichiers de version (package.json, pyproject.toml, etc.)
5. **Création du Tag** : Crée un tag Git avec la nouvelle version
6. **Publication** : Publie la release sur GitHub, PyPI, etc.

#### Règles de Versionnement

| Type de Commit | Impact sur Version | Exemple |
|----------------|-------------------|---------|
| `fix` | Patch (0.0.1) | 1.2.3 → 1.2.4 |
| `feat` | Minor (0.1.0) | 1.2.3 → 1.3.0 |
| BREAKING CHANGE | Major (1.0.0) | 1.2.3 → 2.0.0 |

### 2.3 Avantages pour MagikSwipe

#### Automatisation Complète
- Plus besoin de gérer manuellement les versions
- Changelogs toujours à jour
- Releases cohérentes

#### Qualité du Code
- Commits conventionnels encouragent de meilleurs messages
- Historique clair et navigable
- Releases prédictibles

#### Équipe et Collaboration
- Standards partagés dans l'équipe
- Moins de disputes sur le versionnement
- Processus transparent

### 2.4 Configuration de Base

#### Installation
```bash
pip install python-semantic-release
```

#### Configuration Minimale
```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
branch = "main"
```

### 2.5 Versionnement Sémantique

#### Numéros de Version
Un numéro de version sémantique suit le format : `MAJOR.MINOR.PATCH`

- **MAJOR** : Changements incompatibles (breaking changes)
- **MINOR** : Nouvelles fonctionnalités compatibles
- **PATCH** : Corrections de bugs compatibles

#### Pré-releases
- `1.0.0-alpha.1` : Version alpha
- `1.0.0-beta.2` : Version beta
- `1.0.0-rc.1` : Release candidate

#### Métadonnées de Build
- `1.0.0+20130313144700` : Avec timestamp
- `1.0.0+exp.sha.5114f85` : Avec hash Git

---

## Chapitre 3 : Configuration de Semantic Release

### 3.1 pyproject.toml - Configuration Centrale

Le fichier `pyproject.toml` est le cœur de la configuration Semantic Release pour les projets Python modernes.

#### Structure de Base
```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "magikswipe-backend"
version = "2.0.0"
description = "Backend API for MagikSwipe"
authors = [{name = "MagikSwipe Team"}]
requires-python = ">=3.8"
dependencies = [
    "fastapi",
    "sqlalchemy",
    # ... autres dépendances
]

[tool.semantic_release]
# Configuration Semantic Release
version_toml = ["pyproject.toml:project.version"]
branch = "main"
build_command = "python -m build --sdist --wheel ."
upload_to_release = true
```

#### Configuration Détaillée

##### Version Stamping
```toml
version_toml = ["pyproject.toml:project.version"]
version_variables = ["main.py:version"]
```
Configure quels fichiers mettre à jour avec la nouvelle version.

##### Branches
```toml
branch = "main"
```
Branche depuis laquelle les releases sont créées.

##### Build et Publication
```toml
build_command = "python -m build --sdist --wheel ."
upload_to_release = true
```
Commande pour construire le package et uploader vers GitHub releases.

##### Parser de Commits
```toml
[tool.semantic_release.commit_parser_options]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]
```
Personnalisation des règles de versionnement.

### 3.2 Version Stamping

#### Fichiers Supportés
Semantic Release peut mettre à jour la version dans plusieurs types de fichiers :

- `pyproject.toml` : `[project].version`
- `setup.py` : `version = "1.0.0"`
- `__init__.py` : `__version__ = "1.0.0"`
- `main.py` : `version = "1.0.0"`

#### Exemple pour MagikSwipe
```toml
version_toml = ["pyproject.toml:project.version"]
version_variables = ["backend/main.py:version"]
```

Le fichier `backend/main.py` sera mis à jour :
```python
app = FastAPI(
    title="MagikSwipe Backend",
    version="2.0.1",  # Automatiquement mis à jour
    # ...
)
```

### 3.3 Changelog Generation

#### Configuration du Changelog
```toml
[tool.semantic_release.changelog]
exclude_commit_patterns = [
    '''chore(?:\([^)]*?\))?: .+''',
    '''ci(?:\([^)]*?\))?: .+''',
]
```

#### Format du Changelog
Le changelog généré suit le format Keep a Changelog :

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2025-12-19

### Fixed
- Fix memory leak in image generation (backend)

### Added
- Add multilingual music generation (backend)

## [2.0.0] - 2025-12-15

### Breaking Changes
- Migrate to new API structure (backend)
```

### 3.4 Branches et Releases

#### Stratégie de Branches
Pour MagikSwipe, nous utilisons une stratégie simple :
- `main` : Branche principale pour les releases stables
- Branches de feature : Pour le développement
- Pas de branche `release` séparée

#### Configuration
```toml
branch = "main"
```

### 3.5 Plugins et Extensions

#### Plugins Disponibles
- **@semantic-release/changelog** : Génération du changelog
- **@semantic-release/git** : Commit des changements
- **@semantic-release/github** : Publication sur GitHub
- **@semantic-release/exec** : Exécution de commandes personnalisées

#### Configuration Avancée
```toml
[tool.semantic_release]
plugins = [
    "semantic_release.plugins.github",
    "semantic_release.plugins.changelog",
    "semantic_release.plugins.version",
]
```

---

## Chapitre 4 : GitHub Actions - Automatisation CI/CD

### 4.1 Introduction à GitHub Actions

GitHub Actions est une plateforme d'automatisation intégrée à GitHub qui permet d'automatiser les workflows de développement logiciel.

#### Concepts Clés
- **Workflow** : Processus automatisé (fichier YAML)
- **Job** : Groupe de steps exécutés sur un runner
- **Step** : Tâche individuelle (commande ou action)
- **Action** : Composant réutilisable
- **Runner** : Machine virtuelle exécutant les jobs

### 4.2 Structure d'un Workflow

#### Fichier de Workflow
Les workflows sont définis dans `.github/workflows/nom-du-workflow.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest
```

### 4.3 Triggers et Events

#### Events Disponibles
- `push` : Push vers une branche
- `pull_request` : Création/modification de PR
- `schedule` : Exécution programmée (cron)
- `workflow_dispatch` : Déclenchement manuel
- `release` : Publication de release

#### Configuration pour MagikSwipe
```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
```

### 4.4 Jobs et Steps

#### Structure d'un Job
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Step name
        run: echo "Command to execute"
      
      - name: Use an action
        uses: actions/checkout@v4
```

#### Types de Steps
- **run** : Exécuter des commandes shell
- **uses** : Utiliser une action GitHub
- **with** : Paramètres pour une action

### 4.5 Environnements et Secrets

#### Variables d'Environnement
```yaml
env:
  PYTHON_VERSION: '3.11'
```

#### Secrets GitHub
- `GH_TOKEN` : Token pour Git operations
- `PYPI_TOKEN` : Pour publication PyPI (si utilisé)

Configuration dans GitHub : Settings > Secrets and variables > Actions

### 4.6 Actions Réutilisables

#### Actions Populaires
- `actions/checkout@v4` : Récupérer le code
- `actions/setup-python@v4` : Configurer Python
- `actions/setup-node@v4` : Configurer Node.js
- `codecov/codecov-action@v3` : Rapport de couverture

#### Actions Personnalisées
Création d'actions composites ou JavaScript.

---

## Chapitre 5 : Pipeline CI/CD pour MagikSwipe

### 5.1 Architecture du Pipeline

Le pipeline CI/CD de MagikSwipe suit une approche moderne :

1. **Build** : Construction et validation
2. **Test** : Tests automatisés
3. **Release** : Versionnement et publication
4. **Deploy** : Déploiement en production

### 5.2 Workflow de Release

#### Workflow Complet
```yaml
name: Semantic Release

on:
  push:
    branches:
      - main

jobs:
  test-and-release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install python-semantic-release

      - name: Run tests
        run: |
          cd backend
          pytest

      - name: Semantic Release
        if: success()
        run: |
          cd backend
          semantic-release publish
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
```

### 5.3 Tests Automatisés

#### Tests Backend
```yaml
- name: Run tests
  run: |
    cd backend
    pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

#### Tests Viewer
```yaml
- name: Test viewer
  run: |
    cd viewer
    npm install
    npm run test
```

### 5.4 Build et Packaging

#### Build Python Package
```yaml
- name: Build package
  run: |
    cd backend
    python -m build --sdist --wheel .
```

#### Build Viewer Assets
```yaml
- name: Build viewer
  run: |
    cd viewer
    npm run build
```

### 5.5 Déploiement

#### Déploiement Docker
```yaml
- name: Deploy to production
  if: github.event_name == 'release'
  run: |
    docker-compose -f docker-compose.prod.yml up -d
```

### 5.6 Monitoring et Alertes

#### Notifications
```yaml
- name: Notify on failure
  if: failure()
  run: |
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Build failed"}' \
    ${{ secrets.SLACK_WEBHOOK }}
```

---

## Chapitre 6 : Pratiques de Développement avec Semantic Release

### 6.1 Workflow de Développement

#### Processus Standard
1. Créer une branche de feature
2. Développer la fonctionnalité
3. Commits conventionnels
4. Push et PR
5. Review et merge
6. Release automatique

### 6.2 Gestion des Branches

#### Branches de Feature
```bash
git checkout -b feat/add-music-generation
# Développement...
git commit -m "feat(backend): add music generation endpoint"
git push origin feat/add-music-generation
```

#### Merge vers Main
```bash
git checkout main
git pull origin main
git merge feat/add-music-generation
git push origin main  # Déclenche la release
```

### 6.3 Pull Requests

#### Template de PR
```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] feat: New feature
- [ ] fix: Bug fix
- [ ] docs: Documentation
- [ ] style: Code style
- [ ] refactor: Code refactoring
- [ ] test: Testing
- [ ] chore: Maintenance

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Breaking changes documented
```

### 6.4 Code Reviews

#### Points à Vérifier
- Commits conventionnels
- Tests présents
- Documentation à jour
- Breaking changes clairement identifiés

### 6.5 Release Management

#### Release Automatique
Les releases sont créées automatiquement sur push vers main avec des commits conventionnels.

#### Release Manuelle (si nécessaire)
```bash
semantic-release --noop  # Aperçu
semantic-release publish  # Release forcée
```

### 6.6 Rollbacks et Hotfixes

#### Rollback d'une Release
```bash
git revert <commit-hash>
git push origin main
```

#### Hotfix
```bash
git checkout -b hotfix/critical-bug main
# Fix...
git commit -m "fix: critical bug fix"
git push origin hotfix/critical-bug
# Create PR to main
```

---

## Chapitre 7 : Dépannage et Bonnes Pratiques

### 7.1 Problèmes Courants

#### Commit Non Conventionnel
**Erreur :** `Invalid commit message`
**Solution :** Utiliser `cz commit` ou corriger le message

#### Version Non Mise à Jour
**Erreur :** Fichier de version inchangé
**Solution :** Vérifier la configuration `version_toml`

#### Tag Déjà Existant
**Erreur :** `Tag already exists`
**Solution :** Supprimer le tag et recommencer

### 7.2 Debugging Semantic Release

#### Mode Debug
```bash
semantic-release -vv publish
```

#### Dry Run
```bash
semantic-release --noop version
```

#### Logs Détaillés
```bash
semantic-release --verbose publish
```

### 7.3 Optimisations

#### Performance
- Utiliser `fetch-depth: 0` pour l'historique complet
- Cacher les dépendances
- Paralléliser les jobs

#### Cache
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 7.4 Sécurité

#### Secrets
- Ne jamais commiter de secrets
- Utiliser GitHub secrets
- Rotation régulière des tokens

#### Dépendances
- Auditer régulièrement les dépendances
- Utiliser des outils comme `safety`
- Mettre à jour régulièrement

### 7.5 Maintenance

#### Mises à Jour
```bash
pip install --upgrade python-semantic-release
```

#### Nettoyage
```bash
# Supprimer les anciennes releases
gh release list --limit 100 | grep -E "v[0-9]+\.[0-9]+\.[0-9]+" | head -n 50 | xargs -I {} gh release delete {}
```

---

## Annexes

### Annexe A : Configuration Complète

#### pyproject.toml Complet
```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "magikswipe-backend"
version = "2.0.0"
description = "Backend API for MagikSwipe"
authors = [{name = "MagikSwipe Team"}]
requires-python = ">=3.8"
dependencies = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "sqlalchemy==2.0.23",
    "aiosqlite==0.19.0",
    "supabase==2.0.0",
    "replicate==0.20.0",
    "python-dotenv==1.0.0",
    "pydantic==2.5.2",
    "pydantic-settings==2.1.0",
    "python-slugify==8.0.1",
    "pillow==10.1.0",
    "requests==2.31.0",
    "deep-translator==1.11.4",
    "pyyaml==6.0.1",
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
    "httpx==0.24.1",
    "pytest-cov==4.1.0",
]

[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
version_variables = ["../backend/main.py:version"]
branch = "main"
build_command = "python -m build --sdist --wheel ."
upload_to_release = true

[tool.semantic_release.commit_parser_options]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]
parse_squash_commits = true
ignore_merge_commits = true

[tool.semantic_release.changelog]
exclude_commit_patterns = [
    '''chore(?:\([^)]*?\))?: .+''',
    '''ci(?:\([^)]*?\))?: .+''',
    '''style(?:\([^)]*?\))?: .+''',
    '''refactor(?:\([^)]*?\))?: .+''',
    '''test(?:\([^)]*?\))?: .+''',
    '''build\((?!deps\): .+)''',
    '''Initial [Cc]ommit.*''',
]
```

#### Workflow GitHub Actions Complet
```yaml
name: Semantic Release

on:
  push:
    branches:
      - main

jobs:
  test-and-release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GH_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install python-semantic-release build

      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}

      - name: Semantic Release
        if: success()
        run: |
          cd backend
          semantic-release publish
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
```

### Annexe B : Scripts Utiles

#### Script de Validation de Commits
```bash
#!/bin/bash
# validate-commit.sh

commit_msg=$(cat $1)

# Vérifier le format conventional commit
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,}"; then
    echo "❌ Commit message doesn't follow conventional format"
    echo "Expected: type(scope): description"
    echo "Example: feat(backend): add new endpoint"
    exit 1
fi

echo "✅ Commit message is valid"
```

#### Script de Préparation de Release
```bash
#!/bin/bash
# prepare-release.sh

echo "🚀 Preparing release..."

# Vérifier que tout est committé
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory not clean"
    exit 1
fi

# Vérifier les tests
cd backend
python -m pytest
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✅ Ready for release"
```

### Annexe C : Glossaire

- **Conventional Commit** : Format standardisé pour les messages de commit
- **Semantic Versioning** : Système de versionnement MAJOR.MINOR.PATCH
- **Changelog** : Document listant les changements entre versions
- **CI/CD** : Intégration Continue / Déploiement Continu
- **Workflow** : Processus automatisé dans GitHub Actions
- **Release** : Publication d'une nouvelle version du logiciel
- **Tag** : Marqueur Git pour identifier une version spécifique

### Annexe D : Ressources

#### Documentation Officielle
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

#### Outils Recommandés
- [commitizen](https://commitizen-tools.github.io/commitizen/) : Aide à la création de commits
- [commitlint](https://commitlint.js.org/) : Validation des commits
- [standard-version](https://github.com/conventional-changelog/standard-version) : Alternative à semantic-release

#### Communauté
- [Awesome Semantic Release](https://github.com/semantic-release/awesome-semantic-release)
- [Conventional Changelog](https://github.com/conventional-changelog/conventional-changelog)