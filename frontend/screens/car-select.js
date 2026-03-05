/**
 * Car Select (Onboarding) Screen
 * Welcome + language selector + car model selector (Make → Model → Generation) + start.
 * Loads vehicles-select.json (compact index: 172 brands, 3528 models, 7852 generations)
 * and vehicles_i18n_{lang}.json for localized brand names.
 */

import { emit } from '../event-bus.js';
import { i18n } from '../app.js';

let _container = null;
let _rendered = false;

const LANGUAGES = [
  { code: 'RU', label: '\u0420\u0443\u0441', flag: '\uD83C\uDDF7\uD83C\uDDFA' },
  { code: 'EN', label: 'Eng', flag: '\uD83C\uDDEC\uD83C\uDDE7' },
  { code: 'ZH', label: '\u4E2D\u6587', flag: '\uD83C\uDDE8\uD83C\uDDF3' },
  { code: 'AR', label: '\u0639\u0631\u0628\u064A', flag: '\uD83C\uDDF8\uD83C\uDDE6' },
  { code: 'ES', label: 'Esp', flag: '\uD83C\uDDEA\uD83C\uDDF8' },
];

let selectedLang = 'RU';
let diagEnabled = true;

/** @type {Array|null} Full vehicles index */
let vehiclesData = null;
/** @type {Object|null} Brand name translations for current lang */
let vehiclesI18n = null;

/** Selected state */
let selectedBrandId = null;
let selectedModelId = null;
let selectedGenId = null;

// ─── Data Loading ────────────────────────────────────────

async function loadVehicles() {
  if (vehiclesData) return;
  try {
    const resp = await fetch('data/vehicles-select.json');
    vehiclesData = await resp.json();
  } catch (e) {
    console.warn('[LLCAR] Failed to load vehicles index:', e);
    vehiclesData = [];
  }
}

async function loadVehiclesI18n(lang) {
  try {
    const resp = await fetch(`data/vehicles_i18n_${lang}.json`);
    vehiclesI18n = await resp.json();
  } catch (e) {
    console.warn('[LLCAR] Failed to load vehicles i18n:', e);
    vehiclesI18n = null;
  }
}

/** Get localized brand name */
function getBrandName(brand) {
  if (vehiclesI18n && vehiclesI18n.brands && vehiclesI18n.brands[brand.id]) {
    return vehiclesI18n.brands[brand.id];
  }
  return brand.name;
}

// ─── Render ─────────────────────────────────────────────

