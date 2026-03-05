/**
 * Apply glossary-mesh mapping to component-maps and i18n-glossary-data.
 *
 * Updates:
 *   1. li7-component-map-v2.json - glossary_id for each component
 *   2. li9-component-map-v2.json - glossary_id for each component
 *   3. i18n-glossary-data.json   - adds new terms with translations
 *   4. automotive-glossary-3d-components.json - adds new terms
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');
const mapping = JSON.parse(fs.readFileSync(path.join(base, 'architecture/glossary-mesh-mapping.json'), 'utf8'));
const li7 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li7-component-map-v2.json'), 'utf8'));
const li9 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li9-component-map-v2.json'), 'utf8'));
const i18n = JSON.parse(fs.readFileSync(path.join(base, 'architecture/i18n-glossary-data.json'), 'utf8'));
const glossary = JSON.parse(fs.readFileSync(
  path.join(base, 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'
));

const catToLayer = {
  body_frame: 'body', engine_fuel_exhaust: 'engine',
  drivetrain_suspension: 'drivetrain', ev_electrical: 'ev',
  steering_brakes: 'brakes', sensors_adas: 'sensors',
  hvac_thermal: 'hvac', doors_trunk_interior: 'interior'
};

// ===== 1. Update Li7 component-map glossary_ids =====
let li7Changed = 0;
for (const [meshName, m] of Object.entries(mapping.li7.mapping)) {
  if (m.newGlossaryId && li7.components[meshName]) {
    const old = li7.components[meshName].glossary_id;
    if (old !== m.newGlossaryId) {
      li7.components[meshName].glossary_id = m.newGlossaryId;
      li7Changed++;
    }
  }
}
console.log(`Li7: ${li7Changed} glossary_ids updated`);

// ===== 2. Update Li9 component-map glossary_ids =====
let li9Changed = 0;
for (const [meshName, m] of Object.entries(mapping.li9.mapping)) {
  if (m.newGlossaryId && li9.components[meshName]) {
    const old = li9.components[meshName].glossary_id;
    if (old !== m.newGlossaryId) {
      li9.components[meshName].glossary_id = m.newGlossaryId;
      li9Changed++;
    }
  }
}
console.log(`Li9: ${li9Changed} glossary_ids updated`);

// ===== 3. Update i18n-glossary-data with new terms and fix existing =====
// First, collect all unique glossary_ids from both models
const allGlossaryIds = new Set();
for (const m of Object.values(mapping.li7.mapping)) {
  if (m.newGlossaryId) allGlossaryIds.add(m.newGlossaryId);
}
for (const m of Object.values(mapping.li9.mapping)) {
  if (m.newGlossaryId) allGlossaryIds.add(m.newGlossaryId);
}

let i18nAdded = 0, i18nUpdated = 0;
for (const gid of allGlossaryIds) {
  // Find the translation from the mapping
  let glossaryTerm = null;
  for (const m of Object.values(mapping.li7.mapping)) {
    if (m.newGlossaryId === gid && m.glossaryTerm) { glossaryTerm = m.glossaryTerm; break; }
  }
  if (glossaryTerm === null) {
    for (const m of Object.values(mapping.li9.mapping)) {
      if (m.newGlossaryId === gid && m.glossaryTerm) { glossaryTerm = m.glossaryTerm; break; }
    }
  }

  if (glossaryTerm === null) continue;

  if (i18n.components[gid]) {
    // Update existing: only replace if old was transliterated/generic
    const existing = i18n.components[gid];
    const oldEn = existing.en;
    // Check if the old entry had a proper translation or was a transliteration
    const isTransliteration = /^[A-Z][a-z]+ [A-Z]$|^[A-Z][a-z]+ R$|Podrulevoy|Tsentralnyy|Pribornaya/i.test(oldEn);
    if (isTransliteration) {
      i18n.components[gid] = {
        en: glossaryTerm.en,
        ru: glossaryTerm.ru,
        zh: glossaryTerm.zh,
        ar: glossaryTerm.ar,
        es: glossaryTerm.es
      };
      i18nUpdated++;
    }
  } else {
    // Add new entry
    i18n.components[gid] = {
      en: glossaryTerm.en,
      ru: glossaryTerm.ru,
      zh: glossaryTerm.zh,
      ar: glossaryTerm.ar,
      es: glossaryTerm.es
    };
    i18nAdded++;
  }
}

// Also remove OLD glossary_ids that are no longer referenced
const activeIds = new Set();
for (const comp of Object.values(li7.components)) activeIds.add(comp.glossary_id);
for (const comp of Object.values(li9.components)) activeIds.add(comp.glossary_id);

let i18nRemoved = 0;
for (const gid of Object.keys(i18n.components)) {
  // Don't remove glossary terms not from component maps (generic glossary entries stay)
  // Only remove entries that look like old component-specific transliterations
  if (gid.includes('@') && gid.match(/^[a-z_]+@[a-z]+$/) && activeIds.has(gid) === false) {
    // Check if it was a component-specific entry
    const entry = i18n.components[gid];
    const enVal = entry.en;
    // Keep generic glossary terms (proper English), remove transliterations
    if (/Podrulevoy|Tsentralnyy|Pribornaya|Aromatizator|Nadpis|Ekran|Dvernaya/i.test(enVal)) {
      delete i18n.components[gid];
      i18nRemoved++;
    }
  }
}

// Update total count
i18n.meta.total_components = Object.keys(i18n.components).length;
i18n.meta.generated = new Date().toISOString().split('T')[0];

console.log(`i18n: ${i18nAdded} added, ${i18nUpdated} updated, ${i18nRemoved} removed (total: ${Object.keys(i18n.components).length})`);

// ===== 4. Add new terms to automotive glossary =====
let glossaryAdded = 0;
for (const newTerm of mapping.newGlossaryTerms) {
  const catId = newTerm.catId;
  if (glossary.categories[catId]) {
    // Check if term already exists by en name
    const exists = glossary.categories[catId].terms.some(t =>
      t.en.toLowerCase() === newTerm.en.toLowerCase()
    );
    if (exists === false) {
      glossary.categories[catId].terms.push({
        en: newTerm.en, ru: newTerm.ru,
        zh: newTerm.zh, ar: newTerm.ar, es: newTerm.es
      });
      glossaryAdded++;
    }
  }
}
glossary.meta.total_terms = Object.values(glossary.categories).reduce((sum, cat) => sum + cat.terms.length, 0);
glossary.meta.last_updated = new Date().toISOString().split('T')[0];

console.log(`Glossary: ${glossaryAdded} terms added (total: ${glossary.meta.total_terms})`);

// ===== Write all files =====
fs.writeFileSync(path.join(base, 'architecture/li7-component-map-v2.json'), JSON.stringify(li7, null, 2), 'utf8');
fs.writeFileSync(path.join(base, 'architecture/li9-component-map-v2.json'), JSON.stringify(li9, null, 2), 'utf8');
fs.writeFileSync(path.join(base, 'architecture/i18n-glossary-data.json'), JSON.stringify(i18n, null, 2), 'utf8');
fs.writeFileSync(
  path.join(base, 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'),
  JSON.stringify(glossary, null, 2), 'utf8'
);

console.log('\nAll files updated successfully.');

// ===== Print summary of unique glossary_ids per model =====
const li7Ids = new Set(Object.values(li7.components).map(c => c.glossary_id));
const li9Ids = new Set(Object.values(li9.components).map(c => c.glossary_id));
const sharedIds = [...li7Ids].filter(id => li9Ids.has(id));
console.log(`\nLi7 unique glossary_ids: ${li7Ids.size}`);
console.log(`Li9 unique glossary_ids: ${li9Ids.size}`);
console.log(`Shared between models: ${sharedIds.length}`);
console.log(`Total unique: ${new Set([...li7Ids, ...li9Ids]).size}`);

// Show a few examples of the shared terms
console.log('\nShared glossary_ids (sample):');
sharedIds.slice(0, 15).forEach(gid => {
  const term = i18n.components[gid];
  console.log(`  ${gid}: EN=${term?.en}, RU=${term?.ru}`);
});
