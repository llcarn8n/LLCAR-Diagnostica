/**
 * LLCAR Diagnostica — Internationalization (i18n) Module
 *
 * Supports 5 languages: RU, EN, ZH, AR, ES
 * - Loads UI label translations (built-in)
 * - Loads component name translations from glossary JSON
 * - Persists language choice in localStorage
 * - Provides RTL support for Arabic
 * - Emits 'languagechange' event on document when language switches
 *
 * Usage:
 *   import { i18n } from '../js/i18n.js';
 *   await i18n.init({ glossaryPath: '../Diagnostica/architecture/i18n-glossary-data.json' });
 *   i18n.t('search_placeholder');           // → "Поиск компонентов..."
 *   i18n.componentName('intake_manifold@engine'); // → "впускной коллектор"
 *   i18n.layerName('engine');               // → "Двигатель, топливо, воздух и выхлоп"
 *   i18n.setLanguage('en');                 // switches everything
 */

const SUPPORTED_LANGS = ['ru', 'en', 'zh', 'ar', 'es'];
const RTL_LANGS = ['ar'];
const STORAGE_KEY = 'llcar_language';
const DEFAULT_LANG = 'ru';

// ═══════════════════════════════════════════════════════════
// UI Label Translations
// ═══════════════════════════════════════════════════════════

