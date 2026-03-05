/**
 * LLCAR Diagnostica — Tag Binding System
 *
 * Central integration module connecting all subsystems through glossary tags:
 *   3D Viewer (ThreeViewer) <-> Knowledge Base <-> Diagnostics <-> PID Overlay
 *
 * Maintains a persistent "active component" state that survives screen transitions.
 * When user selects a component in one subsystem, all others react.
 *
 * Events listened:
 *   component:select   — from ThreeViewer (3D click)
 *   component:deselect  — from ThreeViewer (click empty)
 *   kb:article:select  — from Knowledge screen (article click)
 *   pid:sensor:select  — from PID overlay (sensor badge click)
 *
 * Events emitted:
 *   tag:activate       — a glossary_id is now active across the whole app
 *   tag:deactivate     — no component is active anymore
 *   tag:context        — full context object for the active component
 *
 * Usage:
 *   import { TagBinding } from './tag-binding.js';
 *   const binding = new TagBinding();
 *   binding.init({ tagRegistry, knowledgeBase, i18n });
 *   binding.activate('brake_caliper@brakes');
 *   binding.getContext(); // { glossaryId, component, kbArticles, layer, ... }
 */

import { on, off, emit } from './event-bus.js';

export class TagBinding {
  constructor() {
    /** @type {string|null} Currently active glossary_id */
    this._activeGlossaryId = null;
    /** @type {object|null} Cached context for the active tag */
    this._context = null;
    /** @type {object|null} TagRegistry reference */
    this._tagRegistry = null;
    /** @type {object|null} KnowledgeBase reference */
    this._knowledgeBase = null;
    /** @type {object|null} I18n reference */
    this._i18n = null;
    /** @type {boolean} */
    this._initialized = false;

    // Bound handlers
    this._onComponentSelect = this._handleComponentSelect.bind(this);
    this._onComponentDeselect = this._handleComponentDeselect.bind(this);
    this._onKbArticleSelect = this._handleKbArticleSelect.bind(this);
    this._onPidSensorSelect = this._handlePidSensorSelect.bind(this);
  }

  /**
   * Initialize the tag binding system.
   * @param {object} deps
   * @param {object} [deps.tagRegistry] TagRegistry instance
   * @param {object} [deps.knowledgeBase] KnowledgeBase instance
   * @param {object} [deps.i18n] I18n instance
   */
  init(deps = {}) {
    if (this._initialized) return;

    this._tagRegistry = deps.tagRegistry || null;
    this._knowledgeBase = deps.knowledgeBase || null;
    this._i18n = deps.i18n || null;

    // Subscribe to events from all subsystems
    on('component:select', this._onComponentSelect);
    on('component:deselect', this._onComponentDeselect);
    on('kb:article:select', this._onKbArticleSelect);
    on('pid:sensor:select', this._onPidSensorSelect);

    this._initialized = true;
  }

  /**
   * Set/update dependency references (e.g., after lazy loading).
   * @param {object} deps
   */
  setDeps(deps) {
    if (deps.tagRegistry) this._tagRegistry = deps.tagRegistry;
    if (deps.knowledgeBase) this._knowledgeBase = deps.knowledgeBase;
    if (deps.i18n) this._i18n = deps.i18n;
  }

  /**
   * Programmatically activate a component by glossary_id.
   * All subsystems will be notified.
   * @param {string} glossaryId
   * @param {object} [source] Source info { from: 'twin'|'kb'|'pid'|'api' }
   */
  activate(glossaryId, source = {}) {
    if (!glossaryId) return;
    if (glossaryId === this._activeGlossaryId) return;

    this._activeGlossaryId = glossaryId;
    this._context = this._buildContext(glossaryId);

    emit('tag:activate', {
      glossaryId,
      context: this._context,
      source: source.from || 'api',
    });

    emit('tag:context', this._context);
  }

  /**
   * Deactivate the current component.
   */
  deactivate() {
    if (!this._activeGlossaryId) return;
    const prevId = this._activeGlossaryId;
    this._activeGlossaryId = null;
    this._context = null;

    emit('tag:deactivate', { previousGlossaryId: prevId });
  }

  /**
   * Get the currently active glossary_id.
   * @returns {string|null}
   */
  getActiveGlossaryId() {
    return this._activeGlossaryId;
  }

  /**
   * Get the full context for the currently active component.
   * @returns {object|null}
   */
  getContext() {
    return this._context;
  }

  /**
   * Get context for any glossary_id (without activating it).
   * @param {string} glossaryId
   * @returns {object}
   */
  getContextFor(glossaryId) {
    return this._buildContext(glossaryId);
  }

  /**
   * Cleanup and unsubscribe.
   */
  dispose() {
    off('component:select', this._onComponentSelect);
    off('component:deselect', this._onComponentDeselect);
    off('kb:article:select', this._onKbArticleSelect);
    off('pid:sensor:select', this._onPidSensorSelect);

    this._activeGlossaryId = null;
    this._context = null;
    this._initialized = false;
  }

  // ═══════════════════════════════════════════════════════
  // Context Builder
  // ═══════════════════════════════════════════════════════

  /**
   * Build a unified context object for a glossary_id.
   * Aggregates data from TagRegistry, KnowledgeBase, I18n.
   */
  _buildContext(glossaryId) {
    if (!glossaryId) return null;

    const ctx = {
      glossaryId,
      layer: null,
      meshName: null,
      displayName: glossaryId,
      translatedName: null,
      component: null,
      kbArticles: [],
      relatedTags: [],
    };

    // Extract layer from glossary_id format: component@layer
    const atIdx = glossaryId.lastIndexOf('@');
    if (atIdx > 0) {
      ctx.layer = glossaryId.substring(atIdx + 1);
    }

    // TagRegistry data
    if (this._tagRegistry?.loaded) {
      const comp = this._tagRegistry.getComponent(glossaryId);
      if (comp) {
        ctx.component = comp;
        ctx.meshName = comp.meshName || null;
        ctx.displayName = comp.displayName || glossaryId;
        ctx.layer = comp.layer || ctx.layer;
      }
    }

    // I18n translated name
    if (this._i18n) {
      const translated = this._i18n.getComponentName(glossaryId);
      if (translated !== glossaryId) {
        ctx.translatedName = translated;
      }
    }

    // Knowledge Base articles
    if (this._knowledgeBase?._loaded) {
      ctx.kbArticles = this._knowledgeBase.getByTag(glossaryId);
    }

    return ctx;
  }

  // ═══════════════════════════════════════════════════════
  // Event Handlers
  // ═══════════════════════════════════════════════════════

  /** 3D viewer component click */
  _handleComponentSelect(e) {
    const detail = e.detail || e;
    if (detail.glossaryId) {
      this.activate(detail.glossaryId, { from: 'twin' });
    }
  }

  /** 3D viewer click on empty space */
  _handleComponentDeselect() {
    this.deactivate();
  }

  /** Knowledge base article click */
  _handleKbArticleSelect(e) {
    const detail = e.detail || e;
    // If the article has tags, activate the first one
    if (detail.tags && detail.tags.length > 0) {
      this.activate(detail.tags[0], { from: 'kb' });
    }
  }

  /** PID sensor badge click */
  _handlePidSensorSelect(e) {
    const detail = e.detail || e;
    if (detail.glossaryId) {
      this.activate(detail.glossaryId, { from: 'pid' });
    }
  }
}
