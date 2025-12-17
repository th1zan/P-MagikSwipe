"""Generation routes - AI content generation endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db, Univers, UniversAsset, UniversAssetPrompts, UniversAssetTranslation
from schemas import (
    GenerateConceptsRequest, GenerateConceptsResponse,
    GenerateImagesRequest, GenerateVideosRequest,
    GenerateMusicRequest, GenerateAllRequest,
    JobResponse
)
from services.generation_service import generation_service
from services.job_service import job_service
from services.storage_service import storage_service

router = APIRouter(prefix="/generate", tags=["generation"])


# =============================================================================
# CONCEPT GENERATION
# =============================================================================

@router.post("/{slug}/concepts", response_model=GenerateConceptsResponse)
def generate_concepts(
    slug: str,
    data: GenerateConceptsRequest,
    db: Session = Depends(get_db)
):
    """
    Generate concepts for a universe theme.
    
    This is synchronous and returns immediately with concepts + translations.
    Use this before creating assets.
    """
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    if not generation_service.is_available:
        raise HTTPException(status_code=503, detail="AI generation not available - REPLICATE_API_TOKEN not configured")
    
    try:
        # Generate concepts
        concepts = generation_service.generate_concepts(
            theme=data.theme,
            count=data.count,
            language=data.language.value
        )
        
        # Translate to all languages
        translations = generation_service.translate_concepts(
            concepts,
            source_lang=data.language.value
        )
        
        return GenerateConceptsResponse(
            concepts=concepts,
            translations=translations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/{slug}/concepts/apply", response_model=dict)
def apply_concepts(
    slug: str,
    data: GenerateConceptsResponse,
    db: Session = Depends(get_db)
):
    """
    Apply generated concepts to create assets in the database.
    
    Call this after generate_concepts to create the asset entries.
    """
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    # Delete existing assets
    db.query(UniversAsset).filter(UniversAsset.univers_id == univers.id).delete()
    
    # Create new assets from concepts
    created = 0
    for i, concept in enumerate(data.concepts):
        # Use consistent naming: XX_concept.png (matching existing files)
        concept_slug = concept.lower().replace(' ', '_').replace('-', '_')
        image_name = f"{i:02d}_{concept_slug}.png"
        
        asset = UniversAsset(
            univers_id=univers.id,
            sort_order=i + 1,
            image_name=image_name,
            display_name=concept
        )
        db.add(asset)
        db.flush()
        
        # Add translations
        for lang, translated_list in data.translations.items():
            if i < len(translated_list):
                trans = UniversAssetTranslation(
                    asset_id=asset.id,
                    language=lang,
                    display_name=translated_list[i]
                )
                db.add(trans)
        
        created += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Created {created} assets",
        "asset_count": created
    }


# =============================================================================
# IMAGE GENERATION
# =============================================================================

@router.post("/{slug}/images", response_model=JobResponse)
def generate_images(
    slug: str,
    data: GenerateImagesRequest = GenerateImagesRequest(),
    db: Session = Depends(get_db)
):
    """
    Generate images for assets (async job).
    
    Returns a job ID to track progress.
    """
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    if not generation_service.is_available:
        raise HTTPException(status_code=503, detail="AI generation not available")
    
    # Get assets to generate
    if data.asset_ids:
        assets = db.query(UniversAsset)\
            .filter(UniversAsset.univers_id == univers.id)\
            .filter(UniversAsset.id.in_(data.asset_ids))\
            .order_by(UniversAsset.sort_order)\
            .all()
    else:
        assets = univers.assets
    
    if not assets:
        raise HTTPException(status_code=400, detail="No assets to generate images for")
    
    # Prepare data for job
    concepts = [a.display_name for a in assets]
    prompts = []
    for a in assets:
        if a.prompts and a.prompts.custom_image_prompt:
            prompts.append(a.prompts.custom_image_prompt)
        elif univers.prompts and univers.prompts.default_image_prompt:
            prompts.append(univers.prompts.default_image_prompt.replace("{concept}", a.display_name))
        else:
            prompts.append(None)
    
    # Create and run job
    def task(job_id):
        return generation_service.generate_all_images(
            slug=slug,
            concepts=concepts,
            prompts=prompts,
            job_id=job_id,
            theme_context=univers.name
        )
    
    job = job_service.run_async(
        db=db,
        job_type="generate_images",
        task_func=task,
        univers_slug=slug,
        total_steps=len(assets)
    )
    
    return JobResponse(
        id=job.id,
        type=job.type,
        univers_slug=job.univers_slug,
        status=job.status,
        progress=job.progress,
        total_steps=job.total_steps,
        current_step=job.current_step,
        message=job.message,
        created_at=job.created_at
    )


# =============================================================================
# VIDEO GENERATION
# =============================================================================

@router.post("/{slug}/videos", response_model=JobResponse)
def generate_videos(
    slug: str,
    data: GenerateVideosRequest = GenerateVideosRequest(),
    db: Session = Depends(get_db)
):
    """
    Generate videos from images (async job).
    
    Requires images to be generated first.
    """
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    if not generation_service.is_available:
        raise HTTPException(status_code=503, detail="AI generation not available")
    
    # Get assets
    if data.asset_ids:
        assets = db.query(UniversAsset)\
            .filter(UniversAsset.univers_id == univers.id)\
            .filter(UniversAsset.id.in_(data.asset_ids))\
            .order_by(UniversAsset.sort_order)\
            .all()
    else:
        assets = univers.assets
    
    if not assets:
        raise HTTPException(status_code=400, detail="No assets to generate videos for")
    
    # Check images exist
    universe_path = storage_service.get_universe_path(slug)
    existing_images = [f for f in universe_path.iterdir() if f.suffix == ".png"] if universe_path.exists() else []
    
    if not existing_images:
        raise HTTPException(status_code=400, detail="No images found. Generate images first.")
    
    # Prepare data
    concepts = [a.display_name for a in assets]
    prompts = []
    for a in assets:
        if a.prompts and a.prompts.custom_video_prompt:
            prompts.append(a.prompts.custom_video_prompt)
        elif univers.prompts and univers.prompts.default_video_prompt:
            prompts.append(univers.prompts.default_video_prompt.replace("{concept}", a.display_name))
        else:
            prompts.append(None)
    
    # Create and run job
    def task(job_id):
        return generation_service.generate_all_videos(
            slug=slug,
            concepts=concepts,
            prompts=prompts,
            job_id=job_id
        )
    
    job = job_service.run_async(
        db=db,
        job_type="generate_videos",
        task_func=task,
        univers_slug=slug,
        total_steps=len(existing_images)
    )
    
    return JobResponse(
        id=job.id,
        type=job.type,
        univers_slug=job.univers_slug,
        status=job.status,
        progress=job.progress,
        total_steps=job.total_steps,
        current_step=job.current_step,
        message=job.message,
        created_at=job.created_at
    )


# =============================================================================
# MUSIC GENERATION
# =============================================================================

@router.post("/{slug}/music", response_model=JobResponse)
def generate_music(
    slug: str,
    data: GenerateMusicRequest,
    db: Session = Depends(get_db)
):
    """Generate background music for a specific language."""
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    if not generation_service.is_available:
        raise HTTPException(status_code=503, detail="AI generation not available")
    
    def task(job_id):
        return str(generation_service.generate_music(
            slug=slug,
            language=data.language.value,
            style=data.style
        ))
    
    job = job_service.run_async(
        db=db,
        job_type="generate_music",
        task_func=task,
        univers_slug=slug,
        total_steps=1
    )
    
    return JobResponse(
        id=job.id,
        type=job.type,
        univers_slug=job.univers_slug,
        status=job.status,
        progress=job.progress,
        total_steps=job.total_steps,
        current_step=job.current_step,
        message=job.message,
        created_at=job.created_at
    )


# =============================================================================
# FULL GENERATION
# =============================================================================

@router.post("/{slug}/all", response_model=JobResponse)
def generate_all(
    slug: str,
    data: GenerateAllRequest,
    db: Session = Depends(get_db)
):
    """
    Generate complete universe content (concepts, images, videos, music).
    
    This is a full pipeline that:
    1. Generates concepts from theme
    2. Creates assets with translations
    3. Generates images
    4. Generates videos (optional)
    5. Generates music (optional)
    """
    univers = db.query(Univers).filter(Univers.slug == slug).first()
    
    if not univers:
        raise HTTPException(status_code=404, detail=f"Universe '{slug}' not found")
    
    if not generation_service.is_available:
        raise HTTPException(status_code=503, detail="AI generation not available")
    
    def task(job_id):
        # Generate content
        result = generation_service.generate_universe_content(
            slug=slug,
            theme=data.theme,
            concept_count=data.count,
            generate_videos=data.generate_videos,
            generate_music=data.generate_music,
            job_id=job_id
        )
        
        # Create assets in database
        from database import SessionLocal
        db_session = SessionLocal()
        try:
            # Get fresh universe
            univ = db_session.query(Univers).filter(Univers.slug == slug).first()
            
            # Delete existing assets
            db_session.query(UniversAsset).filter(UniversAsset.univers_id == univ.id).delete()
            
            # Create new assets
            for i, concept in enumerate(result["concepts"]):
                asset = UniversAsset(
                    univers_id=univ.id,
                    sort_order=i + 1,
                    image_name=f"asset_{i+1:03d}.png",
                    display_name=concept
                )
                db_session.add(asset)
                db_session.flush()
                
                # Add translations
                for lang, translations in result["translations"].items():
                    if i < len(translations):
                        trans = UniversAssetTranslation(
                            asset_id=asset.id,
                            language=lang,
                            display_name=translations[i]
                        )
                        db_session.add(trans)
            
            db_session.commit()
        finally:
            db_session.close()
        
        return result
    
    # Estimate total steps
    total = data.count * 2  # concepts + images
    if data.generate_videos:
        total += data.count
    if data.generate_music:
        total += 5  # 5 languages
    
    job = job_service.run_async(
        db=db,
        job_type="generate_all",
        task_func=task,
        univers_slug=slug,
        total_steps=total
    )
    
    return JobResponse(
        id=job.id,
        type=job.type,
        univers_slug=job.univers_slug,
        status=job.status,
        progress=job.progress,
        total_steps=job.total_steps,
        current_step=job.current_step,
        message=job.message,
        created_at=job.created_at
    )
