// Common JavaScript utilities for Magik Univers Viewer

// Toast notification system
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<div class="flex items-center gap-3">
    <span class="text-2xl">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
    <span>${message}</span>
  </div>`;
  document.getElementById('toastContainer').appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

// Language flag mapping
function getLangFlag(lang) {
  const flags = {
    'fr': '🇫🇷',
    'en': '🇺🇸',
    'es': '🇪🇸',
    'it': '🇮🇹',
    'de': '🇩🇪'
  };
  return flags[lang] || lang.toUpperCase();
}

// Utility function to get API base URL (using CONFIG if available)
const API_BASE = typeof CONFIG !== 'undefined' ? CONFIG.API_BASE : 'http://localhost:8000/api';