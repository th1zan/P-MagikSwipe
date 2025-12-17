"""Integration tests for Replicate API calls.

These tests make actual API calls to Replicate and consume credits.
Only run these tests when explicitly needed for integration testing.

Requirements:
- Set REPLICATE_API_TOKEN environment variable
- Have sufficient credits
- Run with: pytest tests/test_replicate_integration.py -v --tb=short

WARNING: These tests cost money! Each generation call consumes credits.
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from main import app
from services.generation_service import generation_service


def wait_for_job_completion(client, job_id, timeout=600):  # 10 minutes timeout
    """
    Wait for a background job to complete and return the final job status.

    Args:
        client: TestClient instance
        job_id: Job ID to monitor
        timeout: Maximum wait time in seconds

    Returns:
        Job data dict when completed or failed

    Raises:
        TimeoutError: If job doesn't complete within timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        response = client.get(f"/api/jobs/{job_id}")
        if response.status_code == 200:
            job_data = response.json()
            status = job_data["status"]

            if status in ["completed", "failed"]:
                return job_data

            # Still running, wait a bit
            time.sleep(5)
        else:
            # Job not found or other error
            raise RuntimeError(f"Failed to get job status: {response.status_code} - {response.text}")

    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")


# Only run if REPLICATE_API_TOKEN is set
pytestmark = pytest.mark.skipif(
    not os.getenv("REPLICATE_API_TOKEN"),
    reason="REPLICATE_API_TOKEN not set - skipping integration tests"
)


@pytest.fixture
def client():
    """Test client."""
    with TestClient(app) as test_client:
        yield test_client


def test_replicate_connection():
    """Test that Replicate API is accessible."""
    assert generation_service.is_available, "Replicate API should be available"


@pytest.mark.skip(reason="LLM model needs updating - current model version not available")
def test_generate_concepts_integration(client):
    """Integration test for concept generation."""
    import uuid
    unique_slug = f"integration-test-{uuid.uuid4().hex[:8]}"

    # Create a test universe
    response = client.post("/api/universes", json={
        "name": "Integration Test Universe",
        "slug": unique_slug
    })
    assert response.status_code == 201
    universe = response.json()

    # Generate concepts
    response = client.post(f"/api/generate/{universe['slug']}/concepts", json={
        "theme": "magical forest adventure",
        "count": 3,
        "language": "en"
    })
    assert response.status_code == 200

    data = response.json()
    assert "concepts" in data
    assert "translations" in data
    assert len(data["concepts"]) == 3
    assert isinstance(data["concepts"], list)
    assert all(isinstance(c, str) for c in data["concepts"])


def test_generate_music_integration(client):
    """Integration test for music generation."""
    import uuid
    unique_slug = f"music-integration-{uuid.uuid4().hex[:8]}"

    # Create a test universe
    response = client.post("/api/universes", json={
        "name": "Music Integration Test",
        "slug": unique_slug
    })
    assert response.status_code == 201
    universe = response.json()

    # Generate music
    response = client.post(f"/api/generate/{universe['slug']}/music", json={
        "language": "fr",
        "style": "happy children's music"
    })
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "type" in data
    assert data["type"] == "generate_music"

    # Wait for job completion to verify Replicate API call
    job_id = data["id"]
    completed_job = wait_for_job_completion(client, job_id, timeout=300)  # 5 minutes for music
    assert completed_job["status"] == "completed", f"Music generation failed: {completed_job.get('error', 'Unknown error')}"


def test_generate_images_integration(client):
    """Integration test for image generation."""
    import uuid
    unique_slug = f"images-integration-{uuid.uuid4().hex[:8]}"

    # Create a test universe
    response = client.post("/api/universes", json={
        "name": "Images Integration Test",
        "slug": unique_slug
    })
    assert response.status_code == 201
    universe = response.json()

    # Create an asset
    response = client.post(f"/api/universes/{universe['slug']}/assets", json={
        "display_name": "Test Character",
        "sort_order": 1
    })
    assert response.status_code == 201

    # Generate images
    response = client.post(f"/api/generate/{universe['slug']}/images", json={})
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "type" in data
    assert data["type"] == "generate_images"

    # Wait for job completion to verify Replicate API call
    job_id = data["id"]
    completed_job = wait_for_job_completion(client, job_id, timeout=600)  # 10 minutes for images
    assert completed_job["status"] == "completed", f"Image generation failed: {completed_job.get('error', 'Unknown error')}"


def test_full_generation_pipeline_integration(client):
    """Integration test for complete universe generation pipeline."""
    import uuid
    unique_slug = f"full-pipeline-{uuid.uuid4().hex[:8]}"

    # Create a test universe
    response = client.post("/api/universes", json={
        "name": "Full Pipeline Integration Test",
        "slug": unique_slug
    })
    assert response.status_code == 201
    universe = response.json()

    # Generate everything
    response = client.post(f"/api/generate/{universe['slug']}/all", json={
        "theme": "space adventure",
        "count": 2,
        "generate_videos": False,  # Skip videos to save credits
        "generate_music": True
    })
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "type" in data
    assert data["type"] == "generate_all"

    # Wait for job completion to verify Replicate API calls
    job_id = data["id"]
    completed_job = wait_for_job_completion(client, job_id, timeout=900)  # 15 minutes for full pipeline
    assert completed_job["status"] == "completed", f"Full generation failed: {completed_job.get('error', 'Unknown error')}"


def test_replicate_environment():
    """Verify Replicate API environment is properly configured."""
    from config import settings
    assert settings.REPLICATE_API_TOKEN, "REPLICATE_API_TOKEN not configured"

    import replicate
    try:
        # Test basic API connectivity by listing models
        models_iter = replicate.models.list()
        models = []
        for i, model in enumerate(models_iter):
            models.append(model)
            if i >= 4:  # Get first 5 models
                break
        assert len(models) > 0, "Cannot connect to Replicate API"
        print(f"✅ Replicate API connected - found at least {len(models)} models")
    except Exception as e:
        pytest.fail(f"Replicate API connectivity failed: {e}")


def test_replicate_models_available():
    """Test that configured models are available."""
    from services.generation_service import MODELS

    import replicate
    for model_type, model_id in MODELS.items():
        try:
            # Extract model name (remove version if present)
            model_name = model_id.split(':')[0]
            model = replicate.models.get(model_name)
            assert model is not None, f"Model {model_name} not found"
            print(f"✅ Model {model_name} ({model_type}) is available")
        except Exception as e:
            pytest.fail(f"Model {model_name} ({model_type}) not accessible: {e}")


if __name__ == "__main__":
    print("⚠️  WARNING: These tests make real API calls and consume credits!")
    print("Make sure you have sufficient Replicate credits before running.")
    print("Press Enter to continue or Ctrl+C to abort...")

    try:
        input()
    except KeyboardInterrupt:
        print("Aborted.")
        exit(1)

    pytest.main([__file__, "-v"])