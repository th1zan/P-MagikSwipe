from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
import os
from projet.generators import generate_image, generate_video, generate_theme_music
from deep_translator import GoogleTranslator

router = APIRouter()
STORAGE_PATH = "/app/storage"

def generate_all(universe: str):
    theme = universe.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        return
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    words = data["words"]
    images = data.get("images", [])
    videos = data.get("videos", [])
    music = data.get("music", "")
    
    # Generate images
    for i, word in enumerate(words):
        prompt = images[i] if i < len(images) else None
        generate_image(word, theme, i, prompt)
    
    # Generate videos
    for i, word in enumerate(words):
        img_path = f"{STORAGE_PATH}/univers/{theme}/{i:02d}_{word.replace(' ', '_')}.png"
        if os.path.exists(img_path):
            motion_prompt = videos[i] if i < len(videos) else None
            generate_video(img_path, word, theme, i, motion_prompt)
    
    # Generate music
    lyrics = data.get("lyrics", "")
    generate_theme_music(theme, universe, music, lyrics)

@router.post("/generate/{universe}/images")
def generate_images(universe: str, background_tasks: BackgroundTasks):
    theme = universe.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    words = data["words"]
    images = data.get("images", [])
    
    for i, word in enumerate(words):
        prompt = images[i] if i < len(images) else None
        generate_image(word, theme, i, prompt)
    
    return {"message": "Images generated"}

@router.post("/generate/{universe}/videos")
def generate_videos(universe: str):
    theme = universe.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    words = data["words"]
    videos = data.get("videos", [])
    
    for i, word in enumerate(words):
        img_path = f"{STORAGE_PATH}/univers/{theme}/{i:02d}_{word.replace(' ', '_')}.png"
        if os.path.exists(img_path):
            motion_prompt = videos[i] if i < len(videos) else None
            generate_video(img_path, word, theme, i, motion_prompt)

    return {"message": "Videos generated"}

@router.post("/generate/{universe}/music/{lang}")
def generate_music_lang(universe: str, lang: str):
    theme = universe.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    with open(data_path, 'r') as f:
        data = json.load(f)
    theme_name = data.get("theme", universe)
    music_translations = data.get("music_translations", {})
    if lang not in music_translations:
        music_translations[lang] = {"lyrics": "", "prompt": ""}
    lyrics = music_translations[lang].get("lyrics", "")
    prompt = music_translations[lang].get("prompt", "")
    # Generate music for this lang
    generate_theme_music(theme, theme_name, music_prompt=prompt, lyrics=lyrics if lyrics else None, languages=[lang])
    return {"message": f"Music for {lang} generated"}

@router.post("/generate/{universe}/music-prompts")
def generate_music_prompts(universe: str):
    theme = universe.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")

    # Load default prompts
    defaults_path = os.path.join(STORAGE_PATH, "default_prompts.json")
    if not os.path.exists(defaults_path):
        raise HTTPException(status_code=404, detail="Default prompts not found")

    with open(defaults_path, 'r') as f:
        defaults = json.load(f)

    default_music_prompt = defaults.get("music", "")
    if not default_music_prompt:
        raise HTTPException(status_code=400, detail="No default music prompt found")

    # Load current data
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Update prompts for all languages
    music_translations = data.get("music_translations", {})
    for lang in ["fr", "en", "es", "it", "de"]:
        if lang not in music_translations:
            music_translations[lang] = {"lyrics": "", "prompt": ""}
        # Replace {theme} placeholder with actual theme
        theme_name = data.get("theme", universe)
        music_translations[lang]["prompt"] = default_music_prompt.replace("{theme}", theme_name)

    data["music_translations"] = music_translations

    # Save updated data
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

    return {"message": "Music prompts generated from default"}

