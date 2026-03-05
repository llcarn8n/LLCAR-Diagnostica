/**
 * Находит меши из GLB, которые НЕ привязаны к component-map.
 * Извлекает JSON-чанк из GLB и сравнивает имена узлов с component-map.
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');

// --- Парсинг GLB: извлечение JSON-чанка ---
function extractGlbJson(glbPath) {
  const buf = fs.readFileSync(glbPath);
  // GLB заголовок: magic(4) + version(4) + length(4) = 12 байт
  const magic = buf.readUInt32LE(0);
  if (magic !== 0x46546C67) throw new Error('Не GLB файл');

  // Первый чанк — JSON: chunkLength(4) + chunkType(4) + data
  const chunkLen = buf.readUInt32LE(12);
  const chunkType = buf.readUInt32LE(16);
  if (chunkType !== 0x4E4F534A) throw new Error('Первый чанк не JSON');

  const jsonStr = buf.toString('utf8', 20, 20 + chunkLen);
  return JSON.parse(jsonStr);
}

// --- Получить все имена узлов из glTF JSON ---
function getNodeNames(gltf) {
  const names = [];
  if (gltf.nodes) {
    for (const node of gltf.nodes) {
      if (node.name) names.push(node.name);
    }
  }
  return names;
}

// --- Получить меш-узлы (у которых есть mesh property) ---
function getMeshNodeNames(gltf) {
  const result = [];
  if (!gltf.nodes) return result;
  for (const node of gltf.nodes) {
    if (node.mesh !== undefined && node.name) {
      result.push(node.name);
    }
  }
  return result;
}

// --- Three.js sanitizeName (повторяет логику из Three.js) ---
function sanitizeName(name) {
  return name.replace(/\s/g, '_').replace(/[^\w.-]/g, '');
}

// --- Анализ одной модели ---
function analyzeModel(modelName, glbPath, componentMapPath) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`  ${modelName}`);
  console.log(`${'='.repeat(60)}`);

  const gltf = extractGlbJson(glbPath);
  const compMap = JSON.parse(fs.readFileSync(componentMapPath, 'utf8'));
  const components = compMap.components;

  // Все имена компонентов в component-map
  const mapNames = new Set(Object.keys(components));

  // Все узлы с мешами из GLB
  const meshNodes = getMeshNodeNames(gltf);
  const allNodes = getNodeNames(gltf);

  // Узлы у которых есть дочерние меш-узлы (группы для multi-prim)
  const parentGroups = new Set();
  if (gltf.nodes) {
    for (const node of gltf.nodes) {
      if (node.children) {
        for (const childIdx of node.children) {
          const child = gltf.nodes[childIdx];
          if (child && child.mesh !== undefined) {
            parentGroups.add(node.name);
          }
        }
      }
    }
  }

  console.log(`\nВсего узлов в GLB: ${allNodes.length}`);
  console.log(`Узлов с мешами: ${meshNodes.length}`);
  console.log(`Групп (multi-prim родители): ${parentGroups.size}`);
  console.log(`Компонентов в component-map: ${mapNames.size}`);

  // Проверяем какие меш-узлы НЕ в component-map
  // Three.js при загрузке GLB sanitize-ит имена (пробелы → _)
  const unmapped = [];
  const mapped = [];

  for (const nodeName of meshNodes) {
    const sanitized = sanitizeName(nodeName);

    // Проверка: имя в component-map?
    let found = mapNames.has(nodeName) || mapNames.has(sanitized);

    // Fallback: имя родительской группы (multi-prim)
    if (!found) {
      // Ищем родителя этого узла
      for (const node of gltf.nodes) {
        if (node.children) {
          const nodeIdx = gltf.nodes.findIndex(n => n.name === nodeName);
          if (node.children.includes(nodeIdx)) {
            const parentSanitized = sanitizeName(node.name || '');
            if (mapNames.has(node.name) || mapNames.has(parentSanitized)) {
              found = true;
            }
            break;
          }
        }
      }
    }

    // Fallback: strip _N суффикс (Three.js dedup)
    if (!found) {
      const stripped = sanitized.replace(/_\d+$/, '');
      if (mapNames.has(stripped)) found = true;
    }

    if (found) {
      mapped.push(nodeName);
    } else {
      unmapped.push(nodeName);
    }
  }

  console.log(`\nРаспознано: ${mapped.length}`);
  console.log(`НЕ распознано (unknown): ${unmapped.length}`);

  if (unmapped.length > 0) {
    console.log(`\n--- Нераспознанные меши ---`);
    for (const name of unmapped) {
      console.log(`  "${name}"  →  sanitized: "${sanitizeName(name)}"`);
    }
  }

  // Также проверяем: есть ли в component-map компоненты, которых нет в GLB
  const glbNodeSet = new Set(allNodes.map(n => sanitizeName(n)));
  const missingInGlb = [];
  for (const compName of mapNames) {
    if (!glbNodeSet.has(compName) && !glbNodeSet.has(sanitizeName(compName))) {
      missingInGlb.push(compName);
    }
  }

  if (missingInGlb.length > 0) {
    console.log(`\n--- В component-map, но НЕТ в GLB (${missingInGlb.length}) ---`);
    for (const name of missingInGlb.slice(0, 20)) {
      console.log(`  "${name}" (layer: ${components[name]?.layer})`);
    }
    if (missingInGlb.length > 20) console.log(`  ... и ещё ${missingInGlb.length - 20}`);
  }

  return { meshNodes, unmapped, mapped, mapNames, allNodes, parentGroups };
}

// --- Запуск ---
const li7 = analyzeModel(
  'Li7',
  path.join(base, 'Li7_unified.glb'),
  path.join(base, 'architecture/li7-component-map-v2.json')
);

const li9 = analyzeModel(
  'Li9',
  path.join(base, 'Li9_unified.glb'),
  path.join(base, 'architecture/li9-component-map-v2.json')
);

console.log('\n' + '='.repeat(60));
console.log('  ИТОГО');
console.log('='.repeat(60));
console.log(`Li7: ${li7.unmapped.length} нераспознанных из ${li7.meshNodes.length} мешей`);
console.log(`Li9: ${li9.unmapped.length} нераспознанных из ${li9.meshNodes.length} мешей`);
