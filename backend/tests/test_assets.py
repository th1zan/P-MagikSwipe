"""Tests CRUD pour les assets."""

import pytest


class TestAssetsCRUD:
    """Tests CRUD complets pour les assets."""

    def test_create_asset_basic(self, client, test_universe):
        """Test création d'un asset basique."""
        slug = test_universe["slug"]

        data = {
            "display_name": "Test Asset",
            "sort_order": 1
        }

        response = client.post(f"/api/universes/{slug}/assets", json=data)
        assert response.status_code == 201

        asset = response.json()
        assert asset["display_name"] == data["display_name"]
        assert asset["sort_order"] == data["sort_order"]
        assert "id" in asset
        assert "created_at" in asset

    def test_create_asset_with_translations(self, client, test_universe):
        """Test création d'un asset avec traductions."""
        slug = test_universe["slug"]

        data = {
            "display_name": "Asset with Translations",
            "sort_order": 2,
            "translations": {
                "en": "Asset with Translations EN",
                "es": "Activo con Traducciones",
                "fr": "Asset avec Traductions"
            }
        }

        response = client.post(f"/api/universes/{slug}/assets", json=data)
        assert response.status_code == 201

        asset = response.json()
        assert asset["display_name"] == data["display_name"]
        assert len(asset["translations"]) == 3

        # Vérifier les traductions
        translation_dict = {t["language"]: t["display_name"] for t in asset["translations"]}
        for lang, expected_name in data["translations"].items():
            assert translation_dict[lang] == expected_name

    def test_list_assets(self, client, test_universe):
        """Test listing des assets d'un univers."""
        slug = test_universe["slug"]

        # Créer quelques assets
        assets_data = [
            {"display_name": "Asset 1", "sort_order": 1},
            {"display_name": "Asset 2", "sort_order": 2},
            {"display_name": "Asset 3", "sort_order": 3}
        ]

        for asset_data in assets_data:
            client.post(f"/api/universes/{slug}/assets", json=asset_data)

        # Lister les assets
        response = client.get(f"/api/universes/{slug}/assets")
        assert response.status_code == 200

        assets = response.json()
        assert len(assets) == 3

        # Vérifier l'ordre de tri
        display_names = [a["display_name"] for a in assets]
        assert display_names == ["Asset 1", "Asset 2", "Asset 3"]

    def test_get_specific_asset(self, client, test_universe):
        """Test récupération d'un asset spécifique."""
        slug = test_universe["slug"]

        # Créer un asset
        create_response = client.post(f"/api/universes/{slug}/assets", json={
            "display_name": "Specific Asset",
            "sort_order": 1
        })
        asset_id = create_response.json()["id"]

        # Récupérer cet asset
        response = client.get(f"/api/universes/{slug}/assets/{asset_id}")
        assert response.status_code == 200

        asset = response.json()
        assert asset["id"] == asset_id
        assert asset["display_name"] == "Specific Asset"
        assert "translations" in asset
        assert "created_at" in asset

    def test_get_asset_not_found(self, client, test_universe):
        """Test récupération d'un asset inexistant."""
        slug = test_universe["slug"]

        response = client.get(f"/api/universes/{slug}/assets/invalid-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_asset_basic(self, client, test_universe):
        """Test mise à jour basique d'un asset."""
        slug = test_universe["slug"]

        # Créer un asset
        create_response = client.post(f"/api/universes/{slug}/assets", json={
            "display_name": "Original Asset",
            "sort_order": 1
        })
        asset_id = create_response.json()["id"]

        # Mettre à jour
        update_data = {
            "display_name": "Updated Asset Name",
            "sort_order": 5
        }

        response = client.patch(f"/api/universes/{slug}/assets/{asset_id}", json=update_data)
        assert response.status_code == 200

        asset = response.json()
        assert asset["display_name"] == update_data["display_name"]
        assert asset["sort_order"] == update_data["sort_order"]

    def test_update_asset_translations(self, client, test_universe):
        """Test mise à jour des traductions d'un asset."""
        slug = test_universe["slug"]

        # Créer un asset avec traductions
        create_response = client.post(f"/api/universes/{slug}/assets", json={
            "display_name": "Asset with Translations",
            "translations": {"en": "Original EN", "fr": "Original FR"}
        })
        asset_id = create_response.json()["id"]

        # Mettre à jour les traductions
        new_translations = {
            "en": "Updated EN",
            "es": "Nuevo ES",
            "de": "Neu DE"
        }

        response = client.patch(f"/api/universes/{slug}/assets/{asset_id}", json={
            "translations": new_translations
        })
        assert response.status_code == 200

        asset = response.json()
        assert len(asset["translations"]) == 3

        translation_dict = {t["language"]: t["display_name"] for t in asset["translations"]}
        for lang, expected_name in new_translations.items():
            assert translation_dict[lang] == expected_name

    def test_delete_asset(self, client, test_universe):
        """Test suppression d'un asset."""
        slug = test_universe["slug"]

        # Créer un asset
        create_response = client.post(f"/api/universes/{slug}/assets", json={
            "display_name": "Asset to Delete",
            "sort_order": 1
        })
        asset_id = create_response.json()["id"]

        # Supprimer l'asset
        response = client.delete(f"/api/universes/{slug}/assets/{asset_id}")
        assert response.status_code == 204

        # Vérifier qu'il n'existe plus
        response = client.get(f"/api/universes/{slug}/assets/{asset_id}")
        assert response.status_code == 404

    def test_create_asset_universe_not_found(self, client):
        """Test création d'asset dans un univers inexistant."""
        response = client.post("/api/universes/nonexistent/assets", json={
            "display_name": "Test Asset",
            "sort_order": 1
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]