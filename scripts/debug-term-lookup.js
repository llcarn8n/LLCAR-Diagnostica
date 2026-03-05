const fs = require('fs');
const path = require('path');

const base = path.resolve(__dirname, '..');
const glossary = JSON.parse(fs.readFileSync(
  path.join(base, 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'
));

const catToLayer = {
  body_frame: 'body', engine_fuel_exhaust: 'engine',
  drivetrain_suspension: 'drivetrain', ev_electrical: 'ev',
  steering_brakes: 'brakes', sensors_adas: 'sensors',
  hvac_thermal: 'hvac', doors_trunk_interior: 'interior'
};

// Build termById like in v3
const termById = {};
for (const [catId, cat] of Object.entries(glossary.categories)) {
  const layerId = catToLayer[catId];
  if (layerId === undefined) continue;
  for (const term of cat.terms) {
    const id = term.en.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '').replace(/_+/g, '_');
    termById[id] = { en: term.en, ru: term.ru };
  }
}

// Check specific IDs
const checkIds = [
  'steering_gear_steering_box',
  'instrument_cluster_gauge_cluster',
  'accelerator_pedal',
  'electric_motor_traction',
  'electronic_control_unit_ecu',
  'brake_caliper',
  'tire_tyre',
];

for (const id of checkIds) {
  const found = termById[id];
  console.log(`${id}: ${found ? `YES (en: ${found.en}, ru: ${found.ru})` : 'NOT FOUND'}`);
}

// Find similar IDs
console.log('\nAll IDs containing "steering":');
for (const [id, t] of Object.entries(termById)) {
  if (id.includes('steering')) console.log(`  ${id}: ${t.en}`);
}
console.log('\nAll IDs containing "instrument":');
for (const [id, t] of Object.entries(termById)) {
  if (id.includes('instrument')) console.log(`  ${id}: ${t.en}`);
}
console.log('\nAll IDs containing "electric_motor":');
for (const [id, t] of Object.entries(termById)) {
  if (id.includes('electric_motor')) console.log(`  ${id}: ${t.en}`);
}
console.log('\nAll IDs containing "accelerator":');
for (const [id, t] of Object.entries(termById)) {
  if (id.includes('accelerator')) console.log(`  ${id}: ${t.en}`);
}
console.log('\nAll IDs containing "ecu" or "control_unit":');
for (const [id, t] of Object.entries(termById)) {
  if (id.includes('ecu') || id.includes('control_unit')) console.log(`  ${id}: ${t.en}`);
}