@router.post("/generate/{universe}/lyrics")
def generate_lyrics(universe: str, lyrics_data: dict):
    custom_lyrics = lyrics_data.get("lyrics", "").strip()
    if not custom_lyrics:
        raise HTTPException(status_code=400, detail="Lyrics required")

    theme = universe.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")

    # Load current data
    with open(data_path, 'r') as f:
        data = json.load(f)

    music_translations = data.get("music_translations", {})

    # Set French lyrics
    if "fr" not in music_translations:
        music_translations["fr"] = {"lyrics": "", "prompt": ""}
    music_translations["fr"]["lyrics"] = custom_lyrics

    # Translate to other languages
    for lang in ["en", "es", "it", "de"]:
        if lang not in music_translations:
            music_translations[lang] = {"lyrics": "", "prompt": ""}
        try:
            translated_lyrics = GoogleTranslator(source='fr', target=lang).translate(custom_lyrics)
            music_translations[lang]["lyrics"] = translated_lyrics
        except Exception as e:
            # If translation fails, keep original French lyrics
            music_translations[lang]["lyrics"] = custom_lyrics

    data["music_translations"] = music_translations

    # Save updated data
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

    return {"message": "Lyrics generated and translated"}

@router.post("/generate/{universe}/lyrics/{lang}")
def regenerate_lyrics_lang(universe: str, lang: str):
    theme = universe.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")

    # Load current data
    with open(data_path, 'r') as f:
        data = json.load(f)

    music_translations = data.get("music_translations", {})

    # Get French lyrics as base
    french_lyrics = ""
    if "fr" in music_translations and music_translations["fr"].get("lyrics"):
        french_lyrics = music_translations["fr"]["lyrics"]
    else:
        raise HTTPException(status_code=400, detail="No French lyrics found to regenerate from")

    if lang == "fr":
        # Regenerate French lyrics using AI (simplified - just keep current for now)
        music_translations[lang]["lyrics"] = french_lyrics
    else:
        # Translate from French
        try:
            translated_lyrics = GoogleTranslator(source='fr', target=lang).translate(french_lyrics)
            music_translations[lang]["lyrics"] = translated_lyrics
        except Exception as e:
            music_translations[lang]["lyrics"] = french_lyrics

    data["music_translations"] = music_translations

    # Save updated data
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

    return {"message": f"Lyrics regenerated for {lang}"}

@router.post("/generate/{universe}/music-all")
def generate_all_music(universe: str):
    theme = universe.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")

    with open(data_path, 'r') as f:
        data = json.load(f)

    theme_name = data.get("theme", universe)
    music_translations = data.get("music_translations", {})

    # Generate music sequentially for all languages
    for lang in ["fr", "en", "es", "it", "de"]:
        if lang in music_translations:
            lyrics = music_translations[lang].get("lyrics", "")
            prompt = music_translations[lang].get("prompt", "")
            try:
                generate_theme_music(theme, theme_name, music_prompt=prompt, lyrics=lyrics if lyrics else None, languages=[lang])
            except Exception as e:
                print(f"Error generating music for {lang}: {e}")
                # Continue with next language

    return {"message": "Music generation started for all languages"}

@router.post("/generate/{universe}/all")
def generate_all_endpoint(universe: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_all, universe)
    return {"message": "Generation started in background"}

@router.post("/generate/{universe}/item/{index}/video")
def generate_single_video(universe: str, index: int):
    theme = universe.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    words = data["words"]
    videos = data.get("videos", [])
    if index >= len(words):
        raise HTTPException(status_code=400, detail="Invalid index")
    word = words[index]
    img_path = f"{STORAGE_PATH}/univers/{theme}/{index:02d}_{word.replace(' ', '_')}.png"
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Image not found")
    motion_prompt = videos[index] if index < len(videos) else None
    generate_video(img_path, word, theme, index, motion_prompt)
    
    return {"message": f"Video for {word} generated"}

@router.post("/generate/{universe}/thumbnail")
def regenerate_thumbnail(universe: str):
    theme = universe.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data not found")
    with open(data_path, 'r') as f:
        universe_data = json.load(f)
    if 'items' not in universe_data or not universe_data['items']:
        raise HTTPException(status_code=400, detail="No items found")
    universe_data["thumbnail"] = universe_data['items'][0]['image']
    with open(data_path, 'w') as f:
        json.dump(universe_data, f, indent=2)
    return {"message": f"Thumbnail set for {universe}"}

@router.get("/status/{task_id}")
def get_status(task_id: str):
    # Placeholder for task status
    return {"status": "completed", "task_id": task_id}