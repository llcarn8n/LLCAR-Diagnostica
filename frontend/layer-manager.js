/**
 * LayerManager — Controls visibility and wireframe state of 8 diagnostic layers.
 * Works with ThreeViewer to show/hide/isolate/wireframe groups of meshes.
 */

import * as THREE from 'three';
import { emit } from './event-bus.js';

export class LayerManager {
  /**
   * @param {import('./three-viewer.js').ThreeViewer} viewer
   * @param {object} layerDefinitions - parsed layer-definitions.json
   */
  constructor(viewer, layerDefinitions) {
    this._viewer = viewer;
    this._layerDefs = layerDefinitions;

    /**
     * Map of layerId -> {
     *   meshes: THREE.Mesh[],
     *   visible: boolean,
     *   wireframe: boolean,
     *   ghost: boolean,
     *   originalMaterials: Map<THREE.Mesh, THREE.Material|THREE.Material[]>
     * }
     */
    this._layers = new Map();

    this._initLayers();
  }

  /** Build the internal layer map from layer definitions. */
  _initLayers() {
    const layers = this._layerDefs.layers || {};
    for (const layerId of Object.keys(layers)) {
      this._layers.set(layerId, {
        meshes: [],
        visible: true,
        wireframe: false,
        ghost: false,
        originalMaterials: new Map(),
      });
    }
    // Always have an 'unknown' bucket
    if (!this._layers.has('unknown')) {
      this._layers.set('unknown', {
        meshes: [],
        visible: true,
        wireframe: false,
        ghost: false,
        originalMaterials: new Map(),
      });
    }
  }

  /**
   * Register a mesh into a layer. Called during model load by the viewer.
   * @param {THREE.Mesh} mesh
   * @param {string} layerId
   */
  registerMesh(mesh, layerId) {
    const id = this._layers.has(layerId) ? layerId : 'unknown';
    const layer = this._layers.get(id);
    layer.meshes.push(mesh);
    // Store original material for later restoration
    layer.originalMaterials.set(mesh, mesh.material);
  }

  /**
   * Toggle a layer's visibility.
   * @param {string} layerId
   */
  toggle(layerId) {
    const layer = this._layers.get(layerId);
    if (!layer) return;
    layer.visible ? this.hide(layerId) : this.show(layerId);
  }

  /**
   * Показать конкретный слой.
   * @param {string} layerId
   */
  show(layerId) {
    const layer = this._layers.get(layerId);
    if (!layer) return;
    layer.visible = true;
    for (const mesh of layer.meshes) {
      mesh.visible = true;
    }
    emit('layer:toggle', { layerId, visible: true });
    if (layerId !== 'unknown') this._syncUnknown();
  }

  /**
   * Скрыть конкретный слой.
   * @param {string} layerId
   */
  hide(layerId) {
    const layer = this._layers.get(layerId);
    if (!layer) return;
    layer.visible = false;
    for (const mesh of layer.meshes) {
      mesh.visible = false;
    }
    emit('layer:toggle', { layerId, visible: false });
    if (layerId !== 'unknown') this._syncUnknown();
  }

  /**
   * Синхронизация слоя 'unknown' с остальными:
   * если все основные слои скрыты — скрыть unknown тоже,
   * если хоть один показан — показать unknown.
   */
  _syncUnknown() {
    const unknownLayer = this._layers.get('unknown');
    if (!unknownLayer || unknownLayer.meshes.length === 0) return;

    let anyVisible = false;
    for (const [id, layer] of this._layers) {
      if (id !== 'unknown' && layer.visible) {
        anyVisible = true;
        break;
      }
    }

    if (anyVisible && !unknownLayer.visible) {
      unknownLayer.visible = true;
      for (const mesh of unknownLayer.meshes) mesh.visible = true;
    } else if (!anyVisible && unknownLayer.visible) {
      unknownLayer.visible = false;
      for (const mesh of unknownLayer.meshes) mesh.visible = false;
    }
  }

  /** Показать все слои, восстановив wireframe/ghost. */
  showAll() {
    for (const layerId of this._layers.keys()) {
      this.show(layerId);
      if (this._layers.get(layerId).wireframe) {
        this.setWireframe(layerId, false);
      }
      if (this._layers.get(layerId).ghost) {
        this.setGhost(layerId, false);
      }
    }
    // Гарантия: показать все меши в модели (на случай незарегистрированных)
    if (this._viewer._modelRoot) {
      this._viewer._modelRoot.traverse((child) => {
        if (child.isMesh) child.visible = true;
      });
    }
  }

