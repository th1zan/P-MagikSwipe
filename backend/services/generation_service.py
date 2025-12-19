"""Generation service - AI content generation using Replicate."""
import os
import re
import json
import time
import base64
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from deep_translator import GoogleTranslator
import replicate

from config import settings
from services.storage_service import storage_service
from services.job_service import job_service


# Supported languages
LANGUAGES = ["fr", "en", "es", "it", "de"]

# Replicate models - updated models
MODELS = {
    "llm": "meta/llama-2-70b-chat",  # For generating concepts/object names
    "image": "recraft-ai/recraft-v3",  # High-quality image generation
    "video": "wan-video/wan-2.2-i2v-fast",  # Fast image-to-video generation
    "music": "minimax/music-1.5"  # Music generation with vocals
}


class GenerationService:
    """
    AI content generation service using Replicate.
    
    Generates:
    - Concepts (word lists for themes)
    - Translations (multi-language)
    - Images (PNG illustrations)
    - Videos (MP4 from images)
    - Music (MP3 background music)
    """
    
    def __init__(self):
        self.storage = storage_service
        self._check_api_token()
    
    def _check_api_token(self):
        """Check if Replicate API token is configured."""
        if not settings.REPLICATE_API_TOKEN:
            print("⚠️ REPLICATE_API_TOKEN not configured - AI generation disabled")
        else:
            os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
            print("✅ Replicate API configured")
    
    @property
    def is_available(self) -> bool:
        """Check if AI generation is available."""
        return bool(settings.REPLICATE_API_TOKEN)
    
    # =========================================================================
    # CONCEPT GENERATION (LLM)
    # =========================================================================
    
    def generate_concepts(
        self,
        theme: str,
        count: int = 10,
        language: str = "fr"
    ) -> List[str]:
        """
        Generate a list of concepts for a theme using LLM.
        
        Args:
            theme: Theme description (e.g., "jungle animals")
            count: Number of concepts to generate
            language: Primary language for concepts
        
        Returns:
            List of concept names
        """
        if not self.is_available:
            raise RuntimeError("Replicate API not configured")
        
        system_prompt = """You are a helpful assistant that generates child-friendly concepts. Output ONLY a valid JSON array of strings, nothing else."""

        prompt = f"""Generate exactly {count} simple, child-friendly concepts for the theme: "{theme}".

Rules:
- One word or short phrase per concept
- Appropriate for children aged 3-6
- Common, recognizable items/animals/objects
- Output ONLY a JSON array of strings, nothing else

Example output for "farm animals":
["cow", "pig", "chicken", "horse", "sheep", "duck", "goat", "rooster", "dog", "cat"]

Theme: {theme}
Output:"""

        output = replicate.run(
            MODELS["llm"],
            input={
                "system_prompt": system_prompt,
                "prompt": prompt,
                "max_new_tokens": 500,
                "temperature": 0.7
            }
        )

        # Parse response
        response_text = "".join(output)

        # Extract JSON array
        match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if match:
            concepts = json.loads(match.group())
            return concepts[:count]

        raise ValueError(f"Failed to parse concepts from LLM response: {response_text}")
    
    # =========================================================================
    # TRANSLATION
    # =========================================================================
    
    def translate_text(
        self,
        text: str,
        source_lang: str = "fr",
        target_lang: str = "en"
    ) -> str:
        """
        Translate text using Google Translator.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        if source_lang == target_lang:
            return text
        
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    
    def translate_concepts(
        self,
        concepts: List[str],
        source_lang: str = "fr"
    ) -> Dict[str, List[str]]:
        """
        Translate a list of concepts to all supported languages.
        
        Args:
            concepts: List of concept names
            source_lang: Source language
        
        Returns:
            Dict mapping language code to translated concepts
        """
        translations = {source_lang: concepts}
        
        for lang in LANGUAGES:
            if lang == source_lang:
                continue
            
            translated = []
            for concept in concepts:
                try:
                    translated.append(self.translate_text(concept, source_lang, lang))
                except Exception as e:
                    print(f"Translation error for '{concept}' to {lang}: {e}")
                    translated.append(concept)  # Fallback to original
            
            translations[lang] = translated
        
        return translations
    
    # =========================================================================
    # IMAGE GENERATION
    # =========================================================================
    
    def generate_image_prompt(
        self,
        concept: str,
        theme_context: str = "",
        style: str = "children's illustration"
    ) -> str:
        """
        Generate an image prompt for a concept.
        
        Args:
            concept: The concept to illustrate
            theme_context: Additional context about the theme
            style: Art style description
        
        Returns:
            Formatted image prompt
        """
        base_prompt = f"A cute, friendly {concept}"
        
        if theme_context:
            base_prompt += f" in a {theme_context} setting"
        
        style_suffix = f", {style}, vibrant colors, simple shapes, no text, centered composition, white background"
        
        return base_prompt + style_suffix
    
    def generate_image(
        self,
        prompt: str,
        output_path: Path,
        size: str = "1024x1024"
    ) -> Path:
        """
        Generate an image using Replicate.
        
        Args:
            prompt: Image generation prompt
            output_path: Path to save the image
            size: Image size (e.g., "1024x1024")
        
        Returns:
            Path to saved image
        """
        if not self.is_available:
            raise RuntimeError("Replicate API not configured")
        
        print(f"🎨 Making Replicate API call for image generation: {prompt[:50]}...")
        output = replicate.run(
            MODELS["image"],
            input={
                "prompt": prompt,
                "size": size,
                "style": "digital_illustration"
            }
        )
        print(f"✅ Replicate API call completed for image")
        
        # Download image
        if isinstance(output, list):
            image_url = output[0]
        else:
            image_url = str(output)
        
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        
        return output_path
    
    def generate_all_images(
        self,
        slug: str,
        concepts: List[str],
        prompts: Optional[List[str]] = None,
        job_id: Optional[str] = None,
        theme_context: str = ""
    ) -> List[Path]:
        """
        Generate images for all concepts in a universe.
        
        Args:
            slug: Universe slug
            concepts: List of concept names
            prompts: Optional custom prompts (one per concept)
            job_id: Optional job ID for progress updates
            theme_context: Theme context for prompt generation
        
        Returns:
            List of paths to generated images
        """
        generated = []
        
        if job_id:
            job_service.set_total_steps(job_id, len(concepts))
        
        for i, concept in enumerate(concepts):
            try:
                # Generate or use custom prompt
                if prompts and i < len(prompts) and prompts[i]:
                    prompt = prompts[i]
                else:
                    prompt = self.generate_image_prompt(concept, theme_context)
                
                # Output path (consistent naming with existing files)
                concept_slug = concepts[i].lower().replace(' ', '_').replace('-', '_') if i < len(concepts) else f"item_{i+1}"
                image_name = f"{i:02d}_{concept_slug}.png"
                output_path = self.storage.get_asset_image_path(slug, image_name)
                
                # Generate
                self.generate_image(prompt, output_path)
                generated.append(output_path)
                
                if job_id:
                    job_service.step(job_id, f"Generated image {i+1}/{len(concepts)}: {concept}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error generating image for '{concept}': {e}")
                if job_id:
                    job_service.update_job(job_id, message=f"Error on {concept}: {e}")
        
        return generated
    
    # =========================================================================
    # VIDEO GENERATION
    # =========================================================================
    
    def generate_video_prompt(
        self,
        concept: str,
        motion_type: str = "subtle"
    ) -> str:
        """
        Generate a video motion prompt for an image.
        
        Args:
            concept: The concept in the image
            motion_type: Type of motion (subtle, moderate, dynamic)
        
        Returns:
            Video motion prompt
        """
        motions = {
            "subtle": "gentle swaying, soft breathing motion, slight shimmer",
            "moderate": "playful bouncing, gentle waving, soft rotation",
            "dynamic": "jumping, spinning, energetic movement"
        }
        
        motion = motions.get(motion_type, motions["subtle"])
        return f"The {concept} has {motion}, looping seamlessly, child-friendly animation"
    
    def generate_video(
        self,
        image_path: Path,
        prompt: str,
        output_path: Path,
        duration: float = 3.0
    ) -> Path:
        """
        Generate a video from an image using Replicate.
        
        Args:
            image_path: Path to source image
            prompt: Motion/animation prompt
            output_path: Path to save the video
            duration: Video duration in seconds
        
        Returns:
            Path to saved video
        """
        if not self.is_available:
            raise RuntimeError("Replicate API not configured")
        
        # Read image
        with open(image_path, "rb") as f:
            image_data = f.read()

        output = replicate.run(
            MODELS["video"],
            input={
                "image": f"data:image/png;base64,{base64.b64encode(image_data).decode()}",
                "prompt": prompt,
                "num_frames": int(duration * 8),
                "num_inference_steps": 50
            }
        )
        
        # Download video
        video_url = str(output)
        response = requests.get(video_url)
        response.raise_for_status()
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        
        return output_path
    
    def generate_all_videos(
        self,
        slug: str,
        concepts: List[str],
        prompts: Optional[List[str]] = None,
        job_id: Optional[str] = None
    ) -> List[Path]:
        """
        Generate videos for all assets in a universe.
        
        Args:
            slug: Universe slug
            concepts: List of concept names
            prompts: Optional custom video prompts
            job_id: Optional job ID for progress updates
        
        Returns:
            List of paths to generated videos
        """
        generated = []
        universe_path = self.storage.get_universe_path(slug)

        # Get list of images (flat structure)
        images = sorted([f for f in universe_path.iterdir() if f.suffix == ".png"])
        
        if job_id:
            job_service.set_total_steps(job_id, len(images))
        
        for i, image_path in enumerate(images):
            try:
                concept = concepts[i] if i < len(concepts) else f"item {i+1}"
                
                # Generate or use custom prompt
                if prompts and i < len(prompts) and prompts[i]:
                    prompt = prompts[i]
                else:
                    prompt = self.generate_video_prompt(concept)
                
                # Output path
                output_path = image_path.with_suffix(".mp4")
                
                # Generate
                self.generate_video(image_path, prompt, output_path)
                generated.append(output_path)
                
                if job_id:
                    job_service.step(job_id, f"Generated video {i+1}/{len(images)}: {concept}")
                
                # Rate limiting (videos take longer)
                time.sleep(2)
                
            except Exception as e:
                print(f"Error generating video for image {image_path}: {e}")
                if job_id:
                    job_service.update_job(job_id, message=f"Error: {e}")
        
        return generated
    
    # =========================================================================
    # MUSIC GENERATION
    # =========================================================================
    
    def generate_music(
        self,
        slug: str,
        language: str,
        style: str = "children's music, playful, upbeat",
        duration: int = 60,
        lyrics: Optional[str] = None
    ) -> Path:
        """
        Generate background music for a universe.

        Args:
            slug: Universe slug
            language: Language code
            style: Music style description
            duration: Duration in seconds
            lyrics: Optional lyrics

        Returns:
            Path to saved music file
        """
        if not self.is_available:
            raise RuntimeError("Replicate API not configured")

        # Get stored prompt and lyrics for the language
        from database import SessionLocal, Univers, UniversMusicPrompts
        db = SessionLocal()
        try:
            univers = db.query(Univers).filter(Univers.slug == slug).first()
            if not univers:
                raise ValueError(f"Universe '{slug}' not found")

            stored_prompt = None
            stored_lyrics = None
            for mp in univers.music_prompts:
                if mp.language == language:
                    stored_prompt = mp.prompt
                    stored_lyrics = mp.lyrics
                    break

            # Use stored lyrics or provided lyrics
            if lyrics:
                music_lyrics = lyrics
            elif stored_lyrics:
                music_lyrics = stored_lyrics
            else:
                music_lyrics = ""

            # Use stored prompt for style or fallback
            if stored_prompt:
                style_description = stored_prompt
            else:
                style_description = f"{style}, instrumental background music for {univers.name}"

            input_params = {
                "lyrics": music_lyrics,
                "reference_audio": None,  # Optional: can add reference audio later
                "style_strength": 0.8,  # Default style strength
                "duration": duration
            }

        finally:
            db.close()
        
        print(f"🎵 Making Replicate API call for music generation: {slug} ({language}) - {music_lyrics[:50] if music_lyrics else style_description[:50]}...")
        output = replicate.run(
            MODELS["music"],
            input=input_params
        )
        print(f"✅ Replicate API call completed for music: {slug}")
        
        # Download music
        music_url = str(output)
        response = requests.get(music_url)
        response.raise_for_status()
        
        # Save to file
        output_path = self.storage.get_music_file_path(slug, language)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        
        return output_path
    
    # =========================================================================
    # FULL UNIVERSE GENERATION
    # =========================================================================
    
    def generate_universe_content(
        self,
        slug: str,
        theme: str,
        concept_count: int = 10,
        generate_videos: bool = True,
        generate_music: bool = True,
        job_id: Optional[str] = None
    ) -> Dict:
        """
        Generate all content for a universe.
        
        Args:
            slug: Universe slug
            theme: Theme description
            concept_count: Number of concepts to generate
            generate_videos: Whether to generate videos
            generate_music: Whether to generate music
            job_id: Optional job ID for progress updates
        
        Returns:
            Dict with generated content info
        """
        result = {
            "concepts": [],
            "translations": {},
            "images": [],
            "videos": [],
            "music": []
        }
        
        # Create storage folder
        self.storage.create_universe_folder(slug)
        
        # Step 1: Generate concepts
        if job_id:
            job_service.update_job(job_id, message="Generating concepts...")
        
        concepts = self.generate_concepts(theme, concept_count)
        result["concepts"] = concepts
        
        # Step 2: Translate concepts
        if job_id:
            job_service.update_job(job_id, message="Translating concepts...")
        
        translations = self.translate_concepts(concepts)
        result["translations"] = translations
        
        # Step 3: Generate images
        if job_id:
            job_service.update_job(job_id, message="Generating images...")
        
        images = self.generate_all_images(slug, concepts, theme_context=theme, job_id=job_id)
        result["images"] = [str(p) for p in images]
        
        # Step 4: Generate videos
        if generate_videos:
            if job_id:
                job_service.update_job(job_id, message="Generating videos...")
            
            videos = self.generate_all_videos(slug, concepts, job_id=job_id)
            result["videos"] = [str(p) for p in videos]
        
        # Step 5: Generate music
        if generate_music:
            if job_id:
                job_service.update_job(job_id, message="Generating music...")
            
            for lang in LANGUAGES:
                try:
                    music_path = self.generate_music(slug, lang)
                    result["music"].append(str(music_path))
                except Exception as e:
                    print(f"Music generation failed for {lang}: {e}")
        
        return result


# Singleton instance
generation_service = GenerationService()
