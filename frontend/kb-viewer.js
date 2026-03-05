/**
 * LLCAR Diagnostica — Knowledge Base Viewer Module
 *
 * Renders manual sections as markdown, links them to 3D components
 * via glossary tag matching.
 *
 * Usage:
 *   import { KBViewer } from './kb-viewer.js';
 *   const viewer = new KBViewer(containerEl);
 *   await viewer.loadSections('data/knowledge-base/manual-sections-l9-ru.json');
 *   viewer.setGlossary(glossaryData);  // from i18n-glossary-data.json
 *   viewer.showForComponent('brake_caliper@brakes');
 *   viewer.search('тормоз');
 */

import { on, off, emit } from './event-bus.js';

// ═══════════════════════════════════════════════════════
// Markdown Renderer (~200 lines, no external deps)
// ═══════════════════════════════════════════════════════

/**
 * Escape HTML special characters.
 * @param {string} s
 * @returns {string}
 */
function esc(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Render inline markdown: bold, italic, code, images, links.
 * @param {string} text
 * @returns {string} HTML
 */
function renderInline(text) {
  let out = esc(text);

  // Images: ![alt](src) — ensure absolute path for mineru-output images
  out = out.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
    const imgSrc = src.startsWith('/') || src.startsWith('http') ? src : '/' + src;
    return `<img src="${imgSrc}" alt="${alt}" class="kb-section__img" loading="lazy" onerror="this.alt='[img error: '+this.src+']';this.style.border='2px solid red'" />`;
  });

  // Links: [text](url)
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener">$1</a>');

  // Bold: **text** or __text__
  out = out.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/__(.+?)__/g, '<strong>$1</strong>');

  // Italic: *text* or _text_
  out = out.replace(/\*(.+?)\*/g, '<em>$1</em>');
  out = out.replace(/(?<!\w)_(.+?)_(?!\w)/g, '<em>$1</em>');

  // Inline code: `code`
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>');

  return out;
}

/**
 * Parse a pipe-delimited table block into HTML.
 * @param {string[]} lines — raw table lines (including header + separator)
 * @returns {string} HTML <table>
 */
