"""
Routes pour la gestion des univers (version unifiée sans drafts)
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
import shutil
import re
import yaml
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from slugify import slugify

from models import (
    UniverseStatus,
    UniverseMetadata,
    AssetMetadata,
    CreateUniverseRequest,
    GenerateAssetsRequest,
    UniverseListItem,
    GenerationProgress,
    PromptDefaults
)

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

router = APIRouter()
logger = logging.getLogger(__name__)

STORAGE_PATH = Path("/app/storage")
UNIVERS_PATH = STORAGE_PATH / "univers"
PROMPTS_PATH = STORAGE_PATH / "prompts"

# Cache pour le statut de génération
generation_status: Dict[str, GenerationProgress] = {}


# ==================== Helper Functions ====================

def load_prompts_defaults() -> dict:
    """Charge les prompts par défaut depuis le fichier YAML"""
    defaults_path = PROMPTS_PATH / "themes.yaml"
    if defaults_path.exists():
        with open(defaults_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def get_universe_path(universe_id: str) -> Path:
    """Retourne le chemin d'un univers"""
    return UNIVERS_PATH / universe_id


def load_universe_metadata(universe_id: str) -> UniverseMetadata:
    """Charge les métadonnées d'un univers"""
    universe_path = get_universe_path(universe_id)
    metadata_file = universe_path / "metadata.json"
    
    if not metadata_file.exists():
        raise HTTPException(status_code=404, detail=f"Universe {universe_id} not found")
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return UniverseMetadata(**data)


def save_universe_metadata(universe_id: str, metadata: UniverseMetadata):
    """Sauvegarde les métadonnées d'un univers"""
    universe_path = get_universe_path(universe_id)
    universe_path.mkdir(parents=True, exist_ok=True)
    
    metadata_file = universe_path / "metadata.json"
    metadata.updated_at = datetime.now()
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata.model_dump(mode="json"), f, indent=2, ensure_ascii=False)


