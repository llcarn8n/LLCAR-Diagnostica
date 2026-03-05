const fs = require('fs');
const path = require('path');
const glossary = JSON.parse(fs.readFileSync(
  path.join(__dirname, '..', 'глоссарий 3d компонентов/глоссарий 3d компонентов/automotive-glossary-3d-components.json'), 'utf8'
));

// Search Russian terms
const ruSearchTerms = [
  'рычаг', 'подрулевой', 'номерной', 'номер', 'лепесток',
  'ароматизатор', 'зарядк', 'переключатель', 'значок', 'эмблема', 'надпись',
  'зеркало', 'стабилизатор', 'control arm'
];

for (const q of ruSearchTerms) {
  const ql = q.toLowerCase();
  let found = false;
  for (const [catId, cat] of Object.entries(glossary.categories)) {
    for (const term of cat.terms) {
      if (term.ru.toLowerCase().includes(ql) || term.en.toLowerCase().includes(ql)) {
        console.log(`"${q}" -> ${catId}: EN: ${term.en} | RU: ${term.ru}`);
        found = true;
      }
    }
  }
  if (found === false) console.log(`"${q}" -> NOT FOUND`);
  console.log('---');
}
