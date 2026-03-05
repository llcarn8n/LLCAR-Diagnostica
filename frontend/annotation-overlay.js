/**
 * AnnotationOverlay — CSS2D маркеры для компонентов без 3D-геометрии.
 * Аннотации-точки в 3D пространстве, привязанные к ближайшим мешам.
 * По аналогии с PIDOverlay, но для статических маркеров (датчики, блоки управления и т.д.).
 *
 * Использование:
 *   const overlay = new AnnotationOverlay(viewer);
 *   await overlay.load('data/architecture/annotation-config.json');
 *   overlay.setVisible(true);
 */

import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { emit, on, off } from './event-bus.js';

/** Иконки по категориям аннотаций */
const CATEGORY_ICONS = {
  // Sensors & ADAS
  camera: '\u{1F4F7}',
  adas: '\u{1F441}',
  radar: '\u{1F4E1}',
  sonar: '\u{1F4E1}',
  inertial: '\u{1F9ED}',
  safety: '\u{1F6E1}',
  controller: '\u{1F4BB}',
  // Engine
  ignition: '\u{26A1}',
  fuel: '\u{26FD}',
  exhaust: '\u{1F4A8}',
  emission: '\u{1F32C}',
  intake: '\u{1F32C}',
  pump: '\u{2699}',
  cooling: '\u{2744}',
  electrical: '\u{26A1}',
  // Brakes & steering
  'brake-disc': '\u{1F6D1}',
  'brake-control': '\u{1F6D1}',
  steering: '\u{1F3CE}',
  parking: '\u{1F17F}',
  // EV
  'power-electronics': '\u{26A1}',
  'battery-management': '\u{1F50B}',
  charging: '\u{1F50C}',
  // HVAC
  hvac: '\u{2744}',
  filtration: '\u{1F32C}',
  // Drivetrain
  suspension: '\u{1F504}',
  // Interior
  'control-module': '\u{1F4BB}',
  display: '\u{1F4FA}',
  connector: '\u{1F50C}',
  comfort: '\u{1F4BA}',
  audio: '\u{1F50A}',
  // Body
  'body-electrical': '\u{1F4A1}',
  lighting: '\u{1F4A1}',
  // Default
  default: '\u{1F4CD}',
};

export class AnnotationOverlay {
  /**
   * @param {import('./three-viewer.js').ThreeViewer} viewer
   */
  constructor(viewer) {
    this._viewer = viewer;
    this._visible = false;

    /**
     * glossaryId -> {
     *   config: object,       // данные из annotation-config.json
     *   css2dObject: CSS2DObject,
     *   domElement: HTMLElement,
     *   layerId: string,
     * }
     */
    this._annotations = new Map();

    /** @type {object|null} полный конфиг аннотаций */
    this._config = null;

    // CSS2D renderer (переиспользуем общий или создаём свой)
    this._css2dRenderer = new CSS2DRenderer();
    const w = viewer.renderer.domElement.clientWidth;
    const h = viewer.renderer.domElement.clientHeight;
    this._css2dRenderer.setSize(w, h);
    this._css2dRenderer.domElement.style.position = 'absolute';
    this._css2dRenderer.domElement.style.top = '0';
    this._css2dRenderer.domElement.style.left = '0';
    this._css2dRenderer.domElement.style.pointerEvents = 'none';
    this._css2dRenderer.domElement.style.overflow = 'hidden';
    this._css2dRenderer.domElement.classList.add('annotation-overlay-layer');

    // Добавляем поверх WebGL canvas
    viewer.container.appendChild(this._css2dRenderer.domElement);

    // Регистрируем в render loop viewer'а
    viewer.setAnnotationOverlay(this);

    // Resize
    this._onResize = () => this.resize();
    window.addEventListener('resize', this._onResize);

    // Синхронизация с видимостью слоёв
    this._onLayerToggle = (e) => {
      const { layerId, visible } = e.detail;
      this.setLayerVisible(layerId, visible);
    };
    on('layer:toggle', this._onLayerToggle);
  }

  // ─── Public API ──────────────────────────────────────────

  /**
   * Загрузить конфигурацию аннотаций из JSON.
   * @param {string} configPath — путь к annotation-config.json
   */
  async load(configPath) {
    const resp = await fetch(configPath);
    if (!resp.ok) {
      console.error(`AnnotationOverlay: не удалось загрузить ${configPath} (${resp.status})`);
      return;
    }
    this._config = await resp.json();

    // Строим кеш позиций мешей для привязки аннотаций
    this._computeModelTransform();

    // Считаем сколько аннотаций привязано к каждому anchor — для смещения
    const anchorCounts = new Map(); // anchorMesh → текущий индекс
    const annotations = this._config.annotations || {};
    for (const [glossaryId, annData] of Object.entries(annotations)) {
      const anchor = annData.anchorMesh || '';
      const idx = anchorCounts.get(anchor) || 0;
      this._createAnnotation(glossaryId, annData, idx);
      anchorCounts.set(anchor, idx + 1);
    }
  }

