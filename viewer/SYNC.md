# 🔄 Synchronisation avec Supabase

Ce guide explique comment synchroniser vos univers entre différents environnements (ordinateurs, conteneurs) via la base de données Supabase.

## 📤 Publier vers la base de données

### Utilisation
1. Sélectionnez un univers dans le menu déroulant
2. Cliquez sur le bouton **☁️ Publish to DB**
3. Confirmez l'opération

### Ce qui se passe
- Tous les fichiers (images, vidéos, musique) sont uploadés vers Supabase Storage
- Les métadonnées (nom, traductions, ordre) sont enregistrées dans la base de données
- L'univers devient accessible depuis n'importe quel environnement connecté à la même base

### Quand l'utiliser
- ✅ Après avoir créé ou modifié un univers localement
- ✅ Avant de changer d'ordinateur
- ✅ Pour sauvegarder votre travail
- ✅ Pour partager avec d'autres développeurs

## 📥 Charger depuis la base de données

### Utilisation
1. Sélectionnez un univers dans le menu déroulant (même s'il n'existe pas localement)
2. Cliquez sur le bouton **⬇️ Load from DB**
3. Confirmez l'opération

### Ce qui se passe
- **Tous les fichiers locaux existants sont supprimés** (pour éviter les conflits avec des fichiers renommés)
- Les nouveaux fichiers sont téléchargés depuis Supabase Storage
- Les fichiers `data.json` et `prompts.json` sont recréés à partir des données DB

**Important** : Si vous aviez des fichiers avec l'ancien nom (ex: `01_jungle.png`) et qu'ils ont été renommés dans la DB (ex: `01_monkey.png`), les anciens fichiers sont automatiquement supprimés lors de la synchronisation.

### Quand l'utiliser
- ✅ Sur un nouvel ordinateur pour récupérer un univers
- ✅ Après avoir modifié la base de données directement (ex: via Supabase Dashboard)
- ✅ Si vos fichiers locaux sont corrompus ou désynchronisés
- ✅ Quand vous travaillez avec un volume Docker non synchronisé avec Git

## 🔄 Cas d'usage typiques

### Scénario 1 : Nouveau développeur rejoint le projet
```bash
# Sur le nouvel ordinateur
git clone <repo>
docker compose up -d

# Dans l'interface web (http://localhost:8081/index.html)
# 1. Sélectionner "jungle" (ou autre univers)
# 2. Cliquer "⬇️ Load from DB"
# ✅ L'univers est maintenant disponible localement
```

### Scénario 2 : Modification via Supabase Dashboard
```
1. Vous modifiez les traductions dans Supabase Dashboard
2. Dans l'interface web, sélectionnez l'univers modifié
3. Cliquez "⬇️ Load from DB"
4. ✅ Les modifications sont appliquées localement
```

### Scénario 3 : Travail sur deux ordinateurs
```
Ordinateur A :
1. Créer/modifier un univers
2. Cliquer "☁️ Publish to DB"

Ordinateur B :
1. Sélectionner le même univers
2. Cliquer "⬇️ Load from DB"
3. ✅ Les modifications sont synchronisées
```

## ⚠️ Précautions

### Avant de Load from DB
- ⚠️ **Tous les fichiers locaux seront SUPPRIMÉS puis remplacés**
- ⚠️ Si vous avez des modifications locales non publiées, elles seront PERDUES
- ⚠️ Cette opération est **irréversible** - les anciens fichiers ne peuvent pas être récupérés
- 💡 Astuce : Publiez d'abord (`Publish to DB`) si vous avez des modifications locales importantes
- 💡 Astuce : Faites une sauvegarde manuelle si vous avez des fichiers importants non publiés

### Conflits
Si deux personnes modifient le même univers en même temps :
1. La dernière personne à faire `Publish to DB` écrase les modifications précédentes
2. Utilisez `Load from DB` pour récupérer la version la plus récente

## 🔍 Vérification

### Vérifier qu'un univers est publié
```bash
# Via l'API
curl http://localhost:8000/api/universes

# Dans Supabase Dashboard
# 1. Aller dans "Table Editor"
# 2. Ouvrir la table "univers"
# 3. Chercher votre univers par nom/folder
```

### Vérifier les fichiers uploadés
```
URL publique des fichiers :
https://<votre-projet>.supabase.co/storage/v1/object/public/univers/<folder>/

Exemple :
https://xxx.supabase.co/storage/v1/object/public/univers/jungle/00_lion.png
```

## 🛠️ Dépannage

### Erreur : "Universe not found in database"
- L'univers n'a jamais été publié
- Solution : Créez-le localement puis `Publish to DB`

### Erreur : "Supabase not configured"
- Les variables d'environnement ne sont pas définies
- Vérifiez votre fichier `.env` :
  ```
  SUPABASE_URL=https://xxx.supabase.co
  SUPABASE_SERVICE_ROLE_KEY=eyJxxx...
  ```

### Fichiers manquants après Load from DB
- Vérifiez que tous les fichiers ont été uploadés lors du `Publish to DB`
- Vérifiez les logs de l'API : `docker compose logs api`

### Performance lente
- Normal pour les gros univers (beaucoup de vidéos/images)
- Le téléchargement peut prendre plusieurs minutes
- Surveillez les logs : `docker compose logs -f api`

### Fichiers renommés
**Exemple concret** : Si vous aviez `01_jungle.png` localement et que le fichier a été renommé `01_monkey.png` dans la DB :
1. Lors du `Load from DB`, `01_jungle.png` est **supprimé**
2. Puis `01_monkey.png` est téléchargé
3. Résultat : Pas de duplication, juste le bon fichier ✅

## 📊 Statistiques

Après chaque opération, vous verrez :

**Publish to DB :**
- `files_uploaded` : Nombre de fichiers envoyés
- `assets_created` : Nombre d'assets créés dans la DB

**Load from DB :**
- `files_removed` : Nombre d'anciens fichiers supprimés 🆕
- `files_downloaded` : Nombre de nouveaux fichiers téléchargés
- `assets_synced` : Nombre d'assets synchronisés

Ces statistiques vous permettent de vérifier que l'opération s'est bien déroulée.
