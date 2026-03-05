/**
 * Build glossary ↔ mesh mapping v2.
 *
 * For Li7: match by meshName (Russian)
 * For Li9: match by displayName (Russian)
 *
 * Output:
 *   - architecture/glossary-mesh-mapping.json  (full mapping)
 *   - architecture/glossary-additions.json     (terms to add to glossary)
 */
const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');
const glossary = JSON.parse(fs.readFileSync(
  path.join(base, 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'
));
const li7 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li7-component-map-v2.json'), 'utf8'));
const li9 = JSON.parse(fs.readFileSync(path.join(base, 'architecture/li9-component-map-v2.json'), 'utf8'));

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
const layerToCat = {};
for (const [c, l] of Object.entries(catToLayer)) layerToCat[l] = c;

// ===== Build glossary index =====
const glossaryTerms = []; // flat array of all terms with metadata
const termsByEnLower = {}; // en_lower -> term
const termsByRuLower = {}; // ru_lower -> term

for (const [catId, cat] of Object.entries(glossary.categories)) {
  const layerId = catToLayer[catId];
  if (layerId === undefined) continue;

  cat.terms.forEach((term, idx) => {
    const id = term.en
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '')
      .replace(/_+/g, '_');

    const entry = { ...term, catId, layerId, id, fullId: `${id}@${layerId}` };
    glossaryTerms.push(entry);

    // Index by all English variants (split by " / ")
    for (const variant of term.en.toLowerCase().split(' / ')) {
      const v = variant.trim();
      if (v) termsByEnLower[v] = entry;
    }
    // Index by Russian (exact)
    termsByRuLower[term.ru.toLowerCase()] = entry;
  });
}

