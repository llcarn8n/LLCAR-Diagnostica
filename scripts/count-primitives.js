/**
 * Подсчитывает реальное количество Three.js Mesh-объектов из GLB,
 * учитывая multi-primitive меши (один glTF mesh → несколько Three.js Mesh).
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');

function extractGlbJson(glbPath) {
  const buf = fs.readFileSync(glbPath);
  const chunkLen = buf.readUInt32LE(12);
  return JSON.parse(buf.toString('utf8', 20, 20 + chunkLen));
}

function sanitizeName(name) {
  return name.replace(/\s/g, '_').replace(/[^\w.-]/g, '');
}

function analyzeModel(modelName, glbPath, componentMapPath) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`  ${modelName}`);
  console.log(`${'='.repeat(60)}`);

  const gltf = extractGlbJson(glbPath);
  const compMap = JSON.parse(fs.readFileSync(componentMapPath, 'utf8'));
  const mapNames = new Set(Object.keys(compMap.components));

  // Подсчёт примитивов на меш
  let totalPrimitives = 0;
  const multiPrimMeshes = [];

  if (gltf.meshes) {
    for (let i = 0; i < gltf.meshes.length; i++) {
      const mesh = gltf.meshes[i];
      const primCount = mesh.primitives ? mesh.primitives.length : 1;
      totalPrimitives += primCount;
      if (primCount > 1) {
        multiPrimMeshes.push({ index: i, name: mesh.name, primitives: primCount });
      }
    }
  }

  console.log(`\nglTF mesh объектов: ${gltf.meshes?.length || 0}`);
  console.log(`Общее число примитивов (= Three.js Mesh объектов): ${totalPrimitives}`);
  console.log(`Multi-primitive мешей: ${multiPrimMeshes.length}`);

  if (multiPrimMeshes.length > 0) {
    console.log(`\n--- Multi-primitive меши ---`);
    for (const mp of multiPrimMeshes) {
      console.log(`  mesh[${mp.index}] "${mp.name}" → ${mp.primitives} примитивов`);
    }
  }

  // Теперь проследим: какие node→mesh имеют multi-prim
  // и какие из них создадут "безымянные" дочерние Mesh в Three.js
  const unmatchedPrimitives = [];

  if (gltf.nodes) {
    for (let ni = 0; ni < gltf.nodes.length; ni++) {
      const node = gltf.nodes[ni];
      if (node.mesh === undefined) continue;

      const mesh = gltf.meshes[node.mesh];
      const primCount = mesh.primitives ? mesh.primitives.length : 1;

      if (primCount > 1) {
        // Three.js создаёт Group с именем node.name,
        // дочерние Mesh получают имена "${node.name}_${i}" или просто "${node.name}"
        const nodeName = node.name || '';
        const sanitized = sanitizeName(nodeName);
        const inMap = mapNames.has(nodeName) || mapNames.has(sanitized);

        // Дочерние примитивы — их имена в Three.js:
        // Первый: node.name, остальные: node.name + "_1", "_2", ...
        // или все: mesh.name + "_0", "_1", ...
        // Зависит от версии Three.js

        if (!inMap) {
          unmatchedPrimitives.push({
            nodeName,
            meshName: mesh.name,
            primitives: primCount,
          });
        }
      }
    }
  }

  // Считаем: сколько Mesh-объектов Three.js НЕ имеют прямого совпадения
  // В traverse: child.isMesh → проверка child.name → проверка parent.name
  // Для multi-prim: Group(node.name) → Mesh_0, Mesh_1, ... (child.name часто пустое или "${meshName}_${i}")

  // Давайте посмотрим ВСЕ Three.js Mesh-имена, которые будут созданы
  console.log(`\n--- Симуляция Three.js traverse ---`);

  let threeMeshCount = 0;
  let matchedCount = 0;
  let unmatchedCount = 0;
  const unmatchedDetails = [];

  if (gltf.nodes) {
    for (const node of gltf.nodes) {
      if (node.mesh === undefined) continue;
      const mesh = gltf.meshes[node.mesh];
      const primCount = mesh.primitives?.length || 1;
      const nodeName = node.name || '';
      const sanitized = sanitizeName(nodeName);

      if (primCount === 1) {
        // Один Mesh — имя = node.name
        threeMeshCount++;
        if (mapNames.has(nodeName) || mapNames.has(sanitized) || mapNames.has(sanitized.replace(/_\d+$/, ''))) {
          matchedCount++;
        } else {
          unmatchedCount++;
          unmatchedDetails.push({ name: nodeName, type: 'single' });
        }
      } else {
        // Multi-prim: Three.js создаёт Group + child Meshes
        // Group.name = node.name (это НЕ Mesh, traverse его пропустит)
        // Child Mesh names: "${meshName}_0", "${meshName}_1", ... или пустые
        for (let p = 0; p < primCount; p++) {
          threeMeshCount++;
          // Child mesh name обычно: `${node.name}` для первого или `${node.name}_${p}`
          // Но в Three.js r182 GLTFLoader multi-prim дочерние меши получают name = mesh.name
          // Проверяем: parent.name (= node.name) в component-map?
          if (mapNames.has(nodeName) || mapNames.has(sanitized) || mapNames.has(sanitized.replace(/_\d+$/, ''))) {
            matchedCount++;
          } else {
            unmatchedCount++;
            unmatchedDetails.push({ name: `${nodeName}[prim_${p}]`, type: 'multi-prim child' });
          }
        }
      }
    }
  }

  console.log(`Three.js Mesh объектов: ${threeMeshCount}`);
  console.log(`Совпали с component-map: ${matchedCount}`);
  console.log(`НЕ совпали: ${unmatchedCount}`);

  if (unmatchedDetails.length > 0) {
    console.log(`\n--- Несовпавшие Three.js Mesh ---`);
    for (const d of unmatchedDetails) {
      console.log(`  "${d.name}" (${d.type})`);
    }
  }

  return { totalPrimitives, threeMeshCount, matchedCount, unmatchedCount };
}

analyzeModel(
  'Li7',
  path.join(base, 'Li7_unified.glb'),
  path.join(base, 'architecture/li7-component-map-v2.json')
);

analyzeModel(
  'Li9',
  path.join(base, 'Li9_unified.glb'),
  path.join(base, 'architecture/li9-component-map-v2.json')
);
