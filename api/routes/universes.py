from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
import shutil
import re
from dotenv import load_dotenv
from supabase import create_client
from prompts import generate_base_prompts
from projet.generators import get_dominant_color

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

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
    thumbnail = items[0]["image"] if items else ""
    color = get_dominant_color(os.path.join(universe_dir, thumbnail)) if thumbnail else "#ffffff"
    data = {"thumbnail": thumbnail, "background_color": color, "items": items}
    data_path = os.path.join(universe_dir, "data.json")
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)

    # Insert into univers_assets
    if supabase_client:
        try:
            inserts = []
            for i, item in enumerate(items):
                inserts.append({
                    "univers_folder": theme_folder,
                    "sort_order": i,
                    "image_name": item["image"],
                    "display_name": item["title"]
                })
            supabase_client.table("univers_assets").insert(inserts).execute()
            print(f"Inserted {len(inserts)} assets for {theme_folder}")
        except Exception as e:
            print(f"DB insert error: {e}")

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

@router.patch("/universes/{name}/prompts")
def update_prompts(name: str, updates: dict):
    theme = name.lower().replace(' ', '_')
    prompts_path = os.path.join(STORAGE_PATH, "univers", theme, "prompts.json")

    # Load existing prompts
    if os.path.exists(prompts_path):
        with open(prompts_path, 'r') as f:
            current_prompts = json.load(f)
    else:
        current_prompts = {}

    # Merge updates
    for key, value in updates.items():
        if isinstance(value, list) and key in current_prompts:
            # For arrays like images/videos, replace the entire array
            current_prompts[key] = value
        else:
            current_prompts[key] = value

    # Save updated prompts
    with open(prompts_path, 'w') as f:
        json.dump(current_prompts, f, indent=2)

    return {"message": "Prompts updated"}

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

@router.put("/universes/{name}/color")
def update_color(name: str, color: str):
    if not re.match(r'^#[0-9a-fA-F]{6}$', color):
        raise HTTPException(status_code=400, detail="Invalid color format")
    theme = name.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    with open(data_path, 'r') as f:
        data = json.load(f)
    data['background_color'] = color
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)
    return {"message": "Color updated"}

@router.get("/universes/{name}/color")
def get_color(name: str):
    theme = name.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    with open(data_path, 'r') as f:
        data = json.load(f)
    return {"color": data.get('background_color', '#ffffff')}

@router.get("/universes/{name}/data")
def get_data(name: str):
    theme = name.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    with open(data_path, 'r') as f:
        data = json.load(f)
    return data

@router.patch("/universes/{name}/data")
def update_data(name: str, updates: dict):
    theme = name.lower().replace(' ', '_')
    data_path = os.path.join(STORAGE_PATH, "univers", theme, "data.json")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    with open(data_path, 'r') as f:
        data = json.load(f)
    # Merge updates
    for key, value in updates.items():
        if isinstance(value, dict) and key in data:
            data[key].update(value)
        else:
            data[key] = value
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=2)
    return {"message": "Data updated"}

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

@router.post("/universes/{name}/publish")
def publish_universe(name: str):
    """Upload/publish universe to Supabase storage and database"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    folder = name.lower().replace(' ', '_')
    local_path = os.path.join(STORAGE_PATH, "univers", folder)
    
    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Universe not found")
    
    try:
        # Upload all files to Supabase Storage
        bucket_name = "univers"
        uploaded_files = []
        
        for root, dirs, files in os.walk(local_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, local_path)
                remote_path = f"{folder}/{relative_path}".replace("\\", "/")
                
                with open(file_path, "rb") as f:
                    file_content = f.read()
                    try:
                        # Try to upload, if exists, remove and re-upload
                        supabase_client.storage.from_(bucket_name).upload(
                            remote_path, file_content, {"content-type": "auto"}
                        )
                    except Exception as upload_error:
                        # If file exists, remove it first then upload
                        try:
                            supabase_client.storage.from_(bucket_name).remove([remote_path])
                        except:
                            pass
                        supabase_client.storage.from_(bucket_name).upload(
                            remote_path, file_content, {"content-type": "auto"}
                        )
                uploaded_files.append(remote_path)
        
        # Load universe data
        data_path = os.path.join(local_path, "data.json")
        with open(data_path, 'r') as f:
            universe_data = json.load(f)
        
        # Find thumbnail
        files = os.listdir(local_path)
        thumbnail = next((f for f in files if f.startswith("00_") and f.endswith(".png")), None)
        if not thumbnail:
            thumbnail = files[0] if files else "placeholder.png"
        
        thumbnail_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{folder}/{thumbnail}"
        background_color = universe_data.get('background_color', '#ffffff')
        
        # Insert or update universe in database
        universe_db_data = {
            "name": name,
            "folder": folder,
            "is_public": True,
            "thumbnail_url": thumbnail_url,
            "background_color": background_color,
            "background_music": "music.mp3"
        }
        
        # Check if universe already exists
        existing = supabase_client.table("univers").select("id").eq("folder", folder).execute()
        
        if existing.data:
            # Update existing
            supabase_client.table("univers").update(universe_db_data).eq("folder", folder).execute()
        else:
            # Insert new
            supabase_client.table("univers").insert(universe_db_data).execute()
        
        # Delete existing assets for this universe
        supabase_client.table("univers_assets").delete().eq("univers_folder", folder).execute()
        
        # Insert assets
        items = universe_data.get("items", [])
        if items:
            asset_inserts = []
            for i, item in enumerate(items):
                asset_inserts.append({
                    "univers_folder": folder,
                    "sort_order": i,
                    "image_name": item["image"],
                    "display_name": item["title"]
                })
            asset_response = supabase_client.table("univers_assets").insert(asset_inserts).execute()
            
            # Insert translations
            translation_inserts = []
            for i, item in enumerate(items):
                asset_id = asset_response.data[i]["id"]
                title_translations = item.get("title_translations", {})
                for lang in ["fr", "en", "es", "it", "de"]:
                    display_name = title_translations.get(lang, item["title"])
                    translation_inserts.append({
                        "asset_id": asset_id,
                        "language": lang,
                        "display_name": display_name
                    })
            
            if translation_inserts:
                supabase_client.table("univers_assets_translations").insert(translation_inserts).execute()
        
        return {
            "message": f"Universe '{name}' published successfully",
            "files_uploaded": len(uploaded_files),
            "assets_created": len(items),
            "public_url": f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{folder}/"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish universe: {str(e)}")