"""Universe routes - CRUD operations for universes and assets."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from slugify import slugify

from database import get_db, Univers, UniversPrompts, UniversTranslation, UniversAsset, UniversAssetPrompts, UniversAssetTranslation, UniversMusicPrompts
from schemas import (
    UniversCreate, UniversUpdate, UniversResponse, UniversListItem, UniversListResponse,
    AssetCreate, AssetUpdate, AssetResponse, AssetListResponse,
    UniversMusicPromptsCreate, UniversMusicPromptsUpdate, UniversMusicPromptsResponse
)
from services.storage_service import storage_service

router = APIRouter(prefix="/universes", tags=["universes"])


# =============================================================================
# UNIVERSE CRUD
# =============================================================================

@router.get("", response_model=UniversListResponse)
def list_universes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all universes with pagination."""
    query = db.query(Univers)
    
    if is_public is not None:
        query = query.filter(Univers.is_public == is_public)
    
    total = query.count()
    universes = query.order_by(Univers.created_at.desc()).offset(skip).limit(limit).all()
    
    items = []
    for u in universes:
        items.append(UniversListItem(
            id=u.id,
            name=u.name,
            slug=u.slug,
            thumbnail_url=u.thumbnail_url or storage_service.get_thumbnail_url(u.slug),
            is_public=u.is_public,
            asset_count=len(u.assets),
            last_synced_at=u.last_synced_at
        ))
    
    return UniversListResponse(items=items, total=total)


