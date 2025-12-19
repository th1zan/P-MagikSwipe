"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS
# ============================================================================

class JobStatusEnum(str, Enum):
    """Status of async generation jobs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class LanguageEnum(str, Enum):
    """Supported languages for translations."""
    FR = "fr"
    EN = "en"
    ES = "es"
    IT = "it"
    DE = "de"


# ============================================================================
# TRANSLATION SCHEMAS
# ============================================================================

class TranslationBase(BaseModel):
    """Base translation schema."""
    language: LanguageEnum
    name: str  # For univers
    

class TranslationCreate(TranslationBase):
    """Create translation."""
    pass


class TranslationResponse(TranslationBase):
    """Translation response."""
    id: str
    
    class Config:
        from_attributes = True


class AssetTranslationBase(BaseModel):
    """Base asset translation schema."""
    language: LanguageEnum
    display_name: str


class AssetTranslationCreate(AssetTranslationBase):
    """Create asset translation."""
    pass


class AssetTranslationResponse(AssetTranslationBase):
    """Asset translation response."""
    id: str
    asset_id: str
    
    class Config:
        from_attributes = True


# ============================================================================
# PROMPTS SCHEMAS
# ============================================================================

class UniversPromptsBase(BaseModel):
    """Base prompts schema."""
    default_image_prompt: Optional[str] = None
    default_video_prompt: Optional[str] = None


class UniversPromptsCreate(UniversPromptsBase):
    """Create prompts."""
    pass


class UniversPromptsResponse(UniversPromptsBase):
    """Prompts response."""
    id: str
    univers_id: int
    
    class Config:
        from_attributes = True


class AssetPromptsBase(BaseModel):
    """Base asset prompts schema."""
    custom_image_prompt: Optional[str] = None
    custom_video_prompt: Optional[str] = None


class AssetPromptsCreate(AssetPromptsBase):
    """Create asset prompts."""
    pass


class AssetPromptsResponse(AssetPromptsBase):
    """Asset prompts response."""
    id: str
    asset_id: str
    generation_count: int = 1
    last_generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# MUSIC PROMPTS SCHEMAS
# ============================================================================

class UniversMusicPromptsBase(BaseModel):
    """Base music prompts schema."""
    language: LanguageEnum
    prompt: str
    lyrics: str


class UniversMusicPromptsCreate(UniversMusicPromptsBase):
    """Create music prompts."""
    pass


class UniversMusicPromptsUpdate(BaseModel):
    """Update music prompts."""
    prompt: Optional[str] = None
    lyrics: Optional[str] = None


class UniversMusicPromptsResponse(UniversMusicPromptsBase):
    """Music prompts response."""
    id: str
    univers_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# ASSET SCHEMAS
# ============================================================================

class AssetBase(BaseModel):
    """Base asset schema."""
    sort_order: int
    image_name: str
    display_name: str


class AssetCreate(BaseModel):
    """Create asset request."""
    display_name: str
    sort_order: Optional[int] = None
    translations: Optional[Dict[str, str]] = None  # {lang: display_name}
    custom_image_prompt: Optional[str] = None
    custom_video_prompt: Optional[str] = None


class AssetUpdate(BaseModel):
    """Update asset request."""
    display_name: Optional[str] = None
    sort_order: Optional[int] = None
    translations: Optional[Dict[str, str]] = None
    custom_image_prompt: Optional[str] = None
    custom_video_prompt: Optional[str] = None


class AssetResponse(AssetBase):
    """Asset response with relations."""
    id: str
    univers_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    prompts: Optional[AssetPromptsResponse] = None
    translations: List[AssetTranslationResponse] = []
    
    # Computed URLs
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Asset list item (lighter)."""
    id: str
    sort_order: int
    display_name: str
    image_name: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# UNIVERS SCHEMAS
# ============================================================================

class UniversBase(BaseModel):
    """Base univers schema."""
    name: str
    slug: str
    thumbnail_url: Optional[str] = None
    is_public: bool = True
    background_music: Optional[str] = None
    background_color: Optional[str] = None


