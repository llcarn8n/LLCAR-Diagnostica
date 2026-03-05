/**
 * TagRegistry — Central component registry.
 * Loads a component-map JSON and provides indexed lookups
 * by glossaryId, meshName, and layer.
 */

export class TagRegistry {
  constructor() {
    /** @type {Map<string, object>} glossaryId -> component data */
    this._byGlossaryId = new Map();
    /** @type {Map<string, object>} meshName -> component data (indexed by both original and sanitized names) */
    this._byMeshName = new Map();
    /** @type {Map<string, object[]>} layerId -> array of components */
    this._byLayer = new Map();
    /** @type {Map<string, object>} glossaryId -> annotation data (компоненты без 3D-геометрии) */
    this._annotations = new Map();
    /** @type {Map<string, object[]>} layerId -> array of annotation entries */
    this._annotationsByLayer = new Map();
    /** @type {object|null} raw systems data from component map */
    this._systems = null;
    /** @type {object|null} system colors from component map */
    this._systemColors = null;
    /** @type {boolean} */
    this._loaded = false;
  }

  /**
   * Sanitize a name the same way Three.js PropertyBinding.sanitizeNodeName does.
   * Three.js replaces spaces with underscores and strips []:\/ chars.
   * We need to match against these sanitized names.
   * @param {string} name
   * @returns {string}
   */
  static sanitizeName(name) {
    // Повторяет Three.js PropertyBinding.sanitizeNodeName:
    // пробелы → _, удаляет \ [ ] . : /
    return name.replace(/\s/g, '_').replace(/[\[\].:\\/]/g, '');
  }

  /**
   * Load and index the component map JSON.
   * @param {string} componentMapPath - URL/path to the component-map-v2.json
   */
  async load(componentMapPath) {
    const resp = await fetch(componentMapPath);
    if (!resp.ok) {
      throw new Error(`TagRegistry: failed to load ${componentMapPath} (${resp.status})`);
    }
    const data = await resp.json();

    this._systems = data.systems || {};
    this._systemColors = data.systemColors || {};

    const components = data.components || {};

    for (const [meshName, comp] of Object.entries(components)) {
      const entry = { ...comp, meshName };

      // Index by glossary_id
      if (entry.glossary_id) {
        this._byGlossaryId.set(entry.glossary_id, entry);
      }

      // Index by meshName (original)
      this._byMeshName.set(meshName, entry);

      // Also index by sanitized name (Three.js replaces spaces with _ in node names)
      const sanitized = TagRegistry.sanitizeName(meshName);
      if (sanitized !== meshName) {
        this._byMeshName.set(sanitized, entry);
      }

      // Index by layer
      const layer = entry.layer || 'unknown';
      if (!this._byLayer.has(layer)) {
        this._byLayer.set(layer, []);
      }
      this._byLayer.get(layer).push(entry);
    }

    this._loaded = true;
  }

  /**
   * Загрузить конфиг аннотаций (компоненты без 3D-геометрии).
   * @param {string} annotationConfigPath — путь к annotation-config.json
   */
  async loadAnnotations(annotationConfigPath) {
    try {
      const resp = await fetch(annotationConfigPath);
      if (!resp.ok) {
        console.warn(`TagRegistry: не удалось загрузить аннотации ${annotationConfigPath} (${resp.status})`);
        return;
      }
      const data = await resp.json();
      const annotations = data.annotations || {};

      for (const [glossaryId, annData] of Object.entries(annotations)) {
        const entry = {
          glossary_id: glossaryId,
          displayName: glossaryId.split('@')[0].replace(/_/g, ' '),
          layer: annData.layer,
          isAnnotation: true,
          priority: annData.priority,
          category: annData.category,
          dtcCodes: annData.dtcCodes || [],
          position: annData.position,
          anchorMesh: annData.anchorMesh,
          selectable: true,
        };

        this._annotations.set(glossaryId, entry);

        // Также индексируем в общий _byGlossaryId для единого lookup
        if (!this._byGlossaryId.has(glossaryId)) {
          this._byGlossaryId.set(glossaryId, entry);
        }

        // Индексируем по слою
        const layer = annData.layer || 'unknown';
        if (!this._annotationsByLayer.has(layer)) {
          this._annotationsByLayer.set(layer, []);
        }
        this._annotationsByLayer.get(layer).push(entry);
      }
    } catch (err) {
      console.warn('TagRegistry: ошибка загрузки аннотаций:', err);
    }
  }

