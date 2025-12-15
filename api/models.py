"""
Modèles Pydantic pour la gestion des univers
"""
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class UniverseStatus(str, Enum):
    """Statut d'un univers"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


class PromptDefaults(BaseModel):
    """Prompts par défaut pour un univers"""
    image: Optional[str] = None
    video: Optional[str] = None
    
    
class AssetMetadata(BaseModel):
    """Métadonnées d'un asset individuel"""
    id: str = Field(..., description="ID de l'asset (ex: '01', '02')")
    display_name: str = Field(..., description="Nom affiché de l'asset")
    sort_order: int = Field(..., description="Ordre d'affichage")
    image_prompt: Optional[str] = Field(None, description="Prompt personnalisé pour l'image")
    video_prompt: Optional[str] = Field(None, description="Prompt personnalisé pour la vidéo")
    generated_at: Optional[datetime] = Field(None, description="Date de génération")
    image_file: Optional[str] = Field(None, description="Nom du fichier image")
    video_file: Optional[str] = Field(None, description="Nom du fichier vidéo")


class UniverseMetadata(BaseModel):
    """Métadonnées d'un univers"""
    folder: str = Field(..., description="Nom du dossier de l'univers")
    name: str = Field(..., description="Nom de l'univers")
    theme: str = Field(..., description="Thème de l'univers (jungle, ocean, space, etc.)")
    slug: str = Field(default="", description="Slug pour l'URL")
    status: UniverseStatus = Field(default=UniverseStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    background_color: Optional[str] = Field(None, description="Couleur de fond (hex)")
    thumbnail_url: Optional[str] = Field(None, description="URL de la miniature")
    default_prompts: Optional[PromptDefaults] = Field(None, description="Prompts par défaut de l'univers")
    num_assets: int = Field(default=0, description="Nombre d'assets générés")
    music_lyrics: Optional[Dict[str, str]] = Field(None, description="Paroles de musique par langue (ex: {'fr': 'paroles...'})")


class CreateUniverseRequest(BaseModel):
    """Requête de création d'un univers"""
    name: str = Field(..., description="Nom de l'univers", min_length=1)
    theme: str = Field(..., description="Thème de l'univers")
    custom_prompts: Optional[PromptDefaults] = Field(None, description="Prompts personnalisés (optionnel)")


class GenerateAssetsRequest(BaseModel):
    """Requête de génération d'assets"""
    num_assets: int = Field(default=10, description="Nombre d'assets à générer", ge=1, le=20)
    force_regenerate: bool = Field(default=False, description="Forcer la régénération si assets existent déjà")


class RegenerateAssetRequest(BaseModel):
    """Requête de régénération d'un asset"""
    new_image_prompt: Optional[str] = Field(None, description="Nouveau prompt pour l'image")
    new_video_prompt: Optional[str] = Field(None, description="Nouveau prompt pour la vidéo")
    regenerate_video: bool = Field(default=True, description="Régénérer aussi la vidéo")


class PublishResponse(BaseModel):
    """Réponse de publication vers Supabase"""
    univers_id: int = Field(..., description="ID de l'univers dans Supabase")
    slug: str = Field(..., description="Slug de l'univers")
    published_at: datetime = Field(..., description="Date de publication")
    assets_count: int = Field(..., description="Nombre d'assets publiés")
    storage_url: str = Field(..., description="URL du bucket Supabase")


class UniverseListItem(BaseModel):
    """Item pour la liste des univers"""
    folder: str = Field(..., description="Nom du dossier")
    name: str
    theme: str
    slug: str = ""
    status: UniverseStatus
    created_at: datetime
    updated_at: datetime
    num_assets: int
    thumbnail_path: Optional[str] = None


class GenerationProgress(BaseModel):
    """Progression de génération"""
    folder: str
    status: UniverseStatus
    current_step: str = Field(..., description="Étape en cours")
    progress: int = Field(..., description="Progression en %", ge=0, le=100)
    total_assets: int
    generated_assets: int
    failed_assets: int = 0
    message: Optional[str] = None
