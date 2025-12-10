# 🚀 Comment accéder au Viewer

## ⚠️ IMPORTANT : Utilisez le bon URL !

Le viewer **DOIT** être accédé via le serveur nginx Docker sur :

```
http://localhost:8081
```

### ✅ URLs Correctes

- **Gallery** : http://localhost:8081/gallery.html
- **Admin Panel** : http://localhost:8081/index.html
- **Slideshow** : http://localhost:8081/slideshow.html?universe=nom_univers

### ❌ URLs Incorrectes (Ne fonctionnent PAS)

- ❌ `file:///Users/.../viewer/gallery.html` (fichier local)
- ❌ `http://localhost:3000/viewer/gallery.html` (mauvais port)
- ❌ `/viewer/gallery.html` (chemin absolu sans domaine)

## 🐳 Lancer les services

```bash
# Démarrer tous les services
docker compose up -d

# Vérifier que tout tourne
docker compose ps

# Voir les logs
docker compose logs -f viewer
```

## 🔧 Résolution des problèmes

### Erreur : `Unexpected token '<'` dans les fichiers JS

**Cause** : Vous n'utilisez pas le bon serveur.

**Solution** : Accédez via `http://localhost:8081/gallery.html`

### Erreur : `ReferenceError: CONFIG is not defined`

**Cause** : Les scripts ne se chargent pas dans le bon ordre.

**Solution** : Vérifiez que `config.js` est chargé en premier dans le HTML.

### Le viewer ne se connecte pas à l'API

**Cause** : L'API n'est pas lancée ou le port est incorrect.

**Solution** : 
- Vérifiez que l'API tourne : `docker compose ps`
- L'API doit être sur `http://localhost:8000`
- Vérifiez `js/config.js` : `API_BASE`

## 📁 Structure

```
viewer/
  ├── js/
  │   ├── config.js      ← Configuration centralisée (chargé en 1er)
  │   ├── common.js      ← Fonctions communes
  │   ├── gallery.js     ← Page gallery
  │   ├── index.js       ← Page admin
  │   └── slideshow.js   ← Page slideshow
  ├── css/
  ├── gallery.html       ← Galerie des univers
  ├── index.html         ← Panel admin
  └── slideshow.html     ← Mode présentation
```
