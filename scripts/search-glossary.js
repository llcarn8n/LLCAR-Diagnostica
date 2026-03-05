const fs = require('fs');
const path = require('path');
const glossary = JSON.parse(fs.readFileSync(
  path.join(__dirname, '..', 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'
));

const searchTerms = [
  'upper control arm', 'lower control arm', 'paddle shifter', 'number plate',
  'licence plate frame', 'charging socket', 'charge port', 'charge inlet',
  'stalk switch', 'combination switch', 'badge', 'emblem', 'lettering',
  'air freshener', 'licence-plate', 'licence plate bracket',
  'mirror interior', 'rearview', 'wiper stalk', 'indicator stalk'
];

for (const q of searchTerms) {
  const ql = q.toLowerCase();
  let found = false;
  for (const [catId, cat] of Object.entries(glossary.categories)) {
    for (const term of cat.terms) {
      if (term.en.toLowerCase().includes(ql)) {
        console.log(`${q} -> ${catId}: ${term.en} | ${term.ru}`);
        found = true;
      }
    }
  }
  if (found === false) console.log(`${q} -> NOT FOUND`);
}
