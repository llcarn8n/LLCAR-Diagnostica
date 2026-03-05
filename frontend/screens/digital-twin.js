/**
 * Digital Twin Screen — 3D viewer with layer toggle UI.
 * Renders ThreeViewer into #screen-twin with a layer panel overlay,
 * X-ray toggle, and component info tooltip.
 */

import { ThreeViewer } from '../three-viewer.js';
import { PIDOverlay } from '../pid-overlay.js';
import { AnnotationOverlay } from '../annotation-overlay.js';
import { on, off, emit } from '../event-bus.js';
import { i18n } from '../app.js';

/** @type {ThreeViewer|null} */
let viewer = null;
/** @type {PIDOverlay|null} */
let pidOverlay = null;
/** @type {AnnotationOverlay|null} */
let annotationOverlay = null;
/** @type {object|null} parsed layer-definitions.json (cached) */
let layerDefsCache = null;
/** @type {object|null} parsed parts-bridge.json (cached) */
let partsBridgeCache = null;
/** @type {HTMLElement|null} */
let screenEl = null;

// Layer color/label references (matched to layer-definitions.json)
const LAYER_META = {
  body:       { icon: '\u{1F6E1}', varColor: '--layer-body' },
  engine:     { icon: '\u{2699}',  varColor: '--layer-engine' },
  drivetrain: { icon: '\u{1F504}', varColor: '--layer-transmission' },
  ev:         { icon: '\u{26A1}',  varColor: '--layer-electrical' },
  brakes:     { icon: '\u{1F6D1}', varColor: '--layer-brakes' },
  sensors:    { icon: '\u{1F4E1}', varColor: '--layer-body' },
  hvac:       { icon: '\u{2744}',  varColor: '--layer-climate' },
  interior:   { icon: '\u{1F4BA}', varColor: '--layer-interior' },
};

/**
 * Build the screen DOM.
 * @param {HTMLElement} container
 */
function buildDOM(container) {
  container.innerHTML = `
    <div class="twin-screen">
      <!-- 3D Viewport -->
      <div class="twin-viewport" id="twin-viewport">
        <div class="twin-loading" id="twin-loading">
          <div class="twin-loading__spinner"></div>
          <div class="twin-loading__text" data-i18n="twin.loading_model">Loading 3D model...</div>
          <div class="twin-loading__progress" id="twin-progress">0%</div>
        </div>
      </div>

      <!-- Top toolbar -->
      <div class="twin-toolbar" id="twin-toolbar">
        <button class="twin-toolbar__btn" id="btn-xray" title="X-Ray">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
        </button>
        <button class="twin-toolbar__btn" id="btn-reset-view" title="Reset View">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
        </button>
        <button class="twin-toolbar__btn" id="btn-pid-toggle" title="PID Sensors">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
        </button>
        <button class="twin-toolbar__btn" id="btn-annotations-toggle" title="Annotations">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        </button>
        <button class="twin-toolbar__btn" id="btn-layers-toggle" title="Layers">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>
        </button>
      </div>

      <!-- Layer panel (slide-in) -->
      <div class="twin-layers" id="twin-layers">
        <div class="twin-layers__header">
          <span class="twin-layers__title" data-i18n="twin.layers_title">Layers</span>
          <button class="twin-layers__show-all" id="btn-show-all" data-i18n="twin.show_all">Show All</button>
        </div>
        <div class="twin-layers__list" id="twin-layers-list"></div>
      </div>

      <!-- Component info tooltip -->
      <div class="twin-tooltip" id="twin-tooltip" style="display: none;">
        <div class="twin-tooltip__name" id="twin-tooltip-name"></div>
        <div class="twin-tooltip__layer" id="twin-tooltip-layer"></div>
      </div>

      <!-- Selected component info bar -->
      <div class="twin-info-bar" id="twin-info-bar" style="display: none;">
        <div class="twin-info-bar__content">
          <div class="twin-info-bar__name" id="twin-info-name"></div>
          <div class="twin-info-bar__id" id="twin-info-id"></div>
          <div class="twin-info-bar__parts" id="twin-info-parts" style="display: none;"></div>
        </div>
        <button class="twin-info-bar__kb-link" id="twin-open-kb" data-i18n-title="twin.read_kb" title="Читать в базе знаний">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/></svg>
        </button>
        <button class="twin-info-bar__close" id="twin-info-close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
  `;
}