// ===== Comprehensive manual mapping =====
// meshBaseName (lower) -> glossary fullId OR { en, ru, zh, ar, es } for new terms
const manualMap = {
  // ---- TIRES & WHEELS ----
  'шина': 'tire_tyre@drivetrain',
  'колесо': 'wheel@drivetrain',
  'ступица задняя': 'wheel_hub_hub@drivetrain',
  'ступица передняя': 'wheel_hub_hub@drivetrain',

  // ---- BRAKES ----
  'тормоз': 'brake_caliper@brakes',
  'педаль тормоза': 'brake_pedal@brakes',
  'педаль газа': 'accelerator_pedal@interior',

  // ---- SUSPENSION ----
  'полуось задняя': 'half_shaft_cv_axle@drivetrain',
  'полуось передняя': 'half_shaft_cv_axle@drivetrain',
  'пневмоподвеска': 'air_suspension@drivetrain',
  'амортизатор': 'shock_absorber_damper@drivetrain',
  'амортизатор з (шир.)': 'shock_absorber_damper@drivetrain',
  'стойка передняя': 'strut@drivetrain',
  'стойка передняя (шир.)': 'strut@drivetrain',
  'пружина задняя': 'coil_spring@drivetrain',
  'пружина задняя (шир.)': 'coil_spring@drivetrain',
  'стабилизатор': 'stabilizer_bar_anti_roll_bar@drivetrain',
  'стабилизатор з (шир.)': 'stabilizer_bar_anti_roll_bar@drivetrain',
  'стабилизатор задний': 'rear_anti_roll_bar@drivetrain',
  'стабилизатор п (шир.)': 'stabilizer_bar_anti_roll_bar@drivetrain',
  'стабилизатор передний': 'front_anti_roll_bar@drivetrain',
  'верхний рычаг': 'rear_right_control_arm@drivetrain',  // closest match
  'верхний рычаг задний': 'rear_right_control_arm@drivetrain',
  'верхний рычаг з (шир.)': 'rear_left_control_arm@drivetrain',
  'нижний рычаг': 'front_right_control_arm@drivetrain',
  'нижний рычаг задний': 'rear_left_control_arm@drivetrain',
  'нижний рычаг з (шир.)': 'rear_left_control_arm@drivetrain',
  'нижний рычаг пб': 'front_right_control_arm@drivetrain',
  'нижний рычаг пб (шир.)': 'front_right_control_arm@drivetrain',
  'нижний рычаг па': 'front_left_control_arm@drivetrain',
  'нижний рычаг па (шир.)': 'front_left_control_arm@drivetrain',
  'подрамник': 'subframe@drivetrain',
  'подрамник задний': 'subframe@drivetrain',
  'подрамник задний (шир.)': 'subframe@drivetrain',
  'подрамник передний': 'subframe@drivetrain',

  // ---- STEERING ----
  'рулевой механизм': 'steering_gear_steering_box@brakes',
  'рулевая тяга': 'tie_rod@brakes',
  'рулевая тяга з (шир.)': 'tie_rod@brakes',
  'рулевая тяга задняя': 'tie_rod@brakes',
  'рулевая тяга п (шир.)': 'tie_rod@brakes',
  'рулевая тяга передняя': 'tie_rod@brakes',
  'руль': 'steering_wheel@brakes',
  'руль (экран)': 'steering_wheel@brakes',
  'руль (альт.)': 'steering_wheel@brakes',

  // ---- BODY ----
  'капот': 'bonnet_hood@body',
  'крыша': 'roof@body',
  'крышка багажника': 'trunk_lid@body',
  'защита днища': 'underbody_cover@body',
  'крышка днища': 'underbody_cover@body',
  'кузов': 'body_shell@body',
  'кузов (интерьер)': 'interior_trim@interior',
  'кузов (интерьер) 2': 'interior_trim@interior',
  'бампер передний': 'front_bumper@body',
  'бампер задний': 'rear_bumper@body',
  'бампер задний (часть)': 'rear_bumper@body',
  'крыло правое': 'fender_wing@body',
  'крыло левое': 'fender_wing@body',
  'четвертные панели': 'quarter_panel@body',
  'лобовое стекло': 'windscreen_windshield@body',
  'боковое стекло правое': 'side_window@body',
  'боковое стекло левое': 'side_window@body',
  'стекло двери': 'door_glass@body',
  'стекло багажника': 'rear_window@body',
  'стекло люка': 'sunroof_glass@body',
  'стекло фары правой': 'headlight_lens@body',
  'стекло фары левой': 'headlight_lens@body',
  'фара правая': 'headlight_headlamp@body',
  'фара левая': 'headlight_headlamp@body',
  'зеркало правое': 'wing_mirror_door_mirror_side_mirror@body',
  'зеркало левое': 'wing_mirror_door_mirror_side_mirror@body',
  'днище': 'floor_pan@body',
  'люк': 'sunroof@body',
  'радиатор': 'radiator@hvac',
  'накладка люка': 'sunroof@body',

  // ---- DOORS & INTERIOR ----
  'дверь задняя правая': 'rear_door@body',
  'дверь задняя левая': 'rear_door@body',
  'дверь передняя правая': 'front_door@body',
  'дверь передняя левая': 'front_door@body',
  'ручка двери': 'door_handle_exterior@interior',
  'дверная карта': 'door_trim_panel_door_card@interior',
  'козырёк': 'sun_visor@interior',
  'сиденье (доп.)': 'rear_seat@interior',
  'сиденье пп (часть)': 'front_seat@interior',
  'сиденье пп': 'front_seat@interior',
  'сиденье пл (часть)': 'front_seat@interior',
  'сиденье пл': 'front_seat@interior',
  'сиденья задние': 'rear_seat@interior',
  'подушка сиденья правая': 'seat_cushion_seat_base@interior',
  'подушка сиденья левая': 'seat_cushion_seat_base@interior',
  'бардачок': 'glove_box_glove_compartment@interior',
  'монитор': 'infotainment_screen_multimedia_display@interior',
  'центральный экран': 'infotainment_screen_multimedia_display@interior',
  'экран приборов': 'instrument_cluster_gauge_cluster@interior',
  'приборная панель': 'dashboard_instrument_panel_fascia@interior',
  'приборная панель (экраны)': 'instrument_cluster_gauge_cluster@interior',
  'зеркало салонное': 'interior_rearview_mirror@interior',

  // ---- ENGINE ----
  'двигатель i4': 'engine_ice@engine',
  'впускной коллектор i4': 'intake_manifold@engine',
  'топливный бак': 'fuel_tank@engine',
  'выхлопная труба': 'exhaust_pipe_tail_pipe@engine',
  'выхлопная система': 'exhaust_system@engine',
  'выхлоп i4 1.5 бензин': 'exhaust_manifold@engine',
  'крепление э/мотора': 'engine_mount_motor_mount@engine',
  'лючок бака': 'fuel_filler_cap@engine',

  // ---- EV ----
  'батарея вн': 'traction_battery_hv@ev',
  'электромотор задний': 'electric_motor_traction@ev',
  'электромотор передний': 'electric_motor_traction@ev',
  'проводка э/мотора': 'high_voltage_wiring_harness@ev',
  'проводка батареи': 'high_voltage_wiring_harness@ev',
  'лючок зарядки': 'charging_flap_charge_port_door@ev',

  // ---- HVAC ----
  'охлаждение батареи': 'battery_thermal_management_system_btms@hvac',

  // ---- SENSORS ----
  'блок управления': 'electronic_control_unit_ecu@sensors',

  // ---- INDICATORS ----
  'индикаторы приборов': 'instrument_cluster_gauge_cluster@interior',
  'индикаторы приборов 2': 'instrument_cluster_gauge_cluster@interior',

  // ===== Li9 displayName-based mappings =====
  'накладки кузова': 'body_trim_moulding@body',
  'подкрылки': 'fender_liner@body',
  'усилитель бампера передний': 'bumper_reinforcement@body',
  'усилитель бампера': 'bumper_reinforcement@body',
  'усиление передней части': 'bumper_reinforcement@body',
  'передний дифференциал': 'differential@drivetrain',
  'задний дифференциал': 'differential@drivetrain',
  'передний дифференциал (группа)': 'differential@drivetrain',
  'двигатель v8': 'engine_ice@engine',
  'двигатель (увеличитель запаса хода)': 'engine_ice@engine',
  'коробка передач': 'automatic_transmission_at@engine',
  'защита днища (пластик)': 'underbody_cover@body',
  'раздаточная коробка': 'transfer_case_t_case@drivetrain',
  'рулевая рейка': 'steering_gear_steering_box@brakes',
  'колёсный диск': 'wheel@drivetrain',
  'диск колеса': 'wheel@drivetrain',
  'элемент колеса': 'wheel@drivetrain',
  'каркас кузова': 'body_shell@body',
  'панели кузова': 'body_panel@body',
  'задняя дверь (лифтбек)': 'tailgate@body',
  'стекло задней двери': 'rear_window@body',
  'стекло крышки багажника': 'rear_window@body',
  'поверхность кузова': 'body_shell@body',
  'элемент кузова': 'body_shell@body',
  'элемент кузова (задняя часть)': 'body_shell@body',
  'элемент кузова (боковой)': 'body_shell@body',
  'элемент кузова (нижний)': 'body_shell@body',
  'элемент кузова (крыша)': 'roof@body',
  'элемент кузова (задний)': 'body_shell@body',
  'элемент кузова (боковой п)': 'body_shell@body',
  'элемент кузова (боковой л)': 'body_shell@body',
  'элемент кузова (стойки)': 'body_shell@body',
  'элемент кузова (пороги)': 'sill_rocker_panel@body',
  'элемент кузова (передний)': 'body_shell@body',
  'элемент кузова (основной)': 'body_shell@body',
  'элемент кузова (арка)': 'fender_liner@body',
  'элемент кузова (рамка)': 'body_shell@body',
  'элемент кузова (молдинг)': 'body_trim_moulding@body',
  'элемент кузова (накладка)': 'body_trim_moulding@body',
  'элемент шасси': 'subframe@drivetrain',
  'элемент шасси (передний)': 'subframe@drivetrain',
  'элемент шасси (средний)': 'subframe@drivetrain',
  'элемент шасси (задний)': 'subframe@drivetrain',
  'элемент шасси (боковой)': 'subframe@drivetrain',
  'элемент шасси (нижний)': 'subframe@drivetrain',
  'элемент шасси (поперечный)': 'subframe@drivetrain',
  'элемент шасси (основной)': 'subframe@drivetrain',
  'задняя панель': 'body_shell@body',
  'задняя панель (элемент)': 'body_shell@body',
  'колёсные арки': 'wheel_arch_liner@body',
  'надпись модели': 'emblem@body',
  'стекло заднего фонаря правого': 'tail_light_lens@body',
  'стекло заднего фонаря левого': 'tail_light_lens@body',
  'стекло фонаря багажника': 'tail_light_lens@body',
  'фонарь крышки багажника': 'tail_light_rear_lamp@body',
  'решётка радиатора': 'grille@body',
  'дополнительный элемент': 'body_trim_moulding@body',
  'панель двери': 'door_trim_panel_door_card@interior',
  'передний кардан': 'drive_shaft_propeller_shaft@drivetrain',
  'задний кардан': 'drive_shaft_propeller_shaft@drivetrain',
  'подрамник (элемент)': 'subframe@drivetrain',
  'выхлопная система левая б': 'exhaust_system@engine',
  'нижний рычаг передний а': 'front_left_control_arm@drivetrain',
  'нижний рычаг передний б': 'front_right_control_arm@drivetrain',
  'рулевое колесо': 'steering_wheel@brakes',
  'сиденье заднее (элемент)': 'rear_seat@interior',
  'сиденье заднее (элемент 2)': 'rear_seat@interior',
  'сиденье (элемент)': 'front_seat@interior',
  'блок управления xcu': 'electronic_control_unit_ecu@sensors',
  'лобовое стекло (li9)': 'windscreen_windshield@body',
  'стекло двери зп': 'door_glass@body',
  'стекло двери зл': 'door_glass@body',
  'стекло двери пп': 'door_glass@body',
  'стекло двери пл': 'door_glass@body',
  'боковое стекло правое (li9)': 'side_window@body',
  'боковое стекло левое (li9)': 'side_window@body',
  'зеркало правое (li9)': 'wing_mirror_door_mirror_side_mirror@body',
  'зеркало левое (li9)': 'wing_mirror_door_mirror_side_mirror@body',
  'фонарь задний правый': 'tail_light_rear_lamp@body',
  'фонарь задний левый': 'tail_light_rear_lamp@body',
  'фара (li9)': 'headlight_headlamp@body',
  'стекло фары': 'headlight_lens@body',
  'сиденье переднее правое': 'front_seat@interior',
  'сиденье переднее левое': 'front_seat@interior',
  'задние сиденья': 'rear_seat@interior',
  'дверь зп': 'rear_door@body',
  'дверь зл': 'rear_door@body',
  'дверь пп': 'front_door@body',
  'дверь пл': 'front_door@body',
  'дверная карта зп': 'door_trim_panel_door_card@interior',
  'дверная карта зл': 'door_trim_panel_door_card@interior',
  'дверная карта пп': 'door_trim_panel_door_card@interior',
  'дверная карта пл': 'door_trim_panel_door_card@interior',
  'дверная карта': 'door_trim_panel_door_card@interior',
  'салон': 'interior_trim@interior',
  'приборная панель (li9)': 'dashboard_instrument_panel_fascia@interior',
  'руль (li9)': 'steering_wheel@brakes',
  'центральный экран (li9)': 'infotainment_screen_multimedia_display@interior',
  'капот (li9)': 'bonnet_hood@body',
  'тормоз': 'brake_caliper@brakes',
  'батарея вн': 'traction_battery_hv@ev',
  'фонарь багажника': 'tail_light_rear_lamp@body',
  'стекло фонаря заднего': 'tail_light_lens@body',
  'теплозащита': 'heat_shield@body',
  'дроссельная заслонка': 'throttle_body@engine',
  'головное устройство': 'head_unit_infotainment_unit@sensors',
  'надпись': 'emblem@body',
  'рамка номера': 'licence_plate_bracket@body',
  'накладка люка': 'sunroof@body',
  'экран приборов': 'instrument_cluster_gauge_cluster@interior',
  'индикаторы приборов': 'instrument_cluster_gauge_cluster@interior',
  'индикаторы приборов 2': 'instrument_cluster_gauge_cluster@interior',
  'приборная панель (экраны)': 'instrument_cluster_gauge_cluster@interior',
  'люк': 'sunroof@body',
  'рулевой механизм': 'steering_gear_steering_box@brakes',
  'педаль газа': 'accelerator_pedal@interior',
  'крепление э/мотора': 'engine_mount_motor_mount@engine',
  'электромотор задний': 'electric_motor_traction@ev',
  'электромотор передний': 'electric_motor_traction@ev',
  'блок управления': 'electronic_control_unit_ecu@sensors',
  'проводка э/мотора': 'high_voltage_wiring_harness@ev',
  'проводка батареи': 'high_voltage_wiring_harness@ev',
  'охлаждение батареи': 'battery_thermal_management_system_btms@hvac',
  'лючок зарядки': 'charging_flap_charge_port_door@ev',
};

