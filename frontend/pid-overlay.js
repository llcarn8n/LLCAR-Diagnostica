/**
 * PIDOverlay — CSS2D overlay system for PID sensor readings on 3D components.
 * Attaches floating data rectangles to 3D mesh positions using CSS2DRenderer.
 * Labels always face the camera (billboarding).
 *
 * Usage:
 *   const overlay = new PIDOverlay(viewer);
 *   overlay.bind('intake_manifold@engine', {
 *     pid: '0105', name: 'Coolant Temp', value: '92\u00b0C', unit: '\u00b0C', status: 'healthy'
 *   });
 *   overlay.setVisible(true);
 */

import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { emit, on, off } from './event-bus.js';

/** Demo PID bindings for testing (loaded when loadDemo() is called). */
const DEMO_PIDS = [
  { glossaryId: 'dvigatel_i4@engine',        pid: '0105', name: 'Coolant Temp',  value: '92\u00b0C',  status: 'healthy' },
  { glossaryId: 'batareya_vn@ev',            pid: '015B', name: 'Battery',       value: '14.2V',      status: 'healthy' },
  { glossaryId: 'vpusknoj_kollektor_i4@engine', pid: '0104', name: 'STFT',       value: '+8.2%',      status: 'warning' },
  { glossaryId: 'tormoz_pl@brakes',          pid: '010C', name: 'RPM',           value: '780',        status: 'healthy' },
];

export class PIDOverlay {
  /**
   * @param {import('./three-viewer.js').ThreeViewer} viewer
   */
  constructor(viewer) {
    this._viewer = viewer;
    this._visible = false;

    /**
     * glossaryId -> {
     *   pidData: object,
     *   css2dObject: CSS2DObject,
     *   domElement: HTMLElement,
     *   layerId: string,
     * }
     */
    this._overlays = new Map();

    // CSS2D renderer
    this._css2dRenderer = new CSS2DRenderer();
    const w = viewer.renderer.domElement.clientWidth;
    const h = viewer.renderer.domElement.clientHeight;
    this._css2dRenderer.setSize(w, h);
    this._css2dRenderer.domElement.style.position = 'absolute';
    this._css2dRenderer.domElement.style.top = '0';
    this._css2dRenderer.domElement.style.left = '0';
    this._css2dRenderer.domElement.style.pointerEvents = 'none';
    this._css2dRenderer.domElement.style.overflow = 'hidden';

    // Append to viewer container (on top of WebGL canvas)
    viewer.container.appendChild(this._css2dRenderer.domElement);

    // Register with the viewer's render loop
    viewer.setPIDOverlay(this);

    // Resize handling
    this._onResize = () => this.resize();
    window.addEventListener('resize', this._onResize);

    // Layer sync: hide overlays when their layer is hidden
    this._onLayerToggle = (e) => {
      const { layerId, visible } = e.detail;
      this.setLayerVisible(layerId, visible);
    };
    on('layer:toggle', this._onLayerToggle);
  }

  // ─── Public API ──────────────────────────────────────────

  /**
   * Bind a PID overlay to a 3D component.
   * @param {string} glossaryId - component glossary_id (e.g. 'intake_manifold@engine')
   * @param {object} pidData
   * @param {string} pidData.pid   - OBD PID code (e.g. '0105')
   * @param {string} pidData.name  - display name
   * @param {string} pidData.value - formatted value string (e.g. '92\u00b0C')
   * @param {string} [pidData.unit]   - unit (e.g. '\u00b0C')
   * @param {string} [pidData.status] - 'healthy' | 'warning' | 'critical'
   */
  bind(glossaryId, pidData) {
    // Remove existing overlay for this component
    if (this._overlays.has(glossaryId)) {
      this.unbind(glossaryId);
    }

    const status = pidData.status || 'healthy';

    // Create DOM element using the CSS classes from diagnostica.css
    const dom = this._createDOM(glossaryId, pidData, status);

    // Create CSS2DObject
    const css2d = new CSS2DObject(dom);
    css2d.visible = this._visible;

    // Position at component mesh center
    const meshes = this._viewer.getComponentMeshes(glossaryId);
    if (meshes.length > 0) {
      const center = this._getGroupCenter(meshes);
      css2d.position.copy(center);
    }

    // Add to scene
    this._viewer.scene.add(css2d);

    // Extract layer from glossaryId (format: name@layer)
    const layerId = glossaryId.includes('@') ? glossaryId.split('@')[1] : 'unknown';

    this._overlays.set(glossaryId, {
      pidData: { ...pidData, status },
      css2dObject: css2d,
      domElement: dom,
      layerId,
    });
  }

  /**
   * Remove PID overlay for a component.
   * @param {string} glossaryId
   */
  unbind(glossaryId) {
    const entry = this._overlays.get(glossaryId);
    if (!entry) return;

    if (entry.css2dObject.parent) {
      entry.css2dObject.parent.remove(entry.css2dObject);
    }
    this._overlays.delete(glossaryId);
  }

  /**
   * Update value/status of an existing overlay without recreating.
   * @param {string} glossaryId
   * @param {object} pidData - partial update: { value?, status?, name? }
   */
  update(glossaryId, pidData) {
    const entry = this._overlays.get(glossaryId);
    if (!entry) return;

    // Merge updated fields
    if (pidData.value !== undefined) entry.pidData.value = pidData.value;
    if (pidData.status !== undefined) entry.pidData.status = pidData.status;
    if (pidData.name !== undefined) entry.pidData.name = pidData.name;

    // Update DOM
    this._updateDOM(entry.domElement, entry.pidData);

    emit('pid:update', { glossaryId, pidData: entry.pidData });
  }