/**
 * Inject scoped CSS for the digital-twin screen.
 */
function injectStyles() {
  if (document.getElementById('twin-styles')) return;
  const style = document.createElement('style');
  style.id = 'twin-styles';
  style.textContent = `
    .twin-screen {
      position: relative;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg-page);
    }

    .twin-viewport {
      flex: 1;
      position: relative;
      overflow: hidden;
    }
    .twin-viewport canvas {
      display: block;
      width: 100% !important;
      height: 100% !important;
    }

    /* Loading overlay */
    .twin-loading {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      background: var(--bg-page);
      z-index: 20;
      transition: opacity 0.4s;
    }
    .twin-loading--hidden {
      opacity: 0;
      pointer-events: none;
    }
    .twin-loading__spinner {
      width: 32px;
      height: 32px;
      border: 3px solid var(--border-default);
      border-top-color: var(--accent-primary);
      border-radius: 50%;
      animation: twin-spin 0.8s linear infinite;
    }
    @keyframes twin-spin {
      to { transform: rotate(360deg); }
    }
    .twin-loading__text {
      font-size: 13px;
      color: var(--text-secondary);
    }
    .twin-loading__progress {
      font-size: 12px;
      color: var(--text-tertiary);
      font-variant-numeric: tabular-nums;
    }

    /* Top toolbar */
    .twin-toolbar {
      position: absolute;
      top: 8px;
      right: 8px;
      display: flex;
      gap: 6px;
      z-index: 10;
    }
    .twin-toolbar__btn {
      width: 36px;
      height: 36px;
      border-radius: var(--radius-md);
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-secondary);
      transition: background 0.2s, color 0.2s;
    }
    .twin-toolbar__btn:hover,
    .twin-toolbar__btn--active {
      background: var(--bg-surface);
      color: var(--accent-primary);
    }

    /* Layer panel — horizontal bottom bar */
    .twin-layers {
      position: absolute;
      bottom: 8px;
      left: 8px;
      right: 8px;
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      overflow: visible;
      z-index: 10;
      display: none;
      flex-direction: column;
    }
    .twin-layers--open {
      display: flex;
    }
    .twin-layers__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 12px 2px;
    }
    .twin-layers__title {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-primary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .twin-layers__show-all {
      font-size: 11px;
      color: var(--accent-primary);
      padding: 2px 6px;
      border-radius: var(--radius-sm);
      transition: background 0.2s;
    }
    .twin-layers__show-all:hover {
      background: var(--accent-primary-dim);
    }
    .twin-layers__list {
      display: flex;
      flex-wrap: wrap;
      gap: 2px;
      padding: 4px 8px 6px;
      overflow: visible;
    }

    /* Layer item — compact horizontal chip */
    .twin-layer-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 5px 8px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: background 0.15s;
      user-select: none;
      white-space: nowrap;
    }
    .twin-layer-item:hover {
      background: var(--bg-surface);
    }
    .twin-layer-item__dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    .twin-layer-item__label {
      font-size: 12px;
      color: var(--text-primary);
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .twin-layer-item__count {
      font-size: 10px;
      color: var(--text-tertiary);
      font-variant-numeric: tabular-nums;
    }
    .twin-layer-item--hidden .twin-layer-item__dot {
      opacity: 0.3;
    }
    .twin-layer-item--hidden .twin-layer-item__label {
      color: var(--text-tertiary);
      text-decoration: line-through;
    }
    .twin-layer-item--ghost .twin-layer-item__dot {
      opacity: 0.4;
    }
    .twin-layer-item--ghost .twin-layer-item__label {
      color: var(--text-tertiary);
      font-style: italic;
    }

    /* Isolate button */
    .twin-layer-item__isolate {
      font-size: 10px;
      color: var(--text-tertiary);
      padding: 1px 4px;
      border-radius: 3px;
      opacity: 0;
      transition: opacity 0.15s;
    }
    .twin-layer-item:hover .twin-layer-item__isolate {
      opacity: 1;
    }

    /* Eye button for visibility */
    .twin-layer-item__eye {
      width: 22px;
      height: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 3px;
      color: var(--text-secondary);
      flex-shrink: 0;
      transition: color 0.15s;
    }
    .twin-layer-item__eye:hover {
      color: var(--accent-primary);
    }
    .twin-layer-item--hidden .twin-layer-item__eye {
      color: var(--text-tertiary);
      opacity: 0.5;
    }

    /* Chevron for expand/collapse */
    .twin-layer-item__chevron {
      width: 14px;
      height: 14px;
      flex-shrink: 0;
      transition: transform 0.2s;
    }
    .twin-layer-group--expanded > .twin-layer-item .twin-layer-item__chevron {
      transform: rotate(180deg);
    }

    /* Layer group — positioned for upward component popup */
    .twin-layer-group { position: relative; }

    /* Component list — popup expanding upward from chip */
    .twin-layer-components {
      display: none;
      flex-direction: column;
      max-height: 240px;
      overflow-y: auto;
      position: absolute;
      bottom: 100%;
      left: 0;
      min-width: 220px;
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: 4px;
      margin-bottom: 4px;
      z-index: 20;
      box-shadow: 0 -4px 16px rgba(0,0,0,0.12);
    }
    .twin-layer-group--expanded .twin-layer-components {
      display: flex;
    }
    .twin-layer-components::-webkit-scrollbar {
      width: 3px;
    }
    .twin-layer-components::-webkit-scrollbar-thumb {
      background: var(--border-default);
      border-radius: 2px;
    }

    /* Individual component item */
    .twin-layer-comp {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.15s;
    }
    .twin-layer-comp:hover {
      background: var(--bg-surface);
    }
    .twin-layer-comp__name {
      font-size: 11px;
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }
    .twin-layer-comp:hover .twin-layer-comp__name {
      color: var(--text-primary);
    }
    .twin-layer-comp__dtc {
      font-size: 9px;
      color: var(--status-warning);
      background: var(--warning-bg);
      padding: 1px 4px;
      border-radius: 3px;
      flex-shrink: 0;
    }
    .twin-layer-item__isolate:hover {
      color: var(--accent-primary);
      background: var(--accent-primary-dim);
    }

    /* Hover tooltip */
    .twin-tooltip {
      position: absolute;
      bottom: 60px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: 6px 12px;
      z-index: 10;
      text-align: center;
      pointer-events: none;
    }
    .twin-tooltip__name {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-primary);
    }
    .twin-tooltip__layer {
      font-size: 10px;
      color: var(--text-secondary);
      margin-top: 2px;
    }

    /* Selected component info bar */
    .twin-info-bar {
      position: absolute;
      bottom: 8px;
      left: 8px;
      right: 8px;
      background: var(--bg-card);
      border: 1px solid var(--border-accent);
      border-radius: var(--radius-lg);
      padding: 10px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 10;
    }
    .twin-info-bar__name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
    }
    .twin-info-bar__id {
      font-size: 11px;
      color: var(--text-tertiary);
      margin-top: 2px;
      font-family: monospace;
    }
    .twin-info-bar__parts {
      margin-top: 4px;
      font-size: 11px;
      color: var(--text-secondary);
      max-height: 60px;
      overflow-y: auto;
    }
    .twin-info-bar__parts .part-item {
      display: flex;
      gap: 6px;
      padding: 1px 0;
    }
    .twin-info-bar__parts .part-number {
      font-family: monospace;
      color: var(--accent-primary);
      font-weight: 500;
      white-space: nowrap;
    }
    .twin-info-bar__parts .part-name {
      color: var(--text-secondary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .twin-info-bar__kb-link {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-sm);
      color: var(--accent-primary);
      flex-shrink: 0;
    }
    .twin-info-bar__kb-link:hover {
      background: var(--accent-primary-dim);
    }
    .twin-info-bar__close {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
    }
    .twin-info-bar__close:hover {
      background: var(--bg-surface);
    }

    /* Shift info bar above layers panel when open */
    .twin-layers--open ~ .twin-info-bar {
      bottom: 80px;
    }

    /* ─── Annotation Markers ──────────────────────────────── */
    .annotation-marker {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      transform: translate(-50%, -50%);
      cursor: pointer;
      z-index: 1;
    }
    .annotation-marker__icon {
      font-size: 14px;
      line-height: 1;
      filter: drop-shadow(0 1px 3px rgba(0,0,0,0.5));
      transition: transform 0.2s, filter 0.2s;
    }
    .annotation-marker__pulse {
      position: absolute;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--accent-primary);
      opacity: 0.25;
      animation: ann-pulse 2s ease-out infinite;
    }
    @keyframes ann-pulse {
      0% { transform: scale(0.8); opacity: 0.25; }
      70% { transform: scale(1.6); opacity: 0; }
      100% { transform: scale(0.8); opacity: 0; }
    }
    .annotation-marker--hover .annotation-marker__icon {
      transform: scale(1.3);
      filter: drop-shadow(0 2px 6px rgba(0,212,170,0.5));
    }
    .annotation-marker--hover .annotation-marker__pulse {
      animation: none;
      opacity: 0.4;
      transform: scale(1.3);
    }
    .annotation-marker--selected {
      z-index: 5;
    }
    .annotation-marker--selected .annotation-marker__icon {
      transform: scale(1.4);
      filter: drop-shadow(0 2px 8px rgba(0,212,170,0.7));
    }
    .annotation-marker--selected .annotation-marker__pulse {
      animation: none;
      opacity: 0.5;
      background: var(--accent-primary);
      transform: scale(1.5);
    }

    /* Annotation indicator in component list */
    .twin-layer-comp--annotation {
      border-left: 2px solid var(--accent-primary);
      padding-left: 6px;
    }
    .twin-layer-comp__ann-icon {
      font-size: 10px;
      flex-shrink: 0;
      margin-right: 4px;
    }
  `;
  document.head.appendChild(style);
}

