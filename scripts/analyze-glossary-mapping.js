/**
 * Analyze glossary-to-mesh mapping quality.
 * Shows which glossary_ids map to which meshes and translations.
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');
const i18n = JSON.parse(fs.readFileSync(path.join(base, 'architecture/i18n-glossary-data.json'), 'utf8'));
const li7 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li7-component-map-v2.json'), 'utf8'));
const glossary = JSON.parse(fs.readFileSync(path.join(base, 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'));

// 1. Current state: glossary_id -> meshes
const idToMeshes = {};
for (const [meshName, comp] of Object.entries(li7.components)) {
  const gid = comp.glossary_id;
  if (!idToMeshes[gid]) idToMeshes[gid] = [];
  idToMeshes[gid].push(meshName);
}

console.log('=== CURRENT MAPPING STATE ===');
console.log('Li7 meshes total:', Object.keys(li7.components).length);
console.log('Unique glossary_ids:', Object.keys(idToMeshes).length);
console.log('i18n entries total:', Object.keys(i18n.components).length);
console.log();

// 2. Show mapping quality for all unique IDs
console.log('=== GLOSSARY_ID -> TRANSLATIONS -> MESHES ===');
const entries = Object.entries(idToMeshes);
for (const [gid, meshes] of entries) {
  const trans = i18n.components[gid];
  const ruTrans = trans ? trans.ru : 'MISSING';
  const enTrans = trans ? trans.en : 'MISSING';

  // Find matching glossary term
  const baseRu = (ruTrans || '').toLowerCase();
  let glossaryMatch = null;
  for (const [catId, cat] of Object.entries(glossary.categories)) {
    for (const term of cat.terms) {
      if (term.ru.toLowerCase() === baseRu) {
        glossaryMatch = { catId, term };
        break;
      }
    }
    if (glossaryMatch) break;
  }

  console.log(`${gid}`);
  console.log(`  RU: ${ruTrans} | EN: ${enTrans}`);
  console.log(`  Glossary match: ${glossaryMatch ? 'YES (' + glossaryMatch.catId + ')' : 'NO'}`);
  console.log(`  Meshes (${meshes.length}): ${meshes.length > 4 ? meshes.slice(0,4).join(', ') + '... +' + (meshes.length-4) + ' more' : meshes.join(', ')}`);
  console.log();
}

// 3. Find glossary terms that have NO corresponding meshes
console.log('=== GLOSSARY TERMS WITHOUT MESH MAPPING ===');
const usedRuTerms = new Set();
for (const gid of Object.keys(idToMeshes)) {
  const trans = i18n.components[gid];
  if (trans && trans.ru) usedRuTerms.add(trans.ru.toLowerCase());
}

let unmappedCount = 0;
const unmappedByCat = {};
for (const [catId, cat] of Object.entries(glossary.categories)) {
  const unmapped = [];
  for (const term of cat.terms) {
    const ru = term.ru.toLowerCase();
    // Check if any used term contains this glossary term or vice versa
    let found = false;
    for (const used of usedRuTerms) {
      if (used.includes(ru) || ru.includes(used)) {
        found = true;
        break;
      }
    }
    if (!found) unmapped.push(term.ru);
  }
  unmappedByCat[catId] = unmapped;
  unmappedCount += unmapped.length;
}

console.log(`Total glossary terms: ${glossary.meta.total_terms}`);
console.log(`Terms without any mesh: ${unmappedCount}`);
console.log();

for (const [catId, terms] of Object.entries(unmappedByCat)) {
  if (terms.length > 0) {
    console.log(`${catId} (${terms.length} unmapped):`);
    terms.slice(0, 10).forEach(t => console.log(`  - ${t}`));
    if (terms.length > 10) console.log(`  ... +${terms.length - 10} more`);
    console.log();
  }
}

// 4. Analyze mesh names that could potentially be linked to glossary terms
console.log('=== MESH NAMES -> POTENTIAL GLOSSARY MATCHES ===');
// Extract the "base" component name from mesh names
// Pattern: "ComponentName#2" or "ComponentName#2 — SubPart"
const meshBaseNames = new Set();
for (const meshName of Object.keys(li7.components)) {
  // Strip "#2" suffix and "— SubPart"
  let baseName = meshName.replace(/#\d+$/, '').replace(/#\d+\s*—.*$/, '').trim();
  // Strip position codes (ПЛ, ПП, ЗЛ, ЗП, правый, левый, передний, задний, П, Л)
  baseName = baseName
    .replace(/\s+(ПЛ|ПП|ЗЛ|ЗП|правая|правый|правое|левая|левый|левое|передняя|передний|переднее|задняя|задний|заднее|П|Л)$/i, '')
    .trim();
  meshBaseNames.add(baseName.toLowerCase());
}

console.log(`Unique base mesh names: ${meshBaseNames.size}`);

// For each base mesh name, find potential glossary matches
const potentialMatches = [];
for (const baseName of meshBaseNames) {
  const matches = [];
  for (const [catId, cat] of Object.entries(glossary.categories)) {
    for (const term of cat.terms) {
      const termRu = term.ru.toLowerCase();
      if (termRu === baseName || termRu.includes(baseName) || baseName.includes(termRu)) {
        matches.push({ catId, ru: term.ru, en: term.en });
      }
    }
  }
  if (matches.length > 0) {
    potentialMatches.push({ baseName, matches });
  }
}

console.log(`Base names with glossary matches: ${potentialMatches.length}`);
console.log(`Base names WITHOUT glossary matches: ${meshBaseNames.size - potentialMatches.length}`);
console.log();

// Show unmatched base names
const matchedBaseNames = new Set(potentialMatches.map(p => p.baseName));
const unmatchedBaseNames = [...meshBaseNames].filter(n => !matchedBaseNames.has(n));
console.log('Unmatched base mesh names:');
unmatchedBaseNames.forEach(n => console.log(`  - ${n}`));