def load_assets_metadata(universe_id: str) -> List[AssetMetadata]:
    """Charge les métadonnées des assets d'un univers"""
    universe_path = get_universe_path(universe_id)
    assets_file = universe_path / "assets_metadata.json"
    
    if not assets_file.exists():
        return []
    
    with open(assets_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [AssetMetadata(**asset) for asset in data]


def save_assets_metadata(universe_id: str, assets: List[AssetMetadata]):
    """Sauvegarde les métadonnées des assets"""
    universe_path = get_universe_path(universe_id)
    assets_file = universe_path / "assets_metadata.json"
    
    with open(assets_file, "w", encoding="utf-8") as f:
        json.dump([asset.model_dump(mode="json") for asset in assets], f, indent=2, ensure_ascii=False)


def load_words_data(universe_id: str) -> dict:
    """Charge le fichier words.json d'un univers"""
    universe_path = get_universe_path(universe_id)
    words_file = universe_path / "words.json"
    
    if not words_file.exists():
        return {"words": [], "translations": {}}
    
    with open(words_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_words_data(universe_id: str, data: dict):
    """Sauvegarde le fichier words.json"""
    universe_path = get_universe_path(universe_id)
    words_file = universe_path / "words.json"
    
    with open(words_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_index(universe_id: str, name: str, remove: bool = False):
    """Met à jour index.json"""
    index_path = STORAGE_PATH / "index.json"
    
    if index_path.exists():
        with open(index_path, 'r') as f:
            themes = json.load(f)
    else:
        themes = []
    
    if remove:
        themes = [t for t in themes if t.get('folder') != universe_id]
    else:
        if not any(t.get('folder') == universe_id for t in themes):
            themes.append({"name": name, "folder": universe_id})
    
    with open(index_path, 'w') as f:
        json.dump(themes, f, indent=2, ensure_ascii=False)


# ==================== CRUD Endpoints ====================

@router.get("/universes")
async def list_universes():
    """Liste tous les univers avec leurs métadonnées"""
    universes = []
    
    if not UNIVERS_PATH.exists():
        return universes
    
    for universe_dir in UNIVERS_PATH.iterdir():
        if universe_dir.is_dir():
            metadata_file = universe_dir / "metadata.json"
            
            if metadata_file.exists():
                # Nouvel univers avec metadata.json
                try:
                    metadata = load_universe_metadata(universe_dir.name)
                    
                    # Chercher une miniature
                    thumbnail_path = None
                    assets_dir = universe_dir / "assets"
                    if assets_dir.exists():
                        images = list(assets_dir.glob("*.png")) + list(assets_dir.glob("*.jpg"))
                        if images:
                            thumbnail_path = f"/api/media/universes/{universe_dir.name}/assets/{images[0].name}"
                    
                    universes.append(UniverseListItem(
                        folder=universe_dir.name,
                        name=metadata.name,
                        theme=metadata.theme,
                        slug=metadata.slug,
                        status=metadata.status,
                        created_at=metadata.created_at,
                        updated_at=metadata.updated_at,
                        num_assets=metadata.num_assets,
                        thumbnail_path=thumbnail_path or metadata.thumbnail_url
                    ))
                except Exception as e:
                    logger.error(f"Error loading universe {universe_dir.name}: {e}")
                    continue
            else:
                # Ancien univers sans metadata.json - créer un item minimal
                universes.append(UniverseListItem(
                    folder=universe_dir.name,
                    name=universe_dir.name.replace('_', ' ').title(),
                    theme=universe_dir.name,
                    slug=universe_dir.name,
                    status=UniverseStatus.COMPLETED,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    num_assets=0,
                    thumbnail_path=None
                ))
    
    # Trier par date de mise à jour décroissante
    universes.sort(key=lambda u: u.updated_at, reverse=True)
    
    return universes


@router.post("/universes", status_code=201)
async def create_universe(request: CreateUniverseRequest):
    """
    Crée un nouvel univers
    
    1. Génère un ID à partir du nom (slug)
    2. Vérifie que l'univers n'existe pas déjà
    3. Crée le dossier univers/{id}/
    4. Charge les prompts par défaut selon le thème
    5. Sauvegarde metadata.json
    """
    # Créer un ID basé sur le nom
    slug = slugify(request.name)
    universe_id = slug
    
    # Vérifier que l'univers n'existe pas déjà
    universe_path = get_universe_path(universe_id)
    if universe_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Un univers avec le nom '{request.name}' existe déjà"
        )
    
    # Charger les prompts par défaut
    prompts_defaults = load_prompts_defaults()
    
    # Déterminer les prompts à utiliser
    theme_prompts = prompts_defaults.get("themes", {}).get(request.theme, {})
    if not theme_prompts:
        theme_prompts = prompts_defaults.get("generic", {})
    
    # Créer les prompts par défaut
    default_prompts = PromptDefaults(
        image=request.custom_prompts.image if request.custom_prompts and request.custom_prompts.image else theme_prompts.get("images", ""),
        video=request.custom_prompts.video if request.custom_prompts and request.custom_prompts.video else theme_prompts.get("videos", "")
    )
    
    # Créer les métadonnées
    metadata = UniverseMetadata(
        folder=universe_id,
        name=request.name,
        theme=request.theme,
        slug=slug,
        status=UniverseStatus.DRAFT,
        default_prompts=default_prompts
    )
    
    # Créer le dossier
    universe_path = get_universe_path(universe_id)
    universe_path.mkdir(parents=True, exist_ok=True)
    (universe_path / "assets").mkdir(exist_ok=True)
    
    save_universe_metadata(universe_id, metadata)
    update_index(universe_id, request.name)
    
    logger.info(f"Created universe {universe_id} for '{request.name}'")
    
    response = metadata.model_dump(mode="json")
    response["folder"] = universe_id
    return response


@router.get("/universes/{universe_id}")
async def get_universe(universe_id: str):
    """Récupère les métadonnées d'un univers"""
    metadata = load_universe_metadata(universe_id)
    
    response = metadata.model_dump(mode="json")
    response["folder"] = universe_id
    
    return response


@router.delete("/universes/{universe_id}", status_code=204)
async def delete_universe(universe_id: str):
    """Supprime un univers"""
    universe_path = get_universe_path(universe_id)
    
    if not universe_path.exists():
        raise HTTPException(status_code=404, detail=f"Universe {universe_id} not found")
    
    shutil.rmtree(universe_path)
    update_index(universe_id, "", remove=True)
    
    if universe_id in generation_status:
        del generation_status[universe_id]
    
    logger.info(f"Deleted universe {universe_id}")


# ==================== Assets Endpoints ====================

@router.get("/universes/{universe_id}/assets", response_model=List[AssetMetadata])
async def get_universe_assets(universe_id: str):
    """Récupère la liste des assets d'un univers"""
    load_universe_metadata(universe_id)  # Vérifier que l'univers existe
    return load_assets_metadata(universe_id)


# ==================== Words/Translations Endpoints ====================

@router.get("/universes/{universe_id}/words")
async def get_universe_words(universe_id: str):
    """Récupère les mots et traductions d'un univers"""
    return load_words_data(universe_id)


@router.get("/universes/{universe_id}/data")
async def get_universe_data(universe_id: str):
    """
    Récupère les données complètes d'un univers pour le viewer
    Compatible avec l'ancien format data.json
    """
    universe_path = get_universe_path(universe_id)
    
    # Essayer d'abord data.json (ancien format)
    data_file = universe_path / "data.json"
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Sinon construire depuis les nouveaux fichiers
    try:
        metadata = load_universe_metadata(universe_id)
        words_data = load_words_data(universe_id)
        assets = load_assets_metadata(universe_id)
        
        # Construire les items
        items = []
        for i, asset in enumerate(assets):
            item = {
                "title": asset.display_name,
                "image": asset.image_file or f"{i:02d}_{asset.display_name.replace(' ', '_')}.png",
                "video": asset.video_file,
                "title_translations": {}
            }
            
            # Ajouter les traductions
            for lang in ["fr", "en", "es", "it", "de"]:
                translations = words_data.get("translations", {}).get(lang, [])
                if i < len(translations):
                    item["title_translations"][lang] = translations[i]
            
            items.append(item)
        
        return {
            "items": items,
            "translations": words_data.get("translations", {}),
            "background_color": metadata.background_color or "#ffffff",
            "description": metadata.name,
            "music_translations": build_music_translations(metadata.music_lyrics or {})
        }
    except:
        raise HTTPException(status_code=404, detail="Universe data not found")


def build_music_translations(music_lyrics: dict) -> dict:
    """Construit la structure music_translations depuis music_lyrics"""
    result = {}
    for lang in ["fr", "en", "es", "it", "de"]:
        result[lang] = {
            "lyrics": music_lyrics.get(lang, ""),
            "prompt": ""
        }
    return result


@router.patch("/universes/{universe_id}/data")
async def update_universe_data(universe_id: str, updates: dict):
    """Met à jour les données d'un univers"""
    universe_path = get_universe_path(universe_id)
    data_file = universe_path / "data.json"
    
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    
    # Merge updates
    for key, value in updates.items():
        if isinstance(value, dict) and key in data:
            data[key].update(value)
        else:
            data[key] = value
    
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return {"message": "Data updated"}


# ==================== Prompts Endpoints ====================

@router.get("/universes/{universe_id}/prompts")
async def get_universe_prompts(universe_id: str):
    """Récupère les prompts d'un univers"""
    universe_path = get_universe_path(universe_id)
    prompts_file = universe_path / "prompts.json"
    
    if prompts_file.exists():
        with open(prompts_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Construire depuis assets_metadata
    assets = load_assets_metadata(universe_id)
    words_data = load_words_data(universe_id)
    
    return {
        "words": words_data.get("words", [asset.display_name for asset in assets]),
        "images": [asset.image_prompt or "" for asset in assets],
        "videos": [asset.video_prompt or "" for asset in assets]
    }


@router.patch("/universes/{universe_id}/prompts")
async def update_universe_prompts(universe_id: str, updates: dict):
    """Met à jour les prompts d'un univers"""
    universe_path = get_universe_path(universe_id)
    prompts_file = universe_path / "prompts.json"
    
    if prompts_file.exists():
        with open(prompts_file, "r", encoding="utf-8") as f:
            current = json.load(f)
    else:
        current = {}
    
    current.update(updates)
    
    with open(prompts_file, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    
    return {"message": "Prompts updated"}


# ==================== Generation Endpoints ====================

@router.post("/universes/{universe_id}/translations/generate")
async def generate_universe_translations(universe_id: str):
    """Génère les traductions pour un univers"""
    from projet.translation_generator import generate_translations
    
    metadata = load_universe_metadata(universe_id)
    words_data = load_words_data(universe_id)
    
    if not words_data.get("words"):
        raise HTTPException(status_code=400, detail="No words found to translate")
    
    result = generate_translations(metadata.theme, debug=False)
    words_data["translations"] = result["translations"]
    save_words_data(universe_id, words_data)
    
    return {"message": "Translations generated", "translations": result["translations"]}


@router.post("/universes/{universe_id}/images/prompts/generate")
async def generate_universe_image_prompts(universe_id: str, data: dict):
    """Génère les prompts d'images pour un univers"""
    from services.storage_service import storage_service
    
    default_prompt = data.get("defaultPrompt", "")
    
    if not default_prompt:
        defaults = storage_service.load_default_prompts()
        default_prompt = defaults.get("images", "A beautiful illustration of {object}")
    
    # Charger les objets depuis words.json ou assets_metadata.json
    words_data = load_words_data(universe_id)
    objects = words_data.get("words", [])
    
    if not objects:
        assets = load_assets_metadata(universe_id)
        objects = [a.display_name for a in assets]
    
    if not objects:
        raise HTTPException(status_code=400, detail="No objects found")

    # Générer les prompts
    prompts = [default_prompt.replace("{object}", obj) for obj in objects]
    
    # Sauvegarder
    universe_path = get_universe_path(universe_id)
    prompts_file = universe_path / "prompts.json"
    
    if prompts_file.exists():
        with open(prompts_file, "r", encoding="utf-8") as f:
            current = json.load(f)
    else:
        current = {"words": objects}
    
    current["images"] = prompts
    
    with open(prompts_file, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    
    return {"prompts": prompts}


@router.post("/universes/{universe_id}/videos/prompts/generate")
async def generate_universe_video_prompts(universe_id: str, data: dict):
    """Génère les prompts de vidéos pour un univers"""
    from services.storage_service import storage_service
    
    default_prompt = data.get("defaultPrompt", "")
    
    if not default_prompt:
        defaults = storage_service.load_default_prompts()
        default_prompt = defaults.get("videos", "A short animated video of {object}")
    
    words_data = load_words_data(universe_id)
    objects = words_data.get("words", [])
    
    if not objects:
        assets = load_assets_metadata(universe_id)
        objects = [a.display_name for a in assets]
    
    if not objects:
        raise HTTPException(status_code=400, detail="No objects found")

    prompts = [default_prompt.replace("{object}", obj) for obj in objects]
    
    universe_path = get_universe_path(universe_id)
    prompts_file = universe_path / "prompts.json"
    
    if prompts_file.exists():
        with open(prompts_file, "r", encoding="utf-8") as f:
            current = json.load(f)
    else:
        current = {"words": objects}
    
    current["videos"] = prompts
    
    with open(prompts_file, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    
    return {"prompts": prompts}


@router.post("/universes/{universe_id}/lyrics/generate")
async def generate_universe_lyrics(universe_id: str, data: dict):
    """Génère les paroles pour un univers"""
    from prompts import generate_lyrics as generate_lyrics_fn
    
    metadata = load_universe_metadata(universe_id)
    theme_name = data.get("theme", "") or metadata.theme
    words = data.get("words", [])
    
    if not words:
        words_data = load_words_data(universe_id)
        words = words_data.get("words", [])
    
    try:
        lyrics = generate_lyrics_fn(theme_name, words)
        
        metadata.music_lyrics = metadata.music_lyrics or {}
        metadata.music_lyrics["fr"] = lyrics
        save_universe_metadata(universe_id, metadata)
        
        return {"lyrics": lyrics, "language": "fr"}
        
    except Exception as e:
        logger.error(f"Error generating lyrics for universe {universe_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate lyrics: {str(e)}")


@router.post("/universes/{universe_id}/music/{lang}")
async def generate_universe_music(universe_id: str, lang: str):
    """Génère la musique pour un univers"""
    from projet.generators import generate_theme_music
    
    metadata = load_universe_metadata(universe_id)
    
    generated_paths = generate_theme_music(
        theme_key=universe_id,
        theme_name_fr=metadata.name,
        music_prompt=None,
        lyrics=None,
        languages=[lang]
    )
    
    return {"message": f"Music generated for {lang}", "path": generated_paths[0] if generated_paths else None}


# ==================== Publish/Sync Endpoints ====================

@router.post("/universes/{universe_id}/publish")
async def publish_universe(universe_id: str):
    """Upload/publish universe to Supabase storage and database"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    universe_path = get_universe_path(universe_id)
    
    if not universe_path.exists():
        raise HTTPException(status_code=404, detail="Universe not found")
    
    try:
        # Charger les métadonnées
        metadata = load_universe_metadata(universe_id)
        
        # Upload all files to Supabase Storage
        bucket_name = "univers"
        uploaded_files = []
        
        for root, dirs, files in os.walk(universe_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, universe_path)
                remote_path = f"{universe_id}/{relative_path}".replace("\\", "/")
                
                with open(file_path, "rb") as f:
                    file_content = f.read()
                    try:
                        supabase_client.storage.from_(bucket_name).upload(
                            remote_path, file_content, {"content-type": "auto"}
                        )
                    except:
                        try:
                            supabase_client.storage.from_(bucket_name).remove([remote_path])
                        except:
                            pass
                        supabase_client.storage.from_(bucket_name).upload(
                            remote_path, file_content, {"content-type": "auto"}
                        )
                uploaded_files.append(remote_path)
        
        # Get universe data
        data = await get_universe_data(universe_id)
        items = data.get("items", [])
        
        # Find thumbnail
        thumbnail = items[0]["image"] if items else "placeholder.png"
        thumbnail_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{universe_id}/{thumbnail}"
        
        # Insert or update universe in database
        universe_db_data = {
            "name": metadata.name,
            "slug": universe_id,
            "is_public": True,
            "thumbnail_url": thumbnail_url,
            "background_color": metadata.background_color or "#ffffff",
            "background_music": "music_fr.mp3"
        }

        existing = supabase_client.table("univers").select("id").eq("slug", universe_id).execute()

        universe_id_db = None
        if existing.data:
            supabase_client.table("univers").update(universe_db_data).eq("slug", universe_id).execute()
            universe_id_db = existing.data[0]["id"]
        else:
            insert_response = supabase_client.table("univers").insert(universe_db_data).execute()
            universe_id_db = insert_response.data[0]["id"]

        # Update metadata status
        metadata.status = UniverseStatus.PUBLISHED
        save_universe_metadata(universe_id, metadata)

        # Delete and recreate assets
        supabase_client.table("univers_assets").delete().eq("univers_id", universe_id_db).execute()

        if items:
            asset_inserts = []
            for i, item in enumerate(items):
                asset_inserts.append({
                    "univers_id": universe_id_db,
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
            "message": f"Universe '{metadata.name}' published successfully",
            "files_uploaded": len(uploaded_files),
            "assets_created": len(items),
            "public_url": f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{universe_id}/"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish universe: {str(e)}")


@router.post("/universes/{universe_id}/sync-from-db")
async def sync_universe_from_db(universe_id: str):
    """Download/sync universe from Supabase to local storage"""
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    universe_path = get_universe_path(universe_id)
    
    try:
        # Get universe from database
        universe_response = supabase_client.table("univers").select("*").eq("slug", universe_id).execute()

        if not universe_response.data:
            raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found in database")

        universe_db = universe_response.data[0]

        # Get assets
        assets_response = supabase_client.table("univers_assets").select(
            "*, univers_assets_translations(*)"
        ).eq("univers_id", universe_db["id"]).order("sort_order").execute()
        
        # Clean and recreate directory
        if universe_path.exists():
            shutil.rmtree(universe_path)
        universe_path.mkdir(parents=True, exist_ok=True)
        (universe_path / "assets").mkdir(exist_ok=True)
        
        # Download files from storage
        bucket_name = "univers"
        downloaded_files = []
        
        try:
            files_response = supabase_client.storage.from_(bucket_name).list(universe_id)
            
            for file_obj in files_response:
                file_name = file_obj['name']
                remote_path = f"{universe_id}/{file_name}"
                local_file_path = universe_path / file_name
                
                file_data = supabase_client.storage.from_(bucket_name).download(remote_path)
                
                with open(local_file_path, 'wb') as f:
                    f.write(file_data)
                
                downloaded_files.append(file_name)
        except Exception as e:
            logger.warning(f"Storage download error: {e}")
        
        # Build data files
        items = []
        translations = {"fr": [], "en": [], "es": [], "it": [], "de": []}
        
        for asset in assets_response.data:
            item = {
                "title": asset["display_name"],
                "image": asset["image_name"],
                "video": asset["image_name"].replace(".png", ".mp4"),
                "title_translations": {}
            }
            
            for trans in asset.get("univers_assets_translations", []):
                lang = trans["language"]
                display_name = trans["display_name"]
                item["title_translations"][lang] = display_name
                translations[lang].append(display_name)
            
            for lang in translations.keys():
                if lang not in item["title_translations"]:
                    item["title_translations"][lang] = asset["display_name"]
                    translations[lang].append(asset["display_name"])
            
            items.append(item)
        
        # Create metadata.json
        metadata = UniverseMetadata(
            folder=universe_id,
            name=universe_db["name"],
            theme=universe_id.split("-")[0] if "-" in universe_id else universe_id,
            slug=universe_id.split("-")[0] if "-" in universe_id else universe_id,
            status=UniverseStatus.PUBLISHED,
            background_color=universe_db.get("background_color", "#ffffff")
        )
        save_universe_metadata(universe_id, metadata)
        
        # Create data.json
        data = {
            "items": items,
            "translations": translations,
            "background_color": universe_db.get("background_color", "#ffffff"),
            "description": universe_db.get("name", universe_id),
            "music_translations": {}
        }
        
        with open(universe_path / "data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Create words.json
        words_data = {
            "theme": metadata.theme,
            "words": [item["title"] for item in items],
            "translations": translations
        }
        save_words_data(universe_id, words_data)
        
        # Update index
        update_index(universe_id, universe_db["name"])
        
        return {
            "message": f"Universe '{universe_id}' synced successfully",
            "files_downloaded": len(downloaded_files),
            "assets_synced": len(items)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync universe: {str(e)}")


# ==================== Default Prompts Endpoint ====================

@router.get("/default-prompts")
async def get_default_prompts():
    """Récupère les prompts par défaut"""
    from services.storage_service import storage_service
    return storage_service.load_default_prompts()
