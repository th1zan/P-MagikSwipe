from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
import os
from projet.generators import generate_image, generate_video, generate_theme_music

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

@router.post("/generate/{universe}/music")
def generate_music(universe: str):
    theme = universe.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")
    if not os.path.exists(prompts_path):
        raise HTTPException(status_code=404, detail="Prompts not found")
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    music = data.get("music", "")
    lyrics = data.get("lyrics", "")
    
    generate_theme_music(theme, universe, music, lyrics)
    
    return {"message": "Music generated"}

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