export async function render(container) {
  _container = container;
  if (_rendered) return;
  _rendered = true;

  // Load data in parallel
  const langCode = (i18n.lang || 'ru').toLowerCase();
  await Promise.all([loadVehicles(), loadVehiclesI18n(langCode)]);

  // Restore language
  const stored = localStorage.getItem('llcar-lang');
  if (stored) selectedLang = stored.toUpperCase();

  container.innerHTML = `
    <div class="screen__scrollable" style="display:flex;flex-direction:column;flex:1;">
      <!-- Welcome area -->
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:50px;flex:1;padding:0 20px;">
        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;width:350px;">
          <div style="display:flex;align-items:center;justify-content:center;gap:14px;width:100%;">
            <span style="font-size:15px;color:#F0F6FC;" data-i18n="onboarding.welcome_ru">\u0414\u043E\u0431\u0440\u043E \u043F\u043E\u0436\u0430\u043B\u043E\u0432\u0430\u0442\u044C!</span>
            <span style="font-size:15px;color:var(--text-secondary);">Welcome!</span>
            <span style="font-size:15px;color:var(--text-tertiary);">\u6B22\u8FCE\uFF01</span>
          </div>
          <div style="display:flex;align-items:center;justify-content:center;gap:14px;width:100%;">
            <span style="font-size:15px;color:var(--text-tertiary);">\u0623\u0647\u0644\u0627\u064B \u0648\u0633\u0647\u0644\u0627\u064B!</span>
            <span style="font-size:15px;color:var(--text-secondary);">\u00A1Bienvenido!</span>
          </div>
        </div>
        <p style="font-size:17px;color:#F0F6FC;font-style:italic;text-align:center;letter-spacing:0.3px;" data-i18n="onboarding.tagline">\u0417\u0434\u043E\u0440\u043E\u0432\u044C\u0435 \u0412\u0430\u0448\u0435\u0433\u043E \u0430\u0432\u0442\u043E &mdash; \u0432 \u0412\u0430\u0448\u0438\u0445 \u0440\u0443\u043A\u0430\u0445!</p>
      </div>

      <!-- Language selector -->
      <div style="display:flex;flex-direction:column;gap:10px;padding:0 20px;">
        <span style="font-size:13px;font-weight:600;color:var(--text-secondary);" data-i18n="onboarding.lang_label">\u042F\u0437\u044B\u043A / Language</span>
        <div class="lang-selector" id="lang-selector"></div>
      </div>

      <!-- Car selector -->
      <div style="display:flex;flex-direction:column;gap:10px;padding:20px 20px 0;">
        <h2 style="font-size:17px;font-weight:700;color:var(--text-primary);" data-i18n="onboarding.your_car">\u0412\u0430\u0448 \u0430\u0432\u0442\u043E\u043C\u043E\u0431\u0438\u043B\u044C</h2>
        <p style="font-size:11px;color:var(--text-secondary);line-height:1.4;" data-i18n="onboarding.car_hint">\u0412\u044B\u0431\u0435\u0440\u0438\u0442\u0435 \u0430\u0432\u0442\u043E \u0434\u043B\u044F \u043F\u0435\u0440\u0441\u043E\u043D\u0430\u043B\u0438\u0437\u0430\u0446\u0438\u0438 \u0434\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0438 \u0438 \u0431\u0430\u0437\u044B \u0437\u043D\u0430\u043D\u0438\u0439</p>

        <!-- Make dropdown -->
        <div class="car-select-row" id="row-make" style="cursor:pointer;">
          <div class="car-select-row__left">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>
            <span class="car-select-row__value" id="label-make">\u2014</span>
          </div>
          <span class="car-select-row__hint" data-i18n="onboarding.make">\u041C\u0430\u0440\u043A\u0430</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
        </div>

        <!-- Model dropdown -->
        <div class="car-select-row" id="row-model" style="cursor:pointer;opacity:0.4;pointer-events:none;">
          <div class="car-select-row__left">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><path d="M7 7h.01"/></svg>
            <span class="car-select-row__value" id="label-model">\u2014</span>
          </div>
          <span class="car-select-row__hint" data-i18n="onboarding.model">\u041C\u043E\u0434\u0435\u043B\u044C</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
        </div>

        <!-- Generation dropdown -->
        <div class="car-select-row" id="row-gen" style="cursor:pointer;opacity:0.4;pointer-events:none;">
          <div class="car-select-row__left">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
            <span class="car-select-row__value" id="label-gen">\u2014</span>
          </div>
          <span class="car-select-row__hint" data-i18n="onboarding.generation">\u041F\u043E\u043A\u043E\u043B\u0435\u043D\u0438\u0435</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
        </div>
      </div>

      <!-- Dropdown overlay (shared) -->
      <div id="car-dropdown" class="car-dropdown" style="display:none;">
        <div class="car-dropdown__search-wrap">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input class="car-dropdown__search" id="car-dropdown-search" type="text" placeholder="" autocomplete="off"/>
        </div>
        <div class="car-dropdown__list" id="car-dropdown-list"></div>
      </div>

      <!-- OBD-II Toggle -->
      <div style="display:flex;align-items:center;gap:12px;padding:4px 20px;">
        <div class="toggle toggle--active" id="diag-toggle">
          <div class="toggle__thumb"></div>
        </div>
        <div style="display:flex;flex-direction:column;gap:2px;flex:1;">
          <span style="font-size:13px;font-weight:600;color:var(--text-primary);" data-i18n="onboarding.obd_title">\u041F\u043E\u0434\u043A\u043B\u044E\u0447\u0438\u0442\u044C OBD-II \u0434\u0438\u0430\u0433\u043D\u043E\u0441\u0442\u0438\u043A\u0443</span>
          <span style="font-size:9px;color:var(--text-tertiary);line-height:1.2;" data-i18n="onboarding.obd_hint">\u041D\u0435\u043E\u0431\u044F\u0437\u0430\u0442\u0435\u043B\u044C\u043D\u043E &mdash; \u043C\u043E\u0436\u043D\u043E \u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u044C\u0441\u044F \u0431\u0430\u0437\u043E\u0439 \u0437\u043D\u0430\u043D\u0438\u0439 \u0431\u0435\u0437 \u0430\u0434\u0430\u043F\u0442\u0435\u0440\u0430</span>
        </div>
      </div>

      <!-- Start button -->
      <div style="display:flex;flex-direction:column;align-items:center;gap:12px;padding:4px 20px 18px;">
        <button class="btn btn--primary" id="btn-start" disabled>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>
          <span data-i18n="onboarding.start">\u041D\u0430\u0447\u0430\u0442\u044C</span>
        </button>
        <span style="font-size:10px;color:var(--text-tertiary);text-align:center;" data-i18n="onboarding.terms">\u041F\u0440\u043E\u0434\u043E\u043B\u0436\u0430\u044F, \u0432\u044B \u043F\u0440\u0438\u043D\u0438\u043C\u0430\u0435\u0442\u0435 \u0443\u0441\u043B\u043E\u0432\u0438\u044F \u0438\u0441\u043F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u043D\u0438\u044F</span>
        <div style="width:134px;height:5px;border-radius:9999px;background:var(--text-tertiary);"></div>
      </div>
    </div>
  `;

  injectStyles();
  renderLangButtons();
  bindEvents();
}