/**
 * Populate the layer list from layer definitions with expandable component lists.
 */
function buildLayerList() {
  if (!viewer?.layerManager || !layerDefsCache) return;

  const listEl = document.getElementById('twin-layers-list');
  if (!listEl) return;
  listEl.innerHTML = '';

  const layers = viewer.layerManager.getLayers();

  for (const layer of layers) {
    const wrapper = document.createElement('div');
    wrapper.className = 'twin-layer-group';
    wrapper.dataset.layerId = layer.id;

    // Получаем все компоненты слоя: меши + аннотации
    const layerComponents = viewer.tagRegistry.getByLayerAll(layer.id);
    const label = i18n.getLayerName(layer.id);

    // Layer header
    const header = document.createElement('div');
    header.className = 'twin-layer-item';
    header.dataset.layerId = layer.id;
    header.innerHTML = `
      <button class="twin-layer-item__eye" data-action="visibility" title="Скрыть/показать">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
      </button>
      <div class="twin-layer-item__dot" style="background: ${layer.color}"></div>
      <span class="twin-layer-item__label">${label}</span>
      <span class="twin-layer-item__count">${layerComponents.length}</span>
      <svg class="twin-layer-item__chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
      <button class="twin-layer-item__isolate" data-action="isolate" title="Solo">${i18n.get('twin.solo', 'solo')}</button>
    `;

    // Toggle expand/collapse on header click (but not on buttons)
    // Collapse other groups so only one component popup is open at a time
    header.addEventListener('click', (e) => {
      if (e.target.dataset.action || e.target.closest('[data-action]')) return;
      const wasExpanded = wrapper.classList.contains('twin-layer-group--expanded');
      listEl.querySelectorAll('.twin-layer-group--expanded').forEach(g => {
        g.classList.remove('twin-layer-group--expanded');
      });
      if (!wasExpanded) wrapper.classList.add('twin-layer-group--expanded');
    });

    // Eye button toggles layer visibility
    const eyeBtn = header.querySelector('[data-action="visibility"]');
    eyeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      viewer.layerManager.toggle(layer.id);
      header.classList.toggle('twin-layer-item--hidden');
    });

    // Isolate on solo click — other layers become translucent (ghost)
    const isolateBtn = header.querySelector('[data-action="isolate"]');
    isolateBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Reset X-ray first since isolate handles ghost itself
      if (viewer.xrayEnabled) {
        viewer._xrayEnabled = false; // direct reset without re-toggling layers
        const xBtn = document.getElementById('btn-xray');
        if (xBtn) xBtn.classList.remove('twin-toolbar__btn--active');
      }
      viewer.layerManager.isolate(layer.id);
      // Update visual state: isolated layer is active, others are dimmed
      listEl.querySelectorAll('.twin-layer-item').forEach(el => {
        el.classList.remove('twin-layer-item--hidden');
        if (el.dataset.layerId && el.dataset.layerId !== layer.id) {
          el.classList.add('twin-layer-item--ghost');
        } else {
          el.classList.remove('twin-layer-item--ghost');
        }
      });
    });

    wrapper.appendChild(header);

    // Component list (expandable)
    if (layerComponents.length > 0) {
      const compList = document.createElement('div');
      compList.className = 'twin-layer-components';

      for (const comp of layerComponents) {
        const compItem = document.createElement('div');
        compItem.className = 'twin-layer-comp';
        if (comp.isAnnotation) compItem.classList.add('twin-layer-comp--annotation');
        compItem.dataset.glossaryId = comp.glossary_id || '';
        const translated = comp.glossary_id ? i18n.getComponentName(comp.glossary_id) : null;
        // Если глоссарий вернул сырой id — fallback на displayName
        const compName = (translated && translated !== comp.glossary_id) ? translated : (comp.displayName || comp.meshName);
        const annIcon = comp.isAnnotation ? '<span class="twin-layer-comp__ann-icon" title="Annotation">&#x1F4CD;</span>' : '';
        compItem.innerHTML = `
          ${annIcon}<span class="twin-layer-comp__name">${compName}</span>
          ${comp.dtcCodes?.length ? `<span class="twin-layer-comp__dtc">${comp.dtcCodes.length} DTC</span>` : ''}
        `;

        // Клик — выбрать компонент в 3D
        compItem.addEventListener('click', () => {
          if (comp.glossary_id && viewer) {
            if (comp.isAnnotation && annotationOverlay) {
              // Для аннотаций — подсветить маркер и показать info bar
              annotationOverlay.highlight(comp.glossary_id);
              emit('component:select', {
                glossaryId: comp.glossary_id,
                component: comp,
                meshCount: 0,
              });
            } else {
              viewer.selectByGlossaryId(comp.glossary_id);
            }
          }
        });

        compList.appendChild(compItem);
      }
      wrapper.appendChild(compList);
    }

    listEl.appendChild(wrapper);
  }
}

