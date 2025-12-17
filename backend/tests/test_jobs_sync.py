"""Tests pour les jobs async et la synchronisation."""

import pytest


class TestJobsManagement:
    """Tests de gestion des jobs asynchrones."""

    def test_list_jobs(self, client):
        """Test listing des jobs."""
        response = client.get("/api/jobs")
        assert response.status_code == 200

        jobs = response.json()
        assert isinstance(jobs, list)
        # Peut être vide si aucun job n'a été créé

    def test_cleanup_jobs(self, client):
        """Test nettoyage des jobs terminés."""
        # Créer d'abord quelques jobs terminés si nécessaire
        # Pour le moment, tester juste que l'endpoint répond

        response = client.delete("/api/jobs/cleanup")
        assert response.status_code == 200

        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "deleted_count" in data

    def test_get_job_not_found(self, client):
        """Test récupération d'un job inexistant."""
        response = client.get("/api/jobs/invalid-job-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestSyncOperations:
    """Tests des opérations de synchronisation avec Supabase."""

    def test_sync_status(self, client):
        """Test vérification du statut de connexion Supabase."""
        response = client.get("/api/sync/status")
        assert response.status_code == 200

        data = response.json()
        assert "supabase_connected" in data
        assert "supabase_url" in data

        # Note: supabase_connected peut être True ou False selon la config

    @pytest.mark.skipif(
        not pytest.importorskip("os").getenv("SUPABASE_URL"),
        reason="Supabase not configured"
    )
    def test_sync_pull_universe(self, client):
        """Test synchronisation pull d'un univers (si Supabase configuré)."""
        # Use the fixed test universe created in Supabase
        slug = "test-integration-universe"

        response = client.post(f"/api/sync/pull/{slug}")
        # Accept 200 (success), 404 (not found in Supabase), or 503 (service unavailable)
        assert response.status_code in [200, 404, 503]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "message" in data
            assert "synced_items" in data

    @pytest.mark.skipif(
        not pytest.importorskip("os").getenv("SUPABASE_URL"),
        reason="Supabase not configured"
    )
    def test_sync_push_universe(self, client, test_universe):
        """Test synchronisation push d'un univers (si Supabase configuré)."""
        slug = test_universe["slug"]

        response = client.post(f"/api/sync/push/{slug}")
        assert response.status_code in [200, 503]  # 200 si OK, 503 si pas connecté

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "message" in data
            assert "synced_items" in data

    def test_sync_universe_not_found(self, client):
        """Test synchronisation d'un univers inexistant."""
        response = client.post("/api/sync/pull/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_sync_pull_all(self, client):
        """Test synchronisation complète depuis Supabase."""
        response = client.post("/api/sync/pull-all")
        assert response.status_code in [200, 503]  # 200 si OK, 503 si pas connecté

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "message" in data
            assert "universes_synced" in data
            assert "assets_synced" in data
            assert "files_downloaded" in data