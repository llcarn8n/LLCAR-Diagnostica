/**
 * LLCAR Diagnostica — Knowledge Base v2 (Заботливый помощник)
 *
 * Новый экран KB: ситуационная навигация, progressive disclosure,
 * дерево решений, DTC-интеграция, глоссарий-тултипы, заботливый тон.
 * Работает параллельно со старым knowledge.js.
 */

import { emit, on, off } from '../event-bus.js';
import { KnowledgeBase } from '../knowledge-base.js';
import { renderMarkdown } from '../kb-viewer.js';
import { GlossaryTooltips } from '../kb-glossary.js';

// ═══════════════════════════════════════════════════════════
// Состояние модуля
// ═══════════════════════════════════════════════════════════

let _container = null;
let _rendered = false;
let _kb = null;
let _i18n = null;
let _glossary = null;           // GlossaryTooltips instance
let _glossaryData = null;       // raw glossary JSON
let _persona = 'beginner';     // 'beginner' | 'expert'
let _activeTab = 'situations'; // 'situations' | 'systems' | 'dtc' | 'parts'
let _searchQuery = '';
let _activeVehicle = null;
let _navStack = [];             // стек навигации для Назад

const LAYER_COLORS = {
  body: '#4FC3F7', engine: '#FF7043', drivetrain: '#AB47BC',
  ev: '#66BB6A', brakes: '#EF5350', sensors: '#FFA726',
  hvac: '#26C6DA', interior: '#8D6E63', general: '#8B949E',
  battery: '#66BB6A', lighting: '#FFA726', chassis: '#78909C',
  infotainment: '#EC407A', adas: '#29B6F6', parts: '#78909C',
};

// Base URL для картинок каталога запчастей (через FastAPI)
const PARTS_IMG_BASE = 'http://localhost:8000';

// Перевод системных названий каталога запчастей (EN → RU)
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

// ═══════════════════════════════════════════════════════════
// Ситуационные кластеры (Фаза 5)
// ═══════════════════════════════════════════════════════════

const SITUATION_CLUSTERS = [
  {
    id: 'overheat', icon: '\u{1F321}\uFE0F', urgency: 4,
    title: 'Перегрев двигателя в пробке',
    desc: 'Температура выше нормы, пар из-под капота',
    searchQueries: ['перегрев двигатель температура охлаждение', 'engine overheat coolant temperature'],
    layers: ['engine'], season: 'summer',
    quickAnswer: 'Остановитесь, заглушите мотор, дождитесь остывания. Не открывайте крышку радиатора на горячую.',
  },
  {
    id: 'brake_noise', icon: '\u{1F6DE}', urgency: 3,
    title: 'Скрип или вибрация при торможении',
    desc: 'Посторонние звуки при нажатии на педаль тормоза',
    searchQueries: ['тормоз скрип вибрация колодки диск', 'brake noise squeal vibration pad'],
    layers: ['brakes'],
    quickAnswer: 'Проверьте толщину колодок и состояние дисков. При сильной вибрации — обратитесь на СТО.',
  },
  {
    id: 'battery_drain', icon: '\u{1F50B}', urgency: 3,
    title: 'Разрядка батареи / снижение запаса хода',
    desc: 'Быстрая потеря заряда, запас хода ниже ожидаемого',
    searchQueries: ['батарея разряд запас хода зарядка', 'battery drain range charging soc'],
    layers: ['ev', 'battery'],
    quickAnswer: 'Проверьте уровень заряда и состояние ВВБ. Избегайте глубокого разряда ниже 20%.',
  },
  {
    id: 'cold_start', icon: '\u2744\uFE0F', urgency: 2,
    title: 'Проблемы с запуском зимой',
    desc: 'Долгий запуск, ошибки при низких температурах',
    searchQueries: ['зима мороз запуск холодный старт обогрев', 'cold start winter freeze preheat'],
    layers: ['engine'], season: 'winter',
    quickAnswer: 'Используйте предпусковой подогрев. Проверьте уровень масла и заряд АКБ.',
  },
  {
    id: 'warning_light', icon: '\u26A0\uFE0F', urgency: 4,
    title: 'Загорелась контрольная лампа',
    desc: 'Индикатор неисправности на приборной панели',
    searchQueries: ['индикатор лампа ошибка панель приборов', 'warning light indicator malfunction dashboard'],
    layers: ['sensors'],
    quickAnswer: 'Запишите код ошибки. Жёлтый индикатор — можно ехать осторожно. Красный — остановитесь.',
  },
  {
    id: 'adas_fault', icon: '\u{1F916}', urgency: 2,
    title: 'Сбои системы помощи водителю',
    desc: 'Не работает ACC, LKA, или камеры',
    searchQueries: ['adas acc lka камера датчик калибровка', 'adas acc lka camera sensor calibration'],
    layers: ['adas', 'sensors'],
    quickAnswer: 'Перезапустите систему. Проверьте чистоту камер и датчиков. При повторении — диагностика.',
  },
  {
    id: 'tire_pressure', icon: '\u{1F6DE}', urgency: 3,
    title: 'Потеря давления в шинах',
    desc: 'Индикатор TPMS, неравномерный износ',
    searchQueries: ['давление шина tpms прокол', 'tire pressure tpms flat'],
    layers: ['chassis'],
    quickAnswer: 'Проверьте давление во всех колёсах. Норма: 2.3-2.5 бар. При резкой потере — не двигайтесь.',
  },
  {
    id: 'maintenance', icon: '\u{1F527}', urgency: 1,
    title: 'Плановое ТО и обслуживание',
    desc: 'Замена масла, фильтров, колодок, жидкостей',
    searchQueries: ['замена масло фильтр обслуживание ТО регламент', 'maintenance oil filter service schedule'],
    layers: ['engine', 'brakes'],
    quickAnswer: 'Следуйте регламенту ТО. Основные интервалы: масло — 10 000 км, тормозная жидкость — 2 года.',
  },
  {
    id: 'unknown', icon: '\u2753', urgency: 0,
    title: 'Не знаю что делать?',
    desc: 'Помогу разобраться — шаг за шагом',
    searchQueries: [], layers: [],
    isDecisionTree: true,
  },
];

// ═══════════════════════════════════════════════════════════
// Ежедневные советы (только для новичков)
// ═══════════════════════════════════════════════════════════

const DAILY_TIPS = [
  {
    id: 'daily_charging', icon: '🔌',
    title: 'Правильная зарядка',
    desc: 'Как и когда заряжать, оптимальный уровень SOC',
    searchQueries: ['зарядка батарея soc уровень заряд кабель', 'charging battery soc level cable plug'],
    layers: ['ev', 'battery'],
    quickAnswer: 'Оптимальный уровень заряда — 20–80%. Заряжайте регулярно, не допускайте глубокого разряда.',
  },
  {
    id: 'daily_climate', icon: '❄️',
    title: 'Климат-контроль и экономия',
    desc: 'Кондиционер, обогрев, рециркуляция, расход энергии',
    searchQueries: ['климат контроль кондиционер обогрев рециркуляция температура', 'climate control ac heater recirculation'],
    layers: ['hvac'],
    quickAnswer: 'Рециркуляция экономит энергию. Предварительный обогрев на зарядке — бесплатное тепло.',
  },
  {
    id: 'daily_adas', icon: '🛣️',
    title: 'Круиз-контроль и помощники',
    desc: 'ACC, удержание полосы, автопарковка',
    searchQueries: ['круиз контроль acc lka автопарковка помощник', 'cruise control acc lka autopark assistant'],
    layers: ['adas'],
    quickAnswer: 'ACC работает от 30 км/ч. Держите руки на руле. Автопарковка — только на ровной площадке.',
  },
  {
    id: 'daily_long_trip', icon: '🗺️',
    title: 'Подготовка к дальней поездке',
    desc: 'Проверки перед дорогой, запас хода, остановки',
    searchQueries: ['дальняя поездка подготовка проверка маршрут запас хода', 'long trip preparation check range route'],
    layers: ['engine', 'ev', 'chassis'],
    quickAnswer: 'Проверьте давление шин, уровень жидкостей, зарядите до 100%. Планируйте остановки каждые 200 км.',
  },
  {
    id: 'daily_parking', icon: '🅿️',
    title: 'Парковка и камеры',
    desc: 'Парктроники, камеры кругового обзора, режимы',
    searchQueries: ['парковка камера парктроник обзор датчик', 'parking camera sensor surround view'],
    layers: ['adas', 'sensors'],
    quickAnswer: 'Камера кругового обзора включается автоматически на задней передаче. Парктроники — от 1.5 м.',
  },
  {
    id: 'daily_economy', icon: '⛽',
    title: 'Экономичная езда',
    desc: 'Режимы движения, рекуперация, расход топлива',
    searchQueries: ['экономия расход рекуперация режим eco топливо', 'economy fuel consumption regeneration eco mode'],
    layers: ['ev', 'engine', 'drivetrain'],
    quickAnswer: 'Режим ECO + сильная рекуперация — максимальная экономия. Плавное ускорение экономит до 20%.',
  },
  {
    id: 'daily_child_safety', icon: '👶',
    title: 'Детская безопасность',
    desc: 'ISOFIX, детский замок, подушки безопасности',
    searchQueries: ['isofix детское кресло замок безопасность ребенок', 'isofix child seat lock safety airbag'],
    layers: ['interior', 'body'],
    quickAnswer: 'ISOFIX крепления на задних сиденьях. Включите детский замок. Отключите переднюю подушку для детского кресла.',
  },
  {
    id: 'daily_infotainment', icon: '📱',
    title: 'Мультимедиа и навигация',
    desc: 'Подключение телефона, CarPlay, обновления',
    searchQueries: ['мультимедиа навигация carplay bluetooth подключение обновление', 'infotainment navigation carplay bluetooth update'],
    layers: ['infotainment'],
    quickAnswer: 'CarPlay подключается через USB-C кабель. Обновления системы — через Wi-Fi в настройках.',
  },
];

// ═══════════════════════════════════════════════════════════
// Дерево решений (Фаза 6)
// ═══════════════════════════════════════════════════════════

