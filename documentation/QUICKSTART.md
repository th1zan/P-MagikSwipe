# 🚀 Quickstart - Studio Univers

## ⚡ Démarrage en 5 minutes

### 1️⃣ Configuration (1 min)

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec vos clés
nano .env
```

Renseigner :
- `REPLICATE_API_TOKEN` - Votre token Replicate
- `SUPABASE_URL` - URL de votre projet Supabase
- `SUPABASE_SERVICE_ROLE_KEY` - Clé service role Supabase

### 2️⃣ Optimiser Supabase (2 min)

Ouvrir https://app.supabase.com/project/YOUR_PROJECT/sql

Copier-coller le contenu de `supabase_optimize.sql` et exécuter.

### 3️⃣ Lancer les services (1 min)

```bash
docker compose up -d
```

Vérifier :
```bash
docker compose ps
# Doit afficher studio et api en "running"
```

### 4️⃣ Accéder au Studio (30 sec)

Ouvrir dans le navigateur :
```
http://localhost:8081
```

### 5️⃣ Créer votre premier univers (30 sec)

1. Cliquer sur **"+ Nouvel Univers"**
2. Nom : "Test Ocean"
3. Thème : "ocean"
4. Cliquer sur **"Créer"**
5. Cliquer sur **"🎨 Générer Assets"**
6. Nombre : 3 (pour le test)
7. Attendre ~2 minutes
8. Cliquer sur **"🚀 Publier"**

✅ **C'est fait !** Votre premier univers est créé et publié sur Supabase.

---

## 📖 Workflow détaillé

### Création d'un univers complet

```bash
# 1. Ouvrir le Studio
open http://localhost:8081

# 2. Nouvel Univers
- Cliquer "+ Nouvel Univers"
- Nom: "Jungle Magique"
- Thème: "jungle"
- (Optionnel) Personnaliser les prompts
- Créer

# 3. Générer
- Sélectionner l'univers
- Cliquer "🎨 Générer Assets"
- Choisir 10 assets
- Attendre (suivi en temps réel)

# 4. Itérer (si besoin)
- Cliquer sur un asset
- Cliquer "🔄 Régénérer"
- Modifier le prompt
- Confirmer

# 5. Publier
- Cliquer "🚀 Publier vers Supabase"
- Confirmer
- ✅ Univers disponible dans l'app mobile
```

---

## 🧪 Test rapide via API

```bash
# Lister les univers
curl http://localhost:8000/api/universes

# Créer un univers
curl -X POST http://localhost:8000/api/universes \
  -H "Content-Type: application/json" \
  -d '{"theme": "jungle", "concepts": ["lion", "elephant", "tiger"]}'

# Voir les détails d'un univers
curl http://localhost:8000/api/universes/jungle
```

---

## 🐛 Dépannage

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker compose logs -f

# Rebuilder si nécessaire
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Erreur "REPLICATE_API_TOKEN not set"

```bash
# Vérifier que .env existe et contient le token
cat .env | grep REPLICATE

# Redémarrer l'API
docker compose restart api
```

### Erreur "table does not exist"

```bash
# Vérifier que les tables Supabase sont créées
# Exécuter supabase_optimize.sql dans Supabase SQL Editor
```

### Les images ne s'affichent pas dans le viewer

```bash
# Vérifier que le volume est monté
docker compose exec studio ls -la /usr/share/nginx/html/storage/univers

# Vérifier les permissions
docker compose exec api ls -la /app/storage/univers
```

---

## 🎯 Endpoints principaux

### API (localhost:8000)

```bash
# Lister les univers
curl http://localhost:8000/api/universes

# Créer un univers
curl -X POST http://localhost:8000/api/universes \
  -H "Content-Type: application/json" \
  -d '{"theme": "jungle", "concepts": ["lion", "elephant"]}'

# Voir les détails d'un univers
curl http://localhost:8000/api/universes/{universe_id}

# Publier un univers vers Supabase
curl -X POST http://localhost:8000/api/universes/{universe_id}/publish
```

### Studio (localhost:8081)

- Interface web complète
- Création, génération, régénération, publication
- Prévisualisation en temps réel
- Synchronisation bidirectionnelle avec Supabase

---

## 📚 Documentation complète

- `README_DRAFTS.md` - Architecture détaillée
- `IMPLEMENTATION_COMPLETE.md` - Implémentation complète
- `MIGRATION_SUMMARY.md` - Résumé des changements
- `DOCKER_USAGE.md` - Guide d'utilisation avec Docker 🐳

---

## ✅ Checklist de démarrage

- [ ] Fichier `.env` configuré avec les clés
- [ ] Script `supabase_optimize.sql` exécuté dans Supabase
- [ ] Services Docker lancés (`docker compose up -d`)
- [ ] Studio accessible (http://localhost:8081)
- [ ] API accessible (http://localhost:8000/api/drafts)
- [ ] Premier draft créé et généré
- [ ] Premier univers publié vers Supabase

---

## 🎉 Vous êtes prêt !

Le système est maintenant opérationnel. Profitez de :

- ✨ Création intuitive d'univers
- 🔄 Régénération d'assets individuels
- 📊 Suivi de progression en temps réel
- 🚀 Publication simple vers Supabase
- 📱 Consommation directe par l'app mobile

**Bon développement !** 🚀

---

## 💬 Support

En cas de problème :

1. Consulter les logs : `docker compose logs -f`
2. Vérifier la configuration : `cat .env`
3. Relire la documentation : `README_DRAFTS.md`
4. Tester avec le script : `python3 test_drafts_workflow.py`
