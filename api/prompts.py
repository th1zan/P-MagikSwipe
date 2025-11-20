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
    prompt = f"Génère des paroles de chanson joyeuses pour enfants en français sur le thème '{theme_name}' utilisant ces mots: {', '.join(words[:6])}. Structure simple: [Verse 1] ... [Chorus] ... [Verse 2] ... [Chorus]. Maximum 500 caractères."
    output = replicate.run("meta/llama-2-70b-chat", input={"prompt": prompt, "temperature": 0.8, "max_tokens": 500})
    lyrics = "".join(output).strip()
    # Nettoyage
    start = lyrics.find("[Verse")
    if start != -1:
        lyrics = lyrics[start:]
    lyrics = lyrics.replace("```", "").strip()
    lyrics = lyrics[:590]  # sécurité
    if len(lyrics) < 100:
        lyrics = "[Verse 1]\nDans la jungle tout est beau\nLes animaux dansent en rond\n[Chorus]\nHop hop la jungle magique\nOn rit on chante toute la nuit\n[Verse 2]\nLes singes font des cabrioles\nLes oiseaux volent en farandole"
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