// ─── Event Handlers ──────────────────────────────────────

function onModelProgress(e) {
  const progressEl = document.getElementById('twin-progress');
  if (progressEl) {
    progressEl.textContent = `${e.detail.percent}%`;
  }
}

function onModelLoaded() {
  const loadingEl = document.getElementById('twin-loading');
  if (loadingEl) {
    loadingEl.classList.add('twin-loading--hidden');
  }
  buildLayerList();
  setupPidOverlay();
  setupAnnotationOverlay();
}

/**
 * Initialize PID overlay after model is loaded.
 * Loads demo PID bindings and listens for live data.
 */
function setupPidOverlay() {
  if (!viewer) return;

  pidOverlay = new PIDOverlay(viewer);

  // Load demo PID bindings (in production, call pidOverlay.bind() per PID from server config)
  pidOverlay.loadDemo();

  // Listen for live PID updates from the diagnostics data stream
  on('pid:data', onPidData);
}

/**
 * Инициализация overlay аннотаций после загрузки модели.
 */
async function setupAnnotationOverlay() {
  if (!viewer) return;

  annotationOverlay = new AnnotationOverlay(viewer);

  // Загружаем конфиг аннотаций
  try {
    await annotationOverlay.load('data/architecture/annotation-config.json');
  } catch (err) {
    console.warn('Не удалось загрузить аннотации:', err);
  }

  // Перестроить список слоёв с учётом аннотаций
  buildLayerList();
}

