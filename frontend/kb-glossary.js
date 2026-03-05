/**
 * LLCAR Diagnostica — Glossary Tooltips for KB v2
 *
 * Annotates HTML content with glossary term tooltips.
 * Provides multilingual term translations and KB/3D links.
 */

// Top 100 most common terms for Beginner mode
const TOP_TERMS_BEGINNER = new Set([
  'brake', 'engine', 'battery', 'motor', 'sensor', 'coolant', 'radiator',
  'tire', 'wheel', 'suspension', 'door', 'window', 'mirror', 'camera',
  'airbag', 'seat belt', 'steering wheel', 'headlight', 'taillight',
  'wiper', 'horn', 'fuse', 'relay', 'connector', 'pedal', 'speed',
  'voltage', 'accumulator', 'charging port', 'range extender',
  'smart key', 'turn signal', 'air conditioning', 'trunk', 'roof',
  'radar', 'lidar', 'windshield', 'oil', 'filter', 'exhaust',
  'transmission', 'clutch', 'gearbox', 'drive shaft', 'axle',
  'shock absorber', 'spring', 'bushing', 'bearing', 'gasket',
  'thermostat', 'water pump', 'alternator', 'starter', 'ignition',
  'fuel pump', 'injector', 'throttle', 'intake', 'manifold',
  'catalytic converter', 'muffler', 'turbocharger', 'intercooler',
  'compressor', 'condenser', 'evaporator', 'heater', 'fan',
  'inverter', 'converter', 'charger', 'bms', 'ecu', 'tcu',
  'abs', 'esp', 'adas', 'acc', 'lka', 'aeb', 'bsd',
  'hud', 'display', 'speaker', 'antenna', 'gps', 'bluetooth',
  'usb', 'lamp', 'bulb', 'led', 'halogen', 'xenon',
  'caliper', 'rotor', 'pad', 'disc', 'drum', 'fluid',
  'power steering', 'electric motor', 'generator', 'high voltage',
]);

export class GlossaryTooltips {
  /**
   * @param {object} glossaryData  i18n-glossary-data.json content
   * @param {object} i18n          i18n instance for translations
   */
  constructor(glossaryData, i18n) {
    this._data = glossaryData || {};
    this._i18n = i18n;
    this._index = [];     // sorted by term length (longest first)
    this._activeTooltip = null;
    this._buildTermIndex();
  }

  _buildTermIndex() {
    const entries = this._data.entries || this._data;
    if (!entries || typeof entries !== 'object') return;

    // Build from glossary data — entries keyed by glossary_id
    for (const [gid, entry] of Object.entries(entries)) {
      if (!entry) continue;
      const names = [];
      // Collect names in all languages
      if (entry.ru) names.push({ text: entry.ru, lang: 'ru' });
      if (entry.en) names.push({ text: entry.en, lang: 'en' });
      if (entry.zh) names.push({ text: entry.zh, lang: 'zh' });
      // Also from name field
      const name = entry.name || gid.split('@')[0].replace(/_/g, ' ');
      if (name && !names.find(n => n.text.toLowerCase() === name.toLowerCase())) {
        names.push({ text: name, lang: 'en' });
      }

      for (const n of names) {
        if (n.text.length < 2) continue;
        this._index.push({
          term: n.text,
          termLower: n.text.toLowerCase(),
          lang: n.lang,
          glossaryId: gid,
          entry,
        });
      }
    }

    // Sort longest first for greedy matching
    this._index.sort((a, b) => b.term.length - a.term.length);
  }

  /**
   * Get filtered term index based on persona.
   * @param {'beginner'|'expert'} persona
   * @returns {Array}
   */
  _getTermsForPersona(persona) {
    if (persona === 'expert') return this._index;
    // Beginner: only top terms
    return this._index.filter(t => {
      const key = t.termLower.replace(/[_\-]/g, ' ');
      return TOP_TERMS_BEGINNER.has(key);
    });
  }

