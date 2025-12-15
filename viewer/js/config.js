// Configuration centralisée pour Magik Univers Viewer
// Ce fichier permet de gérer facilement les URLs et chemins selon l'environnement

const CONFIG = {
  // API Configuration
  API_BASE: window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : '/api', // En production, utiliser un chemin relatif
  
  // Storage paths - ajustés selon le contexte de la page
  STORAGE_PATH: {
    // Pour index.html (à la racine de viewer/)
    root: 'storage/univers',
    // Pour slideshow.html et gallery.html (à la racine de viewer/)
    relative: '../storage/univers'
  },
  
  // Helper function pour obtenir le bon chemin selon la page
  getStoragePath: function() {
    // Détecte si on est sur slideshow/gallery (qui utilisent ../storage) ou index (qui utilise storage)
    const path = window.location.pathname;
    if (path.includes('slideshow') || path.includes('gallery')) {
      return this.STORAGE_PATH.relative;
    }
    return this.STORAGE_PATH.root;
  },
  
  // Helper pour construire un chemin complet vers un asset
  getAssetPath: function(universe, filename) {
    const basePath = this.getStoragePath();
    return `${basePath}/${universe}/${filename}`;
  },
  
  // Helper pour gérer les extensions vidéo
  normalizeVideoExtension: function(filename) {
    if (!filename) return '';
    // Si déjà en .webm, ne rien faire
    if (filename.endsWith('.webm')) return filename;
    // Sinon, remplacer .mp4 par .webm
    return filename.replace(/\.mp4$/i, '.webm');
  },
  
  // Helper pour construire une URL d'API
  buildApiUrl: function(identifier, endpoint) {
    return `${this.API_BASE}/universes/${identifier}${endpoint}`;
  }
};

// Export pour utilisation dans les autres fichiers
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
