// Index Page JavaScript for Magik Univers Admin

let currentUniverse = null;
let universeData = null;
let currentLang = 'fr';
let isMuted = false;
let presentationActive = false;
let currentSlideIndex = 0;

// ====================== INIT ======================
async function init() {
  console.log('init() - Démarrage de l\'initialisation');
  await loadUniversesList();
  console.log('Initialisation terminée');
}

async function loadUniversesList() {
  console.log('loadUniversesList() - Récupération de la liste des univers');
  try {
    const res = await fetch(`${API_BASE}/universes`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const universes = await res.json();
    const select = document.getElementById('universeSelect');
    select.innerHTML = '<option value="">Choose a universe...</option>';
    universes.forEach(u => {
      const opt = document.createElement('option');
      opt.value = u.folder;
      opt.textContent = u.name;
      select.appendChild(opt);
    });
    console.log(`${universes.length} univers trouvés`);
  } catch (e) {
    console.error('Erreur chargement univers:', e);
    showToast('Impossible de charger les univers', 'error');
  }
}

async function loadUniverse(folder) {
  if (!folder) {
    document.getElementById('overviewPanel').classList.add('hidden');
    document.getElementById('tabsPanel').classList.add('hidden');
    return;
  }
  currentUniverse = folder;
  console.log('Chargement de l\'univers:', folder);
  try {
    const [promptsRes, dataRes, defaultsRes] = await Promise.all([
      fetch(`${API_BASE}/universes/${folder}/prompts`),
      fetch(`${API_BASE}/universes/${folder}/data`),
      fetch(`${API_BASE}/default-prompts`)
    ]);
    const prompts = await promptsRes.json();
    const data = await dataRes.json();
    const defaults = await defaultsRes.json();

    universeData = {
      objects: prompts.words || [],
      images: prompts.images || [],
      videos: prompts.videos || [],
      items: data.items || [], // Add items for correct file paths
      description: data.description || '',
      translations: data.translations || {},
      music_translations: data.music_translations || {}
    };

    document.getElementById('overviewPanel').classList.remove('hidden');
    document.getElementById('tabsPanel').classList.remove('hidden');

    document.getElementById('descriptionInput').value = universeData.description;
    document.getElementById('conceptsDefaultPrompt').value = defaults.objects || '';
    document.getElementById('imagesDefaultPrompt').value = defaults.images || '';
    document.getElementById('videosDefaultPrompt').value = defaults.videos || '';

    populateOverview();
    populateConcepts();
    populateTranslations();
    populateImages();
    populateVideos();
    populateMusic();

    showToast('Univers chargé !', 'success');
  } catch (e) {
    console.error(e);
    showToast('Erreur chargement univers', 'error');
  }
}

function populateOverview() {
  const concepts = universeData.objects || [];
  const imagesReady = (universeData.images || []).filter(Boolean).length;
  const videosReady = (universeData.videos || []).filter(Boolean).length;
  const musicLangs = Object.keys(universeData.music_translations || {}).length;

  document.getElementById('universeInfo').innerHTML = `
    <div class="bg-blue-50 p-4 rounded-xl"><div class="text-2xl font-bold text-blue-600">${concepts.length}</div><div class="text-sm text-gray-600">Concepts</div></div>
    <div class="bg-green-50 p-4 rounded-xl"><div class="text-2xl font-bold text-green-600">${imagesReady}/${concepts.length}</div><div class="text-sm text-gray-600">Images</div></div>
    <div class="bg-purple-50 p-4 rounded-xl"><div class="text-2xl font-bold text-purple-600">${videosReady}/${concepts.length}</div><div class="text-sm text-gray-600">Videos</div></div>
    <div class="bg-pink-50 p-4 rounded-xl"><div class="text-2xl font-bold text-pink-600">${musicLangs}/5</div><div class="text-sm text-gray-600">Music Languages</div></div>
  `;
}

function populateConcepts() {
  const concepts = universeData.objects || [];
  document.getElementById('conceptCount').textContent = concepts.length;
  document.getElementById('conceptsList').innerHTML = concepts.map((c, i) => `
    <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <span class="text-gray-400 font-mono text-sm w-8">${i + 1}.</span>
      <input type="text" value="${c}" class="flex-1" onchange="updateConcept(${i}, this.value)">
      <button onclick="deleteConcept(${i})" class="text-red-500 hover:text-red-700">Delete</button>
    </div>
  `).join('');
}

function populateTranslations() {
  const concepts = universeData.objects || [];
  const translations = universeData.translations || {};
  const langs = ['en', 'fr', 'es', 'it', 'de'];

  const list = document.getElementById('translationsList');
  list.innerHTML = concepts.map((concept, i) => `
    <div class="mb-6 p-4 bg-gray-50 rounded-xl">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-lg font-bold text-gray-800">${concept}</h4>
        <button onclick="translateSingleConcept(${i}, '${concept.replace(/'/g, "\\'")}')" class="btn btn-primary text-sm px-3 py-1">
          🌍 Translate
        </button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        ${langs.map(lang => `
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1">
              ${lang.toUpperCase()} ${getLangFlag(lang)}
            </label>
            <input type="text"
                   value="${translations[lang]?.[i] || ''}"
                   placeholder="Translation..."
                   data-lang="${lang}"
                   data-index="${i}"
                   onchange="updateTranslation('${lang}', ${i}, this.value)">
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function populateImages() {
  const concepts = universeData.objects || [];
  const imagePrompts = universeData.images || [];

  const grid = document.getElementById('imagesGrid');
  grid.innerHTML = concepts.map((concept, i) => {
    const prompt = imagePrompts[i] || '';
    const item = universeData.items?.[i];
    if (!item) return ''; // Skip if no item data
    const imagePath = CONFIG.getAssetPath(currentUniverse, item.image);

    return `
      <div class="asset-card" onclick="showAssetModal('image', ${i}, '${concept}', '${prompt}')">
        <div class="relative">
          <img src="${imagePath}"
               onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22%3E%3Crect fill=%22%23e5e7eb%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%239ca3af%22 font-size=%2220%22 dy=%22.3em%22%3ENo Image%3C/text%3E%3C/svg%3E'"
               alt="${concept}">
          <div class="asset-badge status-pending">Pending</div>
        </div>
        <div class="p-4">
          <h4 class="font-bold text-gray-800 mb-2">${concept}</h4>
          <p class="text-xs text-gray-600 line-clamp-2">${prompt || 'No prompt yet'}</p>
        </div>
      </div>
    `;
  }).join('');
}

function populateVideos() {
  const concepts = universeData.objects || [];
  const videoPrompts = universeData.videos || [];

  const grid = document.getElementById('videosGrid');
  grid.innerHTML = concepts.map((concept, i) => {
    const prompt = videoPrompts[i] || '';
    const item = universeData.items?.[i];
    if (!item) return ''; // Skip if no item data
    const videoPath = CONFIG.getAssetPath(currentUniverse, CONFIG.normalizeVideoExtension(item.video));

    return `
      <div class="asset-card" onclick="showAssetModal('video', ${i}, '${concept}', '${prompt}')">
        <div class="relative">
          <video src="${videoPath}"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'"
                 class="w-full h-48 object-cover"></video>
          <div class="w-full h-48 bg-gray-200 hidden items-center justify-center text-gray-400">
            No Video
          </div>
          <div class="asset-badge status-pending">Pending</div>
        </div>
        <div class="p-4">
          <h4 class="font-bold text-gray-800 mb-2">${concept}</h4>
          <p class="text-xs text-gray-600 line-clamp-2">${prompt || 'No prompt yet'}</p>
        </div>
      </div>
    `;
  }).join('');
}

function populateMusic() {
  const musicData = universeData.music_translations || {};

  const frLyrics = musicData.fr?.lyrics || '';
  const frPrompt = musicData.fr?.prompt || '';

  document.getElementById('musicLyricsFr').value = frLyrics;
  document.getElementById('musicPromptFr').value = frPrompt;

  const langs = ['en', 'es', 'it', 'de'];
  const container = document.getElementById('musicOtherLangs');

  container.innerHTML = langs.map(lang => {
    const data = musicData[lang] || { lyrics: '', prompt: '' };
    return `
      <div class="p-4 bg-gray-50 rounded-xl">
        <h3 class="text-lg font-bold text-gray-800 mb-3">${getLangFlag(lang)} ${lang.toUpperCase()}</h3>
        <label class="block text-sm font-semibold text-gray-700 mb-2">Lyrics</label>
        <textarea id="musicLyrics${lang}" placeholder="Translated lyrics..." onchange="updateMusicLyrics('${lang}', this.value)">${data.lyrics}</textarea>

        <label class="block text-sm font-semibold text-gray-700 mb-2 mt-3">Prompt</label>
        <input id="musicPrompt${lang}" type="text" value="${data.prompt}" placeholder="Music style..." onchange="updateMusicPrompt('${lang}', this.value)">

        <div class="flex gap-2 mt-3">
          <button onclick="generateMusic('${lang}')" class="btn btn-success">Generate</button>
        </div>
      </div>
    `;
  }).join('');
}

function switchTab(tab) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`tab-${tab}`).classList.remove('hidden');
  event.target.classList.add('active');
}

function showCreateModal() {
  const modal = document.getElementById('createModal');
  modal.innerHTML = `
    <div class="modal-overlay" onclick="closeCreateModal(event)">
      <div class="modal-content max-w-md" onclick="event.stopPropagation()">
        <div class="p-6">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">Create New Universe</h2>

          <label class="block text-sm font-semibold text-gray-700 mb-2">Universe Name</label>
          <input id="newUniverseName" type="text" placeholder="e.g., Cars, Animals, Space..." class="mb-4">

          <label class="block text-sm font-semibold text-gray-700 mb-2">Theme Description</label>
          <textarea id="newUniverseTheme" placeholder="e.g., Red Ferrari car, Tesla Model S, yellow school bus..."></textarea>

          <div class="flex gap-3 mt-6">
            <button onclick="createUniverse()" class="btn btn-primary flex-1">Create</button>
            <button onclick="closeCreateModal()" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  `;
  modal.classList.remove('hidden');
}

function closeCreateModal(event) {
  if (!event || event.target.classList.contains('modal-overlay')) {
    document.getElementById('createModal').classList.add('hidden');
  }
}

async function createUniverse() {
  const name = document.getElementById('newUniverseName').value.trim();
  const theme = document.getElementById('newUniverseTheme').value.trim();

  if (!name) {
    showToast('Please enter a universe name', 'error');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/universes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, theme })
    });

    if (res.ok) {
      showToast('Universe created successfully!', 'success');
      closeCreateModal();
      loadUniversesList();
      // Auto-select the new universe
      document.getElementById('universeSelect').value = name.toLowerCase().replace(' ', '_');
      loadUniverse(name.toLowerCase().replace(' ', '_'));
    } else {
      throw new Error('Failed to create universe');
    }
  } catch (e) {
    showToast('Failed to create universe', 'error');
    console.error(e);
  }
}

