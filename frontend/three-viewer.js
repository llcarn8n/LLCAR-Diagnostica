/**
 * ThreeViewer — Core 3D viewer for the LLCAR Diagnostica app.
 * Loads GLB models, maps meshes to the 8-layer system via component-map,
 * provides raycasting, selection highlighting, X-ray mode.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { TagRegistry } from './tag-registry.js';
import { LayerManager } from './layer-manager.js';
import { emit } from './event-bus.js';

const BG_COLOR = 0x0D1117;

export class ThreeViewer {
  /**
   * @param {HTMLElement} containerElement - DOM element to render into
   */
  constructor(containerElement) {
    this._container = containerElement;
    this._disposed = false;

    // Registries (populated on loadModel)
    /** @type {TagRegistry} */
    this.tagRegistry = new TagRegistry();
    /** @type {LayerManager|null} */
    this.layerManager = null;

    // Three.js core
    this._scene = new THREE.Scene();
    this._scene.background = new THREE.Color(BG_COLOR);
    this._scene.fog = new THREE.Fog(BG_COLOR, 15, 35);

    this._camera = new THREE.PerspectiveCamera(
      45,
      containerElement.clientWidth / containerElement.clientHeight,
      0.01,
      100
    );
    this._camera.position.set(4, 2.5, 4);
    this._camera.lookAt(0, 0, 0);

    this._renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: 'high-performance',
    });
    this._renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this._renderer.setSize(containerElement.clientWidth, containerElement.clientHeight);
    this._renderer.shadowMap.enabled = true;
    this._renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this._renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this._renderer.toneMappingExposure = 1.0;
    this._renderer.sortObjects = true;
    containerElement.appendChild(this._renderer.domElement);

    // Controls
    this._controls = new OrbitControls(this._camera, this._renderer.domElement);
    this._controls.enableDamping = true;
    this._controls.dampingFactor = 0.05;
    this._controls.autoRotate = true;
    this._controls.autoRotateSpeed = 0.5;
    this._controls.maxDistance = 20;
    this._controls.minDistance = 1;

    // Stop auto-rotate on user interaction
    this._onControlStart = () => { this._controls.autoRotate = false; };
    this._controls.addEventListener('start', this._onControlStart);

    // Lighting
    this._setupLights();

    // Raycasting
    this._raycaster = new THREE.Raycaster();
    this._mouse = new THREE.Vector2();
    this._selectableMeshes = [];

    // Selection state
    this._selectedGlossaryId = null;
    this._selectedMeshes = [];
    /** @type {Map<THREE.Mesh, THREE.Material|THREE.Material[]>} */
    this._originalMaterialsForSelection = new Map();

    // Hover state
    this._hoveredMesh = null;
    this._hoveredOrigMaterial = null;

    // X-ray state (managed via LayerManager ghost mode)
    this._xrayEnabled = false;

    // Model root (for disposal)
    this._modelRoot = null;

    // Mesh name -> component data lookup (flat for raycasting)
    /** @type {Map<THREE.Mesh, object>} */
    this._meshToComponent = new Map();

    // Event handlers
    this._onPointerMove = this._handlePointerMove.bind(this);
    this._onClick = this._handleClick.bind(this);
    this._onResize = this.resize.bind(this);

    this._renderer.domElement.addEventListener('pointermove', this._onPointerMove);
    this._renderer.domElement.addEventListener('click', this._onClick);
    window.addEventListener('resize', this._onResize);

    // Start render loop
    this._animate();
  }

  // ─── Lighting ───────────────────────────────────────────

  _setupLights() {
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    this._scene.add(ambient);

    const hemi = new THREE.HemisphereLight(0xddeeff, 0x0D1117, 0.3);
    this._scene.add(hemi);

    const dir = new THREE.DirectionalLight(0xffffff, 0.8);
    dir.position.set(5, 8, 5);
    dir.castShadow = true;
    dir.shadow.mapSize.width = 2048;
    dir.shadow.mapSize.height = 2048;
    dir.shadow.camera.near = 0.5;
    dir.shadow.camera.far = 30;
    dir.shadow.camera.left = -8;
    dir.shadow.camera.right = 8;
    dir.shadow.camera.top = 8;
    dir.shadow.camera.bottom = -8;
    dir.shadow.bias = -0.0005;
    this._scene.add(dir);

    // Fill light from the opposite side
    const fill = new THREE.DirectionalLight(0xffffff, 0.25);
    fill.position.set(-4, 3, -4);
    this._scene.add(fill);
  }

  // ─── Model Loading ──────────────────────────────────────

  /**
   * Load a GLB model and map its meshes to the component map / layer system.
   * @param {string} modelPath - path to .glb file
   * @param {string} componentMapPath - path to component-map-v2.json
   * @param {object} layerDefinitions - parsed layer-definitions.json
   * @returns {Promise<void>}
   */
  async loadModel(modelPath, componentMapPath, layerDefinitions) {
    // Load tag registry
    await this.tagRegistry.load(componentMapPath);

    // Загрузить аннотации (компоненты без 3D-геометрии)
    const annotationConfigPath = componentMapPath.replace(/li[79]-component-map-v2\.json$/, 'annotation-config.json');
    await this.tagRegistry.loadAnnotations(annotationConfigPath);

    // Create layer manager
    this.layerManager = new LayerManager(this, layerDefinitions);

    // Load GLB (with Draco decoder for compressed meshes)
    const loader = new GLTFLoader();
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath('../../node_modules/three/examples/jsm/libs/draco/gltf/');
    loader.setDRACOLoader(dracoLoader);

    const gltf = await new Promise((resolve, reject) => {
      loader.load(
        modelPath,
        resolve,
        (progress) => {
          if (progress.total > 0) {
            const pct = Math.round((progress.loaded / progress.total) * 100);
            emit('model:progress', { percent: pct });
          }
        },
        reject
      );
    });

    const model = gltf.scene;

    // Center and scale
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const scale = 4.0 / maxDim; // fit in ~4 unit sphere

    model.position.sub(center.multiplyScalar(scale));
    model.scale.setScalar(scale);

    // Traverse and tag meshes
    this._selectableMeshes = [];
    this._meshToComponent.clear();

    model.traverse((child) => {
      if (!child.isMesh) return;

      const meshName = child.name || '';
      let comp = this.tagRegistry.getByMeshName(meshName);

      // Fallback: multi-prim дочерние меши — проверяем имя родителя (Group)
      if (!comp && child.parent) {
        const parentName = child.parent.name || '';
        if (parentName) {
          comp = this.tagRegistry.getByMeshName(parentName);
        }
      }

      if (comp) {
        child.userData.glossaryId = comp.glossary_id;
        child.userData.layer = comp.layer;
        child.userData.selectable = comp.selectable !== false;
        child.userData.xray_transparent = !!comp.xray_transparent;
        child.userData.displayName = comp.displayName || meshName;
        this._meshToComponent.set(child, comp);

        if (child.userData.selectable) {
          this._selectableMeshes.push(child);
        }

        // Register with layer manager
        this.layerManager.registerMesh(child, comp.layer);
      } else {
        // Not in component map
        child.userData.layer = 'unknown';
        child.userData.selectable = true;
        child.userData.glossaryId = null;
        this._selectableMeshes.push(child);
        this.layerManager.registerMesh(child, 'unknown');
      }

      // Enable shadows
      child.castShadow = true;
      child.receiveShadow = true;
    });

    this._modelRoot = model;
    this._scene.add(model);

    emit('model:loaded', {
      meshCount: this._selectableMeshes.length,
      layers: this.layerManager.getLayers(),
    });
  }

  // ─── Raycasting ─────────────────────────────────────────

  /**
   * Get the component glossary_id at screen coordinates.
   * @param {number} x - screen X (clientX)
   * @param {number} y - screen Y (clientY)
   * @returns {string|null} glossary_id or null
   */
  getComponentAtPoint(x, y) {
    const rect = this._renderer.domElement.getBoundingClientRect();
    this._mouse.x = ((x - rect.left) / rect.width) * 2 - 1;
    this._mouse.y = -((y - rect.top) / rect.height) * 2 + 1;

    this._raycaster.setFromCamera(this._mouse, this._camera);
    const intersects = this._raycaster.intersectObjects(this._selectableMeshes, false);

    if (intersects.length > 0) {
      const mesh = intersects[0].object;
      return mesh.userData.glossaryId || null;
    }
    return null;
  }

  _handlePointerMove(event) {
    const rect = this._renderer.domElement.getBoundingClientRect();
    this._mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this._mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    this._raycaster.setFromCamera(this._mouse, this._camera);
    const intersects = this._raycaster.intersectObjects(this._selectableMeshes, false);

    // Clear previous hover
    if (this._hoveredMesh && this._hoveredMesh !== this._getFirstSelectedMesh()) {
      this._restoreHover();
    }

    if (intersects.length > 0) {
      const mesh = intersects[0].object;
      // Don't hover-highlight already selected meshes
      if (this._selectedMeshes.includes(mesh)) {
        this._renderer.domElement.style.cursor = 'pointer';
        return;
      }

      this._hoveredMesh = mesh;
      this._hoveredOrigMaterial = mesh.material;

      // Apply subtle emissive glow
      if (mesh.material && mesh.material.isMeshStandardMaterial) {
        mesh.material = mesh.material.clone();
        mesh.material.emissive = new THREE.Color(0x334466);
        mesh.material.emissiveIntensity = 0.5;
      }

      this._renderer.domElement.style.cursor = 'pointer';

      emit('component:hover', {
        glossaryId: mesh.userData.glossaryId,
        displayName: mesh.userData.displayName || mesh.name,
      });
    } else {
      this._renderer.domElement.style.cursor = 'default';
      emit('component:hover', { glossaryId: null });
    }
  }

  _restoreHover() {
    if (this._hoveredMesh && this._hoveredOrigMaterial) {
      // Only restore if this mesh is not in selection highlight
      if (!this._originalMaterialsForSelection.has(this._hoveredMesh)) {
        this._hoveredMesh.material = this._hoveredOrigMaterial;
      }
    }
    this._hoveredMesh = null;
    this._hoveredOrigMaterial = null;
  }

  _getFirstSelectedMesh() {
    return this._selectedMeshes.length > 0 ? this._selectedMeshes[0] : null;
  }

  _handleClick(event) {
    const glossaryId = this.getComponentAtPoint(event.clientX, event.clientY);
    if (glossaryId) {
      this.selectComponent(glossaryId);
    } else {
      this.clearSelection();
    }
  }

  // ─── Selection ──────────────────────────────────────────

  /**
   * Highlight all meshes belonging to a glossary_id.
   * @param {string} glossaryId
   */
  selectComponent(glossaryId) {
    // Clear previous selection
    this.clearSelection();

    this._selectedGlossaryId = glossaryId;

    // Determine highlight color from layer
    const comp = this.tagRegistry.getComponent(glossaryId);
    let highlightColor = 0xFF7043; // fallback
    if (comp && comp.layer) {
      const layerDef = (this.layerManager?._layerDefs?.layers || {})[comp.layer];
      if (layerDef) {
        highlightColor = new THREE.Color(layerDef.color).getHex();
      }
    }

    // Find all meshes with this glossary_id
    for (const mesh of this._selectableMeshes) {
      if (mesh.userData.glossaryId === glossaryId) {
        this._selectedMeshes.push(mesh);
        this._originalMaterialsForSelection.set(mesh, mesh.material);

        // Apply highlight material
        const hlMat = mesh.material.isMeshStandardMaterial
          ? mesh.material.clone()
          : new THREE.MeshStandardMaterial();

        hlMat.emissive = new THREE.Color(highlightColor);
        hlMat.emissiveIntensity = 0.6;
        mesh.material = hlMat;
      }
    }

    emit('component:select', {
      glossaryId,
      component: comp || null,
      meshCount: this._selectedMeshes.length,
    });
  }

  /** Clear current selection, restore original materials. */
  clearSelection() {
    for (const mesh of this._selectedMeshes) {
      const orig = this._originalMaterialsForSelection.get(mesh);
      if (orig) {
        mesh.material = orig;
      }
    }
    this._selectedMeshes = [];
    this._originalMaterialsForSelection.clear();

    if (this._selectedGlossaryId) {
      this._selectedGlossaryId = null;
      emit('component:deselect', {});
    }
  }

  // ─── X-ray Mode ─────────────────────────────────────────

  /** Outer shell layers that X-ray makes transparent */
  static XRAY_SHELL_LAYERS = ['body', 'interior'];

  /**
   * Toggle X-ray mode via LayerManager.
   * - When ON: outer shell layers (body, interior) become ghost (semi-transparent),
   *   revealing inner systems (engine, drivetrain, ev, brakes, sensors, hvac).
   * - When a specific layer is isolated while X-ray is ON, only that layer is fully
   *   visible; everything else (including shell) becomes ghost.
   * @param {boolean} enabled
   */
  setXray(enabled) {
    if (this._xrayEnabled === enabled) return;
    this._xrayEnabled = enabled;

    if (!this.layerManager) return;

    if (enabled) {
      // Ghost the outer shell layers, keep internal systems visible
      for (const layerId of ThreeViewer.XRAY_SHELL_LAYERS) {
        this.layerManager.setGhost(layerId, true);
      }
    } else {
      // Restore all shell layers from ghost
      for (const layerId of ThreeViewer.XRAY_SHELL_LAYERS) {
        this.layerManager.setGhost(layerId, false);
      }
    }

    emit('xray:toggle', { enabled });
  }

  /** @returns {boolean} Whether X-ray mode is active */
  get xrayEnabled() { return this._xrayEnabled; }

  // ─── Resize ─────────────────────────────────────────────

  /** Update renderer and camera on container resize. */
  resize() {
    const w = this._container.clientWidth;
    const h = this._container.clientHeight;
    if (w === 0 || h === 0) return;

    this._camera.aspect = w / h;
    this._camera.updateProjectionMatrix();
    this._renderer.setSize(w, h);
  }

  // ─── Animation Loop ────────────────────────────────────

  _animate() {
    if (this._disposed) return;
    requestAnimationFrame(() => this._animate());
    this._controls.update();
    this._renderer.render(this._scene, this._camera);
    // Render PID overlays (CSS2D) if attached
    if (this._pidOverlay) {
      this._pidOverlay.render();
    }
    // Render annotation overlays (CSS2D) if attached
    if (this._annotationOverlay) {
      this._annotationOverlay.render();
    }
  }

  // ─── Public Accessors ──────────────────────────────────

  /** @returns {THREE.Scene} */
  get scene() { return this._scene; }
  /** @returns {THREE.Camera} */
  get camera() { return this._camera; }
  /** @returns {THREE.WebGLRenderer} */
  get renderer() { return this._renderer; }
  /** @returns {OrbitControls} */
  get controls() { return this._controls; }
  /** @returns {HTMLElement} */
  get container() { return this._container; }
  /** @returns {string|null} currently selected glossary_id */
  get selectedGlossaryId() { return this._selectedGlossaryId; }

  /**
   * Get all meshes matching a glossary_id.
   * @param {string} glossaryId
   * @returns {THREE.Mesh[]}
   */
  getComponentMeshes(glossaryId) {
    return this._selectableMeshes.filter(m => m.userData.glossaryId === glossaryId);
  }

  /**
   * Select a component by glossary_id (alias for selectComponent).
   * Also focuses the camera on it.
   * @param {string} glossaryId
   */
  selectByGlossaryId(glossaryId) {
    this.selectComponent(glossaryId);
    // Focus camera on selected meshes
    if (this._selectedMeshes.length > 0) {
      const box = new THREE.Box3();
      for (const mesh of this._selectedMeshes) {
        box.expandByObject(mesh);
      }
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const dist = Math.max(size.x, size.y, size.z) * 2.5;
      this._controls.target.copy(center);
      this._camera.position.copy(center).add(new THREE.Vector3(dist, dist * 0.6, dist));
      this._controls.autoRotate = false;
    }
  }

  // ─── Group‐level (regional) highlighting ─────────────────

  /** Map diagnostic groups → viz_layer keys used in mesh userData.layer */
  static GROUP_LAYERS = {
    electric:   ['ev'],
    fuel:       ['drivetrain', 'engine'],
    suspension: ['brakes'],
    cabin:      ['body', 'hvac', 'interior'],
    tech:       ['sensors'],
  };

  /**
   * Highlight ALL meshes belonging to a diagnostic group (regional highlight).
   * Uses a softer emissive intensity (0.25) to differentiate from specific selection.
   * @param {string} groupName - one of: electric, fuel, suspension, cabin, tech
   */
  selectByGroup(groupName) {
    const layers = ThreeViewer.GROUP_LAYERS[groupName];
    if (!layers || layers.length === 0) return;

    this.clearSelection();
    this._selectedGlossaryId = `__group:${groupName}`;

    const layerSet = new Set(layers);
    const groupColor = { electric: 0x42A5F5, fuel: 0xFF7043, suspension: 0x66BB6A, cabin: 0xAB47BC, tech: 0x26C6DA };
    const color = new THREE.Color(groupColor[groupName] || 0xFF7043);

    for (const mesh of this._selectableMeshes) {
      const meshLayer = mesh.userData.layer;
      if (meshLayer && layerSet.has(meshLayer)) {
        this._selectedMeshes.push(mesh);
        this._originalMaterialsForSelection.set(mesh, mesh.material);

        const hlMat = mesh.material.isMeshStandardMaterial
          ? mesh.material.clone()
          : new THREE.MeshStandardMaterial();
        hlMat.emissive = color;
        hlMat.emissiveIntensity = 0.25;
        mesh.material = hlMat;
      }
    }

    // Focus camera on the group region
    if (this._selectedMeshes.length > 0) {
      const box = new THREE.Box3();
      for (const mesh of this._selectedMeshes) {
        box.expandByObject(mesh);
      }
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const dist = Math.max(size.x, size.y, size.z) * 2.0;
      this._controls.target.copy(center);
      this._camera.position.copy(center).add(new THREE.Vector3(dist, dist * 0.6, dist));
      this._controls.autoRotate = false;
    }

    emit('component:select', {
      glossaryId: null,
      groupName,
      component: null,
      meshCount: this._selectedMeshes.length,
      isRegional: true,
    });
  }

  /**
   * Attach a PID overlay to the render loop.
   * The overlay must have a render() method.
   * @param {{ render: () => void }|null} pidOverlay
   */
  setPIDOverlay(pidOverlay) {
    this._pidOverlay = pidOverlay;
  }

  /**
   * Attach an annotation overlay to the render loop.
   * The overlay must have a render() method.
   * @param {{ render: () => void }|null} annotationOverlay
   */
  setAnnotationOverlay(annotationOverlay) {
    this._annotationOverlay = annotationOverlay;
  }

  // ─── Disposal ──────────────────────────────────────────

  /** Full cleanup: dispose geometries, materials, textures, renderer. */
  dispose() {
    this._disposed = true;

    // Remove event listeners
    this._renderer.domElement.removeEventListener('pointermove', this._onPointerMove);
    this._renderer.domElement.removeEventListener('click', this._onClick);
    window.removeEventListener('resize', this._onResize);
    this._controls.removeEventListener('start', this._onControlStart);

    // Dispose controls
    this._controls.dispose();

    // Traverse and dispose all geometries/materials/textures
    if (this._modelRoot) {
      this._modelRoot.traverse((child) => {
        if (child.isMesh) {
          if (child.geometry) child.geometry.dispose();
          this._disposeMaterial(child.material);
        }
      });
      this._scene.remove(this._modelRoot);
    }

    // Dispose renderer
    this._renderer.dispose();
    if (this._renderer.domElement.parentNode) {
      this._renderer.domElement.parentNode.removeChild(this._renderer.domElement);
    }

    // Clear references
    this._selectableMeshes = [];
    this._meshToComponent.clear();
    this._selectedMeshes = [];
    this._originalMaterialsForSelection.clear();
  }

  _disposeMaterial(material) {
    if (!material) return;
    const mats = Array.isArray(material) ? material : [material];
    for (const mat of mats) {
      // Dispose all texture maps
      for (const key of Object.keys(mat)) {
        const val = mat[key];
        if (val && val.isTexture) {
          val.dispose();
        }
      }
      mat.dispose();
    }
  }
}