// ===== NEW terms to add to glossary =====
const newGlossaryTerms = [
  {
    id: 'paddle_shifter', catId: 'steering_brakes',
    en: 'paddle shifter', ru: 'подрулевой лепесток',
    zh: '换挡拨片', ar: 'مجداف نقل السرعة', es: 'levas de cambio'
  },
  {
    id: 'licence_plate', catId: 'body_frame',
    en: 'licence plate', ru: 'номерной знак',
    zh: '车牌', ar: 'لوحة ترخيص', es: 'matrícula'
  },
  {
    id: 'licence_plate_bracket', catId: 'body_frame',
    en: 'licence-plate bracket', ru: 'рамка номерного знака',
    zh: '车牌框', ar: 'إطار لوحة الترخيص', es: 'soporte de matrícula'
  },
  {
    id: 'emblem', catId: 'body_frame',
    en: 'emblem / badge', ru: 'эмблема / значок',
    zh: '徽标', ar: 'شعار', es: 'emblema / insignia'
  },
  {
    id: 'air_freshener_fragrance_diffuser', catId: 'doors_trunk_interior',
    en: 'air freshener / fragrance diffuser', ru: 'ароматизатор',
    zh: '香氛系统', ar: 'معطر الهواء', es: 'ambientador / difusor de fragancia'
  },
  {
    id: 'column_switch_combination_switch', catId: 'steering_brakes',
    en: 'column switch / combination switch', ru: 'подрулевой переключатель',
    zh: '组合开关', ar: 'مفتاح التوجيه', es: 'conmutador de columna'
  },
  {
    id: 'headlight_lens', catId: 'body_frame',
    en: 'headlight lens', ru: 'стекло фары',
    zh: '大灯透镜', ar: 'عدسة المصباح الأمامي', es: 'cristal de faro'
  },
  {
    id: 'door_glass', catId: 'body_frame',
    en: 'door glass', ru: 'стекло двери',
    zh: '车门玻璃', ar: 'زجاج الباب', es: 'cristal de puerta'
  },
  {
    id: 'sunroof_glass', catId: 'body_frame',
    en: 'sunroof glass', ru: 'стекло люка',
    zh: '天窗玻璃', ar: 'زجاج فتحة السقف', es: 'cristal del techo solar'
  },
  {
    id: 'front_door', catId: 'body_frame',
    en: 'front door', ru: 'передняя дверь',
    zh: '前车门', ar: 'الباب الأمامي', es: 'puerta delantera'
  },
  {
    id: 'rear_door', catId: 'body_frame',
    en: 'rear door', ru: 'задняя дверь',
    zh: '后车门', ar: 'الباب الخلفي', es: 'puerta trasera'
  },
  {
    id: 'tail_light_lens', catId: 'body_frame',
    en: 'tail light lens', ru: 'стекло фонаря',
    zh: '尾灯透镜', ar: 'عدسة المصباح الخلفي', es: 'cristal de piloto trasero'
  },
  {
    id: 'front_seat', catId: 'doors_trunk_interior',
    en: 'front seat', ru: 'переднее сиденье',
    zh: '前座椅', ar: 'المقعد الأمامي', es: 'asiento delantero'
  },
  {
    id: 'rear_seat', catId: 'doors_trunk_interior',
    en: 'rear seat', ru: 'заднее сиденье',
    zh: '后座椅', ar: 'المقعد الخلفي', es: 'asiento trasero'
  },
  {
    id: 'interior_trim', catId: 'doors_trunk_interior',
    en: 'interior trim', ru: 'обшивка салона',
    zh: '内饰装饰', ar: 'تجهيزات داخلية', es: 'tapizado interior'
  },
  {
    id: 'body_shell', catId: 'body_frame',
    en: 'body shell', ru: 'кузов (несущий)',
    zh: '车身壳体', ar: 'هيكل السيارة', es: 'carrocería (portante)'
  },
  {
    id: 'steering_wheel', catId: 'steering_brakes',
    en: 'steering wheel', ru: 'рулевое колесо / руль',
    zh: '方向盘', ar: 'عجلة القيادة', es: 'volante'
  },
  {
    id: 'body_panel', catId: 'body_frame',
    en: 'body panel', ru: 'панель кузова',
    zh: '车身面板', ar: 'لوحة الهيكل', es: 'panel de carrocería'
  },
  {
    id: 'high_voltage_wiring_harness', catId: 'ev_electrical',
    en: 'high-voltage wiring harness', ru: 'высоковольтный жгут проводов',
    zh: '高压线束', ar: 'حزمة أسلاك الجهد العالي', es: 'mazo de cables de alto voltaje'
  },
  {
    id: 'charging_flap_charge_port_door', catId: 'ev_electrical',
    en: 'charging flap / charge port door', ru: 'крышка зарядного порта',
    zh: '充电口盖', ar: 'غطاء منفذ الشحن', es: 'tapa del puerto de carga'
  },
  {
    id: 'fuel_filler_cap', catId: 'engine_fuel_exhaust',
    en: 'fuel filler cap', ru: 'крышка топливного бака',
    zh: '油箱盖', ar: 'غطاء خزان الوقود', es: 'tapa del depósito de combustible'
  },
  {
    id: 'head_unit_infotainment_unit', catId: 'sensors_adas',
    en: 'head unit / infotainment unit', ru: 'головное устройство',
    zh: '主机 / 信息娱乐系统', ar: 'وحدة الترفيه', es: 'unidad principal / unidad multimedia'
  },
  {
    id: 'wheel_arch_liner', catId: 'body_frame',
    en: 'wheel arch liner', ru: 'колёсные арки',
    zh: '轮拱衬板', ar: 'بطانة قوس العجلة', es: 'protector de paso de rueda'
  },
  {
    id: 'drive_shaft_propeller_shaft', catId: 'drivetrain_suspension',
    en: 'drive shaft / propeller shaft', ru: 'карданный вал',
    zh: '传动轴', ar: 'عمود الإدارة', es: 'eje de transmisión / cardán'
  },
  {
    id: 'sill_rocker_panel', catId: 'body_frame',
    en: 'sill / rocker panel', ru: 'порог',
    zh: '门槛板', ar: 'عتبة الباب', es: 'estribo / umbral'
  },
  {
    id: 'grille', catId: 'body_frame',
    en: 'grille', ru: 'решётка радиатора',
    zh: '进气格栅', ar: 'شبكة المبرد', es: 'rejilla / parrilla'
  },
  {
    id: 'door_trim_panel_door_card', catId: 'doors_trunk_interior',
    en: 'door trim panel / door card', ru: 'дверная карта / обшивка двери',
    zh: '车门内饰板', ar: 'لوحة تجهيز الباب', es: 'panel de puerta'
  },
  {
    id: 'differential', catId: 'drivetrain_suspension',
    en: 'differential', ru: 'дифференциал',
    zh: '差速器', ar: 'ترس تفاضلي', es: 'diferencial'
  },
  {
    id: 'transfer_case_t_case', catId: 'drivetrain_suspension',
    en: 'transfer case', ru: 'раздаточная коробка',
    zh: '分动箱', ar: 'علبة النقل', es: 'caja de transferencia'
  },
  {
    id: 'automatic_transmission_at', catId: 'engine_fuel_exhaust',
    en: 'automatic transmission', ru: 'автоматическая коробка передач',
    zh: '自动变速箱', ar: 'ناقل حركة أوتوماتيكي', es: 'transmisión automática'
  },
  {
    id: 'engine_mount_motor_mount', catId: 'engine_fuel_exhaust',
    en: 'engine mount / motor mount', ru: 'опора двигателя',
    zh: '发动机支架', ar: 'حامل المحرك', es: 'soporte del motor'
  },
];