  /**
   * Построить кеш позиций мешей модели для привязки аннотаций к anchorMesh.
   * Вместо хардкоженных координат используем реальные позиции мешей из 3D модели.
   */
  _computeModelTransform() {
    /** @type {Map<string, THREE.Vector3>} имя меша → мировой центр */
    this._meshPositions = new Map();
    if (!this._viewer._modelRoot) return;

    // Собираем мировые позиции всех мешей
    this._viewer._modelRoot.traverse((child) => {
      if (!child.isMesh || !child.name) return;

      const meshBox = new THREE.Box3().setFromObject(child);
      const center = new THREE.Vector3();
      meshBox.getCenter(center);

      // Сохраняем с оригинальным именем (подчёркивания от sanitizeNodeName)
      this._meshPositions.set(child.name, center.clone());
    });
  }

  /**
   * Найти мировую позицию меша по anchorMesh имени.
   * Поддерживает нечёткий поиск: пробелы↔подчёркивания, частичное совпадение.
   * @param {string} anchorName — имя из annotation-config.json
   * @returns {THREE.Vector3|null}
   */
  _findAnchorPosition(anchorName) {
    if (!anchorName || !this._meshPositions || this._meshPositions.size === 0) return null;

    // Имя в конфиге с пробелами → в модели с подчёркиваниями (Three.js r182 sanitize)
    const sanitized = anchorName.replace(/ /g, '_');

    // 1. Точное совпадение
    if (this._meshPositions.has(sanitized)) return this._meshPositions.get(sanitized);
    if (this._meshPositions.has(anchorName)) return this._meshPositions.get(anchorName);

    // 2. Частичное совпадение — anchorName содержится в имени меша
    //    Например "Лобовое стекло" → "Лобовое_стекло#2_—_Стекло"
    const matches = [];
    for (const [meshName, pos] of this._meshPositions) {
      if (meshName.startsWith(sanitized) || meshName.includes(sanitized)) {
        matches.push(pos);
      }
    }

    if (matches.length > 0) {
      // Усреднённая позиция всех совпавших мешей (если деталь из нескольких частей)
      const avg = new THREE.Vector3();
      for (const p of matches) avg.add(p);
      avg.divideScalar(matches.length);
      return avg;
    }

    return null;
  }

  /**
   * Получить конфиг загруженных аннотаций.
   * @returns {object|null}
   */
  get config() {
    return this._config;
  }

  /**
   * Получить все аннотации (итерабельная Map).
   * @returns {Map}
   */
  get annotations() {
    return this._annotations;
  }

  /**
   * Показать/скрыть все аннотации.
   * @param {boolean} visible
   */
  setVisible(visible) {
    this._visible = visible;
    for (const entry of this._annotations.values()) {
      entry.css2dObject.visible = visible;
    }
    this._css2dRenderer.domElement.style.display = visible ? '' : 'none';
    emit('annotation:visibility', { visible });
  }

  /** @returns {boolean} */
  get visible() {
    return this._visible;
  }

  /**
   * Показать/скрыть аннотации конкретного слоя.
   * @param {string} layerId
   * @param {boolean} visible
   */
  setLayerVisible(layerId, visible) {
    // Поддержка '*' (все слои) из LayerManager.hideAll()
    if (layerId === '*') {
      for (const entry of this._annotations.values()) {
        entry.css2dObject.visible = this._visible && visible;
      }
      return;
    }
    for (const entry of this._annotations.values()) {
      if (entry.layerId === layerId) {
        entry.css2dObject.visible = this._visible && visible;
      }
    }
  }

  /**
   * Получить аннотации конкретного слоя.
   * @param {string} layerId
   * @returns {object[]}
   */
  getByLayer(layerId) {
    const result = [];
    for (const [glossaryId, entry] of this._annotations) {
      if (entry.layerId === layerId) {
        result.push({ glossaryId, ...entry.config });
      }
    }
    return result;
  }

  /**
   * Получить все glossary ID аннотаций.
   * @returns {string[]}
   */
  getAllGlossaryIds() {
    return [...this._annotations.keys()];
  }

  /**
   * Получить конфиг аннотации по glossaryId.
   * @param {string} glossaryId
   * @returns {object|undefined}
   */
  getAnnotation(glossaryId) {
    const entry = this._annotations.get(glossaryId);
    return entry ? entry.config : undefined;
  }

  /**
   * Подсветить аннотацию (например, при выборе из списка).
   * @param {string} glossaryId
   */
  highlight(glossaryId) {
    // Снять подсветку с предыдущих
    for (const entry of this._annotations.values()) {
      entry.domElement.classList.remove('annotation-marker--selected');
    }
    const entry = this._annotations.get(glossaryId);
    if (entry) {
      entry.domElement.classList.add('annotation-marker--selected');
    }
  }

  /** Снять подсветку со всех аннотаций. */
  clearHighlight() {
    for (const entry of this._annotations.values()) {
      entry.domElement.classList.remove('annotation-marker--selected');
    }
  }

