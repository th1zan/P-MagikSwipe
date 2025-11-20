from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
import shutil
from prompts import generate_base_prompts

class UniverseCreate(BaseModel):
    name: str
    theme: str = ""

router = APIRouter()
STORAGE_PATH = "/app/storage"

@router.get("/universes")
def list_universes():
    index_path = os.path.join(STORAGE_PATH, "index.json")
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return json.load(f)
    return []

@router.post("/universes")
def create_universe(universe: UniverseCreate):
    name = universe.name
    theme_folder = name.lower().replace(' ', '_')
    prompt_theme = universe.theme if universe.theme else name
    universe_dir = os.path.join(STORAGE_PATH, "univers", theme_folder)
    os.makedirs(universe_dir, exist_ok=True)

    # Generate base prompts
    prompts = generate_base_prompts(prompt_theme)
    prompts_path = os.path.join(universe_dir, "prompts.json")
    with open(prompts_path, 'w') as f:
        json.dump(prompts, f, indent=2)

    # Create data.json for viewer
    words = prompts["words"]
    items = []
    for i, word in enumerate(words):
        item = {
            "image": f"{i:02d}_{word.replace(' ', '_')}.png",
            "title": word,
            "video": f"{i:02d}_{word.replace(' ', '_')}_silent.mp4"
        }
        items.append(item)
    data = {"items": items}
    data_path = os.path.join(universe_dir, "data.json")
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

    # Update index.json
    index_path = os.path.join(STORAGE_PATH, "index.json")
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            themes = json.load(f)
    else:
        themes = []
    if not any(t['folder'] == theme_folder for t in themes):
        themes.append({"name": name, "folder": theme_folder})
        with open(index_path, 'w') as f:
            json.dump(themes, f, indent=2)

    return {"message": f"Univers '{name}' créé"}

@router.get("/universes/{name}/prompts")
def get_prompts(name: str):
    theme = name.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")
    with open(prompts_path, 'r') as f:
        return json.load(f)

@router.post("/universes/{name}/prompts")
def save_prompts(name: str, prompts: dict):
    theme = name.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    with open(prompts_path, 'w') as f:
        json.dump(prompts, f, indent=2)
    return {"message": "Prompts saved"}

@router.post("/universes/{name}/regenerate-prompts")
def regenerate_prompts(name: str):
    theme = name.lower().replace(' ', '_')
    universe_dir = os.path.join(STORAGE_PATH, "univers", theme)
    if not os.path.exists(universe_dir):
        raise HTTPException(status_code=404, detail="Universe not found")
    prompts = generate_base_prompts(name)
    prompts_path = os.path.join(universe_dir, "prompts.json")
    with open(prompts_path, 'w') as f:
        json.dump(prompts, f, indent=2)
    return {"message": "Prompts regenerated"}

@router.delete("/universes/{name}")
def delete_universe(name: str):
    theme = name.lower().replace(' ', '_')
    universe_dir = os.path.join(STORAGE_PATH, "univers", theme)
    if os.path.exists(universe_dir):
        shutil.rmtree(universe_dir)
    
    # Update index.json
    index_path = os.path.join(STORAGE_PATH, "index.json")
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            themes = json.load(f)
        themes = [t for t in themes if t['folder'] != theme]
        with open(index_path, 'w') as f:
            json.dump(themes, f, indent=2)
    
    return {"message": f"Univers '{name}' supprimé"}