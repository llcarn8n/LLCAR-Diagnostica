/**
 * Knowledge Base Screen (API-powered)
 *
 * Все поисковые запросы через KB API (ChromaDB + sentence-transformers).
 * Семантический поиск на RU/EN/ZH.
 * Бейджи источников, DTC коды, ссылки на manuals.lixiang.com.
 */

import { emit, on, off } from '../event-bus.js';
import { KnowledgeBase } from '../knowledge-base.js';

let _container = null;
let _rendered = false;
let _kb = null;
let _i18n = null;

let activeCategory = 'all';
let activeVehicle = null;
let searchQuery = '';
let selectedComponentTags = [];
let selectedComponentData = null;

const LAYER_COLORS = {
  body: '#4FC3F7',
  engine: '#FF7043',
  drivetrain: '#AB47BC',
  ev: '#66BB6A',
  brakes: '#EF5350',
  sensors: '#FFA726',
  hvac: '#26C6DA',
  interior: '#8D6E63',
  general: '#8B949E',
};

const CATEGORIES = ['all', 'systems', 'manuals', 'dtc'];

// Иконки источников
const SOURCE_BADGES = {
  pdf_l9_ru: { icon: '\u{1F4D6}', label: 'L9 RU' },
  pdf_l7_ru: { icon: '\u{1F4D6}', label: 'L7 RU' },
  pdf_l9_zh: { icon: '\u{1F4D6}', label: 'L9 ZH' },
  pdf_l7_zh: { icon: '\u{1F4D6}', label: 'L7 ZH' },
  parts_zh: { icon: '\u{1F527}', label: 'Parts' },
  web: { icon: '\u{1F310}', label: 'Web' },
  dtc_db: { icon: '\u{26A0}', label: 'DTC' },
};

// Флаги языков
const LANG_FLAGS = { ru: 'RU', en: 'EN', zh: 'ZH' };

function t(key, fallback) {
  if (_i18n) return _i18n.get(key, fallback);
  return fallback || key;
}

/**
 * Рендер экрана базы знаний.
 */
export function render(container) {
  _container = container;

  if (window.__llcar_selectedComponent) {
    selectedComponentTags = [window.__llcar_selectedComponent];
    selectedComponentData = window.__llcar_selectedComponentData || null;
    window.__llcar_selectedComponent = null;
    window.__llcar_selectedComponentData = null;
    if (_rendered && _kb?._loaded) {
      updateTagFilter();
      renderResults();
      return;
    }
  }

  if (_rendered) return;
  _rendered = true;

  _i18n = window.__llcar_i18n || null;

  if (!_kb) {
    _kb = new KnowledgeBase();
    _kb.init().then(() => {
      renderContent();
    });
  } else {
    renderContent();
  }

  on('component:select', _onComponentSelect);
  on('lang:change', _onLangChange);
}

