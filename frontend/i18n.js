/**
 * LLCAR Diagnostica — Internationalization (i18n) Module
 *
 * Supports 5 languages: RU, EN, ZH, AR, ES
 * - Loads UI strings from data/i18n/{lang}.json
 * - Component name translations via glossary data
 * - Persists language choice in localStorage
 * - RTL support for Arabic
 * - Emits 'lang:change' via CustomEvent on document
 *
 * Usage:
 *   import { I18n } from './i18n.js';
 *   const i18n = new I18n();
 *   await i18n.init('ru');
 *   i18n.get('tabs.health');                      // "ЗДОРОВЬЕ"
 *   i18n.getComponentName('intake_manifold@engine'); // "впускной коллектор"
 *   i18n.getLayerName('engine');                   // "Двигатель, топливо..."
 *   await i18n.switchLanguage('en');               // switches everything
 */

const STORAGE_KEY = 'llcar-lang';
const DEFAULT_LANG = 'ru';
const SUPPORTED = [
  { code: 'ru', name: 'Русский',   flag: '\u{1F1F7}\u{1F1FA}' },
  { code: 'en', name: 'English',   flag: '\u{1F1EC}\u{1F1E7}' },
  { code: 'zh', name: '中文',       flag: '\u{1F1E8}\u{1F1F3}' },
  { code: 'ar', name: 'العربية',   flag: '\u{1F1F8}\u{1F1E6}' },
  { code: 'es', name: 'Español',   flag: '\u{1F1EA}\u{1F1F8}' },
];
const RTL_LANGS = new Set(['ar']);

export class I18n {
  constructor() {
    /** @type {string} Current language code */
    this.lang = DEFAULT_LANG;
    /** @type {object} Nested UI string dictionary loaded from JSON */
    this.strings = {};
    /** @type {object|null} Glossary component names { glossaryId: { en, ru, zh, ar, es } } */
    this.glossary = null;
    /** @type {string} Base path to data/i18n/ directory */
    this._basePath = 'data/i18n';
    /** @type {string|null} Path to glossary data JSON */
    this._glossaryPath = null;
  }

  /**
   * Initialize the i18n system.
   * Restores persisted language from localStorage, loads strings.
   * @param {string} [lang] Override starting language (otherwise uses localStorage or 'ru')
   * @param {object} [options]
   * @param {string} [options.basePath] Path to i18n JSON directory (default: 'data/i18n')
   * @param {string} [options.glossaryPath] Path to i18n-glossary-data.json
   */
  async init(lang, options = {}) {
    if (options.basePath) this._basePath = options.basePath;
    if (options.glossaryPath) this._glossaryPath = options.glossaryPath;

    // Restore from localStorage
    const stored = localStorage.getItem(STORAGE_KEY);
    const startLang = lang || stored || DEFAULT_LANG;
    const validLang = SUPPORTED.find(s => s.code === startLang) ? startLang : DEFAULT_LANG;

    await this._loadStrings(validLang);
    this.lang = validLang;
    this._applyDirection();

    // Load glossary data if path provided
    if (this._glossaryPath) {
      await this._loadGlossary();
    }

    return this;
  }

  /**
   * Switch to a new language.
   * Loads new strings, updates DOM, emits event, saves to localStorage.
   * @param {string} lang Language code
   */
  async switchLanguage(lang) {
    if (!SUPPORTED.find(s => s.code === lang)) {
      console.warn(`[i18n] Unsupported language: ${lang}`);
      return;
    }
    if (lang === this.lang) return;

    await this._loadStrings(lang);
    this.lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
    this._applyDirection();
    this.updateDOM();

    // Emit event for all listeners
    document.dispatchEvent(new CustomEvent('lang:change', {
      detail: { lang }
    }));
  }

  /**
   * Get a UI string by dot-notation key.
   * @param {string} key Dot-separated path (e.g. 'tabs.health', 'dashboard.greeting')
   * @param {string} [fallback] Fallback value if key not found
   * @returns {string}
   */
  get(key, fallback) {
    const parts = key.split('.');
    let obj = this.strings;
    for (const part of parts) {
      if (obj == null || typeof obj !== 'object') {
        return fallback !== undefined ? fallback : key;
      }
      obj = obj[part];
    }
    if (obj === undefined || obj === null) {
      return fallback !== undefined ? fallback : key;
    }
    // Handle arrays (e.g. doctor.suggested)
    return obj;
  }

