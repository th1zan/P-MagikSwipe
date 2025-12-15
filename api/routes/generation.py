from fastapi import APIRouter, HTTPException, BackgroundTasks
import yaml
import json
import os
from projet.generators import generate_image, generate_video, generate_theme_music
from deep_translator import GoogleTranslator
from services.storage_service import storage_service
from services.job_service import create_job

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
def generate_images(universe: str, background_tasks: BackgroundTasks, body: dict = None):
    theme = universe.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    words = data["words"]
    images = data.get("images", [])
    
    # Check if async mode requested
    if body and body.get("async"):
        def task():
            for i, word in enumerate(words):
                prompt = images[i] if i < len(images) else None
                generate_image(word, theme, i, prompt)
            return {"count": len(words), "status": "completed"}
        
        job_id = create_job(
            job_type="generate_images",
            universe=universe,
            task_fn=task,
            description=f"Generating {len(words)} images"
        )
        return {"job_id": job_id, "message": "Image generation started"}
    
    # Synchronous mode (legacy)
    for i, word in enumerate(words):
        prompt = images[i] if i < len(images) else None
        generate_image(word, theme, i, prompt)
    
    return {"message": "Images generated"}

@router.post("/generate/{universe}/videos")
def generate_videos(universe: str, body: dict = None):
    theme = universe.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    words = data["words"]
    videos = data.get("videos", [])
    
    # Check if async mode requested
    if body and body.get("async"):
        def task():
            for i, word in enumerate(words):
                img_path = f"{STORAGE_PATH}/univers/{theme}/{i:02d}_{word.replace(' ', '_')}.png"
                if os.path.exists(img_path):
                    motion_prompt = videos[i] if i < len(videos) else None
                    generate_video(img_path, word, theme, i, motion_prompt)
            return {"count": len(words), "status": "completed"}
        
        job_id = create_job(
            job_type="generate_videos",
            universe=universe,
            task_fn=task,
            description=f"Generating {len(words)} videos"
        )
        return {"job_id": job_id, "message": "Video generation started"}
    
    # Synchronous mode (legacy)
    for i, word in enumerate(words):
        img_path = f"{STORAGE_PATH}/univers/{theme}/{i:02d}_{word.replace(' ', '_')}.png"
        if os.path.exists(img_path):
            motion_prompt = videos[i] if i < len(videos) else None
            generate_video(img_path, word, theme, i, motion_prompt)

    return {"message": "Videos generated"}

@router.post("/generate/{universe}/music/{lang}")
def generate_music_lang(universe: str, lang: str, body: dict = None):
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
    
    # Check if async mode requested
    if body and body.get("async"):
        def task():
            generate_theme_music(theme, theme_name, music_prompt=prompt, lyrics=lyrics if lyrics else None, languages=[lang])
            return {"lang": lang, "status": "completed"}
        
        job_id = create_job(
            job_type="generate_music",
            universe=universe,
            task_fn=task,
            description=f"Generating music for {lang.upper()}"
        )
        return {"job_id": job_id, "message": "Music generation started"}
    
    # Synchronous mode (legacy)
    generate_theme_music(theme, theme_name, music_prompt=prompt, lyrics=lyrics if lyrics else None, languages=[lang])
    return {"message": f"Music for {lang} generated"}

@router.post("/generate/{universe}/music-prompts")
def generate_music_prompts(universe: str):
    theme = universe.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")

    # Load default prompts
    defaults_path = os.path.join(STORAGE_PATH, "prompts", "defaults.yaml")
    if not os.path.exists(defaults_path):
        raise HTTPException(status_code=404, detail="Default prompts not found")

    with open(defaults_path, 'r') as f:
        data = yaml.safe_load(f)
        defaults = data.get("defaults", {})

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
    if "fr" in music_translations and isinstance(music_translations["fr"], dict) and music_translations["fr"].get("lyrics"):
        french_lyrics = music_translations["fr"]["lyrics"]
    else:
        raise HTTPException(status_code=400, detail="No French lyrics found to regenerate from")

    # S'assurer que la langue existe avec le bon format
    if not isinstance(music_translations.get(lang), dict):
        music_translations[lang] = {"lyrics": "", "prompt": ""}

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
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {"message": f"Lyrics regenerated for {lang}", "lyrics": music_translations[lang]["lyrics"]}

