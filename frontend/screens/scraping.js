/**
 * LLCAR Diagnostica — Scraping Management Screen
 *
 * GUI для управления web-скрапингом:
 * - Список скраперов со статистикой
 * - Запуск скраперов (по одному или всех)
 * - Просмотр скрапленного контента с фильтрами
 * - Импорт в KB
 * - Удаление мусора
 */

const API_BASE = 'http://localhost:8000';

let _container = null;
let _rendered = false;
let _currentView = 'scrapers';  // 'scrapers' | 'content'
let _contentFilters = { source: '', imported: '', sort: 'newest', page: 1 };
let _scrapersList = [];
let _pollTimers = {};

export function render(container) {
  _container = container;
  if (!_rendered) {
    _container.innerHTML = _buildShell();
    _rendered = true;
  }
  _loadScrapers();
}

export function cleanup() {
  Object.values(_pollTimers).forEach(clearInterval);
  _pollTimers = {};
}

// ── Shell ──────────────────────────────────────────────────────────────

function _buildShell() {
  return `
    <div class="scraping-screen">
      <div class="scraping-header">
        <h1 class="scraping-title">Управление скрапингом</h1>
        <div class="scraping-tabs">
          <button class="scraping-tab scraping-tab--active" data-view="scrapers" onclick="window.__scraping_switchView('scrapers')">
            Скраперы
          </button>
          <button class="scraping-tab" data-view="content" onclick="window.__scraping_switchView('content')">
            Контент
          </button>
        </div>
      </div>
      <div class="scraping-actions-bar">
        <button class="scraping-btn scraping-btn--primary" onclick="window.__scraping_runAll()">
          Запустить все
        </button>
        <button class="scraping-btn scraping-btn--secondary" onclick="window.__scraping_importKB()">
          Импорт в KB
        </button>
        <button class="scraping-btn scraping-btn--ghost" onclick="window.__scraping_refresh()">
          Обновить
        </button>
      </div>
      <div id="scraping-body" class="scraping-body"></div>
    </div>
  `;
}

// ── Global handlers ────────────────────────────────────────────────────

window.__scraping_switchView = (view) => {
  _currentView = view;
  _container.querySelectorAll('.scraping-tab').forEach(t => {
    t.classList.toggle('scraping-tab--active', t.dataset.view === view);
  });
  if (view === 'scrapers') _loadScrapers();
  else { _contentFilters.page = 1; _loadContent(); }
};

window.__scraping_refresh = () => {
  if (_currentView === 'scrapers') _loadScrapers();
  else _loadContent();
};

window.__scraping_runAll = () => _runScraper('all');

window.__scraping_runSingle = (name) => _runScraper(name);

window.__scraping_importKB = async () => {
  const body = document.getElementById('scraping-body');
  body.innerHTML = '<div class="scraping-loading">Импортирую в KB...</div>';
  try {
    const r = await fetch(`${API_BASE}/scrapers/import`, { method: 'POST' });
    const data = await r.json();
    _showNotification(`Импорт завершён: ${data.imported} в KB, ${data.pending} ожидают`);
    _loadScrapers();
  } catch (e) {
    _showNotification('Ошибка импорта: ' + e.message, true);
    _loadScrapers();
  }
};

window.__scraping_deleteItem = async (id) => {
  if (!confirm('Удалить эту запись?')) return;
  try {
    await fetch(`${API_BASE}/scrapers/content/${id}`, { method: 'DELETE' });
    _loadContent();
  } catch (e) {
    _showNotification('Ошибка удаления: ' + e.message, true);
  }
};

window.__scraping_filterSource = (source) => {
  _contentFilters.source = source;
  _contentFilters.page = 1;
  _loadContent();
};

window.__scraping_filterImported = (val) => {
  _contentFilters.imported = val;
  _contentFilters.page = 1;
  _loadContent();
};

window.__scraping_filterSort = (sort) => {
  _contentFilters.sort = sort;
  _loadContent();
};

