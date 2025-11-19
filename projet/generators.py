import replicate
import requests
import os
import yaml
from PIL import Image
import io

# Chargement des prompts une seule fois
with open("prompts.yaml", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)

VIDEO_MODEL = "wan-video/wan-2.2-i2v-fast"
MUSIC_MODEL = PROMPTS["music"]["model"]

def get_theme_description(theme_key: str) -> str:
    return PROMPTS["themes"].get(theme_key, f"univers magique {theme_key}")

def generate_words(theme_name: str):
    prompt = f'Génère exactement 10 mots simples et joyeux pour enfants de 3-7 ans sur le thème "{theme_name}". Un mot par ligne, rien d’autre.'
    output = replicate.run("meta/llama-2-70b-chat", input={"prompt": prompt, "temperature": 0.7, "max_tokens": 200})
    text = "".join(output)
    words = []
    for line in text.split("\n"):
        line = line.strip()
        if line and len(line) < 25:
            # Remove leading numbers like "1. "
            if ". " in line:
                line = line.split(". ", 1)[1]
            words.append(line.lower())
    words = words[:10]
    return words[:10]

def generate_image(word: str, theme_key: str, index: int):
    theme_desc = get_theme_description(theme_key)
    prompt = PROMPTS["words"]["base"].format(word=word, theme_description=theme_desc)

    output = replicate.run(
        "recraft-ai/recraft-v3",
        input={"prompt": prompt, "width": 1024, "height": 1024, "output_format": "png"}
    )
    img_url = output[0] if isinstance(output, list) else output
    img = Image.open(io.BytesIO(requests.get(img_url).content))

    os.makedirs(f"univers/{theme_key}", exist_ok=True)
    path = f"univers/{theme_key}/{index:02d}_{word.replace(' ', '_')}.png"
    img.save(path)
    return path

def generate_video(image_path: str, word: str, theme_key: str, index: int):
    motion_prompt = PROMPTS["video_motion"].format(word=word)

    print(f"  → Animation SILENCIEUSE de '{word}'...")
    output = replicate.run(
        VIDEO_MODEL,
        input={
            "image": open(image_path, "rb"),
            "prompt": motion_prompt,
            "num_frames": 121,      # 5 secondes à 24 fps
            "fps": 24,
            "width": 720,
            "height": 720,
            "guidance_scale": 5.0,
            "num_inference_steps": 50
        }
    )

    video_url = output
    final_path = f"univers/{theme_key}/{index:02d}_{word.replace(' ', '_')}_silent.mp4"
    
    # Téléchargement direct → PAS de son ajouté
    video_data = requests.get(video_url).content
    with open(final_path, "wb") as f:
        f.write(video_data)

    print(f"    Vidéo muette générée : {final_path}")
    return final_path

def generate_theme_music(theme_key: str, theme_name_fr: str):
    music_path = f"univers/{theme_key}/music.mp3"
    if os.path.exists(music_path):
        print("Musique existe déjà → ignorée")
        return music_path

    print("Génération musique d’ambiance...")
    prompt = PROMPTS["music"]["prompt"].format(theme_name=theme_name_fr)

    output = replicate.run(
        MUSIC_MODEL,
        input={
            "prompt": prompt,
            "seconds_total": 10,
            "sample_rate": 44100,
            "output_format": "mp3"
        }
    )
    music_data = requests.get(output).content
    with open(music_path, "wb") as f:
        f.write(music_data)
    print("Musique générée :", music_path)
    return music_path