"""Sync service - Bidirectional sync between local SQLite and Supabase."""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from database import (
    Univers, UniversPrompts, UniversTranslation,
    UniversAsset, UniversAssetPrompts, UniversAssetTranslation, UniversMusicPrompts
)
from services.storage_service import storage_service
from services.supabase_service import supabase_service
from schemas import SyncResponse, SyncInitResponse


class SyncService:
    """
    Handles synchronization between local SQLite database and Supabase.
    
    Strategy: "Last Write Wins" - The source being synced FROM always overwrites.
    """
    
    def __init__(self):
        self.storage = storage_service
        self.supabase = supabase_service
    
    # =========================================================================
    # PULL: Supabase -> Local
    # =========================================================================
    
    def pull_universe(self, db: Session, slug: str, force: bool = False) -> SyncResponse:
        """
        Pull a single universe from Supabase to local SQLite + storage.
        
        Args:
            db: Database session
            slug: Universe slug
            force: Force overwrite even if local is newer
        
        Returns:
            SyncResponse with status
        """
        errors = []
        synced_items = 0
        
        try:
            # Check Supabase connection
            if not self.supabase.is_connected:
                return SyncResponse(
                    success=False,
                    message="Supabase not connected",
                    errors=["SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured"]
                )
            
            # Fetch full universe from Supabase
            remote_data = self.supabase.get_full_univers(slug)
            if not remote_data:
                return SyncResponse(
                    success=False,
                    message=f"Universe '{slug}' not found in Supabase",
                    errors=[f"No universe with slug '{slug}' exists in Supabase"]
                )
            
            remote_univers = remote_data["univers"]
            
            # Check if exists locally
            local_univers = db.query(Univers).filter(Univers.slug == slug).first()
            
            # Create or update universe
            if local_univers:
                # Update existing
                local_univers.name = remote_univers["name"]
                local_univers.thumbnail_url = remote_univers.get("thumbnail_url")
                local_univers.is_public = remote_univers.get("is_public", True)
                local_univers.background_music = remote_univers.get("background_music")
                local_univers.background_color = remote_univers.get("background_color")
                local_univers.supabase_id = remote_univers["id"]
                local_univers.last_synced_at = datetime.utcnow()
            else:
                # Create new
                local_univers = Univers(
                    name=remote_univers["name"],
                    slug=remote_univers["slug"],
                    thumbnail_url=remote_univers.get("thumbnail_url"),
                    is_public=remote_univers.get("is_public", True),
                    background_music=remote_univers.get("background_music"),
                    background_color=remote_univers.get("background_color"),
                    supabase_id=remote_univers["id"],
                    last_synced_at=datetime.utcnow()
                )
                db.add(local_univers)
            
            db.flush()  # Get ID
            synced_items += 1
            
            # Sync prompts
            if remote_data.get("prompts"):
                self._sync_univers_prompts(db, local_univers.id, remote_data["prompts"])
                synced_items += 1
            
            # Sync translations
            self._sync_univers_translations(db, local_univers.id, remote_data.get("translations", []))
            synced_items += len(remote_data.get("translations", []))

            # Sync music prompts
            self._sync_univers_music_prompts(db, local_univers.id, remote_data.get("music_prompts", []))
            synced_items += len(remote_data.get("music_prompts", []))

            # Delete existing assets (replace all)
            db.query(UniversAsset).filter(UniversAsset.univers_id == local_univers.id).delete()
            
            # Sync assets
            for remote_asset in remote_data.get("assets", []):
                try:
                    self._sync_asset(db, local_univers.id, slug, remote_asset)
                    synced_items += 1
                except Exception as e:
                    errors.append(f"Asset {remote_asset.get('id')}: {str(e)}")
            
            # Create local storage folder
            self.storage.create_universe_folder(slug)
            
            # Download media files
            files_downloaded = self._download_universe_files(slug)
            
            db.commit()
            
            return SyncResponse(
                success=True,
                message=f"Successfully pulled '{slug}' from Supabase",
                synced_items=synced_items + files_downloaded,
                errors=errors
            )
            
        except Exception as e:
            db.rollback()
            print(f"[SYNC][ERROR] Exception while inserting universe '{slug}': {e}")
            import traceback
            traceback.print_exc()
            return SyncResponse(
                success=False,
                message=f"Failed to pull '{slug}'",
                errors=[str(e)]
            )
    
    def pull_all(self, db: Session) -> SyncInitResponse:
        """
        Pull ALL universes from Supabase (init sync).
        
        Returns:
            SyncInitResponse with counts
        """
        if not self.supabase.is_connected:
            return SyncInitResponse(
                success=False,
                message="Supabase not connected"
            )
        
        try:
            # Get all universes from Supabase
            remote_universes = self.supabase.get_all_univers()
            
            universes_synced = 0
            assets_synced = 0
            files_downloaded = 0
            errors = []
            
            for remote_univers in remote_universes:
                slug = remote_univers["slug"]
                result = self.pull_universe(db, slug, force=True)
                
                if result.success:
                    universes_synced += 1
                    assets_synced += result.synced_items
                else:
                    errors.extend(result.errors)
            
            return SyncInitResponse(
                success=True,
                message=f"Initialized local database from Supabase",
                universes_synced=universes_synced,
                assets_synced=assets_synced,
                files_downloaded=files_downloaded
            )
            
        except Exception as e:
            return SyncInitResponse(
                success=False,
                message=f"Init sync failed: {str(e)}"
            )
    
    # =========================================================================
    # PUSH: Local -> Supabase
    # =========================================================================
    
    def push_universe(self, db: Session, slug: str, force: bool = False) -> SyncResponse:
        """
        Push a local universe to Supabase.
        
        Args:
            db: Database session
            slug: Universe slug
            force: Force overwrite even if remote is newer
        
        Returns:
            SyncResponse with status
        """
        errors = []
        synced_items = 0
        
        try:
            if not self.supabase.is_connected:
                return SyncResponse(
                    success=False,
                    message="Supabase not connected",
                    errors=["SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured"]
                )
            
            # Get local universe
            local_univers = db.query(Univers).filter(Univers.slug == slug).first()
            if not local_univers:
                return SyncResponse(
                    success=False,
                    message=f"Universe '{slug}' not found locally",
                    errors=[f"No universe with slug '{slug}' exists locally"]
                )
            
            # Upload media files first
            files_uploaded = self._upload_universe_files(slug)
            synced_items += files_uploaded
            
            # Push universe to Supabase
            univers_data = {
                "name": local_univers.name,
                "slug": local_univers.slug,
                "thumbnail_url": local_univers.thumbnail_url,
                "is_public": local_univers.is_public,
                "background_music": local_univers.background_music,
                "background_color": local_univers.background_color
            }
            
            remote_univers = self.supabase.upsert_univers(univers_data)
            remote_id = remote_univers["id"]
            synced_items += 1
            
            # Update local with Supabase ID
            local_univers.supabase_id = remote_id
            local_univers.last_synced_at = datetime.utcnow()
            
            # Push prompts
            if local_univers.prompts:
                self.supabase.upsert_univers_prompts(remote_id, {
                    "default_image_prompt": local_univers.prompts.default_image_prompt,
                    "default_video_prompt": local_univers.prompts.default_video_prompt
                })
                synced_items += 1
            
            # Push translations
            self.supabase.delete_univers_translations(remote_id)
            for trans in local_univers.translations:
                self.supabase.upsert_univers_translation(remote_id, trans.language, trans.name)
                synced_items += 1

            # Push music prompts
            self.supabase.delete_univers_music_prompts(remote_id)
            for prompt in local_univers.music_prompts:
                self.supabase.upsert_univers_music_prompt(remote_id, prompt.language, {
                    "prompt": prompt.prompt,
                    "lyrics": prompt.lyrics
                })
                synced_items += 1

            # Push assets
            self.supabase.delete_all_assets(remote_id)
            for asset in local_univers.assets:
                try:
                    self._push_asset(remote_id, asset)
                    synced_items += 1
                except Exception as e:
                    errors.append(f"Asset {asset.id}: {str(e)}")
            
            db.commit()
            
            return SyncResponse(
                success=True,
                message=f"Successfully pushed '{slug}' to Supabase",
                synced_items=synced_items,
                errors=errors
            )
            
        except Exception as e:
            db.rollback()
            return SyncResponse(
                success=False,
                message=f"Failed to push '{slug}'",
                errors=[str(e)]
            )
    
    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================
    
    def _sync_univers_prompts(self, db: Session, univers_id: int, remote_prompts: dict):
        """Sync universe prompts from remote."""
        existing = db.query(UniversPrompts).filter(UniversPrompts.univers_id == univers_id).first()
        
        if existing:
            existing.default_image_prompt = remote_prompts.get("default_image_prompt")
            existing.default_video_prompt = remote_prompts.get("default_video_prompt")
        else:
            prompts = UniversPrompts(
                univers_id=univers_id,
                default_image_prompt=remote_prompts.get("default_image_prompt"),
                default_video_prompt=remote_prompts.get("default_video_prompt")
            )
            db.add(prompts)
    
    def _sync_univers_translations(self, db: Session, univers_id: int, remote_translations: list):
        """Sync universe translations from remote."""
        # Delete existing
        db.query(UniversTranslation).filter(UniversTranslation.univers_id == univers_id).delete()
        
        # Create new
        for trans in remote_translations:
            translation = UniversTranslation(
                univers_id=univers_id,
                language=trans["language"],
                name=trans["name"]
            )
            db.add(translation)

    def _sync_univers_music_prompts(self, db: Session, univers_id: int, remote_music_prompts: List[Dict[str, Any]]):
        """Sync music prompts from remote."""
        # Delete existing
        db.query(UniversMusicPrompts).filter(UniversMusicPrompts.univers_id == univers_id).delete()

        # Insert new
        for remote_prompt in remote_music_prompts:
            prompt = UniversMusicPrompts(
                univers_id=univers_id,
                language=remote_prompt["language"],
                prompt=remote_prompt["prompt"],
                lyrics=remote_prompt["lyrics"]
            )
            db.add(prompt)

    def _sync_asset(self, db: Session, univers_id: int, slug: str, remote_asset: dict):
        """Sync a single asset from remote."""
        asset = UniversAsset(
            id=remote_asset["id"],
            univers_id=univers_id,
            sort_order=remote_asset["sort_order"],
            image_name=remote_asset["image_name"],
            display_name=remote_asset["display_name"]
        )
        db.add(asset)
        db.flush()
        
        # Sync asset prompts
        if remote_asset.get("prompts"):
            prompts = UniversAssetPrompts(
                asset_id=asset.id,
                custom_image_prompt=remote_asset["prompts"].get("custom_image_prompt"),
                custom_video_prompt=remote_asset["prompts"].get("custom_video_prompt"),
                generation_count=remote_asset["prompts"].get("generation_count", 1)
            )
            db.add(prompts)
        
        # Sync asset translations
        for trans in remote_asset.get("translations", []):
            translation = UniversAssetTranslation(
                asset_id=asset.id,
                language=trans["language"],
                display_name=trans["display_name"]
            )
            db.add(translation)
    
    def _push_asset(self, remote_univers_id: int, asset: UniversAsset):
        """Push a single asset to Supabase."""
        asset_data = {
            "id": asset.id,
            "univers_id": remote_univers_id,
            "sort_order": asset.sort_order,
            "image_name": asset.image_name,
            "display_name": asset.display_name
        }
        
        remote_asset = self.supabase.upsert_asset(asset_data)
        
        # Push prompts
        if asset.prompts:
            self.supabase.upsert_asset_prompts(asset.id, {
                "custom_image_prompt": asset.prompts.custom_image_prompt,
                "custom_video_prompt": asset.prompts.custom_video_prompt,
                "generation_count": asset.prompts.generation_count
            })
        
        # Push translations
        self.supabase.delete_asset_translations(asset.id)
        for trans in asset.translations:
            self.supabase.upsert_asset_translation(asset.id, trans.language, trans.display_name)
    
    def _download_universe_files(self, slug: str) -> int:
        """Download all media files for a universe from Supabase Storage."""
        if not self.supabase.is_connected:
            print(f"[SYNC][MEDIA] Supabase not connected, skipping media download for {slug}")
            return 0

        files_downloaded = 0

        try:
            folders_to_check = [
                f"{slug}",
                f"{slug}/assets",
                f"{slug}/music"
            ]

            print(f"[SYNC][MEDIA] Downloading media for universe '{slug}'...")
            for folder in folders_to_check:
                try:
                    print(f"[SYNC][MEDIA] Listing folder: {folder}")
                    files = self.supabase.list_storage_folder(folder)
                    print(f"[SYNC][MEDIA] Found {len(files)} files in {folder}")
                    for file_info in files:
                        if file_info.get("name") and not file_info["name"].endswith("/"):
                            remote_path = f"{folder}/{file_info['name']}"
                            print(f"[SYNC][MEDIA] Downloading file: {remote_path}")
                            content = self.supabase.download_from_storage(remote_path)
                            if content:
                                self.storage.upload_file(content, remote_path)
                                print(f"[SYNC][MEDIA] Downloaded and saved: {remote_path}")
                                files_downloaded += 1
                            else:
                                print(f"[SYNC][MEDIA][WARN] No content for: {remote_path}")
                except Exception as e:
                    print(f"[SYNC][MEDIA][ERROR] Error listing {folder}: {e}")

            print(f"[SYNC][MEDIA] Total files downloaded for '{slug}': {files_downloaded}")
            return files_downloaded

        except Exception as e:
            print(f"[SYNC][MEDIA][ERROR] Error downloading files for {slug}: {e}")
            return files_downloaded
    
    def _upload_universe_files(self, slug: str) -> int:
        """Upload all media files for a universe to Supabase Storage."""
        if not self.supabase.is_connected:
            return 0
        
        files_uploaded = 0
        universe_path = self.storage.get_universe_path(slug)
        
        if not universe_path.exists():
            return 0
        
        try:
            # Upload all files recursively
            for file_path in universe_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.storage.bucket_path)
                    remote_path = str(relative_path)
                    
                    # Determine content type
                    content_type = self.storage.get_mime_type(remote_path) or "application/octet-stream"
                    
                    # Read and upload
                    content = file_path.read_bytes()
                    self.supabase.upload_to_storage(content, remote_path, content_type)
                    files_uploaded += 1
            
            return files_uploaded
            
        except Exception as e:
            print(f"Error uploading files for {slug}: {e}")
            return files_uploaded


# Singleton instance
sync_service = SyncService()
