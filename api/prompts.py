import os
import json
import replicate
from dotenv import load_dotenv

load_dotenv()

def generate_words(theme_name: str):
    prompt = f'Génère exactement 10 mots simples et joyeux pour enfants de 3-7 ans sur le thème "{theme_name}". Un mot par ligne, rien d’autre.'
    output = replicate.run("meta/llama-2-70b-chat", input={"prompt": prompt, "temperature": 0.7, "max_tokens": 200})
    text = "".join(output)
    words = []
    for line in text.split("\n"):
        line = line.strip()
        if line and len(line) < 25:
            if ". " in line:
                line = line.split(". ", 1)[1]
            words.append(line.lower())
    return words[:10]

def generate_lyrics(theme_name: str, words: list):
    prompt = f"""Create joyful children's song lyrics in French about '{theme_name}' using these words: {', '.join(words[:6])}.

IMPORTANT FORMAT REQUIREMENTS:
- Use ONLY these structure tags: [Verse], [Chorus], [Bridge], [Outro]
- Each line must be separated by a line break
- Total length: 200-550 characters
- Style: Simple, poetic, child-friendly, with rhythm and rhymes
- Use \\n to separate lines within sections

Example structure:
[Verse]
First line here
Second line with rhyme
Third line flows nice
Fourth line sublime

[Chorus]
Catchy repeated phrase here
Make children want to cheer
Simple and clear

[Bridge]
Transition moment sweet
Gentle and complete

[Outro]
Ending so bright
Goodnight

Generate ONLY the lyrics with structure tags, no explanations."""
    
    output = replicate.run("meta/llama-2-70b-chat", input={"prompt": prompt, "temperature": 0.8, "max_tokens": 600})
    lyrics = "".join(output).strip()
    
    # Nettoyage
    start = lyrics.find("[")
    if start != -1:
        lyrics = lyrics[start:]
    
    # Enlever les balises markdown si présentes
    lyrics = lyrics.replace("```", "").strip()
    
    # Limiter à 590 caractères pour Suno AI
    lyrics = lyrics[:590]
    
    # Fallback si trop court ou malformé
    if len(lyrics) < 100 or not any(tag in lyrics for tag in ["[Verse]", "[Chorus]"]):
        lyrics = f"""[Verse]
Dans le monde de {theme_name}
Tout est beau et tout est bien
Les enfants dansent avec joie
Viens découvrir avec moi

[Chorus]
{theme_name}, {theme_name} merveilleux
On s'amuse tous les deux
Chantons ensemble ce refrain
Jusqu'à demain matin

[Bridge]
Chaque moment est magique
Dans cet univers fantastique

[Outro]
Bonne nuit les amis
À demain aussi"""
    
    return lyrics

def generate_base_prompts(theme_name: str):
    # Generate words
    words = generate_words(theme_name)

    # Generate lyrics
    lyrics = generate_lyrics(theme_name, words)
    
    # Load base prompts
    base_dir = "storage/base_prompts"
    with open(os.path.join(base_dir, "description_model.txt"), 'r') as f:
        desc_template = f.read().strip()
    with open(os.path.join(base_dir, "image_model.txt"), 'r') as f:
        img_template = f.read().strip()
    with open(os.path.join(base_dir, "video_model.txt"), 'r') as f:
        vid_template = f.read().strip()
    with open(os.path.join(base_dir, "music_model.txt"), 'r') as f:
        mus_template = f.read().strip()
    
    # Create prompts
    description = desc_template.format(theme=theme_name)
    images = [img_template.format(word=word, theme=theme_name) for word in words]
    videos = [vid_template.format(word=word, theme=theme_name) for word in words]
    music = mus_template.format(theme=theme_name, words=', '.join(words))
    
    return {
        "theme": theme_name,
        "description": description,
        "words": words,
        "images": images,
        "videos": videos,
        "music": music,
        "lyrics": lyrics
    }