async function saveDescription() {
   if (!currentUniverse) return;

   const description = document.getElementById('descriptionInput').value;

   try {
     const res = await fetch(`${API_BASE}/universes/${currentUniverse}/data`, {
       method: 'PATCH',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ description })
     });

     if (res.ok) {
       showToast('Description saved!', 'success');
       universeData.description = description;
     } else {
       throw new Error('Failed to save description');
     }
   } catch (e) {
     showToast('Failed to save description', 'error');
     console.error(e);
   }
 }

 async function renameMediaFiles() {
   if (!currentUniverse) return;

   if (!confirm('This will rename existing media files based on current concepts. Continue?')) return;

   try {
     const res = await fetch(`${API_BASE}/universes/${currentUniverse}/rename-media`, {
       method: 'POST'
     });

     const data = await res.json();
     if (res.ok) {
       showToast(data.message, 'success');
       // Reload universe data to reflect changes
       loadUniverse(currentUniverse);
     } else {
       throw new Error(data.detail || 'Failed to rename media files');
     }
   } catch (e) {
     showToast('Failed to rename media files', 'error');
     console.error(e);
   }
 }

async function generateConcepts() {
  if (!currentUniverse) return;

  const prompt = document.getElementById('conceptsDefaultPrompt').value;

  try {
    const res = await fetch(`${API_BASE}/generate/${currentUniverse}/objects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });

    const data = await res.json();
    if (res.ok) {
      universeData.objects = data.objects;
      populateConcepts();
      populateOverview();
      showToast('Concepts generated!', 'success');
    } else {
      throw new Error(data.detail || 'Failed to generate concepts');
    }
  } catch (e) {
    showToast('Failed to generate concepts', 'error');
    console.error(e);
  }
}

async function autoTranslateAll() {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/translations/generate`, {
      method: 'POST'
    });

    const data = await res.json();
    if (res.ok) {
      universeData.translations = data.translations;
      populateTranslations();
      showToast('Translations generated!', 'success');
    } else {
      throw new Error(data.detail || 'Failed to generate translations');
    }
  } catch (e) {
    showToast('Failed to generate translations', 'error');
    console.error(e);
  }
}