function renderTable(lines) {
  if (lines.length < 2) return '';

  const parseRow = (line) =>
    line.replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim());

  const headers = parseRow(lines[0]);
  // Skip separator line (lines[1] is usually |---|---|)
  const dataStart = (lines[1] && /^[\s|:-]+$/.test(lines[1])) ? 2 : 1;
  const rows = lines.slice(dataStart).map(parseRow);

  let html = '<table class="kb-section__table"><thead><tr>';
  for (const h of headers) {
    html += `<th>${renderInline(h)}</th>`;
  }
  html += '</tr></thead><tbody>';
  for (const row of rows) {
    html += '<tr>';
    for (let i = 0; i < headers.length; i++) {
      html += `<td>${renderInline(row[i] || '')}</td>`;
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  return html;
}

/**
 * Render a markdown string to HTML.
 * Supports: H1-H3, bold, italic, tables, images, ordered/unordered lists,
 * code blocks, paragraphs. Headers get data-glossary-id attributes when matched.
 *
 * @param {string} md — markdown text
 * @param {Map<string,string>} [glossaryLookup] — lowercase name → glossary_id
 * @returns {string} HTML
 */
export function renderMarkdown(md, glossaryLookup) {
  if (!md) return '';

  // ── Pre-process: extract HTML tables and preserve them ──
  // Replace <table>...</table> blocks with placeholders, render them as-is
  const htmlTablePlaceholders = [];
  md = md.replace(/<table[\s>][\s\S]*?<\/table>/gi, (match) => {
    const idx = htmlTablePlaceholders.length;
    // Sanitize: add styling class, keep structure
    const styled = match
      .replace(/<table/g, '<table class="kb-section__table"')
      .replace(/<td/g, '<td style="padding:4px 8px;border:1px solid var(--border-default);font-size:12px;"')
      .replace(/<th/g, '<th style="padding:4px 8px;border:1px solid var(--border-default);font-size:12px;font-weight:600;background:var(--surface-tertiary);"');
    htmlTablePlaceholders.push(styled);
    return `\n__HTML_TABLE_${idx}__\n`;
  });

  const lines = md.split('\n');
  const parts = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trimEnd();

    // ── HTML table placeholder ──
    const tablePlaceholder = trimmed.match(/^__HTML_TABLE_(\d+)__$/);
    if (tablePlaceholder) {
      parts.push(htmlTablePlaceholders[parseInt(tablePlaceholder[1])]);
      i++;
      continue;
    }

    // ── Code block (```) ──
    if (trimmed.startsWith('```')) {
      const lang = trimmed.slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trimEnd().startsWith('```')) {
        codeLines.push(esc(lines[i]));
        i++;
      }
      i++; // skip closing ```
      parts.push(`<pre class="kb-section__code"><code${lang ? ` class="lang-${lang}"` : ''}>${codeLines.join('\n')}</code></pre>`);
      continue;
    }

    // ── Headers (# ## ###) ──
    const hMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (hMatch) {
      const level = hMatch[1].length;
      const text = hMatch[2].trim();
      const id = text.toLowerCase().replace(/[^a-zа-яё0-9\u4e00-\u9fff]+/g, '-').replace(/^-|-$/g, '');
      let glossaryAttr = '';
      if (glossaryLookup) {
        const gid = glossaryLookup.get(text.toLowerCase());
        if (gid) glossaryAttr = ` data-glossary-id="${esc(gid)}"`;
      }
      parts.push(`<h${level} id="${id}" class="kb-section__h${level}"${glossaryAttr}>${renderInline(text)}</h${level}>`);
      i++;
      continue;
    }

    // ── Table (pipe-delimited) ──
    if (trimmed.includes('|') && trimmed.startsWith('|')) {
      const tableLines = [];
      while (i < lines.length && lines[i].trimEnd().includes('|')) {
        tableLines.push(lines[i].trimEnd());
        i++;
      }
      parts.push(renderTable(tableLines));
      continue;
    }

    // ── Unordered list (- or * or ●) ──
    if (/^\s*[-*●]\s+/.test(trimmed)) {
      const items = [];
      while (i < lines.length && /^\s*[-*●]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*●]\s+/, '').trim());
        i++;
      }
      parts.push('<ul>' + items.map(it => `<li>${renderInline(it)}</li>`).join('') + '</ul>');
      continue;
    }

    // ── Ordered list (1. 2. etc) ──
    if (/^\s*\d+[.)]\s+/.test(trimmed)) {
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+[.)]\s+/, '').trim());
        i++;
      }
      parts.push('<ol>' + items.map(it => `<li>${renderInline(it)}</li>`).join('') + '</ol>');
      continue;
    }

    // ── Empty line ──
    if (trimmed === '') {
      i++;
      continue;
    }

    // ── Paragraph (accumulate consecutive non-empty lines) ──
    const paraLines = [];
    while (i < lines.length && lines[i].trim() !== '' &&
           !lines[i].trimEnd().startsWith('#') &&
           !lines[i].trimEnd().startsWith('```') &&
           !/^\s*[-*●]\s+/.test(lines[i]) &&
           !/^\s*\d+[.)]\s+/.test(lines[i]) &&
           !(lines[i].trimEnd().startsWith('|') && lines[i].includes('|'))) {
      paraLines.push(lines[i].trim());
      i++;
    }
    if (paraLines.length > 0) {
      parts.push(`<p>${renderInline(paraLines.join(' '))}</p>`);
    }
  }

  return parts.join('\n');
}

// ═══════════════════════════════════════════════════════
// KBViewer Class
// ═══════════════════════════════════════════════════════