function renderContent() {
  if (!_container) return;

  const totalArticles = _kb ? _kb.getTotalCount() : 0;
  const isOnline = _kb?.isOnline;

  _container.innerHTML = `
    <div class="kb-screen" style="display:flex;flex-direction:column;gap:2px;flex:1;overflow:hidden;">
      <!-- Заголовок -->
      <div style="display:flex;align-items:center;justify-content:space-between;height:48px;padding:0 20px;">
        <div style="display:flex;align-items:center;gap:12px;">
          <button id="kb-back" style="background:none;border:none;cursor:pointer;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          </button>
          <span style="font-size:17px;font-weight:600;color:var(--text-primary);" data-i18n="knowledge.title">${t('knowledge.title', 'Knowledge Base')}</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span id="kb-api-status" style="width:8px;height:8px;border-radius:50%;background:${isOnline ? 'var(--status-ok, #66BB6A)' : 'var(--status-error, #EF5350)'};"></span>
          <span style="font-size:10px;color:var(--text-tertiary);">${isOnline ? 'API' : 'Offline'}</span>
        </div>
      </div>

      <!-- Поиск -->
      <div style="padding:0 20px;">
        <div class="search-bar" style="position:relative;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input type="text" id="kb-search-input"
            placeholder="${t('knowledge.search', 'Search documentation...')}"
            data-i18n-placeholder="knowledge.search"
            style="flex:1;font-size:14px;color:var(--text-primary);background:none;border:none;outline:none;"
            value="${searchQuery}" />
          ${searchQuery ? '<button id="kb-search-clear" style="background:none;border:none;cursor:pointer;padding:2px;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>' : ''}
        </div>
      </div>

      <!-- Фильтры: модель + счётчик -->
      <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 20px;">
        <div style="display:flex;gap:8px;">
          <button class="kb-vehicle-btn ${!activeVehicle ? 'kb-vehicle-btn--active' : ''}" data-vehicle="all" style="font-size:12px;font-weight:600;padding:4px 10px;border-radius:var(--radius-pill);border:1px solid var(--border-default);">
            ${t('knowledge.all', 'All')}
          </button>
          <button class="kb-vehicle-btn ${activeVehicle === 'l7' ? 'kb-vehicle-btn--active' : ''}" data-vehicle="l7" style="font-size:12px;font-weight:600;padding:4px 10px;border-radius:var(--radius-pill);border:1px solid var(--border-default);">
            Li L7
          </button>
          <button class="kb-vehicle-btn ${activeVehicle === 'l9' ? 'kb-vehicle-btn--active' : ''}" data-vehicle="l9" style="font-size:12px;font-weight:600;padding:4px 10px;border-radius:var(--radius-pill);border:1px solid var(--border-default);">
            Li L9
          </button>
        </div>
        <span style="font-size:11px;color:var(--text-secondary);">${totalArticles} <span data-i18n="knowledge.articles">${t('knowledge.articles', 'articles')}</span></span>
      </div>

      <!-- Категории -->
      <div class="system-tabs" id="kb-categories"></div>

      <!-- Фильтр по тегу (из 3D twin) -->
      <div id="kb-tag-filter" style="display:none;padding:4px 20px;">
        <div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--accent-primary-dim);border:1px solid var(--border-accent);border-radius:var(--radius-md);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
          <span id="kb-tag-label" style="flex:1;font-size:12px;color:var(--accent-primary);font-weight:500;"></span>
          <button id="kb-tag-clear" style="background:none;border:none;cursor:pointer;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </div>

      ${!isOnline ? `
        <div style="margin:0 20px;padding:12px;background:var(--status-warning-dim, #FFF3E0);border:1px solid var(--status-warning, #FFA726);border-radius:var(--radius-md);">
          <p style="font-size:13px;color:var(--status-warning, #E65100);margin:0;line-height:1.4;">
            KB API сервер недоступен. Запустите:<br>
            <code style="font-size:12px;background:rgba(0,0,0,0.06);padding:2px 6px;border-radius:4px;">cd Diagnostica && uvicorn api.server:app --port 8000</code>
          </p>
        </div>
      ` : ''}

      <!-- Область прокрутки -->
      <div class="screen__scrollable" id="kb-results" style="display:flex;flex-direction:column;gap:12px;padding:3px 20px 8px;flex:1;">
      </div>
    </div>
  `;

  renderCategoryTabs();
  renderResults();
  bindEvents();
}

// ═══════════════════════════════════════════════════════════
// Рендер результатов
// ═══════════════════════════════════════════════════════════

