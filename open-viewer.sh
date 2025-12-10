#!/bin/bash
# Script pour ouvrir le viewer correctement dans le navigateur

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Magik Univers Viewer${NC}"
echo ""

# Vérifier que Docker tourne
if ! docker compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Les conteneurs ne sont pas lancés${NC}"
    echo -e "${BLUE}Démarrage des services...${NC}"
    docker compose up -d
    sleep 3
fi

# Afficher les URLs
echo -e "${GREEN}✅ Services en cours d'exécution${NC}"
echo ""
echo -e "${BLUE}📱 URLs disponibles :${NC}"
echo ""
echo -e "  🏠 Gallery:      ${GREEN}http://localhost:8081/gallery.html${NC}"
echo -e "  ⚙️  Admin Panel:  ${GREEN}http://localhost:8081/index.html${NC}"
echo -e "  🎠 Slideshow:     ${GREEN}http://localhost:8081/slideshow.html?universe=jungle${NC}"
echo ""
echo -e "${YELLOW}⚠️  N'utilisez PAS /viewer/ dans l'URL !${NC}"
echo ""
echo -e "  🔌 API:          ${GREEN}http://localhost:8000/api${NC}"
echo ""

# Ouvrir le navigateur (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${BLUE}🌐 Ouverture de la galerie dans le navigateur...${NC}"
    open http://localhost:8081/gallery.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8081/gallery.html
fi

echo ""
echo -e "${YELLOW}💡 Astuce : Utilisez toujours http://localhost:8081, jamais file://${NC}"