export class KBViewer {
  /**
   * @param {HTMLElement} containerElement — DOM element to render into
   */
  constructor(containerElement) {
    /** @type {HTMLElement} */
    this._container = containerElement;

    /** @type {Array} All loaded sections */
    this._sections = [];

    /** @type {Map<string, object[]>} glossaryId → sections */
    this._tagToSections = new Map();

    /** @type {Map<string, string[]>} sectionId → glossaryIds */
    this._sectionToTags = new Map();

    /** @type {Map<string, object[]>} layerId → sections */
    this._layerToSections = new Map();

    /** @type {Map<string, string>} lowercase component name → glossary_id (all langs) */
    this._glossaryLookup = new Map();

    /** @type {object|null} Raw glossary data { components: { gid: { en, ru, zh, ... } } } */
    this._glossaryData = null;

    /** @type {string} Current document vehicle */
    this._vehicle = '';

    /** @type {string} Current document language */
    this._language = '';

    // Bound event handlers
    this._onComponentSelect = this._handleComponentSelect.bind(this);
    this._onLangChange = this._handleLangChange.bind(this);

    // Subscribe to events
    on('component:select', this._onComponentSelect);
    on('lang:change', this._onLangChange);
  }

  /**
   * Set glossary data for tag matching.
   * Call this before loadSections() for best results.
   * @param {object} glossaryData — parsed i18n-glossary-data.json
   */
  setGlossary(glossaryData) {
    this._glossaryData = glossaryData;
    this._glossaryLookup.clear();

    const components = glossaryData?.components || {};
    for (const [gid, names] of Object.entries(components)) {
      for (const lang of ['en', 'ru', 'zh', 'ar', 'es']) {
        const name = names[lang];
        if (name && name.length >= 3) {
          this._glossaryLookup.set(name.toLowerCase(), gid);
          // Also store first variant (before /)
          const slash = name.indexOf('/');
          if (slash > 2) {
            this._glossaryLookup.set(name.substring(0, slash).trim().toLowerCase(), gid);
          }
        }
      }
    }
  }

  /**
   * Load manual sections from a JSON file.
   * Indexes sections by component tags and layers.
   * @param {string} sectionsPath — URL to manual-sections-*.json
   */
  async loadSections(sectionsPath) {
    try {
      const resp = await fetch(sectionsPath);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      this._vehicle = data.vehicle || '';
      this._language = data.language || '';
      this._sections = data.sections || [];

      this._buildTagIndex();
    } catch (e) {
      console.warn('[KBViewer] Failed to load sections:', e.message);
    }
  }

  /**
   * Display all sections related to a glossary component.
   * @param {string} glossaryId — e.g. 'brake_caliper@brakes'
   */
  showForComponent(glossaryId) {
    const sections = this._tagToSections.get(glossaryId) || [];

    if (sections.length === 0) {
      this._renderEmpty(glossaryId);
      return;
    }

    const componentName = this._getComponentDisplayName(glossaryId);
    let html = `<div class="kb-results">`;
    html += `<div class="kb-results__header">
      <span class="kb-results__title">${esc(componentName)}</span>
      <span class="kb-results__count">${sections.length} section${sections.length !== 1 ? 's' : ''}</span>
    </div>`;

    for (const section of sections) {
      html += this._renderSectionCard(section);
    }

    html += '</div>';
    this._container.innerHTML = html;
  }

  /**
   * Display overview of all sections for a layer.
   * @param {string} layerId — e.g. 'engine', 'brakes'
   */
  showForLayer(layerId) {
    const sections = this._layerToSections.get(layerId) || [];

    if (sections.length === 0) {
      this._renderEmpty(layerId);
      return;
    }

    const layerLabel = this._getLayerLabel(layerId);
    let html = `<div class="kb-results">`;
    html += `<div class="kb-results__header">
      <span class="kb-results__title">${esc(layerLabel)}</span>
      <span class="kb-results__count">${sections.length} section${sections.length !== 1 ? 's' : ''}</span>
    </div>`;

    for (const section of sections.slice(0, 30)) {
      html += this._renderSectionCard(section);
    }

    if (sections.length > 30) {
      html += `<div class="kb-section kb-section--more">+${sections.length - 30} more sections</div>`;
    }

    html += '</div>';
    this._container.innerHTML = html;
  }