  /**
   * Annotate HTML string with glossary tooltip spans.
   * Skips terms inside <code>, <a>, existing tooltips.
   * @param {string} html
   * @param {'beginner'|'expert'} persona
   * @returns {string}
   */
  annotateHTML(html, persona = 'expert') {
    if (!html || this._index.length === 0) return html;

    const terms = this._getTermsForPersona(persona);
    if (terms.length === 0) return html;

    // Split HTML into tags and text segments
    const segments = html.split(/(<[^>]+>)/);
    let insideSkip = 0; // nesting depth of skip tags

    const skipTags = ['code', 'a', 'pre', 'script', 'style'];
    const annotated = new Set(); // track already annotated positions

    const result = segments.map(segment => {
      // Check if this is a tag
      if (segment.startsWith('<')) {
        const tagMatch = segment.match(/^<\/?(\w+)/);
        if (tagMatch) {
          const tagName = tagMatch[1].toLowerCase();
          if (skipTags.includes(tagName) || tagName === 'span' && segment.includes('kbv2-glossary-term')) {
            if (segment.startsWith('</')) insideSkip = Math.max(0, insideSkip - 1);
            else if (!segment.endsWith('/>')) insideSkip++;
          }
        }
        return segment;
      }

      // Text segment — skip if inside excluded tag
      if (insideSkip > 0) return segment;

      // Try to annotate terms (first match only per segment to avoid overlap)
      let result = segment;
      let matchCount = 0;
      const maxMatches = 3; // max annotations per segment

      for (const t of terms) {
        if (matchCount >= maxMatches) break;
        const idx = result.toLowerCase().indexOf(t.termLower);
        if (idx === -1) continue;

        // Check word boundary
        const before = idx > 0 ? result[idx - 1] : ' ';
        const after = idx + t.term.length < result.length ? result[idx + t.term.length] : ' ';
        if (/\w/.test(before) || /\w/.test(after)) continue;

        const original = result.slice(idx, idx + t.term.length);
        const key = `${t.glossaryId}`;
        if (annotated.has(key)) continue;
        annotated.add(key);

        const replacement = `<span class="kbv2-glossary-term" data-glossary-id="${t.glossaryId}" data-term="${t.termLower}">${original}</span>`;
        result = result.slice(0, idx) + replacement + result.slice(idx + t.term.length);
        matchCount++;
      }

      return result;
    });

    return result.join('');
  }

  /**
   * Show tooltip for a glossary term element.
   * @param {HTMLElement} termElement
   */
  showTooltip(termElement) {
    this.hideTooltip();
    const gid = termElement.dataset.glossaryId;
    if (!gid) return;

    const entry = this._findEntry(gid);
    if (!entry) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'kbv2-glossary-tooltip';

    const layer = gid.split('@')[1] || '';

    // Build translations table
    const langs = ['ru', 'en', 'zh', 'ar', 'es'];
    const langLabels = { ru: 'RU', en: 'EN', zh: 'ZH', ar: 'AR', es: 'ES' };
    let transHTML = '';
    for (const lang of langs) {
      const val = entry[lang];
      if (val) {
        transHTML += `<div style="display:flex;gap:6px;align-items:baseline;">
          <span style="font-size:10px;color:var(--text-tertiary);min-width:20px;">${langLabels[lang]}</span>
          <span style="font-size:12px;color:var(--text-primary);">${val}</span>
        </div>`;
      }
    }

    tooltip.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:6px;">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);">${entry.ru || entry.en || gid.split('@')[0].replace(/_/g, ' ')}</div>
        ${layer ? `<span style="font-size:10px;color:var(--text-tertiary);">Layer: ${layer}</span>` : ''}
        <div style="display:flex;flex-direction:column;gap:2px;">${transHTML}</div>
        <div style="display:flex;gap:6px;margin-top:4px;">
          <button class="kbv2-glossary-action" data-action="search" data-gid="${gid}" style="font-size:11px;padding:3px 8px;border-radius:6px;background:var(--accent-primary-dim);color:var(--accent-primary);border:none;cursor:pointer;">Искать</button>
          <button class="kbv2-glossary-action" data-action="3d" data-gid="${gid}" style="font-size:11px;padding:3px 8px;border-radius:6px;background:var(--bg-surface);color:var(--text-secondary);border:1px solid var(--border-default);cursor:pointer;">3D</button>
        </div>
      </div>
    `;

    // Position tooltip near element
    const rect = termElement.getBoundingClientRect();
    tooltip.style.left = `${rect.left}px`;
    tooltip.style.top = `${rect.bottom + 4}px`;

    document.body.appendChild(tooltip);
    this._activeTooltip = tooltip;

    // Auto-hide on outside click
    setTimeout(() => {
      const handler = (e) => {
        if (!tooltip.contains(e.target) && e.target !== termElement) {
          this.hideTooltip();
          document.removeEventListener('click', handler);
        }
      };
      document.addEventListener('click', handler);
    }, 50);
  }

  hideTooltip() {
    if (this._activeTooltip) {
      this._activeTooltip.remove();
      this._activeTooltip = null;
    }
  }

  _findEntry(glossaryId) {
    const entries = this._data.entries || this._data;
    if (entries[glossaryId]) return entries[glossaryId];
    // Search in index
    const found = this._index.find(t => t.glossaryId === glossaryId);
    return found?.entry || null;
  }
}
