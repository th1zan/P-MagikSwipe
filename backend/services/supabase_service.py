"""Supabase service - Interface with Supabase DB and Storage."""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from config import settings


class SupabaseService:
    """
    Interface with Supabase for:
    - PostgreSQL database (univers, assets, translations, prompts)
    - Storage bucket (media files)
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Supabase client if credentials are available."""
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            try:
                self.client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize Supabase: {e}")
                self.client = None
        else:
            print("ℹ️ Supabase credentials not configured - running in local-only mode")
    
    @property
    def is_connected(self) -> bool:
        """Check if Supabase client is available."""
        return self.client is not None
    
    def _require_client(self):
        """Raise error if client not available."""
        if not self.client:
            raise ConnectionError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    
    # =========================================================================
    # UNIVERS OPERATIONS
    # =========================================================================
    
    def get_all_univers(self) -> List[Dict[str, Any]]:
        """Fetch all universes from Supabase."""
        self._require_client()
        
        response = self.client.table("univers")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        
        return response.data
    
    def get_univers_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Fetch a universe by slug."""
        self._require_client()
        
        response = self.client.table("univers")\
            .select("*")\
            .eq("slug", slug)\
            .single()\
            .execute()
        
        return response.data if response.data else None
    
    def get_univers_by_id(self, univers_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a universe by ID."""
        self._require_client()
        
        response = self.client.table("univers")\
            .select("*")\
            .eq("id", univers_id)\
            .single()\
            .execute()
        
        return response.data if response.data else None
    
    def upsert_univers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a universe (by slug)."""
        self._require_client()
        
        response = self.client.table("univers")\
            .upsert(data, on_conflict="slug")\
            .execute()
        
        return response.data[0] if response.data else None
    
    def delete_univers(self, univers_id: int) -> bool:
        """Delete a universe by ID."""
        self._require_client()
        
        self.client.table("univers")\
            .delete()\
            .eq("id", univers_id)\
            .execute()
        
        return True
    
    # =========================================================================
    # UNIVERS PROMPTS OPERATIONS
    # =========================================================================
    
    def get_univers_prompts(self, univers_id: int) -> Optional[Dict[str, Any]]:
        """Fetch prompts for a universe."""
        self._require_client()
        
        response = self.client.table("univers_prompts")\
            .select("*")\
            .eq("univers_id", univers_id)\
            .execute()
        
        return response.data[0] if response.data else None
    
    def upsert_univers_prompts(self, univers_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update universe prompts."""
        self._require_client()
        
        data["univers_id"] = univers_id
        
        response = self.client.table("univers_prompts")\
            .upsert(data, on_conflict="univers_id")\
            .execute()
        
        return response.data[0] if response.data else None
    
    # =========================================================================
    # UNIVERS TRANSLATIONS OPERATIONS
    # =========================================================================
    
    def get_univers_translations(self, univers_id: int) -> List[Dict[str, Any]]:
        """Fetch all translations for a universe."""
        self._require_client()
        
        response = self.client.table("univers_translations")\
            .select("*")\
            .eq("univers_id", univers_id)\
            .execute()
        
        return response.data
    
    def upsert_univers_translation(self, univers_id: int, language: str, name: str) -> Dict[str, Any]:
        """Insert or update a universe translation."""
        self._require_client()
        
        # Check if exists
        existing = self.client.table("univers_translations")\
            .select("id")\
            .eq("univers_id", univers_id)\
            .eq("language", language)\
            .execute()
        
        data = {
            "univers_id": univers_id,
            "language": language,
            "name": name
        }
        
        if existing.data:
            data["id"] = existing.data[0]["id"]
        
        response = self.client.table("univers_translations")\
            .upsert(data)\
            .execute()
        
        return response.data[0] if response.data else None
    
    def delete_univers_translations(self, univers_id: int):
        """Delete all translations for a universe."""
        self._require_client()
        
        self.client.table("univers_translations")\
            .delete()\
            .eq("univers_id", univers_id)\
            .execute()
    
    # =========================================================================
    # ASSETS OPERATIONS
    # =========================================================================
    
    def get_assets(self, univers_id: int) -> List[Dict[str, Any]]:
        """Fetch all assets for a universe."""
        self._require_client()
        
        response = self.client.table("univers_assets")\
            .select("*")\
            .eq("univers_id", univers_id)\
            .order("sort_order")\
            .execute()
        
        return response.data
    
    def get_asset_by_id(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Fetch an asset by ID."""
        self._require_client()
        
        response = self.client.table("univers_assets")\
            .select("*")\
            .eq("id", asset_id)\
            .single()\
            .execute()
        
        return response.data if response.data else None
    
    def upsert_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update an asset."""
        self._require_client()
        
        response = self.client.table("univers_assets")\
            .upsert(data)\
            .execute()
        
        return response.data[0] if response.data else None
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset by ID."""
        self._require_client()
        
        self.client.table("univers_assets")\
            .delete()\
            .eq("id", asset_id)\
            .execute()
        
        return True
    
    def delete_all_assets(self, univers_id: int):
        """Delete all assets for a universe."""
        self._require_client()
        
        self.client.table("univers_assets")\
            .delete()\
            .eq("univers_id", univers_id)\
            .execute()
    
    # =========================================================================
    # ASSET PROMPTS OPERATIONS
    # =========================================================================
    
    def get_asset_prompts(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Fetch prompts for an asset."""
        self._require_client()
        
        response = self.client.table("univers_assets_prompts")\
            .select("*")\
            .eq("asset_id", asset_id)\
            .execute()
        
        return response.data[0] if response.data else None
    
    def upsert_asset_prompts(self, asset_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update asset prompts."""
        self._require_client()
        
        data["asset_id"] = asset_id
        
        response = self.client.table("univers_assets_prompts")\
            .upsert(data, on_conflict="asset_id")\
            .execute()
        
        return response.data[0] if response.data else None
    
    # =========================================================================
    # ASSET TRANSLATIONS OPERATIONS
    # =========================================================================
    
    def get_asset_translations(self, asset_id: str) -> List[Dict[str, Any]]:
        """Fetch all translations for an asset."""
        self._require_client()
        
        response = self.client.table("univers_assets_translations")\
            .select("*")\
            .eq("asset_id", asset_id)\
            .execute()
        
        return response.data
    
    def upsert_asset_translation(self, asset_id: str, language: str, display_name: str) -> Dict[str, Any]:
        """Insert or update an asset translation."""
        self._require_client()
        
        # Check if exists
        existing = self.client.table("univers_assets_translations")\
            .select("id")\
            .eq("asset_id", asset_id)\
            .eq("language", language)\
            .execute()
        
        data = {
            "asset_id": asset_id,
            "language": language,
            "display_name": display_name
        }
        
        if existing.data:
            data["id"] = existing.data[0]["id"]
        
        response = self.client.table("univers_assets_translations")\
            .upsert(data)\
            .execute()
        
        return response.data[0] if response.data else None
    
    def delete_asset_translations(self, asset_id: str):
        """Delete all translations for an asset."""
        self._require_client()
        
        self.client.table("univers_assets_translations")\
            .delete()\
            .eq("asset_id", asset_id)\
            .execute()
    
    # =========================================================================
    # STORAGE OPERATIONS
    # =========================================================================
    
    def upload_to_storage(
        self,
        file_content: bytes,
        remote_path: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload a file to Supabase Storage.
        
        Args:
            file_content: File bytes
            remote_path: Path in bucket (e.g., "jungle/assets/image.png")
            content_type: MIME type
        
        Returns:
            Public URL of uploaded file
        """
        self._require_client()
        
        bucket = self.client.storage.from_(settings.SUPABASE_BUCKET_NAME)
        
        # Remove existing file if present
        try:
            bucket.remove([remote_path])
        except:
            pass
        
        # Upload new file
        bucket.upload(
            remote_path,
            file_content,
            {"content-type": content_type}
        )
        
        return bucket.get_public_url(remote_path)
    
    def download_from_storage(self, remote_path: str) -> Optional[bytes]:
        """
        Download a file from Supabase Storage.
        
        Args:
            remote_path: Path in bucket
        
        Returns:
            File content as bytes, or None if not found
        """
        self._require_client()
        
        try:
            bucket = self.client.storage.from_(settings.SUPABASE_BUCKET_NAME)
            response = bucket.download(remote_path)
            return response
        except Exception as e:
            print(f"Download failed: {e}")
            return None
    
    def delete_from_storage(self, remote_paths: List[str]) -> bool:
        """Delete files from Supabase Storage."""
        self._require_client()
        
        try:
            bucket = self.client.storage.from_(settings.SUPABASE_BUCKET_NAME)
            bucket.remove(remote_paths)
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False
    
    def list_storage_folder(self, prefix: str) -> List[Dict[str, Any]]:
        """
        List files in a storage folder.
        
        Args:
            prefix: Folder path (e.g., "jungle/assets")
        
        Returns:
            List of file info dicts
        """
        self._require_client()
        
        try:
            bucket = self.client.storage.from_(settings.SUPABASE_BUCKET_NAME)
            response = bucket.list(prefix)
            return response
        except Exception as e:
            print(f"List failed: {e}")
            return []
    
    def get_storage_public_url(self, remote_path: str) -> str:
        """Get public URL for a file in Supabase Storage."""
        self._require_client()
        
        bucket = self.client.storage.from_(settings.SUPABASE_BUCKET_NAME)
        return bucket.get_public_url(remote_path)
    
    # =========================================================================
    # FULL UNIVERSE FETCH (with all relations)
    # =========================================================================
    
    def get_full_univers(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a complete universe with all related data.
        
        Returns:
            Dict with: univers, prompts, translations, assets (with their prompts/translations)
        """
        self._require_client()
        
        # Get universe
        univers = self.get_univers_by_slug(slug)
        if not univers:
            return None
        
        univers_id = univers["id"]
        
        # Get prompts
        prompts = self.get_univers_prompts(univers_id)
        
        # Get translations
        translations = self.get_univers_translations(univers_id)
        
        # Get music prompts
        music_prompts = self.get_univers_music_prompts(univers_id)

        # Get assets with their relations
        assets = self.get_assets(univers_id)
        for asset in assets:
            asset["prompts"] = self.get_asset_prompts(asset["id"])
            asset["translations"] = self.get_asset_translations(asset["id"])

        return {
            "univers": univers,
            "prompts": prompts,
            "translations": translations,
            "music_prompts": music_prompts,
            "assets": assets
        }

    def get_univers_music_prompts(self, univers_id: int) -> List[Dict[str, Any]]:
        """Get music prompts for a universe."""
        self._require_client()
        response = self.client.table("univers_music_prompts")\
            .select("*")\
            .eq("univers_id", univers_id)\
            .execute()
        return response.data

    def upsert_univers_music_prompt(self, univers_id: int, language: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert music prompt."""
        self._require_client()
        data_with_id = {
            "univers_id": univers_id,
            "language": language,
            **data
        }
        response = self.client.table("univers_music_prompts")\
            .upsert(data_with_id)\
            .execute()
        return response.data[0]

    def delete_univers_music_prompts(self, univers_id: int):
        """Delete all music prompts for a universe."""
        self._require_client()
        self.client.table("univers_music_prompts")\
            .delete()\
            .eq("univers_id", univers_id)\
            .execute()


# Singleton instance
supabase_service = SupabaseService()