const DECISION_TREE = {
  root: {
    question: 'Безопасно ли продолжать движение?',
    intro: 'Давайте вместе определим, что происходит с вашим автомобилем.',
    options: [
      { label: 'Да, вроде всё работает', next: 'monitor' },
      { label: 'Нет, что-то серьёзное', next: 'stop' },
      { label: 'Не уверен(а)', next: 'check_symptoms' },
    ],
  },
  monitor: {
    type: 'recommendation',
    urgency: 1,
    title: 'Мониторинг и запись на СТО',
    text: 'Если автомобиль едет нормально, запланируйте визит на СТО в ближайшие дни. Следите за индикаторами на панели.',
    actions: ['Записаться на диагностику', 'Проверить коды ошибок'],
    searchQuery: 'диагностика обслуживание проверка',
  },
  stop: {
    type: 'recommendation',
    urgency: 5,
    title: 'Остановитесь в безопасном месте',
    text: 'Включите аварийную сигнализацию, остановитесь на обочине. Не пытайтесь продолжить движение — это может усугубить ситуацию.',
    actions: ['Вызвать эвакуатор', 'Позвонить на горячую линию Li Auto'],
    searchQuery: 'экстренная остановка эвакуатор безопасность',
  },
  check_symptoms: {
    question: 'Какой симптом вы наблюдаете?',
    intro: 'Опишите, что именно вас беспокоит.',
    options: [
      { label: 'Необычный звук', next: 'sound_search' },
      { label: 'Запах горелого', next: 'stop' },
      { label: 'Индикатор на панели', next: 'indicator_search' },
      { label: 'Потеря мощности', next: 'power_loss_search' },
    ],
  },
  sound_search: {
    type: 'recommendation',
    urgency: 2,
    title: 'Необычные звуки',
    text: 'Обратите внимание: откуда звук (перед/зад, слева/справа), когда он появляется (при торможении, повороте, на скорости).',
    searchQuery: 'звук шум стук скрип вибрация',
  },
  indicator_search: {
    type: 'recommendation',
    urgency: 3,
    title: 'Индикатор на панели',
    text: 'Красный индикатор — остановитесь. Жёлтый — можно ехать с осторожностью до СТО. Запишите текст или код ошибки.',
    searchQuery: 'индикатор лампа ошибка панель приборов предупреждение',
  },
  power_loss_search: {
    type: 'recommendation',
    urgency: 3,
    title: 'Потеря мощности',
    text: 'Снизьте скорость и двигайтесь в правой полосе. Если мощность упала резко — остановитесь.',
    searchQuery: 'потеря мощности тяга ускорение обороты',
  },
};

// ═══════════════════════════════════════════════════════════
// Заботливый тон (Фаза 8)
// ═══════════════════════════════════════════════════════════

const CARING_REPLACEMENTS = [
  [/ПРЕДУПРЕЖДЕНИЕ/g, 'Обратите внимание'],
  [/WARNING/gi, 'Обратите внимание'],
  [/ОШИБКА/g, 'Обнаружено отклонение'],
  [/ERROR/gi, 'Обнаружено отклонение'],
  [/НЕИСПРАВНОСТЬ/g, 'Нетипичное поведение'],
  [/FAULT/gi, 'Нетипичное поведение'],
  [/КРИТИЧЕСКАЯ/g, 'Требует внимания'],
  [/CRITICAL/gi, 'Требует внимания'],
  [/DANGER/gi, 'Будьте осторожны'],
  [/ОПАСНОСТЬ/g, 'Будьте осторожны'],
];

function _caringTone(text) {
  if (!text) return text;
  let result = text;
  for (const [pattern, replacement] of CARING_REPLACEMENTS) {
    result = result.replace(pattern, replacement);
  }
  return result;
}

// ═══════════════════════════════════════════════════════════
// Sparklines (Фаза 8)
// ═══════════════════════════════════════════════════════════

function renderSparkline(data, width = 60, height = 20, color = '#3FB950') {
  if (!data || data.length < 2) return '';
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const step = width / (data.length - 1);

  const points = data.map((v, i) => {
    const x = i * step;
    const y = height - ((v - min) / range) * (height - 2) - 1;
    return `${x},${y}`;
  }).join(' ');

  return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="vertical-align:middle;">
    <polyline points="${points}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

// ═══════════════════════════════════════════════════════════
// Вспомогательные
// ═══════════════════════════════════════════════════════════

function t(key, fallback) {
  if (_i18n) return _i18n.get(key, fallback);
  return fallback || key;
}

function getLocalizedEntry(entry) {
  const userLang = _i18n?.lang || 'ru';
  const srcLang = entry.source_language || '';
  if (srcLang === userLang) return entry;
  if (entry.translations?.length > 0) {
    const tr = entry.translations.find(t => t.lang === userLang);
    if (tr) {
      return {
        ...entry,
        title: tr.title || entry.title,
        content: tr.content || entry.content,
        _translated: true,
      };
    }
  }
  return entry;
}

/** Получить текущий месяц для сезонной подсветки */
function _currentSeason() {
  const month = new Date().getMonth(); // 0-11
  if (month >= 10 || month <= 2) return 'winter';
  if (month >= 5 && month <= 8) return 'summer';
  return null;
}

/** Urgency → цвет */
function _urgencyColor(urgency) {
  if (urgency >= 4) return 'var(--status-critical)';
  if (urgency >= 3) return 'var(--status-warning)';
  if (urgency >= 2) return '#FFA726';
  return 'var(--status-healthy)';
}

/** Urgency → фон */
function _urgencyBg(urgency) {
  if (urgency >= 4) return 'var(--critical-bg)';
  if (urgency >= 3) return 'var(--warning-bg)';
  return 'var(--healthy-bg)';
}

const SOURCE_BADGES = {
  pdf_l9_ru: { icon: '\u{1F4D6}', label: 'L9 RU' },
  pdf_l7_ru: { icon: '\u{1F4D6}', label: 'L7 RU' },
  pdf_l9_zh: { icon: '\u{1F4D6}', label: 'L9 ZH' },
  pdf_l7_zh: { icon: '\u{1F4D6}', label: 'L7 ZH' },
  pdf_l9_zh_full: { icon: '\u{1F4D6}', label: 'L9 ZH' },
  pdf_l7_zh_full: { icon: '\u{1F4D6}', label: 'L7 ZH' },
  parts_zh: { icon: '\u{1F527}', label: 'Каталог' },
  parts_l9_zh: { icon: '\u{1F527}', label: 'L9 Каталог' },
  web: { icon: '\u{1F310}', label: 'Веб' },
  dtc_db: { icon: '\u26A0', label: 'DTC' },
  dtc_database: { icon: '\u26A0', label: 'DTC' },
};

// ═══════════════════════════════════════════════════════════
// Жизненный цикл экрана
// ═══════════════════════════════════════════════════════════

export function render(container) {
  _container = container;

  // Восстановить persona из localStorage
  _persona = localStorage.getItem('llcar-persona') || 'beginner';

  // Обработка deep link из 3D twin
  if (window.__llcar_selectedComponent) {
    const gid = window.__llcar_selectedComponent;
    const data = window.__llcar_selectedComponentData;
    window.__llcar_selectedComponent = null;
    window.__llcar_selectedComponentData = null;
    // Ищем статьи для этого компонента
    _searchQuery = gid.split('@')[0].replace(/_/g, ' ');
  }

  // Обработка DTC навигации
  if (window.__llcar_dtcNavigate) {
    const dtcCode = window.__llcar_dtcNavigate;
    window.__llcar_dtcNavigate = null;
    _activeTab = 'dtc';
    _searchQuery = dtcCode;
  }

  if (_rendered) {
    _renderContent();
    return;
  }
  _rendered = true;

  _i18n = window.__llcar_i18n || null;

  if (!_kb) {
    _kb = new KnowledgeBase();
    _kb.init().then(() => {
      _loadGlossary().then(() => _renderContent());
    });
  } else {
    _renderContent();
  }

  on('component:select', _onComponentSelect);
  on('lang:change', _onLangChange);
  on('dtc:navigate', _onDTCNavigate);
}

export function cleanup() {
  off('component:select', _onComponentSelect);
  off('lang:change', _onLangChange);
  off('dtc:navigate', _onDTCNavigate);
  _navStack = [];
}

function _onComponentSelect(e) {
  const gid = e.detail?.glossaryId;
  if (gid) {
    _searchQuery = gid.split('@')[0].replace(/_/g, ' ');
    _renderContent();
  }
}

function _onLangChange() {
  if (_rendered) _renderContent();
}

function _onDTCNavigate(e) {
  const code = e.detail?.code;
  if (code) {
    _activeTab = 'dtc';
    _searchQuery = code;
    _renderContent();
  }
}

async function _loadGlossary() {
  try {
    const resp = await fetch('data/architecture/i18n-glossary-data.json');
    if (resp.ok) {
      _glossaryData = await resp.json();
      _glossary = new GlossaryTooltips(_glossaryData, _i18n);
    }
  } catch (_) { /* игнорируем */ }
}

// ═══════════════════════════════════════════════════════════
// Основной рендер
// ═══════════════════════════════════════════════════════════

function _renderContent() {
  if (!_container) return;

  const isOnline = _kb?.isOnline;

  _container.innerHTML = `
    <div class="kbv2-screen">
      <!-- Заголовок -->
      <div class="kbv2-header">
        <div class="kbv2-header__left">
          <span class="kbv2-header__title">${t('kbv2.title', 'База знаний')}</span>
        </div>
        <div class="kbv2-header__right">
          <div class="kbv2-persona-switch" id="kbv2-persona">
            <button class="kbv2-persona-btn ${_persona === 'beginner' ? 'kbv2-persona-btn--active' : ''}" data-persona="beginner">${t('kbv2.beginner', 'Новичок')}</button>
            <button class="kbv2-persona-btn ${_persona === 'expert' ? 'kbv2-persona-btn--active' : ''}" data-persona="expert">${t('kbv2.expert', 'Эксперт')}</button>
          </div>
          <button class="kbv2-admin-btn" id="kbv2-scraping-btn" title="Управление скрапингом">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          </button>
          <span class="kbv2-status ${isOnline ? 'kbv2-status--online' : 'kbv2-status--offline'}"></span>
        </div>
      </div>

      <!-- Поиск -->
      <div class="kbv2-search-wrap">
        <div class="kbv2-search-bar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input type="text" id="kbv2-search" class="kbv2-search-input"
            placeholder="${t('kbv2.search_placeholder', 'Опишите проблему или введите код ошибки...')}"
            value="${_searchQuery}" />
          ${_searchQuery ? `<button id="kbv2-search-clear" class="kbv2-search-clear">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>` : ''}
        </div>
      </div>

      <!-- Табы -->
      <div class="kbv2-tabs" id="kbv2-tabs"></div>

      ${!isOnline ? `
        <div class="kbv2-offline-banner">
          <span>${t('kbv2.offline_msg', 'API сервер недоступен. Ситуационная навигация работает офлайн.')}</span>
        </div>
      ` : ''}

      <!-- Область контента -->
      <div class="screen__scrollable kbv2-results" id="kbv2-results"></div>
    </div>
  `;

  _renderTabs();
  _renderView();
  _bindMainEvents();
}

// ═══════════════════════════════════════════════════════════
// Табы
// ═══════════════════════════════════════════════════════════

const TABS = [
  { id: 'situations', label: 'Ситуации', icon: '\u{1F4CB}' },
  { id: 'systems', label: 'Системы', icon: '\u2699\uFE0F' },
  { id: 'dtc', label: 'DTC', icon: '\u26A0\uFE0F' },
  { id: 'parts', label: 'Запчасти', icon: '\u{1F527}' },
];

function _renderTabs() {
  const tabsEl = _container?.querySelector('#kbv2-tabs');
  if (!tabsEl) return;

  tabsEl.innerHTML = TABS.map(tab => `
    <button class="kbv2-tab ${tab.id === _activeTab ? 'kbv2-tab--active' : ''}" data-tab="${tab.id}">
      ${t(`kbv2.tab_${tab.id}`, tab.label)}
    </button>
  `).join('');

  tabsEl.querySelectorAll('.kbv2-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      _activeTab = btn.dataset.tab;
      _searchQuery = '';
      const input = _container?.querySelector('#kbv2-search');
      if (input) input.value = '';
      _navStack = [];
      _renderTabs();
      _renderView();
    });
  });
}

