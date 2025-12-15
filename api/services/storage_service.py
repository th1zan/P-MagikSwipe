"""
Service centralisé pour gérer les chemins et opérations de stockage
pour les univers
"""
import os
import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Service pour gérer uniformément le stockage des univers"""
    
    def __init__(self, storage_path: str = "/app/storage"):
        self.storage_path = Path(storage_path)
        self.univers_path = self.storage_path / "univers"
        self.prompts_path = self.storage_path / "prompts"
    
    def get_universe_path(self, universe_name: str) -> Path:
        """
        Retourne le chemin d'un univers
        
        Args:
            universe_name: Nom de l'univers (sera normalisé)
            
        Returns:
            Path vers le dossier de l'univers
        """
        theme = universe_name.lower().replace(' ', '_')
        return self.univers_path / theme
    
    def get_prompts_file_path(self, identifier: str) -> Path:
        """
        Retourne le chemin vers le fichier de prompts
        
        Args:
            identifier: Nom de l'univers
            
        Returns:
            Path vers prompts.json
        """
        universe_path = self.get_universe_path(identifier)
        return universe_path / "prompts.json"
    
    def load_objects(self, identifier: str) -> List[str]:
        """
        Charge la liste des objets/mots depuis le fichier prompts
        
        Args:
            identifier: Nom de l'univers
            
        Returns:
            Liste des noms d'objets/mots
            
        Raises:
            HTTPException: Si le fichier n'existe pas ou est invalide
        """
        prompts_file = self.get_prompts_file_path(identifier)
        
        if not prompts_file.exists():
            raise HTTPException(
                status_code=404, 
                detail="Universe prompts not found"
            )
        
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # prompts.json contient {words: [...], images: [...], ...}
            return data.get("words", [])
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error loading objects from {prompts_file}: {e}")
            raise HTTPException(status_code=500, detail="Invalid prompts file format")
    
    def load_prompts_data(self, identifier: str) -> Dict:
        """
        Charge toutes les données de prompts depuis le fichier
        
        Args:
            identifier: Nom de l'univers
            
        Returns:
            Dictionnaire avec les données complètes
            
        Raises:
            HTTPException: Si le fichier n'existe pas ou est invalide
        """
        prompts_file = self.get_prompts_file_path(identifier)
        
        if not prompts_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Universe prompts not found"
            )
        
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error loading prompts data from {prompts_file}: {e}")
            raise HTTPException(status_code=500, detail="Invalid prompts file format")
    
    def save_prompts_data(self, identifier: str, data: Dict):
        """
        Sauvegarde les données de prompts dans le fichier
        
        Args:
            identifier: Nom de l'univers
            data: Données complètes à sauvegarder
        """
        prompts_file = self.get_prompts_file_path(identifier)
        prompts_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving prompts data to {prompts_file}: {e}")
            raise HTTPException(status_code=500, detail="Failed to save prompts")
    
    def update_prompts(
        self, 
        identifier: str, 
        prompts: List[str], 
        prompts_type: str
    ):
        """
        Met à jour les prompts d'un type spécifique (images ou videos)
        
        Args:
            identifier: Nom de l'univers
            prompts: Liste des prompts à sauvegarder
            prompts_type: Type de prompts ("images" ou "videos")
        """
        # Pour les univers, on met à jour prompts.json
        data = self.load_prompts_data(identifier)
        data[prompts_type] = prompts
        self.save_prompts_data(identifier, data)
    
    def load_default_prompts(self) -> Dict:
        """
        Charge les prompts par défaut depuis defaults.yaml
        
        Returns:
            Dictionnaire avec les prompts par défaut
        """
        defaults_path = self.prompts_path / "defaults.yaml"
        
        if not defaults_path.exists():
            return {
                "images": "A beautiful, colorful illustration of {object} in a magical setting, perfect for children, vibrant and enchanting.",
                "videos": "A short animated video of {object} moving happily and magically, joyful and child-friendly.",
                "objects": "Generate 10 simple objects for children related to the theme {theme}.",
                "music": "Joyful children's song about {theme}, with bouncy melody and fun lyrics."
            }
        
        try:
            with open(defaults_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get("defaults", {})
        except Exception as e:
            logger.error(f"Error loading default prompts: {e}")
            return {}
    
    def load_theme_prompts(self) -> Dict:
        """
        Charge les prompts thématiques depuis themes.yaml
        
        Returns:
            Dictionnaire avec les prompts par thème
        """
        themes_path = self.prompts_path / "themes.yaml"
        
        if not themes_path.exists():
            return {}
        
        try:
            with open(themes_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading theme prompts: {e}")
            return {}
    
    def generate_prompts_for_objects(
        self,
        objects: List[str],
        default_prompt: str,
        custom_prompts: Optional[List[str]] = None
    ) -> List[str]:
        """
        Génère des prompts pour une liste d'objets
        
        Args:
            objects: Liste des objets
            default_prompt: Prompt par défaut avec placeholder {object}
            custom_prompts: Prompts personnalisés optionnels
            
        Returns:
            Liste des prompts générés
        """
        prompts = []
        for i, obj in enumerate(objects):
            if custom_prompts and i < len(custom_prompts) and custom_prompts[i]:
                # Utiliser le prompt personnalisé
                prompts.append(custom_prompts[i])
            else:
                # Générer depuis le template par défaut
                prompt = default_prompt.replace("{object}", obj)
                prompts.append(prompt)
        
        return prompts
    
    def list_all_universes(self) -> List[str]:
        """
        Liste tous les univers disponibles
        
        Returns:
            Liste des noms d'univers
        """
        if not self.univers_path.exists():
            return []
        
        return [d.name for d in self.univers_path.iterdir() if d.is_dir()]


# Instance globale du service
storage_service = StorageService()
