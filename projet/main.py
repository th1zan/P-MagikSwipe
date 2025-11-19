import os
import argparse
import json
from dotenv import load_dotenv
from generators import generate_words, generate_image, generate_video

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--theme', type=str, help='Thème pour générer mots, images et vidéos')
    parser.add_argument('--words-only', action='store_true', help='Générer seulement les mots')
    parser.add_argument('--images-only', action='store_true', help='Générer seulement les images (nécessite words.json)')
    parser.add_argument('--videos-only', action='store_true', help='Générer seulement les vidéos (nécessite words.json et images)')
    args = parser.parse_args()

    if not args.theme:
        print("Erreur : --theme est requis.")
        return

    theme = args.theme.lower().replace(' ', '_')
    os.makedirs(f"univers/{theme}", exist_ok=True)

    if args.words_only:
        print(f"Génération de mots pour le thème '{args.theme}'...")
        words = generate_words(args.theme)
        print(f"Mots générés : {words}")
        with open(f"univers/{theme}/words.json", 'w') as f:
            json.dump({"theme": args.theme, "words": words}, f, indent=2)
        print(f"Mots sauvegardés dans univers/{theme}/words.json")
        return

    # Charger les mots
    words_file = f"univers/{theme}/words.json"
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
            img_path = f"univers/{theme}/{i:02d}_{word.replace(' ', '_')}.png"
            if not os.path.exists(img_path):
                print(f"Erreur : Image {img_path} manquante. Lancez --images-only d'abord.")
                continue
            print(f"Génération vidéo pour '{word}'...")
            generate_video(img_path, word, theme, i)
        print("Vidéos générées.")
        return

    # Pipeline complet
    print(f"Génération de mots pour le thème '{args.theme}'...")
    words = generate_words(args.theme)
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
    with open(f"univers/{theme}/data.json", 'w') as f:
        json.dump({"items": items}, f, indent=2)

    # Mettre à jour list.json
    list_path = "univers/list.json"
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