// ═══════════════════════════════════════════════════════════
// Маршрутизатор контента
// ═══════════════════════════════════════════════════════════

async function _renderView() {
  const resultsEl = _container?.querySelector('#kbv2-results');
  if (!resultsEl) return;

  // Если есть поисковый запрос — показать результаты
  if (_searchQuery) {
    await _renderSearchResults(resultsEl);
    return;
  }

  switch (_activeTab) {
    case 'situations': _renderSituationsView(resultsEl); break;
    case 'systems':    await _renderSystemsView(resultsEl); break;
    case 'dtc':        await _renderDTCView(resultsEl); break;
    case 'parts':      await _renderPartsView(resultsEl); break;
    default:           _renderSituationsView(resultsEl);
  }
}

// ═══════════════════════════════════════════════════════════
// Фаза 5: Ситуационная навигация
// ═══════════════════════════════════════════════════════════

function _renderSituationsView(resultsEl) {
  const season = _currentSeason();
  const isBeginner = _persona === 'beginner';

  let html = `
    <div class="kbv2-section-title">${t('kbv2.situations_title', 'Что случилось?')}</div>
    <div class="kbv2-section-subtitle">${isBeginner
      ? t('kbv2.situations_subtitle', 'Выберите ситуацию — мы подскажем, что делать')
      : 'Выберите категорию для быстрого поиска по KB'}</div>
    <div class="kbv2-situations-grid">
  `;

  for (const sit of SITUATION_CLUSTERS) {
    // Эксперт: скрыть дерево решений (он знает что делать)
    if (sit.isDecisionTree && !isBeginner) continue;

    const isSeasonal = sit.season === season;
    const urgColor = _urgencyColor(sit.urgency);
    const isTree = sit.isDecisionTree;

    // Эксперт: показать слои вместо простого описания
    const descText = isBeginner
      ? sit.desc
      : (sit.layers?.length ? `${sit.desc} [${sit.layers.join(', ')}]` : sit.desc);

    html += `
      <div class="kbv2-situation-card ${isTree ? 'kbv2-situation-card--tree' : ''} ${isSeasonal ? 'kbv2-situation-card--seasonal' : ''}"
           data-situation="${sit.id}" style="--sit-color: ${urgColor};">
        <div class="kbv2-situation-card__icon">${sit.icon}</div>
        <div class="kbv2-situation-card__content">
          <div class="kbv2-situation-card__title">${sit.title}</div>
          <div class="kbv2-situation-card__desc">${descText}</div>
        </div>
        ${sit.urgency >= 3 ? `<div class="kbv2-urgency-dot" style="background:${urgColor};"></div>` : ''}
        ${isSeasonal ? `<div class="kbv2-seasonal-badge">${season === 'winter' ? '\u2744\uFE0F' : '\u2600\uFE0F'}</div>` : ''}
      </div>
    `;
  }

  html += `</div>`;

  // Ежедневные советы — только для новичков
  if (isBeginner) {
    html += `
      <div class="kbv2-section-title" style="margin-top:20px;">${t('kbv2.daily_tips_title', 'Ежедневная езда')}</div>
      <div class="kbv2-section-subtitle">${t('kbv2.daily_tips_subtitle', 'Полезные инструкции на каждый день')}</div>
      <div class="kbv2-situations-grid">
    `;
    for (const tip of DAILY_TIPS) {
      html += `
        <div class="kbv2-situation-card kbv2-situation-card--tip"
             data-daily-tip="${tip.id}" style="--sit-color: #4A90D9;">
          <div class="kbv2-situation-card__icon">${tip.icon}</div>
          <div class="kbv2-situation-card__content">
            <div class="kbv2-situation-card__title">${tip.title}</div>
            <div class="kbv2-situation-card__desc">${tip.desc}</div>
          </div>
        </div>
      `;
    }
    html += `</div>`;
  }

  // Если онлайн — показать блок систем снизу
  if (_kb?.isOnline) {
    const stats = _kb.getLayerStats();
    if (stats.length > 0) {
      html += `<div class="kbv2-section-title" style="margin-top:16px;">${t('kbv2.popular_systems', 'Популярные системы')}</div>`;
      html += `<div class="kbv2-systems-compact">`;
      for (const stat of stats.slice(0, 6)) {
        if (stat.id === 'general' || stat.id === 'unknown') continue;
        const color = LAYER_COLORS[stat.id] || '#8B949E';
        html += `
          <div class="kbv2-system-chip" data-layer="${stat.id}" style="--sys-color:${color};">
            <span class="kbv2-system-chip__dot" style="background:${color};"></span>
            ${t(`layers.${stat.id}`, stat.id)}
            <span class="kbv2-system-chip__count">${stat.count}</span>
          </div>
        `;
      }
      html += `</div>`;
    }
  }

  resultsEl.innerHTML = html;

  // Клик по ситуации
  resultsEl.querySelectorAll('.kbv2-situation-card').forEach(el => {
    el.addEventListener('click', () => {
      const sitId = el.dataset.situation;
      const sit = SITUATION_CLUSTERS.find(s => s.id === sitId);
      if (!sit) return;
      if (sit.isDecisionTree) {
        _navStack.push({ type: 'situations' });
        _renderDecisionTree(resultsEl, 'root');
      } else {
        _navStack.push({ type: 'situations' });
        _renderSituationDetail(resultsEl, sit);
      }
    });
  });

  // Клик по ежедневному совету
  resultsEl.querySelectorAll('.kbv2-situation-card[data-daily-tip]').forEach(el => {
    el.addEventListener('click', () => {
      const tipId = el.dataset.dailyTip;
      const tip = DAILY_TIPS.find(t => t.id === tipId);
      if (!tip) return;
      _navStack.push({ type: 'situations' });
      _renderSituationDetail(resultsEl, tip);
    });
  });

  // Клик по системе
  resultsEl.querySelectorAll('.kbv2-system-chip').forEach(el => {
    el.addEventListener('click', async () => {
      const layerId = el.dataset.layer;
      _navStack.push({ type: 'situations' });
      await _renderLayerArticles(resultsEl, layerId);
    });
  });
}