async function translateSingleConcept(index, concept) {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/translations/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        concept_index: index,
        concept: concept
      })
    });

    const data = await res.json();
    if (res.ok) {
      // Update only the translations for this specific concept
      const langs = ['en', 'fr', 'es', 'it', 'de'];
      langs.forEach(lang => {
        if (data.translations[lang] && data.translations[lang][index]) {
          if (!universeData.translations[lang]) {
            universeData.translations[lang] = [];
          }
          universeData.translations[lang][index] = data.translations[lang][index];
        }
      });
      populateTranslations();
      showToast(`Translation generated for "${concept}"!`, 'success');
    } else {
      throw new Error(data.detail || 'Failed to generate translation');
    }
  } catch (e) {
    showToast('Failed to generate translation', 'error');
    console.error(e);
  }
}

async function generateImagePrompts() {
  if (!currentUniverse) return;

  const defaultPrompt = document.getElementById('imagesDefaultPrompt').value;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/images/prompts/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ defaultPrompt })
    });

    const data = await res.json();
    if (res.ok) {
      universeData.images = data.prompts;
      populateImages();
      showToast('Image prompts generated!', 'success');
    } else {
      throw new Error(data.detail || 'Failed to generate image prompts');
    }
  } catch (e) {
    showToast('Failed to generate image prompts', 'error');
    console.error(e);
  }
}