window.__scraping_goPage = (page) => {
  _contentFilters.page = page;
  _loadContent();
};

// ── Scrapers List ──────────────────────────────────────────────────────

async function _loadScrapers() {
  const body = document.getElementById('scraping-body');
  if (!body) return;
  body.innerHTML = '<div class="scraping-loading">Загрузка...</div>';

  try {
    const r = await fetch(`${API_BASE}/scrapers/list`);
    const data = await r.json();
    _scrapersList = data.scrapers;
    _renderScrapers();
  } catch (e) {
    body.innerHTML = `<div class="scraping-error">
      Ошибка подключения к API: ${e.message}<br>
      <small>Убедитесь, что сервер запущен: uvicorn api.server:app --port 8000</small>
    </div>`;
  }
}

function _renderScrapers() {
  const body = document.getElementById('scraping-body');
  if (!body) return;

  // Summary stats
  const totalItems = _scrapersList.reduce((s, sc) => s + sc.total, 0);
  const totalImported = _scrapersList.reduce((s, sc) => s + sc.imported, 0);
  const activeSources = _scrapersList.filter(sc => sc.total > 0).length;

  let html = `
    <div class="scraping-summary">
      <div class="scraping-stat">
        <div class="scraping-stat__value">${totalItems}</div>
        <div class="scraping-stat__label">Всего записей</div>
      </div>
      <div class="scraping-stat">
        <div class="scraping-stat__value">${totalImported}</div>
        <div class="scraping-stat__label">Импортировано</div>
      </div>
      <div class="scraping-stat">
        <div class="scraping-stat__value">${totalItems - totalImported}</div>
        <div class="scraping-stat__label">Ожидают</div>
      </div>
      <div class="scraping-stat">
        <div class="scraping-stat__value">${activeSources}/${_scrapersList.length}</div>
        <div class="scraping-stat__label">Активных</div>
      </div>
    </div>
    <div class="scraping-list">
  `;

  for (const sc of _scrapersList) {
    const statusClass = sc.status === 'running' ? 'scraping-status--running' :
                        sc.status === 'done' ? 'scraping-status--done' :
                        sc.status === 'error' ? 'scraping-status--error' :
                        'scraping-status--idle';
    const statusText = sc.status === 'running' ? 'Работает...' :
                       sc.status === 'done' ? 'Готово' :
                       sc.status === 'error' ? 'Ошибка' :
                       sc.status === 'timeout' ? 'Таймаут' : 'Ожидание';

    const lastDate = sc.last_scraped ? new Date(sc.last_scraped).toLocaleDateString('ru-RU') : '—';
    const relBar = sc.avg_relevance > 0
      ? `<div class="scraping-rel-bar"><div class="scraping-rel-bar__fill" style="width:${Math.round(sc.avg_relevance * 100)}%;background:${sc.avg_relevance > 0.7 ? '#4caf50' : sc.avg_relevance > 0.4 ? '#ff9800' : '#f44336'}"></div></div>`
      : '<span class="scraping-muted">—</span>';

    html += `
      <div class="scraping-card" data-scraper="${sc.name}">
        <div class="scraping-card__header">
          <div class="scraping-card__name">${sc.name}</div>
          <span class="scraping-card__lang">${sc.lang}</span>
          <span class="scraping-card__status ${statusClass}">${statusText}</span>
        </div>
        <div class="scraping-card__stats">
          <div class="scraping-card__metric">
            <span class="scraping-card__metric-val">${sc.total}</span>
            <span class="scraping-card__metric-lbl">записей</span>
          </div>
          <div class="scraping-card__metric">
            <span class="scraping-card__metric-val">${sc.imported}</span>
            <span class="scraping-card__metric-lbl">в KB</span>
          </div>
          <div class="scraping-card__metric">
            ${relBar}
            <span class="scraping-card__metric-lbl">релевантность</span>
          </div>
          <div class="scraping-card__metric">
            <span class="scraping-card__metric-val">${sc.avg_length > 0 ? Math.round(sc.avg_length / 1000) + 'K' : '—'}</span>
            <span class="scraping-card__metric-lbl">ср. длина</span>
          </div>
          <div class="scraping-card__metric">
            <span class="scraping-card__metric-val">${lastDate}</span>
            <span class="scraping-card__metric-lbl">последний</span>
          </div>
        </div>
        <div class="scraping-card__actions">
          <button class="scraping-btn scraping-btn--small" onclick="window.__scraping_runSingle('${sc.name}')"
                  ${sc.status === 'running' ? 'disabled' : ''}>
            ${sc.status === 'running' ? 'Работает...' : 'Запустить'}
          </button>
          <button class="scraping-btn scraping-btn--small scraping-btn--ghost"
                  onclick="window.__scraping_filterSource('${sc.name}'); window.__scraping_switchView('content')">
            Контент
          </button>
        </div>
      </div>
    `;
  }

  html += '</div>';
  body.innerHTML = html;
}

