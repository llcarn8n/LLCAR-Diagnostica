/**
 * LLCAR Diagnostica — Main App Controller
 * SPA router with screen management and tab bar.
 */

import { emit, on } from './event-bus.js';
import { I18n } from './i18n.js';
import { render as renderCarSelect, cleanup as cleanupCarSelect } from './screens/car-select.js';
import { render as renderDashboard, cleanup as cleanupDashboard } from './screens/dashboard.js';
import { render as renderDiagnostics, cleanup as cleanupDiagnostics } from './screens/diagnostics.js';
import { render as renderDigitalTwin, cleanup as cleanupDigitalTwin } from './screens/digital-twin.js';
import { render as renderHealthCert, cleanup as cleanupHealthCert } from './screens/health-cert.js';
import { render as renderKnowledge, cleanup as cleanupKnowledge } from './screens/knowledge.js';
import { render as renderKnowledgeV2, cleanup as cleanupKnowledgeV2 } from './screens/knowledge-v2.js';
import { render as renderAiAssistant, cleanup as cleanupAiAssistant } from './screens/ai-assistant.js';
import { render as renderScraping, cleanup as cleanupScraping } from './screens/scraping.js';

/** @type {I18n} Global i18n instance */
export const i18n = new I18n();

/** @type {string} Current active screen name */
let currentScreen = 'onboarding';

/** Tab ID -> Screen name mapping */
const TAB_TO_SCREEN = {
  health: 'dashboard',
  diagnostics: 'diagnostics',
  twin: 'twin',
  knowledge: 'knowledge-v2',
  doctor: 'doctor',
};

/** Screen name -> { render, cleanup } mapping */
const SCREENS = {
  onboarding:   { render: renderCarSelect,   cleanup: cleanupCarSelect },
  dashboard:    { render: renderDashboard,    cleanup: cleanupDashboard },
  diagnostics:  { render: renderDiagnostics,  cleanup: cleanupDiagnostics },
  twin:         { render: renderDigitalTwin,  cleanup: cleanupDigitalTwin },
  certificate:  { render: renderHealthCert,   cleanup: cleanupHealthCert },
  knowledge:    { render: renderKnowledge,    cleanup: cleanupKnowledge },
  'knowledge-v2': { render: renderKnowledgeV2, cleanup: cleanupKnowledgeV2 },
  doctor:       { render: renderAiAssistant,  cleanup: cleanupAiAssistant },
  scraping:     { render: renderScraping,     cleanup: cleanupScraping },
};

/**
 * Switch to a new screen.
 * @param {string} screenName
 */
export function switchScreen(screenName) {
  if (!SCREENS[screenName] || screenName === currentScreen) return;

  // Cleanup previous screen
  const prev = SCREENS[currentScreen];
  if (prev && prev.cleanup) {
    prev.cleanup();
  }

  // Hide all screens
  document.querySelectorAll('.screen').forEach(el => {
    el.classList.remove('screen--active');
  });

  // Show target screen
  const targetEl = document.getElementById(`screen-${screenName}`);
  if (targetEl) {
    targetEl.classList.add('screen--active');
  }

  // Render screen content
  const next = SCREENS[screenName];
  if (next && next.render) {
    next.render(targetEl);
  }

  // Update translated text on the new screen
  i18n.updateDOM();

  // Update tab bar
  const tabBar = document.getElementById('tab-bar');
  if (screenName === 'onboarding') {
    tabBar.style.display = 'none';
  } else {
    tabBar.style.display = '';
    updateTabBar(screenName);
  }

  currentScreen = screenName;
  emit('screen:change', { screen: screenName });
}

/**
 * Get current screen name.
 * @returns {string}
 */
export function getCurrentScreen() {
  return currentScreen;
}

