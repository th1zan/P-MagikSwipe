# publish_universe.py
import os
import json
import argparse
from supabase import create_client
from dotenv import load_dotenv
from projet.main import main as generate_universe  # ton script actuel

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
                    remote_path, f.read(), {"upsert": True}
                )
            print(f"Uploaded {remote_path}")

def add_universe_to_db(name: str, folder: str, thumbnail_file: str = "00_"):
    """Ajoute l’univers dans la table Supabase"""
    # Trouve la première image qui commence par "00_"
    files = os.listdir(f"storage/univers/{folder}")
    thumbnail = next((f for f in files if f.startswith(thumbnail_file) and f.endswith(".png")), None)
    if not thumbnail:
        thumbnail = files[0] if files else "placeholder.png"

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{folder}/{thumbnail}"

    # Load background_color from data.json
    data_path = f"storage/univers/{folder}/data.json"
    color = "#ffffff"
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            universe_data = json.load(f)
        color = universe_data.get('background_color', '#ffffff')

    data = {
        "name": name,
        "folder": folder,
        "is_public": True,
        "thumbnail_url": public_url,
        "background_color": color,
        "background_music": "music.mp3",
        "created_at": "now()"
    }

    response = supabase.table(TABLE_NAME).insert(data).execute()
    if response.data:
        univers_id = response.data[0]["id"]
        print(f"Univers '{name}' ajouté dans la base !")
        return univers_id
    else:
        print("Erreur DB :", response)
        return None

def publish(theme_name: str):
    """Étape finale : génère + upload + ajoute en DB"""
    print(f"Génération de l'univers : {theme_name}")
    
    # Étape 1 : génération avec ton script actuel
    import sys
    sys.argv = ["", "--theme", theme_name]  # simule les args
    generate_universe()

    folder = theme_name.lower().replace(" ", "_")
    local_path = f"storage/univers/{folder}"

    if not os.path.exists(local_path):
        print("Erreur : dossier non généré")
        return

    print("Upload vers Supabase Storage...")
    upload_folder_to_supabase(local_path, folder)

    print("Ajout dans la base de données...")
    univers_id = add_universe_to_db(theme_name, folder)
    if not univers_id:
        return

    # Insert assets into univers_assets
    data_path = f"storage/univers/{folder}/data.json"
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            universe_data = json.load(f)
        items = universe_data.get("items", [])
        try:
            inserts = []
            for i, item in enumerate(items):
                inserts.append({
                    "univers_id": univers_id,
                    "sort_order": i,
                    "image_name": item["image"],
                    "display_name": item["title"]
                })
            asset_responses = supabase.table("univers_assets").insert(inserts).execute()
            print(f"Inserted {len(inserts)} assets for {folder}")

            # Insert translations
            for i, item in enumerate(items):
                asset_id = asset_responses.data[i]["id"]
                translations = []
                title_translations = item.get("title_translations", {})
                for lang in ["fr", "en", "es", "it", "de"]:
                    display_name = title_translations.get(lang, item["title"])
                    translations.append({
                        "asset_id": asset_id,
                        "language": lang,
                        "display_name": display_name
                    })
                supabase.table("univers_assets_translations").insert(translations).execute()
            print(f"Inserted translations for {len(items)} assets")
        except Exception as e:
            print(f"DB assets/translations insert error: {e}")

    print(f"\nUnivers '{theme_name}' publié avec succès !")
    print(f"Visible dans l'app : {SUPABASE_URL}/storage/v1/object/public/univers/{folder}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("theme", help="Nom de l'univers (ex: Forêt Enchantée)")
    args = parser.parse_args()
    publish(args.theme)