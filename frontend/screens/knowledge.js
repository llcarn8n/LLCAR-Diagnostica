/**
 * Knowledge Base Screen (API-powered)
 *
 * Все поисковые запросы через KB API v2 (LanceDB + FTS5 + ColBERT).
 * Гибридный семантический поиск на RU/EN/ZH.
 * Бейджи источников, DTC коды, ссылки на manuals.lixiang.com.
 */

import { emit, on, off } from '../event-bus.js';
import { KnowledgeBase } from '../knowledge-base.js';
import { renderMarkdown } from '../kb-viewer.js';

let _container = null;
let _rendered = false;
let _kb = null;
let _i18n = null;

let activeCategory = 'all';
let activeVehicle = null;
let searchQuery = '';
let selectedComponentTags = [];
let selectedComponentData = null;
let _partsBridgeCache = null;

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

const CATEGORIES = ['all', 'systems', 'parts', 'manuals', 'dtc'];


// Иконки источников
const SOURCE_BADGES = {
  pdf_l9_ru:              { icon: '\u{1F4D6}', label: 'L9 RU' },
  pdf_l7_ru:              { icon: '\u{1F4D6}', label: 'L7 RU' },
  pdf_l9_zh:              { icon: '\u{1F4D6}', label: 'L9 ZH' },
  pdf_l7_zh:              { icon: '\u{1F4D6}', label: 'L7 ZH' },
  pdf_l9_zh_full:         { icon: '\u{1F4D6}', label: 'L9 ZH' },
  pdf_l7_zh_full:         { icon: '\u{1F4D6}', label: 'L7 ZH' },
  parts_zh:               { icon: '\u{1F527}', label: 'Каталог' },
  parts_l9_zh:            { icon: '\u{1F527}', label: 'L9 Каталог' },
  web:                    { icon: '\u{1F310}', label: 'Веб' },
  web_l7_zh:              { icon: '\u{1F310}', label: 'L7 Веб' },
  dtc_db:                 { icon: '\u{26A0}', label: 'DTC' },
  dtc_database:           { icon: '\u{26A0}', label: 'DTC' },
  mineru_l9_en_config:    { icon: '\u{1F4CB}', label: 'L9 Конфиг.' },
  mineru_l7_zh_config:    { icon: '\u{1F4CB}', label: 'L7 Конфиг.' },
  mineru_l9_zh_parts:     { icon: '\u{1F527}', label: 'L9 Каталог' },
  mineru_l9_en:           { icon: '\u{1F4D6}', label: 'L9 EN' },
  mineru_l9_zh_owners:    { icon: '\u{1F4D6}', label: 'L9 ZH' },
  mineru_l7_zh_owners:    { icon: '\u{1F4D6}', label: 'L7 ZH' },
  mineru_l9_ru:           { icon: '\u{1F4D6}', label: 'L9 RU' },
};

// Флаги языков
const LANG_FLAGS = { ru: 'RU', en: 'EN', zh: 'ZH' };

/** Получить заголовок и контент на языке пользователя (из переводов если есть) */
function getLocalizedEntry(entry) {
  const userLang = _i18n?.currentLang || _i18n?.lang || 'ru';
  const srcLang = entry.source_language || '';
  // Если язык статьи совпадает — ничего не делаем
  if (srcLang === userLang) return entry;
  // Ищем перевод в translations
  if (entry.translations?.length > 0) {
    const tr = entry.translations.find(t => t.lang === userLang);
    if (tr && tr.title) {
      return { ...entry, title: tr.title, content: tr.content || entry.content, _translated: true };
    }
  }
  return entry;
}

/** Общие фильтры для всех поисковых вызовов */
function _searchFilters(extra = {}) {
  return {
    model: activeVehicle || undefined,
    translations: true,
    ...extra,
  };
}

/** Обновить счётчик статей в заголовке */
function _updateArticleCount(count) {
  const el = _container?.querySelector('#kb-article-count');
  if (el) el.textContent = `${count} ${t('knowledge.articles', 'статей')}`;
}

// Base URL for parts catalog images (served by FastAPI)
const PARTS_IMG_BASE = 'http://localhost:8000';

// RU translations for part catalog system names
const SYSTEM_NAME_RU = {
  'Interior Trim System': 'Система внутренней отделки',
  'Passive Safety System': 'Пассивная безопасность',
  'HVAC & Thermal Management': 'Климат и терморегуляция',
  'Closures (Doors, Hood, Tailgate)': 'Двери, капот, багажник',
  'Seat System': 'Сиденья',
  'Engine Assembly': 'Двигатель',
  'Power & Signal Distribution': 'Электропитание и сигнализация',
  'Rear Suspension': 'Задняя подвеска',
  'Body Structure': 'Кузов',
  'Smart Cabin / Infotainment': 'Мультимедиа и салон',
  'Service Brake System': 'Тормозная система',
  'Power Drive System': 'Силовой привод',
  'Lighting System': 'Освещение',
  'Intake System': 'Система впуска',
  'Front Suspension': 'Передняя подвеска',
  'Vehicle Accessories & Consumables': 'Аксессуары и расходники',
  'Fuel Supply System': 'Топливная система',
  'Engine/Drivetrain Mounts': 'Опоры двигателя и трансмиссии',
  'Autonomous Driving System': 'Автопилот',
  'Exhaust System': 'Выхлопная система',
  'Steering System': 'Рулевое управление',
  'Power Battery System': 'Тяговая батарея',
  'Exterior Trim System': 'Наружная отделка',
};

function _sysNameFromEn(systemEn) {
  const lang = _i18n?.lang || 'ru';
  if (lang === 'ru') return SYSTEM_NAME_RU[systemEn] || systemEn;
  return systemEn;
}

function t(key, fallback) {
  if (_i18n) return _i18n.get(key, fallback);
  return fallback || key;
}

/**
 * Рендер экрана базы знаний.
 */