// ─── Styles ─────────────────────────────────────────────

function injectStyles() {
  if (document.getElementById('car-select-styles')) return;
  const style = document.createElement('style');
  style.id = 'car-select-styles';
  style.textContent = `
    .car-dropdown {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      max-height: 55vh;
      background: var(--bg-card);
      border-top: 1px solid var(--border-default);
      border-radius: var(--radius-lg) var(--radius-lg) 0 0;
      z-index: 100;
      display: flex;
      flex-direction: column;
      box-shadow: 0 -4px 24px rgba(0,0,0,0.4);
      animation: slideUp 0.2s ease-out;
    }
    @keyframes slideUp {
      from { transform: translateY(100%); }
      to   { transform: translateY(0); }
    }
    .car-dropdown__search-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px 8px;
      border-bottom: 1px solid var(--border-default);
    }
    .car-dropdown__search {
      flex: 1;
      background: none;
      border: none;
      color: var(--text-primary);
      font-size: 14px;
      outline: none;
    }
    .car-dropdown__search::placeholder {
      color: var(--text-tertiary);
    }
    .car-dropdown__list {
      flex: 1;
      overflow-y: auto;
      padding: 4px 0;
    }
    .car-dropdown__item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 16px;
      font-size: 14px;
      color: var(--text-primary);
      cursor: pointer;
      transition: background 0.15s;
    }
    .car-dropdown__item:hover,
    .car-dropdown__item:active {
      background: var(--bg-surface);
    }
    .car-dropdown__item--selected {
      color: var(--accent-primary);
      font-weight: 600;
    }
    .car-dropdown__item-sub {
      font-size: 11px;
      color: var(--text-tertiary);
    }
    .car-dropdown__backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.3);
      z-index: 99;
    }
  `;
  document.head.appendChild(style);
}

// ─── Language Buttons ───────────────────────────────────

function renderLangButtons() {
  const selector = _container.querySelector('#lang-selector');
  if (!selector) return;

  selector.innerHTML = LANGUAGES.map(lang => `
    <button class="lang-btn ${lang.code === selectedLang ? 'lang-btn--active' : ''}" data-lang="${lang.code}">
      <div class="lang-btn__flag">${lang.flag}</div>
      <span class="lang-btn__code">${lang.code}</span>
      <span class="lang-btn__label">${lang.label}</span>
    </button>
  `).join('');

  selector.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      selectedLang = btn.dataset.lang;
      renderLangButtons();
      const lc = selectedLang.toLowerCase();
      await i18n.switchLanguage(lc);
      // Reload brand translations
      await loadVehiclesI18n(lc);
      // Refresh displayed brand name if one is selected
      if (selectedBrandId) {
        const brand = vehiclesData.find(b => b.id === selectedBrandId);
        if (brand) {
          const labelMake = _container.querySelector('#label-make');
          if (labelMake) labelMake.textContent = getBrandName(brand);
        }
      }
    });
  });
}

