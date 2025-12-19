# Instructions pour les Agents - MagikSwipe

## Vue d'Ensemble

Ces instructions guident les agents IA (comme opencode) dans la gestion et le développement du projet MagikSwipe. Elles assurent une approche cohérente et professionnelle du développement, en mettant l'accent sur les conventional commits, GitHub CLI, et la maintenance automatisée des versions.

## Conventional Commits

### Format Obligatoire

Tous les commits doivent suivre la spécification [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types de Commits

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Changement de documentation
- `style`: Changement de style (formatage, etc.)
- `refactor`: Refactorisation du code
- `test`: Ajout ou modification de tests
- `chore`: Tâche de maintenance

### Scopes pour MagikSwipe

Utilisez ces scopes pour catégoriser les changements :

- `backend`: Changements backend Python/FastAPI (API, base de données, services)
- `viewer`: Changements interface web (HTML, CSS, JavaScript)
- `shared`: Changements transversaux (config, Docker, docs)
- `docs`: Documentation uniquement
- `test`: Tests et configuration de test
- `ci`: Intégration continue et déploiement

### Exemples de Commits

```
feat(backend): add music generation endpoint
fix(viewer): resolve gallery loading issue
docs: update API documentation
chore(shared): update Docker configuration
refactor(backend): extract database logic to service
test(backend): add integration tests for sync
```

### Breaking Changes

Pour les changements incompatibles, ajoutez `!` après le type ou un footer `BREAKING CHANGE`:

```
feat(backend)!: migrate to new database schema
fix(viewer)!: remove deprecated jQuery dependency

BREAKING CHANGE: API endpoints have changed
```

## Gestion des Pull Requests

### Création de PR

Utilisez toujours GitHub CLI (`gh`) pour créer des PR :

```bash
# Créer une branche de feature
git checkout -b feat/add-feature

# Commits conventionnels
git commit -m "feat(backend): implement new feature"

# Push et création de PR
git push origin feat/add-feature
gh pr create --title "feat(backend): implement new feature" --body "Description détaillée"
```

### Template de PR

Utilisez ce format pour les descriptions de PR :

```markdown
## Description
Brief description of the changes.

## Type of Change
- [x] feat: New feature
- [ ] fix: Bug fix
- [ ] docs: Documentation
- [ ] refactor: Code refactoring

## Testing
- [x] Tests added/updated
- [x] Manual testing completed

## Breaking Changes
- [ ] Yes (describe below)
- [x] No

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->
```

### Review Process

- Assignez au moins un reviewer
- Attendez l'approbation avant le merge
- Utilisez squash merge pour les branches de feature
- Le merge vers `main` déclenche automatiquement la release

## Maintenance du README

### Responsabilités

- Mettez à jour le README.md après chaque changement significatif
- Gardez la documentation à jour avec les nouvelles fonctionnalités
- Vérifiez que les exemples de code fonctionnent
- Maintenez les badges et statuts à jour

### Quand Mettre à Jour

- Nouvelle fonctionnalité majeure
- Changement d'API
- Nouveau prérequis
- Changement dans les instructions d'installation
- Mise à jour de version

### Format des Mises à Jour

```markdown
## [2.0.1] - 2025-12-19

### Added
- Multilingual music generation support
- New API endpoint for custom prompts

### Fixed
- Gallery loading performance issue
- Database connection pooling
```

## Utilisation de GitHub CLI

### Commandes Essentielles

```bash
# Issues
gh issue list
gh issue create --title "Bug: description" --body "Details"
gh issue close 123

# Pull Requests
gh pr list
gh pr create --title "feat: description" --body "Details"
gh pr checkout 456
gh pr merge 456 --squash

# Releases
gh release list
gh release create v2.0.1 --title "Release v2.0.1" --notes "Changelog"

# Repository
gh repo clone owner/repo
gh repo create new-repo
```

### Automatisation

- Préférez `gh` aux opérations manuelles dans GitHub UI
- Utilisez des scripts pour les tâches répétitives
- Intégrez `gh` dans les workflows d'automatisation

## Workflow Semantic Release

### Processus Automatique

1. **Commits Conventionnels** : Tous les commits suivent le format conventional
2. **Push vers Main** : Les merges vers `main` déclenchent la CI/CD
3. **Tests** : Exécution automatique des tests
4. **Versionnement** : Calcul automatique de la nouvelle version
5. **Changelog** : Génération automatique du CHANGELOG.md
6. **Release** : Création du tag et de la release GitHub

### Gestion des Versions

- `fix` → patch (2.0.0 → 2.0.1)
- `feat` → minor (2.0.0 → 2.1.0)
- BREAKING CHANGE → major (2.0.0 → 3.0.0)

### Intervention Manuelle

En cas de besoin, forcez une release :

```bash
cd backend
semantic-release --noop version  # Aperçu
semantic-release publish         # Release forcée
```

## Bonnes Pratiques de Développement

### Code Quality

- Respectez les conventions de code (black, flake8)
- Ajoutez des tests pour toute nouvelle fonctionnalité
- Documentez les APIs et fonctions complexes
- Utilisez des types Python pour la sécurité de type

### Sécurité

- Ne commitez jamais de secrets ou tokens
- Utilisez les variables d'environnement
- Auditez régulièrement les dépendances
- Validez les entrées utilisateur

### Performance

- Optimisez les requêtes de base de données
- Utilisez la mise en cache appropriée
- Monitorer les performances des endpoints
- Évitez les fuites de mémoire

### Tests

- Écrivez des tests unitaires pour la logique métier
- Ajoutez des tests d'intégration pour les APIs
- Testez les cas d'erreur et edge cases
- Maintenez une couverture de code > 80%

## Dépannage

### Problèmes Courants

#### Commit Rejeté
```
❌ Commit message doesn't follow conventional format
```
**Solution** : Utilisez `cz commit` ou corrigez le message

#### Release Échouée
- Vérifiez les logs GitHub Actions
- Assurez-vous que tous les tests passent
- Vérifiez la configuration semantic-release

#### Conflits de Merge
- Rebasez sur main avant de merger
- Résolvez les conflits localement
- Testez après le merge

### Ressources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Release Docs](https://python-semantic-release.readthedocs.io/)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [MagikSwipe Manual](SEMANTIC_RELEASE_MANUAL.md)

## Contact

Pour les questions sur ces instructions, consultez :
- Le manuel complet : `SEMANTIC_RELEASE_MANUAL.md`
- Les issues GitHub pour les problèmes techniques
- L'équipe MagikSwipe pour les clarifications