/** Update active tab highlight */
function updateTabBar(screenName) {
  // Оба экрана knowledge и knowledge-v2 подсвечивают таб "knowledge"
  const resolvedScreen = (screenName === 'knowledge') ? 'knowledge-v2' : screenName;
  const activeTab = Object.entries(TAB_TO_SCREEN).find(([, s]) => s === resolvedScreen);
  const activeTabId = activeTab ? activeTab[0] : null;

  document.querySelectorAll('.tab-bar__item').forEach(btn => {
    const tabId = btn.dataset.tab;
    if (tabId === activeTabId) {
      btn.classList.add('tab-bar__item--active');
    } else {
      btn.classList.remove('tab-bar__item--active');
    }
  });
}

/** Initialize the app */
async function init() {
  // Initialize i18n (loads UI strings, restores saved language)
  await i18n.init(null, {
    basePath: 'data/i18n',
    glossaryPath: 'data/architecture/i18n-glossary-data.json',
  });

  // Tab bar clicks
  document.querySelectorAll('.tab-bar__item').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;
      let screenName = TAB_TO_SCREEN[tabId];
      // Таб «Знания»: новичок → knowledge-v2, эксперт → knowledge (старый)
      if (tabId === 'knowledge') {
        const persona = localStorage.getItem('llcar-persona') || 'beginner';
        screenName = persona === 'expert' ? 'knowledge' : 'knowledge-v2';
      }
      if (screenName) {
        switchScreen(screenName);
      }
    });
  });

  // Listen for app:start from onboarding
  on('app:start', (e) => {
    // Save selected model to localStorage
    const model = e.detail?.model || 'li7';
    localStorage.setItem('llcar-model', model);
    switchScreen('dashboard');
  });

  // Listen for navigation events
  on('app:navigate', (e) => {
    if (e.detail && e.detail.screen) {
      switchScreen(e.detail.screen);
    }
  });

  // Expose i18n globally for modules that can't import (e.g. knowledge.js)
  window.__llcar_i18n = i18n;

  // Re-translate current screen on language change
  document.addEventListener('lang:change', () => {
    i18n.updateDOM();
  });

  // Cross-screen tag binding: 3D component select → prepare KB filter
  on('component:select', (e) => {
    const glossaryId = e.detail?.glossaryId;
    if (glossaryId) {
      // Store selected component for cross-screen use
      window.__llcar_selectedComponent = glossaryId;
    }
  });

  on('component:deselect', () => {
    window.__llcar_selectedComponent = null;
  });

  // KB article click → показываем деталь статьи внутри KB (НЕ переход в 3D)
  // Переход в 3D доступен через отдельную кнопку "Показать в 3D" в деталях статьи
  on('kb:article:select', (e) => {
    // Ничего не делаем здесь — knowledge.js сам покажет деталь статьи
  });

  // Navigate to KB with component filter from 3D twin
  on('twin:open-kb', (e) => {
    const detail = e.detail || {};
    const glossaryId = detail.glossaryId;
    if (glossaryId) {
      window.__llcar_selectedComponent = glossaryId;
      // Передаём доп. данные аннотации для улучшенного поиска
      window.__llcar_selectedComponentData = {
        glossaryId,
        dtcCodes: detail.dtcCodes || [],
        category: detail.category || '',
        layer: detail.layer || '',
      };
    }
    switchScreen('knowledge-v2');
  });

  // Hash routing: #scraping, #knowledge, etc.
  const hash = window.location.hash.replace('#', '');
  if (hash && SCREENS[hash]) {
    switchScreen(hash);
  } else {
    // Render initial screen
    const onboardingEl = document.getElementById('screen-onboarding');
    if (onboardingEl) {
      SCREENS.onboarding.render(onboardingEl);
      i18n.updateDOM();
    }
  }
}

// Boot
init().catch(err => {
  console.error('[LLCAR] Init failed:', err);
  // Render onboarding anyway so user sees something
  const el = document.getElementById('screen-onboarding');
  if (el) {
    SCREENS.onboarding.render(el);
  }
});