@router.post("/universes/{universe}/lyrics/generate")
def generate_lyrics_ai(universe: str, lyrics_data: dict):
    """Generate lyrics using AI based on theme and words"""
    theme = universe.lower().replace(' ', '_')
    theme_name = lyrics_data.get("theme", universe)
    words = lyrics_data.get("words", [])
    
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    
    # Import the lyrics generation function
    from api.prompts import generate_lyrics as generate_lyrics_fn
    
    try:
        # Generate French lyrics
        lyrics = generate_lyrics_fn(theme_name, words)
        
        # Load and update data
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        music_translations = data.get("music_translations", {})
        if "fr" not in music_translations:
            music_translations["fr"] = {"lyrics": "", "prompt": ""}
        
        music_translations["fr"]["lyrics"] = lyrics
        data["music_translations"] = music_translations
        
        # Save updated data
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"lyrics": lyrics, "message": "Lyrics generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate lyrics: {str(e)}")

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

@router.post("/generate/{universe}/objects")
def generate_universe_objects(universe: str, data: dict):
    theme = universe.lower().replace(' ', '_')
    prompt = data.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")

    # Generate objects using AI
    from projet.translation_generator import generate_translations
    try:
        result = generate_translations(theme, debug=False)
        objects = result["words"]

        # Save to prompts.json
        prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
        if os.path.exists(prompts_path):
            with open(prompts_path, 'r') as f:
                prompts_data = json.load(f)
        else:
            prompts_data = {}

        prompts_data["words"] = objects
        with open(prompts_path, 'w') as f:
            json.dump(prompts_data, f, indent=2)

        return {"objects": objects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/universes/{universe}/translations/generate")
def generate_translations_endpoint(universe: str):
    theme = universe.lower().replace(' ', '_')

    # Load concepts from prompts.json
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")

    with open(prompts_path, 'r') as f:
        prompts_data = json.load(f)

    concepts = prompts_data.get("words", [])
    if not concepts:
        raise HTTPException(status_code=400, detail="No concepts found")

    # Load current data.json
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    translations = {}
    langs = ['en', 'es', 'it', 'de']

    # Translate each concept
    for lang in langs:
        translations[lang] = []
        for concept in concepts:
            try:
                translated = GoogleTranslator(source='fr', target=lang).translate(concept)
                translations[lang].append(translated)
            except Exception as e:
                # Fallback to original if translation fails
                translations[lang].append(concept)

    # French is the source, so copy original concepts
    translations['fr'] = concepts.copy()

    data["translations"] = translations

    # Save updated data
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

    return {"message": "Translations generated", "translations": translations}

@router.post("/universes/{universe}/images/prompts/generate")
def generate_image_prompts_endpoint(universe: str, data: dict):
    default_prompt = data.get("defaultPrompt", "")

    if not default_prompt:
        # Load from defaults
        defaults = storage_service.load_default_prompts()
        default_prompt = defaults.get("images", "A beautiful 3D illustration of {object}, child-friendly, colorful...")

    # Load objects
    objects = storage_service.load_objects(universe)
    if not objects:
        raise HTTPException(status_code=400, detail="No objects found")

    # Generate prompts
    image_prompts = storage_service.generate_prompts_for_objects(
        objects=objects,
        default_prompt=default_prompt
    )

    # Save prompts
    storage_service.update_prompts(
        identifier=universe,
        prompts=image_prompts,
        prompts_type="images"
    )

    return {"message": "Image prompts generated", "prompts": image_prompts}

@router.post("/universes/{universe}/videos/prompts/generate")
def generate_video_prompts_endpoint(universe: str, data: dict):
    default_prompt = data.get("defaultPrompt", "")

    if not default_prompt:
        # Load from defaults
        defaults = storage_service.load_default_prompts()
        default_prompt = defaults.get("videos", "A short animated video of {object}, smooth motion, child-friendly...")

    # Load objects
    objects = storage_service.load_objects(universe)
    if not objects:
        raise HTTPException(status_code=400, detail="No objects found")

    # Generate prompts
    video_prompts = storage_service.generate_prompts_for_objects(
        objects=objects,
        default_prompt=default_prompt
    )

    # Save prompts
    storage_service.update_prompts(
        identifier=universe,
        prompts=video_prompts,
        prompts_type="videos"
    )

    return {"message": "Video prompts generated", "prompts": video_prompts}

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

@router.post("/universes/{universe}/images/{index}/regenerate")
def regenerate_image(universe: str, index: int):
    theme = universe.lower().replace(' ', '_')

    # Load data.json for items
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data not found")

    with open(data_path, 'r') as f:
        data = json.load(f)

    items = data.get("items", [])
    if index >= len(items):
        raise HTTPException(status_code=400, detail="Invalid index")

    item = items[index]
    concept = item.get("title", "")

    # Load image prompt from prompts.json if exists
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    prompt = None
    if os.path.exists(prompts_path):
        with open(prompts_path, 'r') as f:
            prompts_data = json.load(f)
        image_prompts = prompts_data.get("images", [])
        prompt = image_prompts[index] if index < len(image_prompts) else None

    # Generate image
    generate_image(concept, theme, index, prompt)

    return {"message": f"Image for {concept} regenerated"}

@router.post("/universes/{universe}/videos/{index}/regenerate")
def regenerate_video(universe: str, index: int):
    theme = universe.lower().replace(' ', '_')

    # Load data.json for items
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data not found")

    with open(data_path, 'r') as f:
        data = json.load(f)

    items = data.get("items", [])
    if index >= len(items):
        raise HTTPException(status_code=400, detail="Invalid index")

    item = items[index]
    concept = item.get("title", "")

    # Load video prompt from prompts.json if exists
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    prompt = None
    if os.path.exists(prompts_path):
        with open(prompts_path, 'r') as f:
            prompts_data = json.load(f)
        video_prompts = prompts_data.get("videos", [])
        prompt = video_prompts[index] if index < len(video_prompts) else None

    # Check if image exists for video generation
    img_path = f"{STORAGE_PATH}/univers/{theme}/{index:02d}_{concept.replace(' ', '_')}.png"
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Image not found - generate image first")

    # Generate video
    generate_video(img_path, concept, theme, index, prompt)

    return {"message": f"Video for {concept} regenerated"}

@router.post("/universes/{universe}/rename-media")
def rename_media_endpoint(universe: str):
    theme = universe.lower().replace(' ', '_')

    # Load prompts for concepts
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")

    with open(prompts_path, 'r') as f:
        prompts_data = json.load(f)

    concepts = prompts_data.get("words", [])
    if not concepts:
        raise HTTPException(status_code=400, detail="No concepts found")

    # Load data for items
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data not found")

    with open(data_path, 'r') as f:
        data = json.load(f)

    items = data.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="No items found")

    renamed_count = 0
    for i, concept in enumerate(concepts[:len(items)]):
        if not concept.strip():
            continue

        old_image = items[i].get("image", "")
        old_video = items[i].get("video", "")

        new_base = f"{i:02d}_{concept.replace(' ', '_')}"
        new_image = f"{new_base}.png"
        new_video = f"{new_base}_silent.mp4"  # Keep .mp4 in data

        # Rename image
        old_image_path = os.path.join(STORAGE_PATH, "univers", theme, old_image)
        new_image_path = os.path.join(STORAGE_PATH, "univers", theme, new_image)
        if os.path.exists(old_image_path) and old_image != new_image:
            if os.path.exists(new_image_path):
                # Conflict, add suffix
                base, ext = os.path.splitext(new_image)
                counter = 1
                while os.path.exists(os.path.join(STORAGE_PATH, "univers", theme, f"{base}_{counter}{ext}")):
                    counter += 1
                new_image = f"{base}_{counter}{ext}"
                new_image_path = os.path.join(STORAGE_PATH, "univers", theme, new_image)
            os.rename(old_image_path, new_image_path)
            renamed_count += 1

        # Rename video webm
        old_video_webm = old_video.replace('.mp4', '.webm') if old_video else ""
        new_video_webm = new_video.replace('.mp4', '.webm')
        old_video_path = os.path.join(STORAGE_PATH, "univers", theme, old_video_webm)
        new_video_path = os.path.join(STORAGE_PATH, "univers", theme, new_video_webm)
        if os.path.exists(old_video_path) and old_video_webm != new_video_webm:
            if os.path.exists(new_video_path):
                base, ext = os.path.splitext(new_video_webm)
                counter = 1
                while os.path.exists(os.path.join(STORAGE_PATH, "univers", theme, f"{base}_{counter}{ext}")):
                    counter += 1
                new_video_webm = f"{base}_{counter}{ext}"
                new_video_path = os.path.join(STORAGE_PATH, "univers", theme, new_video_webm)
            os.rename(old_video_path, new_video_path)

        # Rename video mp4
        old_mp4_path = os.path.join(STORAGE_PATH, "univers", theme, old_video)
        new_mp4_path = os.path.join(STORAGE_PATH, "univers", theme, new_video)
        if os.path.exists(old_mp4_path) and old_video != new_video:
            if os.path.exists(new_mp4_path):
                base, ext = os.path.splitext(new_video)
                counter = 1
                while os.path.exists(os.path.join(STORAGE_PATH, "univers", theme, f"{base}_{counter}{ext}")):
                    counter += 1
                new_video = f"{base}_{counter}{ext}"
                new_mp4_path = os.path.join(STORAGE_PATH, "univers", theme, new_video)
            os.rename(old_mp4_path, new_mp4_path)

        # Update items
        items[i]["image"] = new_image
        items[i]["video"] = new_video
        items[i]["title"] = concept

    # Save data
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

    return {"message": f"Renamed {renamed_count} media files", "renamed": renamed_count}

@router.get("/status/{task_id}")
def get_status(task_id: str):
    # Placeholder for task status
    return {"status": "completed", "task_id": task_id}