@router.post("", response_model=UniversResponse, status_code=201)
def create_universe(
    data: UniversCreate,
    db: Session = Depends(get_db)
):
    """Create a new universe."""
    # Generate slug if not provided
    slug = data.slug or slugify(data.name)
    
    # Check if slug exists
    existing = db.query(Univers).filter(Univers.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Universe with slug '{slug}' already exists")
    
    # Create universe
    univers = Univers(
        name=data.name,
        slug=slug,
        background_color=data.background_color,
        is_public=data.is_public
    )
    db.add(univers)
    db.flush()
    
    # Create prompts if provided
    if data.default_image_prompt or data.default_video_prompt:
        prompts = UniversPrompts(
            univers_id=univers.id,
            default_image_prompt=data.default_image_prompt,
            default_video_prompt=data.default_video_prompt
        )
        db.add(prompts)
    
    # Create translations if provided
    if data.translations:
        for lang, name in data.translations.items():
            trans = UniversTranslation(
                univers_id=univers.id,
                language=lang,
                name=name
            )
            db.add(trans)
    
    # Create storage folder
    storage_service.create_universe_folder(slug)
    
    db.commit()
    db.refresh(univers)
    
    return _build_univers_response(univers)


@router.get("/{slug}", response_model=UniversResponse)
def get_universe(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a universe by slug with all relations."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    return _build_univers_response(univers)


@router.patch("/{slug}", response_model=UniversResponse)
def update_universe(
    slug: str,
    data: UniversUpdate,
    db: Session = Depends(get_db)
):
    """Update a universe."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    # Update basic fields
    if data.name is not None:
        univers.name = data.name
    if data.thumbnail_url is not None:
        univers.thumbnail_url = data.thumbnail_url
    if data.is_public is not None:
        univers.is_public = data.is_public
    if data.background_music is not None:
        univers.background_music = data.background_music
    if data.background_color is not None:
        univers.background_color = data.background_color
    
    # Update prompts
    if data.default_image_prompt is not None or data.default_video_prompt is not None:
        if univers.prompts:
            if data.default_image_prompt is not None:
                univers.prompts.default_image_prompt = data.default_image_prompt
            if data.default_video_prompt is not None:
                univers.prompts.default_video_prompt = data.default_video_prompt
        else:
            prompts = UniversPrompts(
                univers_id=univers.id,
                default_image_prompt=data.default_image_prompt,
                default_video_prompt=data.default_video_prompt
            )
            db.add(prompts)
    
    # Update translations
    if data.translations is not None:
        # Delete existing
        db.query(UniversTranslation).filter(UniversTranslation.univers_id == univers.id).delete()
        
        # Add new
        for lang, name in data.translations.items():
            trans = UniversTranslation(
                univers_id=univers.id,
                language=lang,
                name=name
            )
            db.add(trans)
    
    db.commit()
    db.refresh(univers)
    
    return _build_univers_response(univers)


@router.delete("/{slug}", status_code=204)
def delete_universe(
    slug: str,
    db: Session = Depends(get_db)
):
    """Delete a universe and all its assets."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    # Delete from database (cascades to assets, translations, prompts)
    db.delete(univers)
    db.commit()
    
    # Delete storage folder
    storage_service.delete_universe_folder(slug)
    
    return None


# =============================================================================
# ASSET CRUD
# =============================================================================

@router.get("/{slug}/assets", response_model=List[AssetListResponse])
def list_assets(
    slug: str,
    db: Session = Depends(get_db)
):
    """List all assets in a universe."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    assets = []
    for a in univers.assets:
        assets.append(AssetListResponse(
            id=a.id,
            sort_order=a.sort_order,
            display_name=a.display_name,
            image_name=a.image_name,
            image_url=storage_service.get_asset_image_url(slug, a.image_name),
            video_url=storage_service.get_asset_video_url(slug, a.image_name)
        ))
    
    return assets


@router.post("/{slug}/assets", response_model=AssetResponse, status_code=201)
def create_asset(
    slug: str,
    data: AssetCreate,
    db: Session = Depends(get_db)
):
    """Create a new asset in a universe."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    # Determine sort order
    if data.sort_order is not None:
        sort_order = data.sort_order
    else:
        max_order = db.query(UniversAsset)\
            .filter(UniversAsset.univers_id == univers.id)\
            .count()
        sort_order = max_order + 1
    
    # Generate image name
    image_name = f"asset_{sort_order:03d}.png"
    
    # Create asset
    asset = UniversAsset(
        univers_id=univers.id,
        sort_order=sort_order,
        image_name=image_name,
        display_name=data.display_name
    )
    db.add(asset)
    db.flush()
    
    # Create prompts if provided
    if data.custom_image_prompt or data.custom_video_prompt:
        prompts = UniversAssetPrompts(
            asset_id=asset.id,
            custom_image_prompt=data.custom_image_prompt,
            custom_video_prompt=data.custom_video_prompt
        )
        db.add(prompts)
    
    # Create translations if provided
    if data.translations:
        for lang, display_name in data.translations.items():
            trans = UniversAssetTranslation(
                asset_id=asset.id,
                language=lang,
                display_name=display_name
            )
            db.add(trans)
    
    db.commit()
    db.refresh(asset)
    
    return _build_asset_response(asset, slug)


@router.get("/{slug}/assets/{asset_id}", response_model=AssetResponse)
def get_asset(
    slug: str,
    asset_id: str,
    db: Session = Depends(get_db)
):
    """Get a single asset by ID."""
    asset = db.query(UniversAsset)\
        .join(Univers)\
        .filter(Univers.slug == slug, UniversAsset.id == asset_id)\
        .first()
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")
    
    return _build_asset_response(asset, slug)


@router.patch("/{slug}/assets/{asset_id}", response_model=AssetResponse)
def update_asset(
    slug: str,
    asset_id: str,
    data: AssetUpdate,
    db: Session = Depends(get_db)
):
    """Update an asset."""
    asset = db.query(UniversAsset)\
        .join(Univers)\
        .filter(Univers.slug == slug, UniversAsset.id == asset_id)\
        .first()
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")
    
    # Update basic fields
    if data.display_name is not None:
        asset.display_name = data.display_name
    if data.sort_order is not None:
        asset.sort_order = data.sort_order
    
    # Update prompts
    if data.custom_image_prompt is not None or data.custom_video_prompt is not None:
        if asset.prompts:
            if data.custom_image_prompt is not None:
                asset.prompts.custom_image_prompt = data.custom_image_prompt
            if data.custom_video_prompt is not None:
                asset.prompts.custom_video_prompt = data.custom_video_prompt
        else:
            prompts = UniversAssetPrompts(
                asset_id=asset.id,
                custom_image_prompt=data.custom_image_prompt,
                custom_video_prompt=data.custom_video_prompt
            )
            db.add(prompts)
    
    # Update translations
    if data.translations is not None:
        db.query(UniversAssetTranslation).filter(UniversAssetTranslation.asset_id == asset.id).delete()
        
        for lang, display_name in data.translations.items():
            trans = UniversAssetTranslation(
                asset_id=asset.id,
                language=lang,
                display_name=display_name
            )
            db.add(trans)
    
    db.commit()
    db.refresh(asset)
    
    return _build_asset_response(asset, slug)


@router.delete("/{slug}/assets/{asset_id}", status_code=204)
def delete_asset(
    slug: str,
    asset_id: str,
    db: Session = Depends(get_db)
):
    """Delete an asset."""
    asset = db.query(UniversAsset)\
        .join(Univers)\
        .filter(Univers.slug == slug, UniversAsset.id == asset_id)\
        .first()
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")
    
    image_name = asset.image_name
    
    # Delete from database
    db.delete(asset)
    db.commit()
    
    # Delete files
    storage_service.delete_file(f"{slug}/{image_name}")
    video_name = image_name.replace(".png", ".mp4")
    storage_service.delete_file(f"{slug}/{video_name}")
    
    return None


# =============================================================================
# MUSIC PROMPTS CRUD
# =============================================================================

@router.get("/{slug}/music-prompts", response_model=List[UniversMusicPromptsResponse])
def list_music_prompts(slug: str, db: Session = Depends(get_db)):
    """List all music prompts for a universe."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()

    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")

    return univers.music_prompts


@router.post("/{slug}/music-prompts", response_model=UniversMusicPromptsResponse, status_code=201)
def create_music_prompt(
    slug: str,
    data: UniversMusicPromptsCreate,
    db: Session = Depends(get_db)
):
    """Create music prompt for a specific language."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()

    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")

    # Check if language already exists
    existing = db.query(UniversMusicPrompts)\
        .filter(UniversMusicPrompts.univers_id == univers.id)\
        .filter(UniversMusicPrompts.language == data.language.value)\
        .first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Music prompt for language '{data.language.value}' already exists"
        )

    prompt = UniversMusicPrompts(
        univers_id=univers.id,
        language=data.language.value,
        prompt=data.prompt,
        lyrics=data.lyrics
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@router.get("/{slug}/music-prompts/{language}", response_model=UniversMusicPromptsResponse)
def get_music_prompt(slug: str, language: str, db: Session = Depends(get_db)):
    """Get music prompt for a specific language."""
    prompt = db.query(UniversMusicPrompts)\
        .join(Univers)\
        .filter(Univers.slug == slug)\
        .filter(UniversMusicPrompts.language == language)\
        .first()

    if not prompt:
        raise HTTPException(status_code=404, detail=f"Music prompt for '{language}' not found")

    return prompt


@router.patch("/{slug}/music-prompts/{language}", response_model=UniversMusicPromptsResponse)
def update_music_prompt(
    slug: str,
    language: str,
    data: UniversMusicPromptsUpdate,
    db: Session = Depends(get_db)
):
    """Update music prompt for a specific language."""
    prompt = db.query(UniversMusicPrompts)\
        .join(Univers)\
        .filter(Univers.slug == slug)\
        .filter(UniversMusicPrompts.language == language)\
        .first()

    if not prompt:
        raise HTTPException(status_code=404, detail=f"Music prompt for '{language}' not found")

    if data.prompt is not None:
        prompt.prompt = data.prompt
    if data.lyrics is not None:
        prompt.lyrics = data.lyrics

    db.commit()
    db.refresh(prompt)
    return prompt


@router.delete("/{slug}/music-prompts/{language}", status_code=204)
def delete_music_prompt(slug: str, language: str, db: Session = Depends(get_db)):
    """Delete music prompt for a specific language."""
    prompt = db.query(UniversMusicPrompts)\
        .join(Univers)\
        .filter(Univers.slug == slug)\
        .filter(UniversMusicPrompts.language == language)\
        .first()

    if not prompt:
        raise HTTPException(status_code=404, detail=f"Music prompt for '{language}' not found")

    db.delete(prompt)
    db.commit()
    return None


# =============================================================================
# HELPERS
# =============================================================================

def _build_univers_response(univers: Univers) -> UniversResponse:
    """Build a complete universe response with all relations."""
    slug = univers.slug
    
    # Build assets list
    assets = []
    for a in univers.assets:
        assets.append(AssetListResponse(
            id=a.id,
            sort_order=a.sort_order,
            display_name=a.display_name,
            image_name=a.image_name,
            image_url=storage_service.get_asset_image_url(slug, a.image_name),
            video_url=storage_service.get_asset_video_url(slug, a.image_name)
        ))
    
    # Build translations
    from schemas import TranslationResponse, UniversPromptsResponse
    translations = [
        TranslationResponse(id=t.id, language=t.language, name=t.name)
        for t in univers.translations
    ]
    
    # Build prompts
    prompts = None
    if univers.prompts:
        prompts = UniversPromptsResponse(
            id=univers.prompts.id,
            univers_id=univers.id,
            default_image_prompt=univers.prompts.default_image_prompt,
            default_video_prompt=univers.prompts.default_video_prompt
        )

    # Build music prompts
    from schemas import UniversMusicPromptsResponse
    music_prompts = [
        UniversMusicPromptsResponse(
            id=mp.id,
            univers_id=mp.univers_id,
            language=mp.language,
            prompt=mp.prompt,
            lyrics=mp.lyrics,
            created_at=mp.created_at
        )
        for mp in univers.music_prompts
    ]

    return UniversResponse(
        id=univers.id,
        name=univers.name,
        slug=univers.slug,
        thumbnail_url=univers.thumbnail_url or storage_service.get_thumbnail_url(slug),
        is_public=univers.is_public,
        background_music=univers.background_music,
        background_color=univers.background_color,
        created_at=univers.created_at,
        updated_at=univers.updated_at,
        supabase_id=univers.supabase_id,
        last_synced_at=univers.last_synced_at,
        prompts=prompts,
        translations=translations,
        music_prompts=music_prompts,
        assets=assets,
        asset_count=len(assets)
    )


def _build_asset_response(asset: UniversAsset, slug: str) -> AssetResponse:
    """Build a complete asset response with all relations."""
    from schemas import AssetPromptsResponse, AssetTranslationResponse
    
    prompts = None
    if asset.prompts:
        prompts = AssetPromptsResponse(
            id=asset.prompts.id,
            asset_id=asset.id,
            custom_image_prompt=asset.prompts.custom_image_prompt,
            custom_video_prompt=asset.prompts.custom_video_prompt,
            generation_count=asset.prompts.generation_count,
            last_generated_at=asset.prompts.last_generated_at
        )
    
    translations = [
        AssetTranslationResponse(
            id=t.id,
            asset_id=asset.id,
            language=t.language,
            display_name=t.display_name
        )
        for t in asset.translations
    ]
    
    return AssetResponse(
        id=asset.id,
        univers_id=asset.univers_id,
        sort_order=asset.sort_order,
        image_name=asset.image_name,
        display_name=asset.display_name,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        prompts=prompts,
        translations=translations,
        image_url=storage_service.get_asset_image_url(slug, asset.image_name),
        video_url=storage_service.get_asset_video_url(slug, asset.image_name)
    )