class UniversCreate(BaseModel):
    """Create univers request."""
    name: str
    slug: Optional[str] = None  # Auto-generated from name if not provided
    is_public: bool = True
    background_color: Optional[str] = "#1a1a2e"
    default_image_prompt: Optional[str] = None
    default_video_prompt: Optional[str] = None
    translations: Optional[Dict[str, str]] = None  # {lang: name}


class UniversUpdate(BaseModel):
    """Update univers request."""
    name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_public: Optional[bool] = None
    background_music: Optional[str] = None
    background_color: Optional[str] = None
    default_image_prompt: Optional[str] = None
    default_video_prompt: Optional[str] = None
    translations: Optional[Dict[str, str]] = None


class UniversResponse(UniversBase):
    """Univers response with relations."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    supabase_id: Optional[int] = None
    last_synced_at: Optional[datetime] = None
    prompts: Optional[UniversPromptsResponse] = None
    translations: List[TranslationResponse] = []
    music_prompts: List[UniversMusicPromptsResponse] = []
    assets: List[AssetListResponse] = []
    asset_count: int = 0
    
    class Config:
        from_attributes = True


class UniversListItem(BaseModel):
    """Univers list item (lighter)."""
    id: int
    name: str
    slug: str
    thumbnail_url: Optional[str] = None
    is_public: bool
    asset_count: int = 0
    last_synced_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UniversListResponse(BaseModel):
    """Paginated univers list."""
    items: List[UniversListItem]
    total: int


# ============================================================================
# JOB SCHEMAS
# ============================================================================

class JobCreate(BaseModel):
    """Create job request (internal)."""
    type: str
    univers_slug: Optional[str] = None
    total_steps: int = 0


class JobUpdate(BaseModel):
    """Update job progress (internal)."""
    status: Optional[JobStatusEnum] = None
    progress: Optional[int] = None
    current_step: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None
    result: Optional[str] = None


class JobResponse(BaseModel):
    """Job status response."""
    id: str
    type: str
    univers_slug: Optional[str] = None
    status: JobStatusEnum
    progress: int
    total_steps: int
    current_step: int
    message: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# GENERATION SCHEMAS
# ============================================================================

class GenerateConceptsRequest(BaseModel):
    """Request to generate concepts for a universe."""
    theme: str
    count: int = Field(default=10, ge=1, le=50)
    language: LanguageEnum = LanguageEnum.FR


class GenerateConceptsResponse(BaseModel):
    """Response with generated concepts."""
    concepts: List[str]
    translations: Dict[str, List[str]]  # {lang: [translated_concepts]}


class GenerateImagesRequest(BaseModel):
    """Request to generate images for assets."""
    asset_ids: Optional[List[str]] = None  # None = all assets
    regenerate: bool = False


class GenerateVideosRequest(BaseModel):
    """Request to generate videos for assets."""
    asset_ids: Optional[List[str]] = None
    regenerate: bool = False


class GenerateMusicRequest(BaseModel):
    """Request to generate background music."""
    language: LanguageEnum = LanguageEnum.FR
    style: str = Field(min_length=10, max_length=300, default="children friendly, playful")


class GenerateAllRequest(BaseModel):
    """Request to generate complete universe content."""
    theme: str
    count: int = Field(default=10, ge=1, le=50)
    generate_videos: bool = True
    generate_music: bool = True
    regenerate: bool = False


# ============================================================================
# SYNC SCHEMAS
# ============================================================================

class SyncRequest(BaseModel):
    """Request to sync with Supabase."""
    force: bool = False  # Force overwrite even if newer


class SyncResponse(BaseModel):
    """Sync operation result."""
    success: bool
    message: str
    synced_items: int = 0
    errors: List[str] = []


class SyncInitResponse(BaseModel):
    """Init sync response."""
    success: bool
    message: str
    universes_synced: int = 0
    assets_synced: int = 0
    files_downloaded: int = 0