async function generateVideoPrompts() {
  if (!currentUniverse) return;

  const defaultPrompt = document.getElementById('videosDefaultPrompt').value;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/videos/prompts/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ defaultPrompt })
    });

    const data = await res.json();
    if (res.ok) {
      universeData.videos = data.prompts;
      populateVideos();
      showToast('Video prompts generated!', 'success');
    } else {
      throw new Error(data.detail || 'Failed to generate video prompts');
    }
  } catch (e) {
    showToast('Failed to generate video prompts', 'error');
    console.error(e);
  }
}

async function generateAllImages() {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/generate/${currentUniverse}/images`, {
      method: 'POST'
    });

    if (res.ok) {
      showToast('Images generation started!', 'success');
    } else {
      throw new Error('Failed to start image generation');
    }
  } catch (e) {
    showToast('Failed to generate images', 'error');
    console.error(e);
  }
}

async function generateAllVideos() {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/generate/${currentUniverse}/videos`, {
      method: 'POST'
    });

    if (res.ok) {
      showToast('Videos generation started!', 'success');
    } else {
      throw new Error('Failed to start video generation');
    }
  } catch (e) {
    showToast('Failed to generate videos', 'error');
    console.error(e);
  }
}

function showAssetModal(type, index, concept, currentPrompt) {
  const modal = document.getElementById('assetModal');
  const isImage = type === 'image';
  const item = universeData.items?.[index];
  if (!item) {
    showToast('Asset data not found', 'error');
    return;
  }
  const filename = isImage ? item.image : CONFIG.normalizeVideoExtension(item.video);
  const assetPath = CONFIG.getAssetPath(currentUniverse, filename);

  modal.innerHTML = `
    <div class="modal-overlay" onclick="closeAssetModal(event)">
      <div class="modal-content" onclick="event.stopPropagation()">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-800">${concept}</h2>
            <button onclick="closeAssetModal()" class="text-gray-400 hover:text-gray-600 text-2xl">×</button>
          </div>

          <div class="mb-6">
            ${isImage
              ? `<img src="${assetPath}" class="w-full rounded-xl" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 800 600%22%3E%3Crect fill=%22%23e5e7eb%22 width=%22800%22 height=%22600%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%239ca3af%22 font-size=%2240%22 dy=%22.3em%22%3ENo Image Generated%3C/text%3E%3C/svg%3E'">`
              : `<video src="${assetPath}" controls class="w-full rounded-xl" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'"></video>
                 <div class="w-full h-96 bg-gray-200 hidden items-center justify-center text-gray-400 text-xl rounded-xl">No Video Generated</div>`
            }
          </div>

          <div class="mb-4">
            <label class="block text-sm font-semibold text-gray-700 mb-2">Prompt</label>
            <textarea id="modalPrompt" class="font-mono text-sm">${currentPrompt}</textarea>
          </div>

          <div class="flex gap-3 flex-wrap">
            <button onclick="saveAssetPrompt('${type}', ${index})" class="btn btn-success">
              Save Prompt
            </button>
            <button onclick="regenerateAsset('${type}', ${index})" class="btn btn-primary">
              Regenerate ${isImage ? 'Image' : 'Video'}
            </button>
            <button onclick="closeAssetModal()" class="btn btn-secondary">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
  modal.classList.remove('hidden');
}

