import os
import argparse
import json
import logging
from dotenv import load_dotenv
from supabase import create_client
from generators import generate_words, generate_image, generate_video, generate_theme_music, get_dominant_color

load_dotenv()

debug = os.getenv('MODE') == 'DEBUG'
logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def update_thumbnail(theme):
    data_path = f"storage/univers/{theme}/data.json"
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
        if 'items' in data and data['items']:
            data['thumbnail'] = data['items'][0]['image']
            with open(data_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Thumbnail updated for {theme}")

def update_background_color(theme, color):
    import re
    if not re.match(r'^#[0-9a-fA-F]{6}$', color):
        print("Couleur invalide")
        return
    data_path = f"storage/univers/{theme}/data.json"
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
        data['background_color'] = color
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Couleur mise à jour pour {theme}")

def populate_assets():
    if not supabase_client:
        print("Erreur: Client Supabase non configuré")
        return
    index_path = "storage/index.json"
    if not os.path.exists(index_path):
        print("Erreur: index.json non trouvé")
        return
    with open(index_path, 'r') as f:
        themes = json.load(f)
    for t in themes:
        folder = t['folder']
        data_path = f"storage/univers/{folder}/data.json"
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
            items = data.get("items", [])
            if items:
                try:
                    inserts = []
                    for i, item in enumerate(items):
                        inserts.append({
                            "univers_folder": folder,
                            "sort_order": i,
                            "image_name": item["image"],
                            "display_name": item["title"]
                        })
                    supabase_client.table("univers_assets").insert(inserts).execute()
                    print(f"Inserted {len(inserts)} assets for {folder}")
                except Exception as e:
                    print(f"DB insert error for {folder}: {e}")
        else:
            print(f"data.json non trouvé pour {folder}")

def sync_univers_db():
    if not supabase_client:
        print("Erreur: Client Supabase non configuré")
        return
    index_path = "storage/index.json"
    if not os.path.exists(index_path):
        print("Erreur: index.json non trouvé")
        return
    with open(index_path, 'r') as f:
        themes = json.load(f)
    for t in themes:
        folder = t['folder']
        name = t['name']
        data_path = f"storage/univers/{folder}/data.json"
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
            color = data.get('background_color', '#ffffff')
            try:
                # Check if row exists
                response = supabase_client.table("univers").select("id").eq("folder", folder).execute()
                update_data = {
                    "name": name,
                    "folder": folder,
                    "background_color": color,
                    "background_music": "music.mp3",
                    "is_public": True
                }
                if response.data:
                    # Update existing
                    supabase_client.table("univers").update(update_data).eq("folder", folder).execute()
                    print(f"Updated DB for {folder}")
                else:
                    # Insert new
                    supabase_client.table("univers").insert(update_data).execute()
                    print(f"Inserted DB row for {folder}")
            except Exception as e:
                print(f"DB sync error for {folder}: {e}")
        else:
            print(f"data.json non trouvé pour {folder}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--theme', type=str, help='Thème pour générer mots, images et vidéos')
    parser.add_argument('--words-only', action='store_true', help='Générer seulement les mots')
    parser.add_argument('--images-only', action='store_true', help='Générer seulement les images (nécessite words.json)')
    parser.add_argument('--videos-only', action='store_true', help='Générer seulement les vidéos (nécessite words.json et images)')
    parser.add_argument('--music-only', action='store_true', help='Générer seulement la musique (nécessite words.json)')
    parser.add_argument('--force-thumbnail', action='store_true', help='Forcer la régénération de la miniature (première image)')
    parser.add_argument('--update-color', action='store_true', help='Mettre à jour la couleur de fond')
    parser.add_argument('--color', type=str, help='Couleur en hex (ex: #10b981)')
    parser.add_argument('--populate-assets', action='store_true', help='Populer la table univers_assets avec les données existantes')
    parser.add_argument('--sync-univers-db', action='store_true', help='Synchroniser la table univers avec les données locales (musique, couleur) sans régénération')
    parser.add_argument('--update-translations', action='store_true', help='Mettre à jour les traductions pour un thème existant (nécessite words.json)')
    parser.add_argument('--upload-translations-only', action='store_true', help='Uploader seulement les traductions vers DB pour un thème existant (nécessite data.json)')
    args = parser.parse_args()

    if args.populate_assets:
        populate_assets()
        return

    if args.sync_univers_db:
        sync_univers_db()
        return

    if args.update_translations:
        if not args.theme:
            print("Erreur : --theme est requis pour --update-translations.")
            return
        theme = args.theme.lower().replace(' ', '_')
        words_file = f"storage/univers/{theme}/words.json"
        if not os.path.exists(words_file):
            print(f"Erreur : {words_file} n'existe pas. Lancez d'abord --words-only.")
            return
        with open(words_file, 'r') as f:
            data = json.load(f)
        words = data["words"]
        # Regenerate translations
        words_dict = generate_words(args.theme)
        # Update words.json
        with open(words_file, 'w') as f:
            json.dump({"theme": args.theme, "words": words, "words_translations": words_dict}, f, indent=2)
        # Update data.json if exists
        data_file = f"storage/univers/{theme}/data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                universe_data = json.load(f)
            items = universe_data.get("items", [])
            for i, item in enumerate(items):
                item["title_translations"] = {
                    lang: words_dict[lang][i] if i < len(words_dict.get(lang, [])) else item["title"]
                    for lang in ["fr", "en", "es", "it", "de"]
                }
            with open(data_file, 'w') as f:
                json.dump(universe_data, f, indent=2)
            logging.info(f"Traductions mises à jour pour {theme}")
        return

    if args.upload_translations_only:
        if not args.theme:
            print("Erreur : --theme est requis pour --upload-translations-only.")
            return
        theme = args.theme.lower().replace(' ', '_')
        logging.info(f"Upload des traductions pour {theme}...")
        data_file = f"storage/univers/{theme}/data.json"
        if not os.path.exists(data_file):
            print(f"Erreur : {data_file} n'existe pas.")
            return
        with open(data_file, 'r') as f:
            universe_data = json.load(f)
        items = universe_data.get("items", [])
        if not supabase_client:
            print("Erreur: Client Supabase non configuré")
            return
        # Get univers_id
        logging.debug(f"Querying univers with slug: {theme}")
        univers_response = supabase_client.table("univers").select("id").eq("slug", theme).execute()
        logging.debug(f"Univers response: {univers_response.data}")
        if not univers_response.data:
            logging.error(f"Univers '{theme}' not found in DB")
            return
        univers_id = univers_response.data[0]["id"]
        logging.debug(f"Univers ID: {univers_id}")
        # Get existing assets
        assets_response = supabase_client.table("univers_assets").select("id, sort_order").eq("univers_id", univers_id).execute()
        asset_map = {asset["sort_order"]: asset["id"] for asset in assets_response.data}
        # Upload translations
        for i, item in enumerate(items):
            asset_id = asset_map.get(i)
            if asset_id:
                translations = item.get("title_translations", {})
                trans_data = [
                    {"asset_id": asset_id, "language": lang, "display_name": translations.get(lang, item["title"])}
                    for lang in ["fr", "en", "es", "it", "de"]
                ]
                supabase_client.table("univers_assets_translations").upsert(trans_data).execute()
        print(f"Traductions uploadées pour {theme}")
        return

    if args.update_color:
        if not args.theme or not args.color:
            print("Erreur: --theme et --color requis pour --update-color")
            return
        theme = args.theme.lower().replace(' ', '_')
        update_background_color(theme, args.color)
        return

    if args.force_thumbnail:
        if args.theme:
            theme = args.theme.lower().replace(' ', '_')
            update_thumbnail(theme)
        else:
            index_path = "storage/index.json"
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    themes = json.load(f)
                for t in themes:
                    update_thumbnail(t['folder'])
        return

    if not args.theme:
        print("Erreur : --theme est requis.")
        return

    theme = args.theme.lower().replace(' ', '_')
    os.makedirs(f"storage/univers/{theme}", exist_ok=True)

    if args.words_only:
        logging.info(f"Génération de mots pour le thème '{args.theme}'...")
        words_dict = generate_words(args.theme, debug=debug)
        words = words_dict["fr"]
        logging.info(f"Mots générés : {words}")
        logging.debug(f"Words dict: {words_dict}")
        with open(f"storage/univers/{theme}/words.json", 'w') as f:
            json.dump({"theme": args.theme, "words": words, "words_translations": words_dict}, f, indent=2)
        logging.info(f"Mots sauvegardés dans storage/univers/{theme}/words.json")
        return

    # Charger les mots
    words_file = f"storage/univers/{theme}/words.json"
    if not os.path.exists(words_file):
        print(f"Erreur : {words_file} n'existe pas. Lancez d'abord --words-only.")
        return
    with open(words_file, 'r') as f:
        data = json.load(f)
        words = data["words"]

    if args.images_only:
        print("Génération des images...")
        for i, word in enumerate(words):
            print(f"Génération image pour '{word}'...")
            generate_image(word, theme, i)
        print("Images générées.")
        return

    if args.videos_only:
        print("Génération des vidéos...")
        for i, word in enumerate(words):
            img_path = f"storage/univers/{theme}/{i:02d}_{word.replace(' ', '_')}.png"
            if not os.path.exists(img_path):
                print(f"Erreur : Image {img_path} manquante. Lancez --images-only d'abord.")
                continue
            print(f"Génération vidéo pour '{word}'...")
            generate_video(img_path, word, theme, i)
        print("Vidéos générées.")
        return

    if args.music_only:
        print("Génération de la musique...")
        generate_theme_music(theme, args.theme)
        print("Musique générée.")
        return

    # Pipeline complet
    print(f"Génération de mots pour le thème '{args.theme}'...")
    words_dict = generate_words(args.theme)
    words = words_dict["fr"]
    print(f"Mots générés : {words}")

    items = []
    for i, word in enumerate(words):
        print(f"Génération image pour '{word}'...")
        img_path = generate_image(word, theme, i)
        print(f"Génération vidéo pour '{word}'...")
        vid_path = generate_video(img_path, word, theme, i)
        items.append({
            "image": os.path.basename(img_path),
            "title": word,
            "video": os.path.basename(vid_path)
        })

    # Sauvegarder data.json
    thumbnail = items[0]["image"] if items else ""
    color = get_dominant_color(f"storage/univers/{theme}/{thumbnail}") if thumbnail else "#ffffff"
    # Ajouter traductions
    for i, item in enumerate(items):
        item["title_translations"] = {
            lang: words_dict[lang][i] if i < len(words_dict.get(lang, [])) else item["title"]
            for lang in ["fr", "en", "es", "it", "de"]
        }
    with open(f"storage/univers/{theme}/data.json", 'w') as f:
        json.dump({"thumbnail": thumbnail, "background_color": color, "items": items, "words_translations": words_dict}, f, indent=2)

    # Insert into univers_assets
    if supabase_client:
        try:
            # Récupérer univers_id
            univers_response = supabase_client.table("univers").select("id").eq("slug", theme).execute()
            if not univers_response.data:
                print(f"Univers '{theme}' not found in DB")
            else:
                univers_id = univers_response.data[0]["id"]
                inserts = []
                for i, item in enumerate(items):
                    asset_data = {
                        "univers_id": univers_id,
                        "sort_order": i,
                        "image_name": item["image"],
                        "display_name": item["title"]
                    }
                    # Insérer asset
                    asset_response = supabase_client.table("univers_assets").insert(asset_data).execute()
                    asset_id = asset_response.data[0]["id"]
                    # Insérer traductions
                    translations = [
                        {"asset_id": asset_id, "language": lang, "display_name": item["title_translations"][lang]}
                        for lang in ["fr", "en", "es", "it", "de"]
                    ]
                    supabase_client.table("univers_assets_translations").insert(translations).execute()
                print(f"Inserted {len(inserts)} assets with translations for {theme}")
        except Exception as e:
            print(f"DB insert error: {e}")

    # Mettre à jour index.json
    list_path = "storage/index.json"
    if os.path.exists(list_path):
        with open(list_path, 'r') as f:
            themes = json.load(f)
    else:
        themes = []
    if not any(t['folder'] == theme for t in themes):
        themes.append({"name": args.theme.capitalize(), "folder": theme})
        with open(list_path, 'w') as f:
            json.dump(themes, f, indent=2)

    print(f"Univers '{args.theme}' généré avec succès !")

if __name__ == "__main__":
    main()