// ─── Dropdown Logic ─────────────────────────────────────

let activeDropdown = null; // 'make' | 'model' | 'gen'
let backdropEl = null;

function openDropdown(type) {
  activeDropdown = type;
  const dropdown = _container.querySelector('#car-dropdown');
  const listEl = _container.querySelector('#car-dropdown-list');
  const searchEl = _container.querySelector('#car-dropdown-search');
  if (!dropdown || !listEl || !searchEl) return;

  searchEl.value = '';
  dropdown.style.display = '';

  // Create backdrop
  if (!backdropEl) {
    backdropEl = document.createElement('div');
    backdropEl.className = 'car-dropdown__backdrop';
    backdropEl.addEventListener('click', closeDropdown);
  }
  _container.appendChild(backdropEl);

  // Set search placeholder
  const placeholders = {
    make: i18n.get('common.search', '\u041F\u043E\u0438\u0441\u043A') + '...',
    model: i18n.get('common.search', '\u041F\u043E\u0438\u0441\u043A') + '...',
    gen: i18n.get('common.search', '\u041F\u043E\u0438\u0441\u043A') + '...',
  };
  searchEl.placeholder = placeholders[type] || '';
  searchEl.focus();

  renderDropdownItems('');

  searchEl.oninput = () => renderDropdownItems(searchEl.value.trim().toLowerCase());
}

function closeDropdown() {
  activeDropdown = null;
  const dropdown = _container.querySelector('#car-dropdown');
  if (dropdown) dropdown.style.display = 'none';
  if (backdropEl && backdropEl.parentNode) {
    backdropEl.parentNode.removeChild(backdropEl);
  }
}

function renderDropdownItems(query) {
  const listEl = _container.querySelector('#car-dropdown-list');
  if (!listEl) return;

  let items = [];

  if (activeDropdown === 'make') {
    items = (vehiclesData || []).map(b => ({
      id: b.id,
      label: getBrandName(b),
      sub: b.country || '',
      selected: b.id === selectedBrandId,
    }));
  } else if (activeDropdown === 'model') {
    const brand = vehiclesData.find(b => b.id === selectedBrandId);
    if (brand) {
      items = brand.models.map(m => ({
        id: m.id,
        label: m.name,
        sub: m.segment || '',
        selected: m.id === selectedModelId,
      }));
    }
  } else if (activeDropdown === 'gen') {
    const brand = vehiclesData.find(b => b.id === selectedBrandId);
    const model = brand ? brand.models.find(m => m.id === selectedModelId) : null;
    if (model) {
      items = model.generations.map(g => {
        const years = g.ys ? (g.ys + ' \u2013 ' + (g.ye || '\u043D.\u0432.')) : '';
        return {
          id: g.id,
          label: g.name,
          sub: [g.body, years].filter(Boolean).join(' \u2022 '),
          selected: g.id === selectedGenId,
        };
      });
    }
  }

  // Filter by query
  if (query) {
    items = items.filter(it => it.label.toLowerCase().includes(query));
  }

  listEl.innerHTML = items.map(it => `
    <div class="car-dropdown__item ${it.selected ? 'car-dropdown__item--selected' : ''}" data-id="${it.id}">
      <span>${it.label}</span>
      ${it.sub ? `<span class="car-dropdown__item-sub">${it.sub}</span>` : ''}
    </div>
  `).join('');

  listEl.querySelectorAll('.car-dropdown__item').forEach(el => {
    el.addEventListener('click', () => onDropdownSelect(el.dataset.id));
  });
}

