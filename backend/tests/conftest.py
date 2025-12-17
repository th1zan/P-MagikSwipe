"""Configuration pytest pour les tests de l'API MagikSwipe."""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="function")
def client():
    """Client FastAPI de test."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_universe(client):
    """Fixture créant un univers de test avec slug unique."""
    import uuid
    unique_slug = f"test-universe-{uuid.uuid4().hex[:8]}"

    response = client.post("/api/universes", json={
        "name": "Test Universe",
        "slug": unique_slug,
        "is_public": True
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def private_universe(client):
    """Fixture créant un univers privé de test avec slug unique."""
    import uuid
    unique_slug = f"private-test-{uuid.uuid4().hex[:8]}"

    response = client.post("/api/universes", json={
        "name": "Private Test Universe",
        "slug": unique_slug,
        "is_public": False
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def universe_with_music_prompts(client, test_universe):
    """Fixture créant un univers avec des prompts musique."""
    universe_slug = test_universe["slug"]

    # Créer quelques prompts musique
    prompts_data = [
        {"language": "fr", "prompt": "musique douce enfantine", "lyrics": "Paroles en français"},
        {"language": "en", "prompt": "soft children music", "lyrics": "English lyrics"}
    ]

    created_prompts = []
    for prompt_data in prompts_data:
        response = client.post(f"/api/universes/{universe_slug}/music-prompts", json=prompt_data)
        assert response.status_code == 201
        created_prompts.append(response.json())

    return {"universe": test_universe, "prompts": created_prompts}