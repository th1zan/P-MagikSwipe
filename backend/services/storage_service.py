"""Local storage service - Manages files in local bucket (mirrors Supabase Storage)."""
import os
import shutil
import mimetypes
from pathlib import Path
from typing import Optional, List, BinaryIO, Union
from config import settings


class StorageService:
    """
    Manages local file storage mirroring Supabase Storage bucket structure.
    
    Structure (flat):
        /storage/buckets/univers/{slug}/
            ├── thumbnail.jpg
            ├── asset_001.png
            ├── asset_001.mp4
            ├── fr.mp3
            ├── en.mp3
            └── ...
    """
    
    def __init__(self):
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
        self.bucket_path = settings.BUCKETS_PATH / self.bucket_name
        self.bucket_path.mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # PATH HELPERS
    # =========================================================================
    
    def get_universe_path(self, slug: str) -> Path:
        """Get local path for a universe folder."""
        return self.bucket_path / slug
    
    def get_asset_image_path(self, slug: str, image_name: str) -> Path:
        """Get full path for an asset image (flat structure)."""
        return self.get_universe_path(slug) / image_name

    def get_asset_video_path(self, slug: str, image_name: str) -> Path:
        """Get full path for an asset video (same name, .mp4 extension, flat structure)."""
        video_name = Path(image_name).stem + ".mp4"
        return self.get_universe_path(slug) / video_name
    
    def get_thumbnail_path(self, slug: str) -> Path:
        """Get path for universe thumbnail."""
        return self.get_universe_path(slug) / "thumbnail.jpg"
    
    def get_music_file_path(self, slug: str, language: str) -> Path:
        """Get path for music file in a specific language (flat structure)."""
        return self.get_universe_path(slug) / f"{language}.mp3"
    
    # =========================================================================
    # URL GENERATION (for API responses)
    # =========================================================================
    
    def get_public_url(self, remote_path: str) -> str:
        """
        Get public URL for a file (served by FastAPI StaticFiles).

        Args:
            remote_path: Path relative to bucket (e.g., "jungle/asset_001.png")

        Returns:
            URL like "/storage/buckets/univers/jungle/asset_001.png"
        """
        return f"/storage/buckets/{self.bucket_name}/{remote_path}"

    def get_asset_image_url(self, slug: str, image_name: str) -> Optional[str]:
        """Get public URL for an asset image if it exists."""
        path = self.get_asset_image_path(slug, image_name)
        if path.exists():
            return self.get_public_url(f"{slug}/{image_name}")
        return None

    def get_asset_video_url(self, slug: str, image_name: str) -> Optional[str]:
        """Get public URL for an asset video if it exists."""
        video_name = Path(image_name).stem + ".mp4"
        path = self.get_asset_video_path(slug, image_name)
        if path.exists():
            return self.get_public_url(f"{slug}/{video_name}")
        return None

    def get_thumbnail_url(self, slug: str) -> Optional[str]:
        """Get public URL for universe thumbnail if it exists."""
        path = self.get_thumbnail_path(slug)
        if path.exists():
            return self.get_public_url(f"{slug}/thumbnail.jpg")
        return None

    def get_music_url(self, slug: str, language: str) -> Optional[str]:
        """Get public URL for music file if it exists."""
        path = self.get_music_file_path(slug, language)
        if path.exists():
            return self.get_public_url(f"{slug}/{language}.mp3")
        return None
    
    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================
    
    def upload_file(
        self,
        content: Union[bytes, BinaryIO, Path],
        remote_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload/save a file to local storage.
        
        Args:
            content: File content (bytes, file object, or source Path)
            remote_path: Path relative to bucket (e.g., "jungle/assets/image.png")
            content_type: MIME type (optional)
        
        Returns:
            Public URL of the uploaded file
        """
        local_path = self.bucket_path / remote_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(content, Path):
            shutil.copy(content, local_path)
        elif isinstance(content, bytes):
            local_path.write_bytes(content)
        else:
            # File-like object
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(content, f)
        
        return self.get_public_url(remote_path)
    
    def download_file(self, remote_path: str) -> Optional[bytes]:
        """
        Download/read a file from local storage.
        
        Args:
            remote_path: Path relative to bucket
        
        Returns:
            File content as bytes, or None if not found
        """
        local_path = self.bucket_path / remote_path
        if local_path.exists():
            return local_path.read_bytes()
        return None
    
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from local storage.
        
        Args:
            remote_path: Path relative to bucket
        
        Returns:
            True if deleted, False if not found
        """
        local_path = self.bucket_path / remote_path
        if local_path.exists():
            local_path.unlink()
            return True
        return False
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if a file exists in local storage."""
        local_path = self.bucket_path / remote_path
        return local_path.exists()
    
    # =========================================================================
    # DIRECTORY OPERATIONS
    # =========================================================================
    
    def create_universe_folder(self, slug: str) -> Path:
        """Create folder structure for a new universe (flat structure)."""
        universe_path = self.get_universe_path(slug)
        universe_path.mkdir(parents=True, exist_ok=True)
        # Plus de sous-dossiers - structure plate
        return universe_path
    
    def delete_universe_folder(self, slug: str) -> bool:
        """Delete entire universe folder and all contents."""
        universe_path = self.get_universe_path(slug)
        if universe_path.exists():
            shutil.rmtree(universe_path)
            return True
        return False
    
    def list_universe_folders(self) -> List[str]:
        """List all universe slugs in storage."""
        if not self.bucket_path.exists():
            return []
        
        return [
            d.name for d in self.bucket_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    def list_universe_files(self, slug: str, subfolder: str = "") -> List[str]:
        """
        List all files in a universe folder.
        
        Args:
            slug: Universe slug
            subfolder: Optional subfolder ("assets", "music", etc.)
        
        Returns:
            List of filenames
        """
        path = self.get_universe_path(slug)
        if subfolder:
            path = path / subfolder
        
        if not path.exists():
            return []
        
        return [f.name for f in path.iterdir() if f.is_file()]
    
    def list_assets(self, slug: str) -> List[dict]:
        """
        List all assets in a universe with their URLs (flat structure).

        Returns:
            List of dicts with {image_name, image_url, video_url}
        """
        universe_path = self.get_universe_path(slug)
        if not universe_path.exists():
            return []

        # Group by base name (image + optional video)
        assets = {}
        for f in universe_path.iterdir():
            if f.is_file():
                stem = f.stem
                ext = f.suffix.lower()

                if stem not in assets:
                    assets[stem] = {"image_name": None, "image_url": None, "video_url": None}

                if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                    assets[stem]["image_name"] = f.name
                    assets[stem]["image_url"] = self.get_public_url(f"{slug}/{f.name}")
                elif ext in ['.mp4', '.webm']:
                    assets[stem]["video_url"] = self.get_public_url(f"{slug}/{f.name}")

        return list(assets.values())
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """Get file size in bytes."""
        local_path = self.bucket_path / remote_path
        if local_path.exists():
            return local_path.stat().st_size
        return None
    
    def get_mime_type(self, remote_path: str) -> Optional[str]:
        """Get MIME type of a file."""
        mime_type, _ = mimetypes.guess_type(remote_path)
        return mime_type
    
    def copy_file(self, source_path: str, dest_path: str) -> str:
        """Copy a file within the bucket."""
        src = self.bucket_path / source_path
        dst = self.bucket_path / dest_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        return self.get_public_url(dest_path)


# Singleton instance
storage_service = StorageService()
