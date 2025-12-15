from fastapi import APIRouter, HTTPException
import json
import yaml
import os
from pathlib import Path
from deep_translator import GoogleTranslator
from projet.translation_generator import generate_translations

router = APIRouter()

STORAGE_PATH = "/app/storage"

@router.get("/default-prompts")
async def get_default_prompts():
    try:
        with open(f"{STORAGE_PATH}/prompts/defaults.yaml", 'r') as f:
            data = yaml.safe_load(f)
            return data.get("defaults", {})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Default prompts not found")

@router.post("/default-prompts")
async def save_default_prompts(data: dict):
    try:
        # Load existing
        try:
            with open(f"{STORAGE_PATH}/prompts/defaults.yaml", 'r') as f:
                existing = yaml.safe_load(f)
        except:
            existing = {}
        # Update defaults
        existing["defaults"] = data
        with open(f"{STORAGE_PATH}/prompts/defaults.yaml", 'w') as f:
            yaml.dump(existing, f, default_flow_style=False)
        return {"message": "Defaults saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def load_defaults():
    try:
        with open(f"{STORAGE_PATH}/prompts/defaults.yaml", 'r') as f:
            data = yaml.safe_load(f)
            return data.get("defaults", {})
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

@router.post("/generate/lyrics")
async def generate_lyrics_endpoint(data: dict):
    lyrics = data.get("lyrics", "")
    universe = data.get("universe", "")
    prompt = data.get("prompt", "")  # Prompt français à traduire aussi
    
    if not lyrics or not universe:
        raise HTTPException(status_code=400, detail="Lyrics and universe required")

    # Update data.json for universe
    data_path = os.path.join(STORAGE_PATH, "univers", universe, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    
    with open(data_path, 'r') as f:
        universe_data = json.load(f)
    
    # Récupérer ou initialiser music_translations avec le bon format
    music_translations = universe_data.get("music_translations", {})
    
    # S'assurer que fr existe avec le bon format
    if not isinstance(music_translations.get("fr"), dict):
        music_translations["fr"] = {"lyrics": lyrics, "prompt": prompt}
    else:
        music_translations["fr"]["lyrics"] = lyrics
        if prompt:
            music_translations["fr"]["prompt"] = prompt
    
    # Traduire vers les autres langues
    for lang in ["en", "es", "it", "de"]:
        try:
            translated_lyrics = GoogleTranslator(source='fr', target=lang).translate(lyrics)
        except:
            translated_lyrics = lyrics  # Fallback
        
        # Traduire le prompt aussi si présent
        translated_prompt = ""
        if prompt:
            try:
                translated_prompt = GoogleTranslator(source='fr', target=lang).translate(prompt)
            except:
                translated_prompt = prompt  # Fallback
        
        # S'assurer que la langue existe avec le bon format
        if not isinstance(music_translations.get(lang), dict):
            music_translations[lang] = {"lyrics": translated_lyrics, "prompt": translated_prompt}
        else:
            music_translations[lang]["lyrics"] = translated_lyrics
            if translated_prompt:
                music_translations[lang]["prompt"] = translated_prompt
    
    universe_data["music_translations"] = music_translations
    
    with open(data_path, 'w') as f:
        json.dump(universe_data, f, indent=2, ensure_ascii=False)

    return {"message": "Lyrics and prompts translated", "translations": music_translations}


@router.post("/translate-text")
async def translate_text_endpoint(data: dict):
    """Traduit un texte simple d'une langue à une autre"""
    text = data.get("text", "")
    source = data.get("source", "fr")
    target = data.get("target", "en")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text required")
    
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return {"translated": translated, "source": source, "target": target}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")