function closeAssetModal(event) {
  if (!event || event.target.classList.contains('modal-overlay')) {
    document.getElementById('assetModal').classList.add('hidden');
  }
}

async function saveAssetPrompt(type, index) {
  if (!currentUniverse) return;

  const prompt = document.getElementById('modalPrompt').value;
  const key = type === 'image' ? 'images' : 'videos';

  // Update local data
  universeData[key][index] = prompt;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/prompts`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [key]: universeData[key] })
    });

    if (res.ok) {
      showToast('Prompt saved!', 'success');
      // Refresh the grid
      if (type === 'image') {
        populateImages();
      } else {
        populateVideos();
      }
    } else {
      throw new Error('Failed to save prompt');
    }
  } catch (e) {
    showToast('Failed to save prompt', 'error');
    console.error(e);
  }
}

async function regenerateAsset(type, index) {
  if (!currentUniverse) return;

  const endpoint = `${API_BASE}/universes/${currentUniverse}/${type === 'image' ? 'images' : 'videos'}/${index}/regenerate`;

  try {
    const res = await fetch(endpoint, { method: 'POST' });

    if (res.ok) {
      showToast(`${type === 'image' ? 'Image' : 'Video'} regeneration started!`, 'success');
      closeAssetModal();
    } else {
      throw new Error(`Failed to regenerate ${type}`);
    }
  } catch (e) {
    showToast(`Failed to regenerate ${type}`, 'error');
    console.error(e);
  }
}

function updateConcept(index, value) {
  universeData.objects[index] = value;
}

function updateTranslation(lang, index, value) {
  if (!universeData.translations[lang]) {
    universeData.translations[lang] = [];
  }
  universeData.translations[lang][index] = value;
}

function updateMusicLyrics(lang, value) {
  if (!universeData.music_translations[lang]) {
    universeData.music_translations[lang] = { lyrics: '', prompt: '' };
  }
  universeData.music_translations[lang].lyrics = value;
}

function updateMusicPrompt(lang, value) {
  if (!universeData.music_translations[lang]) {
    universeData.music_translations[lang] = { lyrics: '', prompt: '' };
  }
  universeData.music_translations[lang].prompt = value;
}

function deleteConcept(index) {
  universeData.objects.splice(index, 1);
  // Also remove corresponding prompts
  if (universeData.images && universeData.images.length > index) {
    universeData.images.splice(index, 1);
  }
  if (universeData.videos && universeData.videos.length > index) {
    universeData.videos.splice(index, 1);
  }
  populateConcepts();
  populateImages();
  populateVideos();
  populateOverview();
}

function addConceptManually() {
  const concept = prompt('Enter new concept:');
  if (concept && concept.trim()) {
    universeData.objects.push(concept.trim());
    populateConcepts();
    populateOverview();
  }
}

async function saveConcepts() {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/prompts`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ words: universeData.objects })
    });

    if (res.ok) {
      showToast('Concepts saved!', 'success');
    } else {
      throw new Error('Failed to save concepts');
    }
  } catch (e) {
    showToast('Failed to save concepts', 'error');
    console.error(e);
  }
}