  /**
   * Get component data by glossary_id (включая аннотации).
   * @param {string} glossaryId
   * @returns {object|undefined}
   */
  getComponent(glossaryId) {
    return this._byGlossaryId.get(glossaryId);
  }

  /**
   * Get all components in a given layer (только меши, без аннотаций).
   * @param {string} layerId
   * @returns {object[]}
   */
  getByLayer(layerId) {
    return this._byLayer.get(layerId) || [];
  }

  /**
   * Get all components + annotations in a given layer.
   * @param {string} layerId
   * @returns {object[]}
   */
  getByLayerAll(layerId) {
    const meshComps = this._byLayer.get(layerId) || [];
    const annComps = this._annotationsByLayer.get(layerId) || [];
    return [...meshComps, ...annComps];
  }

  /**
   * Получить только аннотации слоя.
   * @param {string} layerId
   * @returns {object[]}
   */
  getAnnotationsByLayer(layerId) {
    return this._annotationsByLayer.get(layerId) || [];
  }

  /**
   * Проверить, является ли компонент аннотацией.
   * @param {string} glossaryId
   * @returns {boolean}
   */
  isAnnotation(glossaryId) {
    return this._annotations.has(glossaryId);
  }

  /**
   * Получить количество аннотаций для каждого слоя.
   * @returns {Object<string, number>}
   */
  getAnnotationCounts() {
    const counts = {};
    for (const [layerId, anns] of this._annotationsByLayer) {
      counts[layerId] = anns.length;
    }
    return counts;
  }

  /**
   * Reverse lookup: GLB mesh name -> component data.
   * Handles Three.js name deduplication suffixes (_1, _2, etc.)
   * @param {string} meshName
   * @returns {object|undefined}
   */
  getByMeshName(meshName) {
    const direct = this._byMeshName.get(meshName);
    if (direct) return direct;

    // Three.js createUniqueName добавляет _N для дубликатов.
    const stripped = meshName.replace(/_\d+$/, '');
    if (stripped !== meshName) {
      const found = this._byMeshName.get(stripped);
      if (found) return found;
    }

    // Blender-дубли с суффиксом #N (например "Руль_(альт)#2").
    // Убираем #N и пробуем снова.
    const strippedHash = meshName.replace(/#\d+$/, '');
    if (strippedHash !== meshName) {
      const found = this._byMeshName.get(strippedHash);
      if (found) return found;
      // Комбинация: #N + _N
      const doubleStripped = strippedHash.replace(/_\d+$/, '');
      if (doubleStripped !== strippedHash) {
        return this._byMeshName.get(doubleStripped);
      }
    }

    return undefined;
  }

  /**
   * Simple search across displayNames (включая аннотации).
   * @param {string} query
   * @param {string} [lang] - unused for now, searches displayName directly
   * @returns {object[]}
   */
  search(query, lang) {
    if (!query || query.length < 2) return [];
    const q = query.toLowerCase();
    const results = [];

    for (const comp of this._byGlossaryId.values()) {
      const name = (comp.displayName || '').toLowerCase();
      if (name.includes(q)) {
        results.push(comp);
      }
    }

    return results;
  }

  /**
   * Get all layer IDs with component counts (меши + аннотации).
   * @returns {object[]} Array of { layerId, count, meshCount, annotationCount }
   */
  getAllLayers() {
    // Собираем все уникальные слои из мешей и аннотаций
    const layerIds = new Set([
      ...this._byLayer.keys(),
      ...this._annotationsByLayer.keys(),
    ]);
    const layers = [];
    for (const layerId of layerIds) {
      const meshCount = (this._byLayer.get(layerId) || []).length;
      const annotationCount = (this._annotationsByLayer.get(layerId) || []).length;
      layers.push({
        layerId,
        count: meshCount + annotationCount,
        meshCount,
        annotationCount,
      });
    }
    return layers;
  }

  /**
   * Get system color info for a layer.
   * @param {string} layerId
   * @returns {object|undefined} { normal, warning, critical }
   */
  getSystemColors(layerId) {
    return this._systemColors[layerId];
  }

  /**
   * Get raw systems data.
   * @returns {object}
   */
  getSystems() {
    return this._systems;
  }

  /** @returns {boolean} */
  get loaded() {
    return this._loaded;
  }
}
