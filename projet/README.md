# Magik Swipe

Projet pour générer des univers magiques pour enfants : mots → images → vidéos animées courtes, avec un viewer swipeable.

## Structure
- `main.py` : Script principal pour génération.
- `generators.py` : Fonctions de génération (mots, images, vidéos).
- `viewer.html` : Interface web pour naviguer les univers.
- `univers/` : Dossier pour données générées (images, vidéos, métadonnées).
- `Dockerfile` : Conteneur pour exécution.
- `run.sh` : Script pour build et run.

## Installation
1. Clonez ou copiez le projet.
2. Créez `.env` basé sur `.env.example` avec votre `REPLICATE_API_TOKEN`.

## Utilisation
### Avec Docker (recommandé)
1. Construisez : `./run.sh build`
2. Lancez complet : `./run.sh run jungle`
3. Étapes séparées :
   - Mots : `./run.sh run jungle --words-only`
   - Images : `./run.sh run jungle --images-only`
   - Vidéos : `./run.sh run jungle --videos-only`
4. Ouvrez `viewer.html` dans un navigateur pour visualiser.

### Avec Docker Compose
1. `docker compose up -d`
2. Les services démarrent automatiquement.

### Localement
1. Installez deps : `pip install -r requirements.txt`
2. Lancez complet : `python main.py --theme jungle`
3. Étapes séparées :
   - Mots : `python main.py --theme jungle --words-only`
   - Images : `python main.py --theme jungle --images-only`
   - Vidéos : `python main.py --theme jungle --videos-only`

## Fonctionnement
- Génère 10 mots-clés via Replicate (Llama-3.3-70B).
- Crée images via Replicate (Recraft-V3).
- Anime les images en vidéos courtes via Replicate (WAN 2.2 I2V).
- Ajoute audio TTS français avec gTTS/MoviePy.
- Met à jour `univers/list.json` et crée `univers/{theme}/data.json`.

## Dépendances
- replicate : Appels IA
- moviepy : Édition vidéo (ajout audio)
- gtts : Génération TTS
- pillow : Traitement images
- requests : Téléchargements
- python-dotenv : Variables d'environnement