function onComponentHover(e) {
  const tooltip = document.getElementById('twin-tooltip');
  const nameEl = document.getElementById('twin-tooltip-name');
  const layerEl = document.getElementById('twin-tooltip-layer');
  if (!tooltip || !nameEl || !layerEl) return;

  if (e.detail.glossaryId) {
    const comp = viewer?.tagRegistry?.getComponent(e.detail.glossaryId);
    const translatedName = i18n.getComponentName(e.detail.glossaryId);
    nameEl.textContent = translatedName !== e.detail.glossaryId ? translatedName : (e.detail.displayName || e.detail.glossaryId);
    layerEl.textContent = comp?.layer ? i18n.getLayerName(comp.layer) : '';
    tooltip.style.display = '';
  } else {
    tooltip.style.display = 'none';
  }
}

function onComponentSelect(e) {
  const bar = document.getElementById('twin-info-bar');
  const nameEl = document.getElementById('twin-info-name');
  const idEl = document.getElementById('twin-info-id');
  const partsEl = document.getElementById('twin-info-parts');
  if (!bar || !nameEl || !idEl) return;

  const comp = e.detail.component;
  if (comp) {
    const glossaryId = e.detail.glossaryId;
    const translatedName = i18n.getComponentName(glossaryId);
    nameEl.textContent = translatedName !== glossaryId ? translatedName : (comp.displayName || comp.meshName);
    idEl.textContent = glossaryId;
    bar.style.display = '';

    // Show parts from parts-bridge if available
    if (partsEl) {
      const parts = findPartsForGlossaryId(glossaryId, e.detail.meshName);
      if (parts.length > 0) {
        const lang = i18n.lang || 'ru';
        const html = parts.slice(0, 5).map(p => {
          let name;
          if (lang === 'zh') name = p.name_zh || p.name_en;
          else if (lang === 'ru') name = p.name_ru || p.name_en || p.name_zh;
          else name = p.name_en || p.name_zh;
          name = name || p.name_zh || p.number;
          return `<div class="part-item part-item--clickable" data-part-number="${p.number}" data-part-name="${p.name_zh || ''}" style="cursor:pointer;"><span class="part-number">${p.number}</span><span class="part-name">${name}</span></div>`;
        }).join('');
        partsEl.innerHTML = (parts.length > 5 ? html + `<div style="color:var(--text-tertiary)">+${parts.length - 5} ...</div>` : html);
        partsEl.style.display = '';
        // Make parts clickable → navigate to KB parts detail
        partsEl.querySelectorAll('.part-item--clickable').forEach(el => {
          el.addEventListener('click', (ev) => {
            ev.stopPropagation();
            const pn = el.dataset.partNumber;
            if (pn) {
              window.__llcar_partDetail = { partNumber: pn, nameZh: el.dataset.partName };
              emit('app:navigate', { screen: 'knowledge' });
            }
          });
        });
      } else {
        partsEl.style.display = 'none';
        partsEl.innerHTML = '';
      }
    }
  }
}

