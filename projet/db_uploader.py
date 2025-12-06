import os
import json
import logging
from dotenv import load_dotenv
from supabase import create_client
from deep_translator import GoogleTranslator

load_dotenv()

debug = os.getenv('MODE') == 'DEBUG'
logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def upload_universe_data(theme: str):
    """
    Upload univers, assets et traductions de manière cohérente.
    """
    data_file = f"storage/univers/{theme}/data.json"
    if not os.path.exists(data_file):
        logging.error(f"Data file not found: {data_file}")
        return

    with open(data_file, 'r') as f:
        data = json.load(f)

    # Upload univers (si pas existant)
    univers_data = {
        "name": data.get("univers_name", data["theme"].capitalize()),
        "slug": theme,
        "is_public": True,
        "thumbnail_url": f"{SUPABASE_URL}/storage/v1/object/public/univers/{theme}/{data.get('thumbnail', '')}",
        "background_color": data.get("background_color", "#ffffff"),
        "background_music": "music.mp3"
    }
    univers_response = supabase_client.table("univers").upsert(univers_data, on_conflict="slug").execute()
    univers_id = univers_response.data[0]["id"]
    logging.info(f"Univers uploaded: {theme}")

    # Fetch the name from univers table for accurate translation
    univers_info = supabase_client.table("univers").select("name").eq("id", univers_id).execute()
    univers_name = univers_info.data[0]["name"] if univers_info.data else data["theme"]
    logging.debug(f"Using univers name for translation: {univers_name}")

    # Upload univers translations
    univers_translations = data.get("univers_translations", {})
    if not univers_translations:
        # Translate univers_name if absent
        univers_name = data.get("univers_name", data["theme"].capitalize())
        univers_translations = {"en": univers_name}
        for lang in ["fr", "es", "it", "de"]:
            univers_translations[lang] = GoogleTranslator(source='en', target=lang).translate(univers_name)
        logging.info(f"Translated univers: {univers_translations}")
    univers_trans_data = [
        {"univers_id": univers_id, "language": lang, "name": univers_translations.get(lang, data.get("univers_name", data["theme"]))}
        for lang in ["en", "fr", "es", "it", "de"]
    ]
    supabase_client.table("univers_translations").upsert(univers_trans_data, on_conflict="univers_id,language").execute()
    logging.info(f"Univers translations uploaded for {theme}")

    # Upload assets
    items = data.get("items", [])
    for item in items:
        asset_data = {
            "univers_id": univers_id,
            "sort_order": items.index(item),
            "image_name": item["image"],
            "display_name": item["title"]  # en
        }
        asset_response = supabase_client.table("univers_assets").upsert(asset_data, on_conflict="univers_id,sort_order").execute()
        asset_id = asset_response.data[0]["id"]

        # Upload translations
        translations = item.get("title_translations", {})
        trans_data = [
            {"asset_id": asset_id, "language": lang, "display_name": translations.get(lang, item["title"])}
            for lang in ["en", "fr", "es", "it", "de"]
        ]
        supabase_client.table("univers_assets_translations").upsert(trans_data, on_conflict="asset_id,language").execute()

    logging.info(f"Assets and translations uploaded for {theme}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python db_uploader.py <theme>")
        sys.exit(1)
    upload_universe_data(sys.argv[1])