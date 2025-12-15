"""
Service pour gérer les interactions avec Supabase
"""
import os
import logging
from typing import Dict, List, Optional
from supabase import create_client, Client
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service pour gérer les opérations Supabase"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY doivent être définis")
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self.storage_bucket = "univers"
    
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """
        Upload un fichier vers Supabase Storage
        
        Args:
            local_path: Chemin local du fichier
            remote_path: Chemin dans le bucket (ex: "jungle/01.png")
            
        Returns:
            URL publique du fichier
        """
        with open(local_path, 'rb') as f:
            file_data = f.read()
        
        # Upload le fichier
        result = self.client.storage.from_(self.storage_bucket).upload(
            remote_path,
            file_data,
            file_options={"upsert": "true"}
        )
        
        # Récupère l'URL publique
        public_url = self.client.storage.from_(self.storage_bucket).get_public_url(remote_path)
        
        logger.info(f"Uploaded {local_path} to {remote_path}")
        return public_url
    
    def create_univers(
        self,
        name: str,
        slug: str,
        thumbnail_url: Optional[str] = None,
        background_color: Optional[str] = None,
        background_music: Optional[str] = None,
        is_public: bool = False,
        owner_id: Optional[str] = None
    ) -> int:
        """
        Crée un nouvel univers dans Supabase
        
        Returns:
            ID de l'univers créé
        """
        data = {
            "name": name,
            "slug": slug,
            "is_public": is_public
        }
        
        if thumbnail_url:
            data["thumbnail_url"] = thumbnail_url
        if background_color:
            data["background_color"] = background_color
        if background_music:
            data["background_music"] = background_music
        if owner_id:
            data["owner_id"] = owner_id
        
        result = self.client.table("univers").insert(data).execute()
        univers_id = result.data[0]["id"]
        
        logger.info(f"Created univers {name} with ID {univers_id}")
        return univers_id
    
    def create_univers_prompts(
        self,
        univers_id: int,
        default_image_prompt: Optional[str] = None,
        default_video_prompt: Optional[str] = None
    ) -> str:
        """
        Crée les prompts par défaut pour un univers
        
        Returns:
            UUID du record créé
        """
        data = {
            "univers_id": univers_id,
            "default_image_prompt": default_image_prompt,
            "default_video_prompt": default_video_prompt
        }
        
        result = self.client.table("univers_prompts").insert(data).execute()
        prompt_id = result.data[0]["id"]
        
        logger.info(f"Created univers_prompts for univers {univers_id}")
        return prompt_id
    
    def create_univers_translations(
        self,
        univers_id: int,
        translations: Dict[str, str]
    ):
        """
        Crée les traductions pour un univers
        
        Args:
            univers_id: ID de l'univers
            translations: Dict {langue: nom_traduit}
        """
        records = [
            {
                "univers_id": univers_id,
                "language": lang,
                "name": name
            }
            for lang, name in translations.items()
        ]
        
        if records:
            self.client.table("univers_translations").insert(records).execute()
            logger.info(f"Created {len(records)} translations for univers {univers_id}")
    
    def create_univers_asset(
        self,
        univers_id: int,
        sort_order: int,
        image_name: str,
        display_name: str
    ) -> str:
        """
        Crée un asset pour un univers
        
        Returns:
            UUID de l'asset créé
        """
        data = {
            "univers_id": univers_id,
            "sort_order": sort_order,
            "image_name": image_name,
            "display_name": display_name
        }
        
        result = self.client.table("univers_assets").insert(data).execute()
        asset_id = result.data[0]["id"]
        
        logger.info(f"Created asset {image_name} for univers {univers_id}")
        return asset_id
    
    def create_asset_prompts(
        self,
        asset_id: str,
        custom_image_prompt: Optional[str] = None,
        custom_video_prompt: Optional[str] = None,
        generation_count: int = 1
    ) -> str:
        """
        Crée les prompts personnalisés pour un asset
        
        Returns:
            UUID du record créé
        """
        data = {
            "asset_id": asset_id,
            "custom_image_prompt": custom_image_prompt,
            "custom_video_prompt": custom_video_prompt,
            "generation_count": generation_count,
            "last_generated_at": datetime.now().isoformat()
        }
        
        result = self.client.table("univers_assets_prompts").insert(data).execute()
        prompt_id = result.data[0]["id"]
        
        logger.info(f"Created asset_prompts for asset {asset_id}")
        return prompt_id
    
    def create_asset_translations(
        self,
        asset_id: str,
        translations: Dict[str, str]
    ):
        """
        Crée les traductions pour un asset
        
        Args:
            asset_id: UUID de l'asset
            translations: Dict {langue: nom_traduit}
        """
        records = [
            {
                "asset_id": asset_id,
                "language": lang,
                "display_name": name
            }
            for lang, name in translations.items()
        ]
        
        if records:
            self.client.table("univers_assets_translations").insert(records).execute()
            logger.info(f"Created {len(records)} translations for asset {asset_id}")
    
    def update_univers_public_status(self, univers_id: int, is_public: bool = True):
        """
        Met à jour le statut public d'un univers
        """
        self.client.table("univers").update({"is_public": is_public}).eq("id", univers_id).execute()
        logger.info(f"Updated univers {univers_id} is_public to {is_public}")
    
    def delete_univers_assets(self, univers_id: int):
        """
        Supprime tous les assets d'un univers (pour re-publication)
        """
        self.client.table("univers_assets").delete().eq("univers_id", univers_id).execute()
        logger.info(f"Deleted all assets for univers {univers_id}")


# Instance globale
supabase_service = SupabaseService()
