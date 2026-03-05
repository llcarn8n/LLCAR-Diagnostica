/**
 * LLCAR Diagnostica — Language Selector Component
 *
 * Creates a compact language switcher dropdown for the top bar.
 * Reads/writes language via the i18n singleton.
 *
 * Usage:
 *   import { createLanguageSelector } from '../js/language-selector.js';
 *   const selector = createLanguageSelector(i18n);
 *   document.querySelector('.top-bar').appendChild(selector);
 */

import { i18n, LANG_META } from './i18n.js';

/**
 * Create a language selector DOM element.
 * Returns an HTMLElement ready to be appended to the top bar.
 *
 * @param {object} i18nInstance - The i18n singleton (optional, uses imported i18n by default)
 * @returns {HTMLElement}
 */
export function createLanguageSelector(i18nInstance) {
  const inst = i18nInstance || i18n;

  const wrapper = document.createElement('div');
  wrapper.className = 'lang-selector';

  const btn = document.createElement('button');
  btn.className = 'lang-btn';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Select language');
  updateButtonLabel(btn, inst.lang);

  const dropdown = document.createElement('div');
  dropdown.className = 'lang-dropdown';
  dropdown.style.display = 'none';

  for (const lang of inst.supportedLanguages) {
    const meta = LANG_META[lang];
    const option = document.createElement('button');
    option.className = 'lang-option';
    option.type = 'button';
    option.dataset.lang = lang;
    if (lang === inst.lang) option.classList.add('active');
    option.innerHTML = `<span class="lang-flag">${meta.flag}</span><span class="lang-name">${meta.nativeName}</span>`;

    option.addEventListener('click', () => {
      inst.setLanguage(lang);
      dropdown.style.display = 'none';
      updateButtonLabel(btn, lang);
      // Update active state
      dropdown.querySelectorAll('.lang-option').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.lang === lang);
      });
    });

    dropdown.appendChild(option);
  }

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const isVisible = dropdown.style.display !== 'none';
    dropdown.style.display = isVisible ? 'none' : 'flex';
  });

  // Close dropdown on outside click
  document.addEventListener('click', () => {
    dropdown.style.display = 'none';
  });
  wrapper.addEventListener('click', (e) => e.stopPropagation());

  wrapper.appendChild(btn);
  wrapper.appendChild(dropdown);

  // Listen for external language changes
  inst.onChange((lang) => {
    updateButtonLabel(btn, lang);
    dropdown.querySelectorAll('.lang-option').forEach(opt => {
      opt.classList.toggle('active', opt.dataset.lang === lang);
    });
  });

  return wrapper;
}

function updateButtonLabel(btn, lang) {
  const meta = LANG_META[lang];
  btn.innerHTML = `<span class="lang-flag">${meta.flag}</span><span class="lang-code">${lang.toUpperCase()}</span>`;
}

/**
 * CSS styles for the language selector.
 * Call this once to inject styles into <head>.
 */
export function injectLanguageSelectorStyles() {
  if (document.getElementById('lang-selector-styles')) return;

  const style = document.createElement('style');
  style.id = 'lang-selector-styles';
  style.textContent = `
    .lang-selector {
      position: relative;
      margin-left: 8px;
    }

    .lang-btn {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      background: var(--ex-input-bg, rgba(255,255,255,0.06));
      border: 1px solid var(--ex-input-border, rgba(255,255,255,0.1));
      border-radius: var(--ex-radius-sm, 6px);
      color: var(--ex-text, #ccc);
      font-size: 12px;
      font-family: inherit;
      cursor: pointer;
      transition: border-color 0.15s;
    }
    .lang-btn:hover {
      border-color: var(--ex-accent, #4488ff);
    }

    .lang-flag {
      font-size: 14px;
      line-height: 1;
    }

    .lang-code {
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 0.5px;
    }

    .lang-dropdown {
      position: absolute;
      top: calc(100% + 4px);
      right: 0;
      flex-direction: column;
      min-width: 140px;
      background: var(--ex-panel, rgba(16, 18, 30, 0.98));
      border: 1px solid var(--ex-panel-border, rgba(255,255,255,0.08));
      border-radius: var(--ex-radius, 8px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
      z-index: 1000;
      overflow: hidden;
    }

    .lang-option {
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
      padding: 8px 12px;
      background: none;
      border: none;
      color: var(--ex-text, #ccc);
      font-size: 13px;
      font-family: inherit;
      cursor: pointer;
      text-align: left;
      transition: background 0.12s;
    }
    [dir="rtl"] .lang-option {
      text-align: right;
    }
    .lang-option:hover {
      background: rgba(255,255,255,0.06);
    }
    .lang-option.active {
      background: rgba(68,136,255,0.12);
      color: var(--ex-accent-light, #88bbff);
    }
    .lang-option .lang-name {
      flex: 1;
    }

    /* RTL adjustments */
    [dir="rtl"] .lang-selector {
      margin-left: 0;
      margin-right: 8px;
    }
    [dir="rtl"] .lang-dropdown {
      right: auto;
      left: 0;
    }
    [dir="rtl"] .dtc-search {
      margin-left: 0;
      margin-right: auto;
    }
    [dir="rtl"] .back-link {
      direction: ltr;
    }

    /* General RTL layout overrides */
    [dir="rtl"] .app-layout {
      grid-template-columns: 320px 1fr 280px;
    }
    [dir="rtl"] .left-panel {
      grid-column: 3;
      grid-row: 2;
      border-left: none;
      border-right: 1px solid var(--ex-panel-border, rgba(255,255,255,0.08));
    }
    [dir="rtl"] .right-panel {
      grid-column: 1;
      grid-row: 2;
      border-right: none;
      border-left: 1px solid var(--ex-panel-border, rgba(255,255,255,0.08));
    }
  `;
  document.head.appendChild(style);
}