// ── Run Scraper ────────────────────────────────────────────────────────

async function _runScraper(name) {
  try {
    const r = await fetch(`${API_BASE}/scrapers/run/${name}`, { method: 'POST' });
    const data = await r.json();
    if (data.status === 'already_running') {
      _showNotification(`${name} уже запущен`);
      return;
    }
    _showNotification(`${name}: запущен`);

    // Poll status
    _pollTimers[name] = setInterval(async () => {
      try {
        const sr = await fetch(`${API_BASE}/scrapers/status/${name}`);
        const st = await sr.json();
        if (st.status !== 'running') {
          clearInterval(_pollTimers[name]);
          delete _pollTimers[name];
          if (st.status === 'done') {
            _showNotification(`${name}: завершён`);
          } else {
            _showNotification(`${name}: ${st.status} — ${st.error || ''}`, true);
          }
          _loadScrapers();
        } else {
          // Update card status in DOM
          const card = document.querySelector(`[data-scraper="${name}"]`);
          if (card) {
            const statusEl = card.querySelector('.scraping-card__status');
            if (statusEl) {
              statusEl.className = 'scraping-card__status scraping-status--running';
              statusEl.textContent = 'Работает...';
            }
          }
        }
      } catch (e) { /* ignore poll errors */ }
    }, 3000);

    _loadScrapers();
  } catch (e) {
    _showNotification('Ошибка запуска: ' + e.message, true);
  }
}

// ── Content Browser ────────────────────────────────────────────────────

async function _loadContent() {
  const body = document.getElementById('scraping-body');
  if (!body) return;
  body.innerHTML = '<div class="scraping-loading">Загрузка контента...</div>';

  const f = _contentFilters;
  const params = new URLSearchParams({
    page: f.page,
    per_page: 15,
    sort: f.sort,
  });
  if (f.source) params.set('source', f.source);
  if (f.imported) params.set('imported', f.imported);

  try {
    const r = await fetch(`${API_BASE}/scrapers/content?${params}`);
    const data = await r.json();
    _renderContent(data);
  } catch (e) {
    body.innerHTML = `<div class="scraping-error">Ошибка: ${e.message}</div>`;
  }
}

