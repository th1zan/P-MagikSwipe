"""Tests CRUD pour les univers (y compris visibilité et traductions)."""

import pytest


class TestUniverseCRUD:
    """Tests de base CRUD pour les univers."""

    def test_list_universes(self, client):
        """Test listing des univers."""
        response = client.get("/api/universes")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_create_universe_public(self, client):
        """Test création d'un univers public."""
        import uuid
        unique_slug = f"public-test-{uuid.uuid4().hex[:8]}"

        data = {
            "name": "Public Test Universe",
            "slug": unique_slug,
            "is_public": True,
            "background_color": "#ff6b6b"
        }

        response = client.post("/api/universes", json=data)
        assert response.status_code == 201

        universe = response.json()
        assert universe["name"] == data["name"]
        assert universe["slug"] == unique_slug
        assert universe["is_public"] == True
        assert universe["background_color"] == data["background_color"]
        assert "id" in universe
        assert "created_at" in universe

    def test_create_universe_private(self, client):
        """Test création d'un univers privé."""
        import uuid
        unique_slug = f"private-test-{uuid.uuid4().hex[:8]}"

        data = {
            "name": "Private Test Universe",
            "slug": unique_slug,
            "is_public": False
        }

        response = client.post("/api/universes", json=data)
        assert response.status_code == 201

        universe = response.json()
        assert universe["name"] == data["name"]
        assert universe["slug"] == unique_slug
        assert universe["is_public"] == False

    def test_create_universe_duplicate_slug(self, client):
        """Test création avec slug déjà existant."""
        # Créer le premier univers
        data = {"name": "Original Universe", "slug": "duplicate-test"}
        client.post("/api/universes", json=data)

        # Tenter de créer un deuxième avec le même slug
        response = client.post("/api/universes", json=data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_universe_by_slug(self, client, test_universe):
        """Test récupération d'un univers par slug."""
        slug = test_universe["slug"]
        response = client.get(f"/api/universes/{slug}")
        assert response.status_code == 200

        universe = response.json()
        assert universe["slug"] == slug
        assert "assets" in universe
        assert "translations" in universe
        assert "music_prompts" in universe

    def test_get_universe_not_found(self, client):
        """Test récupération d'un univers inexistant."""
        response = client.get("/api/universes/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUniverseVisibility:
    """Tests de gestion de la visibilité des univers."""

    def test_universe_visibility_filtering_public(self, client, test_universe, private_universe):
        """Test filtrage des univers publics."""
        response = client.get("/api/universes?is_public=true")
        assert response.status_code == 200

        universes = response.json()["items"]
        # Devrait inclure test_universe (public) mais pas private_universe
        public_slugs = [u["slug"] for u in universes]
        assert test_universe["slug"] in public_slugs
        assert private_universe["slug"] not in public_slugs

        # Vérifier que tous sont publics
        for universe in universes:
            assert universe["is_public"] == True

    def test_universe_visibility_filtering_private(self, client, test_universe, private_universe):
        """Test filtrage des univers privés."""
        response = client.get("/api/universes?is_public=false")
        assert response.status_code == 200

        universes = response.json()["items"]
        # Devrait inclure private_universe mais pas test_universe
        private_slugs = [u["slug"] for u in universes]
        assert private_universe["slug"] in private_slugs
        assert test_universe["slug"] not in private_slugs

        # Vérifier que tous sont privés
        for universe in universes:
            assert universe["is_public"] == False

    def test_toggle_universe_visibility_public_to_private(self, client, test_universe):
        """Test changement de visibilité public → privé."""
        slug = test_universe["slug"]

        # Changer en privé
        response = client.patch(f"/api/universes/{slug}", json={"is_public": False})
        assert response.status_code == 200
        assert response.json()["is_public"] == False

        # Vérifier que c'est maintenant privé
        response = client.get(f"/api/universes/{slug}")
        assert response.json()["is_public"] == False

    def test_toggle_universe_visibility_private_to_public(self, client, private_universe):
        """Test changement de visibilité privé → public."""
        slug = private_universe["slug"]

        # Changer en public
        response = client.patch(f"/api/universes/{slug}", json={"is_public": True})
        assert response.status_code == 200
        assert response.json()["is_public"] == True

        # Vérifier que c'est maintenant public
        response = client.get(f"/api/universes/{slug}")
        assert response.json()["is_public"] == True


class TestUniverseTranslations:
    """Tests de gestion des traductions d'univers."""

    def test_add_universe_translations(self, client, test_universe):
        """Test ajout de traductions à un univers."""
        slug = test_universe["slug"]

        translations = {
            "en": "English Universe Name",
            "es": "Nombre del Universo en Español",
            "fr": "Nom de l'Univers en Français"
        }

        response = client.patch(f"/api/universes/{slug}", json={"translations": translations})
        assert response.status_code == 200

        # Vérifier les traductions
        universe = response.json()
        assert len(universe["translations"]) == 3

        translation_dict = {t["language"]: t["name"] for t in universe["translations"]}
        for lang, expected_name in translations.items():
            assert translation_dict[lang] == expected_name

    def test_update_universe_basic_fields(self, client, test_universe):
        """Test mise à jour des champs de base."""
        slug = test_universe["slug"]

        updates = {
            "name": "Updated Universe Name",
            "background_color": "#4ecdc4",
            "background_music": "test-music.mp3"
        }

        response = client.patch(f"/api/universes/{slug}", json=updates)
        assert response.status_code == 200

        universe = response.json()
        assert universe["name"] == updates["name"]
        assert universe["background_color"] == updates["background_color"]
        assert universe["background_music"] == updates["background_music"]

    def test_delete_universe(self, client, test_universe):
        """Test suppression d'un univers."""
        slug = test_universe["slug"]

        # Supprimer
        response = client.delete(f"/api/universes/{slug}")
        assert response.status_code == 204

        # Vérifier qu'il n'existe plus
        response = client.get(f"/api/universes/{slug}")
        assert response.status_code == 404