const UI_LABELS = {
  // -- Top bar --
  back: {
    ru: '← Назад', en: '← Back', zh: '← 返回', ar: '← رجوع', es: '← Volver'
  },
  dtc_label: {
    ru: 'DTC:', en: 'DTC:', zh: 'DTC:', ar: 'DTC:', es: 'DTC:'
  },
  dtc_placeholder: {
    ru: 'P0A80', en: 'P0A80', zh: 'P0A80', ar: 'P0A80', es: 'P0A80'
  },
  dtc_search: {
    ru: 'Поиск', en: 'Search', zh: '搜索', ar: 'بحث', es: 'Buscar'
  },

  // -- Left panel --
  components: {
    ru: 'Компоненты', en: 'Components', zh: '组件', ar: 'المكونات', es: 'Componentes'
  },
  search_placeholder: {
    ru: 'Поиск компонентов...', en: 'Search components...', zh: '搜索组件...', ar: 'بحث المكونات...', es: 'Buscar componentes...'
  },
  all_systems: {
    ru: 'Все', en: 'All', zh: '全部', ar: 'الكل', es: 'Todos'
  },

  // -- Viewport --
  xray: {
    ru: 'X-Ray', en: 'X-Ray', zh: 'X-Ray', ar: 'X-Ray', es: 'X-Ray'
  },
  reset_camera: {
    ru: 'Сброс камеры', en: 'Reset Camera', zh: '重置相机', ar: 'إعادة ضبط الكاميرا', es: 'Reiniciar cámara'
  },
  reset_highlight: {
    ru: 'Сбросить подсветку', en: 'Clear Highlight', zh: '清除高亮', ar: 'إزالة التمييز', es: 'Borrar resaltado'
  },
  loading_model: {
    ru: 'Загрузка 3D модели...', en: 'Loading 3D model...', zh: '加载3D模型...', ar: 'تحميل النموذج ثلاثي الأبعاد...', es: 'Cargando modelo 3D...'
  },

  // -- Right panel --
  info: {
    ru: 'Информация', en: 'Information', zh: '信息', ar: 'معلومات', es: 'Información'
  },
  info_empty: {
    ru: 'Кликните на компонент в 3D-сцене или найдите DTC-код для получения информации',
    en: 'Click a component in the 3D scene or search a DTC code to get information',
    zh: '点击3D场景中的组件或搜索DTC代码获取信息',
    ar: 'انقر على مكون في المشهد ثلاثي الأبعاد أو ابحث عن رمز DTC للحصول على معلومات',
    es: 'Haga clic en un componente de la escena 3D o busque un código DTC para obtener información'
  },
  save_key: {
    ru: 'Сохр', en: 'Save', zh: '保存', ar: 'حفظ', es: 'Guardar'
  },
  ask_claude: {
    ru: 'Спросить Claude', en: 'Ask Claude', zh: '询问Claude', ar: 'اسأل Claude', es: 'Preguntar a Claude'
  },
  ask_claude_thinking: {
    ru: 'Думаю...', en: 'Thinking...', zh: '思考中...', ar: 'جاري التفكير...', es: 'Pensando...'
  },
  claude_placeholder: {
    ru: 'Задайте вопрос о компоненте...', en: 'Ask a question about the component...', zh: '关于此组件提问...', ar: 'اطرح سؤالاً عن المكون...', es: 'Haga una pregunta sobre el componente...'
  },
  claude_system_prompt: {
    ru: 'Ты автомобильный диагност для Li Auto. Отвечай кратко и по делу на русском языке.',
    en: 'You are an automotive diagnostician for Li Auto. Answer concisely and to the point in English.',
    zh: '你是理想汽车的诊断专家。请简洁、专业地用中文回答。',
    ar: 'أنت فني تشخيص سيارات لشركة Li Auto. أجب بإيجاز وبشكل مباشر باللغة العربية.',
    es: 'Eres un diagnosticador automotriz para Li Auto. Responde de forma concisa y directa en español.'
  },

  // -- Status bar --
  initializing: {
    ru: 'Инициализация...', en: 'Initializing...', zh: '初始化中...', ar: 'جاري التهيئة...', es: 'Inicializando...'
  },
  meshes_count: {
    ru: 'Мешей', en: 'Meshes', zh: '网格', ar: 'شبكات', es: 'Mallas'
  },
  ready: {
    ru: 'Готово', en: 'Ready', zh: '就绪', ar: 'جاهز', es: 'Listo'
  },

  // -- Component details --
  system_label: {
    ru: 'Система', en: 'System', zh: '系统', ar: 'النظام', es: 'Sistema'
  },
  dtc_codes: {
    ru: 'DTC коды', en: 'DTC Codes', zh: 'DTC代码', ar: 'رموز DTC', es: 'Códigos DTC'
  },
  manual_sections: {
    ru: 'Разделы мануала', en: 'Manual Sections', zh: '手册章节', ar: 'أقسام الدليل', es: 'Secciones del manual'
  },
  related_components: {
    ru: 'Связанные компоненты', en: 'Related Components', zh: '相关组件', ar: 'المكونات ذات الصلة', es: 'Componentes relacionados'
  },
  no_dtc: {
    ru: 'Нет DTC кодов', en: 'No DTC codes', zh: '无DTC代码', ar: 'لا توجد رموز DTC', es: 'Sin códigos DTC'
  },

  // -- Language selector --
  language: {
    ru: 'Язык', en: 'Language', zh: '语言', ar: 'اللغة', es: 'Idioma'
  },

  // -- Error messages --
  error_load_model: {
    ru: 'Ошибка загрузки модели', en: 'Error loading model', zh: '模型加载错误', ar: 'خطأ في تحميل النموذج', es: 'Error al cargar el modelo'
  },
  error_generic: {
    ru: 'Ошибка', en: 'Error', zh: '错误', ar: 'خطأ', es: 'Error'
  },

  // -- PID overlay --
  pid_overlay: {
    ru: 'PID Наложение', en: 'PID Overlay', zh: 'PID叠加', ar: 'تراكب PID', es: 'Superposición PID'
  },
  pid_no_data: {
    ru: 'Нет данных', en: 'No data', zh: '无数据', ar: 'لا توجد بيانات', es: 'Sin datos'
  },

  // -- Knowledge base --
  knowledge_base: {
    ru: 'База знаний', en: 'Knowledge Base', zh: '知识库', ar: 'قاعدة المعرفة', es: 'Base de conocimientos'
  },
};