  /**
   * Show/hide all PID overlays.
   * @param {boolean} visible
   */
  setVisible(visible) {
    this._visible = visible;
    for (const entry of this._overlays.values()) {
      entry.css2dObject.visible = visible;
    }
    this._css2dRenderer.domElement.style.display = visible ? '' : 'none';
    emit('pid:visibility', { visible });
  }

  /** @returns {boolean} */
  get visible() {
    return this._visible;
  }

  /**
   * Show/hide PID overlays for a specific layer.
   * @param {string} layerId
   * @param {boolean} visible
   */
  setLayerVisible(layerId, visible) {
    for (const entry of this._overlays.values()) {
      if (entry.layerId === layerId) {
        entry.css2dObject.visible = this._visible && visible;
      }
    }
  }

  /** Remove all overlays. */
  clear() {
    for (const glossaryId of [...this._overlays.keys()]) {
      this.unbind(glossaryId);
    }
  }

  /** Update CSS2DRenderer size to match the WebGL renderer. */
  resize() {
    const w = this._viewer.renderer.domElement.clientWidth;
    const h = this._viewer.renderer.domElement.clientHeight;
    this._css2dRenderer.setSize(w, h);
  }

  /**
   * Render pass — called by ThreeViewer's animation loop.
   * Must be called every frame for labels to track camera.
   */
  render() {
    if (this._visible) {
      this._css2dRenderer.render(this._viewer.scene, this._viewer.camera);
    }
  }

  /**
   * Bind the demo PIDs for testing.
   */
  loadDemo() {
    for (const d of DEMO_PIDS) {
      this.bind(d.glossaryId, {
        pid: d.pid,
        name: d.name,
        value: d.value,
        status: d.status,
      });
    }
  }

  /** Full cleanup. */
  dispose() {
    this.clear();

    window.removeEventListener('resize', this._onResize);
    off('layer:toggle', this._onLayerToggle);

    // Detach from viewer render loop
    this._viewer.setPIDOverlay(null);

    if (this._css2dRenderer.domElement.parentNode) {
      this._css2dRenderer.domElement.parentNode.removeChild(this._css2dRenderer.domElement);
    }
  }

  // ─── DOM ─────────────────────────────────────────────────

  /**
   * Create the overlay DOM element.
   * Uses .pid-overlay classes from diagnostica.css.
   * @param {string} glossaryId
   * @param {object} pidData
   * @param {string} status
   * @returns {HTMLElement}
   */
  _createDOM(glossaryId, pidData, status) {
    const el = document.createElement('div');
    el.className = 'pid-overlay';
    el.dataset.glossaryId = glossaryId;
    el.dataset.status = status;

    if (status === 'warning') {
      el.classList.add('pid-overlay--warning');
    } else if (status === 'critical') {
      el.classList.add('pid-overlay--critical');
    }

    el.innerHTML = `
      <span class="pid-overlay__dot${status !== 'healthy' ? ' pid-overlay__dot--' + status : ''}"></span>
      <span class="pid-overlay__value${status !== 'healthy' ? ' pid-overlay__value--' + status : ''}">${this._esc(pidData.value || '--')}</span>
      <span class="pid-overlay__label">${this._esc(pidData.name || '')}</span>
    `;

    // pointer-events on the individual overlay so clicks work
    // even though the overlay layer container is pointer-events: none
    el.style.pointerEvents = 'auto';
    el.style.cursor = 'pointer';
    el.style.whiteSpace = 'nowrap';
    // Offset upward so the tag floats above the mesh center
    el.style.transform = 'translate(-50%, -100%) translateY(-6px)';

    el.addEventListener('click', (e) => {
      e.stopPropagation();
      emit('component:select', { glossaryId });
      emit('pid:click', { glossaryId, pidData });
    });

    return el;
  }

  /**
   * Update an existing DOM element with new pidData.
   * @param {HTMLElement} dom
   * @param {object} pidData
   */
  _updateDOM(dom, pidData) {
    const status = pidData.status || 'healthy';

    // Update data attribute
    dom.dataset.status = status;

    // Update status classes
    dom.classList.remove('pid-overlay--warning', 'pid-overlay--critical');
    if (status === 'warning') dom.classList.add('pid-overlay--warning');
    if (status === 'critical') dom.classList.add('pid-overlay--critical');

    // Dot
    const dot = dom.querySelector('.pid-overlay__dot');
    if (dot) {
      dot.className = 'pid-overlay__dot';
      if (status !== 'healthy') dot.classList.add('pid-overlay__dot--' + status);
    }

    // Value
    const valEl = dom.querySelector('.pid-overlay__value');
    if (valEl) {
      valEl.textContent = pidData.value || '--';
      valEl.className = 'pid-overlay__value';
      if (status !== 'healthy') valEl.classList.add('pid-overlay__value--' + status);
    }

    // Label
    const labelEl = dom.querySelector('.pid-overlay__label');
    if (labelEl && pidData.name) {
      labelEl.textContent = pidData.name;
    }
  }

  // ─── Geometry helpers ────────────────────────────────────

  /**
   * Compute the center of a group of meshes (world-space).
   * @param {THREE.Mesh[]} meshes
   * @returns {THREE.Vector3}
   */
  _getGroupCenter(meshes) {
    const box = new THREE.Box3();
    for (const mesh of meshes) {
      box.expandByObject(mesh);
    }
    const center = new THREE.Vector3();
    box.getCenter(center);
    return center;
  }

  // ─── Utils ──────────────────────────────────────────────

  _esc(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }
}