export function render(container) {
  _container = container;

  // Deep link from 3D twin → specific part detail
  if (window.__llcar_partDetail) {
    const { partNumber, nameZh } = window.__llcar_partDetail;
    window.__llcar_partDetail = null;
    activeCategory = 'parts';
    if (_rendered && _kb?._loaded) {
      const resultsEl = _container.querySelector('.kb-results');
      if (resultsEl) {
        renderPartDetail(resultsEl, partNumber, nameZh, null);
        return;
      }
    }
    // Will render after init, store for later
    window.__llcar_partDetail = { partNumber, nameZh };
  }

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
          <span style="font-size:17px;font-weight:600;color:var(--text-primary);" data-i18n="knowledge.title">${t('knowledge.title', 'База знаний')}</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <div class="kbv2-persona-switch" id="kb-persona-switch" style="display:inline-flex;gap:2px;background:var(--bg-elevated,#1E2024);border-radius:var(--radius-pill,12px);padding:2px;">
            <button class="kbv2-persona-btn" data-persona="beginner" style="font-size:10px;font-weight:500;padding:3px 10px;border-radius:var(--radius-pill,12px);border:none;cursor:pointer;color:var(--text-tertiary);background:none;">${t('kbv2.beginner', 'Новичок')}</button>
            <button class="kbv2-persona-btn kbv2-persona-btn--active" data-persona="expert" style="font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--radius-pill,12px);border:none;cursor:pointer;background:var(--accent-primary);color:var(--text-on-accent,#fff);">${t('kbv2.expert', 'Эксперт')}</button>
          </div>
          <span id="kb-api-status" style="width:8px;height:8px;border-radius:50%;background:${isOnline ? 'var(--status-ok, #66BB6A)' : 'var(--status-error, #EF5350)'};"></span>
          <span style="font-size:10px;color:var(--text-tertiary);">${isOnline ? 'API' : 'Offline'}</span>
        </div>
      </div>

      <!-- Поиск -->
      <div style="padding:0 20px;">
        <div class="search-bar" style="position:relative;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input type="text" id="kb-search-input"
            placeholder="${t('knowledge.search', 'Поиск по документации...')}"
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
            ${t('knowledge.all', 'Все')}
          </button>
          <button class="kb-vehicle-btn ${activeVehicle === 'l7' ? 'kb-vehicle-btn--active' : ''}" data-vehicle="l7" style="font-size:12px;font-weight:600;padding:4px 10px;border-radius:var(--radius-pill);border:1px solid var(--border-default);">
            Li L7
          </button>
          <button class="kb-vehicle-btn ${activeVehicle === 'l9' ? 'kb-vehicle-btn--active' : ''}" data-vehicle="l9" style="font-size:12px;font-weight:600;padding:4px 10px;border-radius:var(--radius-pill);border:1px solid var(--border-default);">
            Li L9
          </button>
        </div>
        <span id="kb-article-count" style="font-size:11px;color:var(--text-secondary);">${totalArticles} ${t('knowledge.articles', 'статей')}</span>
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
      resultsEl.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;padding:40px 0;color:var(--text-tertiary);font-size:14px;" data-i18n="common.loading">${t('common.loading', 'Загрузка...')}</div>`;
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
    if (entries.length < 5 && selectedComponentData?.dtc_codes?.length > 0) {
      for (const dtc of selectedComponentData.dtc_codes) {
        const dtcResult = await _kb.getDTC(dtc);
        for (const art of (dtcResult.chunks || dtcResult.articles || [])) {
          if (!entries.find(e => e.chunk_id === art.chunk_id)) entries.push(art);
        }
      }
    }
  } else if (activeCategory === 'parts') {
    renderPartsView(resultsEl);
    return;
  } else if (searchQuery) {
    const searchResp = await _kb.search(searchQuery, _searchFilters(), 50);
    entries = searchResp.results || [];
    // Обновить счётчик — показать сколько найдено
    _updateArticleCount(searchResp.total || entries.length);
  } else if (activeCategory === 'systems') {
    renderLayerView(resultsEl);
    return;
  } else if (activeCategory === 'dtc') {
    renderDTCView(resultsEl);
    return;
  } else {
    // По умолчанию — показать обзор систем вместо случайного поиска
    renderDefaultView(resultsEl);
    return;
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
              <span style="font-size:12px;color:var(--text-secondary);">${t('knowledge.system', 'Система')}: ${layerLabel}</span>
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
            ${t('knowledge.no_articles_component', 'Статей по этому компоненту не найдено')}
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
          <span style="color:var(--text-tertiary);font-size:14px;" data-i18n="knowledge.no_results">${t('knowledge.no_results', 'Ничего не найдено')}</span>
        </div>
      `;
    }
    return;
  }

  // Локализация: показываем переведённые заголовки
  entries = entries.map(e => getLocalizedEntry(e));

  // Сортировка: экстренные (urgency >= 4) наверху, потом по релевантности
  entries.sort((a, b) => {
    const aUrg = (a.urgency || 1) >= 4 ? 1 : 0;
    const bUrg = (b.urgency || 1) >= 4 ? 1 : 0;
    if (aUrg !== bUrg) return bUrg - aUrg;
    return (b.score || 0) - (a.score || 0);
  });

  // Дедупликация и рендер карточек
  entries = _deduplicateResults(entries);
  const html = entries.slice(0, 40).map(entry => renderArticleCard(entry)).join('');
  resultsEl.innerHTML = html;
  bindResultEvents(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Default View — ситуационные быстрые кнопки
// ═══════════════════════════════════════════════════════════

async function renderDefaultView(resultsEl) {
  const quickSearches = [
    { icon: '\u26A0\uFE0F', label: t('knowledge.emergency', 'Экстренные ситуации'), query: 'опасность предупреждение остановить', color: '#EF5350' },
    { icon: '\u{1F527}', label: t('knowledge.maintenance_title', 'Обслуживание'), query: 'замена масло фильтр обслуживание', color: '#42A5F5' },
    { icon: '\u{1F50B}', label: t('knowledge.battery_ev', 'Батарея и электро'), query: 'батарея зарядка напряжение', color: '#66BB6A' },
    { icon: '\u{1F6DE}', label: t('knowledge.brakes_title', 'Тормозная система'), query: 'тормоз колодки диск', color: '#EF5350' },
    { icon: '\u2744\uFE0F', label: t('knowledge.winter', 'Зимняя эксплуатация'), query: 'зима мороз обогрев', color: '#4FC3F7' },
    { icon: '\u{1F321}\uFE0F', label: t('knowledge.summer', 'Летняя эксплуатация'), query: 'перегрев охлаждение кондиционер', color: '#FFA726' },
    { icon: '\u{1F4A1}', label: t('knowledge.lights', 'Освещение'), query: 'фара свет лампа', color: '#FFA726' },
    { icon: '\u{1F3CE}\uFE0F', label: t('knowledge.drivetrain_title', 'Трансмиссия'), query: 'привод трансмиссия коробка', color: '#AB47BC' },
  ];

  let html = `<div style="display:flex;flex-direction:column;gap:12px;">
    <span style="font-size:14px;font-weight:600;color:var(--text-primary);padding:4px 0;">${t('knowledge.quick_search', 'Быстрый поиск по ситуации')}</span>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
  `;

  for (const qs of quickSearches) {
    html += `
      <div class="kb-quick-search" data-query="${qs.query}" style="cursor:pointer;display:flex;align-items:center;gap:10px;padding:12px;border-radius:var(--radius-md);border:1px solid var(--border-default);background:var(--surface-secondary);">
        <span style="font-size:20px;">${qs.icon}</span>
        <span style="font-size:13px;font-weight:500;color:var(--text-primary);">${qs.label}</span>
      </div>
    `;
  }

  html += `</div>`;

  // Блок систем
  const stats = _kb.getLayerStats();
  if (stats.length > 0) {
    html += `<span style="font-size:14px;font-weight:600;color:var(--text-primary);padding:8px 0 4px 0;">${t('knowledge.systems', 'Системы')}</span>`;
    for (const stat of stats) {
      if (stat.id === 'general' || stat.id === 'unknown') continue;
      const color = LAYER_COLORS[stat.id] || '#8B949E';
      const layerLabel = t(`layers.${stat.id}`, stat.id);
      html += renderSystemItem(layerLabel, `${stat.count} ${t('knowledge.articles', 'статей')}`, color, stat.id);
    }
  }

  html += `</div>`;
  resultsEl.innerHTML = html;

  // Быстрый поиск по клику
  resultsEl.querySelectorAll('.kb-quick-search').forEach(el => {
    el.addEventListener('click', () => {
      searchQuery = el.dataset.query;
      activeCategory = 'all';
      // Полный перерисовка чтобы кнопка X появилась
      renderContent();
    });
  });

  // Клик по системе — browse без текстового запроса
  resultsEl.querySelectorAll('.kb-system-item').forEach(el => {
    el.addEventListener('click', async () => {
      const layerId = el.dataset.layer;
      if (layerId) {
        const layerLabel = t(`layers.${layerId}`, layerId);
        const resp = await _kb.browse(layerId, { model: activeVehicle || undefined }, 50);
        const entries = (resp.results || []).map(e => getLocalizedEntry(e));
        _updateArticleCount(resp.total || entries.length);
        renderFilteredResults(entries, `${layerLabel} (${resp.total || entries.length})`);
      }
    });
  });
}

// ═══════════════════════════════════════════════════════════
// DTC View — все коды ошибок
// ═══════════════════════════════════════════════════════════

async function renderDTCView(resultsEl) {
  // If user typed a specific DTC code — search for it
  if (searchQuery) {
    const dtcResult = await _kb.getDTC(searchQuery.trim().toUpperCase());
    const chunks = dtcResult?.chunks || [];
    if (chunks.length > 0) {
      const localized = chunks.map(e => getLocalizedEntry(e));
      renderFilteredResults(localized, `DTC ${searchQuery.toUpperCase()}`);
      return;
    }
    // Fallback to text search
    const entries = (await _kb.search(searchQuery, _searchFilters({ contentType: 'dtc' }), 50)).results || [];
    if (entries.length > 0) {
      const localized = entries.map(e => getLocalizedEntry(e));
      renderFilteredResults(localized, `DTC: ${searchQuery}`);
      return;
    }
  }

  // Show all DTC codes — browse by content_type, no text search
  const allDTC = (await _kb.browse(null, { model: activeVehicle || undefined, content_type: 'dtc' }, 500)).results || [];
  const localized = allDTC.map(e => getLocalizedEntry(e));

  // Deduplicate DTC by code — prefer entry with descriptive title (not just "Код неисправности: PXXXX")
  const dtcDeduped = _deduplicateDTC(localized);

  // Group by prefix: P=Powertrain, C=Chassis, B=Body, U=Network
  const groups = { P: [], C: [], B: [], U: [], other: [] };
  const groupLabels = {
    P: 'Двигатель и трансмиссия',
    C: 'Шасси, подвеска, тормоза',
    B: 'Кузов, салон, освещение',
    U: 'CAN-шина, связь модулей',
    other: 'Прочие',
  };

  for (const entry of dtcDeduped) {
    const code = (entry.dtc_codes?.[0] || entry.title || '').toUpperCase();
    const prefix = code.charAt(code.indexOf('DTC ') >= 0 ? code.indexOf('DTC ') + 4 : 0);
    if (groups[prefix]) groups[prefix].push(entry);
    else groups.other.push(entry);
  }

  _updateArticleCount(dtcDeduped.length);

  let html = `<div style="display:flex;flex-direction:column;gap:12px;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:14px;font-weight:600;color:var(--text-primary);">DTC коды ошибок (${dtcDeduped.length})</span>
    </div>
    <div style="font-size:12px;color:var(--text-tertiary);padding:0 0 4px 0;">
      Введите код (напр. P0300) в поиске. Префикс: P=двигатель, B=кузов, C=шасси, U=связь
    </div>
  `;

  for (const [prefix, items] of Object.entries(groups)) {
    if (items.length === 0) continue;
    const label = groupLabels[prefix] || prefix;
    html += `<div style="font-size:13px;font-weight:600;color:var(--text-secondary);padding:8px 0 2px 0;">${prefix} — ${label} (${items.length})</div>`;
    html += items.map(entry => renderArticleCard(entry)).join('');
  }

  html += `</div>`;
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
    const subtitle = `${stat.count} ${t('knowledge.articles', 'статей')}`;

    html += renderSystemItem(layerLabel, subtitle, color, stat.id);
  }

  resultsEl.innerHTML = html;

  resultsEl.querySelectorAll('.kb-system-item').forEach(el => {
    el.addEventListener('click', async () => {
      const layerId = el.dataset.layer;
      if (layerId) {
        const layerLabel = t(`layers.${layerId}`, layerId);
        // Используем browse (без текстового запроса) — просто фильтр по слою
        const resp = await _kb.browse(layerId, { model: activeVehicle || undefined }, 50);
        const entries = (resp.results || []).map(e => getLocalizedEntry(e));
        _updateArticleCount(resp.total || entries.length);
        renderFilteredResults(entries, `${layerLabel} (${resp.total || entries.length})`);
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

  entries = _deduplicateResults(entries);
  html += entries.map(entry => renderArticleCard(entry)).join('');
  resultsEl.innerHTML = html;

  resultsEl.querySelector('#kb-filter-back')?.addEventListener('click', () => {
    activeCategory = 'systems';
    renderResults();
  });
  bindResultEvents(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Parts Catalog View
// ═══════════════════════════════════════════════════════════

async function renderPartsView(resultsEl) {
  // If there's a search query, search parts directly
  if (searchQuery) {
    const resp = await _kb.searchParts(searchQuery, { limit: 50 });
    if (resp.results?.length > 0) {
      renderPartsResults(resultsEl, resp.results, searchQuery);
    } else {
      resultsEl.innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 0;gap:12px;">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5" stroke-linecap="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          <span style="color:var(--text-tertiary);font-size:14px;" data-i18n="knowledge.no_results">${t('knowledge.no_results', 'Ничего не найдено')}</span>
        </div>
      `;
    }
    return;
  }

  // Show parts stats overview
  const stats = await _kb.getPartsStats();
  if (!stats || stats.total_parts === 0) {
    resultsEl.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 0;gap:12px;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5" stroke-linecap="round">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
        </svg>
        <span style="color:var(--text-tertiary);font-size:14px;">${t('knowledge.parts_empty', 'Каталог деталей не загружен')}</span>
        <span style="color:var(--text-tertiary);font-size:12px;">Run: python scripts/ocr_parts_tables.py</span>
      </div>
    `;
    return;
  }

  // Summary header
  let html = `
    <div style="padding:8px 0;display:flex;align-items:center;gap:12px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:22px;font-weight:700;color:var(--text-primary);">${stats.total_parts.toLocaleString()}</span>
        <span style="font-size:12px;color:var(--text-secondary);">${t('knowledge.parts_total', 'деталей')}</span>
      </div>
      <span style="font-size:11px;color:var(--text-tertiary);">${stats.unique_part_numbers} ${t('knowledge.unique', 'уникальных')}</span>
    </div>
  `;

  // System list
  const PART_SYSTEM_COLORS = {
    'Power Battery System': '#66BB6A',
    'Power Drive System': '#AB47BC',
    'Engine Assembly': '#FF7043',
    'Front Suspension': '#26C6DA',
    'Rear Suspension': '#26C6DA',
    'Service Brake System': '#EF5350',
    'HVAC & Thermal Management': '#42A5F5',
    'Interior Trim System': '#8D6E63',
    'Exterior Trim System': '#78909C',
    'Lighting System': '#FFA726',
    'Seat System': '#A1887F',
    'Steering System': '#7E57C2',
    'Closures (Doors, Hood, Tailgate)': '#5C6BC0',
    'Body Structure': '#546E7A',
    'Autonomous Driving System': '#29B6F6',
    'Smart Cabin / Infotainment': '#EC407A',
  };

  function _sysName(sys) {
    const lang = _i18n?.lang || 'ru';
    if (lang === 'zh') return sys.system_zh || sys.system_en;
    return _sysNameFromEn(sys.system_en) || sys.system_zh;
  }

  for (const sys of stats.systems) {
    const color = PART_SYSTEM_COLORS[sys.system_en] || '#8B949E';
    const subtitle = `${sys.part_count} ${t('knowledge.parts_total', 'деталей')} \u00B7 ${sys.subsystem_count} ${t('knowledge.subsystems', 'подсистем')}`;
    html += `
      <div class="kb-system-item kb-parts-system" data-system="${sys.system_en}" style="cursor:pointer;">
        <div class="kb-system-item__left">
          <div class="kb-system-item__icon" style="background:${color}20;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
          </div>
          <div class="kb-system-item__info">
            <span class="kb-system-item__title">${_sysName(sys)}</span>
            <span class="kb-system-item__subtitle">${subtitle}</span>
          </div>
        </div>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
      </div>
    `;
  }

  resultsEl.innerHTML = html;

  // Bind click events — open subsystem view with illustrations
  resultsEl.querySelectorAll('.kb-parts-system').forEach(el => {
    el.addEventListener('click', async () => {
      const sysName = el.dataset.system;
      await renderSubsystemsView(resultsEl, sysName);
    });
  });
}

async function renderSubsystemsView(resultsEl, systemName) {
  resultsEl.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;padding:30px 0;color:var(--text-tertiary);font-size:13px;">
    <svg width="18" height="18" viewBox="0 0 24 24" style="animation:spin 1s linear infinite;margin-right:8px;" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
    ${t('common.loading', 'Загрузка...')}
  </div>`;

  // Load ALL parts for this system, then group by source_image (= catalog diagram)
  const resp = await _kb.searchParts('', { system: systemName, limit: 1000 });
  const allParts = resp.results || [];
  if (allParts.length === 0) {
    resultsEl.innerHTML = `<div style="padding:40px 0;text-align:center;color:var(--text-tertiary);font-size:13px;">${t('knowledge.no_results', 'Ничего не найдено')}</div>`;
    return;
  }

  // Group by diagram_image — each unique assembly diagram
  const groups = new Map();
  for (const part of allParts) {
    const key = part.diagram_image || part.source_image || '__no_image__';
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(part);
  }

  // Sort groups by page_idx of first part
  const sortedGroups = [...groups.entries()].sort((a, b) => {
    const pageA = a[1][0]?.page_idx ?? 9999;
    const pageB = b[1][0]?.page_idx ?? 9999;
    return pageA - pageB;
  });

  let html = `
    <div style="display:flex;align-items:center;gap:8px;padding:4px 0;">
      <button id="kb-parts-back" style="background:none;border:none;cursor:pointer;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <span style="font-size:14px;font-weight:600;color:var(--text-primary);">${_sysNameFromEn(systemName)}</span>
      <span style="font-size:11px;color:var(--text-secondary);">(${sortedGroups.length} ${t('knowledge.diagrams', 'диаграмм')}, ${allParts.length} ${t('knowledge.parts_total', 'деталей')})</span>
    </div>
  `;

  // Render each diagram full-width with its parts listed below
  for (const [imgKey, parts] of sortedGroups) {
    const imgSrc = imgKey !== '__no_image__' ? PARTS_IMG_BASE + '/' + imgKey : '';
    const pageNum = parts[0]?.page_idx;

    // Full-width diagram image — outside card div to avoid flex/overflow issues
    if (imgSrc) {
      html += `<div style="margin:8px 0 0;border-radius:10px 10px 0 0;border:1px solid var(--border-default);border-bottom:none;background:#f5f5f5;text-align:center;"><img src="${imgSrc}" style="max-width:100%;height:auto;display:inline-block;border-radius:10px 10px 0 0;" /></div>`;
    }

    html += `<div style="margin:0 0 16px;border-radius:${imgSrc ? '0 0 10px 10px' : '10px'};border:1px solid var(--border-default);${imgSrc ? 'border-top:none;' : ''}background:var(--bg-secondary);">`;

    // Parts for this diagram
    html += `<div style="padding:8px 10px;">`;
    if (pageNum != null) {
      html += `<div style="font-size:10px;color:var(--text-tertiary);margin-bottom:4px;">${t('knowledge.page', 'Стр.')} ${pageNum} \u00B7 ${parts.length} ${t('knowledge.parts_short', 'дет.')}</div>`;
    }
    for (const part of parts) {
      html += `
        <div class="kb-part-card" data-part-number="${part.part_number}" data-part-name="${(part.part_name_zh || '').replace(/"/g, '&quot;')}" data-system="${systemName.replace(/"/g, '&quot;')}" style="cursor:pointer;display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid var(--border-default);">
          <span style="font-family:monospace;font-size:11px;color:var(--accent-primary);font-weight:500;min-width:110px;">${part.part_number}</span>
          <span style="font-size:12px;color:var(--text-primary);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${_partDisplayName(part)}</span>
          ${part.hotspot_id ? `<span style="font-size:10px;color:var(--text-tertiary);flex-shrink:0;">#${part.hotspot_id}</span>` : ''}
        </div>`;
    }
    html += `</div></div>`;
  }

  resultsEl.innerHTML = html;

  resultsEl.querySelector('#kb-parts-back')?.addEventListener('click', () => {
    activeCategory = 'parts';
    renderResults();
  });

  // Click diagram image → open full size
  resultsEl.querySelectorAll('.kb-diagram-img').forEach(img => {
    img.addEventListener('click', () => window.open(img.src, '_blank'));
  });

  // Click part → detail view
  resultsEl.querySelectorAll('.kb-part-card').forEach(el => {
    el.addEventListener('click', () => {
      const pn = el.dataset.partNumber;
      const nameZh = el.dataset.partName;
      const sys = el.dataset.system;
      renderPartDetail(resultsEl, pn, nameZh, sys);
    });
  });
}

function renderPartsResults(resultsEl, parts, title, parentSystem) {
  // Deduplicate by part_number (keep first occurrence)
  const seenPN = new Set();
  parts = parts.filter(p => {
    if (seenPN.has(p.part_number)) return false;
    seenPN.add(p.part_number);
    return true;
  });

  // Find assembly diagram illustration from parts
  const illustration = parts.find(p => p.diagram_image)?.diagram_image
    || parts.find(p => p.source_image)?.source_image;

  let html = `
    <div style="display:flex;align-items:center;gap:8px;padding:4px 0;">
      <button id="kb-parts-back" style="background:none;border:none;cursor:pointer;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <span style="font-size:14px;font-weight:600;color:var(--text-primary);">${title}</span>
      <span id="kb-parts-count" style="font-size:11px;color:var(--text-secondary);">(${parts.length})</span>
    </div>
  `;

  // Show illustration prominently at the top
  if (illustration) {
    const imgSrc = PARTS_IMG_BASE + '/' + illustration.replace(/^\//, '');
    html += `
      <div style="margin:4px 0 8px;border-radius:10px;overflow:hidden;border:1px solid var(--border-default);">
        <img src="${imgSrc}" alt="${t('knowledge.catalog_page', 'Диаграмма каталога')}" style="max-width:100%;display:inline-block;cursor:pointer;" id="kb-parts-illustration" onerror="console.warn('Parts img failed:', this.src);this.parentElement.style.display='none'" />
      </div>
    `;
  }

  html += `
    <div style="padding:4px 0 8px;">
      <input id="kb-parts-filter" type="text" placeholder="${t('knowledge.filter_parts', 'Фильтр деталей...')}"
        style="width:100%;box-sizing:border-box;padding:8px 12px;border-radius:8px;border:1px solid var(--border-default);background:var(--bg-secondary);color:var(--text-primary);font-size:13px;outline:none;" />
    </div>
  `;

  // Parts list container
  html += `<div id="kb-parts-list">`;
  for (const part of parts) {
    html += renderPartCard(part);
  }
  html += `</div>`;

  resultsEl.innerHTML = html;

  // Click illustration → open full size
  const illustrationImg = resultsEl.querySelector('#kb-parts-illustration');
  if (illustrationImg) {
    illustrationImg.addEventListener('click', () => window.open(illustrationImg.src, '_blank'));
  }

  // Filter input — client-side search within loaded parts
  const filterInput = resultsEl.querySelector('#kb-parts-filter');
  const listEl = resultsEl.querySelector('#kb-parts-list');
  const countEl = resultsEl.querySelector('#kb-parts-count');
  if (filterInput) {
    filterInput.addEventListener('input', () => {
      const q = filterInput.value.toLowerCase().trim();
      if (!q) {
        listEl.innerHTML = parts.map(p => renderPartCard(p)).join('');
        countEl.textContent = `(${parts.length})`;
      } else {
        const filtered = parts.filter(p =>
          (p.part_number || '').toLowerCase().includes(q) ||
          (p.part_name_zh || '').includes(q) ||
          (p.part_name_en || '').toLowerCase().includes(q) ||
          (p.part_name_ru || '').toLowerCase().includes(q)
        );
        listEl.innerHTML = filtered.length
          ? filtered.map(p => renderPartCard(p)).join('')
          : `<div style="padding:16px;text-align:center;color:var(--text-tertiary);font-size:13px;">${t('common.no_results', 'Ничего не найдено')}</div>`;
        countEl.textContent = `(${filtered.length}/${parts.length})`;
      }
      _bindPartCardClicks(listEl, parentSystem || title);
    });
  }

  resultsEl.querySelector('#kb-parts-back')?.addEventListener('click', () => {
    if (parentSystem) {
      renderSubsystemsView(resultsEl, parentSystem);
    } else {
      activeCategory = 'parts';
      renderResults();
    }
  });

  _bindPartCardClicks(listEl || resultsEl, parentSystem || title);
}

function _bindPartCardClicks(container, parentSystem) {
  const resultsEl = _container?.querySelector('#kb-results') || container;
  container.querySelectorAll('.kb-part-card').forEach(el => {
    el.addEventListener('click', () => {
      const pn = el.dataset.partNumber;
      const nameZh = el.dataset.partName;
      renderPartDetail(resultsEl, pn, nameZh, parentSystem);
    });
  });
}

function _partDisplayName(part) {
  const lang = _i18n ? _i18n.lang : 'ru';
  if (lang === 'zh') return part.part_name_zh || part.part_name_en || '';
  if (lang === 'ru') return part.part_name_ru || part.part_name_en || part.part_name_zh || '';
  return part.part_name_en || part.part_name_zh || '';
}

function _partSecondaryName(part) {
  const lang = _i18n ? _i18n.lang : 'ru';
  if (lang === 'zh') return part.part_name_en || '';
  if (lang === 'ru') return part.part_name_en || '';
  return part.part_name_zh || '';
}

function renderPartCard(part) {
  const name = _partDisplayName(part);
  const secondary = _partSecondaryName(part);
  return `
    <div class="kb-content-item kb-part-card" data-part-number="${part.part_number}" data-part-name="${(part.part_name_zh || '').replace(/"/g, '&quot;')}" style="cursor:pointer;padding:6px 0;">
      <div style="width:4px;height:100%;min-height:28px;border-radius:2px;background:#78909C;flex-shrink:0;"></div>
      <div class="kb-content-item__info" style="flex:1;min-width:0;">
        <span class="kb-content-item__title" style="font-size:13px;">${name}</span>
        <span class="kb-content-item__subtitle" style="display:flex;align-items:center;gap:6px;">
          <span style="font-family:monospace;font-size:11px;color:var(--accent-primary);font-weight:500;">${part.part_number}</span>
          ${part.hotspot_id ? `<span style="font-size:10px;color:var(--text-tertiary);">ID: ${part.hotspot_id}</span>` : ''}
          ${secondary ? `<span style="font-size:10px;color:var(--text-tertiary);">${secondary}</span>` : ''}
        </span>
      </div>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round"><path d="m9 18 6-6-6-6"/></svg>
    </div>
  `;
}

async function renderPartDetail(resultsEl, partNumber, nameZh, parentSystem) {
  resultsEl.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;padding:30px 0;color:var(--text-tertiary);font-size:13px;">
    <svg width="18" height="18" viewBox="0 0 24 24" style="animation:spin 1s linear infinite;margin-right:8px;" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
    ${t('common.loading', 'Загрузка...')}
  </div>`;

  // Fetch part details from API
  let partData = null;
  try {
    const resp = await fetch(`${_kb._api}/parts/${encodeURIComponent(partNumber)}`);
    if (resp.ok) partData = await resp.json();
  } catch (_) { /* ignore */ }

  const part = partData?.results?.[0];

  // Search KB for related articles by part name
  let relatedArticles = [];
  const searchTerm = nameZh || partNumber;
  try {
    const searchResp = await _kb.search(searchTerm, _searchFilters(), 5);
    relatedArticles = searchResp.results || [];
  } catch (_) { /* ignore */ }

  // Find 3D mesh link via parts-bridge (cached)
  let meshLink = null;
  try {
    if (!_partsBridgeCache) {
      const bridgeResp = await fetch('data/architecture/parts-bridge.json');
      if (bridgeResp.ok) _partsBridgeCache = await bridgeResp.json();
    }
    if (_partsBridgeCache) {
      for (const [, sys] of Object.entries(_partsBridgeCache.systems || {})) {
        const matchedPart = sys.parts?.find(p => p.number === partNumber);
        if (matchedPart) {
          // Prefer individual part glossary_id, fallback to system-level
          const partGid = matchedPart.glossary_id;
          const gids = partGid ? [partGid] : (sys.glossary_ids || []);
          meshLink = {
            glossary_ids: gids,
            meshes_l9: sys.meshes_l9 || [],
            group: sys.group,
            system_en: sys.en,
          };
          break;
        }
      }
    }
  } catch (_) { /* ignore */ }

  // Build detail view
  const diagramSrc = part?.diagram_image ? (PARTS_IMG_BASE + '/' + part.diagram_image) : '';
  const sourceSrc = part?.source_image ? (PARTS_IMG_BASE + '/' + part.source_image) : '';
  const displayName = part ? _partDisplayName(part) : (nameZh || partNumber);

  let html = `
    <div style="display:flex;align-items:center;gap:8px;padding:4px 0;">
      <button id="kb-part-detail-back" style="background:none;border:none;cursor:pointer;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      <span style="font-size:14px;font-weight:600;color:var(--text-primary);">Деталь компонента</span>
    </div>

    ${diagramSrc ? `<div style="margin:12px 0;border-radius:12px;overflow:hidden;border:1px solid var(--border-default);background:var(--bg-secondary);text-align:center;padding:8px;min-height:200px;">
        <img src="${diagramSrc}" alt="Диаграмма каталога" style="width:100%;max-height:500px;object-fit:contain;display:inline-block;cursor:pointer;border-radius:8px;" id="kb-part-img" onerror="this.parentElement.style.display='none'" />
      </div>` : ''}
    ${!diagramSrc && sourceSrc ? `<div style="margin:12px 0;border-radius:12px;overflow:hidden;border:1px solid var(--border-default);background:var(--bg-secondary);text-align:center;padding:8px;min-height:200px;">
        <img src="${sourceSrc}" alt="Таблица каталога" style="width:100%;max-height:500px;object-fit:contain;display:inline-block;cursor:pointer;border-radius:8px;" id="kb-part-img" onerror="this.parentElement.style.display='none'" />
      </div>` : ''}

    <div style="background:var(--bg-secondary);border-radius:12px;padding:16px;margin:8px 0;">
      <div style="font-size:16px;font-weight:600;color:var(--text-primary);margin-bottom:8px;">${displayName}</div>
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
        <span style="font-family:monospace;font-size:13px;color:var(--accent-primary);font-weight:600;background:rgba(0,200,150,0.1);padding:4px 10px;border-radius:6px;">${partNumber}</span>
        ${part?.hotspot_id ? `<span style="font-size:11px;color:var(--text-tertiary);background:var(--bg-tertiary);padding:4px 10px;border-radius:6px;">№ ${part.hotspot_id}</span>` : ''}
      </div>
      <div style="display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--text-secondary);">
        ${part?.system_en ? `<div><span style="color:var(--text-tertiary);">Система:</span> ${_i18n?.lang === 'zh' ? (part.system_zh || part.system_en) : _sysNameFromEn(part.system_en)}</div>` : ''}
        ${part?.subsystem_en ? `<div><span style="color:var(--text-tertiary);">Подсистема:</span> ${_i18n?.lang === 'zh' ? (part.subsystem_zh || part.subsystem_en) : (part.subsystem_ru || part.subsystem_en)}</div>` : ''}
        ${(part?.page_idx != null && part.page_idx > 1) ? `<div><span style="color:var(--text-tertiary);">Стр.:</span> ${part.page_idx}</div>` : ''}
      </div>
    </div>

    ${meshLink && meshLink.glossary_ids.length > 0 ? `
    <button class="kb-3d-link" data-glossary="${meshLink.glossary_ids[0]}" style="display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:10px 16px;background:var(--accent-primary);color:white;border:none;border-radius:var(--radius-md);cursor:pointer;font-size:13px;font-weight:500;margin:8px 0;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
      Показать в 3D
    </button>
    ` : meshLink?.group ? `
    <button class="kb-3d-region-link" data-group="${meshLink.group}" style="display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:10px 16px;background:var(--bg-tertiary);color:var(--text-secondary);border:1px solid var(--border-default);border-radius:var(--radius-md);cursor:pointer;font-size:13px;font-weight:500;margin:8px 0;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
      Показать область в 3D
    </button>
    ` : ''}
  `;

  // Related KB articles (localized)
  const localizedRelated = relatedArticles.map(e => getLocalizedEntry(e));
  if (localizedRelated.length > 0) {
    html += `<div style="font-size:12px;font-weight:600;color:var(--text-secondary);padding:12px 0 6px 0;">Связанные статьи (${localizedRelated.length})</div>`;
    html += localizedRelated.map(entry => renderArticleCard(entry)).join('');
  } else {
    html += `<div style="text-align:center;padding:20px 0;color:var(--text-tertiary);font-size:12px;">Связанных статей не найдено</div>`;
  }

  resultsEl.innerHTML = html;

  // Back button → go back to subsystems view
  resultsEl.querySelector('#kb-part-detail-back')?.addEventListener('click', async () => {
    if (parentSystem) {
      await renderSubsystemsView(resultsEl, parentSystem);
    } else {
      activeCategory = 'parts';
      renderResults();
    }
  });

  // 3D links — navigate to Digital Twin (specific component)
  resultsEl.querySelectorAll('.kb-3d-link').forEach(el => {
    el.addEventListener('click', () => {
      const gid = el.dataset.glossary;
      if (gid) {
        window.__llcar_selectedComponent = gid;
        emit('app:navigate', { screen: 'twin' });
        setTimeout(() => emit('component:select', { glossaryId: gid, source: 'kb' }), 300);
      }
    });
  });

  // Regional 3D link — highlight entire group
  resultsEl.querySelectorAll('.kb-3d-region-link').forEach(el => {
    el.addEventListener('click', () => {
      const group = el.dataset.group;
      if (group) {
        window.__llcar_selectedGroup = group;
        emit('app:navigate', { screen: 'twin' });
        setTimeout(() => emit('region:select', { group, source: 'kb' }), 300);
      }
    });
  });

  // Click image → open full size in new tab
  const imgEl = resultsEl.querySelector('#kb-part-img');
  if (imgEl) {
    imgEl.addEventListener('click', () => window.open(imgEl.src, '_blank'));
  }

  // Bind clicks on related article cards
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

// ── Extract meaningful title from generic-titled entries ──
const _GENERIC_TITLES = new Set([
  'предупреждение', 'warning', '警告', 'внимание', 'примечание',
  'note', '注意', '提示', '用户手册', '用车场景', 'caution'
]);

function _extractTitle(entry) {
  let title = (entry.title || '').trim();
  // Strip roman numerals: "I. ", "XI. ", "III. "
  title = title.replace(/^[IVXLCDM]+\.\s+/, '');
  const titleLower = title.toLowerCase().trim();

  if (!_GENERIC_TITLES.has(titleLower) || !entry.content) return title;

  // Extract the ESSENCE — topic/subject from content, not just first chars
  let text = entry.content;
  // Remove the title word itself from content start (with markdown headers)
  text = text.replace(/^#{0,3}\s*(Предупреждение|Warning|Примечание|Внимание|Caution|注意|警告|提示)\s*/i, '');
  // Clean up noise
  text = text.replace(/\n/g, ' ')
    .replace(/<[^>]+>/g, '')         // HTML tags
    .replace(/\$[^$]*\$/g, '')       // LaTeX
    .replace(/!\[.*?\]\(.*?\)/g, '') // markdown images
    .replace(/#{1,3}\s*/g, '')       // markdown headers
    .replace(/^[●•▪▸\-–—\d\.\)\s]+/, '')  // bullet markers, numbering at start
    .replace(/\s{2,}/g, ' ')
    .trim();

  if (text.length < 10) return title;

  // Strategy: extract the SUBJECT/TOPIC, not full sentence
  // 1. Find first complete sentence (up to 100 chars)
  const sentenceEnd = text.match(/^(.{15,100}?[.!。])\s/);
  if (sentenceEnd) {
    let sent = sentenceEnd[1];
    // If sentence is long, try to shorten to a key phrase (before comma/dash)
    if (sent.length > 70) {
      const commaIdx = sent.indexOf(',', 25);
      if (commaIdx > 25 && commaIdx < 70) {
        sent = sent.slice(0, commaIdx);
      }
    }
    return sent;
  }

  // 2. No sentence end — try key phrase before comma/semicolon/dash
  const shortPhrase = text.match(/^(.{15,70}?)[,;—–]/);
  if (shortPhrase) {
    let phrase = shortPhrase[1].trim();
    phrase = phrase.charAt(0).toUpperCase() + phrase.slice(1);
    // Remove trailing short prepositions
    phrase = phrase.replace(/\s+(в|на|и|или|с|к|от|по|для|при|из|за|без|до)$/i, '');
    if (phrase.length >= 15) return phrase;
  }

  // 3. No boundary — take first 70 chars at word boundary
  if (text.length <= 70) return text;
  const cut = text.lastIndexOf(' ', 70);
  return text.slice(0, cut > 25 ? cut : 70) + '…';
}

// ── Deduplicate DTC entries by code, prefer descriptive title ──
function _deduplicateDTC(entries) {
  if (!entries || entries.length <= 1) return entries;
  const byCode = new Map(); // dtc_code → best entry
  for (const entry of entries) {
    const code = entry.dtc_codes?.[0] || _extractDTCCode(entry.title) || '';
    if (!code) { continue; }
    const existing = byCode.get(code);
    if (!existing) {
      byCode.set(code, entry);
    } else {
      // Prefer entry with longer, more descriptive title (not just "Код неисправности: PXXXX")
      const existTitle = existing.title || '';
      const newTitle = entry.title || '';
      const existHasDesc = existTitle.length > code.length + 20;
      const newHasDesc = newTitle.length > code.length + 20;
      if (newHasDesc && !existHasDesc) byCode.set(code, entry);
      // If both have descriptions, prefer Russian source
      else if (newHasDesc && existHasDesc && entry.source_language === 'ru' && existing.source_language !== 'ru') byCode.set(code, entry);
    }
  }
  return [...byCode.values()];
}

function _extractDTCCode(title) {
  if (!title) return null;
  const m = title.match(/[PCBU]\d{4,5}/i);
  return m ? m[0].toUpperCase() : null;
}

// ── Deduplicate results by content similarity ──
function _deduplicateResults(entries) {
  if (!entries || entries.length <= 1) return entries;
  const result = [];
  const fingerprints = []; // stored for similarity comparison

  for (const entry of entries) {
    // Create a normalized fingerprint: extract key words from first 200 chars
    const raw = (entry.content || '').replace(/\s+/g, ' ').trim().slice(0, 200);
    // Extract significant words (3+ chars, skip common words)
    const words = raw.toLowerCase()
      .replace(/[●•▪▸\-–—\d\.\)\(\[\]:,;!?。]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length >= 3);
    const wordSet = new Set(words.slice(0, 30));

    // Check similarity with existing entries
    let isDuplicate = false;
    for (const existing of fingerprints) {
      // Jaccard similarity: intersection / union
      let intersection = 0;
      for (const w of wordSet) {
        if (existing.has(w)) intersection++;
      }
      const union = wordSet.size + existing.size - intersection;
      if (union > 0 && intersection / union > 0.6) {
        isDuplicate = true;
        break;
      }
    }

    if (!isDuplicate) {
      fingerprints.push(wordSet);
      result.push(entry);
    }
  }
  return result;
}

function renderArticleCard(entry) {
  const color = LAYER_COLORS[entry.layer] || '#8B949E';
  const vehicleLabel = entry.model === 'l9' ? 'L9' : entry.model === 'l7' ? 'L7' : 'All';
  const pageInfo = (entry.page_start && entry.page_start > 1) ? `p.${entry.page_start}` : '';

  // Если заголовок слишком общий — извлечь суть из контента
  let displayTitle = _extractTitle(entry);
  entry = { ...entry, title: displayTitle };

  // ── Urgency / Emergency styling ──
  const isEmergency = (entry.urgency || 1) >= 4;
  const emergencyStyle = isEmergency
    ? 'border:2px solid #EF5350;background:rgba(239,83,80,0.08);'
    : '';
  const emergencyStripe = isEmergency ? '#EF5350' : color;

  // ── Trust level dots (1-5) ──
  const trustLevel = entry.trust_level || 2;
  const trustDots = Array.from({length: 5}, (_, i) =>
    i < trustLevel ? '\u25CF' : '\u25CB'
  ).join('');
  const trustLabels = { 5: 'Офиц. мануал', 4: 'Мануал (перевод)', 3: 'СМИ', 2: 'Веб', 1: 'Не верифиц.' };
  const trustLabel = trustLabels[trustLevel] || '';
  const trustBadge = `<span style="font-size:10px;color:var(--text-tertiary);letter-spacing:-1px;" title="${trustLabel}">${trustDots} ${trustLabel}</span>`;

  // ── Situation type badge ──
  const sitTypeConfig = {
    emergency:      { text: '\u26A0 Опасность',    color: '#EF5350', bg: 'rgba(239,83,80,0.12)' },
    troubleshooting:{ text: '\u{1F50D} Неисправность', color: '#FFA726', bg: 'rgba(255,167,38,0.12)' },
    maintenance:    { text: '\u{1F527} Процедура',  color: '#42A5F5', bg: 'rgba(66,165,245,0.12)' },
    specification:  { text: '\u{1F4CB} Спец.',       color: '#78909C', bg: 'rgba(120,144,156,0.12)' },
    learning:       { text: '',             color: '', bg: '' },
  };
  const sitConf = sitTypeConfig[entry.situation_type] || sitTypeConfig.learning;
  const sitBadge = sitConf.text
    ? `<span style="font-size:10px;color:${sitConf.color};background:${sitConf.bg};padding:1px 6px;border-radius:10px;">${sitConf.text}</span>`
    : '';

  // ── Translation badge ──
  const userLang = _i18n?.currentLang || 'ru';
  const srcLang = entry.source_language || '';
  const translationBadge = (srcLang && srcLang !== userLang)
    ? `<span style="font-size:9px;color:#F9A825;background:rgba(249,168,37,0.12);padding:1px 5px;border-radius:8px;">${(srcLang || '').toUpperCase()}\u2192${userLang.toUpperCase()}</span>`
    : '';

  // ── Source badge ──
  const srcInfo = SOURCE_BADGES[entry.source] || { icon: '\u{1F4C4}', label: entry.source };
  const sourceBadge = `<span style="font-size:10px;color:var(--text-tertiary);background:var(--surface-tertiary, rgba(0,0,0,0.04));padding:1px 6px;border-radius:10px;">${srcInfo.icon} ${srcInfo.label}</span>`;

  // Язык
  const langBadge = entry.source_language ? `<span style="font-size:10px;color:var(--text-tertiary);">${LANG_FLAGS[entry.source_language] || entry.source_language}</span>` : '';

  // DTC коды
  let dtcBadges = '';
  if (entry.dtc_codes?.length > 0) {
    dtcBadges = entry.dtc_codes.slice(0, 3).map(dtc =>
      `<span style="font-size:10px;color:${color};background:${color}15;padding:1px 5px;border-radius:8px;">${dtc}</span>`
    ).join('');
  }

  // Score (релевантность)
  const scoreBar = entry.score != null
    ? `<div style="width:30px;height:3px;border-radius:2px;background:var(--border-default);overflow:hidden;flex-shrink:0;">
        <div style="width:${Math.min(100, Math.round(entry.score * 100))}%;height:100%;background:${color};border-radius:2px;"></div>
       </div>` : '';

  return `
    <div class="kb-content-item" data-entry-id="${entry.chunk_id}" style="cursor:pointer;${emergencyStyle}">
      <div style="width:4px;height:100%;min-height:36px;border-radius:2px;background:${emergencyStripe};flex-shrink:0;" title="${t(`layers.${entry.layer}`, entry.layer || '')}"></div>
      <div class="kb-content-item__info" style="flex:1;min-width:0;">
        <span class="kb-content-item__title">${entry.title}</span>
        <span class="kb-content-item__subtitle" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <span>${vehicleLabel}</span>
          ${trustBadge}
          ${translationBadge}
          ${pageInfo ? `<span>&bull;</span><span>${pageInfo}</span>` : ''}
          ${sourceBadge}
          ${sitBadge}
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
    all: t('knowledge.all', 'Все'),
    systems: t('knowledge.systems', 'Системы'),
    parts: t('knowledge.parts', 'Компоненты'),
    manuals: t('knowledge.manuals', 'Руководства'),
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
      selectedComponentData = null;
      // Сброс поиска при переключении вкладки
      searchQuery = '';
      const input = _container?.querySelector('#kb-search-input');
      if (input) input.value = '';
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

  // Переключатель персоны: Новичок → knowledge-v2
  _container?.querySelectorAll('#kb-persona-switch .kbv2-persona-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const persona = btn.dataset.persona;
      localStorage.setItem('llcar-persona', persona);
      if (persona === 'beginner') {
        emit('app:navigate', { screen: 'knowledge-v2' });
      }
    });
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
  _bindCompTags(resultsEl);
}

async function findEntryById(id) {
  // Пробуем найти в кэше (_Cache._m — внутренняя Map)
  if (_kb?._cache?._m) {
    for (const [, cached] of _kb._cache._m) {
      const items = cached.v?.results;
      if (Array.isArray(items)) {
        const found = items.find(e => e.chunk_id === id);
        if (found) return found;
      }
    }
  }
  // Запрос к API по chunk_id напрямую
  const chunk = await _kb.getChunk(id);
  if (chunk) return chunk;
  // Фоллбэк: поиск по ID как текстовому запросу
  const resp = await _kb.search(id, {}, 1);
  return resp.results?.[0] || null;
}

// ── Glossary term translation (EN → RU) ──
const _GLOSSARY_RU = {
  'brake': 'Тормоз', 'brake pedal': 'Педаль тормоза', 'brake system': 'Тормозная система',
  'steering wheel': 'Рулевое колесо', 'seat belt': 'Ремень безопасности', 'safety belt': 'Ремень безопасности',
  'airbag': 'Подушка безопасности', 'sensor': 'Датчик', 'side mirror': 'Боковое зеркало',
  'rear view mirror': 'Зеркало заднего вида', 'windshield': 'Лобовое стекло', 'windshield windscreen': 'Лобовое стекло',
  'ambient lighting': 'Подсветка салона', 'charging port': 'Зарядный порт',
  'range extender': 'Расширитель запаса хода', 'range extender rex': 'Расширитель запаса хода (REX)',
  'traction battery hv battery': 'Тяговая батарея (HV)', 'smart key': 'Смарт-ключ',
  'smart key key fob': 'Смарт-ключ / брелок', 'smart key proximity key keyless entry fob': 'Бесключевой доступ',
  'lane keep assist lka': 'Удержание в полосе (LKA)', 'lane keep assist': 'Удержание в полосе',
  'turn signal indicator': 'Указатель поворота', 'turn signal': 'Указатель поворота',
  'hud head up display': 'Проекционный дисплей (HUD)', 'low beam dipped beam': 'Ближний свет',
  'air conditioning system': 'Система кондиционирования', 'obstacle': 'Препятствие',
  'pedal': 'Педаль', 'speed': 'Скорость', 'velocity': 'Скорость',
  'automatic gearbox informal': 'АКПП',
  'accumulator': 'Аккумулятор', 'voltage': 'Напряжение', 'battery': 'Батарея',
  'tire': 'Шина', 'tyre': 'Шина', 'wheel': 'Колесо', 'suspension': 'Подвеска',
  'engine': 'Двигатель', 'motor': 'Мотор', 'coolant': 'Охлаждающая жидкость',
  'radiator': 'Радиатор', 'headlight': 'Фара', 'taillight': 'Задний фонарь',
  'door': 'Дверь', 'window': 'Стекло', 'roof': 'Крыша', 'trunk': 'Багажник',
  'horn': 'Звуковой сигнал', 'wiper': 'Стеклоочиститель', 'mirror': 'Зеркало',
  'camera': 'Камера', 'radar': 'Радар', 'lidar': 'Лидар',
  'fuse': 'Предохранитель', 'relay': 'Реле', 'connector': 'Разъём',
};
// WHITELIST approach: show ONLY terms that have Russian translation
// Anything not in _GLOSSARY_RU is hidden (no English fallback)
function _renderGlossaryTags(terms, color) {
  if (!terms || terms.length === 0) return '';
  const seen = new Set();
  const rendered = [];
  for (const tag of terms) {
    const raw = tag.split('@')[0].replace(/_/g, ' ').toLowerCase().trim();
    const label = _GLOSSARY_RU[raw];
    if (!label) continue; // skip unknown terms — no English in UI
    if (seen.has(label)) continue; // dedup by translated label
    seen.add(label);
    rendered.push(`<span class="kb-comp-tag" data-gid="${tag}" style="cursor:pointer;font-size:11px;padding:2px 8px;border-radius:10px;background:${color}20;color:${color};border:1px solid ${color}40;white-space:nowrap;">${label}</span>`);
  }
  return rendered.join('');
}

// Маппинг glossary term → система каталога запчастей (для перехода к диаграммам)
const _TERM_TO_SYSTEM = {
  'brake': 'Service Brake System', 'brake pedal': 'Service Brake System', 'brake system': 'Service Brake System',
  'steering wheel': 'Steering System',
  'seat belt': 'Passive Safety System', 'safety belt': 'Passive Safety System', 'airbag': 'Passive Safety System',
  'sensor': 'Autonomous Driving System', 'camera': 'Autonomous Driving System', 'radar': 'Autonomous Driving System', 'lidar': 'Autonomous Driving System',
  'side mirror': 'Exterior Trim System', 'rear view mirror': 'Exterior Trim System', 'mirror': 'Exterior Trim System',
  'windshield': 'Body Structure', 'windshield windscreen': 'Body Structure',
  'ambient lighting': 'Lighting System', 'headlight': 'Lighting System', 'taillight': 'Lighting System', 'low beam dipped beam': 'Lighting System', 'turn signal': 'Lighting System', 'turn signal indicator': 'Lighting System',
  'charging port': 'Power Battery System', 'traction battery hv battery': 'Power Battery System', 'accumulator': 'Power Battery System', 'battery': 'Power Battery System', 'voltage': 'Power Battery System',
  'range extender': 'Engine Assembly', 'range extender rex': 'Engine Assembly', 'engine': 'Engine Assembly', 'motor': 'Power Drive System', 'coolant': 'Engine Assembly', 'radiator': 'Engine Assembly',
  'smart key': 'Smart Cabin / Infotainment', 'smart key key fob': 'Smart Cabin / Infotainment', 'smart key proximity key keyless entry fob': 'Smart Cabin / Infotainment', 'hud head up display': 'Smart Cabin / Infotainment',
  'lane keep assist lka': 'Autonomous Driving System', 'lane keep assist': 'Autonomous Driving System',
  'air conditioning system': 'HVAC & Thermal Management',
  'pedal': 'Service Brake System', 'suspension': 'Front Suspension',
  'tire': 'Front Suspension', 'tyre': 'Front Suspension', 'wheel': 'Front Suspension',
  'door': 'Closures (Doors, Hood, Tailgate)', 'window': 'Closures (Doors, Hood, Tailgate)', 'trunk': 'Closures (Doors, Hood, Tailgate)', 'roof': 'Body Structure',
  'horn': 'Power & Signal Distribution', 'wiper': 'Exterior Trim System',
  'fuse': 'Power & Signal Distribution', 'relay': 'Power & Signal Distribution', 'connector': 'Power & Signal Distribution',
  'automatic gearbox informal': 'Power Drive System',
};

/** Bind click handlers on glossary component tags → open component view with diagram */
function _bindCompTags(container) {
  container?.querySelectorAll('.kb-comp-tag[data-gid]').forEach(el => {
    el.addEventListener('click', (ev) => {
      ev.stopPropagation();
      const gid = el.dataset.gid;
      if (!gid) return;
      const raw = gid.split('@')[0].replace(/_/g, ' ').toLowerCase().trim();
      const system = _TERM_TO_SYSTEM[raw];
      if (system) {
        // Переход к диаграмме системы каталога запчастей
        const resultsEl = _container?.querySelector('#kb-results');
        if (resultsEl) renderSubsystemsView(resultsEl, system);
      } else {
        // Fallback: текстовый поиск
        const ruLabel = _GLOSSARY_RU[raw] || raw;
        activeCategory = 'all';
        searchQuery = ruLabel;
        const input = _container?.querySelector('#kb-search-input');
        if (input) input.value = ruLabel;
        selectedComponentTags = [];
        selectedComponentData = null;
        updateTagFilter();
        renderContent();
      }
    });
  });
}

// ═══════════════════════════════════════════════════════════
// Article Detail
// ═══════════════════════════════════════════════════════════

function renderArticleDetail(entry) {
  const resultsEl = _container?.querySelector('#kb-results');
  if (!resultsEl) return;

  // Локализация
  entry = getLocalizedEntry(entry);

  const color = LAYER_COLORS[entry.layer] || '#8B949E';
  const vehicleLabel = entry.model === 'l9' ? 'Li L9' : entry.model === 'l7' ? 'Li L7' : 'All';
  const pageInfo = (entry.page_start && entry.page_start > 1) ? `p. ${entry.page_start}` : '';
  const srcInfo = SOURCE_BADGES[entry.source] || { icon: '\u{1F4C4}', label: entry.source };

  // Экстренность
  const isEmergency = (entry.urgency || 1) >= 4;
  const emergencyBanner = isEmergency
    ? `<div style="background:rgba(239,83,80,0.1);border:1px solid #EF5350;border-radius:var(--radius-md);padding:10px 14px;display:flex;align-items:center;gap:8px;">
        <span style="font-size:18px;">\u26A0\uFE0F</span>
        <span style="font-size:13px;color:#EF5350;font-weight:600;">Внимание! Критическая информация по безопасности</span>
       </div>` : '';

  // Trust dots
  const trustLevel = entry.trust_level || 2;
  const trustDots = Array.from({length: 5}, (_, i) => i < trustLevel ? '\u25CF' : '\u25CB').join('');
  const trustLabels = { 5: 'Офиц. мануал', 4: 'Мануал (перевод)', 3: 'СМИ', 2: 'Веб-источник', 1: 'Не верифицировано' };
  const trustText = trustLabels[trustLevel] || '';

  // Бейдж перевода
  const userLang = _i18n?.currentLang || _i18n?.lang || 'ru';
  const srcLang = entry.source_language || '';
  const translationNote = (srcLang && srcLang !== userLang)
    ? `<span style="font-size:11px;color:#F9A825;background:rgba(249,168,37,0.12);padding:2px 8px;border-radius:10px;">${srcLang.toUpperCase()}\u2192${userLang.toUpperCase()} ${entry._translated ? 'Перевод' : 'Оригинал'}</span>`
    : '';

  // Теги glossary_terms (перевод + дедупликация) + fallback по layer
  let _compTerms = entry.glossary_terms?.length > 0 ? entry.glossary_terms : [];
  if (_compTerms.length === 0 && entry.layer) {
    // Fallback: подбираем компоненты по layer из _GLOSSARY_RU
    const layerTerms = [];
    for (const key of Object.keys(_GLOSSARY_RU)) {
      layerTerms.push(`${key.replace(/ /g, '_')}@${entry.layer}`);
    }
    _compTerms = layerTerms.slice(0, 15);
  }
  const tags = _renderGlossaryTags(_compTerms, color);

  // DTC коды
  const dtcHtml = (entry.dtc_codes?.length > 0) ? `
    <div style="display:flex;flex-wrap:wrap;gap:6px;">
      ${entry.dtc_codes.map(dtc => `<span class="kb-dtc-badge" data-dtc="${dtc}" style="cursor:pointer;font-size:12px;padding:3px 10px;border-radius:12px;background:${color}15;color:${color};border:1px solid ${color}30;font-weight:500;">${dtc}</span>`).join('')}
    </div>` : '';

  // Situation type badge
  const sitLabels = {
    emergency: '\u26A0 Опасность', troubleshooting: '\u{1F50D} Диагностика',
    maintenance: '\u{1F527} Процедура', specification: '\u{1F4CB} Спецификация', learning: '\u{1F4D6} Справка',
  };
  const sitLabel = sitLabels[entry.situation_type] || '';

  let badges = '';
  if (entry.has_procedures) {
    badges += '<span style="font-size:11px;color:var(--accent-primary);background:var(--accent-primary-dim);padding:2px 8px;border-radius:10px;">Пошаговая инструкция</span>';
  }
  if (entry.has_warnings) {
    badges += '<span style="font-size:11px;color:var(--status-warning);background:var(--warning-bg);padding:2px 8px;border-radius:10px;">Предупреждение</span>';
  }

  // Ссылка на источник
  const sourceLink = entry.source_url
    ? `<a href="${entry.source_url}" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:var(--accent-primary);text-decoration:none;">
        ${srcInfo.icon} ${t('knowledge.open_source', 'Открыть источник')} &rarr;
       </a>` : '';

  resultsEl.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:16px;">
      <button id="kb-detail-back" style="display:flex;align-items:center;gap:6px;background:none;border:none;cursor:pointer;padding:4px 0;color:var(--text-secondary);font-size:13px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
        ${t('knowledge.back_to_results', 'Назад к результатам')}
      </button>

      ${emergencyBanner}

      <div style="display:flex;gap:12px;align-items:flex-start;">
        <div style="width:4px;min-height:48px;border-radius:2px;background:${isEmergency ? '#EF5350' : color};flex-shrink:0;margin-top:2px;"></div>
        <div style="flex:1;">
          <h3 style="font-size:16px;font-weight:600;color:var(--text-primary);margin:0 0 8px 0;line-height:1.3;">${entry.title}</h3>
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span style="font-size:12px;color:var(--text-secondary);">${vehicleLabel}</span>
            <span style="font-size:11px;color:var(--text-tertiary);letter-spacing:-1px;" title="${trustText}">${trustDots}</span>
            <span style="font-size:11px;color:var(--text-tertiary);">${trustText}</span>
            ${translationNote}
            ${pageInfo ? `<span style="font-size:12px;color:var(--text-tertiary);">&bull; ${pageInfo}</span>` : ''}
            <span style="font-size:11px;color:var(--text-tertiary);">${srcInfo.icon} ${srcInfo.label}</span>
            ${sitLabel ? `<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:var(--surface-tertiary);">${sitLabel}</span>` : ''}
            ${badges}
          </div>
        </div>
      </div>

      <div style="background:var(--surface-secondary);border-radius:var(--radius-md);border:1px solid ${isEmergency ? '#EF5350' : 'var(--border-default)'};overflow:hidden;">
        <div class="kb-detail-content" style="font-size:13px;color:var(--text-secondary);line-height:1.6;padding:12px;">${renderMarkdown(entry.content || entry.preview || 'No content')}</div>
      </div>

      ${dtcHtml}
      ${tags ? `<div style="display:flex;flex-wrap:wrap;gap:6px;max-height:60px;overflow-y:auto;">${tags}</div>` : ''}
      ${sourceLink}

      ${(entry.glossary_terms?.length > 0) ? `
        <button id="kb-show-in-3d" data-tag="${entry.glossary_terms[0]}" style="display:flex;align-items:center;justify-content:center;gap:8px;padding:10px 16px;background:var(--accent-primary);color:white;border:none;border-radius:var(--radius-md);cursor:pointer;font-size:13px;font-weight:500;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.3 7 12 12 20.7 7"/><line x1="12" y1="22" x2="12" y2="12"/></svg>
          ${t('knowledge.show_in_3d', 'Показать в 3D')}
        </button>
      ` : ''}

      <!-- Связанные статьи (загружаются асинхронно) -->
      <div id="kb-related-articles" style="display:flex;flex-direction:column;gap:8px;">
        <span style="font-size:13px;font-weight:600;color:var(--text-secondary);">Связанные статьи</span>
        <div style="color:var(--text-tertiary);font-size:12px;">Загрузка...</div>
      </div>
    </div>
  `;

  // Загрузить связанные статьи
  _loadRelatedArticles(entry, resultsEl);

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

  // Bind component tags in article detail
  _bindCompTags(resultsEl);
}

/** Загрузить и показать связанные статьи + ссылки на компоненты */
async function _loadRelatedArticles(entry, resultsEl) {
  const relEl = resultsEl.querySelector('#kb-related-articles');
  if (!relEl || !_kb) return;

  let html = `<span style="font-size:13px;font-weight:600;color:var(--text-secondary);">Связанные статьи</span>`;

  // 1. Ссылки на компоненты (parts) — по glossary_terms (только переведённые)
  let _relTerms = entry.glossary_terms?.length > 0 ? entry.glossary_terms : [];
  if (_relTerms.length === 0 && entry.layer) {
    for (const key of Object.keys(_GLOSSARY_RU)) {
      _relTerms.push(`${key.replace(/ /g, '_')}@${entry.layer}`);
    }
    _relTerms = _relTerms.slice(0, 10);
  }
  if (_relTerms.length > 0) {
    const seen = new Set();
    let partCount = 0;
    for (const term of _relTerms) {
      if (partCount >= 4) break;
      const raw = term.split('@')[0].replace(/_/g, ' ').toLowerCase().trim();
      const label = _GLOSSARY_RU[raw];
      if (!label || seen.has(label)) continue; // whitelist only
      seen.add(label);
      const layer = term.split('@')[1] || entry.layer || '';
      const layerLabel = t(`layers.${layer}`, layer);
      html += `
        <div class="kb-related-part" data-term="${term}" style="cursor:pointer;display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:var(--radius-md);border:1px solid var(--border-default);background:var(--surface-secondary);">
          <span style="font-size:16px;">\u{1F527}</span>
          <div style="flex:1;">
            <span style="font-size:13px;color:var(--text-primary);font-weight:500;">${label}</span>
            <span style="font-size:11px;color:var(--text-tertiary);display:block;">${layerLabel} \u2192 Компоненты</span>
          </div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round"><path d="m9 18 6-6-6-6"/></svg>
        </div>`;
      partCount++;
    }
  }

  // 2. Связанные DTC коды → поиск по ним
  if (entry.dtc_codes?.length > 0) {
    for (const dtc of entry.dtc_codes.slice(0, 3)) {
      html += `
        <div class="kb-related-dtc" data-dtc="${dtc}" style="cursor:pointer;display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:var(--radius-md);border:1px solid var(--border-default);background:var(--surface-secondary);">
          <span style="font-size:16px;">⚠️</span>
          <div style="flex:1;">
            <span style="font-size:13px;color:var(--text-primary);font-weight:500;">${dtc}</span>
            <span style="font-size:11px;color:var(--text-tertiary);display:block;">Код ошибки → DTC</span>
          </div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round"><path d="m9 18 6-6-6-6"/></svg>
        </div>`;
    }
  }

  // 3. Другие статьи в том же слое (browse top-5, excluding current)
  try {
    const resp = await _kb.browse(entry.layer, { model: entry.model || activeVehicle || undefined }, 6);
    const related = (resp.results || [])
      .filter(r => r.chunk_id !== entry.chunk_id)
      .slice(0, 4)
      .map(e => getLocalizedEntry(e));

    if (related.length > 0) {
      const layerLabel = t(`layers.${entry.layer}`, entry.layer || '');
      html += `<span style="font-size:12px;color:var(--text-tertiary);padding:4px 0 0 0;">Ещё в разделе «${layerLabel}»:</span>`;
      html += related.map(r => renderArticleCard(r)).join('');
    }
  } catch {}

  relEl.innerHTML = html;

  // Клик по компоненту → переход в parts
  relEl.querySelectorAll('.kb-related-part').forEach(el => {
    el.addEventListener('click', () => {
      const term = el.dataset.term;
      const raw = term.split('@')[0].replace(/_/g, ' ').toLowerCase().trim();
      // Use Russian translation for search, fallback to English term
      const ruLabel = _GLOSSARY_RU[raw];
      activeCategory = 'parts';
      searchQuery = ruLabel || raw;
      renderContent();
    });
  });

  // Клик по DTC → поиск
  relEl.querySelectorAll('.kb-related-dtc').forEach(el => {
    el.addEventListener('click', () => {
      activeCategory = 'dtc';
      searchQuery = el.dataset.dtc;
      renderContent();
    });
  });

  // Клик по связанной статье
  bindResultEvents(relEl);
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
      const raw = gid.split('@')[0].replace(/_/g, ' ').toLowerCase().trim();
      const ruLabel = _GLOSSARY_RU[raw];
      if (ruLabel) return ruLabel;
      if (_i18n) {
        const i18nName = _i18n.getComponentName(gid);
        if (i18nName && i18nName !== gid) return i18nName;
      }
      return raw;
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
    selectedComponentData = {
      glossaryId: detail.glossaryId,
      dtcCodes: detail.component?.dtcCodes || [],
      category: detail.component?.category || '',
      layer: detail.component?.layer || detail.glossaryId.split('@')[1] || '',
    };
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
  // Preserve activeCategory and searchQuery so drill-down state survives screen switches
  selectedComponentTags = [];
  selectedComponentData = null;
  off('component:select', _onComponentSelect);
  off('lang:change', _onLangChange);
  if (_container) _container.innerHTML = '';
}