// Language display names and flag emojis
const LANG_META = {
  ru: { name: 'Русский', nativeName: 'Русский', flag: '🇷🇺' },
  en: { name: 'English', nativeName: 'English', flag: '🇬🇧' },
  zh: { name: 'Chinese', nativeName: '中文', flag: '🇨🇳' },
  ar: { name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦' },
  es: { name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
};

// ═══════════════════════════════════════════════════════════
// i18n Singleton
// ═══════════════════════════════════════════════════════════

class I18n {
  constructor() {
    this._lang = DEFAULT_LANG;
    this._glossary = null;        // { components: {}, layers: {} }
    this._glossaryLoaded = false;
    this._observers = [];
  }

  /** Initialize the i18n system. Call once at app startup. */
  async init(options = {}) {
    // Restore persisted language
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && SUPPORTED_LANGS.includes(stored)) {
      this._lang = stored;
    }

    // Load glossary translations if path provided
    if (options.glossaryPath) {
      try {
        const resp = await fetch(options.glossaryPath);
        if (resp.ok) {
          this._glossary = await resp.json();
          this._glossaryLoaded = true;
        }
      } catch (e) {
        console.warn('[i18n] Failed to load glossary translations:', e.message);
      }
    }

    // Apply RTL if needed
    this._applyDirection();
    return this;
  }

  /** Current language code. */
  get lang() { return this._lang; }

  /** Whether current language is RTL. */
  get isRTL() { return RTL_LANGS.includes(this._lang); }

  /** All supported language codes. */
  get supportedLanguages() { return [...SUPPORTED_LANGS]; }

  /** Language metadata (name, nativeName, flag). */
  get languageMeta() { return LANG_META; }

  /** Whether glossary data is loaded. */
  get glossaryLoaded() { return this._glossaryLoaded; }

  /**
   * Set the active language.
   * Updates localStorage, applies RTL, and dispatches 'languagechange' event.
   */
  setLanguage(lang) {
    if (!SUPPORTED_LANGS.includes(lang)) {
      console.warn(`[i18n] Unsupported language: ${lang}`);
      return;
    }
    if (lang === this._lang) return;

    this._lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
    this._applyDirection();

    // Notify observers
    for (const cb of this._observers) {
      try { cb(lang); } catch (e) { console.error('[i18n] observer error:', e); }
    }

    // Dispatch DOM event
    document.dispatchEvent(new CustomEvent('languagechange', { detail: { lang } }));
  }

  /**
   * Translate a UI label key.
   * Falls back to Russian, then returns the key itself.
   */
  t(key) {
    const entry = UI_LABELS[key];
    if (!entry) return key;
    return entry[this._lang] || entry[DEFAULT_LANG] || key;
  }

  /**
   * Get component display name in current language by glossary_id.
   * @param {string} glossaryId - e.g. "intake_manifold@engine"
   * @returns {string} Translated name or the glossaryId as fallback
   */
  componentName(glossaryId) {
    if (!this._glossary?.components) return glossaryId;
    const entry = this._glossary.components[glossaryId];
    if (!entry) return glossaryId;
    return entry[this._lang] || entry[DEFAULT_LANG] || glossaryId;
  }

  /**
   * Get layer display name in current language.
   * @param {string} layerId - e.g. "engine"
   * @returns {string}
   */
  layerName(layerId) {
    if (!this._glossary?.layers) return layerId;
    const entry = this._glossary.layers[layerId];
    if (!entry) return layerId;
    return entry[this._lang] || entry[DEFAULT_LANG] || layerId;
  }

  /**
   * Get all translations for a component (all 5 languages).
   * Useful for building search aliases.
   * @param {string} glossaryId
   * @returns {object|null} { en, ru, zh, ar, es }
   */
  componentAllLangs(glossaryId) {
    if (!this._glossary?.components) return null;
    return this._glossary.components[glossaryId] || null;
  }

  /**
   * Search components by name across all languages.
   * Returns matching glossary_ids.
   * @param {string} query - Search string
   * @param {number} limit - Max results (default 20)
   * @returns {string[]} Array of glossary_ids
   */
  searchComponents(query, limit = 20) {
    if (!this._glossary?.components || !query) return [];
    const q = query.toLowerCase().trim();
    if (q.length < 2) return [];

    const results = [];
    for (const [gid, names] of Object.entries(this._glossary.components)) {
      for (const lang of SUPPORTED_LANGS) {
        if (names[lang] && names[lang].toLowerCase().includes(q)) {
          results.push(gid);
          break;
        }
      }
      if (results.length >= limit) break;
    }
    return results;
  }

  /**
   * Register an observer callback for language changes.
   * @param {function} callback - Called with (newLang) when language changes
   * @returns {function} Unsubscribe function
   */
  onChange(callback) {
    this._observers.push(callback);
    return () => {
      const idx = this._observers.indexOf(callback);
      if (idx >= 0) this._observers.splice(idx, 1);
    };
  }

  /**
   * Update all DOM elements with data-i18n attribute.
   * <span data-i18n="components">Компоненты</span>
   * Also updates data-i18n-placeholder for input placeholders.
   */
  updateDOM() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      el.placeholder = this.t(key);
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      el.title = this.t(key);
    });
  }

  /** Apply dir="rtl" or dir="ltr" to <html>. */
  _applyDirection() {
    const html = document.documentElement;
    if (this.isRTL) {
      html.setAttribute('dir', 'rtl');
      html.setAttribute('lang', this._lang);
    } else {
      html.setAttribute('dir', 'ltr');
      html.setAttribute('lang', this._lang);
    }
  }
}

// Export singleton
export const i18n = new I18n();
export { SUPPORTED_LANGS, RTL_LANGS, LANG_META, UI_LABELS };