  /** Скрыть ВСЕ слои включая unknown + все незарегистрированные меши. */
  hideAll() {
    for (const layerId of this._layers.keys()) {
      const layer = this._layers.get(layerId);
      layer.visible = false;
      for (const mesh of layer.meshes) {
        mesh.visible = false;
      }
    }
    // Гарантия: скрыть ВСЕ меши в модели (даже незарегистрированные)
    if (this._viewer._modelRoot) {
      this._viewer._modelRoot.traverse((child) => {
        if (child.isMesh) child.visible = false;
      });
    }
    emit('layer:toggle', { layerId: '*', visible: false });
  }

  /**
   * Isolate a single layer: show it fully, make all others semi-transparent (ghost).
   * @param {string} layerId
   */
  isolate(layerId) {
    for (const id of this._layers.keys()) {
      if (id === layerId) {
        this.show(id);
        this.setWireframe(id, false);
        this.setGhost(id, false);
      } else {
        // unknown и остальные слои — полупрозрачные
        this.show(id);
        this.setWireframe(id, false);
        this.setGhost(id, true);
      }
    }
    emit('layer:isolate', { layerId });
  }

  /**
   * Set ghost (translucent) mode for a layer.
   * Meshes become semi-transparent to let the isolated layer shine through.
   * @param {string} layerId
   * @param {boolean} enabled
   */
  setGhost(layerId, enabled) {
    const layer = this._layers.get(layerId);
    if (!layer) return;

    const layerDef = (this._layerDefs.layers || {})[layerId];
    const color = layerDef ? layerDef.color : '#888888';

    if (enabled && !layer.ghost) {
      const ghostMat = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        opacity: 0.08,
        transparent: true,
        depthWrite: false,
        side: THREE.DoubleSide,
        roughness: 0.9,
        metalness: 0,
      });
      for (const mesh of layer.meshes) {
        // Store original if not already stored by wireframe
        if (!layer.wireframe) {
          // original is already stored when mesh was registered
        }
        mesh.material = ghostMat;
        mesh.renderOrder = -1; // render behind opaque layers
      }
      layer.ghost = true;
    } else if (!enabled && layer.ghost) {
      // Restore original materials
      for (const mesh of layer.meshes) {
        const orig = layer.originalMaterials.get(mesh);
        if (orig) {
          mesh.material = orig;
          mesh.renderOrder = 0;
        }
      }
      layer.ghost = false;
    }
  }

  /**
   * Set wireframe mode for a layer.
   * @param {string} layerId
   * @param {boolean} enabled
   */
  setWireframe(layerId, enabled) {
    const layer = this._layers.get(layerId);
    if (!layer) return;

    const layerDef = (this._layerDefs.layers || {})[layerId];
    const color = layerDef ? layerDef.color : '#888888';

    if (enabled && !layer.wireframe) {
      // Switch to wireframe material
      const wireMat = new THREE.MeshBasicMaterial({
        wireframe: true,
        color: new THREE.Color(color),
        opacity: 0.3,
        transparent: true,
        depthWrite: false,
      });
      for (const mesh of layer.meshes) {
        mesh.material = wireMat;
      }
      layer.wireframe = true;
    } else if (!enabled && layer.wireframe) {
      // Restore original materials
      for (const mesh of layer.meshes) {
        const orig = layer.originalMaterials.get(mesh);
        if (orig) {
          mesh.material = orig;
        }
      }
      layer.wireframe = false;
    }
  }

  /**
   * Get current visibility state of all layers.
   * @returns {Object<string, boolean>}
   */
  getState() {
    const state = {};
    for (const [id, layer] of this._layers) {
      state[id] = layer.visible;
    }
    return state;
  }

  /**
   * Get layer definitions enriched with mesh counts and annotation counts.
   * @returns {object[]}
   */
  getLayers() {
    const defs = this._layerDefs.layers || {};
    const result = [];
    // Получаем количество аннотаций из TagRegistry (если доступен)
    const annCounts = this._viewer.tagRegistry?.getAnnotationCounts() || {};
    for (const [id, def] of Object.entries(defs)) {
      const layer = this._layers.get(id);
      result.push({
        id,
        ...def,
        meshCount: layer ? layer.meshes.length : 0,
        annotationCount: annCounts[id] || 0,
        visible: layer ? layer.visible : true,
        wireframe: layer ? layer.wireframe : false,
        ghost: layer ? layer.ghost : false,
      });
    }
    return result;
  }

  /**
   * Clear all meshes (call before loading a new model).
   */
  clear() {
    for (const layer of this._layers.values()) {
      layer.meshes = [];
      layer.originalMaterials.clear();
      layer.wireframe = false;
      layer.ghost = false;
      layer.visible = true;
    }
  }
}