/**
 * Handle regional selection — highlight all meshes in a diagnostic group.
 * Triggered from KB when a part has no specific glossary_id mesh.
 */
function onRegionSelect(e) {
  const group = e.detail?.group;
  if (!group || !viewer) return;

  // If source is 'kb', the viewer was just navigated to — need to wait for model
  if (e.detail?.source === 'kb' && !viewer._modelRoot) {
    // Retry after model loads
    const handler = () => {
      off('model:loaded', handler);
      setTimeout(() => viewer.selectByGroup(group), 100);
    };
    on('model:loaded', handler);
    return;
  }

  viewer.selectByGroup(group);

  // Show group info in the info bar
  const bar = document.getElementById('twin-info-bar');
  if (bar) {
    const nameEl = bar.querySelector('.info-bar__name');
    const idEl = bar.querySelector('.info-bar__id');
    const partsEl = bar.querySelector('#twin-parts');
    const groupLabels = { electric: 'Electric / EV', fuel: 'Engine / Drivetrain', suspension: 'Brakes / Steering', cabin: 'Body / Interior', tech: 'Sensors / ADAS' };
    if (nameEl) nameEl.textContent = groupLabels[group] || group;
    if (idEl) idEl.textContent = `Region: ${group}`;
    if (partsEl) { partsEl.style.display = 'none'; partsEl.innerHTML = ''; }
    bar.style.display = '';
  }
}

