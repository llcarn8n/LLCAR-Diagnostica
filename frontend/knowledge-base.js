/**
 * LLCAR Diagnostica — Knowledge Base API Client v2
 *
 * Клиент к FastAPI KB серверу v2 (LanceDB + FTS5 + ColBERT).
 * Поддерживает все 8 эндпоинтов: search, semantic, keyword,
 * chunk, dtc, glossary, stats, embed.
 *
 * Использование:
 *   import { KnowledgeBase } from './knowledge-base.js';
 *   const kb = new KnowledgeBase({ apiBase: 'http://localhost:8000' });
 *   await kb.init();
 *   const results = await kb.search('тормоз');
 *   const dtc    = await kb.getDTC('P0300');
 *   const glossary = await kb.glossarySearch('brake');
 */

const DEFAULT_API_BASE = 'http://localhost:8000';
const DEFAULT_TIMEOUT_MS = 8000;
const DEFAULT_CACHE_TTL = 60_000;   // 60 s
const CACHE_MAX_SIZE    = 200;

// ─── Helpers ─────────────────────────────────────────────────────────────────

function _signal(ms) {
  return AbortSignal.timeout ? AbortSignal.timeout(ms) : undefined;
}

async function _post(url, body, timeoutMs) {
  const resp = await fetch(url, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
    signal:  _signal(timeoutMs),
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

async function _get(url, timeoutMs) {
  const resp = await fetch(url, { signal: _signal(timeoutMs) });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

// ─── LRU cache ───────────────────────────────────────────────────────────────

class _Cache {
  constructor(maxSize = CACHE_MAX_SIZE, ttl = DEFAULT_CACHE_TTL) {
    this._m   = new Map();
    this._max = maxSize;
    this._ttl = ttl;
  }

  get(key) {
    const e = this._m.get(key);
    if (!e) return undefined;
    if (Date.now() - e.ts > this._ttl) { this._m.delete(key); return undefined; }
    // LRU: re-insert at tail
    this._m.delete(key);
    this._m.set(key, e);
    return e.v;
  }

  set(key, value) {
    if (this._m.size >= this._max) {
      this._m.delete(this._m.keys().next().value);   // evict oldest
    }
    this._m.set(key, { v: value, ts: Date.now() });
  }

  clear() { this._m.clear(); }
}

// ─── Main class ──────────────────────────────────────────────────────────────

export class KnowledgeBase {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiBase]   URL API сервера (default: http://localhost:8000)
   * @param {string} [opts.brand]     Фильтр бренда (default: 'li_auto')
   * @param {number} [opts.timeout]   Таймаут запроса мс (default: 8000)
   * @param {number} [opts.cacheTtl]  TTL кэша мс      (default: 60000)
   */
  constructor(opts = {}) {
    this._api     = (opts.apiBase || DEFAULT_API_BASE).replace(/\/$/, '');
    this._brand   = opts.brand   || 'li_auto';
    this._timeout = opts.timeout || DEFAULT_TIMEOUT_MS;
    this._cache   = new _Cache(CACHE_MAX_SIZE, opts.cacheTtl || DEFAULT_CACHE_TTL);

    this._online  = false;
    this._loaded  = false;
    this._stats   = null;
    this._health  = null;
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  /**
   * Проверяет доступность API и загружает статистику.
   * @returns {KnowledgeBase} this
   */
  async init() {
    if (this._loaded) return this;
    try {
      const h = await _get(`${this._api}/health`, this._timeout);
      this._health = h;
      this._online = h.status === 'ok';
      if (this._online) {
        this._stats = await this._loadStats();
        this._loaded = true;
      }
    } catch {
      this._online = false;
    }
    return this;
  }

  /** Доступен ли API. */
  get isOnline() { return this._online; }

  /** Доступен ли LanceDB (dense search). */
  get isDenseAvailable() { return this._health?.lancedb_available === true; }

  /** Загружена ли база. */
  get isLoaded() { return this._loaded; }

  // ── Core search ───────────────────────────────────────────────────────────

  /**
   * 3-stage гибридный поиск (dense + BM25 + ColBERT).
   * @param {string}  query
   * @param {object}  [filters]
   * @param {string}  [filters.model]       'l7' | 'l9'
   * @param {string}  [filters.vehicle]     alias for model
   * @param {string}  [filters.layer]       'engine' | 'brakes' | ...
   * @param {string}  [filters.lang]        'ru' | 'en' | 'zh'
   * @param {string}  [filters.language]    alias for lang
   * @param {string}  [filters.contentType] 'manual' | 'parts'
   * @param {boolean} [filters.translations] включить переводы
   * @param {number}  [limit=10]
   * @param {number}  [offset=0]
   * @returns {Promise<SearchResponse>}
   */
  async search(query, filters = {}, limit = 10, offset = 0) {
    if (!query?.trim() || !this._online) return _emptySearch(query);

    const body = {
      query,
      brand:                this._brand,
      model:                filters.model    || filters.vehicle  || undefined,
      language:             filters.lang     || filters.language || undefined,
      layer:                filters.layer    || undefined,
      content_type:         filters.contentType || undefined,
      include_translations: filters.translations ?? false,
      limit,
      offset,
    };
    _stripUndefined(body);

    const cacheKey = `search:${JSON.stringify(body)}`;
    const cached = this._cache.get(cacheKey);
    if (cached) return cached;

    try {
      const data = await _post(`${this._api}/search`, body, this._timeout);
      this._cache.set(cacheKey, data);
      return data;
    } catch {
      return _emptySearch(query);
    }
  }

  /**
   * Только dense-поиск через LanceDB (требует build_embeddings.py).
   * @param {string} query
   * @param {object} [filters]
   * @param {number} [limit=10]
   * @returns {Promise<SearchResponse>}
   */
  async searchSemantic(query, filters = {}, limit = 10) {
    if (!query?.trim() || !this._online) return _emptySearch(query);

    const body = {
      query,
      brand:        this._brand,
      model:        filters.model    || filters.vehicle  || undefined,
      language:     filters.lang     || filters.language || undefined,
      layer:        filters.layer    || undefined,
      content_type: filters.contentType || undefined,
      limit,
    };
    _stripUndefined(body);

    try {
      return await _post(`${this._api}/search/semantic`, body, this._timeout);
    } catch {
      return _emptySearch(query);
    }
  }

  /**
   * Только BM25 keyword-поиск через FTS5.
   * @param {string} query
   * @param {object} [filters]
   * @param {number} [limit=10]
   * @returns {Promise<SearchResponse>}
   */
  async searchKeyword(query, filters = {}, limit = 10) {
    if (!query?.trim() || !this._online) return _emptySearch(query);

    const body = {
      query,
      brand:        this._brand,
      model:        filters.model    || filters.vehicle  || undefined,
      language:     filters.lang     || filters.language || undefined,
      layer:        filters.layer    || undefined,
      content_type: filters.contentType || undefined,
      limit,
    };
    _stripUndefined(body);

    try {
      return await _post(`${this._api}/search/keyword`, body, this._timeout);
    } catch {
      return _emptySearch(query);
    }
  }

  // ── Chunk / DTC / Glossary ────────────────────────────────────────────────

  /**
   * Просмотр статей по слою (без текстового поиска).
   * @param {string} layer  Напр. 'battery', 'engine'
   * @param {object} [filters]  {model, content_type}
   * @param {number} [limit]
   * @returns {Promise<{total:number, results:Array}>}
   */
  async browse(layer, filters = {}, limit = 50) {
    if (!this._online) return { total: 0, results: [] };

    const params = new URLSearchParams();
    if (layer) params.set('layer', layer);
    if (filters.model) params.set('model', filters.model);
    if (filters.content_type) params.set('content_type', filters.content_type);
    params.set('limit', String(limit));
    params.set('include_translations', 'true');

    try {
      return await _get(`${this._api}/browse?${params}`, this._timeout);
    } catch {
      return { total: 0, results: [] };
    }
  }

  /**
   * Получить полный чанк по ID.
   * @param {string} chunkId
   * @returns {Promise<object|null>}
   */
  async getChunk(chunkId) {
    if (!chunkId || !this._online) return null;

    const cacheKey = `chunk:${chunkId}`;
    const cached = this._cache.get(cacheKey);
    if (cached !== undefined) return cached;

    try {
      const data = await _get(`${this._api}/chunk/${encodeURIComponent(chunkId)}?include_translations=true`, this._timeout);
      this._cache.set(cacheKey, data);
      return data;
    } catch {
      return null;
    }
  }

  /**
   * Поиск по DTC коду. Обратная совместимость с v1 (поле articles → chunks).
   * @param {string} code  Напр. 'P0300', 'U0184'
   * @param {string} [brand]
   * @returns {Promise<DTCResponse>}
   */
  async getDTC(code, brand) {
    if (!code || !this._online) return _emptyDTC(code);

    const cacheKey = `dtc:${code}:${brand || this._brand}`;
    const cached = this._cache.get(cacheKey);
    if (cached !== undefined) return cached;

    const url = brand
      ? `${this._api}/dtc/${encodeURIComponent(code)}?brand=${encodeURIComponent(brand)}`
      : `${this._api}/dtc/${encodeURIComponent(code)}`;

    try {
      const data = await _get(url, this._timeout);
      // Backward-compat: expose .articles as alias for .chunks
      if (data.chunks && !data.articles) data.articles = data.chunks;
      this._cache.set(cacheKey, data);
      return data;
    } catch {
      return _emptyDTC(code);
    }
  }

  /**
   * Поиск по ID глоссария (напр. 'brake_caliper@brakes') или тексту.
   * Замена v1 getComponentArticles().
   * @param {string} query   Термин или glossary_id
   * @param {object} [opts]
   * @param {string} [opts.language]
   * @param {number} [opts.limit=20]
   * @returns {Promise<GlossaryResponse>}
   */
  async glossarySearch(query, opts = {}) {
    if (!query || !this._online) return _emptyGlossary(query);

    const body = { query, limit: opts.limit || 20 };
    if (opts.language) body.language = opts.language;

    const cacheKey = `glossary:${JSON.stringify(body)}`;
    const cached = this._cache.get(cacheKey);
    if (cached !== undefined) return cached;

    try {
      const data = await _post(`${this._api}/glossary/search`, body, this._timeout);
      this._cache.set(cacheKey, data);
      return data;
    } catch {
      return _emptyGlossary(query);
    }
  }

  /**
   * Статьи для компонента из 3D модели (обратная совместимость с v1).
   * @param {string} glossaryId  Напр. 'brake_caliper@brakes'
   * @param {string} [vehicle]   'l7' | 'l9' (игнорируется в v2, фильтрация на стороне KB)
   * @returns {Promise<Array>}
   */
  async getComponentArticles(glossaryId, vehicle) {
    const resp = await this.glossarySearch(glossaryId);
    return resp.chunks || [];
  }

  // ── Stats ─────────────────────────────────────────────────────────────────

  /**
   * Детальная статистика KB.
   * @returns {Promise<object|null>}
   */
  async getStats() {
    if (this._stats) return this._stats;
    return this._loadStats();
  }

  /** Общее число чанков. */
  getTotalCount() {
    return this._stats?.chunks_total
        ?? this._health?.chunks_total
        ?? 0;
  }

  /**
   * Статистика по слоям.
   * @returns {Array<{id: string, count: number}>}
   */
  getLayerStats() {
    const byLayer = this._stats?.by_layer;
    if (!byLayer) return [];
    return Object.entries(byLayer)
      .map(([id, count]) => ({ id, count }))
      .sort((a, b) => b.count - a.count);
  }

  /**
   * Статистика по языкам.
   * @returns {Array<{id: string, count: number}>}
   */
  getLangStats() {
    const byLang = this._stats?.by_language;
    if (!byLang) return [];
    return Object.entries(byLang)
      .map(([id, count]) => ({ id, count }))
      .sort((a, b) => b.count - a.count);
  }

  // ── Parts catalog ───────────────────────────────────────────────────────

  /**
   * Поиск по каталогу запчастей.
   * @param {string}  query     Запрос (номер, название)
   * @param {object}  [opts]
   * @param {string}  [opts.system]     Фильтр системы (EN)
   * @param {string}  [opts.subsystem]  Фильтр подсистемы
   * @param {string}  [opts.lang]       'zh' | 'en'
   * @param {number}  [opts.limit=50]
   * @returns {Promise<{query, system, total, results}>}
   */
  async searchParts(query = '', opts = {}) {
    if (!this._online) return { query, system: '', total: 0, results: [] };

    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (opts.system) params.set('system', opts.system);
    if (opts.subsystem) params.set('subsystem', opts.subsystem);
    if (opts.lang) params.set('lang', opts.lang);
    params.set('limit', String(opts.limit || 50));

    const cacheKey = `parts:${params.toString()}`;
    const cached = this._cache.get(cacheKey);
    if (cached) return cached;

    try {
      const data = await _get(`${this._api}/parts/search?${params}`, this._timeout);
      this._cache.set(cacheKey, data);
      return data;
    } catch {
      return { query, system: '', total: 0, results: [] };
    }
  }

  /**
   * Статистика каталога запчастей.
   * @returns {Promise<{total_parts, unique_part_numbers, systems_count, systems}|null>}
   */
  async getPartsStats() {
    const cacheKey = 'parts_stats';
    const cached = this._cache.get(cacheKey);
    if (cached) return cached;

    try {
      const data = await _get(`${this._api}/parts/stats`, this._timeout);
      this._cache.set(cacheKey, data);
      return data;
    } catch {
      return null;
    }
  }

  /**
   * Получить деталь по артикулу.
   * @param {string} partNumber
   * @returns {Promise<{part_number, count, results}|null>}
   */
  async getPart(partNumber) {
    if (!partNumber || !this._online) return null;
    try {
      return await _get(`${this._api}/parts/${encodeURIComponent(partNumber)}`, this._timeout);
    } catch {
      return null;
    }
  }

  async getSubsystems(systemName) {
    if (!systemName || !this._online) return null;
    try {
      return await _get(`${this._api}/parts/subsystems/${encodeURIComponent(systemName)}`, this._timeout);
    } catch {
      return null;
    }
  }

  // ── Articles (situational) ─────────────────────────────────────────────────

  /**
   * Получить список ситуационных статей.
   * @param {string} [category] - Фильтр: emergency/troubleshooting/maintenance/daily/seasonal
   * @param {string} [lang='ru']
   * @returns {Promise<{total, articles}>}
   */
  async getArticles(category, lang = 'ru') {
    if (!this._online) return { total: 0, articles: [] };
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    params.set('lang', lang);

    const cacheKey = `articles:${params.toString()}`;
    const cached = this._cache.get(cacheKey);
    if (cached) return cached;

    try {
      const data = await _get(`${this._api}/articles?${params}`, this._timeout);
      this._cache.set(cacheKey, data);
      return data;
    } catch {
      return { total: 0, articles: [] };
    }
  }

  /**
   * Получить статью по slug с разбивкой по секциям.
   * @param {string} slug - e.g. 'overheat', 'brake_noise'
   * @param {string} [lang='ru']
   * @returns {Promise<object|null>}
   */
  async getArticle(slug, lang = 'ru') {
    if (!slug || !this._online) return null;
    const params = new URLSearchParams({ lang, include_translations: 'true' });
    try {
      return await _get(`${this._api}/article/${encodeURIComponent(slug)}?${params}`, this._timeout);
    } catch {
      return null;
    }
  }

  // ── Embed (optional, GPU required) ────────────────────────────────────────

  /**
   * Вычислить embedding для текста (требует GPU на сервере).
   * @param {string|string[]} texts
   * @param {'content'|'colbert'} [model='content']
   * @returns {Promise<number[][]|null>}
   */
  async embed(texts, model = 'content') {
    if (!this._online) return null;
    const arr = Array.isArray(texts) ? texts : [texts];
    try {
      const data = await _post(`${this._api}/embed`, { texts: arr, model }, this._timeout * 3);
      return data.embeddings || null;
    } catch {
      return null;
    }
  }

  // ── Cache ─────────────────────────────────────────────────────────────────

  /** Очистить кэш. */
  clearCache() { this._cache.clear(); }

  // ── Private ───────────────────────────────────────────────────────────────

  async _loadStats() {
    try {
      const data = await _get(`${this._api}/stats`, this._timeout);
      this._stats = data;
      return data;
    } catch {
      return null;
    }
  }
}

// ─── Empty-response factories ─────────────────────────────────────────────────

function _emptySearch(query) {
  return { query: query || '', total: 0, offset: 0, results: [], search_mode: 'offline', latency_ms: 0 };
}

function _emptyDTC(code) {
  return { code, brand: '', total: 0, search_mode: 'offline', latency_ms: 0, chunks: [], articles: [] };
}

function _emptyGlossary(query) {
  return { query, matched_glossary_ids: [], total_chunks: 0, latency_ms: 0, chunks: [] };
}

function _stripUndefined(obj) {
  for (const k of Object.keys(obj)) {
    if (obj[k] === undefined) delete obj[k];
  }
}
