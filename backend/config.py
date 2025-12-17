"""Configuration settings for the backend."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Storage paths
    STORAGE_PATH: Path = Path("/app/storage")
    DB_PATH: Path = Path("/app/storage/db/local.db")
    BUCKETS_PATH: Path = Path("/app/storage/buckets")
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_BUCKET_NAME: str = "univers"
    
    # Replicate AI
    REPLICATE_API_TOKEN: str = ""
    
    # Sync settings
    SYNC_MODE: str = "last_write_wins"  # Options: last_write_wins, timestamp_merge
    
    # Server
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Ensure directories exist
settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
settings.BUCKETS_PATH.mkdir(parents=True, exist_ok=True)
(settings.BUCKETS_PATH / "univers").mkdir(parents=True, exist_ok=True)