  /**
   * Get translated component name by glossary_id.
   * @param {string} glossaryId e.g. 'intake_manifold@engine'
   * @returns {string}
   */
  getComponentName(glossaryId) {
    if (!this.glossary?.components) return glossaryId;
    const entry = this.glossary.components[glossaryId];
    if (!entry) return glossaryId;
    return entry[this.lang] || entry[DEFAULT_LANG] || glossaryId;
  }

  /**
   * Get translated layer display name.
   * First checks loaded glossary data, then falls back to UI strings.
   * @param {string} layerId e.g. 'engine'
   * @returns {string}
   */
  getLayerName(layerId) {
    // Try glossary layer labels first
    if (this.glossary?.layers?.[layerId]) {
      const entry = this.glossary.layers[layerId];
      return entry[this.lang] || entry[DEFAULT_LANG] || layerId;
    }
    // Fallback to UI strings
    return this.get(`layers.${layerId}`, layerId);
  }

  /**
   * Get all translations for a component (all 5 languages).
   * @param {string} glossaryId
   * @returns {object|null} { en, ru, zh, ar, es }
   */
  getComponentAllLangs(glossaryId) {
    if (!this.glossary?.components) return null;
    return this.glossary.components[glossaryId] || null;
  }

  /**
   * Search components by name across all languages.
   * @param {string} query
   * @param {number} [limit=20]
   * @returns {string[]} Array of glossary_ids
   */
  searchComponents(query, limit = 20) {
    if (!this.glossary?.components || !query) return [];
    const q = query.toLowerCase().trim();
    if (q.length < 2) return [];

    const results = [];
    for (const [gid, names] of Object.entries(this.glossary.components)) {
      for (const langMeta of SUPPORTED) {
        const val = names[langMeta.code];
        if (val && val.toLowerCase().includes(q)) {
          results.push(gid);
          break;
        }
      }
      if (results.length >= limit) break;
    }
    return results;
  }

  /** @returns {string} Current language code */
  getCurrentLang() {
    return this.lang;
  }

  /**
   * Get supported languages metadata.
   * @returns {Array<{code: string, name: string, flag: string}>}
   */
  getSupportedLangs() {
    return [...SUPPORTED];
  }

  /** @returns {boolean} Whether current language is RTL */
  isRTL() {
    return RTL_LANGS.has(this.lang);
  }

  /**
   * Update all DOM elements with data-i18n attributes.
   * - data-i18n="key" → sets textContent
   * - data-i18n-placeholder="key" → sets placeholder
   * - data-i18n-title="key" → sets title
   * - data-i18n-html="key" → sets innerHTML (use sparingly)
   */
  updateDOM() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const val = this.get(key);
      if (val !== key) el.textContent = val;
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const val = this.get(key);
      if (val !== key) el.placeholder = val;
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      const val = this.get(key);
      if (val !== key) el.title = val;
    });
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      const val = this.get(key);
      if (val !== key) el.innerHTML = val;
    });
  }

  // ═══════════════════════════════════════════════════════
  // Private methods
  // ═══════════════════════════════════════════════════════

  /** Load UI strings JSON for a language. */
  async _loadStrings(lang) {
    const url = `${this._basePath}/${lang}.json`;
    try {
      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      this.strings = await resp.json();
    } catch (e) {
      console.warn(`[i18n] Failed to load ${url}:`, e.message);
      // Try loading default language as fallback
      if (lang !== DEFAULT_LANG) {
        try {
          const fallbackResp = await fetch(`${this._basePath}/${DEFAULT_LANG}.json`);
          if (fallbackResp.ok) this.strings = await fallbackResp.json();
        } catch (_) { /* give up */ }
      }
    }
  }

  /** Load glossary translations JSON. */
  async _loadGlossary() {
    if (!this._glossaryPath) return;
    try {
      const resp = await fetch(this._glossaryPath);
      if (resp.ok) {
        this.glossary = await resp.json();
      }
    } catch (e) {
      console.warn('[i18n] Failed to load glossary:', e.message);
    }
  }

  /** Apply dir="rtl" or dir="ltr" to document root. */
  _applyDirection() {
    const html = document.documentElement;
    html.setAttribute('lang', this.lang);
    html.setAttribute('dir', this.isRTL() ? 'rtl' : 'ltr');
  }
}
