import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_list_universes():
    response = requests.get(f"{BASE_URL}/universes")
    assert response.status_code == 200
    print("List universes: OK")

# def test_create_universe():
#     data = {"name": "Test Universe"}
#     response = requests.post(f"{BASE_URL}/universes", json=data)
#     assert response.status_code == 200
#     print("Create universe: OK")

# def test_get_prompts():
#     response = requests.get(f"{BASE_URL}/universes/Test%20Universe/prompts")
#     assert response.status_code == 200
#     print("Get prompts: OK")

# def test_save_prompts():
#     prompts = {"theme": "Test Universe", "description": "Test", "words": ["test"], "images": ["test image"], "videos": ["test video"], "music": "test music"}
#     response = requests.post(f"{BASE_URL}/universes/Test%20Universe/prompts", json=prompts)
#     assert response.status_code == 200
#     print("Save prompts: OK")

# def test_generate_images():
#     response = requests.post(f"{BASE_URL}/generate/Test%20Universe/images")
#     assert response.status_code == 200
#     print("Generate images: OK")

# Add more tests as needed

if __name__ == "__main__":
    test_list_universes()
    # test_create_universe()
    # test_get_prompts()
    # test_save_prompts()
    # test_generate_images()
    print("Basic test passed!")