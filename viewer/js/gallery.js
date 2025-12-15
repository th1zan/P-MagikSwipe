// Gallery + Slideshow JavaScript for Magik Univers

let currentUniverse = null;
let universeData = null;
let currentLang = 'fr';
let isMuted = false;
let presentationActive = false;
let currentSlideIndex = 0;

// ========== GALLERY FUNCTIONS ==========

async function loadGallery() {
  console.log('Loading gallery...');

  try {
    const res = await fetch(`${API_BASE}/universes`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const universes = await res.json();
    console.log('Loaded universes:', universes);

    document.getElementById('loadingState').classList.add('hidden');

    if (universes.length === 0) {
      document.getElementById('emptyState').classList.remove('hidden');
      return;
    }

    // Load data for each universe to get item counts
    const universesWithData = await Promise.all(
      universes.map(async (u) => {
        try {
          const dataRes = await fetch(`${API_BASE}/universes/${u.folder}/data`);
          const data = await dataRes.json();
          return {
            ...u,
            itemCount: data.items?.length || 0,
            thumbnail: data.items?.[0]?.image || null
          };
        } catch (e) {
          console.error(`Error loading data for ${u.folder}:`, e);
          return { ...u, itemCount: 0, thumbnail: null };
        }
      })
    );

    const grid = document.getElementById('universesGrid');
    grid.innerHTML = universesWithData.map(u => {
      const thumbnailPath = u.thumbnail
        ? CONFIG.getAssetPath(u.folder, u.thumbnail)
        : 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22%3E%3Crect fill=%22%23667eea%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22white%22 font-size=%2240%22 dy=%22.3em%22%3E✨%3C/text%3E%3C/svg%3E';

      return `
        <div class="universe-card" onclick="openUniverse('${u.folder}', '${u.name.replace(/'/g, "\\'")}')">
          <div class="badge">${u.itemCount} items</div>
          <img src="${thumbnailPath}"
               alt="${u.name}"
               onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22%3E%3Crect fill=%22%23667eea%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22white%22 font-size=%2240%22 dy=%22.3em%22%3E✨%3C/text%3E%3C/svg%3E'">
          <div class="universe-info">
            <div class="universe-title">${u.name}</div>
            <div class="universe-count">🎠 Click to explore</div>
          </div>
        </div>
      `;
    }).join('');

    grid.classList.remove('hidden');

  } catch (e) {
    console.error('Error loading gallery:', e);
    document.getElementById('loadingState').innerHTML = `
      <div class="text-center text-white">
        <div class="text-4xl mb-4">⚠️</div>
        <div class="text-xl">Failed to load universes</div>
        <button onclick="location.reload()" class="btn mt-4">Retry</button>
      </div>
    `;
  }
}

async function openUniverse(folder, name) {
  currentUniverse = folder;
  document.getElementById('galleryView').classList.add('hidden');
  document.getElementById('slideshowView').classList.remove('hidden');
  document.getElementById('universeTitle').textContent = name || folder;

  try {
    const res = await fetch(`${API_BASE}/universes/${folder}/data`);
    universeData = await res.json();
    populateContactSheet();
    startMusic();
  } catch (e) {
    console.error('Error loading universe:', e);
    backToGallery();
  }
}

function backToGallery() {
  stopPresentation();
  const audio = document.getElementById('bgMusic');
  if (audio) audio.pause();
  document.getElementById('slideshowView').classList.add('hidden');
  document.getElementById('galleryView').classList.remove('hidden');
  currentUniverse = null;
  universeData = null;
}

// ========== SLIDESHOW FUNCTIONS ==========

function populateContactSheet() {
  const grid = document.getElementById('imagesGrid');
  const items = universeData?.items || [];

  grid.innerHTML = items.map((item, i) => {
    if (!item?.image) return '';
    const imagePath = CONFIG.getAssetPath(currentUniverse, item.image);
    const title = item.title_translations?.[currentLang] || item.title;
    return `
      <div class="asset-card cursor-pointer hover:scale-105 transition" onclick="goToSlide(${i})">
        <img src="${imagePath}" alt="${item.title}" class="w-full h-32 object-cover rounded-lg shadow-lg">
        <div class="text-center text-white font-bold mt-2 drop-shadow">${title}</div>
      </div>
    `;
  }).join('');
}

function startPresentation() {
  presentationActive = true;
  currentSlideIndex = 0;
  document.getElementById('contactSheet').classList.add('hidden');
  document.getElementById('presentationMode').classList.remove('hidden');
  document.getElementById('startPresentationBtn').textContent = '◼️ Stop';
  document.getElementById('startPresentationBtn').onclick = stopPresentation;
  showSlide(currentSlideIndex);
  document.addEventListener('keydown', handleKeyNavigation);
}

function stopPresentation() {
  presentationActive = false;
  document.getElementById('contactSheet').classList.remove('hidden');
  document.getElementById('presentationMode').classList.add('hidden');
  document.getElementById('startPresentationBtn').textContent = '▶️ Start';
  document.getElementById('startPresentationBtn').onclick = startPresentation;
  document.removeEventListener('keydown', handleKeyNavigation);
}

function showSlide(index) {
  const items = universeData?.items || [];
  if (items.length === 0) return;

  if (index < 0) index = items.length - 1;
  if (index >= items.length) index = 0;
  currentSlideIndex = index;

  const item = items[index];
  if (!item?.image) return;
  
  const imagePath = CONFIG.getAssetPath(currentUniverse, item.image);
  const title = item.title_translations?.[currentLang] || item.title;

  document.getElementById('presentationSlide').innerHTML = `
    <img src="${imagePath}" alt="${item.title}" class="max-h-full max-w-full object-contain cursor-pointer" onclick="playVideo(${index})">
    <div class="absolute bottom-20 left-1/2 -translate-x-1/2 text-4xl font-bold text-white drop-shadow-lg bg-black/30 px-6 py-2 rounded-full">${title}</div>
  `;
  document.getElementById('slideCounter').textContent = `${index + 1} / ${items.length}`;
}

function nextSlide() { showSlide(currentSlideIndex + 1); }
function previousSlide() { showSlide(currentSlideIndex - 1); }

function goToSlide(index) {
  if (!presentationActive) startPresentation();
  showSlide(index);
}

function handleKeyNavigation(e) {
  if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); nextSlide(); }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); previousSlide(); }
  else if (e.key === 'Escape') { stopPresentation(); }
}

