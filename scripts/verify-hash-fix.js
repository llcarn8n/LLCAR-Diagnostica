/**
 * Проверяет: после добавления #N стриппинга все ли 37 "unknown" мешей
 * теперь находят совпадение в component-map.
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');

// Те 37 мешей что были в unknown (из консоли браузера)
const unknownMeshes = [
  { name: 'Верхний_рычаг_З_(шир)#2', parent: 'Scene' },
  { name: 'Рулевая_тяга_З_(шир)#2', parent: 'Scene' },
  { name: 'Рулевая_тяга_П_(шир)#2', parent: 'Scene' },
  { name: 'Стабилизатор_З_(шир)#2', parent: 'Scene' },
  { name: 'Стабилизатор_П_(шир)#2', parent: 'Scene' },
  { name: 'Подрамник_задний_(шир)#2', parent: 'Scene' },
  { name: 'Стойка_передняя_(шир)#2_—_Накладка', parent: 'Стойка_передняя_(шир)#2' },
  { name: 'Стойка_передняя_(шир)#2_—_Рычаг', parent: 'Стойка_передняя_(шир)#2' },
  { name: 'Руль_(альт)#2_—_Приборная_панель', parent: 'Руль_(альт)#2' },
  { name: 'Руль_(альт)#2_—_Обшивка', parent: 'Руль_(альт)#2' },
  { name: 'Руль_(альт)#2_—_Отделка', parent: 'Руль_(альт)#2' },
  { name: 'Руль_(альт)#2_—_Спидометр', parent: 'Руль_(альт)#2' },
  { name: 'Руль_(альт)#2_—_Дисплей_руля', parent: 'Руль_(альт)#2' },
  { name: 'Руль_(альт)#2_—_Накладка_руля', parent: 'Руль_(альт)#2' },
  { name: 'Пружина_задняя_(шир)#2', parent: 'Scene' },
  { name: 'Амортизатор_З_(шир)#2', parent: 'Scene' },
  { name: 'Центральный_экран#2_—_Доп_дисплей', parent: 'Центральный_экран#2' },
  { name: 'Нижний_рычаг_З_(шир)#2', parent: 'Scene' },
  { name: 'Нижний_рычаг_ПБ_(шир)#2', parent: 'Scene' },
  { name: 'Нижний_рычаг_ПА_(шир)#2', parent: 'Scene' },
  { name: 'Выхлоп_I4_15_бензин#2', parent: 'Scene' },
  { name: 'Индикаторы_приборов_2#2_—_Инд_давление', parent: 'Индикаторы_приборов_2#2' },
  { name: 'Индикаторы_приборов_2#2_—_Инд_ABS', parent: 'Индикаторы_приборов_2#2' },
  { name: 'Индикаторы_приборов_2#2_—_Инд_ПТФ', parent: 'Индикаторы_приборов_2#2' },
  { name: 'Индикаторы_приборов_2#2_—_Инд_масло', parent: 'Индикаторы_приборов_2#2' },
  { name: 'Индикаторы_приборов_2#2_—_Инд_температура', parent: 'Индикаторы_приборов_2#2' },
  { name: 'Индикаторы_приборов_2#2_—_Инд_задний_ПТФ', parent: 'Индикаторы_приборов_2#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_поворотник_Л', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_поворотник_П', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_Check_Engine', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_ручник', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_топливо', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_дальний_свет', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_ближний_свет', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_ESC', parent: 'Индикаторы_приборов#2' },
  { name: 'Индикаторы_приборов#2_—_Инд_TCS', parent: 'Индикаторы_приборов#2' },
  { name: 'Сиденье_(доп)#2', parent: 'Scene' },
];

// Загружаем component-map Li7
const compMap = JSON.parse(fs.readFileSync(
  path.join(base, 'architecture/li7-component-map-v2.json'), 'utf8'
));

// Строим индекс как TagRegistry
function sanitizeName(name) {
  // Повторяет Three.js PropertyBinding.sanitizeNodeName: пробелы → _, удаляет \ [ ] . : /
  return name.replace(/\s/g, '_').replace(/[\[\].:\\/]/g, '');
}

const byMeshName = new Map();
for (const [meshName, comp] of Object.entries(compMap.components)) {
  byMeshName.set(meshName, { ...comp, meshName });
  const sanitized = sanitizeName(meshName);
  if (sanitized !== meshName) {
    byMeshName.set(sanitized, { ...comp, meshName });
  }
}

// Новая логика getByMeshName с #N стриппингом
function getByMeshName(name) {
  // Прямое совпадение
  if (byMeshName.has(name)) return byMeshName.get(name);

  // Без _N суффикса
  const stripped = name.replace(/_\d+$/, '');
  if (stripped !== name && byMeshName.has(stripped)) return byMeshName.get(stripped);

  // Без #N суффикса
  const strippedHash = name.replace(/#\d+$/, '');
  if (strippedHash !== name) {
    if (byMeshName.has(strippedHash)) return byMeshName.get(strippedHash);
    const doubleStripped = strippedHash.replace(/_\d+$/, '');
    if (doubleStripped !== strippedHash && byMeshName.has(doubleStripped))
      return byMeshName.get(doubleStripped);
  }

  return undefined;
}

// Проверяем каждый unknown меш
let matched = 0;
let still_unknown = 0;

console.log('Проверка 37 unknown мешей с новой логикой #N стриппинга:\n');

for (const m of unknownMeshes) {
  // 1. По имени меша
  let comp = getByMeshName(m.name);
  let matchedBy = 'имя меша';

  // 2. Fallback: по имени родителя
  if (!comp && m.parent !== 'Scene') {
    comp = getByMeshName(m.parent);
    matchedBy = 'имя родителя';
  }

  if (comp) {
    matched++;
    console.log(`  ✓ "${m.name}" → ${comp.meshName} (слой: ${comp.layer}) [по ${matchedBy}]`);
  } else {
    still_unknown++;
    console.log(`  ✗ "${m.name}" → НЕ НАЙДЕН (parent: ${m.parent})`);
  }
}

console.log(`\nРезультат: ${matched}/37 совпали, ${still_unknown} не найдены`);
