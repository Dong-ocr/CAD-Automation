import {
  initScene, FURNITURE_DATA, addToScene, removeFromScene,
  selectObject, deselectObject, getClickedFurniture,
  changeMaterialColor, setView, setupDrag
} from './scene.js';

let selected = null;

// Init
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('canvas-container');
  initScene(container);

  buildCatalog('all');
  setupCategoryTabs();
  setupViewButtons();
  setupTransformControls();
  setupMaterialSwatches();
  setupColorDots();
  setupZoom();

  // Drag-to-move + click-to-select
  setupDrag(container,
    (obj) => { selected = obj; updatePropertiesPanel(obj.userData); },
    () => { selected = null; showEmptyProperties(); }
  );

  // Hide loader
  setTimeout(() => document.getElementById('loader').classList.add('hidden'), 800);
});

// Catalog
function buildCatalog(cat) {
  const list = document.getElementById('catalog-list');
  list.innerHTML = '';
  const items = cat === 'all' ? FURNITURE_DATA : FURNITURE_DATA.filter(f => f.cat === cat);
  items.forEach((item, i) => {
    const el = document.createElement('div');
    el.className = 'catalog-item';
    el.style.animationDelay = `${i * 0.05}s`;
    el.innerHTML = `
      <div class="item-thumb"><span class="thumb-icon">${getCatIcon(item.cat)}</span></div>
      <div class="item-info">
        <div class="item-name">${item.name}</div>
        <div class="item-dims">${(item.w*100).toFixed(0)} × ${(item.d*100).toFixed(0)} × ${(item.h*100).toFixed(0)} cm</div>
      </div>
      <div class="item-price">${item.price}</div>`;
    el.addEventListener('click', () => {
      const mesh = addToScene(item.id);
      if (mesh) {
        selectObject(mesh);
        selected = mesh;
        updatePropertiesPanel(mesh.userData);
        showOverlay(`Added ${item.name} to scene`);
      }
    });
    list.appendChild(el);
  });
}

function getCatIcon(cat) {
  const icons = { sofas:'🛋️', tables:'🪑', chairs:'💺', lighting:'💡', decor:'🌿' };
  return icons[cat] || '📦';
}

function setupCategoryTabs() {
  document.querySelectorAll('.cat-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      buildCatalog(tab.dataset.cat);
    });
  });
}

// View buttons
function setupViewButtons() {
  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      setView(btn.dataset.view);
    });
  });
}

// Viewport selection is now handled by setupDrag in scene.js

// Properties Panel
function updatePropertiesPanel(data) {
  document.getElementById('prop-empty').style.display = 'none';
  document.getElementById('prop-content').style.display = 'block';
  document.getElementById('prop-name').textContent = data.name;
  document.getElementById('prop-cat').textContent = data.cat;
  document.getElementById('dim-w').textContent = (data.w * 100).toFixed(0);
  document.getElementById('dim-d').textContent = (data.d * 100).toFixed(0);
  document.getElementById('dim-h').textContent = (data.h * 100).toFixed(0);
  document.getElementById('sel-item-info').textContent = `${data.name} selected`;

  // Reset sliders
  document.getElementById('rot-slider').value = 0;
  document.getElementById('rot-val').textContent = '0°';
  document.getElementById('scale-slider').value = 100;
  document.getElementById('scale-val').textContent = '100%';
}

function showEmptyProperties() {
  document.getElementById('prop-empty').style.display = 'flex';
  document.getElementById('prop-content').style.display = 'none';
  document.getElementById('sel-item-info').textContent = 'No selection';
}

// Transform controls
function setupTransformControls() {
  // Rotation slider
  document.getElementById('rot-slider').addEventListener('input', (e) => {
    if (!selected) return;
    const deg = parseFloat(e.target.value);
    selected.rotation.y = deg * Math.PI / 180;
    document.getElementById('rot-val').textContent = `${deg}°`;
  });

  // Scale slider
  document.getElementById('scale-slider').addEventListener('input', (e) => {
    if (!selected) return;
    const s = parseFloat(e.target.value) / 100;
    selected.scale.set(s, s, s);
    document.getElementById('scale-val').textContent = `${e.target.value}%`;
  });

  // Delete button
  document.getElementById('btn-delete').addEventListener('click', () => {
    if (selected) {
      const name = selected.userData.name;
      removeFromScene(selected);
      selected = null;
      showEmptyProperties();
      showOverlay(`Removed ${name}`);
    }
  });

  // Mode buttons
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}

// Material swatches
function setupMaterialSwatches() {
  document.querySelectorAll('.material-swatch').forEach(sw => {
    sw.addEventListener('click', () => {
      document.querySelectorAll('.material-swatch').forEach(s => s.classList.remove('active'));
      sw.classList.add('active');
      if (selected) {
        changeMaterialColor(selected, sw.dataset.color);
        showOverlay(`Applied ${sw.dataset.name} material`);
      }
    });
  });
}

// Color dots
function setupColorDots() {
  document.querySelectorAll('.color-dot').forEach(dot => {
    dot.addEventListener('click', () => {
      document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
      if (selected) changeMaterialColor(selected, dot.dataset.color);
    });
  });
}

// Zoom controls
function setupZoom() {
  document.getElementById('zoom-in').addEventListener('click', () => {
    const cam = document.querySelector('#canvas-container canvas')?.__three_camera;
  });
  document.getElementById('zoom-out').addEventListener('click', () => {});
}

// Overlay notification
function showOverlay(msg) {
  const el = document.getElementById('viewport-overlay');
  el.textContent = msg;
  el.classList.add('visible');
  setTimeout(() => el.classList.remove('visible'), 1800);
}
