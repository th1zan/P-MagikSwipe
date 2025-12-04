import replicate
import requests
import os
import yaml
import json
import logging
from PIL import Image
import io
from collections import Counter
import subprocess
import re
from deep_translator import GoogleTranslator

# Chargement des prompts une seule fois
with open("storage/prompts.yaml", encoding="utf-8") as f:
    PROMPTS = yaml.safe_load(f)

VIDEO_MODEL = "wan-video/wan-2.2-i2v-fast"
MUSIC_MODEL = PROMPTS["music"]["model"]

def get_theme_description(theme_key: str) -> str:
    return PROMPTS["themes"].get(theme_key, f"univers magique {theme_key}")

def generate_words(theme_name: str, debug=False):
    # Génère seulement en anglais
    prompt = f'Generate exactly 10 simple and joyful words for children aged 3-7 on the theme "{theme_name}" in English. Provide them as a comma-separated list without numbering or bullets.'
    logging.debug(f"Sending prompt to IA: {prompt}")
    output = replicate.run("meta/llama-2-70b-chat", input={"prompt": prompt, "temperature": 0.7, "max_tokens": 200})
    text = "".join(output)
    logging.debug(f"IA response: {text}")
    # Nettoyer : extraire les mots après l'intro (après ":\n\n" ou similaire)
    if ":\n\n" in text:
        text = text.split(":\n\n", 1)[1]
    # Utiliser regex pour extraire les mots simples
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    en_words = [word.lower() for word in words if len(word) < 20][:10]
    logging.debug(f"Extracted English words: {en_words}")

    # Traduis vers autres langues
    words_dict = {"en": en_words}
    for lang in ["fr", "es", "it", "de"]:
        logging.debug(f"Translating to {lang}...")
        translated = [GoogleTranslator(source='en', target=lang).translate(word).lower() for word in en_words]
        logging.debug(f"Translated to {lang}: {translated}")
        words_dict[lang] = translated

    return words_dict

def generate_image(word: str, theme_key: str, index: int, prompt=None):
    if prompt is None:
        theme_desc = get_theme_description(theme_key)
        prompt = PROMPTS["words"]["base"].format(word=word, theme_description=theme_desc)

    output = replicate.run(
        "recraft-ai/recraft-v3",
        input={"prompt": prompt, "width": 1024, "height": 1024, "output_format": "png"}
    )
    img_url = output[0] if isinstance(output, list) else output
    img = Image.open(io.BytesIO(requests.get(img_url).content))

    os.makedirs(f"storage/univers/{theme_key}", exist_ok=True)
    path = f"storage/univers/{theme_key}/{index:02d}_{word.replace(' ', '_')}.png"
    img.save(path)
    return path

def generate_video(image_path: str, word: str, theme_key: str, index: int, motion_prompt=None):
    if motion_prompt is None:
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
    temp_path = f"storage/univers/{theme_key}/{index:02d}_{word.replace(' ', '_')}_temp.mp4"
    final_path = f"storage/univers/{theme_key}/{index:02d}_{word.replace(' ', '_')}_silent.webm"

    # Téléchargement direct → PAS de son ajouté
    video_data = requests.get(video_url).content
    with open(temp_path, "wb") as f:
        f.write(video_data)

    # Conversion en WebM
    subprocess.run([
        "ffmpeg", "-i", temp_path, "-c:v", "libvpx-vp9", "-an", final_path
    ], check=True)

    # Conserver aussi le MP4
    mp4_path = final_path.replace('_silent.webm', '_silent.mp4')
    os.rename(temp_path, mp4_path)

    print(f"    Vidéo muette générée : {final_path}")
    return final_path

def generate_theme_music(theme_key: str, theme_name_fr: str, music_prompt=None, lyrics=None):
    music_path = f"storage/univers/{theme_key}/music.mp3"
    if os.path.exists(music_path):
        print("Musique existe déjà → ignorée")
        return music_path

    if lyrics is None:
        # Charger les mots
        words_file = f"storage/univers/{theme_key}/words.json"
        with open(words_file, 'r', encoding='utf-8') as f:
            words_data = json.load(f)
        words = words_data["words"]

        # Générer lyrics
        lyrics_prompt = f"Génère des paroles de chanson joyeuses pour enfants en français sur le thème '{theme_name_fr}' utilisant ces mots: {', '.join(words[:6])}. Maximum 500 caractères. Structure simple: [Verse 1] ... [Chorus] ... [Verse 2] ... [Chorus]"

        lyrics_output = replicate.run("meta/llama-2-70b-chat", input={"prompt": lyrics_prompt, "temperature": 0.8, "max_tokens": 500})
        lyrics = "".join(lyrics_output).strip()

        # Nettoyage + troncature FORCÉE
        start = lyrics.find("[Verse")
        if start != -1:
            lyrics = lyrics[start:]
        lyrics = lyrics.replace("```", "").strip()
        lyrics = lyrics[:590]  # sécurité

        if len(lyrics) < 100:
            lyrics = "[Verse 1]\nDans la jungle tout est beau\nLes animaux dansent en rond\n[Chorus]\nHop hop la jungle magique\nOn rit on chante toute la nuit\n[Verse 2]\nLes singes font des cabrioles\nLes oiseaux volent en farandole"

    print(f"Paroles finales ({len(lyrics)} caractères) :\n{lyrics}")

    # Musique
    if music_prompt is None:
        music_prompt = "chanson enfantine française joyeuse et douce, xylophone, flûte, clochettes, percussions légères, style comptine, très mignonne et bouncy, nursery rhyme vibe"

    output = replicate.run(
        "minimax/music-1.5",
        input={
            "lyrics": lyrics,
            "prompt": music_prompt,
            "duration": 60,           # ← ajoute ça si tu veux 60s
            "bitrate": 256000,
            "sample_rate": 44100,
            "audio_format": "mp3"
        }
    )

    music_url = output["url"] if isinstance(output, dict) else output
    music_data = requests.get(music_url).content
    with open(music_path, "wb") as f:
        f.write(music_data)
    print(f"Musique générée : {music_path}")
    return music_path

def get_dominant_color(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((100, 100))  # resize for performance
        pixels = list(img.getdata())
        most_common = Counter(pixels).most_common(1)[0][0]
        # assuming RGB
        if isinstance(most_common, tuple) and len(most_common) == 3:
            return f"#{most_common[0]:02x}{most_common[1]:02x}{most_common[2]:02x}"
        else:
            return "#ffffff"  # fallback
    except Exception:
        return "#ffffff"