async function renderResults() {
  const resultsEl = _container?.querySelector('#kb-results');
  if (!resultsEl || !_kb || !_kb._loaded) {
    if (resultsEl) {
      resultsEl.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;padding:40px 0;color:var(--text-tertiary);font-size:14px;" data-i18n="common.loading">${t('common.loading', 'Loading...')}</div>`;
    }
    return;
  }

  // Показываем индикатор загрузки
  resultsEl.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;padding:30px 0;color:var(--text-tertiary);font-size:13px;">
    <svg width="18" height="18" viewBox="0 0 24 24" style="animation:spin 1s linear infinite;margin-right:8px;" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
    ${t('common.searching', 'Поиск...')}
  </div>`;

  let entries = [];

  if (selectedComponentTags.length > 0) {
    // Поиск по компоненту из 3D
    const gid = selectedComponentTags[0];
    entries = await _kb.getComponentArticles(gid, activeVehicle);

    // Дополнительный поиск по DTC если есть
    if (entries.length < 5 && selectedComponentData?.dtcCodes?.length > 0) {
      for (const dtc of selectedComponentData.dtcCodes) {
        const dtcResult = await _kb.getDTC(dtc);
        for (const art of dtcResult.articles || []) {
          if (!entries.find(e => e.id === art.id)) entries.push(art);
        }
      }
    }
  } else if (searchQuery) {
    entries = await _kb.search(searchQuery, {
      vehicle: activeVehicle || undefined,
    }, 50);
  } else if (activeCategory === 'systems') {
    renderLayerView(resultsEl);
    return;
  } else if (activeCategory === 'dtc') {
    entries = await _kb.search('DTC diagnostic trouble code', {
      vehicle: activeVehicle || undefined,
      contentType: 'dtc',
    }, 50);
  } else {
    // По умолчанию — показать популярные запросы или все
    entries = await _kb.search('руководство пользователя обслуживание', {
      vehicle: activeVehicle || undefined,
    }, 30);
  }

  if (entries.length === 0) {
    if (selectedComponentTags.length > 0 && selectedComponentData) {
      const gid = selectedComponentTags[0];
      const compName = (_i18n ? _i18n.getComponentName(gid) : null) || gid.split('@')[0].replace(/_/g, ' ').replace(/ ann$/, '');
      const layer = selectedComponentData.layer || gid.split('@')[1] || '';
      const dtcCodes = selectedComponentData.dtcCodes || [];
      const layerLabel = _i18n ? _i18n.getLayerName(layer) : layer;
      const color = LAYER_COLORS[layer] || '#8B949E';

      resultsEl.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:16px;padding:20px 0;">
          <div style="display:flex;gap:12px;align-items:flex-start;">
            <div style="width:4px;min-height:40px;border-radius:2px;background:${color};flex-shrink:0;"></div>
            <div>
              <h3 style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0 0 4px 0;">${compName}</h3>
              <span style="font-size:12px;color:var(--text-secondary);">${t('knowledge.system', 'System')}: ${layerLabel}</span>
            </div>
          </div>
          ${dtcCodes.length > 0 ? `
            <div style="padding:12px;background:var(--surface-secondary);border-radius:var(--radius-md);border:1px solid var(--border-default);">
              <span style="font-size:12px;color:var(--text-secondary);font-weight:500;">DTC:</span>
              <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">
                ${dtcCodes.map(dtc => `<span class="kb-dtc-badge" data-dtc="${dtc}" style="cursor:pointer;font-size:12px;padding:2px 8px;border-radius:10px;background:${color}20;color:${color};border:1px solid ${color}40;">${dtc}</span>`).join('')}
              </div>
            </div>
          ` : ''}
          <div style="text-align:center;padding:20px 0;color:var(--text-tertiary);font-size:13px;">
            ${t('knowledge.no_articles_component', 'No articles found for this component')}
          </div>
        </div>
      `;
      // Клик по DTC бейджу → поиск
      resultsEl.querySelectorAll('.kb-dtc-badge').forEach(el => {
        el.addEventListener('click', async () => {
          searchQuery = el.dataset.dtc;
          const input = _container?.querySelector('#kb-search-input');
          if (input) input.value = searchQuery;
          selectedComponentTags = [];
          selectedComponentData = null;
          updateTagFilter();
          await renderResults();
        });
      });
    } else {
      resultsEl.innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 0;gap:12px;">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5" stroke-linecap="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          <span style="color:var(--text-tertiary);font-size:14px;" data-i18n="knowledge.no_results">${t('knowledge.no_results', 'Nothing found')}</span>
        </div>
      `;
    }
    return;
  }

  // Рендер карточек
  const html = entries.slice(0, 40).map(entry => renderArticleCard(entry)).join('');
  resultsEl.innerHTML = html;
  bindResultEvents(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Layer Overview
// ═══════════════════════════════════════════════════════════

function renderLayerView(resultsEl) {
  const stats = _kb.getLayerStats();
  let html = '';

  for (const stat of stats) {
    if (stat.id === 'general' || stat.id === 'unknown') continue;
    const color = LAYER_COLORS[stat.id] || '#8B949E';
    const layerLabel = t(`layers.${stat.id}`, stat.id);
    const subtitle = `${stat.count} ${t('knowledge.articles', 'articles')}`;

    html += renderSystemItem(layerLabel, subtitle, color, stat.id);
  }

  resultsEl.innerHTML = html;

  resultsEl.querySelectorAll('.kb-system-item').forEach(el => {
    el.addEventListener('click', async () => {
      const layerId = el.dataset.layer;
      if (layerId) {
        activeCategory = 'all';
        searchQuery = '';
        const entries = await _kb.search(layerId, { layer: layerId }, 50);
        renderFilteredResults(entries, t(`layers.${layerId}`, layerId));
      }
    });
  });
}

async function renderFilteredResults(entries, title) {
  const resultsEl = _container?.querySelector('#kb-results');
  if (!resultsEl) return;

  let html = `<div style="display:flex;align-items:center;gap:8px;padding:4px 0;">
    <button id="kb-filter-back" style="background:none;border:none;cursor:pointer;">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
    </button>
    <span style="font-size:14px;font-weight:600;color:var(--text-primary);">${title}</span>
    <span style="font-size:11px;color:var(--text-secondary);">(${entries.length})</span>
  </div>`;

  html += entries.map(entry => renderArticleCard(entry)).join('');
  resultsEl.innerHTML = html;

  resultsEl.querySelector('#kb-filter-back')?.addEventListener('click', () => {
    activeCategory = 'systems';
    renderResults();
  });
  bindResultEvents(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Render Helpers
// ═══════════════════════════════════════════════════════════

function renderSystemItem(title, subtitle, color, layerId) {
  return `
    <div class="kb-system-item" data-layer="${layerId}" style="cursor:pointer;">
      <div class="kb-system-item__left">
        <div class="kb-system-item__icon" style="background:${color}20;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
        </div>
        <div class="kb-system-item__info">
          <span class="kb-system-item__title">${title}</span>
          <span class="kb-system-item__subtitle">${subtitle}</span>
        </div>
      </div>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
    </div>
  `;
}

function renderArticleCard(entry) {
  const color = LAYER_COLORS[entry.layer] || '#8B949E';
  const vehicleLabel = entry.vehicle === 'l9' ? 'L9' : entry.vehicle === 'l7' ? 'L7' : 'All';
  const pageInfo = entry.pageStart ? `p.${entry.pageStart}` : '';

  // Бейдж источника
  const srcInfo = SOURCE_BADGES[entry.source] || { icon: '\u{1F4C4}', label: entry.source };
  const sourceBadge = `<span style="font-size:10px;color:var(--text-tertiary);background:var(--surface-tertiary, rgba(0,0,0,0.04));padding:1px 6px;border-radius:10px;">${srcInfo.icon} ${srcInfo.label}</span>`;

  // Язык
  const langBadge = entry.language ? `<span style="font-size:10px;color:var(--text-tertiary);">${LANG_FLAGS[entry.language] || entry.language}</span>` : '';

  // DTC коды
  let dtcBadges = '';
  if (entry.dtcCodes?.length > 0) {
    dtcBadges = entry.dtcCodes.slice(0, 3).map(dtc =>
      `<span style="font-size:10px;color:${color};background:${color}15;padding:1px 5px;border-radius:8px;">${dtc}</span>`
    ).join('');
  }

  // Инструкции / предупреждения
  let badges = '';
  if (entry.hasProcedures) {
    badges += '<span style="font-size:10px;color:var(--accent-primary);background:var(--accent-primary-dim);padding:1px 6px;border-radius:10px;">steps</span>';
  }
  if (entry.hasWarnings) {
    badges += '<span style="font-size:10px;color:var(--status-warning);background:var(--warning-bg);padding:1px 6px;border-radius:10px;">warning</span>';
  }

  // Score (релевантность)
  const scoreBar = entry.score != null
    ? `<div style="width:30px;height:3px;border-radius:2px;background:var(--border-default);overflow:hidden;flex-shrink:0;">
        <div style="width:${Math.round(entry.score * 100)}%;height:100%;background:${color};border-radius:2px;"></div>
       </div>` : '';

  return `
    <div class="kb-content-item" data-entry-id="${entry.id}" style="cursor:pointer;">
      <div style="width:4px;height:100%;min-height:36px;border-radius:2px;background:${color};flex-shrink:0;"></div>
      <div class="kb-content-item__info" style="flex:1;min-width:0;">
        <span class="kb-content-item__title">${entry.title}</span>
        <span class="kb-content-item__subtitle" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <span>${vehicleLabel}</span>
          ${langBadge}
          ${pageInfo ? `<span>&bull;</span><span>${pageInfo}</span>` : ''}
          ${sourceBadge}
          ${badges}
          ${dtcBadges}
        </span>
      </div>
      ${scoreBar}
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round"><path d="m9 18 6-6-6-6"/></svg>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════
// Category Tabs
// ═══════════════════════════════════════════════════════════

function renderCategoryTabs() {
  const tabsEl = _container?.querySelector('#kb-categories');
  if (!tabsEl) return;

  const labels = {
    all: t('knowledge.all', 'All'),
    systems: t('knowledge.systems', 'Systems'),
    manuals: t('knowledge.manuals', 'Manuals'),
    dtc: 'DTC',
  };

  tabsEl.innerHTML = CATEGORIES.map(cat => `
    <button class="system-tab ${cat === activeCategory ? 'system-tab--active' : ''}" data-cat="${cat}">
      ${labels[cat] || cat}
    </button>
  `).join('');

  tabsEl.querySelectorAll('.system-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      activeCategory = btn.dataset.cat;
      selectedComponentTags = [];
      updateTagFilter();
      renderCategoryTabs();
      renderResults();
    });
  });
}

