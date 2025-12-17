// Configuration centralisée pour Magik Univers Viewer
// Ce fichier permet de gérer facilement les URLs et chemins selon l'environnement

const CONFIG = {
  // API Configuration
  API_BASE: window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api'
    : '/api', // En production, utiliser un chemin relatif

  STORAGE_BASE: window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '', // In production, use relative paths

  // Helper pour construire un chemin complet vers un asset
  getAssetPath: function(universe, filename) {
    return `${this.STORAGE_BASE}/storage/buckets/univers/${universe}/${filename}`;
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