  /**
   * Full-text search across all sections.
   * Returns matching sections with highlighted snippets.
   * @param {string} query
   * @returns {Array<{section: object, matches: number, snippet: string}>}
   */
  search(query) {
    if (!query || query.length < 2) {
      this.clear();
      return [];
    }

    const q = query.toLowerCase().trim();
    const tokens = q.split(/\s+/).filter(t => t.length >= 2);
    const results = [];

    for (const section of this._sections) {
      const title = (section.title || '').toLowerCase();
      const content = (section.content || '').toLowerCase();

      let matches = 0;
      for (const token of tokens) {
        if (title.includes(token)) matches += 3;
        // Count occurrences in content
        let idx = -1;
        while ((idx = content.indexOf(token, idx + 1)) !== -1) {
          matches++;
        }
      }

      if (matches > 0) {
        // Build a snippet around the first match
        const snippet = this._buildSnippet(section.content || '', tokens[0], 150);
        results.push({ section, matches, snippet });
      }
    }

    results.sort((a, b) => b.matches - a.matches);

    // Render results
    this._renderSearchResults(query, results.slice(0, 30));

    return results;
  }

  /**
   * Render a markdown string to HTML.
   * Exposed publicly for external use.
   * @param {string} mdString
   * @returns {string} HTML
   */
  renderMarkdown(mdString) {
    return renderMarkdown(mdString, this._glossaryLookup);
  }

  /**
   * Clear the viewer container.
   */
  clear() {
    this._container.innerHTML = '';
  }

  /**
   * Dispose: unsubscribe from events, clear state.
   */
  dispose() {
    off('component:select', this._onComponentSelect);
    off('lang:change', this._onLangChange);
    this._sections = [];
    this._tagToSections.clear();
    this._sectionToTags.clear();
    this._layerToSections.clear();
    this.clear();
  }

  // ═══════════════════════════════════════════════════════
  // Tag Index Builder
  // ═══════════════════════════════════════════════════════

  /**
   * Build bidirectional index: glossaryId <-> sections.
   * Parses section titles and content to find component name matches.
   */
  _buildTagIndex() {
    this._tagToSections.clear();
    this._sectionToTags.clear();
    this._layerToSections.clear();

    for (const section of this._sections) {
      const foundTags = new Set();

      // Search for glossary component names in title + first 1000 chars of content
      const searchText = ((section.title || '') + ' ' + (section.content || '').substring(0, 1000)).toLowerCase();

      for (const [name, gid] of this._glossaryLookup) {
        if (name.length < 3) continue;
        if (searchText.includes(name)) {
          foundTags.add(gid);
        }
      }

      // Convert Set to Array and store
      const tagsArray = [...foundTags];
      this._sectionToTags.set(section.sectionId, tagsArray);

      // Bidirectional: glossaryId → sections
      for (const gid of tagsArray) {
        if (!this._tagToSections.has(gid)) {
          this._tagToSections.set(gid, []);
        }
        this._tagToSections.get(gid).push(section);
      }

      // Layer index: extract layer from tags
      const layers = new Set();
      for (const gid of tagsArray) {
        const atIdx = gid.lastIndexOf('@');
        if (atIdx > 0) {
          layers.add(gid.substring(atIdx + 1));
        }
      }
      // Also classify by keyword if no tags found
      if (layers.size === 0) {
        const layer = this._classifyByKeyword(searchText);
        if (layer) layers.add(layer);
      }

      for (const layer of layers) {
        if (!this._layerToSections.has(layer)) {
          this._layerToSections.set(layer, []);
        }
        this._layerToSections.get(layer).push(section);
      }
    }
  }

