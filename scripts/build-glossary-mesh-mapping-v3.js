/**
 * Build glossary ↔ mesh mapping v3 (FINAL).
 *
 * Key fix: manual map uses term ID only (no @layer).
 * The @layer suffix is taken from the component's own layer.
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');
const glossary = JSON.parse(fs.readFileSync(
  path.join(base, 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'
));
const li7 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li7-component-map-v2.json'), 'utf8'));
const li9 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li9-component-map-v2.json'), 'utf8'));

// Category → Layer
const catToLayer = {
  body_frame: 'body', engine_fuel_exhaust: 'engine',
  drivetrain_suspension: 'drivetrain', ev_electrical: 'ev',
  steering_brakes: 'brakes', sensors_adas: 'sensors',
  hvac_thermal: 'hvac', doors_trunk_interior: 'interior'
};

// ===== NEW terms to add to glossary =====
const newTerms = [
  { id: 'paddle_shifter', catId: 'steering_brakes',
    en: 'paddle shifter', ru: 'подрулевой лепесток',
    zh: '换挡拨片', ar: 'مجداف نقل السرعة', es: 'levas de cambio' },
  { id: 'licence_plate', catId: 'body_frame',
    en: 'licence plate', ru: 'номерной знак',
    zh: '车牌', ar: 'لوحة ترخيص', es: 'matrícula' },
  { id: 'licence_plate_bracket', catId: 'body_frame',
    en: 'licence-plate bracket', ru: 'рамка номерного знака',
    zh: '车牌框', ar: 'إطار لوحة الترخيص', es: 'soporte de matrícula' },
  { id: 'emblem', catId: 'body_frame',
    en: 'emblem / badge', ru: 'эмблема / значок',
    zh: '徽标', ar: 'شعار', es: 'emblema / insignia' },
  { id: 'air_freshener', catId: 'doors_trunk_interior',
    en: 'air freshener / fragrance diffuser', ru: 'ароматизатор',
    zh: '香氛系统', ar: 'معطر الهواء', es: 'ambientador / difusor de fragancia' },
  { id: 'column_switch', catId: 'steering_brakes',
    en: 'column switch / combination switch', ru: 'подрулевой переключатель',
    zh: '组合开关', ar: 'مفتاح التوجيه', es: 'conmutador de columna' },
  { id: 'headlight_lens', catId: 'body_frame',
    en: 'headlight lens', ru: 'стекло фары',
    zh: '大灯透镜', ar: 'عدسة المصباح الأمامي', es: 'cristal de faro' },
  { id: 'door_glass', catId: 'body_frame',
    en: 'door glass', ru: 'стекло двери',
    zh: '车门玻璃', ar: 'زجاج الباب', es: 'cristal de puerta' },
  { id: 'sunroof_glass', catId: 'body_frame',
    en: 'sunroof glass', ru: 'стекло люка',
    zh: '天窗玻璃', ar: 'زجاج فتحة السقف', es: 'cristal del techo solar' },
  { id: 'front_door', catId: 'body_frame',
    en: 'front door', ru: 'передняя дверь',
    zh: '前车门', ar: 'الباب الأمامي', es: 'puerta delantera' },
  { id: 'rear_door', catId: 'body_frame',
    en: 'rear door', ru: 'задняя дверь',
    zh: '后车门', ar: 'الباب الخلفي', es: 'puerta trasera' },
  { id: 'tail_light_lens', catId: 'body_frame',
    en: 'tail light lens', ru: 'стекло фонаря',
    zh: '尾灯透镜', ar: 'عدسة المصباح الخلفي', es: 'cristal de piloto trasero' },
  { id: 'front_seat', catId: 'doors_trunk_interior',
    en: 'front seat', ru: 'переднее сиденье',
    zh: '前座椅', ar: 'المقعد الأمامي', es: 'asiento delantero' },
  { id: 'rear_seat', catId: 'doors_trunk_interior',
    en: 'rear seat', ru: 'заднее сиденье',
    zh: '后座椅', ar: 'المقعد الخلفي', es: 'asiento trasero' },
  { id: 'interior_trim', catId: 'doors_trunk_interior',
    en: 'interior trim', ru: 'обшивка салона',
    zh: '内饰装饰', ar: 'تجهيزات داخلية', es: 'tapizado interior' },
  { id: 'body_shell', catId: 'body_frame',
    en: 'body shell', ru: 'кузов (несущий)',
    zh: '车身壳体', ar: 'هيكل السيارة', es: 'carrocería (portante)' },
  { id: 'steering_wheel', catId: 'steering_brakes',
    en: 'steering wheel', ru: 'рулевое колесо / руль',
    zh: '方向盘', ar: 'عجلة القيادة', es: 'volante' },
  { id: 'high_voltage_wiring', catId: 'ev_electrical',
    en: 'high-voltage wiring harness', ru: 'высоковольтный жгут проводов',
    zh: '高压线束', ar: 'حزمة أسلاك الجهد العالي', es: 'mazo de cables de alto voltaje' },
  { id: 'charge_port_door', catId: 'ev_electrical',
    en: 'charging flap / charge port door', ru: 'крышка зарядного порта',
    zh: '充电口盖', ar: 'غطاء منفذ الشحن', es: 'tapa del puerto de carga' },
  { id: 'fuel_filler_cap', catId: 'engine_fuel_exhaust',
    en: 'fuel filler cap / fuel door', ru: 'крышка топливного бака / лючок бака',
    zh: '油箱盖', ar: 'غطاء خزان الوقود', es: 'tapa del depósito de combustible' },
  { id: 'head_unit', catId: 'sensors_adas',
    en: 'head unit / infotainment unit', ru: 'головное устройство',
    zh: '主机 / 信息娱乐系统', ar: 'وحدة الترفيه', es: 'unidad principal / unidad multimedia' },
  { id: 'wheel_arch_liner', catId: 'body_frame',
    en: 'wheel arch liner', ru: 'подкрылок / колёсные арки',
    zh: '轮拱衬板', ar: 'بطانة قوس العجلة', es: 'protector de paso de rueda' },
  { id: 'propeller_shaft', catId: 'drivetrain_suspension',
    en: 'drive shaft / propeller shaft', ru: 'карданный вал',
    zh: '传动轴', ar: 'عمود الإدارة', es: 'eje de transmisión / cardán' },
  { id: 'door_trim_panel', catId: 'doors_trunk_interior',
    en: 'door trim panel / door card', ru: 'дверная карта / обшивка двери',
    zh: '车门内饰板', ar: 'لوحة تجهيز الباب', es: 'panel de puerta' },
  { id: 'engine_mount', catId: 'engine_fuel_exhaust',
    en: 'engine mount / motor mount', ru: 'опора двигателя',
    zh: '发动机支架', ar: 'حامل المحرك', es: 'soporte del motor' },
  { id: 'sunroof_panel', catId: 'body_frame',
    en: 'sunroof', ru: 'люк крыши',
    zh: '天窗', ar: 'فتحة السقف', es: 'techo solar' },
];

// ===== Build glossary term index =====
// termById[id] = { en, ru, zh, ar, es, catId, layerId }
const termById = {};

for (const [catId, cat] of Object.entries(glossary.categories)) {
  const layerId = catToLayer[catId];
  if (layerId === undefined) continue;
  for (const term of cat.terms) {
    const id = term.en.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '').replace(/_+/g, '_');
    termById[id] = { ...term, catId, layerId, id };
  }
}
// Add new terms
for (const nt of newTerms) {
  const layerId = catToLayer[nt.catId];
  termById[nt.id] = { ...nt, layerId };
}

// ===== Manual map: baseName (lower) → term ID =====
const manual = {
  // ---- TIRES & WHEELS ----
  'шина': 'tire_tyre',
  'колесо': 'wheel',
  'ступица задняя': 'wheel_hub_hub',
  'ступица передняя': 'wheel_hub_hub',
  'диск колеса': 'wheel',
  'элемент колеса': 'wheel',
  'колёсный диск': 'wheel',

  // ---- BRAKES ----
  'тормоз': 'brake_caliper',
  'педаль тормоза': 'brake_pedal',
  'педаль газа': 'accelerator_pedal_gas_pedal',

  // ---- SUSPENSION ----
  'полуось задняя': 'half_shaft_cv_axle',
  'полуось передняя': 'half_shaft_cv_axle',
  'пневмоподвеска': 'air_suspension',
  'амортизатор': 'shock_absorber_damper',
  'амортизатор з (шир.)': 'shock_absorber_damper',
  'стойка передняя': 'strut',
  'стойка передняя (шир.)': 'strut',
  'пружина задняя': 'coil_spring',
  'пружина задняя (шир.)': 'coil_spring',
  'стабилизатор': 'stabilizer_bar_anti_roll_bar',
  'стабилизатор з (шир.)': 'stabilizer_bar_anti_roll_bar',
  'стабилизатор задний': 'rear_anti_roll_bar',
  'стабилизатор п (шир.)': 'stabilizer_bar_anti_roll_bar',
  'стабилизатор передний': 'front_anti_roll_bar',
  'верхний рычаг': 'rear_right_control_arm',
  'верхний рычаг задний': 'rear_right_control_arm',
  'верхний рычаг з (шир.)': 'rear_left_control_arm',
  'нижний рычаг': 'front_right_control_arm',
  'нижний рычаг задний': 'rear_left_control_arm',
  'нижний рычаг з (шир.)': 'rear_left_control_arm',
  'нижний рычаг пб': 'front_right_control_arm',
  'нижний рычаг пб (шир.)': 'front_right_control_arm',
  'нижний рычаг па': 'front_left_control_arm',
  'нижний рычаг па (шир.)': 'front_left_control_arm',
  'нижний рычаг передний а': 'front_left_control_arm',
  'нижний рычаг передний б': 'front_right_control_arm',
  'подрамник': 'subframe',
  'подрамник задний': 'subframe',
  'подрамник задний (шир.)': 'subframe',
  'подрамник передний': 'subframe',
  'подрамник (элемент)': 'subframe',

  // ---- STEERING ----
  'рулевой механизм': 'steering_box',
  'рулевая тяга': 'tie_rod',
  'рулевая тяга з (шир.)': 'tie_rod',
  'рулевая тяга задняя': 'tie_rod',
  'рулевая тяга п (шир.)': 'tie_rod',
  'рулевая тяга передняя': 'tie_rod',
  'рулевая рейка': 'steering_rack_rack_and_pinion',
  'руль': 'steering_wheel',
  'руль (экран)': 'steering_wheel',
  'руль (альт.)': 'steering_wheel',
  'рулевое колесо': 'steering_wheel',
  'подрулевой лепесток': 'paddle_shifter',
  'подрулевой переключатель': 'column_switch',

  // ---- BODY ----
  'капот': 'bonnet_hood',
  'крыша': 'roof',
  'крышка багажника': 'trunk_lid',
  'защита днища': 'underbody_cover',
  'крышка днища': 'underbody_cover',
  'кузов': 'body_shell',
  'кузов (интерьер)': 'interior_trim',
  'кузов (интерьер) 2': 'interior_trim',
  'бампер передний': 'front_bumper',
  'бампер передний (часть)': 'front_bumper',
  'бампер задний': 'rear_bumper',
  'бампер задний (часть)': 'rear_bumper',
  'крыло правое': 'fender_wing',
  'крыло левое': 'fender_wing',
  'четвертные панели': 'quarter_panel',
  'лобовое стекло': 'windscreen_windshield',
  'боковое стекло правое': 'side_window',
  'боковое стекло левое': 'side_window',
  'стекло двери': 'door_glass',
  'стекло багажника': 'rear_window',
  'стекло люка': 'sunroof_glass',
  'стекло фары правой': 'headlight_lens',
  'стекло фары левой': 'headlight_lens',
  'стекло фары': 'headlight_lens',
  'фара правая': 'headlight_headlamp',
  'фара левая': 'headlight_headlamp',
  'фара': 'headlight_headlamp',
  'зеркало правое': 'wing_mirror_door_mirror_side_mirror',
  'зеркало левое': 'wing_mirror_door_mirror_side_mirror',
  'днище': 'floor_pan',
  'люк': 'sunroof_panel',
  'накладка люка': 'sunroof_panel',
  'радиатор': 'radiator',
  'рамка номера': 'licence_plate_bracket',
  'номерной знак задний': 'licence_plate',
  'номерной знак передний': 'licence_plate',
  'надпись': 'emblem',
  'надпись "+"': 'emblem',
  'надпись "d"': 'emblem',
  'надпись хром': 'emblem',
  'надпись чёрная': 'emblem',
  'надпись модели': 'emblem',
  'теплозащита': 'heat_shield',
  'решётка радиатора': 'grille',
  'накладки кузова': 'body_trim_moulding',
  'подкрылки': 'fender_liner',
  'усилитель бампера передний': 'bumper_reinforcement',
  'усилитель бампера': 'bumper_reinforcement',
  'усиление передней части': 'bumper_reinforcement',
  'каркас кузова': 'body_shell',
  'панели кузова': 'body_panel',
  'поверхность кузова': 'body_shell',
  'элемент кузова': 'body_shell',
  'элемент кузова (задняя часть)': 'body_shell',
  'элемент кузова (боковой)': 'body_shell',
  'элемент кузова (нижний)': 'body_shell',
  'элемент кузова (крыша)': 'roof',
  'элемент кузова (задний)': 'body_shell',
  'элемент кузова (боковой п)': 'body_shell',
  'элемент кузова (боковой л)': 'body_shell',
  'элемент кузова (стойки)': 'body_shell',
  'элемент кузова (пороги)': 'sill_rocker_panel',
  'элемент кузова (передний)': 'body_shell',
  'элемент кузова (основной)': 'body_shell',
  'элемент кузова (арка)': 'wheel_arch_liner',
  'элемент кузова (рамка)': 'body_shell',
  'элемент кузова (молдинг)': 'body_trim_moulding',
  'элемент кузова (накладка)': 'body_trim_moulding',
  'элемент шасси': 'subframe',
  'элемент шасси (передний)': 'subframe',
  'элемент шасси (средний)': 'subframe',
  'элемент шасси (задний)': 'subframe',
  'элемент шасси (боковой)': 'subframe',
  'элемент шасси (нижний)': 'subframe',
  'элемент шасси (поперечный)': 'subframe',
  'элемент шасси (основной)': 'subframe',
  'задняя панель': 'body_shell',
  'задняя панель (элемент)': 'body_shell',
  'колёсные арки': 'wheel_arch_liner',
  'дополнительный элемент': 'body_trim_moulding',

  // ---- DOORS & INTERIOR ----
  'дверь задняя правая': 'rear_door',
  'дверь задняя левая': 'rear_door',
  'дверь передняя правая': 'front_door',
  'дверь передняя левая': 'front_door',
  'дверь зп': 'rear_door',
  'дверь зл': 'rear_door',
  'дверь пп': 'front_door',
  'дверь пл': 'front_door',
  'ручка двери': 'door_handle_exterior',
  'дверная карта': 'door_trim_panel',
  'дверная карта пп': 'door_trim_panel',
  'дверная карта пл': 'door_trim_panel',
  'дверная карта зп': 'door_trim_panel',
  'дверная карта зл': 'door_trim_panel',
  'панель двери': 'door_trim_panel',
  'задняя дверь (лифтбек)': 'tailgate',
  'козырёк': 'sun_visor',
  'сиденье (доп.)': 'rear_seat',
  'сиденье пп (часть)': 'front_seat',
  'сиденье пп': 'front_seat',
  'сиденье пл (часть)': 'front_seat',
  'сиденье пл': 'front_seat',
  'сиденье переднее правое': 'front_seat',
  'сиденье переднее левое': 'front_seat',
  'сиденья задние': 'rear_seat',
  'задние сиденья': 'rear_seat',
  'сиденье заднее': 'rear_seat',
  'сиденье (элемент)': 'front_seat',
  'подушка сиденья правая': 'seat_cushion_seat_base',
  'подушка сиденья левая': 'seat_cushion_seat_base',
  'бардачок': 'glove_box_glove_compartment',
  'монитор': 'infotainment_screen_multimedia_display',
  'центральный экран': 'infotainment_screen_multimedia_display',
  'экран приборов': 'instrument_cluster',
  'приборная панель': 'dashboard_instrument_panel_fascia',
  'приборная панель (экраны)': 'instrument_cluster',
  'индикаторы приборов': 'instrument_cluster',
  'индикаторы приборов 2': 'instrument_cluster',
  'зеркало салонное': 'interior_rearview_mirror',
  'ароматизатор': 'air_freshener',
  'салон': 'interior_trim',

  // ---- ENGINE ----
  'двигатель i4': 'engine_ice',
  'двигатель (увеличитель запаса хода)': 'engine_ice',
  'двигатель v8': 'engine_ice',
  'впускной коллектор i4': 'intake_manifold',
  'топливный бак': 'fuel_tank',
  'выхлопная труба': 'exhaust_pipe_tail_pipe',
  'выхлопная система': 'exhaust_system',
  'выхлопная система левая б': 'exhaust_system',
  'выхлоп i4 1.5 бензин': 'exhaust_manifold',
  'крепление э/мотора': 'engine_mount',
  'лючок бака': 'fuel_filler_cap',
  'коробка передач': 'automatic_transmission_at',
  'дроссельная заслонка': 'throttle_body',

  // ---- EV ----
  'батарея вн': 'traction_battery_hv_battery',
  'электромотор задний': 'rear_electric_motor',
  'электромотор передний': 'front_electric_motor',
  'проводка э/мотора': 'high_voltage_wiring',
  'проводка батареи': 'high_voltage_wiring',
  'лючок зарядки': 'charge_port_door',

  // ---- HVAC ----
  'охлаждение батареи': 'battery_thermal_management_system_btms',

  // ---- SENSORS ----
  'блок управления': 'motor_control_unit',
  'блок управления xcu': 'motor_control_unit',
  'головное устройство': 'head_unit',

  // ---- DRIVETRAIN ----
  'передний дифференциал': 'differential',
  'задний дифференциал': 'differential',
  'передний дифференциал (группа)': 'differential',
  'раздаточная коробка': 'transfer_case_t_case',
  'передний кардан': 'propeller_shaft',
  'задний кардан': 'propeller_shaft',

  // ---- LIGHTS ----
  'стекло заднего фонаря правого': 'tail_light_lens',
  'стекло заднего фонаря левого': 'tail_light_lens',
  'стекло фонаря багажника': 'tail_light_lens',
  'фонарь крышки багажника': 'tail_light_rear_lamp',
  'фонарь задний правый': 'tail_light_rear_lamp',
  'фонарь задний левый': 'tail_light_rear_lamp',
  'стекло задней двери': 'rear_window',
  'стекло крышки багажника': 'rear_window',
};

// ===== Position-stripping patterns =====
const stripPatterns = [
  /\s+пл$/i, /\s+пп$/i, /\s+зл$/i, /\s+зп$/i,
  /\s+п$/i, /\s+л$/i,
  /\s+(передний|передняя|переднее|передних)(\s*\(шир\.\))?$/i,
  /\s+(задний|задняя|заднее|задних)(\s*\(шир\.\))?$/i,
  /\s+(правый|правая|правое)(\s*\(шир\.\))?$/i,
  /\s+(левый|левая|левое)(\s*\(шир\.\))?$/i,
  /\s*\(шир\.\)$/i,
  /\s*\(li9\)$/i,
  /\s*\(\d+\)$/i,
  /\s*\(часть\s*\d*\)$/i,
  /\s*\(элемент\s*\d*\)$/i,
  /\s*\(группа\)$/i,
];

function stripPositionCodes(name) {
  let s = name;
  let prev;
  // Apply patterns iteratively until no more changes
  do {
    prev = s;
    for (const pat of stripPatterns) {
      s = s.replace(pat, '').trim();
    }
  } while (s !== prev);
  return s;
}

// ===== Match a component to a glossary term =====
function matchComponent(meshName, comp, useDisplayName) {
  const layer = comp.layer;
  const nameToMatch = useDisplayName ? (comp.displayName || meshName) : meshName;

  // Extract base name
  let baseName = nameToMatch;
  const dashIdx = baseName.indexOf(' — ');
  if (dashIdx !== -1) baseName = baseName.substring(0, dashIdx);
  baseName = baseName.replace(/#\d+$/, '').trim();

  const lower = baseName.toLowerCase();

  // 1. Direct manual lookup
  if (manual[lower]) {
    const term = termById[manual[lower]];
    if (term) return { baseName, termId: manual[lower], term, matchType: 'manual', score: 100 };
  }

  // 2. Strip position codes + manual lookup
  const stripped = stripPositionCodes(lower);
  if (stripped !== lower && manual[stripped]) {
    const term = termById[manual[stripped]];
    if (term) return { baseName, termId: manual[stripped], term, matchType: 'manual-stripped', score: 98 };
  }

  // 3. Exact Russian match in glossary
  for (const [id, t] of Object.entries(termById)) {
    if (t.ru.toLowerCase() === lower || t.ru.toLowerCase() === stripped) {
      return { baseName, termId: id, term: t, matchType: 'exact-ru', score: 90 };
    }
  }

  // 4. Russian substring (longest match wins)
  let bestId = null, bestLen = 0, bestTerm = null;
  for (const [id, t] of Object.entries(termById)) {
    const tRu = t.ru.toLowerCase();
    if (stripped.includes(tRu) && tRu.length > bestLen && tRu.length >= 3) {
      bestId = id; bestLen = tRu.length; bestTerm = t;
    }
  }
  if (bestTerm) return { baseName, termId: bestId, term: bestTerm, matchType: 'substring-ru', score: 70 };

  return { baseName, termId: null, term: null, matchType: 'none', score: 0 };
}

// ===== Process component map =====
function processMap(compMap, useDisplayName, label) {
  const mapping = {};
  let matched = 0, unmatched = 0;
  const byType = {};

  for (const [meshName, comp] of Object.entries(compMap.components)) {
    const result = matchComponent(meshName, comp, useDisplayName);
    const newGlossaryId = result.termId ? `${result.termId}@${comp.layer}` : null;

    mapping[meshName] = {
      layer: comp.layer,
      baseName: result.baseName,
      displayName: comp.displayName || undefined,
      oldGlossaryId: comp.glossary_id,
      newGlossaryId,
      matchType: result.matchType,
      matchScore: result.score,
      glossaryTerm: result.term ? {
        en: result.term.en, ru: result.term.ru,
        zh: result.term.zh, ar: result.term.ar, es: result.term.es
      } : null
    };

    if (newGlossaryId) matched++; else unmatched++;
    byType[result.matchType] = (byType[result.matchType] || 0) + 1;
  }

  console.log(`\n=== ${label} ===`);
  console.log(`Matched: ${matched}/${Object.keys(compMap.components).length} (${Math.round(matched/Object.keys(compMap.components).length*100)}%)`);
  console.log('By type:', JSON.stringify(byType));

  const unmatchedList = Object.entries(mapping).filter(([_, m]) => m.matchType === 'none');
  if (unmatchedList.length > 0) {
    console.log(`\nUnmatched (${unmatchedList.length}):`);
    unmatchedList.forEach(([name, m]) => {
      console.log(`  ${name} (display: "${m.displayName || '-'}", base: "${m.baseName}", layer: ${m.layer})`);
    });
  }

  return { mapping, stats: { total: Object.keys(compMap.components).length, matched, unmatched, byType } };
}

const li7Result = processMap(li7, false, 'Li7');
const li9Result = processMap(li9, true, 'Li9');

// ===== Write mapping output =====
const output = {
  meta: {
    generated: new Date().toISOString(),
    description: 'Glossary ↔ 3D mesh mapping for Li7 and Li9',
    glossarySource: 'automotive-glossary-3d-components.json v3.1-3d',
    newTermsCount: newTerms.length
  },
  newGlossaryTerms: newTerms,
  li7: { stats: li7Result.stats, mapping: li7Result.mapping },
  li9: { stats: li9Result.stats, mapping: li9Result.mapping }
};

const outPath = path.join(base, 'architecture/glossary-mesh-mapping.json');
fs.writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf8');
console.log(`\nMapping → ${outPath}`);

// ===== Show sample of corrected mappings =====
console.log('\n=== Sample corrected Li7 mappings ===');
Object.entries(li7Result.mapping).slice(0, 10).forEach(([name, m]) => {
  if (m.newGlossaryId) {
    const changed = m.oldGlossaryId !== m.newGlossaryId ? ' [CHANGED]' : '';
    console.log(`${name}: ${m.oldGlossaryId} → ${m.newGlossaryId}${changed}`);
    if (m.glossaryTerm) console.log(`  EN: ${m.glossaryTerm.en} | ZH: ${m.glossaryTerm.zh} | ES: ${m.glossaryTerm.es}`);
  }
});