// Index new terms
for (const nt of newGlossaryTerms) {
  const layerId = catToLayer[nt.catId];
  const fullId = `${nt.id}@${layerId}`;
  glossaryTerms.push({ ...nt, layerId, fullId });
}

// Build fast lookup: fullId -> term
const termByFullId = {};
for (const t of glossaryTerms) {
  termByFullId[t.fullId] = t;
}

// ===== Process mesh components =====
function processComponent(meshName, comp, useDisplayName) {
  const layer = comp.layer;
  const nameToMatch = useDisplayName ? (comp.displayName || meshName) : meshName;

  // Extract base name from mesh name (strip #2, sub-parts)
  let baseName = nameToMatch;
  const dashIdx = baseName.indexOf(' — ');
  if (dashIdx !== -1) baseName = baseName.substring(0, dashIdx);
  baseName = baseName.replace(/#\d+$/, '').trim();

  const lower = baseName.toLowerCase();

  // 1. Check manual map first (exact)
  if (manualMap[lower]) {
    const fullId = manualMap[lower];
    const term = termByFullId[fullId];
    if (term) {
      return { baseName, newGlossaryId: fullId, term, matchType: 'manual', score: 100 };
    }
  }

  // 2. Strip position codes, numbered suffixes, parenthesized qualifiers
  let stripped = lower;
  const posPatterns = [
    /\s+пл$/i, /\s+пп$/i, /\s+зл$/i, /\s+зп$/i,
    /\s+п$/i, /\s+л$/i,
    /\s+(передний|передняя|переднее|передних)(\s*\(шир\.\))?$/i,
    /\s+(задний|задняя|заднее|задних)(\s*\(шир\.\))?$/i,
    /\s+(правый|правая|правое)(\s*\(шир\.\))?$/i,
    /\s+(левый|левая|левое)(\s*\(шир\.\))?$/i,
    /\s*\(шир\.\)$/i,
    /\s*\(li9\)$/i,
    /\s*\(\d+\)$/i,        // (3), (2) etc
    /\s*\(часть\s*\d*\)$/i, // (часть 1), (часть)
    /\s*\(элемент\s*\d*\)$/i, // (элемент), (элемент 2)
    /\s*\(группа\)$/i,     // (группа)
  ];
  for (const pat of posPatterns) {
    stripped = stripped.replace(pat, '').trim();
  }

  if (stripped !== lower && manualMap[stripped]) {
    const fullId = manualMap[stripped];
    const term = termByFullId[fullId];
    if (term) {
      return { baseName, newGlossaryId: fullId, term, matchType: 'manual-stripped', score: 98 };
    }
  }

  // 3. Exact Russian match in glossary
  for (const t of glossaryTerms) {
    if (t.ru.toLowerCase() === lower || t.ru.toLowerCase() === stripped) {
      return { baseName, newGlossaryId: t.fullId, term: t, matchType: 'exact-ru', score: 90 };
    }
  }

  // 4. English match for Li9 (match meshName words against EN glossary terms)
  if (useDisplayName) {
    // try displayName-based matching already covered above
  } else {
    // For Li7, try Russian substring
    let bestMatch = null;
    let bestLen = 0;
    for (const t of glossaryTerms) {
      const tRu = t.ru.toLowerCase();
      if (stripped.includes(tRu) && tRu.length > bestLen && tRu.length >= 3) {
        bestMatch = t;
        bestLen = tRu.length;
      }
    }
    if (bestMatch) {
      return { baseName, newGlossaryId: bestMatch.fullId, term: bestMatch, matchType: 'substring-ru', score: 70 };
    }
  }

  return { baseName, newGlossaryId: null, term: null, matchType: 'none', score: 0 };
}

// Process Li7
console.log('=== Li7 Processing ===');
const li7Mapping = {};
let li7Matched = 0, li7Unmatched = 0;
const li7ByType = {};

for (const [meshName, comp] of Object.entries(li7.components)) {
  const result = processComponent(meshName, comp, false);
  li7Mapping[meshName] = {
    layer: comp.layer,
    baseName: result.baseName,
    oldGlossaryId: comp.glossary_id,
    newGlossaryId: result.newGlossaryId,
    matchType: result.matchType,
    matchScore: result.score,
    glossaryTerm: result.term ? {
      en: result.term.en, ru: result.term.ru,
      zh: result.term.zh, ar: result.term.ar, es: result.term.es
    } : null
  };
  if (result.newGlossaryId) {
    li7Matched++;
  } else {
    li7Unmatched++;
  }
  li7ByType[result.matchType] = (li7ByType[result.matchType] || 0) + 1;
}

console.log(`Matched: ${li7Matched}/${Object.keys(li7.components).length}`);
console.log('By type:', JSON.stringify(li7ByType));

// Show Li7 unmatched
const li7UnmatchedList = Object.entries(li7Mapping).filter(([_, m]) => m.matchType === 'none');
if (li7UnmatchedList.length > 0) {
  console.log('\nUnmatched Li7:');
  li7UnmatchedList.forEach(([name, m]) => console.log(`  ${name} (base: "${m.baseName}", layer: ${m.layer})`));
}

// Process Li9
console.log('\n=== Li9 Processing ===');
const li9Mapping = {};
let li9Matched = 0, li9Unmatched = 0;
const li9ByType = {};

for (const [meshName, comp] of Object.entries(li9.components)) {
  const result = processComponent(meshName, comp, true);
  li9Mapping[meshName] = {
    layer: comp.layer,
    displayName: comp.displayName,
    baseName: result.baseName,
    oldGlossaryId: comp.glossary_id,
    newGlossaryId: result.newGlossaryId,
    matchType: result.matchType,
    matchScore: result.score,
    glossaryTerm: result.term ? {
      en: result.term.en, ru: result.term.ru,
      zh: result.term.zh, ar: result.term.ar, es: result.term.es
    } : null
  };
  if (result.newGlossaryId) {
    li9Matched++;
  } else {
    li9Unmatched++;
  }
  li9ByType[result.matchType] = (li9ByType[result.matchType] || 0) + 1;
}

console.log(`Matched: ${li9Matched}/${Object.keys(li9.components).length}`);
console.log('By type:', JSON.stringify(li9ByType));

const li9UnmatchedList = Object.entries(li9Mapping).filter(([_, m]) => m.matchType === 'none');
if (li9UnmatchedList.length > 0) {
  console.log('\nUnmatched Li9:');
  li9UnmatchedList.forEach(([name, m]) => console.log(`  ${name} (display: "${m.displayName}", base: "${m.baseName}", layer: ${m.layer})`));
}

// ===== Write output =====
const output = {
  meta: {
    generated: new Date().toISOString(),
    description: 'Glossary ↔ 3D mesh mapping for Li7 and Li9',
    glossarySource: 'automotive-glossary-3d-components.json v3.1-3d',
    newTermsAdded: newGlossaryTerms.length
  },
  newGlossaryTerms,
  li7: {
    stats: { total: Object.keys(li7.components).length, matched: li7Matched, unmatched: li7Unmatched, byType: li7ByType },
    mapping: li7Mapping
  },
  li9: {
    stats: { total: Object.keys(li9.components).length, matched: li9Matched, unmatched: li9Unmatched, byType: li9ByType },
    mapping: li9Mapping
  }
};

fs.writeFileSync(
  path.join(base, 'architecture/glossary-mesh-mapping.json'),
  JSON.stringify(output, null, 2), 'utf8'
);
console.log('\nOutput: architecture/glossary-mesh-mapping.json');