/**
 * Find parts from parts-bridge.json matching a glossary_id or mesh name.
 * @param {string} glossaryId
 * @param {string} [meshName]
 * @returns {Array<{number: string, name_zh: string, name_en: string|null}>}
 */
function findPartsForGlossaryId(glossaryId, meshName) {
  if (!partsBridgeCache || !partsBridgeCache.systems) return [];

  // First pass: collect per-part glossary_id matches (most specific)
  const directMatches = [];
  // Second pass: system-level matches (fallback)
  const systemMatches = [];

  for (const sys of Object.values(partsBridgeCache.systems)) {
    const hasGlossary = glossaryId && sys.glossary_ids?.includes(glossaryId);
    const hasMesh = meshName && sys.meshes_l9?.some(m => meshName.startsWith(m) || m.startsWith(meshName));

    if (hasGlossary || hasMesh) {
      for (const part of (sys.parts || [])) {
        if (part.glossary_id === glossaryId) {
          directMatches.push(part);
        } else {
          systemMatches.push(part);
        }
      }
    }
  }

  // Prefer direct matches; fall back to system-level (limited to 8)
  if (directMatches.length > 0) return directMatches;
  return systemMatches.slice(0, 8);
}

function onComponentDeselect() {
  const bar = document.getElementById('twin-info-bar');
  if (bar) bar.style.display = 'none';
}

/**
 * Handle live PID data from the diagnostics server stream.
 * Expected event detail: { updates: [{ glossaryId, value, status?, name? }, ...] }
 */
function onPidData(e) {
  if (!pidOverlay || !e.detail?.updates) return;
  for (const u of e.detail.updates) {
    pidOverlay.update(u.glossaryId, u);
  }
}

function onLangChange() {
  // Rebuild layer list with new language translations
  buildLayerList();
}

// ─── Public API (called by app.js) ──────────────────────

/**
 * Render the Digital Twin screen.
 * @param {HTMLElement} container - #screen-twin
 */
