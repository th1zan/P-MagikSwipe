from fastapi import APIRouter, HTTPException
import json
import os
from projet.translation_generator import generate_translations

router = APIRouter()

STORAGE_PATH = "/app/storage"

@router.get("/default-prompts")
async def get_default_prompts():
    try:
        with open(f"{STORAGE_PATH}/default_prompts.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Default prompts not found")

@router.post("/default-prompts")
async def save_default_prompts(data: dict):
    try:
        with open(f"{STORAGE_PATH}/default_prompts.json", 'w') as f:
            json.dump(data, f, indent=2)
        return {"message": "Defaults saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def load_defaults():
    try:
        with open(f"{STORAGE_PATH}/default_prompts.json", 'r') as f:
            return json.load(f)
    except:
        return {}

@router.post("/generate-objects")
async def generate_objects(data: dict):
    theme = data.get("theme", "")
    prompt = data.get("prompt", "")
    if not theme:
        raise HTTPException(status_code=400, detail="Theme required")
    defaults = load_defaults()
    if not prompt:
        prompt = defaults.get("objects", "Generate 10 simple objects for children related to the theme.")
    # Generate objects using IA
    full_prompt = f"{prompt} Generate exactly 10 simple words for children aged 3-7 related to the theme '{theme}'."
    try:
        result = generate_translations(theme, debug=False)
        objects = result["words"]
        return {"objects": objects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-image-prompts")
async def generate_image_prompts(data: dict):
    objects = data.get("objects", [])
    default_prompt = data.get("default_prompt", "")
    if not default_prompt:
        defaults = load_defaults()
        default_prompt = defaults.get("images", "A beautiful, colorful illustration of {object} in a magical setting, perfect for children, vibrant and enchanting.")
    prompts = []
    for obj in objects:
        prompt = default_prompt.replace("{object}", obj)
        prompts.append(prompt)
    return {"image_prompts": prompts}

@router.post("/generate-video-prompts")
async def generate_video_prompts(data: dict):
    image_prompts = data.get("image_prompts", [])
    default_prompt = data.get("default_prompt", "")
    if not default_prompt:
        defaults = load_defaults()
        default_prompt = defaults.get("videos", "A short animated video of {object} moving happily and magically, joyful and child-friendly.")
    prompts = []
    for img_prompt in image_prompts:
        # Extract object from image prompt (simple heuristic)
        obj = img_prompt.split(" of ")[1].split(" ")[0] if " of " in img_prompt else "object"
        prompt = default_prompt.replace("{object}", obj)
        prompts.append(prompt)
    return {"video_prompts": prompts}

@router.post("/generate-music-prompt")
async def generate_music_prompt(data: dict):
    theme = data.get("theme", "")
    if not theme:
        raise HTTPException(status_code=400, detail="Theme required")
    defaults = load_defaults()
    prompt = defaults.get("music", "Joyful children's song about {theme}, with bouncy melody and fun lyrics.").replace("{theme}", theme)
    return {"music_prompt": prompt}