// ═══════════════════════════════════════════════════════════
// Events
// ═══════════════════════════════════════════════════════════

function bindEvents() {
  _container?.querySelector('#kb-back')?.addEventListener('click', () => {
    emit('app:navigate', { screen: 'dashboard' });
  });

  const searchInput = _container?.querySelector('#kb-search-input');
  if (searchInput) {
    let debounceTimer = null;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        searchQuery = searchInput.value.trim();
        renderResults();
        const clearBtn = _container?.querySelector('#kb-search-clear');
        if (clearBtn) clearBtn.style.display = searchQuery ? '' : 'none';
      }, 400);
    });
  }

  _container?.querySelector('#kb-search-clear')?.addEventListener('click', () => {
    searchQuery = '';
    const input = _container?.querySelector('#kb-search-input');
    if (input) input.value = '';
    renderResults();
  });

  _container?.querySelectorAll('.kb-vehicle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const v = btn.dataset.vehicle;
      activeVehicle = v === 'all' ? null : v;
      renderContent();
    });
  });

  _container?.querySelector('#kb-tag-clear')?.addEventListener('click', () => {
    selectedComponentTags = [];
    selectedComponentData = null;
    updateTagFilter();
    renderResults();
  });
}

function bindResultEvents(resultsEl) {
  resultsEl.querySelectorAll('.kb-content-item[data-entry-id]').forEach(el => {
    el.addEventListener('click', async () => {
      const entryId = el.dataset.entryId;
      // Ищем запись из последних результатов или делаем запрос
      const entry = await findEntryById(entryId);
      if (entry) renderArticleDetail(entry);
    });
  });
}

