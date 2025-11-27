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

    data = {
        "name": name,
        "folder": folder,
        "is_public": True,
        "thumbnail_url": public_url,
        "created_at": "now()"
    }
    
    response = supabase.table(TABLE_NAME).insert(data).execute()
    if response.data:
        print(f"Univers '{name}' ajouté dans la base !")
    else:
        print("Erreur DB :", response)

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
    add_universe_to_db(theme_name, folder)

    print(f"\nUnivers '{theme_name}' publié avec succès !")
    print(f"Visible dans l'app : {SUPABASE_URL}/storage/v1/object/public/univers/{folder}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("theme", help="Nom de l'univers (ex: Forêt Enchantée)")
    args = parser.parse_args()
    publish(args.theme)