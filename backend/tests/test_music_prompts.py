"""Tests CRUD pour les prompts musique multilingues."""

import pytest


class TestMusicPromptsCRUD:
    """Tests CRUD complets pour les prompts musique."""

    def test_create_music_prompt_french(self, client, test_universe):
        """Test création d'un prompt musique français."""
        slug = test_universe["slug"]

        data = {
            "language": "fr",
            "prompt": "musique douce et enfantine française",
            "lyrics": "Paroles en français pour la musique douce"
        }

        response = client.post(f"/api/universes/{slug}/music-prompts", json=data)
        assert response.status_code == 201

        prompt = response.json()
        assert prompt["language"] == "fr"
        assert prompt["prompt"] == data["prompt"]
        assert prompt["lyrics"] == data["lyrics"]
        assert "id" in prompt
        assert "created_at" in prompt

    def test_create_music_prompt_english(self, client, test_universe):
        """Test création d'un prompt musique anglais."""
        slug = test_universe["slug"]

        data = {
            "language": "en",
            "prompt": "soft and child-friendly english music",
            "lyrics": "English lyrics for soft music"
        }

        response = client.post(f"/api/universes/{slug}/music-prompts", json=data)
        assert response.status_code == 201
        assert response.json()["language"] == "en"

    def test_create_duplicate_language_prompt(self, client, test_universe):
        """Test création de prompts pour la même langue (doit échouer)."""
        slug = test_universe["slug"]

        # Créer le premier prompt français
        data = {
            "language": "fr",
            "prompt": "premier prompt français",
            "lyrics": "premières paroles"
        }
        client.post(f"/api/universes/{slug}/music-prompts", json=data)

        # Tenter de créer un deuxième prompt français
        data2 = {
            "language": "fr",
            "prompt": "deuxième prompt français",
            "lyrics": "deuxièmes paroles"
        }
        response = client.post(f"/api/universes/{slug}/music-prompts", json=data2)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_list_music_prompts(self, client, universe_with_music_prompts):
        """Test listing de tous les prompts musique."""
        slug = universe_with_music_prompts["universe"]["slug"]

        response = client.get(f"/api/universes/{slug}/music-prompts")
        assert response.status_code == 200

        prompts = response.json()
        assert len(prompts) == 2  # Les 2 prompts créés dans la fixture

        languages = [p["language"] for p in prompts]
        assert "fr" in languages
        assert "en" in languages

    def test_get_specific_music_prompt(self, client, universe_with_music_prompts):
        """Test récupération d'un prompt musique spécifique."""
        slug = universe_with_music_prompts["universe"]["slug"]

        response = client.get(f"/api/universes/{slug}/music-prompts/fr")
        assert response.status_code == 200

        prompt = response.json()
        assert prompt["language"] == "fr"
        assert "musique douce" in prompt["prompt"]

    def test_get_nonexistent_music_prompt(self, client, test_universe):
        """Test récupération d'un prompt inexistant."""
        slug = test_universe["slug"]

        response = client.get(f"/api/universes/{slug}/music-prompts/it")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_music_prompt(self, client, universe_with_music_prompts):
        """Test mise à jour d'un prompt musique."""
        slug = universe_with_music_prompts["universe"]["slug"]

        # Mettre à jour les paroles françaises
        update_data = {
            "lyrics": "Paroles françaises mises à jour avec succès"
        }

        response = client.patch(f"/api/universes/{slug}/music-prompts/fr", json=update_data)
        assert response.status_code == 200

        prompt = response.json()
        assert prompt["lyrics"] == update_data["lyrics"]
        assert prompt["language"] == "fr"

    def test_update_music_prompt_prompt_and_lyrics(self, client, universe_with_music_prompts):
        """Test mise à jour complète d'un prompt musique."""
        slug = universe_with_music_prompts["universe"]["slug"]

        update_data = {
            "prompt": "Nouveau prompt musical italien",
            "lyrics": "Nuove parole italiane per la musica"
        }

        response = client.patch(f"/api/universes/{slug}/music-prompts/fr", json=update_data)
        assert response.status_code == 200

        prompt = response.json()
        assert prompt["prompt"] == update_data["prompt"]
        assert prompt["lyrics"] == update_data["lyrics"]

    def test_delete_music_prompt(self, client, universe_with_music_prompts):
        """Test suppression d'un prompt musique."""
        slug = universe_with_music_prompts["universe"]["slug"]

        # Supprimer le prompt anglais
        response = client.delete(f"/api/universes/{slug}/music-prompts/en")
        assert response.status_code == 204

        # Vérifier qu'il n'existe plus
        response = client.get(f"/api/universes/{slug}/music-prompts/en")
        assert response.status_code == 404

        # Vérifier qu'il reste le français
        response = client.get(f"/api/universes/{slug}/music-prompts/fr")
        assert response.status_code == 200

    def test_music_prompt_validation_languages(self, client, test_universe):
        """Test validation des langues supportées."""
        slug = test_universe["slug"]

        # Langues valides
        valid_languages = ["fr", "en", "es", "it", "de"]

        for lang in valid_languages:
            data = {
                "language": lang,
                "prompt": f"prompt in {lang}",
                "lyrics": f"lyrics in {lang}"
            }
            response = client.post(f"/api/universes/{slug}/music-prompts", json=data)
            assert response.status_code == 201

        # Langue invalide
        invalid_data = {
            "language": "invalid",
            "prompt": "invalid language prompt",
            "lyrics": "invalid language lyrics"
        }
        response = client.post(f"/api/universes/{slug}/music-prompts", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_music_prompt_universe_not_found(self, client):
        """Test accès à un univers inexistant."""
        response = client.post("/api/universes/nonexistent/music-prompts", json={
            "language": "fr",
            "prompt": "test",
            "lyrics": "test"
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]