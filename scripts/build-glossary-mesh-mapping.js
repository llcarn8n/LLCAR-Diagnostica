/**
 * Build a comprehensive glossary ↔ mesh mapping.
 *
 * For each Li7/Li9 mesh component:
 *   1. Extract the base component name (strip #2, position codes, sub-parts)
 *   2. Match to the best glossary term via multi-level fuzzy matching
 *   3. Generate proper glossary_id referencing the actual glossary term
 *   4. Generate updated component-maps and i18n-glossary-data
 *
 * Output: Diagnostica/architecture/glossary-mesh-mapping.json
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');
const glossary = JSON.parse(fs.readFileSync(
  path.join(base, 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'
));
const li7 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li7-component-map-v2.json'), 'utf8'));
const li9 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li9-component-map-v2.json'), 'utf8'));
const i18n = JSON.parse(fs.readFileSync(path.join(base, 'architecture/i18n-glossary-data.json'), 'utf8'));

// ===== Category ID → Layer ID mapping =====
const catToLayer = {
  body_frame: 'body',
  engine_fuel_exhaust: 'engine',
  drivetrain_suspension: 'drivetrain',
  ev_electrical: 'ev',
  steering_brakes: 'brakes',
  sensors_adas: 'sensors',
  hvac_thermal: 'hvac',
  doors_trunk_interior: 'interior'
};

// ===== Build glossary index =====
// glossaryIndex[layerId] = [ { en, ru, zh, ar, es, catId, termIdx, id } ]
const glossaryIndex = {};
const glossaryById = {}; // id -> term with translations

for (const [catId, cat] of Object.entries(glossary.categories)) {
  const layerId = catToLayer[catId];
  if (!layerId) continue;
  if (!glossaryIndex[layerId]) glossaryIndex[layerId] = [];

  cat.terms.forEach((term, idx) => {
    // Generate a stable ID from English term
    const id = term.en
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '')
      .replace(/_+/g, '_');

    const entry = { ...term, catId, termIdx: idx, id, layerId };
    glossaryIndex[layerId].push(entry);
    glossaryById[`${id}@${layerId}`] = entry;
  });
}

// ===== Position code patterns =====
const positionCodes = {
  'ПЛ': { ru: 'передний левый', en: 'front left', abbr: 'FL' },
  'ПП': { ru: 'передний правый', en: 'front right', abbr: 'FR' },
  'ЗЛ': { ru: 'задний левый', en: 'rear left', abbr: 'RL' },
  'ЗП': { ru: 'задний правый', en: 'rear right', abbr: 'RR' },
  'П': { ru: 'правый', en: 'right', abbr: 'R' },
  'Л': { ru: 'левый', en: 'left', abbr: 'L' },
};

// ===== Manual mapping overrides =====
// For tricky cases where automatic matching fails
const manualMeshToGlossary = {
  // Base mesh name (lowercased, no #2, no position) -> glossary term en name
  'шина': 'tyre / tire',
  'тормоз': 'brake caliper',
  'полуось передняя': 'half shaft / axle shaft',
  'полуось задняя': 'half shaft / axle shaft',
  'подрулевой лепесток': 'paddle shifter',
  'рамка номера': 'licence-plate bracket',
  'козырёк': 'sun visor',
  'проводка э/мотора': 'high-voltage wiring harness',
  'проводка батареи': 'high-voltage wiring harness',
  'ароматизатор': 'air freshener / fragrance diffuser',
  'верхний рычаг': 'upper control arm',
  'нижний рычаг': 'lower control arm',
  'нижний рычаг пб': 'lower control arm',
  'нижний рычаг па': 'lower control arm',
  'крышка днища': 'underbody cover',
  'стабилизатор': 'anti-roll bar / sway bar',
  'накладка люка': 'sunroof',
  'руль (экран)': 'steering wheel',
  'руль (альт.)': 'steering wheel',
  'руль': 'steering wheel',
  'пружина задняя': 'coil spring',
  'экран приборов': 'instrument cluster / gauge cluster',
  'надпись': 'emblem / badge',
  'выхлоп i4 1.5 бензин': 'exhaust manifold',
  'крепление э/мотора': 'engine mount / motor mount',
  'дверная карта': 'door trim panel / door card',
  'лючок зарядки': 'charging port / charge socket',
  'лючок бака': 'fuel filler door',
  'подрулевой переключатель': 'column switch / combination switch',
  'сиденья задние': 'rear seat',
  'центральный экран': 'infotainment screen / multimedia display',
  'четвертные панели': 'quarter panel',
  'зеркало правое': 'wing mirror / side mirror',
  'зеркало левое': 'wing mirror / side mirror',
  'зеркало салонное': 'rear-view mirror (interior)',
  'индикаторы приборов': 'instrument cluster / gauge cluster',
  'индикаторы приборов 2': 'instrument cluster / gauge cluster',
  'приборная панель (экраны)': 'instrument cluster / gauge cluster',
  'приборная панель': 'dashboard / instrument panel / fascia',
  'бампер задний (часть)': 'rear bumper',
  'бампер задний': 'rear bumper',
  'бампер передний': 'front bumper',
  'кузов (интерьер)': 'interior trim',
  'кузов (интерьер) 2': 'interior trim',
  'кузов': 'body shell',
  'колесо': 'wheel',
  'стекло фары правой': 'headlight lens',
  'стекло фары левой': 'headlight lens',
  'стекло люка': 'sunroof',
  'стекло багажника': 'rear window',
  'фара правая': 'headlight / headlamp',
  'фара левая': 'headlight / headlamp',
  'крыло правое': 'fender / wing',
  'крыло левое': 'fender / wing',
  'стойка передняя': 'strut',
  'стойка передняя (шир.)': 'strut',
  'рулевая тяга': 'tie rod',
  'рулевая тяга з (шир.)': 'tie rod',
  'рулевая тяга п (шир.)': 'tie rod',
  'подрамник': 'subframe',
  'подрамник задний': 'subframe',
  'подрамник задний (шир.)': 'subframe',
  'амортизатор': 'shock absorber / damper',
  'амортизатор з (шир.)': 'shock absorber / damper',
  'пневмоподвеска': 'air suspension',
  'рулевой механизм': 'steering gear / steering box',
  'подушка сиденья правая': 'seat cushion / seat base',
  'подушка сиденья левая': 'seat cushion / seat base',
  'блок управления': 'electronic control unit (ECU)',
  'электромотор задний': 'electric motor (traction)',
  'электромотор передний': 'electric motor (traction)',
  'батарея вн': 'traction battery (HV)',
  'охлаждение батареи': 'battery thermal management system (BTMS)',
  'педаль газа': 'accelerator pedal',
  'педаль тормоза': 'brake pedal',
  'номерной знак задний': 'licence plate',
  'номерной знак передний': 'licence plate',
  'лобовое стекло': 'windscreen / windshield',
  'люк': 'sunroof',
  'боковое стекло правое': 'side window',
  'боковое стекло левое': 'side window',
  'днище': 'floor pan',
  'радиатор': 'radiator',
  'монитор': 'infotainment screen / multimedia display',
  'бардачок': 'glove box / glove compartment',
  'сиденье (доп.)': 'rear seat',
  'сиденье пп (часть)': 'front seat',
  'сиденье пп': 'front seat',
  'сиденье пл (часть)': 'front seat',
  'сиденье пл': 'front seat',
  'дверь задняя правая': 'door (rear)',
  'дверь задняя левая': 'door (rear)',
  'дверь передняя правая': 'door (front)',
  'дверь передняя левая': 'door (front)',
  'ручка двери': 'door handle (exterior)',
  'стекло двери': 'door glass',
  'ступица задняя': 'wheel hub / hub',
  'ступица передняя': 'wheel hub / hub',
  'впускной коллектор i4': 'intake manifold',
  'топливный бак': 'fuel tank',
  'выхлопная труба': 'exhaust pipe / tail pipe',
  'выхлопная система': 'exhaust system',
  'двигатель i4': 'engine (ICE)',
  'крыша': 'roof',
  'капот': 'bonnet / hood',
  'крышка багажника': 'trunk lid',
  'защита днища': 'underbody cover',
  'стабилизатор з (шир.)': 'anti-roll bar / sway bar',
  'стабилизатор задний': 'anti-roll bar / sway bar',
  'стабилизатор п (шир.)': 'anti-roll bar / sway bar',
  'стабилизатор передний': 'anti-roll bar / sway bar',
  'верхний рычаг з (шир.)': 'upper control arm',
  'верхний рычаг задний': 'upper control arm',
  'нижний рычаг з (шир.)': 'lower control arm',
  'нижний рычаг задний': 'lower control arm',
  'нижний рычаг пб (шир.)': 'lower control arm',
  'нижний рычаг пб': 'lower control arm',
  'нижний рычаг па (шир.)': 'lower control arm',
  'пружина задняя (шир.)': 'coil spring',
  'пружина задняя': 'coil spring',
};

// ===== Extract base component name from mesh name =====
function extractBaseName(meshName) {
  let name = meshName;
  // Remove sub-part after " — "
  const dashIdx = name.indexOf(' — ');
  if (dashIdx !== -1) name = name.substring(0, dashIdx);
  // Remove #2 suffix
  name = name.replace(/#\d+$/, '').trim();
  return name;
}

// ===== Find the best glossary term for a mesh base name =====
function findGlossaryMatch(baseName, layerId) {
  const lower = baseName.toLowerCase();

  // 1. Check manual overrides first
  if (manualMeshToGlossary[lower]) {
    const targetEn = manualMeshToGlossary[lower].toLowerCase();
    // Find glossary term matching this English name
    for (const [lid, terms] of Object.entries(glossaryIndex)) {
      for (const term of terms) {
        if (term.en.toLowerCase() === targetEn) {
          return { term, matchType: 'manual', score: 100 };
        }
      }
    }
    // Try partial match on English name
    for (const [lid, terms] of Object.entries(glossaryIndex)) {
      for (const term of terms) {
        const termEn = term.en.toLowerCase();
        if (targetEn.includes(termEn) || termEn.includes(targetEn)) {
          return { term, matchType: 'manual-partial', score: 95 };
        }
        // Match first variant (before " / ")
        const firstVariant = targetEn.split(' / ')[0].trim();
        const termFirst = termEn.split(' / ')[0].trim();
        if (firstVariant === termFirst) {
          return { term, matchType: 'manual-variant', score: 98 };
        }
      }
    }
  }

  // 2. Strip position codes for matching
  let stripped = lower;
  for (const code of Object.keys(positionCodes)) {
    const regex = new RegExp(`\\s+${code.toLowerCase()}$`);
    stripped = stripped.replace(regex, '').trim();
  }
  // Also strip long position words
  stripped = stripped
    .replace(/\s+(передний|передняя|переднее|задний|задняя|заднее|правый|правая|правое|левый|левая|левое)\s*(\(шир\.\))?$/i, '')
    .replace(/\s*\(шир\.\)$/, '')
    .trim();

  // Check manual overrides again with stripped name
  if (manualMeshToGlossary[stripped]) {
    const targetEn = manualMeshToGlossary[stripped].toLowerCase();
    for (const [lid, terms] of Object.entries(glossaryIndex)) {
      for (const term of terms) {
        const termEn = term.en.toLowerCase();
        if (termEn === targetEn) {
          return { term, matchType: 'manual-stripped', score: 99 };
        }
        const firstVariant = targetEn.split(' / ')[0].trim();
        const termFirst = termEn.split(' / ')[0].trim();
        if (firstVariant === termFirst) {
          return { term, matchType: 'manual-stripped-variant', score: 97 };
        }
      }
    }
  }

  // 3. Exact Russian match in preferred layer
  const layerTerms = glossaryIndex[layerId] || [];
  for (const term of layerTerms) {
    if (term.ru.toLowerCase() === lower || term.ru.toLowerCase() === stripped) {
      return { term, matchType: 'exact-layer', score: 90 };
    }
  }

  // 4. Exact Russian match in any layer
  for (const [lid, terms] of Object.entries(glossaryIndex)) {
    for (const term of terms) {
      if (term.ru.toLowerCase() === lower || term.ru.toLowerCase() === stripped) {
        return { term, matchType: 'exact-any', score: 85 };
      }
    }
  }

  // 5. Russian substring match (glossary term contained in mesh name)
  let bestSubstr = null;
  let bestSubstrLen = 0;
  for (const [lid, terms] of Object.entries(glossaryIndex)) {
    for (const term of terms) {
      const termRu = term.ru.toLowerCase();
      if (stripped.includes(termRu) && termRu.length > bestSubstrLen) {
        bestSubstr = term;
        bestSubstrLen = termRu.length;
      }
    }
  }
  if (bestSubstr && bestSubstrLen >= 3) {
    return { term: bestSubstr, matchType: 'substring', score: 70 };
  }

  // 6. Reverse substring (mesh name contained in glossary term)
  bestSubstr = null;
  bestSubstrLen = 0;
  for (const [lid, terms] of Object.entries(glossaryIndex)) {
    for (const term of terms) {
      const termRu = term.ru.toLowerCase();
      if (termRu.includes(stripped) && stripped.length >= 3 && stripped.length > bestSubstrLen) {
        bestSubstr = term;
        bestSubstrLen = stripped.length;
      }
    }
  }
  if (bestSubstr) {
    return { term: bestSubstr, matchType: 'reverse-substring', score: 60 };
  }

  return null;
}

// ===== Process all meshes in a component map =====
function processComponentMap(compMap) {
  const results = {};
  const stats = { total: 0, matched: 0, unmatched: 0, byMatchType: {} };

  for (const [meshName, comp] of Object.entries(compMap.components)) {
    stats.total++;
    const baseName = extractBaseName(meshName);
    const match = findGlossaryMatch(baseName, comp.layer);

    if (match) {
      stats.matched++;
      const mt = match.matchType;
      stats.byMatchType[mt] = (stats.byMatchType[mt] || 0) + 1;

      results[meshName] = {
        baseName,
        layer: comp.layer,
        oldGlossaryId: comp.glossary_id,
        newGlossaryId: `${match.term.id}@${comp.layer}`,
        glossaryTerm: {
          en: match.term.en,
          ru: match.term.ru,
          zh: match.term.zh,
          ar: match.term.ar,
          es: match.term.es
        },
        matchType: match.matchType,
        matchScore: match.score
      };
    } else {
      stats.unmatched++;
      results[meshName] = {
        baseName,
        layer: comp.layer,
        oldGlossaryId: comp.glossary_id,
        newGlossaryId: null,
        glossaryTerm: null,
        matchType: 'none',
        matchScore: 0
      };
    }
  }

  return { results, stats };
}

// ===== Run for Li7 =====
console.log('=== Processing Li7 ===');
const li7Results = processComponentMap(li7);
console.log('Stats:', JSON.stringify(li7Results.stats, null, 2));

// Show unmatched
const li7Unmatched = Object.entries(li7Results.results)
  .filter(([_, r]) => r.matchType === 'none');
console.log('\nUnmatched Li7 meshes:', li7Unmatched.length);
li7Unmatched.forEach(([meshName, r]) => {
  console.log(`  ${meshName} (base: "${r.baseName}", layer: ${r.layer})`);
});

// ===== Run for Li9 =====
console.log('\n=== Processing Li9 ===');
const li9Results = processComponentMap(li9);
console.log('Stats:', JSON.stringify(li9Results.stats, null, 2));

const li9Unmatched = Object.entries(li9Results.results)
  .filter(([_, r]) => r.matchType === 'none');
console.log('\nUnmatched Li9 meshes:', li9Unmatched.length);
li9Unmatched.forEach(([meshName, r]) => {
  console.log(`  ${meshName} (base: "${r.baseName}", layer: ${r.layer})`);
});

// ===== Show sample of matched results =====
console.log('\n=== Sample matched results (Li7, first 20) ===');
Object.entries(li7Results.results)
  .filter(([_, r]) => r.matchType !== 'none')
  .slice(0, 20)
  .forEach(([meshName, r]) => {
    console.log(`${meshName}`);
    console.log(`  old: ${r.oldGlossaryId} -> new: ${r.newGlossaryId}`);
    console.log(`  match: ${r.matchType} (${r.matchScore})`);
    console.log(`  EN: ${r.glossaryTerm.en} | RU: ${r.glossaryTerm.ru}`);
    console.log();
  });

// ===== Write full mapping output =====
const output = {
  meta: {
    generated: new Date().toISOString(),
    glossarySource: 'automotive-glossary-3d-components.json v3.1-3d',
    description: 'Mapping between automotive glossary terms and Li7/Li9 3D mesh components'
  },
  li7: {
    stats: li7Results.stats,
    mapping: li7Results.results
  },
  li9: {
    stats: li9Results.stats,
    mapping: li9Results.results
  }
};

fs.writeFileSync(
  path.join(base, 'architecture/glossary-mesh-mapping.json'),
  JSON.stringify(output, null, 2),
  'utf8'
);
console.log('\nMapping written to architecture/glossary-mesh-mapping.json');