async function _renderSituationDetail(resultsEl, situation) {
  resultsEl.innerHTML = _renderLoadingSpinner();

  // Поиск статей по всем запросам ситуации
  let allEntries = [];
  for (const query of situation.searchQueries) {
    try {
      const resp = await _kb.search(query, { translations: true }, 10);
      for (const r of (resp.results || [])) {
        if (!allEntries.find(e => e.chunk_id === r.chunk_id)) {
          allEntries.push(r);
        }
      }
    } catch (_) { /* игнорируем */ }
  }

  allEntries = allEntries.map(e => getLocalizedEntry(e));
  allEntries = _deduplicateResults(allEntries);

  const urgColor = _urgencyColor(situation.urgency);

  let html = `
    ${_renderBackButton()}

    <div class="kbv2-situation-header" style="--sit-color: ${urgColor};">
      <span class="kbv2-situation-header__icon">${situation.icon}</span>
      <div>
        <div class="kbv2-situation-header__title">${situation.title}</div>
        ${situation.urgency >= 3 ? `<div class="kbv2-urgency-badge" style="color:${urgColor};">${t('kbv2.needs_attention', 'Требует внимания')}</div>` : ''}
      </div>
    </div>

    ${situation.quickAnswer ? `
      <div class="kbv2-quick-answer">
        <div class="kbv2-quick-answer__label">${t('kbv2.quick_answer', 'Быстрый ответ')}</div>
        <div class="kbv2-quick-answer__text">${situation.quickAnswer}</div>
      </div>
    ` : ''}

    <div class="kbv2-section-title">${t('kbv2.related_articles', 'Связанные статьи')} (${allEntries.length})</div>
  `;

  if (allEntries.length > 0) {
    html += allEntries.map(e => _renderBriefCard(e)).join('');
  } else {
    html += `<div class="kbv2-empty">${t('kbv2.no_articles', 'Статей не найдено')}</div>`;
  }

  // Связанные DTC
  const relatedDTC = [];
  for (const entry of allEntries) {
    if (entry.dtc_codes?.length > 0) {
      for (const dtc of entry.dtc_codes) {
        if (!relatedDTC.includes(dtc)) relatedDTC.push(dtc);
      }
    }
  }
  if (relatedDTC.length > 0) {
    html += `
      <div class="kbv2-section-title">${t('kbv2.related_dtc', 'Связанные DTC коды')}</div>
      <div class="kbv2-dtc-chips">
        ${relatedDTC.slice(0, 10).map(dtc => `<span class="kbv2-dtc-chip" data-dtc="${dtc}">${dtc}</span>`).join('')}
      </div>
    `;
  }

  resultsEl.innerHTML = html;
  _bindBackButton(resultsEl);
  _bindBriefCards(resultsEl);
  _bindDTCChips(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Фаза 6: Дерево решений
// ═══════════════════════════════════════════════════════════

function _renderDecisionTree(resultsEl, nodeId) {
  const node = DECISION_TREE[nodeId];
  if (!node) return;

  if (node.type === 'recommendation') {
    _renderRecommendation(resultsEl, node);
    return;
  }

  const urgColor = _urgencyColor(2);

  let html = `
    ${_renderBackButton()}

    <div class="kbv2-decision-node">
      ${node.intro ? `<div class="kbv2-decision-intro">${node.intro}</div>` : ''}
      <div class="kbv2-decision-question">${node.question}</div>
      <div class="kbv2-decision-options">
        ${node.options.map(opt => `
          <button class="kbv2-decision-option" data-next="${opt.next}">
            ${opt.label}
          </button>
        `).join('')}
      </div>
    </div>
  `;

  resultsEl.innerHTML = html;
  _bindBackButton(resultsEl);

  resultsEl.querySelectorAll('.kbv2-decision-option').forEach(btn => {
    btn.addEventListener('click', () => {
      _navStack.push({ type: 'decision', nodeId });
      _renderDecisionTree(resultsEl, btn.dataset.next);
    });
  });
}

async function _renderRecommendation(resultsEl, node) {
  const urgColor = _urgencyColor(node.urgency || 2);

  let html = `
    ${_renderBackButton()}

    <div class="kbv2-recommendation" style="--rec-color: ${urgColor};">
      <div class="kbv2-recommendation__urgency" style="background:${_urgencyBg(node.urgency)};border-color:${urgColor};">
        ${node.urgency >= 4 ? '\u{1F6D1}' : node.urgency >= 3 ? '\u26A0\uFE0F' : '\u2139\uFE0F'}
        <span style="color:${urgColor};font-weight:600;">${node.title}</span>
      </div>
      <div class="kbv2-recommendation__text">${node.text}</div>
      ${node.actions ? `
        <div class="kbv2-recommendation__actions">
          ${node.actions.map(a => `<div class="kbv2-recommendation__action">${a}</div>`).join('')}
        </div>
      ` : ''}
    </div>
  `;

  // Поиск связанных статей
  if (node.searchQuery && _kb?.isOnline) {
    html += `<div class="kbv2-section-title">${t('kbv2.related_articles', 'Связанные статьи')}</div>`;
    resultsEl.innerHTML = html + _renderLoadingSpinner();
    _bindBackButton(resultsEl);

    try {
      const resp = await _kb.search(node.searchQuery, { translations: true }, 5);
      const entries = (resp.results || []).map(e => getLocalizedEntry(e));
      html += entries.map(e => _renderBriefCard(e)).join('');
    } catch (_) {
      html += `<div class="kbv2-empty">${t('kbv2.search_error', 'Не удалось загрузить статьи')}</div>`;
    }
  }

  resultsEl.innerHTML = html;
  _bindBackButton(resultsEl);
  _bindBriefCards(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Фаза 2: Progressive Disclosure — Краткие карточки
// ═══════════════════════════════════════════════════════════

function _renderBriefCard(entry) {
  const color = LAYER_COLORS[entry.layer] || '#8B949E';
  const isEmergency = (entry.urgency || 1) >= 4;
  const stripeColor = isEmergency ? 'var(--status-critical)' : color;

  // Заголовок — фоллбэк на DTC-код если пустой
  let title = _extractTitle(entry);
  if (!title || title.length < 3) {
    const dtcCode = entry.dtc_codes?.[0] || '';
    title = dtcCode ? `DTC ${dtcCode}` : (entry.chunk_id || 'Статья');
  }
  if (_persona === 'beginner') {
    title = _caringTone(title);
  }

  // Превью контента — фоллбэк на layer/system
  const maxPreview = _persona === 'beginner' ? 200 : 500;
  let preview = (entry.content || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
  if (!preview && entry.layer) {
    const layerName = t(`layers.${entry.layer}`, entry.layer);
    preview = `Система: ${layerName}`;
  }
  if (preview.length > maxPreview) preview = preview.slice(0, maxPreview) + '...';
  if (_persona === 'beginner') preview = _caringTone(preview);

  // Критичность
  const urgency = entry.urgency || 1;
  const urgDot = urgency >= 3
    ? `<span class="kbv2-urgency-indicator" style="background:${_urgencyColor(urgency)};"></span>`
    : '';

  // Кнопка действия
  let actionLabel = t('kbv2.read_more', 'Подробнее');
  let actionClass = 'kbv2-action--default';
  const sitType = entry.situation_type || '';
  if (sitType === 'emergency' || isEmergency) {
    actionLabel = t('kbv2.what_to_do', 'Что делать?');
    actionClass = 'kbv2-action--emergency';
  } else if (sitType === 'troubleshooting') {
    actionLabel = t('kbv2.diagnostics', 'Диагностика');
    actionClass = 'kbv2-action--warning';
  } else if (sitType === 'maintenance' || entry.has_procedures) {
    actionLabel = t('kbv2.instruction', 'Инструкция');
    actionClass = 'kbv2-action--info';
  }

  // Trust (только для эксперта)
  const trustLevel = entry.trust_level || 2;
  const trustHTML = _persona === 'expert'
    ? `<span class="kbv2-trust-dots">${'\u25CF'.repeat(trustLevel)}${'\u25CB'.repeat(5 - trustLevel)}</span>`
    : '';

  // Score (только для эксперта)
  const scoreHTML = (_persona === 'expert' && entry.score != null)
    ? `<span class="kbv2-score">${Math.round(entry.score * 100)}%</span>`
    : '';

  return `
    <div class="kbv2-brief-card ${isEmergency ? 'kbv2-brief-card--emergency' : ''}" data-entry-id="${entry.chunk_id}">
      <div class="kbv2-brief-card__stripe" style="background:${stripeColor};"></div>
      <div class="kbv2-brief-card__body">
        <div class="kbv2-brief-card__top">
          ${urgDot}
          <span class="kbv2-brief-card__title">${title}</span>
        </div>
        <div class="kbv2-brief-card__preview">${preview.slice(0, 80)}</div>
        <div class="kbv2-brief-card__footer">
          ${trustHTML} ${scoreHTML}
          <button class="kbv2-brief-card__action ${actionClass}">${actionLabel}</button>
        </div>
      </div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════════════
// Фаза 2: Полная статья
// ═══════════════════════════════════════════════════════════

async function _renderArticleDetail(resultsEl, entry) {
  resultsEl.innerHTML = _renderLoadingSpinner();

  // Всегда загружаем полный чанк с переводами
  if (entry.chunk_id && _kb?.isOnline) {
    const full = await _kb.getChunk(entry.chunk_id);
    if (full) entry = { ...entry, ...full };
  }

  entry = getLocalizedEntry(entry);
  const color = LAYER_COLORS[entry.layer] || '#8B949E';
  const isEmergency = (entry.urgency || 1) >= 4;

  // Рендер контента
  let contentHTML = renderMarkdown(entry.content || '');

  // Заботливый тон для новичка
  if (_persona === 'beginner') {
    contentHTML = _caringTone(contentHTML);
  }

  // Глоссарий-тултипы (Фаза 3)
  if (_glossary) {
    contentHTML = _glossary.annotateHTML(contentHTML, _persona);
  }

  const srcInfo = SOURCE_BADGES[entry.source] || { icon: '\u{1F4C4}', label: entry.source || '' };

  let html = `
    ${_renderBackButton()}

    ${isEmergency ? `
      <div class="kbv2-emergency-banner">
        <span class="kbv2-emergency-banner__icon">\u26A0\uFE0F</span>
        <span>${_persona === 'beginner'
          ? t('kbv2.emergency_caring', 'Обнаружено нетипичное поведение. Давайте разберёмся.')
          : t('kbv2.emergency_expert', 'Критическая информация по безопасности')
        }</span>
      </div>
    ` : ''}

    <div class="kbv2-article-header">
      <div class="kbv2-article-stripe" style="background:${isEmergency ? 'var(--status-critical)' : color};"></div>
      <div class="kbv2-article-meta">
        <h3 class="kbv2-article-title">${_persona === 'beginner' ? _caringTone(entry.title || '') : (entry.title || '')}</h3>
        <div class="kbv2-article-badges">
          <span>${entry.model === 'l9' ? 'Li L9' : entry.model === 'l7' ? 'Li L7' : 'All'}</span>
          <span>${srcInfo.icon} ${srcInfo.label}</span>
          ${entry.has_procedures ? `<span class="kbv2-badge kbv2-badge--accent">${t('kbv2.step_by_step', 'Пошаговая')}</span>` : ''}
          ${entry.has_warnings ? `<span class="kbv2-badge kbv2-badge--warning">${t('kbv2.has_warnings', 'Предупреждение')}</span>` : ''}
        </div>
      </div>
    </div>

    <div class="kbv2-article-content">${contentHTML}</div>
  `;

  // DTC бейджи (Фаза 4)
  if (entry.dtc_codes?.length > 0) {
    html += `
      <div class="kbv2-section-title">${t('kbv2.dtc_codes', 'Коды ошибок')}</div>
      <div class="kbv2-dtc-chips">
        ${entry.dtc_codes.map(dtc => `<span class="kbv2-dtc-chip" data-dtc="${dtc}">${dtc}</span>`).join('')}
      </div>
    `;
  }

  // Глоссарий-теги (из glossary_terms или fallback по layer)
  {
    let compTerms = entry.glossary_terms?.length > 0 ? entry.glossary_terms : [];
    // Fallback: если нет glossary_terms, показываем компоненты из layer
    if (compTerms.length === 0 && entry.layer && _glossaryData?.components) {
      const layerComps = [];
      for (const [gid, names] of Object.entries(_glossaryData.components)) {
        const parts = gid.split('@');
        if (parts[1] === entry.layer || (!parts[1] && entry.layer)) {
          layerComps.push(gid);
        }
      }
      compTerms = layerComps.slice(0, 12);
    }
    const tags = _renderGlossaryTags(compTerms, color);
    if (tags) {
      html += `
        <div class="kbv2-section-title">${t('kbv2.components', 'Связанные компоненты')}</div>
        <div class="kbv2-tags-wrap">${tags}</div>
      `;
    }
  }

  // 3D-интеграция (Фаза 7)
  if (entry.glossary_terms?.length > 0) {
    const firstGid = entry.glossary_terms[0];
    html += `
      <button class="kbv2-3d-btn" data-gid="${firstGid}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        ${t('kbv2.show_in_3d', 'Показать в 3D')}
      </button>
    `;
  }

  // Пошаговый wizard (Фаза 2)
  if (entry.has_procedures) {
    html += `
      <button class="kbv2-wizard-btn" data-entry-id="${entry.chunk_id}">
        ${t('kbv2.start_wizard', 'Начать пошагово')}
      </button>
    `;
  }

  resultsEl.innerHTML = html;
  _bindBackButton(resultsEl);
  _bindDTCChips(resultsEl);
  _bindGlossaryTerms(resultsEl);
  _bindCompTagsV2(resultsEl);

  // 3D кнопка
  resultsEl.querySelectorAll('.kbv2-3d-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const gid = btn.dataset.gid;
      if (gid) {
        window.__llcar_selectedComponent = gid;
        emit('app:navigate', { screen: 'twin' });
        setTimeout(() => emit('component:select', { glossaryId: gid, source: 'kb-v2' }), 300);
      }
    });
  });

  // Wizard кнопка
  resultsEl.querySelectorAll('.kbv2-wizard-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      _navStack.push({ type: 'article', entry });
      _renderProcedureWizard(resultsEl, entry);
    });
  });
}

// ═══════════════════════════════════════════════════════════
// Фаза 2: Пошаговый wizard
// ═══════════════════════════════════════════════════════════

function _renderProcedureWizard(resultsEl, entry) {
  // Парсим контент по нумерованным спискам
  const content = entry.content || '';
  const steps = [];

  // Ищем нумерованные шаги: "1. ", "2. " и т.д.
  const stepRegex = /(?:^|\n)\s*(\d+)[\.\)]\s+([\s\S]*?)(?=(?:\n\s*\d+[\.\)]\s)|\n\n|$)/g;
  let match;
  while ((match = stepRegex.exec(content)) !== null) {
    steps.push({
      num: parseInt(match[1]),
      text: match[2].trim(),
    });
  }

  // Если не нашли нумерованные шаги — разбиваем по абзацам
  if (steps.length < 2) {
    const paras = content.split(/\n\n+/).filter(p => p.trim().length > 20);
    paras.forEach((p, i) => steps.push({ num: i + 1, text: p.trim() }));
  }

  if (steps.length === 0) {
    steps.push({ num: 1, text: content });
  }

  let currentStep = 0;

  function renderStep() {
    const step = steps[currentStep];
    let stepHTML = renderMarkdown(step.text);
    if (_persona === 'beginner') stepHTML = _caringTone(stepHTML);

    resultsEl.innerHTML = `
      ${_renderBackButton()}

      <div class="kbv2-wizard">
        <div class="kbv2-wizard__progress">
          <span class="kbv2-wizard__step-label">${t('kbv2.step', 'Шаг')} ${currentStep + 1} ${t('kbv2.of', 'из')} ${steps.length}</span>
          <div class="kbv2-wizard__progress-bar">
            <div class="kbv2-wizard__progress-fill" style="width:${((currentStep + 1) / steps.length) * 100}%;"></div>
          </div>
        </div>

        <div class="kbv2-wizard__content">${stepHTML}</div>

        <div class="kbv2-wizard__nav">
          ${currentStep > 0 ? `<button class="kbv2-wizard__prev">${t('common.back', 'Назад')}</button>` : '<div></div>'}
          ${currentStep < steps.length - 1
            ? `<button class="kbv2-wizard__next">${t('kbv2.next_step', 'Далее')}</button>`
            : `<button class="kbv2-wizard__done">${t('kbv2.done', 'Готово')}</button>`
          }
        </div>
      </div>
    `;

    _bindBackButton(resultsEl);

    resultsEl.querySelector('.kbv2-wizard__prev')?.addEventListener('click', () => {
      currentStep--;
      renderStep();
    });
    resultsEl.querySelector('.kbv2-wizard__next')?.addEventListener('click', () => {
      currentStep++;
      renderStep();
    });
    resultsEl.querySelector('.kbv2-wizard__done')?.addEventListener('click', () => {
      _goBack(resultsEl);
    });
  }

  renderStep();
}

// ═══════════════════════════════════════════════════════════
// Фаза 4: DTC → KB интеграция
// ═══════════════════════════════════════════════════════════

async function _renderDTCView(resultsEl) {
  if (!_kb?.isOnline) {
    resultsEl.innerHTML = `<div class="kbv2-empty">${t('kbv2.need_api', 'Требуется подключение к API')}</div>`;
    return;
  }

  resultsEl.innerHTML = _renderLoadingSpinner();

  // Если есть запрос — искать конкретный DTC
  if (_searchQuery) {
    const code = _searchQuery.trim().toUpperCase();
    try {
      const dtcResult = await _kb.getDTC(code);
      if (dtcResult && (dtcResult.chunks?.length > 0 || dtcResult.description)) {
        _renderDTCDetail(resultsEl, code, dtcResult);
        return;
      }
    } catch (_) { /* продолжаем */ }

    // Фоллбэк — текстовый поиск
    const entries = (await _kb.search(_searchQuery, { translations: true }, 20)).results || [];
    const localized = entries.map(e => getLocalizedEntry(e));
    if (localized.length > 0) {
      resultsEl.innerHTML = `
        ${_renderBackButton()}
        <div class="kbv2-section-title">DTC: ${_searchQuery} (${localized.length})</div>
        ${localized.map(e => _renderBriefCard(e)).join('')}
      `;
      _bindBackButton(resultsEl);
      _bindBriefCards(resultsEl);
      return;
    }
  }

  // Показать все DTC сгруппированные (с дедупликацией по коду)
  const allDTC = (await _kb.browse(null, { content_type: 'dtc' }, 500)).results || [];
  const localized = _deduplicateDTC(allDTC.map(e => getLocalizedEntry(e)));

  const groups = { P: [], C: [], B: [], U: [], other: [] };
  const groupLabels = {
    P: 'Двигатель и трансмиссия', C: 'Шасси, подвеска, тормоза',
    B: 'Кузов, салон, освещение', U: 'CAN-шина, связь модулей', other: 'Прочие',
  };

  for (const entry of localized) {
    const code = (entry.dtc_codes?.[0] || entry.title || '').toUpperCase();
    const prefix = code.match(/[PCBU]/)?.[0] || 'other';
    (groups[prefix] || groups.other).push(entry);
  }

  let html = `
    <div class="kbv2-section-title">DTC ${t('kbv2.error_codes', 'коды ошибок')} (${localized.length})</div>
    <div class="kbv2-dtc-hint">${t('kbv2.dtc_hint', 'Введите код (напр. P0300) в поиске')}</div>
  `;

  for (const [prefix, items] of Object.entries(groups)) {
    if (items.length === 0) continue;
    html += `<div class="kbv2-group-title">${prefix} \u2014 ${groupLabels[prefix]} (${items.length})</div>`;
    html += items.map(e => _renderBriefCard(e)).join('');
  }

  resultsEl.innerHTML = html;
  _bindBriefCards(resultsEl);
}

function _renderDTCDetail(resultsEl, code, dtcData) {
  const severity = dtcData.severity || 'medium';
  const severityConfig = {
    low: { color: 'var(--status-healthy)', label: t('kbv2.severity_low', 'Низкая'), canDrive: t('kbv2.can_drive_yes', 'Да, безопасно') },
    medium: { color: 'var(--status-warning)', label: t('kbv2.severity_medium', 'Средняя'), canDrive: t('kbv2.can_drive_caution', 'Да, с осторожностью') },
    high: { color: 'var(--status-critical)', label: t('kbv2.severity_high', 'Высокая'), canDrive: t('kbv2.can_drive_no', 'Нет, опасно') },
  };
  const sev = severityConfig[severity] || severityConfig.medium;
  const desc = _persona === 'beginner'
    ? _caringTone(dtcData.description || `Код ${code}`)
    : (dtcData.description || `Код ${code}`);

  let html = `
    ${_renderBackButton()}

    <div class="kbv2-dtc-detail">
      <div class="kbv2-dtc-detail__code" style="color:${sev.color};">${code}</div>
      <div class="kbv2-dtc-detail__desc">${desc}</div>

      <div class="kbv2-dtc-detail__grid">
        <div class="kbv2-dtc-detail__item">
          <span class="kbv2-dtc-detail__label">${t('kbv2.severity', 'Серьёзность')}</span>
          <span class="kbv2-dtc-detail__value" style="color:${sev.color};">${sev.label}</span>
        </div>
        <div class="kbv2-dtc-detail__item">
          <span class="kbv2-dtc-detail__label">${t('kbv2.can_drive', 'Можно ехать?')}</span>
          <span class="kbv2-dtc-detail__value">${sev.canDrive}</span>
        </div>
        ${dtcData.system ? `
        <div class="kbv2-dtc-detail__item">
          <span class="kbv2-dtc-detail__label">${t('kbv2.system', 'Система')}</span>
          <span class="kbv2-dtc-detail__value">${dtcData.system}</span>
        </div>
        ` : ''}
      </div>
    </div>
  `;

  // Связанные статьи
  const chunks = (dtcData.chunks || []).map(e => getLocalizedEntry(e));
  if (chunks.length > 0) {
    html += `<div class="kbv2-section-title">${t('kbv2.related_articles', 'Связанные статьи')}</div>`;
    html += chunks.map(e => _renderBriefCard(e)).join('');
  }

  resultsEl.innerHTML = html;
  _bindBackButton(resultsEl);
  _bindBriefCards(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Системы и поиск
// ═══════════════════════════════════════════════════════════

async function _renderSystemsView(resultsEl) {
  if (!_kb?.isOnline) {
    resultsEl.innerHTML = `<div class="kbv2-empty">${t('kbv2.need_api', 'Требуется подключение к API')}</div>`;
    return;
  }

  const stats = _kb.getLayerStats();
  // Mock sparkline данные (стабильные тренды)
  const mockSparklines = {
    engine: [80, 78, 82, 79, 85, 83, 80], brakes: [90, 88, 92, 91, 89, 90, 92],
    ev: [95, 93, 94, 96, 95, 94, 95], battery: [88, 87, 85, 86, 84, 85, 83],
    sensors: [92, 91, 93, 92, 94, 93, 92], hvac: [85, 86, 84, 87, 86, 85, 86],
  };

  let html = `<div class="kbv2-section-title">${t('kbv2.all_systems', 'Все системы')}</div>`;

  for (const stat of stats) {
    if (stat.id === 'general' || stat.id === 'unknown') continue;
    const color = LAYER_COLORS[stat.id] || '#8B949E';
    const layerLabel = t(`layers.${stat.id}`, stat.id);
    const sparkData = mockSparklines[stat.id];
    const sparkColor = color;

    html += `
      <div class="kbv2-system-card" data-layer="${stat.id}">
        <div class="kbv2-system-card__icon" style="background:${color}20;">
          <span style="color:${color};font-size:16px;">\u2699\uFE0F</span>
        </div>
        <div class="kbv2-system-card__info">
          <span class="kbv2-system-card__title">${layerLabel}</span>
          <span class="kbv2-system-card__count">${stat.count} ${t('knowledge.articles', 'статей')}</span>
        </div>
        ${sparkData ? `<div class="kbv2-system-card__spark">${renderSparkline(sparkData, 50, 18, sparkColor)}</div>` : ''}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
      </div>
    `;
  }

  resultsEl.innerHTML = html;

  resultsEl.querySelectorAll('.kbv2-system-card').forEach(el => {
    el.addEventListener('click', async () => {
      _navStack.push({ type: 'systems' });
      await _renderLayerArticles(resultsEl, el.dataset.layer);
    });
  });
}

async function _renderLayerArticles(resultsEl, layerId) {
  resultsEl.innerHTML = _renderLoadingSpinner();
  const layerLabel = t(`layers.${layerId}`, layerId);
  const resp = await _kb.browse(layerId, { model: _activeVehicle || undefined }, 50);
  const entries = (resp.results || []).map(e => getLocalizedEntry(e));
  const deduped = _deduplicateResults(entries);

  let html = `
    ${_renderBackButton()}
    <div class="kbv2-section-title">${layerLabel} (${resp.total || deduped.length})</div>
    ${deduped.map(e => _renderBriefCard(e)).join('')}
  `;

  if (deduped.length === 0) {
    html += `<div class="kbv2-empty">${t('kbv2.no_articles', 'Статей не найдено')}</div>`;
  }

  resultsEl.innerHTML = html;
  _bindBackButton(resultsEl);
  _bindBriefCards(resultsEl);
}

async function _renderPartsView(resultsEl) {
  if (!_kb?.isOnline) {
    resultsEl.innerHTML = `<div class="kbv2-empty">${t('kbv2.need_api', 'Требуется подключение к API')}</div>`;
    return;
  }
  resultsEl.innerHTML = _renderLoadingSpinner();

  const stats = await _kb.getPartsStats();
  if (!stats?.total_parts) {
    resultsEl.innerHTML = `<div class="kbv2-empty">${t('kbv2.parts_empty', 'Каталог деталей не загружен')}</div>`;
    return;
  }

  let html = `
    <div class="kbv2-section-title">${t('kbv2.parts_catalog', 'Каталог запчастей')}</div>
    <div class="kbv2-parts-summary">
      <span class="kbv2-parts-summary__count">${stats.total_parts.toLocaleString()}</span>
      <span class="kbv2-parts-summary__label">${t('kbv2.parts_total', 'деталей')}</span>
    </div>
  `;

  for (const sys of stats.systems) {
    const lang = _i18n?.lang || 'ru';
    const sysName = (lang === 'ru' && SYSTEM_NAME_RU[sys.system_en])
      ? SYSTEM_NAME_RU[sys.system_en]
      : (sys.system_en || sys.system_zh);
    html += `
      <div class="kbv2-system-card kbv2-parts-system" data-system="${sys.system_en}">
        <div class="kbv2-system-card__icon" style="background:rgba(120,144,156,0.2);">
          <span style="font-size:14px;">\u{1F527}</span>
        </div>
        <div class="kbv2-system-card__info">
          <span class="kbv2-system-card__title">${sysName}</span>
          <span class="kbv2-system-card__count">${sys.part_count} ${t('kbv2.parts_short', 'дет.')}</span>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
      </div>
    `;
  }

  resultsEl.innerHTML = html;

  resultsEl.querySelectorAll('.kbv2-parts-system').forEach(el => {
    el.addEventListener('click', async () => {
      _navStack.push({ type: 'parts' });
      const sysEn = el.dataset.system;
      resultsEl.innerHTML = _renderLoadingSpinner();
      const resp = await _kb.searchParts('', { system: sysEn, limit: 200 });
      const allParts = resp.results || [];
      const lang2 = _i18n?.lang || 'ru';
      const sysTitle = (lang2 === 'ru' && SYSTEM_NAME_RU[sysEn]) ? SYSTEM_NAME_RU[sysEn] : sysEn;

      // Группировка по диаграмме (как в старом knowledge.js)
      const groups = {};
      for (const part of allParts) {
        const key = part.diagram_image || part.source_image || '__no_image__';
        if (!groups[key]) groups[key] = [];
        groups[key].push(part);
      }
      const sortedGroups = Object.entries(groups).sort((a, b) => {
        const pageA = a[1][0]?.page_idx ?? 9999;
        const pageB = b[1][0]?.page_idx ?? 9999;
        return pageA - pageB;
      });

      let html = `
        ${_renderBackButton()}
        <div class="kbv2-section-title">${sysTitle}</div>
        <div style="font-size:11px;color:var(--text-secondary);margin-bottom:8px;">
          ${sortedGroups.length} диаграмм, ${allParts.length} деталей
        </div>
      `;

      for (const [imgKey, parts] of sortedGroups) {
        const imgSrc = imgKey !== '__no_image__' ? PARTS_IMG_BASE + '/' + imgKey : '';

        // Диаграмма каталога
        if (imgSrc) {
          html += `<div style="margin:8px 0 0;border-radius:10px 10px 0 0;border:1px solid var(--border-default);border-bottom:none;background:#f5f5f5;text-align:center;">
            <img class="kbv2-diagram-img" src="${imgSrc}" style="max-width:100%;height:auto;display:inline-block;border-radius:10px 10px 0 0;cursor:pointer;" onerror="this.parentElement.style.display='none'" />
          </div>`;
        }

        // Список деталей под диаграммой
        html += `<div style="margin:0 0 16px;border-radius:${imgSrc ? '0 0 10px 10px' : '10px'};border:1px solid var(--border-default);${imgSrc ? 'border-top:none;' : ''}background:var(--bg-secondary);padding:8px;">`;
        for (const part of parts) {
          const name = part.part_name_ru || part.part_name_en || part.part_name_zh || part.part_number;
          html += `
            <div class="kbv2-part-item" data-part="${part.part_number}">
              ${part.hotspot_id ? `<span class="kbv2-part-item__hotspot">#${part.hotspot_id}</span>` : ''}
              <span class="kbv2-part-item__number">${part.part_number}</span>
              <span class="kbv2-part-item__name">${name}</span>
            </div>
          `;
        }
        html += `</div>`;
      }

      resultsEl.innerHTML = html;
      _bindBackButton(resultsEl);

      // Клик на диаграмму → открыть полный размер
      resultsEl.querySelectorAll('.kbv2-diagram-img').forEach(img => {
        img.addEventListener('click', () => window.open(img.src, '_blank'));
      });

      // Клик на деталь → детальный вид
      resultsEl.querySelectorAll('.kbv2-part-item').forEach(el => {
        el.addEventListener('click', () => {
          const partNumber = el.dataset.part;
          const partName = el.querySelector('.kbv2-part-item__name')?.textContent || '';
          _navStack.push({ type: 'parts-system', system: sysEn });
          _renderPartDetail(resultsEl, partNumber, partName);
        });
      });
    });
  });
}

/** Детальный вид одной запчасти */
async function _renderPartDetail(resultsEl, partNumber, partName) {
  resultsEl.innerHTML = _renderLoadingSpinner();

  // Загружаем данные детали
  let partData = null;
  try {
    const resp = await fetch(`${PARTS_IMG_BASE}/parts/${encodeURIComponent(partNumber)}`);
    if (resp.ok) partData = await resp.json();
  } catch (_) { /* ignore */ }

  const part = partData?.results?.[0];

  // Ищем связанные KB-статьи
  let relatedArticles = [];
  const searchTerm = part?.part_name_zh || part?.part_name_en || partName || partNumber;
  try {
    const resp = await _kb.search(searchTerm, { translations: true }, 5);
    relatedArticles = (resp.results || []).map(e => getLocalizedEntry(e));
  } catch (_) { /* ignore */ }

  // Диаграмма
  const diagramSrc = part?.diagram_image ? (PARTS_IMG_BASE + '/' + part.diagram_image) : '';
  const sourceSrc = part?.source_image ? (PARTS_IMG_BASE + '/' + part.source_image) : '';
  const imgSrc = diagramSrc || sourceSrc;
  const displayName = part
    ? (part.part_name_ru || part.part_name_en || part.part_name_zh || partNumber)
    : (partName || partNumber);

  const lang = _i18n?.lang || 'ru';
  const sysLabel = part?.system_en
    ? ((lang === 'ru' && SYSTEM_NAME_RU[part.system_en]) ? SYSTEM_NAME_RU[part.system_en] : part.system_en)
    : '';

  let html = `
    ${_renderBackButton()}

    ${imgSrc ? `<div style="margin:12px 0;border-radius:12px;overflow:hidden;border:1px solid var(--border-default);background:var(--bg-secondary);text-align:center;padding:8px;min-height:200px;">
      <img class="kbv2-part-detail-img" src="${imgSrc}" alt="Диаграмма каталога" style="width:100%;max-height:500px;object-fit:contain;display:inline-block;cursor:pointer;border-radius:8px;" onerror="console.warn('[KB-V2] Image load failed:', this.src); this.alt='Диаграмма недоступна'; this.style.padding='20px'; this.style.color='#999';" />
    </div>` : '<div style="text-align:center;padding:16px;color:var(--text-tertiary);font-size:12px;">Диаграмма каталога недоступна</div>'}

    <div style="background:var(--bg-secondary);border-radius:12px;padding:16px;margin:8px 0;">
      <div style="font-size:16px;font-weight:600;color:var(--text-primary);margin-bottom:8px;">${displayName}</div>
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
        <span style="font-family:monospace;font-size:13px;color:var(--accent-primary);font-weight:600;background:rgba(0,200,150,0.1);padding:4px 10px;border-radius:6px;">${partNumber}</span>
        ${part?.hotspot_id ? `<span style="font-size:11px;color:var(--text-tertiary);background:var(--bg-tertiary,#2a2d32);padding:4px 10px;border-radius:6px;"># ${part.hotspot_id}</span>` : ''}
      </div>
      <div style="display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--text-secondary);">
        ${sysLabel ? `<div><span style="color:var(--text-tertiary);">Система:</span> ${sysLabel}</div>` : ''}
        ${part?.subsystem_en ? `<div><span style="color:var(--text-tertiary);">Подсистема:</span> ${part.subsystem_ru || part.subsystem_en}</div>` : ''}
        ${part?.page_idx ? `<div><span style="color:var(--text-tertiary);">Стр.:</span> ${part.page_idx}</div>` : ''}
      </div>
    </div>
  `;

  // Связанные статьи
  if (relatedArticles.length > 0) {
    html += `<div class="kbv2-section-title" style="margin-top:12px;">${t('kbv2.related_articles', 'Связанные статьи')} (${relatedArticles.length})</div>`;
    html += relatedArticles.map(e => _renderBriefCard(e)).join('');
  }

  resultsEl.innerHTML = html;
  _bindBackButton(resultsEl);
  _bindBriefCards(resultsEl);

  // Клик на диаграмму → полный размер
  resultsEl.querySelector('.kbv2-part-detail-img')?.addEventListener('click', function() {
    window.open(this.src, '_blank');
  });
}

async function _renderSearchResults(resultsEl) {
  if (!_kb?.isOnline) {
    resultsEl.innerHTML = `<div class="kbv2-empty">${t('kbv2.need_api', 'Требуется подключение к API')}</div>`;
    return;
  }

  resultsEl.innerHTML = _renderLoadingSpinner();

  const resp = await _kb.search(_searchQuery, { translations: true }, 30);
  const entries = (resp.results || []).map(e => getLocalizedEntry(e));
  const deduped = _deduplicateResults(entries);

  // Сортировка: экстренные наверху
  deduped.sort((a, b) => {
    const aUrg = (a.urgency || 1) >= 4 ? 1 : 0;
    const bUrg = (b.urgency || 1) >= 4 ? 1 : 0;
    if (aUrg !== bUrg) return bUrg - aUrg;
    return (b.score || 0) - (a.score || 0);
  });

  let html = `
    <div class="kbv2-section-title">${t('kbv2.search_results', 'Результаты')} (${resp.total || deduped.length})</div>
  `;

  if (deduped.length > 0) {
    html += deduped.map(e => _renderBriefCard(e)).join('');
  } else {
    html += `<div class="kbv2-empty">${t('kbv2.no_results', 'Ничего не найдено. Попробуйте изменить запрос.')}</div>`;
  }

  resultsEl.innerHTML = html;
  _bindBriefCards(resultsEl);
}

// ═══════════════════════════════════════════════════════════
// Вспомогательные рендер-функции
// ═══════════════════════════════════════════════════════════

function _renderBackButton() {
  return `
    <button class="kbv2-back-btn" id="kbv2-back">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 18-6-6 6-6"/></svg>
      ${t('common.back', 'Назад')}
    </button>
  `;
}

function _renderLoadingSpinner() {
  return `<div class="kbv2-loading">
    <svg width="18" height="18" viewBox="0 0 24 24" style="animation:spin 1s linear infinite;" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
    ${t('common.loading', 'Загрузка...')}
  </div>`;
}

// Whitelist RU-перевод для тегов (аналогично Expert mode)
const _GLOSSARY_RU_V2 = {
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

function _renderGlossaryTags(terms, color) {
  if (!terms || terms.length === 0) return '';
  const seen = new Set();
  const rendered = [];
  for (const tag of terms) {
    const raw = tag.split('@')[0].replace(/_/g, ' ').toLowerCase().trim();
    const label = _GLOSSARY_RU_V2[raw];
    if (!label) continue; // whitelist only — skip unknown terms
    if (seen.has(label)) continue;
    seen.add(label);
    rendered.push(`<span class="kbv2-tag kbv2-comp-link" data-term="${raw}" style="cursor:pointer;color:${color};background:${color}15;border-color:${color}40;">${label}</span>`);
  }
  return rendered.join('');
}

// Маппинг glossary term → система каталога запчастей
const _TERM_TO_SYSTEM_V2 = {
  'brake': 'Service Brake System', 'brake pedal': 'Service Brake System', 'brake system': 'Service Brake System',
  'steering wheel': 'Steering System',
  'seat belt': 'Passive Safety System', 'safety belt': 'Passive Safety System', 'airbag': 'Passive Safety System',
  'sensor': 'Autonomous Driving System', 'camera': 'Autonomous Driving System', 'radar': 'Autonomous Driving System', 'lidar': 'Autonomous Driving System',
  'side mirror': 'Exterior Trim System', 'mirror': 'Exterior Trim System',
  'windshield': 'Body Structure',
  'ambient lighting': 'Lighting System', 'headlight': 'Lighting System', 'taillight': 'Lighting System', 'turn signal': 'Lighting System',
  'charging port': 'Power Battery System', 'accumulator': 'Power Battery System', 'battery': 'Power Battery System', 'voltage': 'Power Battery System', 'traction battery hv battery': 'Power Battery System',
  'range extender': 'Engine Assembly', 'engine': 'Engine Assembly', 'motor': 'Power Drive System', 'coolant': 'Engine Assembly', 'radiator': 'Engine Assembly',
  'smart key': 'Smart Cabin / Infotainment', 'hud head up display': 'Smart Cabin / Infotainment',
  'lane keep assist': 'Autonomous Driving System',
  'air conditioning system': 'HVAC & Thermal Management',
  'suspension': 'Front Suspension', 'tire': 'Front Suspension', 'wheel': 'Front Suspension',
  'door': 'Closures (Doors, Hood, Tailgate)', 'window': 'Closures (Doors, Hood, Tailgate)', 'trunk': 'Closures (Doors, Hood, Tailgate)', 'roof': 'Body Structure',
  'horn': 'Power & Signal Distribution', 'wiper': 'Exterior Trim System',
  'fuse': 'Power & Signal Distribution', 'relay': 'Power & Signal Distribution', 'connector': 'Power & Signal Distribution',
  'pedal': 'Service Brake System',
};

/** Привязать клик по тегам компонентов → диаграмма системы или поиск статей */
function _bindCompTagsV2(container) {
  container?.querySelectorAll('.kbv2-comp-link[data-term]').forEach(el => {
    el.addEventListener('click', async (ev) => {
      ev.stopPropagation();
      const term = el.dataset.term;
      if (!term) return;
      const system = _TERM_TO_SYSTEM_V2[term];
      if (system) {
        // Переход к диаграмме системы
        _activeTab = 'parts';
        _navStack.push({ type: 'article' });
        const resultsEl = _container?.querySelector('#kbv2-results');
        if (!resultsEl) return;
        resultsEl.innerHTML = _renderLoadingSpinner();
        const resp = await _kb.searchParts('', { system, limit: 200 });
        const allParts = resp.results || [];
        const sysTitle = SYSTEM_NAME_RU[system] || system;

        const groups = {};
        for (const part of allParts) {
          const key = part.diagram_image || part.source_image || '__no_image__';
          if (!groups[key]) groups[key] = [];
          groups[key].push(part);
        }
        const sortedGroups = Object.entries(groups).sort((a, b) =>
          (a[1][0]?.page_idx ?? 9999) - (b[1][0]?.page_idx ?? 9999));

        let html = `${_renderBackButton()}
          <div class="kbv2-section-title">${sysTitle}</div>
          <div style="font-size:11px;color:var(--text-secondary);margin-bottom:8px;">
            ${sortedGroups.length} диаграмм, ${allParts.length} деталей
          </div>`;

        for (const [imgKey, parts] of sortedGroups) {
          const imgSrc = imgKey !== '__no_image__' ? PARTS_IMG_BASE + '/' + imgKey : '';
          if (imgSrc) {
            html += `<div style="margin:8px 0 0;border-radius:10px 10px 0 0;border:1px solid var(--border-default);border-bottom:none;background:#f5f5f5;text-align:center;">
              <img class="kbv2-diagram-img" src="${imgSrc}" style="max-width:100%;height:auto;display:inline-block;border-radius:10px 10px 0 0;cursor:pointer;" onerror="this.parentElement.style.display='none'" />
            </div>`;
          }
          html += `<div style="margin:0 0 16px;border-radius:${imgSrc ? '0 0 10px 10px' : '10px'};border:1px solid var(--border-default);${imgSrc ? 'border-top:none;' : ''}background:var(--bg-secondary);padding:8px;">`;
          for (const part of parts) {
            const name = part.part_name_ru || part.part_name_en || part.part_name_zh || part.part_number;
            html += `<div class="kbv2-part-item" data-part="${part.part_number}">
              ${part.hotspot_id ? `<span class="kbv2-part-item__hotspot">#${part.hotspot_id}</span>` : ''}
              <span class="kbv2-part-item__number">${part.part_number}</span>
              <span class="kbv2-part-item__name">${name}</span>
            </div>`;
          }
          html += `</div>`;
        }

        resultsEl.innerHTML = html;
        _bindBackButton(resultsEl);
        resultsEl.querySelectorAll('.kbv2-diagram-img').forEach(img => {
          img.addEventListener('click', () => window.open(img.src, '_blank'));
        });
        resultsEl.querySelectorAll('.kbv2-part-item').forEach(el2 => {
          el2.addEventListener('click', () => {
            const pn = el2.dataset.part;
            const pName = el2.querySelector('.kbv2-part-item__name')?.textContent || '';
            _navStack.push({ type: 'parts-system', system });
            _renderPartDetail(resultsEl, pn, pName);
          });
        });
      } else {
        // Fallback: текстовый поиск по русскому названию
        const ruLabel = el.textContent.trim();
        if (ruLabel) {
          _searchQuery = ruLabel;
          const input = _container?.querySelector('#kbv2-search');
          if (input) input.value = ruLabel;
          _renderContent();
        }
      }
    });
  });
}

// ── Извлечение осмысленного заголовка ──
const _GENERIC_TITLES = new Set([
  'предупреждение', 'warning', '警告', 'внимание', 'примечание',
  'note', '注意', '提示', '用户手册', '用车场景', 'caution',
]);

function _extractTitle(entry) {
  let title = (entry.title || '').trim();
  title = title.replace(/^[IVXLCDM]+\.\s+/, '');
  const titleLower = title.toLowerCase().trim();
  if (!_GENERIC_TITLES.has(titleLower) || !entry.content) return title;

  let text = entry.content;
  text = text.replace(/^#{0,3}\s*(Предупреждение|Warning|Примечание|Внимание|Caution|注意|警告|提示)\s*/i, '');
  text = text.replace(/\n/g, ' ').replace(/<[^>]+>/g, '').replace(/!\[.*?\]\(.*?\)/g, '')
    .replace(/#{1,3}\s*/g, '').replace(/^[●•▪▸\-–—\d\.\)\s]+/, '').replace(/\s{2,}/g, ' ').trim();

  if (text.length < 10) return title;
  const sentenceEnd = text.match(/^(.{15,100}?[.!。])\s/);
  if (sentenceEnd) {
    let sent = sentenceEnd[1];
    if (sent.length > 70) {
      const commaIdx = sent.indexOf(',', 25);
      if (commaIdx > 25 && commaIdx < 70) sent = sent.slice(0, commaIdx);
    }
    return sent;
  }
  if (text.length <= 70) return text;
  const cut = text.lastIndexOf(' ', 70);
  return text.slice(0, cut > 25 ? cut : 70) + '\u2026';
}

// ── Дедупликация ──
function _deduplicateDTC(entries) {
  if (!entries || entries.length <= 1) return entries;
  const byCode = new Map();
  for (const entry of entries) {
    const code = entry.dtc_codes?.[0] || _extractDTCCode(entry.title) || '';
    if (!code) continue;
    const existing = byCode.get(code);
    if (!existing) {
      byCode.set(code, entry);
    } else {
      const existTitle = existing.title || '';
      const newTitle = entry.title || '';
      const existHasDesc = existTitle.length > code.length + 20;
      const newHasDesc = newTitle.length > code.length + 20;
      if (newHasDesc && !existHasDesc) byCode.set(code, entry);
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

function _deduplicateResults(entries) {
  if (!entries || entries.length <= 1) return entries;
  const result = [];
  const fingerprints = [];
  for (const entry of entries) {
    const raw = (entry.content || '').replace(/\s+/g, ' ').trim().slice(0, 200);
    const words = raw.toLowerCase().replace(/[●•▪▸\-–—\d\.\)\(\[\]:,;!?。]/g, ' ')
      .split(/\s+/).filter(w => w.length >= 3);
    const wordSet = new Set(words.slice(0, 30));
    let isDuplicate = false;
    for (const existing of fingerprints) {
      let intersection = 0;
      for (const w of wordSet) { if (existing.has(w)) intersection++; }
      const union = wordSet.size + existing.size - intersection;
      if (union > 0 && intersection / union > 0.6) { isDuplicate = true; break; }
    }
    if (!isDuplicate) { fingerprints.push(wordSet); result.push(entry); }
  }
  return result;
}

// ═══════════════════════════════════════════════════════════
// Привязка событий
// ═══════════════════════════════════════════════════════════

function _bindMainEvents() {
  // Поиск
  const searchInput = _container?.querySelector('#kbv2-search');
  if (searchInput) {
    let debounce = null;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        _searchQuery = searchInput.value.trim();
        _renderView();
      }, 400);
    });
  }

  // Очистка поиска
  _container?.querySelector('#kbv2-search-clear')?.addEventListener('click', () => {
    _searchQuery = '';
    const input = _container?.querySelector('#kbv2-search');
    if (input) input.value = '';
    _renderContent();
  });

  // Persona переключатель
  _container?.querySelectorAll('.kbv2-persona-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const newPersona = btn.dataset.persona;
      if (newPersona === _persona) return;
      _persona = newPersona;
      localStorage.setItem('llcar-persona', _persona);

      if (newPersona === 'expert') {
        // Эксперт → переключаемся на старый классический экран
        emit('app:navigate', { screen: 'knowledge' });
      } else {
        // Новичок → остаёмся на v2
        _renderContent();
        _showPersonaToast(_persona);
      }
    });
  });

  // Кнопка «Скрапинг»
  _container?.querySelector('#kbv2-scraping-btn')?.addEventListener('click', () => {
    emit('app:navigate', { screen: 'scraping' });
  });
}

/** Показать короткий toast при смене персоны */
function _showPersonaToast(persona) {
  const existing = _container?.querySelector('.kbv2-toast');
  if (existing) existing.remove();

  const msg = persona === 'beginner'
    ? 'Режим «Новичок»: простые объяснения, дерево решений, заботливый тон'
    : 'Режим «Эксперт»: технические детали, коды, оценки релевантности';

  const toast = document.createElement('div');
  toast.className = 'kbv2-toast';
  toast.textContent = msg;
  _container?.querySelector('.kbv2-screen')?.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('kbv2-toast--visible'));
  setTimeout(() => {
    toast.classList.remove('kbv2-toast--visible');
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

function _bindBackButton(container) {
  container?.querySelector('#kbv2-back')?.addEventListener('click', () => {
    _goBack(container);
  });
}

function _goBack(resultsEl) {
  if (_navStack.length > 0) {
    const prev = _navStack.pop();
    switch (prev.type) {
      case 'situations': _renderSituationsView(resultsEl); break;
      case 'systems': _renderSystemsView(resultsEl); break;
      case 'dtc': _renderDTCView(resultsEl); break;
      case 'parts': _renderPartsView(resultsEl); break;
      case 'parts-system':
        // Вернуться к списку деталей системы — перерисуем весь parts view
        // и кликнем по нужной системе (через _renderPartsView)
        _renderPartsView(resultsEl);
        break;
      case 'decision': _renderDecisionTree(resultsEl, prev.nodeId); break;
      case 'article': _renderArticleDetail(resultsEl, prev.entry); break;
      case 'situation_detail': _renderSituationDetail(resultsEl, prev.situation); break;
      default: _renderView();
    }
  } else {
    _renderView();
  }
}

function _bindBriefCards(container) {
  container?.querySelectorAll('.kbv2-brief-card').forEach(el => {
    el.addEventListener('click', async () => {
      const entryId = el.dataset.entryId;
      if (!entryId) return;
      // Найти запись
      let entry = await _findEntryById(entryId);
      if (entry) {
        _navStack.push({ type: _activeTab });
        await _renderArticleDetail(container, entry);
      }
    });
  });
}

async function _findEntryById(id) {
  if (_kb?._cache?._m) {
    for (const [, cached] of _kb._cache._m) {
      const items = cached.v?.results;
      if (Array.isArray(items)) {
        const found = items.find(e => e.chunk_id === id);
        if (found) return found;
      }
    }
  }
  const chunk = await _kb.getChunk(id);
  if (chunk) return chunk;
  const resp = await _kb.search(id, {}, 1);
  return resp.results?.[0] || null;
}

function _bindDTCChips(container) {
  container?.querySelectorAll('.kbv2-dtc-chip').forEach(el => {
    el.addEventListener('click', async (e) => {
      e.stopPropagation();
      const code = el.dataset.dtc;
      if (code) {
        _activeTab = 'dtc';
        _searchQuery = code;
        _renderTabs();
        await _renderView();
      }
    });
  });
}

function _bindGlossaryTerms(container) {
  if (!_glossary) return;
  container?.querySelectorAll('.kbv2-glossary-term').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      _glossary.showTooltip(el);
    });
  });

  // Действия из тултипов
  document.addEventListener('click', (e) => {
    const actionBtn = e.target.closest('.kbv2-glossary-action');
    if (!actionBtn) return;
    const action = actionBtn.dataset.action;
    const gid = actionBtn.dataset.gid;
    if (action === 'search' && gid) {
      _searchQuery = gid.split('@')[0].replace(/_/g, ' ');
      const input = _container?.querySelector('#kbv2-search');
      if (input) input.value = _searchQuery;
      _glossary.hideTooltip();
      _renderView();
    } else if (action === '3d' && gid) {
      _glossary.hideTooltip();
      window.__llcar_selectedComponent = gid;
      emit('app:navigate', { screen: 'twin' });
      setTimeout(() => emit('component:select', { glossaryId: gid, source: 'kb-v2' }), 300);
    }
  });
}