async function saveTranslations() {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/data`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ translations: universeData.translations })
    });

    if (res.ok) {
      showToast('Translations saved!', 'success');
    } else {
      throw new Error('Failed to save translations');
    }
  } catch (e) {
    showToast('Failed to save translations', 'error');
    console.error(e);
  }
}

async function saveMusic() {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/data`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ music_translations: universeData.music_translations })
    });

    if (res.ok) {
      showToast('Music data saved!', 'success');
    } else {
      throw new Error('Failed to save music data');
    }
  } catch (e) {
    showToast('Failed to save music data', 'error');
    console.error(e);
  }
}

async function generateLyricsAI() {
  if (!currentUniverse) return;

  try {
    showToast('Generating lyrics with AI...', 'info');

    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/lyrics/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        theme: currentUniverse,
        words: universeData.objects || []
      })
    });

    const data = await res.json();
    if (res.ok) {
      // Update French lyrics
      const lyrics = data.lyrics || '';
      document.getElementById('musicLyricsFr').value = lyrics;
      updateMusicLyrics('fr', lyrics);

      showToast('Lyrics generated with AI!', 'success');
    } else {
      throw new Error(data.detail || 'Failed to generate lyrics');
    }
  } catch (e) {
    showToast('Failed to generate lyrics', 'error');
    console.error(e);
  }
}

async function translateLyrics() {
  if (!currentUniverse) return;

  const frLyrics = document.getElementById('musicLyricsFr').value;

  if (!frLyrics.trim()) {
    showToast('Please add French lyrics first', 'error');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/generate/lyrics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lyrics: frLyrics })
    });

    if (res.ok) {
      showToast('Lyrics translated!', 'success');
      // Reload universe data to get updated translations
      loadUniverse(currentUniverse);
    } else {
      throw new Error('Failed to translate lyrics');
    }
  } catch (e) {
    showToast('Failed to translate lyrics', 'error');
    console.error(e);
  }
}

async function generateMusic(lang) {
  if (!currentUniverse) return;

  try {
    const res = await fetch(`${API_BASE}/generate/${currentUniverse}/music/${lang}`, {
      method: 'POST'
    });

    if (res.ok) {
      showToast(`Music generation started for ${lang.toUpperCase()}!`, 'success');
    } else {
      throw new Error(`Failed to generate music for ${lang}`);
    }
  } catch (e) {
    showToast(`Failed to generate music for ${lang}`, 'error');
    console.error(e);
  }
}

