// Slideshow Page JavaScript for Magik Univers

let currentUniverse = null;
let universeData = null;
let currentLang = 'fr';
let isMuted = false;
let presentationActive = false;
let currentSlideIndex = 0;

async function init() {
  const params = new URLSearchParams(window.location.search);
  const universeFolder = params.get('universe');

  if (!universeFolder) {
    alert('No universe specified');
    goBack();
    return;
  }

  currentUniverse = universeFolder;
  await loadUniverse();
}

async function loadUniverse() {
  try {
    const [dataRes, universesRes] = await Promise.all([
      fetch(`${API_BASE}/universes/${currentUniverse}/data`),
      fetch(`${API_BASE}/universes`)
    ]);

    const data = await dataRes.json();
    const universes = await universesRes.json();
    const universeInfo = universes.find(u => u.folder === currentUniverse);

    universeData = data;
    document.getElementById('universeTitle').textContent = universeInfo?.name || currentUniverse;

    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('contactSheet').classList.remove('hidden');

    populateContactSheet();
    startMusic();

  } catch (e) {
    console.error('Error loading universe:', e);
    alert('Failed to load universe');
    goBack();
  }
}

function populateContactSheet() {
  const grid = document.getElementById('imagesGrid');
  const items = universeData.items || [];
  const translations = universeData.translations || {};

  grid.innerHTML = items.map((item, i) => {
    if (!item || !item.image) return ''; // Skip invalid items
    const imagePath = CONFIG.getAssetPath(currentUniverse, item.image);
    const narration = translations[currentLang]?.[i] || item.title;

    return `
      <div class="asset-card" onclick="goToSlide(${i})">
        <img src="${imagePath}" alt="${item.title}">
        <div class="asset-title">${narration}</div>
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
  document.getElementById('startPresentationBtn').textContent = '▶️ Start Presentation';
  document.getElementById('startPresentationBtn').onclick = startPresentation;
  document.removeEventListener('keydown', handleKeyNavigation);
}

function showSlide(index) {
  const items = universeData.items || [];
  const translations = universeData.translations || {};

  if (index < 0) index = items.length - 1;
  if (index >= items.length) index = 0;

  currentSlideIndex = index;

  const item = items[index];
  if (!item || !item.image) {
    console.warn('Invalid item at index', index);
    return;
  }
  const imagePath = CONFIG.getAssetPath(currentUniverse, item.image);
  const narration = translations[currentLang]?.[index] || item.title;

  document.getElementById('presentationSlide').innerHTML = `
    <img src="${imagePath}"
         alt="${item.title}"
         onclick="playVideo(${index})">
    <div class="presentation-title">${narration}</div>
  `;

  document.getElementById('slideCounter').textContent = `${index + 1} / ${items.length}`;
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

function playVideo(index) {
  const items = universeData.items || [];
  const item = items[index];
  if (!item || !item.video) {
    console.error('Video not available for index', index);
    return;
  }
  const videoPath = CONFIG.getAssetPath(currentUniverse, CONFIG.normalizeVideoExtension(item.video));
  const videoPlayer = document.getElementById('videoPlayer');
  videoPlayer.src = videoPath;
  videoPlayer.load();
  document.getElementById('videoModal').classList.remove('hidden');
  setTimeout(() => {
    videoPlayer.play().catch(e => console.error('Video play failed:', e));
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
  populateContactSheet();
  if (presentationActive) {
    showSlide(currentSlideIndex);
  }
  startMusic();
}

function startMusic() {
  const musicPath = CONFIG.getAssetPath(currentUniverse, `music_${currentLang}.mp3`);
  const audio = document.getElementById('bgMusic');
  audio.src = musicPath;
  audio.volume = isMuted ? 0 : 0.5;
  audio.play().catch(err => {
    console.warn('Audio autoplay blocked:', err);
    // Optionally show toast to user
    // Note: showToast may not be available in slideshow.js without common.js
  });
}

function toggleMute() {
  isMuted = !isMuted;
  const audio = document.getElementById('bgMusic');
  audio.volume = isMuted ? 0 : 0.5;
  document.getElementById('muteBtn').textContent = isMuted ? '🔇' : '🔊';
}

function goBack() {
  window.location.href = 'gallery.html';
}

window.addEventListener('load', init);