function playVideo(index) {
  const item = universeData?.items?.[index];
  if (!item?.video) return;
  const videoPath = CONFIG.getAssetPath(currentUniverse, CONFIG.normalizeVideoExtension(item.video));
  const videoPlayer = document.getElementById('videoPlayer');
  videoPlayer.src = videoPath;
  document.getElementById('videoModal').classList.remove('hidden');
  videoPlayer.play().catch(e => console.warn('Video play failed:', e));
}

function closeVideoModal() {
  const videoPlayer = document.getElementById('videoPlayer');
  if (videoPlayer) {
    videoPlayer.pause();
    videoPlayer.src = '';
  }
  document.getElementById('videoModal').classList.add('hidden');
}

function changeLanguage(lang) {
  currentLang = lang;
  populateContactSheet();
  if (presentationActive) showSlide(currentSlideIndex);
  startMusic();
}

function startMusic() {
  const audio = document.getElementById('bgMusic');
  if (!audio || !currentUniverse) return;
  audio.src = CONFIG.getAssetPath(currentUniverse, `music_${currentLang}.mp3`);
  audio.volume = isMuted ? 0 : 0.5;
  audio.play().catch(() => {});
}

function toggleMute() {
  isMuted = !isMuted;
  const audio = document.getElementById('bgMusic');
  if (audio) audio.volume = isMuted ? 0 : 0.5;
  document.getElementById('muteBtn').textContent = isMuted ? '🔇' : '🔊';
}

// ========== INIT ==========
window.addEventListener('load', loadGallery);