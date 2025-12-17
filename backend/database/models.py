"""SQLAlchemy ORM models - Mirror of Supabase PostgreSQL schema."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


# ============================================================================
# ENUMS
# ============================================================================

class JobStatus(str, PyEnum):
    """Status of async generation jobs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Language(str, PyEnum):
    """Supported languages for translations."""
    FR = "fr"
    EN = "en"
    ES = "es"
    IT = "it"
    DE = "de"


# ============================================================================
# UNIVERS (Main entity)
# ============================================================================

class Univers(Base):
    """Universe entity - collection of themed assets."""
    __tablename__ = "univers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True, index=True)
    thumbnail_url = Column(Text)
    is_public = Column(Boolean, default=True)
    owner_id = Column(String(36))  # UUID as string
    background_music = Column(Text)
    background_color = Column(Text)
    
    # Sync metadata
    supabase_id = Column(BigInteger, nullable=True)  # ID in Supabase (for sync)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assets = relationship(
        "UniversAsset",
        back_populates="univers",
        cascade="all, delete-orphan",
        order_by="UniversAsset.sort_order"
    )
    prompts = relationship(
        "UniversPrompts",
        back_populates="univers",
        cascade="all, delete-orphan",
        uselist=False  # One-to-one
    )
    translations = relationship(
        "UniversTranslation",
        back_populates="univers",
        cascade="all, delete-orphan"
    )
    music_prompts = relationship(
        "UniversMusicPrompts",
        back_populates="univers",
        cascade="all, delete-orphan"
    )


# ============================================================================
# UNIVERS PROMPTS (Default prompts for universe)
# ============================================================================

class UniversPrompts(Base):
    """Default prompts for image/video generation in a universe."""
    __tablename__ = "univers_prompts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    univers_id = Column(BigInteger, ForeignKey("univers.id", ondelete="CASCADE"), nullable=False)
    default_image_prompt = Column(Text)
    default_video_prompt = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    univers = relationship("Univers", back_populates="prompts")


# ============================================================================
# UNIVERS TRANSLATIONS
# ============================================================================

class UniversTranslation(Base):
    """Translations of universe name in different languages."""
    __tablename__ = "univers_translations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    univers_id = Column(BigInteger, ForeignKey("univers.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(2), nullable=False)
    name = Column(Text, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "language IN ('fr', 'en', 'es', 'it', 'de')",
            name="valid_language"
        ),
    )
    
    # Relationships
    univers = relationship("Univers", back_populates="translations")


# ============================================================================
# UNIVERS ASSETS
# ============================================================================

class UniversAsset(Base):
    """Individual asset within a universe (image + video + name)."""
    __tablename__ = "univers_assets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    univers_id = Column(BigInteger, ForeignKey("univers.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, nullable=False)
    image_name = Column(Text, nullable=False)  # Filename in storage
    display_name = Column(Text, nullable=False)  # Default display name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    univers = relationship("Univers", back_populates="assets")
    prompts = relationship(
        "UniversAssetPrompts", 
        back_populates="asset", 
        cascade="all, delete-orphan",
        uselist=False  # One-to-one
    )
    translations = relationship(
        "UniversAssetTranslation", 
        back_populates="asset", 
        cascade="all, delete-orphan"
    )


# ============================================================================
# UNIVERS ASSETS PROMPTS
# ============================================================================

class UniversAssetPrompts(Base):
    """Custom prompts for a specific asset's image/video generation."""
    __tablename__ = "univers_assets_prompts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("univers_assets.id", ondelete="CASCADE"), nullable=False, unique=True)
    custom_image_prompt = Column(Text)
    custom_video_prompt = Column(Text)
    generation_count = Column(Integer, default=1)
    last_generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("UniversAsset", back_populates="prompts")


# ============================================================================
# UNIVERS ASSETS TRANSLATIONS
# ============================================================================

class UniversAssetTranslation(Base):
    """Translations of asset display name in different languages."""
    __tablename__ = "univers_assets_translations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("univers_assets.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(2), nullable=False)
    display_name = Column(Text, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "language IN ('fr', 'en', 'es', 'it', 'de')",
            name="valid_asset_language"
        ),
    )

    # Relationships
    asset = relationship("UniversAsset", back_populates="translations")


# ============================================================================
# UNIVERS MUSIC PROMPTS
# ============================================================================

class UniversMusicPrompts(Base):
    """Music prompts and lyrics for each language."""
    __tablename__ = "univers_music_prompts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    univers_id = Column(BigInteger, ForeignKey("univers.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(2), nullable=False)
    prompt = Column(Text, nullable=False)
    lyrics = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "language IN ('fr', 'en', 'es', 'it', 'de')",
            name="valid_music_language"
        ),
        UniqueConstraint("univers_id", "language", name="unique_music_prompt_per_lang"),
    )

    # Relationships
    univers = relationship("Univers", back_populates="music_prompts")


# ============================================================================
# JOBS (Persistent async job tracking)
# ============================================================================

class Job(Base):
    """Persistent job tracking for async operations."""
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(50), nullable=False)  # e.g., "generate_images", "generate_videos"
    univers_slug = Column(String(100), nullable=True)  # Related universe
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    total_steps = Column(Integer, default=0)
    current_step = Column(Integer, default=0)
    message = Column(Text)
    error = Column(Text)
    result = Column(Text)  # JSON serialized result
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