async function publishToSupabase() {
  if (!currentUniverse) {
    showToast('Please select a universe first', 'error');
    return;
  }

  if (!confirm(`Publish "${currentUniverse}" to Supabase database?\n\nThis will upload all files and update the database.`)) {
    return;
  }

  const publishBtn = document.getElementById('publishBtn');
  const originalText = publishBtn.innerHTML;
  publishBtn.disabled = true;
  publishBtn.innerHTML = '⏳ Publishing...';

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/publish`, {
      method: 'POST'
    });

    const data = await res.json();
    if (res.ok) {
      showToast(`✅ Published successfully! ${data.files_uploaded} files uploaded, ${data.assets_created} assets created.`, 'success');
      console.log('Published to:', data.public_url);
    } else {
      throw new Error(data.detail || 'Failed to publish');
    }
  } catch (e) {
    showToast('Failed to publish to database', 'error');
    console.error(e);
  } finally {
    publishBtn.disabled = false;
    publishBtn.innerHTML = originalText;
  }
}

async function syncFromSupabase() {
  if (!currentUniverse) {
    showToast('Please select a universe first', 'error');
    return;
  }

  if (!confirm(`Load "${currentUniverse}" from Supabase database?\n\nThis will download all files and data from the database and overwrite local files.`)) {
    return;
  }

  const syncBtn = document.getElementById('syncBtn');
  const originalText = syncBtn.innerHTML;
  syncBtn.disabled = true;
  syncBtn.innerHTML = '⏳ Loading...';

  try {
    const res = await fetch(`${API_BASE}/universes/${currentUniverse}/sync-from-db`, {
      method: 'POST'
    });

    const data = await res.json();
    if (res.ok) {
      const message = `✅ Synced successfully! ${data.files_removed || 0} old files removed, ${data.files_downloaded} new files downloaded, ${data.assets_synced} assets synced.`;
      showToast(message, 'success');
      console.log('Synced from DB to:', data.local_path);
      
      // Reload the universe to show updated data
      await loadUniverse(currentUniverse);
    } else {
      throw new Error(data.detail || 'Failed to sync from database');
    }
  } catch (e) {
    showToast('Failed to load from database', 'error');
    console.error(e);
  } finally {
    syncBtn.disabled = false;
    syncBtn.innerHTML = originalText;
  }
}

// ====================== SLIDESHOW ======================
function enterSlideshow() {
  if (!currentUniverse || !universeData) {
    showToast('Please select a universe first', 'error');
    return;
  }
  document.getElementById('langSelect').value = currentLang;
  document.getElementById('muteBtn').textContent = isMuted ? '🔇' : '🔊';
  document.getElementById('slideshowMode').classList.remove('hidden');
  document.getElementById('mainContainer').classList.add('hidden'); // Hide main container
  populateSlideshow();
  startMusic();
}

function exitSlideshow() {
  if (presentationActive) {
    stopPresentation();
  }
  document.getElementById('slideshowMode').classList.add('hidden');
  document.getElementById('mainContainer').classList.remove('hidden');
  stopMusic();
  document.removeEventListener('keydown', handleKeyNavigation);
}

function populateSlideshow() {
  const grid = document.getElementById('imagesGridSlideshow');
  const concepts = universeData.objects || [];
  const translations = universeData.translations || {};
  const items = universeData.items || [];

  grid.innerHTML = concepts.map((concept, i) => {
    const item = items[i];
    if (!item) return ''; // Skip if no item
    const imagePath = CONFIG.getAssetPath(currentUniverse, item.image || `image_${i}.png`);
    const narration = translations[currentLang]?.[i] || concept;
    return `
      <div class="asset-card" onclick="goToSlide(${i})">
        <img src="${imagePath}" alt="${concept}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 200 150%22%3E%3Crect fill=%22%23e5e7eb%22 width=%22200%22 height=%22150%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%239ca3af%22 font-size=%2212%22 dy=%22.3em%22%3ENo Image%3C/text%3E%3C/svg%3E'">
        <div class="asset-title">${narration}</div>
      </div>
    `;
  }).join('');
}

function playVideo(index) {
  console.log('playVideo called for index:', index);
  const items = universeData.items || [];
  const item = items[index];
  if (!item || !item.video) {
    showToast('Video not available', 'error');
    return;
  }
  const videoPath = CONFIG.getAssetPath(currentUniverse, CONFIG.normalizeVideoExtension(item.video));
  console.log('Video path:', videoPath);
  const videoPlayer = document.getElementById('videoPlayer');
  videoPlayer.src = videoPath;
  videoPlayer.load();
  document.getElementById('videoModal').classList.remove('hidden');
  // Delay play to ensure modal is rendered and handle autoplay policies
  setTimeout(() => {
    videoPlayer.play().then(() => {
      console.log('Video playing successfully');
    }).catch(e => {
      console.error('Video play failed:', e);
      showToast('Click the video to start playback', 'info');
      // Add click handler to play on user interaction
      videoPlayer.onclick = () => {
        videoPlayer.play().catch(err => console.error('Play on click failed:', err));
      };
    });
  }, 100);
}

function closeVideoModal() {
  const videoPlayer = document.getElementById('videoPlayer');
  videoPlayer.pause();
  videoPlayer.src = '';
  document.getElementById('videoModal').classList.add('hidden');
}

function changeLanguage(lang) {
  currentLang = lang;
  populateSlideshow();
  startMusic(); // Restart music for new lang
}

function startMusic() {
  const musicPath = CONFIG.getAssetPath(currentUniverse, `music_${currentLang}.mp3`);
  const audio = document.getElementById('bgMusic');
  audio.src = musicPath;
  audio.volume = isMuted ? 0 : 0.5;
  audio.play().catch(() => {}); // Ignore autoplay block
}

function stopMusic() {
  const audio = document.getElementById('bgMusic');
  audio.pause();
  audio.src = '';
}

function toggleMute() {
  isMuted = !isMuted;
  const audio = document.getElementById('bgMusic');
  audio.volume = isMuted ? 0 : 0.5;
  document.getElementById('muteBtn').textContent = isMuted ? '🔇' : '🔊';
}

// ====================== PRESENTATION MODE ======================
function startPresentation() {
  presentationActive = true;
  currentSlideIndex = 0;
  document.getElementById('contactSheet').classList.add('hidden');
  document.getElementById('presentationMode').classList.remove('hidden');
  document.getElementById('startPresentationBtn').textContent = '◼️ Stop';
  document.getElementById('startPresentationBtn').onclick = stopPresentation;
  showSlide(currentSlideIndex);
  // Add keyboard navigation
  document.addEventListener('keydown', handleKeyNavigation);
}

function stopPresentation() {
  presentationActive = false;
  document.getElementById('contactSheet').classList.remove('hidden');
  document.getElementById('presentationMode').classList.add('hidden');
  document.getElementById('startPresentationBtn').textContent = '▶️ Start Presentation';
  document.getElementById('startPresentationBtn').onclick = startPresentation;
  document.removeEventListener('keydown', handleKeyNavigation);
}

function showSlide(index) {
  const concepts = universeData.objects || [];
  const translations = universeData.translations || {};
  const items = universeData.items || [];

  if (index < 0) index = concepts.length - 1;
  if (index >= concepts.length) index = 0;

  currentSlideIndex = index;

  const concept = concepts[index];
  const item = items[index];
  if (!item) {
    console.warn('No item data for slide', index);
    return;
  }
  const imagePath = CONFIG.getAssetPath(currentUniverse, item.image || `image_${index}.png`);
  const narration = translations[currentLang]?.[index] || concept;

  const slideContainer = document.getElementById('presentationSlide');
  slideContainer.innerHTML = `
    <img src="${imagePath}"
         alt="${concept}"
         onclick="playVideoFromSlide(${index})"
         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 800 600%22%3E%3Crect fill=%22%23e5e7eb%22 width=%22800%22 height=%22600%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%239ca3af%22 font-size=%2240%22 dy=%22.3em%22%3ENo Image%3C/text%3E%3C/svg%3E'">
    <div class="presentation-title">${narration}</div>
  `;

  document.getElementById('slideCounter').textContent = `${index + 1} / ${concepts.length}`;
}

function nextSlide() {
  if (!presentationActive) return;
  showSlide(currentSlideIndex + 1);
}

function previousSlide() {
  if (!presentationActive) return;
  showSlide(currentSlideIndex - 1);
}

function goToSlide(index) {
  if (!presentationActive) {
    startPresentation();
  }
  showSlide(index);
}

function handleKeyNavigation(e) {
  if (!presentationActive) return;
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
    e.preventDefault();
    nextSlide();
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault();
    previousSlide();
  } else if (e.key === 'Escape') {
    stopPresentation();
  }
}

function playVideoFromSlide(index) {
  playVideo(index);
  // Store current slide index for return
  const videoPlayer = document.getElementById('videoPlayer');
  videoPlayer.dataset.slideIndex = index;
  // Optional: Auto-advance to next slide when video ends
  videoPlayer.onended = () => {
    // Just close and return to current slide, don't auto-advance
    closeVideoModal();
  };
}

// ====================== DÉMARRAGE ======================
// LE PLUS IMPORTANT : on initialise UNIQUEMENT quand tout est prêt
window.addEventListener('load', () => {
  console.log('Page entièrement chargée - lancement de init()');
  init();
});