# upload_universe.py
import os
import json
import argparse
import unicodedata
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────
# CONFIGURE ICI (une seule fois)
# ─────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # service_role key
BUCKET_NAME = "univers"
TABLE_NAME = "univers"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_folder_to_supabase(local_folder: str, bucket_path: str):
    """Upload tout un dossier vers Supabase Storage"""
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, local_folder)
            remote_path = f"{bucket_path}/{relative_path}".replace("\\", "/")
            
            with open(file_path, "rb") as f:
                supabase.storage.from_(BUCKET_NAME).upload(
                    remote_path, f.read(), {"upsert": "true"}
                )
            print(f"Uploaded {remote_path}")

def get_existing_folders():
    """Récupère les slugs déjà uploadés depuis la DB"""
    response = supabase.table(TABLE_NAME).select("slug").execute()
    if response.data:
        return {item["slug"] for item in response.data}
    return set()

def add_universe_to_db(name: str, sanitized_slug: str, actual_folder: str, thumbnail_file: str = "00_"):
    # Générer noms en anglais, espagnol, italien, allemand
    import replicate
    prompt = f'Traduis ce nom de thème français en anglais, espagnol, italien, allemand : "{name}". Fournis chaque traduction sur une ligne séparée.'
    output = replicate.run("meta/llama-2-70b-chat", input={"prompt": prompt, "temperature": 0.5, "max_tokens": 200})
    translations_text = "".join(output).strip().split("\n")
    name_translations = {"fr": name}
    langs = ["en", "es", "it", "de"]
    for i, lang in enumerate(langs):
        if i < len(translations_text):
            name_translations[lang] = translations_text[i].strip()
        else:
            name_translations[lang] = name  # Fallback
    """Ajoute l’univers dans la table Supabase"""
    # Trouve la première image qui commence par "00_"
    files = os.listdir(f"storage/univers/{actual_folder}")
    thumbnail = next((f for f in files if f.startswith(thumbnail_file) and f.endswith(".png")), None)
    if not thumbnail:
        thumbnail = files[0] if files else "placeholder.png"

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{sanitized_folder}/{thumbnail}"

    data = {
        "name": name,
        "slug": sanitized_slug,
        "is_public": True,
        "thumbnail_url": public_url,
        "created_at": "now()"
    }
    
    response = supabase.table(TABLE_NAME).upsert(data, on_conflict="slug").execute()
    if response.data:
        univers_id = response.data[0]["id"]
        # Insérer traductions pour l'univers
        translations = [
            {"univers_id": univers_id, "language": lang, "name": name_translations[lang]}
            for lang in ["fr", "en", "es", "it", "de"]
        ]
        supabase.table("univers_translations").insert(translations).execute()
        print(f"Univers '{name}' ajouté dans la base avec traductions !")
    else:
        print("Erreur DB :", response)

def upload(theme_name: str, actual_folder: str = None, force: bool = False):
    """Upload seulement : upload + ajoute en DB"""
    if actual_folder is None:
        actual_folder = unicodedata.normalize('NFD', theme_name.lower().replace(" ", "_")).encode('ascii', 'ignore').decode('ascii')
    sanitized_slug = unicodedata.normalize('NFD', theme_name.lower().replace(" ", "_")).encode('ascii', 'ignore').decode('ascii')
    local_path = f"storage/univers/{actual_folder}"

    if not os.path.exists(local_path):
        print(f"Erreur : dossier {local_path} n'existe pas. Générez l'univers d'abord.")
        return

    existing = get_existing_folders()
    if sanitized_slug in existing and not force:
        print(f"Univers '{theme_name}' déjà uploadé. Utilisez --force pour re-upload.")
        return

    print(f"Upload de l'univers : {theme_name}")
    upload_folder_to_supabase(local_path, sanitized_slug)

    print("Ajout dans la base de données...")
    add_universe_to_db(theme_name, sanitized_slug, actual_folder)

    print(f"\nUnivers '{theme_name}' uploadé avec succès !")
    print(f"Visible dans l'app : {SUPABASE_URL}/storage/v1/object/public/univers/{sanitized_slug}/")

def upload_all(force: bool = False):
    """Upload tous les univers non encore uploadés"""
    univers_dir = "storage/univers"
    if not os.path.exists(univers_dir):
        print("Erreur : dossier storage/univers n'existe pas.")
        return

    existing = get_existing_folders()
    folders = [f for f in os.listdir(univers_dir) if os.path.isdir(os.path.join(univers_dir, f))]

    for folder in folders:
        # Inférer le nom depuis le folder (remplacer _ par espace et capitaliser)
        name = folder.replace("_", " ").title()
        upload(name, folder, force)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("theme", nargs='?', help="Nom de l'univers existant (ex: Jungle Magique). Si omis, upload tous les univers.")
    parser.add_argument("--force", action="store_true", help="Force l'upload même si déjà présent.")
    args = parser.parse_args()

    if args.theme:
        upload(args.theme, args.force)
    else:
        upload_all(args.force)