async function findEntryById(id) {
  // Пробуем найти в кэше через search
  if (_kb?._cache) {
    for (const [, cached] of _kb._cache) {
      const items = cached.data;
      if (Array.isArray(items)) {
        const found = items.find(e => e.id === id);
        if (found) return found;
      } else if (items?.articles) {
        const found = items.articles.find(e => e.id === id);
        if (found) return found;
      }
    }
  }
  // Запрос к API по ID (через search)
  const results = await _kb.search(id, {}, 1);
  return results[0] || null;
}

// ═══════════════════════════════════════════════════════════
// Article Detail
// ═══════════════════════════════════════════════════════════

function renderArticleDetail(entry) {
  const resultsEl = _container?.querySelector('#kb-results');
  if (!resultsEl) return;

  const color = LAYER_COLORS[entry.layer] || '#8B949E';
  const vehicleLabel = entry.vehicle === 'l9' ? 'Li L9' : entry.vehicle === 'l7' ? 'Li L7' : 'All';
  const pageInfo = entry.pageStart ? `p. ${entry.pageStart}` : '';
  const srcInfo = SOURCE_BADGES[entry.source] || { icon: '\u{1F4C4}', label: entry.source };

  // Теги glossary_ids
  const tags = (entry.glossaryIds || []).map(tag => {
    const name = tag.split('@')[0].replace(/_/g, ' ');
    return `<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:${color}20;color:${color};border:1px solid ${color}40;">${name}</span>`;
  }).join('');

  // DTC коды
  const dtcHtml = (entry.dtcCodes?.length > 0) ? `
    <div style="display:flex;flex-wrap:wrap;gap:6px;">
      ${entry.dtcCodes.map(dtc => `<span class="kb-dtc-badge" data-dtc="${dtc}" style="cursor:pointer;font-size:12px;padding:3px 10px;border-radius:12px;background:${color}15;color:${color};border:1px solid ${color}30;font-weight:500;">${dtc}</span>`).join('')}
    </div>` : '';

  let badges = '';
  if (entry.hasProcedures) {
    badges += '<span style="font-size:11px;color:var(--accent-primary);background:var(--accent-primary-dim);padding:2px 8px;border-radius:10px;">Пошаговая инструкция</span>';
  }
  if (entry.hasWarnings) {
    badges += '<span style="font-size:11px;color:var(--status-warning);background:var(--warning-bg);padding:2px 8px;border-radius:10px;">Предупреждение</span>';
  }

  // Ссылка на источник
  const sourceLink = entry.sourceUrl
    ? `<a href="${entry.sourceUrl}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:var(--accent-primary);text-decoration:none;">
        ${srcInfo.icon} ${t('knowledge.open_source', 'Open source')} &rarr;
       </a>` : '';

  resultsEl.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:16px;">
      <button id="kb-detail-back" style="display:flex;align-items:center;gap:6px;background:none;border:none;cursor:pointer;padding:4px 0;color:var(--text-secondary);font-size:13px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
        ${t('knowledge.back_to_results', 'Back to results')}
      </button>

      <div style="display:flex;gap:12px;align-items:flex-start;">
        <div style="width:4px;min-height:48px;border-radius:2px;background:${color};flex-shrink:0;margin-top:2px;"></div>
        <div style="flex:1;">
          <h3 style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0 0 8px 0;line-height:1.3;">${entry.title}</h3>
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span style="font-size:12px;color:var(--text-secondary);">${vehicleLabel}</span>
            <span style="font-size:12px;color:var(--text-tertiary);">${LANG_FLAGS[entry.language] || ''}</span>
            ${pageInfo ? `<span style="font-size:12px;color:var(--text-tertiary);">&bull; ${pageInfo}</span>` : ''}
            <span style="font-size:11px;color:var(--text-tertiary);">${srcInfo.icon} ${srcInfo.label}</span>
            ${badges}
          </div>
        </div>
      </div>

      <div style="padding:12px;background:var(--surface-secondary);border-radius:var(--radius-md);border:1px solid var(--border-default);">
        <p style="font-size:13px;color:var(--text-secondary);line-height:1.6;margin:0;white-space:pre-wrap;">${entry.content || entry.preview || 'No content'}</p>
      </div>

      ${dtcHtml}
      ${tags ? `<div style="display:flex;flex-wrap:wrap;gap:6px;">${tags}</div>` : ''}
      ${sourceLink}

      ${(entry.glossaryIds?.length > 0) ? `
        <button id="kb-show-in-3d" data-tag="${entry.glossaryIds[0]}" style="display:flex;align-items:center;justify-content:center;gap:8px;padding:10px 16px;background:var(--accent-primary);color:white;border:none;border-radius:var(--radius-md);cursor:pointer;font-size:13px;font-weight:500;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.3 7 12 12 20.7 7"/><line x1="12" y1="22" x2="12" y2="12"/></svg>
          ${t('knowledge.show_in_3d', 'Show in 3D')}
        </button>
      ` : ''}
    </div>
  `;

  // Назад
  resultsEl.querySelector('#kb-detail-back')?.addEventListener('click', () => renderResults());

  // 3D
  resultsEl.querySelector('#kb-show-in-3d')?.addEventListener('click', () => {
    const tag = resultsEl.querySelector('#kb-show-in-3d')?.dataset.tag;
    if (tag) {
      window.__llcar_selectedComponent = tag;
      emit('app:navigate', { screen: 'twin' });
      setTimeout(() => emit('component:select', { glossaryId: tag, source: 'kb' }), 300);
    }
  });

  // DTC бейджи
  resultsEl.querySelectorAll('.kb-dtc-badge').forEach(el => {
    el.addEventListener('click', async (e) => {
      e.stopPropagation();
      searchQuery = el.dataset.dtc;
      const input = _container?.querySelector('#kb-search-input');
      if (input) input.value = searchQuery;
      selectedComponentTags = [];
      selectedComponentData = null;
      updateTagFilter();
      await renderResults();
    });
  });
}

// ═══════════════════════════════════════════════════════════
// Tag Filter
// ═══════════════════════════════════════════════════════════

function updateTagFilter() {
  const filterEl = _container?.querySelector('#kb-tag-filter');
  const labelEl = _container?.querySelector('#kb-tag-label');
  if (!filterEl || !labelEl) return;

  if (selectedComponentTags.length > 0) {
    filterEl.style.display = '';
    const names = selectedComponentTags.map(gid => {
      if (_i18n) return _i18n.getComponentName(gid);
      return gid.split('@')[0].replace(/_/g, ' ');
    });
    labelEl.textContent = names.join(', ');
  } else {
    filterEl.style.display = 'none';
  }
}

// ═══════════════════════════════════════════════════════════
// External Event Handlers
// ═══════════════════════════════════════════════════════════

function _onComponentSelect(e) {
  const detail = e.detail || e;
  if (detail.glossaryId) {
    selectedComponentTags = [detail.glossaryId];
    if (detail.component?.isAnnotation) {
      selectedComponentData = {
        glossaryId: detail.glossaryId,
        dtcCodes: detail.component.dtcCodes || [],
        category: detail.component.category || '',
        layer: detail.component.layer || '',
      };
    }
  } else if (detail.tags) {
    selectedComponentTags = detail.tags;
  }
  const kbScreen = document.getElementById('screen-knowledge');
  const isVisible = kbScreen?.classList.contains('screen--active');
  if (selectedComponentTags.length > 0 && _rendered && isVisible) {
    updateTagFilter();
    renderResults();
  }
}

function _onLangChange() {
  _i18n = window.__llcar_i18n || null;
  if (_rendered) {
    _rendered = false;
    render(_container);
  }
}

// ═══════════════════════════════════════════════════════════
// Public API
// ═══════════════════════════════════════════════════════════

export function getKB() { return _kb; }

export function setI18n(i18n) {
  _i18n = i18n;
  if (typeof window !== 'undefined') window.__llcar_i18n = i18n;
}

export function cleanup() {
  _rendered = false;
  activeCategory = 'all';
  searchQuery = '';
  selectedComponentTags = [];
  selectedComponentData = null;
  off('component:select', _onComponentSelect);
  off('lang:change', _onLangChange);
  if (_container) _container.innerHTML = '';
}