function _renderContent(data) {
  const body = document.getElementById('scraping-body');
  if (!body) return;

  // Filters bar
  const sources = [...new Set(_scrapersList.map(s => s.name).filter(Boolean))];
  let html = `
    <div class="scraping-filters">
      <select class="scraping-select" onchange="window.__scraping_filterSource(this.value)">
        <option value="">Все источники</option>
        ${sources.map(s => `<option value="${s}" ${s === _contentFilters.source ? 'selected' : ''}>${s}</option>`).join('')}
      </select>
      <select class="scraping-select" onchange="window.__scraping_filterImported(this.value)">
        <option value="" ${_contentFilters.imported === '' ? 'selected' : ''}>Все</option>
        <option value="1" ${_contentFilters.imported === '1' ? 'selected' : ''}>Импортированные</option>
        <option value="0" ${_contentFilters.imported === '0' ? 'selected' : ''}>Неимпортированные</option>
      </select>
      <select class="scraping-select" onchange="window.__scraping_filterSort(this.value)">
        <option value="newest" ${_contentFilters.sort === 'newest' ? 'selected' : ''}>Новые</option>
        <option value="oldest" ${_contentFilters.sort === 'oldest' ? 'selected' : ''}>Старые</option>
        <option value="relevance" ${_contentFilters.sort === 'relevance' ? 'selected' : ''}>Релевантность</option>
        <option value="length" ${_contentFilters.sort === 'length' ? 'selected' : ''}>Длина</option>
      </select>
      <span class="scraping-count">${data.total} записей</span>
    </div>
  `;

  // Content list
  html += '<div class="scraping-content-list">';
  for (const item of data.items) {
    const relColor = (item.relevance || 0) > 0.7 ? '#4caf50' :
                     (item.relevance || 0) > 0.4 ? '#ff9800' : '#f44336';
    const classIcon = {
      'owner_review': 'review',
      'troubleshooting': 'wrench',
      'maintenance': 'tool',
      'specs': 'spec',
      'description': 'doc',
      'guide': 'guide',
      'news': 'news',
    }[item.content_class] || 'doc';

    html += `
      <div class="scraping-content-item ${item.imported ? 'scraping-content-item--imported' : ''}">
        <div class="scraping-content-item__header">
          <span class="scraping-content-item__class" title="${item.content_class || 'unknown'}">${item.content_class || '?'}</span>
          <span class="scraping-content-item__source">${item.source_name}</span>
          <span class="scraping-content-item__lang">${item.lang}</span>
          ${item.imported ? '<span class="scraping-badge scraping-badge--green">KB</span>' : ''}
          <span class="scraping-content-item__rel" style="color:${relColor}">${((item.relevance || 0) * 100).toFixed(0)}%</span>
        </div>
        <div class="scraping-content-item__title">${_escapeHtml(item.title || 'Без заголовка')}</div>
        <div class="scraping-content-item__preview">${_escapeHtml(item.preview || '')}</div>
        <div class="scraping-content-item__footer">
          <span>${(item.content_length / 1000).toFixed(1)}K символов</span>
          <span>${item.scraped_at ? new Date(item.scraped_at).toLocaleDateString('ru-RU') : '—'}</span>
          ${item.dtc_codes ? `<span class="scraping-badge scraping-badge--blue">DTC: ${item.dtc_codes}</span>` : ''}
          <a href="${item.url}" target="_blank" class="scraping-link">Источник</a>
          <button class="scraping-btn scraping-btn--tiny scraping-btn--danger"
                  onclick="window.__scraping_deleteItem(${item.id})">Удалить</button>
        </div>
      </div>
    `;
  }
  html += '</div>';

  // Pagination
  if (data.pages > 1) {
    html += '<div class="scraping-pagination">';
    const p = data.page;
    if (p > 1) html += `<button class="scraping-btn scraping-btn--small" onclick="window.__scraping_goPage(${p - 1})">Назад</button>`;
    html += `<span class="scraping-page-info">Стр. ${p} из ${data.pages}</span>`;
    if (p < data.pages) html += `<button class="scraping-btn scraping-btn--small" onclick="window.__scraping_goPage(${p + 1})">Далее</button>`;
    html += '</div>';
  }

  body.innerHTML = html;
}

// ── Helpers ────────────────────────────────────────────────────────────

function _escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function _showNotification(msg, isError = false) {
  let notif = document.querySelector('.scraping-notification');
  if (!notif) {
    notif = document.createElement('div');
    notif.className = 'scraping-notification';
    document.body.appendChild(notif);
  }
  notif.textContent = msg;
  notif.className = `scraping-notification ${isError ? 'scraping-notification--error' : 'scraping-notification--success'}`;
  notif.style.display = 'block';
  setTimeout(() => { notif.style.display = 'none'; }, 4000);
}
