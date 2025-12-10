// Gallery Page JavaScript for Magik Univers

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
        <div class="universe-card" onclick="openUniverse('${u.folder}')">
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

function openUniverse(folder) {
  // Redirect to slideshow page with universe parameter
  window.location.href = `slideshow.html?universe=${folder}`;
}

// Load gallery on page load
window.addEventListener('load', loadGallery);