  // ═══════════════════════════════════════════════════════
  // Rendering Helpers
  // ═══════════════════════════════════════════════════════

  /**
   * Render a single section as a card.
   */
  _renderSectionCard(section) {
    const tags = this._sectionToTags.get(section.sectionId) || [];
    const pageInfo = section.pageStart ? `p.${section.pageStart}${section.pageEnd && section.pageEnd !== section.pageStart ? '-' + section.pageEnd : ''}` : '';

    // Render content as markdown
    const contentHtml = renderMarkdown(section.content || '', this._glossaryLookup);

    // Build tag badges
    let tagBadges = '';
    if (tags.length > 0) {
      tagBadges = '<div class="kb-section__tags">';
      for (const gid of tags.slice(0, 8)) {
        const name = this._getComponentDisplayName(gid);
        const layer = gid.split('@').pop();
        tagBadges += `<span class="kb-section__tag" data-glossary-id="${esc(gid)}" data-layer="${esc(layer)}">${esc(name)}</span>`;
      }
      if (tags.length > 8) {
        tagBadges += `<span class="kb-section__tag kb-section__tag--more">+${tags.length - 8}</span>`;
      }
      tagBadges += '</div>';
    }

    return `
      <div class="kb-section" data-section-id="${esc(section.sectionId)}">
        <div class="kb-section__header">
          <h3 class="kb-section__title">${esc(section.title || 'Untitled')}</h3>
          <span class="kb-section__meta">${esc(pageInfo)}</span>
        </div>
        ${tagBadges}
        <div class="kb-section__content">${contentHtml}</div>
      </div>
    `;
  }

  /**
   * Render search results with highlighted snippets.
   */
  _renderSearchResults(query, results) {
    if (results.length === 0) {
      this._container.innerHTML = `
        <div class="kb-empty">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5" stroke-linecap="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          <span>No results for "${esc(query)}"</span>
        </div>
      `;
      return;
    }

    const tokens = query.toLowerCase().split(/\s+/).filter(t => t.length >= 2);

    let html = `<div class="kb-results">`;
    html += `<div class="kb-results__header">
      <span class="kb-results__title">Search: "${esc(query)}"</span>
      <span class="kb-results__count">${results.length} result${results.length !== 1 ? 's' : ''}</span>
    </div>`;

    for (const { section, matches, snippet } of results) {
      const highlightedSnippet = this._highlightTokens(snippet, tokens);
      const highlightedTitle = this._highlightTokens(esc(section.title || ''), tokens);
      const pageInfo = section.pageStart ? `p.${section.pageStart}` : '';

      html += `
        <div class="kb-section kb-section--search-result" data-section-id="${esc(section.sectionId)}">
          <div class="kb-section__header">
            <h3 class="kb-section__title">${highlightedTitle}</h3>
            <span class="kb-section__meta">${matches} matches &middot; ${esc(pageInfo)}</span>
          </div>
          <div class="kb-section__snippet">${highlightedSnippet}</div>
        </div>
      `;
    }

    html += '</div>';
    this._container.innerHTML = html;

    // Bind click to expand full section
    this._container.querySelectorAll('.kb-section--search-result').forEach(el => {
      el.addEventListener('click', () => {
        const sectionId = el.dataset.sectionId;
        const section = this._sections.find(s => s.sectionId === sectionId);
        if (section) {
          this._expandSection(section);
        }
      });
    });
  }

  /**
   * Render a single expanded section.
   */
  _expandSection(section) {
    let html = `<div class="kb-results">`;
    html += `<button class="kb-results__back" id="kb-viewer-back">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
      Back to results
    </button>`;
    html += this._renderSectionCard(section);
    html += '</div>';
    this._container.innerHTML = html;

    // Bind tag badge clicks
    this._container.querySelectorAll('.kb-section__tag[data-glossary-id]').forEach(badge => {
      badge.addEventListener('click', (e) => {
        e.stopPropagation();
        const gid = badge.dataset.glossaryId;
        emit('kb:tag:click', { glossaryId: gid });
      });
    });
  }