  /** Обновить размер CSS2DRenderer. */
  resize() {
    const w = this._viewer.renderer.domElement.clientWidth;
    const h = this._viewer.renderer.domElement.clientHeight;
    this._css2dRenderer.setSize(w, h);
  }

  /**
   * Render pass — вызывается из ThreeViewer animation loop.
   */
  render() {
    if (this._visible) {
      this._css2dRenderer.render(this._viewer.scene, this._viewer.camera);
    }
  }

  /** Удалить все аннотации. */
  clear() {
    for (const [glossaryId, entry] of this._annotations) {
      if (entry.css2dObject.parent) {
        entry.css2dObject.parent.remove(entry.css2dObject);
      }
    }
    this._annotations.clear();
  }

  /** Полная очистка. */
  dispose() {
    this.clear();
    window.removeEventListener('resize', this._onResize);
    off('layer:toggle', this._onLayerToggle);

    this._viewer.setAnnotationOverlay(null);

    if (this._css2dRenderer.domElement.parentNode) {
      this._css2dRenderer.domElement.parentNode.removeChild(this._css2dRenderer.domElement);
    }
  }

  // ─── Приватные методы ─────────────────────────────────────

  /**
   * Создать одну аннотацию-маркер в 3D пространстве.
   * @param {string} glossaryId
   * @param {object} annData — запись из annotation-config.json
   * @param {number} anchorIndex — порядковый номер среди аннотаций с тем же anchor (для смещения)
   */
  _createAnnotation(glossaryId, annData, anchorIndex = 0) {
    const layerId = annData.layer || 'unknown';

    // Создаём DOM элемент маркера
    const dom = this._createDOM(glossaryId, annData);

    // Создаём CSS2DObject
    const css2d = new CSS2DObject(dom);
    css2d.visible = this._visible;

    // Позиция: берём из реального меша-якоря (anchorMesh).
    const anchorPos = this._findAnchorPosition(annData.anchorMesh);
    if (anchorPos) {
      css2d.position.copy(anchorPos);
      // Если несколько аннотаций на одном anchor — разносим по кругу
      if (anchorIndex > 0) {
        const angle = (anchorIndex * Math.PI * 2) / 5; // Раскладка по кругу (макс. ~5 точек)
        const radius = 0.15; // Радиус разноса
        css2d.position.x += Math.cos(angle) * radius;
        css2d.position.z += Math.sin(angle) * radius;
      }
    } else if (annData.position && annData.position.length === 3) {
      // Fallback: координаты из конфига (anchor не найден)
      console.warn(`AnnotationOverlay: anchor "${annData.anchorMesh}" не найден для ${glossaryId}`);
      css2d.position.set(annData.position[0], annData.position[1], annData.position[2]);
    } else {
      console.warn(`AnnotationOverlay: нет позиции для ${glossaryId}`);
    }

    // Добавляем в сцену
    this._viewer.scene.add(css2d);

    this._annotations.set(glossaryId, {
      config: annData,
      css2dObject: css2d,
      domElement: dom,
      layerId,
    });
  }

  /**
   * Создать DOM элемент маркера аннотации.
   * @param {string} glossaryId
   * @param {object} annData
   * @returns {HTMLElement}
   */
  _createDOM(glossaryId, annData) {
    const el = document.createElement('div');
    el.className = 'annotation-marker';
    el.dataset.glossaryId = glossaryId;
    el.dataset.layer = annData.layer || 'unknown';
    el.dataset.priority = annData.priority || 'P3';

    const icon = CATEGORY_ICONS[annData.category] || CATEGORY_ICONS.default;

    el.innerHTML = `
      <span class="annotation-marker__icon">${icon}</span>
      <span class="annotation-marker__pulse"></span>
    `;

    // pointer-events чтобы клики работали сквозь pointer-events: none контейнера
    el.style.pointerEvents = 'auto';
    el.style.cursor = 'pointer';

    // Клик — выбрать компонент и перейти в базу знаний
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      emit('component:select', {
        glossaryId,
        component: {
          glossary_id: glossaryId,
          layer: annData.layer,
          category: annData.category || '',
          displayName: glossaryId.split('@')[0].replace(/_/g, ' '),
          dtcCodes: annData.dtcCodes || [],
          isAnnotation: true,
        },
        meshCount: 0,
      });
      emit('annotation:click', { glossaryId, annData });
      // Переход в базу знаний к компоненту с дополнительными данными для поиска
      emit('twin:open-kb', {
        glossaryId,
        dtcCodes: annData.dtcCodes || [],
        category: annData.category || '',
        layer: annData.layer || '',
      });
    });

    // Hover — показать тултип
    el.addEventListener('mouseenter', () => {
      emit('component:hover', {
        glossaryId,
        displayName: glossaryId.split('@')[0].replace(/_/g, ' '),
        isAnnotation: true,
      });
      el.classList.add('annotation-marker--hover');
    });

    el.addEventListener('mouseleave', () => {
      emit('component:hover', { glossaryId: null });
      el.classList.remove('annotation-marker--hover');
    });

    return el;
  }
}
