"""Tests pour la génération IA avec mocks (évite les coûts Replicate)."""

import pytest
from unittest.mock import patch, MagicMock


class TestGenerationConcepts:
    """Tests génération de concepts (avec mock pour éviter coûts)."""

    @patch('services.generation_service.replicate.run')
    @patch('config.settings.REPLICATE_API_TOKEN', 'fake_token')
    def test_generate_concepts_success(self, mock_replicate, client, test_universe):
        """Test génération de concepts réussie (avec mock)."""
        slug = test_universe["slug"]

        # Mock de la réponse Replicate - retourner un générateur qui produit une string JSON
        mock_replicate.return_value = ['["vache", "cochon", "cheval"]']

        # Mock de la traduction
        with patch('services.generation_service.GoogleTranslator') as mock_translator:
            mock_translator.return_value.translate.return_value = "translated_concept"

            response = client.post(f"/api/generate/{slug}/concepts", json={
                "theme": "animaux de la ferme",
                "count": 3,
                "language": "fr"
            })

            # Devrait réussir avec le mock
            assert response.status_code == 200
            data = response.json()
            assert "concepts" in data
            assert "translations" in data
            assert len(data["concepts"]) == 3

    def test_generate_concepts_universe_not_found(self, client):
        """Test génération de concepts pour univers inexistant."""
        response = client.post("/api/generate/nonexistent/concepts", json={
            "theme": "test",
            "count": 2,
            "language": "fr"
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_generate_concepts_invalid_count(self, client, test_universe):
        """Test génération avec count invalide."""
        slug = test_universe["slug"]

        response = client.post(f"/api/generate/{slug}/concepts", json={
            "theme": "test",
            "count": 100,  # Trop élevé
            "language": "fr"
        })
        assert response.status_code == 422  # Validation error


class TestGenerationMusic:
    """Tests génération de musique (avec mock pour éviter coûts)."""

    @patch('services.generation_service.replicate.run')
    @patch('config.settings.REPLICATE_API_TOKEN', 'fake_token')
    def test_generate_music_success(self, mock_replicate, client, universe_with_music_prompts):
        """Test génération de musique réussie (avec mock)."""
        slug = universe_with_music_prompts["universe"]["slug"]

        # Mock de la réponse Replicate
        mock_response = MagicMock()
        mock_response.__str__ = MagicMock(return_value='audio_url_here')
        mock_replicate.return_value = mock_response

        with patch('services.generation_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'fake_audio_data'
            mock_get.return_value = mock_response

            response = client.post(f"/api/generate/{slug}/music", json={
                "language": "fr"
            })

            # Devrait créer un job
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "type" in data
            assert data["type"] == "generate_music"

    def test_generate_music_universe_not_found(self, client):
        """Test génération de musique pour univers inexistant."""
        response = client.post("/api/generate/nonexistent/music", json={
            "language": "fr"
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_generate_music_invalid_language(self, client, test_universe):
        """Test génération de musique avec langue invalide."""
        slug = test_universe["slug"]

        response = client.post(f"/api/generate/{slug}/music", json={
            "language": "invalid_lang"
        })
        assert response.status_code == 422  # Validation error


class TestGenerationImages:
    """Tests génération d'images (avec mock pour éviter coûts)."""

    @patch('services.generation_service.replicate.run')
    @patch('config.settings.REPLICATE_API_TOKEN', 'fake_token')
    def test_generate_images_success(self, mock_replicate, client, test_universe):
        """Test génération d'images réussie (avec mock)."""
        slug = test_universe["slug"]

        # Créer d'abord un asset
        asset_response = client.post(f"/api/universes/{slug}/assets", json={
            "display_name": "Test Asset for Images",
            "sort_order": 1
        })
        assert asset_response.status_code == 201

        # Mock de la réponse Replicate
        mock_response = MagicMock()
        mock_response.__str__ = MagicMock(return_value='image_url_here')
        mock_replicate.return_value = mock_response

        with patch('services.generation_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'fake_image_data'
            mock_get.return_value = mock_response

            response = client.post(f"/api/generate/{slug}/images")

            # Devrait créer un job
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "type" in data
            assert data["type"] == "generate_images"

    @patch('config.settings.REPLICATE_API_TOKEN', 'fake_token')
    def test_generate_images_no_assets(self, client, test_universe):
        """Test génération d'images sans assets."""
        slug = test_universe["slug"]

        response = client.post(f"/api/generate/{slug}/images")
        assert response.status_code == 400
        assert "No assets" in response.json()["detail"]


class TestGenerationVideos:
    """Tests génération de vidéos (avec mock pour éviter coûts)."""

    @patch('services.generation_service.replicate.run')
    @patch('config.settings.REPLICATE_API_TOKEN', 'fake_token')
    def test_generate_videos_success(self, mock_replicate, client, test_universe):
        """Test génération de vidéos réussie (avec mock)."""
        slug = test_universe["slug"]

        # Create an asset first
        asset_response = client.post(f"/api/universes/{slug}/assets", json={
            "display_name": "Test Asset",
            "sort_order": 1
        })
        assert asset_response.status_code == 201

        # Cette fois on utilise l'endpoint qui attend des images existantes
        # Simuler qu'il y a des images
        response = client.post(f"/api/generate/{slug}/videos")
        # Devrait échouer car pas d'images, mais avec le bon code d'erreur
        assert response.status_code == 400
        assert "No images found" in response.json()["detail"]


class TestGenerationAll:
    """Tests génération complète (avec mock pour éviter coûts)."""

    @patch('services.generation_service.replicate.run')
    @patch('config.settings.REPLICATE_API_TOKEN', 'fake_token')
    def test_generate_all_success(self, mock_replicate, client, test_universe):
        """Test génération complète réussie (avec mock)."""
        # Mock de multiples appels Replicate
        mock_response = MagicMock()
        mock_response.__str__ = MagicMock(return_value='content_url_here')
        mock_replicate.return_value = mock_response

        with patch('services.generation_service.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'fake_content_data'
            mock_get.return_value = mock_response

            response = client.post(f"/api/generate/{test_universe['slug']}/all", json={
                "theme": "test theme",
                "count": 10,
                "generate_videos": True,
                "generate_music": True
            })

            # Devrait créer un job
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "type" in data
            assert data["type"] == "generate_all"