  /**
   * Render empty state.
   */
  _renderEmpty(label) {
    this._container.innerHTML = `
      <div class="kb-empty">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5" stroke-linecap="round">
          <path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>
        </svg>
        <span>No articles found for "${esc(label || 'this component')}"</span>
      </div>
    `;
  }

  // ═══════════════════════════════════════════════════════
  // Text Utilities
  // ═══════════════════════════════════════════════════════

  /**
   * Build a snippet around the first occurrence of a token.
   */
  _buildSnippet(content, token, maxLen) {
    const lc = content.toLowerCase();
    const idx = lc.indexOf(token.toLowerCase());
    if (idx === -1) return content.substring(0, maxLen) + (content.length > maxLen ? '...' : '');

    const start = Math.max(0, idx - 60);
    const end = Math.min(content.length, idx + token.length + maxLen - 60);
    let snippet = content.substring(start, end).replace(/\n/g, ' ').replace(/\s+/g, ' ');
    if (start > 0) snippet = '...' + snippet;
    if (end < content.length) snippet += '...';
    return snippet;
  }

  /**
   * Highlight search tokens in text with <mark>.
   */
  _highlightTokens(text, tokens) {
    let result = text;
    for (const token of tokens) {
      const regex = new RegExp(`(${token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      result = result.replace(regex, '<mark>$1</mark>');
    }
    return result;
  }

  /**
   * Get display name for a glossary_id.
   */
  _getComponentDisplayName(glossaryId) {
    if (this._glossaryData?.components?.[glossaryId]) {
      const names = this._glossaryData.components[glossaryId];
      return names[this._language] || names.en || names.ru || glossaryId;
    }
    // Fallback: format glossary_id as readable
    const atIdx = glossaryId.lastIndexOf('@');
    const name = atIdx > 0 ? glossaryId.substring(0, atIdx) : glossaryId;
    return name.replace(/_/g, ' ');
  }

  /**
   * Get display name for a layer.
   */
  _getLayerLabel(layerId) {
    if (this._glossaryData?.layers?.[layerId]) {
      const labels = this._glossaryData.layers[layerId];
      return labels[this._language] || labels.en || labels.ru || layerId;
    }
    return layerId;
  }

  /**
   * Simple keyword-based layer classification for sections without tags.
   */
  _classifyByKeyword(text) {
    const rules = [
      ['engine', /двигатель|мотор|топлив|выхлоп|глушитель|engine|fuel|exhaust/i],
      ['drivetrain', /трансмисс|подвеск|привод|колес|шин|suspension|wheel|tire/i],
      ['ev', /аккумулятор|батаре|зарядк|электрич|battery|charging|inverter/i],
      ['brakes', /тормоз|руле|brake|steering|abs|esp/i],
      ['sensors', /камер|радар|лидар|датчик|sensor|airbag|lidar/i],
      ['hvac', /кондиционер|климат|отоплен|вентиляц|hvac|temperature/i],
      ['interior', /сиден|двер|багажник|экран|seat|door|trunk|dashboard/i],
      ['body', /кузов|бампер|крыл|крыш|капот|body|bumper|roof|hood/i],
    ];
    for (const [layer, regex] of rules) {
      if (regex.test(text)) return layer;
    }
    return null;
  }

  // ═══════════════════════════════════════════════════════
  // Event Handlers
  // ═══════════════════════════════════════════════════════

  _handleComponentSelect(e) {
    const detail = e.detail || e;
    if (detail.glossaryId) {
      this.showForComponent(detail.glossaryId);
    }
  }

  _handleLangChange(e) {
    const detail = e.detail || e;
    if (detail.lang) {
      this._language = detail.lang;
    }
  }
}