export async function render(container) {
  screenEl = container;
  injectStyles();
  buildDOM(container);

  // Wire toolbar buttons
  document.getElementById('btn-xray')?.addEventListener('click', () => {
    if (!viewer) return;
    const btn = document.getElementById('btn-xray');
    const isActive = btn.classList.toggle('twin-toolbar__btn--active');
    viewer.setXray(isActive);
    // Update layer panel visual state for shell layers
    if (isActive) {
      for (const shellId of ['body', 'interior']) {
        const item = document.querySelector(`.twin-layer-item[data-layer-id="${shellId}"]`);
        if (item) item.classList.add('twin-layer-item--ghost');
      }
    } else {
      document.querySelectorAll('.twin-layer-item--ghost').forEach(el => {
        el.classList.remove('twin-layer-item--ghost');
      });
    }
  });

  document.getElementById('btn-reset-view')?.addEventListener('click', () => {
    if (!viewer) return;
    viewer.controls.reset();
    viewer.controls.autoRotate = true;
    // Also reset X-ray and layers
    if (viewer.xrayEnabled) {
      viewer.setXray(false);
      const xBtn = document.getElementById('btn-xray');
      if (xBtn) xBtn.classList.remove('twin-toolbar__btn--active');
    }
    if (viewer.layerManager) {
      viewer.layerManager.showAll();
      document.querySelectorAll('.twin-layer-item').forEach(el => {
        el.classList.remove('twin-layer-item--hidden');
        el.classList.remove('twin-layer-item--ghost');
      });
    }
  });

  document.getElementById('btn-pid-toggle')?.addEventListener('click', () => {
    if (!pidOverlay) return;
    const btn = document.getElementById('btn-pid-toggle');
    const nowVisible = !pidOverlay.visible;
    pidOverlay.setVisible(nowVisible);
    btn.classList.toggle('twin-toolbar__btn--active', nowVisible);
  });

  document.getElementById('btn-annotations-toggle')?.addEventListener('click', () => {
    if (!annotationOverlay) return;
    const btn = document.getElementById('btn-annotations-toggle');
    const nowVisible = !annotationOverlay.visible;
    annotationOverlay.setVisible(nowVisible);
    btn.classList.toggle('twin-toolbar__btn--active', nowVisible);
  });

  document.getElementById('btn-layers-toggle')?.addEventListener('click', () => {
    const panel = document.getElementById('twin-layers');
    if (panel) panel.classList.toggle('twin-layers--open');
  });

  document.getElementById('btn-show-all')?.addEventListener('click', () => {
    if (!viewer?.layerManager) return;
    viewer.layerManager.showAll();
    // Reset X-ray state too
    if (viewer.xrayEnabled) {
      viewer.setXray(false);
      const xBtn = document.getElementById('btn-xray');
      if (xBtn) xBtn.classList.remove('twin-toolbar__btn--active');
    }
    // Reset visual state of all layer items
    document.querySelectorAll('.twin-layer-item').forEach(el => {
      el.classList.remove('twin-layer-item--hidden');
      el.classList.remove('twin-layer-item--ghost');
    });
  });

  document.getElementById('twin-info-close')?.addEventListener('click', () => {
    if (viewer) viewer.clearSelection();
  });

  // Open KB for selected component
  document.getElementById('twin-open-kb')?.addEventListener('click', () => {
    const idEl = document.getElementById('twin-info-id');
    const glossaryId = idEl?.textContent;
    if (glossaryId) {
      emit('twin:open-kb', { glossaryId });
    }
  });

  // Subscribe to events
  on('model:progress', onModelProgress);
  on('model:loaded', onModelLoaded);
  on('component:hover', onComponentHover);
  on('component:select', onComponentSelect);
  on('component:deselect', onComponentDeselect);
  on('region:select', onRegionSelect);

  // Re-render layer list when language changes
  document.addEventListener('lang:change', onLangChange);

  // Create viewer
  const viewport = document.getElementById('twin-viewport');
  if (!viewport) return;

  viewer = new ThreeViewer(viewport);

  // Load layer definitions
  try {
    const resp = await fetch('data/architecture/layer-definitions.json');
    layerDefsCache = await resp.json();
  } catch (err) {
    console.error('Failed to load layer definitions:', err);
    return;
  }

  // Load parts-bridge (non-blocking, parts display is optional)
  fetch('data/architecture/parts-bridge.json')
    .then(r => r.ok ? r.json() : null)
    .then(data => { partsBridgeCache = data; })
    .catch(() => { /* parts-bridge not available yet — OK */ });

  // Determine which model to load from localStorage (default li7)
  const selectedModel = localStorage.getItem('llcar-model') || 'li7';
  const modelPath = selectedModel === 'li9'
    ? '../assets/models/Li9_unified.glb'
    : '../assets/models/Li7_unified.glb';
  const componentMapPath = selectedModel === 'li9'
    ? 'data/architecture/li9-component-map-v2.json'
    : 'data/architecture/li7-component-map-v2.json';

  try {
    await viewer.loadModel(modelPath, componentMapPath, layerDefsCache);
  } catch (err) {
    console.error('Failed to load 3D model:', err);
    const loadingEl = document.getElementById('twin-loading');
    if (loadingEl) {
      loadingEl.querySelector('.twin-loading__text').textContent = 'Failed to load 3D model';
      loadingEl.querySelector('.twin-loading__spinner').style.display = 'none';
    }
  }
}

/**
 * Cleanup the Digital Twin screen.
 */
export function cleanup() {
  off('model:progress', onModelProgress);
  off('model:loaded', onModelLoaded);
  off('component:hover', onComponentHover);
  off('component:select', onComponentSelect);
  off('component:deselect', onComponentDeselect);
  off('region:select', onRegionSelect);
  off('pid:data', onPidData);
  document.removeEventListener('lang:change', onLangChange);

  if (annotationOverlay) {
    annotationOverlay.dispose();
    annotationOverlay = null;
  }

  if (pidOverlay) {
    pidOverlay.dispose();
    pidOverlay = null;
  }

  if (viewer) {
    viewer.dispose();
    viewer = null;
  }

  // Keep partsBridgeCache — it's static data, no need to re-fetch

  if (screenEl) {
    screenEl.innerHTML = '';
    screenEl = null;
  }
}