function onDropdownSelect(id) {
  if (activeDropdown === 'make') {
    selectedBrandId = id;
    selectedModelId = null;
    selectedGenId = null;
    const brand = vehiclesData.find(b => b.id === id);
    _container.querySelector('#label-make').textContent = brand ? getBrandName(brand) : id;
    _container.querySelector('#label-model').textContent = '\u2014';
    _container.querySelector('#label-gen').textContent = '\u2014';
    // Enable model row, disable gen
    setRowEnabled('row-model', true);
    setRowEnabled('row-gen', false);
    updateStartButton();
  } else if (activeDropdown === 'model') {
    selectedModelId = id;
    selectedGenId = null;
    const brand = vehiclesData.find(b => b.id === selectedBrandId);
    const model = brand ? brand.models.find(m => m.id === id) : null;
    _container.querySelector('#label-model').textContent = model ? model.name : id;
    _container.querySelector('#label-gen').textContent = '\u2014';
    setRowEnabled('row-gen', true);
    // Auto-select if only 1 generation
    if (model && model.generations.length === 1) {
      selectedGenId = model.generations[0].id;
      const g = model.generations[0];
      const years = g.ys ? (g.ys + ' \u2013 ' + (g.ye || '\u043D.\u0432.')) : '';
      _container.querySelector('#label-gen').textContent = years || g.name;
    }
    updateStartButton();
  } else if (activeDropdown === 'gen') {
    selectedGenId = id;
    const brand = vehiclesData.find(b => b.id === selectedBrandId);
    const model = brand ? brand.models.find(m => m.id === selectedModelId) : null;
    const gen = model ? model.generations.find(g => g.id === id) : null;
    if (gen) {
      const years = gen.ys ? (gen.ys + ' \u2013 ' + (gen.ye || '\u043D.\u0432.')) : gen.name;
      _container.querySelector('#label-gen').textContent = years;
    }
    updateStartButton();
  }
  closeDropdown();
}

function setRowEnabled(rowId, enabled) {
  const row = _container.querySelector('#' + rowId);
  if (!row) return;
  row.style.opacity = enabled ? '1' : '0.4';
  row.style.pointerEvents = enabled ? 'auto' : 'none';
}

function updateStartButton() {
  const btn = _container.querySelector('#btn-start');
  if (!btn) return;
  // Enable start when at least brand + model are selected
  const ready = selectedBrandId && selectedModelId;
  btn.disabled = !ready;
  btn.style.opacity = ready ? '1' : '0.5';
}

// ─── Events ─────────────────────────────────────────────

function bindEvents() {
  _container.querySelector('#row-make')?.addEventListener('click', () => openDropdown('make'));
  _container.querySelector('#row-model')?.addEventListener('click', () => openDropdown('model'));
  _container.querySelector('#row-gen')?.addEventListener('click', () => openDropdown('gen'));

  // Toggle OBD
  const toggle = _container.querySelector('#diag-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      diagEnabled = !diagEnabled;
      toggle.classList.toggle('toggle--active', diagEnabled);
    });
  }

  // Start
  const startBtn = _container.querySelector('#btn-start');
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      if (!selectedBrandId || !selectedModelId) return;

      // Determine model key for localStorage (li7, li9, or generic brand_model)
      let modelKey = selectedBrandId + '_' + selectedModelId;
      // Special handling for Li L7/L9 (which have 3D models)
      if (selectedBrandId === 'li') {
        if (selectedModelId === 'li_l7') modelKey = 'li7';
        else if (selectedModelId === 'li_l9') modelKey = 'li9';
      }

      localStorage.setItem('llcar-model', modelKey);
      localStorage.setItem('llcar-brand', selectedBrandId);
      localStorage.setItem('llcar-model-id', selectedModelId);
      localStorage.setItem('llcar-gen-id', selectedGenId || '');

      // Save display names for dashboard
      const brandObj = vehiclesData?.find(b => b.id === selectedBrandId);
      const modelObj = brandObj?.models?.find(m => m.id === selectedModelId);
      localStorage.setItem('llcar-brand-name', brandObj ? getBrandName(brandObj) : selectedBrandId);
      localStorage.setItem('llcar-model-name', modelObj ? modelObj.name : selectedModelId);

      emit('app:start', {
        lang: selectedLang,
        model: modelKey,
        brand: selectedBrandId,
        modelId: selectedModelId,
        genId: selectedGenId,
        diagEnabled,
      });
    });
  }
}

// ─── Cleanup ────────────────────────────────────────────

export function cleanup() {
  _rendered = false;
  closeDropdown();
  if (_container) {
    _container.innerHTML = '';
  }
}
