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
2. Créez `.env` basé sur `.env.example` avec votre `REPLICATE_API_TOKEN`, `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY`.

## Utilisation
### Avec Docker (recommandé)
1. Construisez : `./run.sh build`
2. Lancez complet : `./run.sh run jungle`
3. Étapes séparées :
    - Mots : `./run.sh run jungle --words-only`
    - Images : `./run.sh run jungle --images-only`
    - Vidéos : `./run.sh run jungle --videos-only`
    - Musique : `./run.sh run jungle --music-only`
4. Populer la DB : `./run.sh run --populate-assets` (popule univers_assets pour tous les univers existants)
5. Sync DB : `./run.sh run --sync-univers-db` (synchronise la table univers avec musique/couleur sans régénération, insère si manquant)
6. Ouvrez `viewer.html` dans un navigateur pour visualiser.

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
    - Musique : `python main.py --theme jungle --music-only`
4. Populer la DB : `python main.py --populate-assets` (popule univers_assets pour tous les univers existants)
5. Sync DB : `python main.py --sync-univers-db` (synchronise la table univers avec musique/couleur sans régénération, insère si manquant)

## Upload vers Supabase
Une fois l'univers généré, vous pouvez l'uploader vers Supabase Storage et mettre à jour la base de données.

### Configuration Supabase
1. Créez un projet Supabase.
2. Créez un bucket public `univers`.
3. Créez les tables via les requêtes SQL ci-dessous.
4. Copiez l'URL du projet et la clé service_role dans `.env`.

### Requêtes SQL pour créer les tables dans Supabase
Utilisez ces requêtes dans l'interface SQL Editor de Supabase pour créer les tables nécessaires. (Note: Les tables sont déjà créées dans le projet actuel.)

Pour ajouter les colonnes manquantes si elles n'existent pas :
```sql
alter table univers add column if not exists background_color text;
alter table univers add column if not exists background_music text;
```

#### Table `univers`
```sql
create table univers (
  id int8 primary key,
  name text,
  folder text unique,
  thumbnail_url text,
  background_color text,
  background_music text,
  is_public boolean,
  created_at timestamptz
);
```

#### Table `univers_assets`
```sql
create table univers_assets (
  id uuid primary key default uuid_generate_v4(),
  univers_folder text not null,
  sort_order int not null,
  image_name text not null,
  display_name text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index idx_univers_assets_folder on univers_assets(univers_folder);
create index idx_univers_assets_order on univers_assets(univers_folder, sort_order);
```

### Utilisation
- **Upload seulement** (univers déjà généré) : `python upload_universe.py "Nom de l'Univers"`
- **Upload tous les univers** : `python upload_universe.py` (sans argument)
- **Forcer l'upload** : `python upload_universe.py --force` (re-upload même si déjà présent)
- **Génération + Upload** (tout en un) : `python publish_universe.py "Nom de l'Univers"`

Exemples :
- `python upload_universe.py "Jungle Magique"`
- `python publish_universe.py "Océan Enchanté"`

Les fichiers sont uploadés dans le bucket Supabase et l'entrée est ajoutée dans la table `univers`.

## Fonctionnement
- Génère 10 mots-clés via Replicate (Llama-2-70B-Chat).
- Crée images via Replicate (Recraft-V3).
- Anime les images en vidéos courtes via Replicate (WAN 2.2 I2V).
- Génère musique thématique via Replicate (Minimax Music-1.5).
- Met à jour `univers/list.json` et crée `univers/{theme}/data.json`.

## Dépendances
- replicate : Appels IA
- moviepy : Édition vidéo (ajout audio)
- gtts : Génération TTS
- pillow : Traitement images
- requests : Téléchargements
- python-dotenv : Variables d'environnement