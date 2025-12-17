"""Tests pour les endpoints d'administration (nettoyage des univers de test)."""

import pytest


class TestAdminCleanup:
    """Tests pour les fonctionnalités de nettoyage administrateur."""

    def test_list_test_universes(self, client, test_universe):
        """Test listing des univers de test."""
        response = client.get("/api/admin/cleanup-test-universes")
        assert response.status_code == 200

        data = response.json()
        assert "test_universes_count" in data
        assert "test_universe_slugs" in data
        assert "pattern" in data
        assert data["pattern"] == "*test* (case-insensitive)"

        # Should find at least our test universe
        assert test_universe["slug"] in data["test_universe_slugs"]

    def test_cleanup_single_universe_dry_run(self, client, test_universe):
        """Test nettoyage d'un univers individuel (dry run)."""
        slug = test_universe["slug"]

        response = client.delete(f"/api/admin/cleanup-test-universes/{slug}")
        assert response.status_code == 400
        assert "Confirmation required" in response.json()["detail"]

    def test_cleanup_single_universe_invalid_pattern(self, client):
        """Test nettoyage d'un univers qui ne suit pas le pattern de test."""
        response = client.delete("/api/admin/cleanup-test-universes/my-universe?confirm=true")
        assert response.status_code == 400
        assert "is not a test universe" in response.json()["detail"]

    def test_cleanup_all_universes_dry_run(self, client, test_universe):
        """Test nettoyage de tous les univers (dry run seulement)."""
        response = client.post("/api/admin/cleanup-test-universes?dry_run=true")
        assert response.status_code == 200

        data = response.json()
        assert data["dry_run"] == True
        assert data["confirmed"] == False
        assert "found_test_universes" in data
        assert "test_universe_slugs" in data
        assert "DRY RUN" in data["message"]

        # Should find our test universe
        assert test_universe["slug"] in data["test_universe_slugs"]

    def test_cleanup_all_universes_requires_confirmation(self, client):
        """Test que le nettoyage global nécessite une confirmation."""
        response = client.post("/api/admin/cleanup-test-universes?dry_run=false")
        assert response.status_code == 400
        assert "confirm" in response.json()["detail"].lower()

    def test_validation_functions(self):
        """Test des fonctions de validation."""
        from routes.admin import is_test_universe

        # Patterns valides (contiennent 'test' n'importe où, case-insensitive)
        assert is_test_universe("test-universe-abc12345") == True
        assert is_test_universe("test-private-def67890") == True
        assert is_test_universe("test-anything") == True
        assert is_test_universe("test-cleanup01") == True
        assert is_test_universe("test-") == True

        # Variations de casse acceptées
        assert is_test_universe("Test-universe-abc12345") == True
        assert is_test_universe("TEST-private-def67890") == True
        assert is_test_universe("Test-anything") == True
        assert is_test_universe("TEST-cleanup01") == True

        # 'test' n'importe où dans le slug
        assert is_test_universe("my-test-universe") == True
        assert is_test_universe("universe-test-123") == True
        assert is_test_universe("prefix-test-suffix") == True
        assert is_test_universe("testing-phase") == True
        assert is_test_universe("contest-winner") == True  # ⚠️ Inclusif mais sécurisé

        # Patterns invalides (ne contiennent pas 'test')
        assert is_test_universe("my-universe") == False
        assert is_test_universe("production-universe") == False
        assert is_test_universe("dev-universe") == False