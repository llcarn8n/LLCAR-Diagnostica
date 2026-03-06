# Unified Topic Catalog — Li Auto KB Enrichment

**Total: 47 unified topics** (merged from 120 raw topics across 4 sources)

## Sources
| Source | File | Raw Topics |
|--------|------|------------|
| RU articles (autonews, drom, getcar, autoreview) | topics_from_articles_ru.json | 35 |
| Telegram (@lixiangautorussia) | topics_from_telegram.json | 25 |
| EN articles (cnevpost, carnewschina, carscoops) | topics_from_articles_en.json | 25 |
| New scraped (kursiv, autoplt, 110km, lixiang_sto) | topics_from_new_scraped.json | 35 |

## Confidence Distribution
- **CONFIRMED**: 8
- **HIGH**: 7
- **MEDIUM**: 21
- **LOW**: 11

## By Category
- **owner_experience**: 14
- **troubleshooting**: 7
- **safety**: 6
- **technology**: 5
- **maintenance**: 4
- **market**: 4
- **specs**: 4
- **news**: 1
- **legal**: 1
- **comparison**: 1

---

## All Topics

### TROUBLESHOOTING

#### unified_adas_autopilot: Лидар и ADAS — повреждения, фантомное торможение, калибровка
*LiDAR and ADAS — Damage, Phantom Braking, Calibration*

- **Confidence**: CONFIRMED
- **Models**: L6, L7, L8, L9, i8
- **Systems**: adas, battery, drivetrain, infotainment, interior
- **Layer**: adas
- **Season**: winter
- **Cost**: 40,000+ руб (калибровка)
- **Sources**: 9 URLs from en_articles, ru_articles, telegram
- **Merged from**: topic_ru_014, topic_ru_018, topic_tg_021, topic_en_007, topic_en_019

**RU**: AutoChina blog представляет детальные обзоры всей линейки Li Auto: L7 как «умный электрический SUV из Китая» (15.7" OLED, 330 кВт, Autopilot 3.0), L8 (до 1315 км запаса хода, рецензент проехал 4000 км), L6 (компактный SUV, доступная альтернатива), Li i8 (первый электрический SUV, от 339,800). Все модели объединяет философия: электрический комфорт + гибридная надёжность.

**EN**: Detailed trim comparison. L9 Pro: ~400K CNY. L7/L8 Max now with dual-chamber air suspension and 52.3 kWh battery. Multimedia processor (Snapdragon) same on Pro/Max — screens don't differ in speed. Autopilot chip (Nvidia Orin): Pro — 1 chip, Max — 2 chips. Orin affects camera processing and ADAS, not interface. Max justified for future 'heavy' ADAS features.

**Key facts:**
- Калибровка лидара — от 40,000 руб
- 2025 рестайл: лидар на 55% меньше, энергоэффективность +55%
- Фантомное торможение: AEB путает билборды с реальными объектами
- NOA нестабилен — руль рыскает, не видит разметку
- Защита лидара (STUDIO27) — рекомендуется
- Рейтинг drom.ru: 9.1/10
- После ДТП с подушками безопасности — авто полная блокировка
- Генератор не успевает заряжать при 130+ км/ч
- Визуализация ADAS — точность распознавания >95%
- Автопилот «тупой» — перестраивается в пробке без причины

**Sources:**
- https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
- https://kz.kursiv.media/2025-06-09/kmlz-li-auto-problems/
- https://www.drom.ru/reviews/li/l9/5kopeek/
- https://t.me/lixiangautorussia/1699218
- https://t.me/lixiangautorussia/4
- https://carnewschina.com/2023/01/27/li-l9-user-claimed-driving-assistance-system-failed-resulting-in-an-accident
- https://autochina.blog/li-auto-l8-2024-review-specs-range-hybrid-suv/
- https://autochina.blog/li-l7-electric-suv-review-premium-chinese-ev/

---

#### unified_timing_chain: Двигатель 1.5T L2E15M — ресурс, масложор, цепь ГРМ
*1.5T L2E15M Engine — Longevity, Oil Consumption, Timing Chain*

- **Confidence**: CONFIRMED
- **Models**: L7, L8, L9
- **Systems**: engine
- **Layer**: engine
- **Season**: all
- **Sources**: 9 URLs from en_articles, new_scraped, ru_articles, telegram
- **Merged from**: topic_ru_009, topic_en_015, topic_new_009, topic_tg_004

**RU**: Жаркие споры о марке бензина. Двигатель 1.5T (BMW-наследник) имеет степень сжатия 12.5-15:1, что формально требует высокооктанового топлива. Одни считают что нужен 98/100, другие — что 95 достаточно, так как ДВС работает только как генератор на стабильных оборотах. Клуб рекомендует следовать указаниям производителя. Важно: у Lixiang мотор не крутит колеса — нагрузка ниже стандартной.

**EN**: Russian company Faker Autogroup bought a Li L9 aiming for 1 million km. The 1.5T engine died at 307,000 km due to timing chain tensioner failure that destroyed the engine. This confirms the consensus issue with the 1.5T timing chain (issue_h7). InsideEVs noted: 'old-school tech let it down' — impressive electric components, but the conventional ICE failed.

**Key facts:**
- Архитектура Prince (BMW/PSA), универсальный сканер его видит
- Цепь ГРМ Morse-типа — инспекция каждые 100-120 тыс. км
- Документированный отказ при 307,000 км (тест Faker Autogroup)
- ~4 ревизии поршней — текущие серийные исправлены
- Масло менять каждые 7-8 тыс. км (не 10-12 тыс.)
- 307,000 km (190,000 miles) — timing chain tensioner failure
- Engine completely destroyed — not repairable
- Faker Autogroup is in Russia, works on gray-imported Chinese EVs
- Confirms consensus issue_h7: 1.5T timing chain stretch/failure
- InsideEVs: 'Chinese cars are exciting, but long-term durability is a question mark'

**Sources:**
- https://kz.kursiv.media/2026-02-16/rmnm-motor-lixiang-raskritikovali-iz-za-nenadezhnoy-konstrukcii-cepi-grm/
- https://insideevs.com/news/775394/li-auto-l9-russia-erev/
- https://carexpo.ru/2025/12/08/li-auto-l9-proshel-v-rf-367-tysyach-km-i-slomalsya-skolko-stoit-remont/
- https://autoplt.ru/dvigateli-lixiang-l7-l8-l9/
- https://kz.kursiv.media/2026-02-16/rmnm-motor-lixiang-raskritikovali-iz-za-nenadezhnoy-konstrukcii-cepi-grm
- https://t.me/lixiangautorussia/1509373
- https://t.me/lixiangautorussia/1386728
- https://t.me/lixiangautorussia/1215327

---

#### unified_unique_topic_ru_025: Батарея зимой — потеря запаса хода, предварительный прогрев
*Battery in Winter — Range Loss, Preconditioning*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: battery
- **Layer**: battery
- **Season**: winter
- **Sources**: 2 URLs from ru_articles
- **Merged from**: topic_ru_025

**RU**: Батарея теряет 15-20% ёмкости на холоде. При -30 обогреватель потребляет 8-9 кВт, даже стоя заряд заканчивается за ~3 часа. Зарядка при -20 требует 30 мин прогрева. L7 (40 кВтч) — ~100 км зимой, L9 (52.3 кВтч) — ~120 км (vs 180 км летом). Рекомендации: прогрев перед поездкой, заряд выше 20%, гаражное хранение.

**EN**: Battery loses 15-20% capacity in cold. At -30C heater draws 8-9 kW, even standing still charge lasts ~3 hours. Charging at -20C needs 30 min warmup. L7 (40 kWh) ~100 km winter, L9 (52.3 kWh) ~120 km (vs 180 km summer). Recommendations: precondition before driving, keep above 20%, garage parking.

**Key facts:**
- L7 батарея 40 кВтч: ~100 км зимой
- L9 батарея 52.3 кВтч: ~120 км зимой (180 км летом)
- При -30: обогреватель 8-9 кВт, заряд на 3 часа стоянки
- Зарядка при -20: нужно 30 мин прогрева перед началом
- Запас хода зимой падает ~2x относительно лета

**Sources:**
- https://www.drom.ru/reviews/li/l7/5kopeek/
- https://www.drom.ru/reviews/li/l9/5kopeek/

---

#### unified_air_filter: Воздушный фильтр забивается снегом — остановка двигателя-генератора в метель
*Air Filter Clogs with Snow — Engine-Generator Stalls in Blizzard*

- **Confidence**: LOW
- **Models**: L7, L9
- **Systems**: engine
- **Layer**: engine
- **Season**: winter
- **Sources**: 1 URLs from new_scraped
- **Merged from**: topic_new_018

**RU**: В сильную метель снег забивает патрубки и воздушный фильтр ДВС-генератора. Мотор теряет мощность и перестаёт заряжать батарею. Фильтр превращается в ледяную пробку. Программного решения нет. Требуется ручная разборка и очистка. Аналогичная проблема у BMW X5/X6/X7.

**EN**: In heavy blizzards, snow clogs the engine air intake ducts and filter. The ICE generator loses power and stops charging the battery. Filter becomes an ice plug. No software fix exists. Manual disassembly and cleaning required. Same issue affects BMW X5/X6/X7.

**Key facts:**
- Snow enters air filter in heavy blizzard conditions
- ICE stops → battery not charging → full stop risk
- No OTA/software fix possible
- Manual filter disassembly required roadside
- Same issue on BMW X5/X6/X7 — not brand-specific
- First signs: sudden power loss, charge level dropping

**Sources:**
- https://kz.kursiv.media/2026-01-27/shkv-vladelcy-lixiang-zhaluyutsya-na-ostanovku-gibridov-v-snegopad

---

#### unified_lower_control_arm: Замена передних рычагов L9 — износ сайлентблоков при 58 тыс. км
*Front Control Arm Replacement L9 — Bushing Wear at 58K km*

- **Confidence**: LOW
- **Models**: L9
- **Systems**: suspension
- **Layer**: chassis
- **Season**: all
- **Sources**: 1 URLs from new_scraped
- **Merged from**: topic_new_007

**RU**: Lixiang L9 2024 года с пробегом 58 тыс. км потребовал замену передних рычагов подвески. Двухрычажная передняя и пятирычажная задняя подвеска Magic Carpet адаптивная, но сайлентблоки рычагов изнашиваются при активной эксплуатации. Нарушается геометрия подвески, ухудшается управляемость, ускоряется износ шин.

**EN**: A 2024 Lixiang L9 with 58K km mileage required front control arm replacement. The dual-wishbone front and five-link rear Magic Carpet suspension is adaptive, but arm bushings wear under active driving. Suspension geometry is disrupted, handling worsens, and tire wear accelerates.

**Key facts:**
- 2024 L9 at 58,000 km needed front arm replacement
- Front: double-wishbone, Rear: 5-link multilink
- Magic Carpet adaptive suspension with dual-chamber air springs
- Bushings lose elasticity from frequent damping changes
- Regular inspection recommended for early detection

**Sources:**
- https://lixiang-sto.ru/blog/zamena-perednikh-rychagov-na-lixiang-l9/

---

#### unified_unique_topic_ru_034: Утечка хладагента — угроза батарее летом
*Refrigerant Leak — Battery Threat in Summer*

- **Confidence**: LOW
- **Models**: L7, L8, L9
- **Systems**: hvac, battery
- **Layer**: hvac
- **Season**: summer
- **Cost**: 20,000+ руб
- **Sources**: 1 URLs from ru_articles
- **Merged from**: topic_ru_034

**RU**: Хладагент исчезает из системы кондиционирования. Слабое место — трубки в районе заднего левого колеса. Критично: кондиционер охлаждает не только салон, но и ВВ батарею. Без охлаждения возможен перегрев и возгорание. Ремонт климат-контроля — от 20,000 руб.

**EN**: Refrigerant disappears from AC system. Weak point — lines near rear left wheel. Critical: AC cools not only the cabin but also the HV battery. Without cooling, overheating and fire risk. AC repair from 20,000 RUB.

**Key facts:**
- Слабое место: трубки у заднего левого колеса
- Кондиционер охлаждает ВВ батарею — критически важно
- Ремонт: от 20,000 руб
- Проявляется после первой зимы

**Sources:**
- https://www.gazeta.ru/auto/news/2025/02/16/25100204.shtml

---

#### unified_wptc_heater: Ремонт отопителя Lixiang L7 — неисправность WPTC в EV-режиме
*Heater Repair L7 — WPTC Failure in EV Mode*

- **Confidence**: LOW
- **Models**: L7
- **Systems**: battery, hvac
- **Layer**: hvac
- **Season**: winter
- **Sources**: 1 URLs from new_scraped
- **Merged from**: topic_new_005

**RU**: Гибриды Lixiang используют двухконтурную систему отопления: тепло ДВС или высоковольтный нагреватель WPTC. При выходе WPTC из строя салон не обогревается в EV-режиме, а батарея теряет оптимальную температуру. Диагностика показывает блок WPTC недоступным. Замена выполняется с демонтажом элементов передней панели.

**EN**: Lixiang hybrids use dual-loop heating: ICE heat or high-voltage WPTC heater. When WPTC fails, cabin heating is lost in EV mode and battery loses optimal temperature. Diagnostics show WPTC block as unavailable. Replacement requires partial front panel disassembly.

**Key facts:**
- WPTC = Water PTC heater, runs on HV battery power
- Dual function: cabin heating + battery temperature management
- Failure = no heat in EV mode + battery degradation risk
- Error displayed on multimedia screen
- Repair requires LDM diagnostics

**Sources:**
- https://lixiang-sto.ru/blog/remont-otopitelia-lixiang/

---

### SAFETY

#### unified_air_suspension: Li L9 — подвеска тест-автомобиля сломалась перед стартом продаж
*Li L9 — Test Car Suspension Breakage Before Sales Start*

- **Confidence**: CONFIRMED
- **Models**: L6, L7, L8, L9, MEGA
- **Systems**: battery, body, brakes, chassis, cooling, electronics, engine, sensors, steering, suspension
- **Layer**: suspension
- **Season**: all
- **Sources**: 28 URLs from en_articles, new_scraped, ru_articles, telegram
- **Merged from**: topic_en_006, topic_en_010, topic_ru_001, topic_ru_004, topic_ru_008, topic_ru_020, topic_ru_030, topic_ru_032, topic_new_003, topic_new_011, topic_new_015, topic_new_024, topic_ru_029, topic_ru_035, topic_tg_005

**RU**: Перед началом продаж L9 в июле 2022 у тестового автомобиля провалилось левое переднее колесо (отказ пневмоподвески) при проезде ямы 20 см на скорости 90 км/ч. Li Auto заявила, что использовалась пилотная версия подушки, производственная — в 2.5 раза прочнее. Ранее в 2020 Li ONE отозвали 10,469 штук за проблемы с передней подвеской, и Li Auto извинилась за попытку назвать отзыв 'апгрейдом'.

**EN**: Winter operation is the key concern for Russian owners. Includes: filter on air suspension compressor, -30C washer fluid (not -10!), silicone on handles, lidar protection, grille shutter cleaning, 12V battery check, running board anti-corrosion, oil change interval reduction to 7-8K km. ICE air filter clogs with snow in blizzards within hours, potentially immobilizing the vehicle.

**Key facts:**
- L9 test car suspension failed at 90 km/h over 20cm pothole in Chongqing
- Pilot-version cushion ring used in some test cars due to supply issues
- Production version claimed 2.5x stronger than pilot version
- 2020: 10,469 Li ONE recalled for front suspension design flaw
- Li Auto initially called recall a 'free upgrade' — drew public criticism, then apologized
- Former Geely Research Institute director questioned the 90km/h pothole explanation
- Apr 2024: prices cut up to 30,000 yuan across L7/L8/L9
- Trim names restructured: Air/Pro/Max -> Pro/Max/Ultra
- New L7 Air and L8 Air without air suspension — 18,000 yuan cheaper
- L9 Pro launched without LiDAR at 429,800 (30K less than Max)

**Sources:**
- https://cnevpost.com/2020/08/16/li-auto-denies-quality-issues-caused-axle-breakage/
- https://cnevpost.com/2020/11/06/li-auto-recalls-10469-li-ones-after-criticism-of-previous-upgrade-move/
- https://cnevpost.com/2022/07/18/li-auto-in-spotlight-for-li-l9-test-car-suspension-breakage/
- https://carnewschina.com/2024/04/22/li-auto-slashed-prices-by-4200-usd-to-intensify-competition-in-china
- https://cnevpost.com/2023/08/03/li-auto-launches-li-l9-pro-no-lidar-cheaper/
- https://cnevpost.com/2026/02/27/li-auto-rolls-out-profit-sharing-for-store-managers-revive-sales/
- https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
- https://getcar.ru/en/blog/problemy-pnevmopodveski-lixiang-l9/

---

#### unified_mega_recall: Li MEGA — провал запуска, отзыв батарей, пожар и финансовые потери
*Li MEGA — Failed Launch, Battery Recall, Fire Incident and Financial Fallout*

- **Confidence**: HIGH
- **Models**: L6, L7, L8, L9, MEGA
- **Systems**: battery, cooling, interior, suspension
- **Layer**: battery
- **Season**: all
- **Sources**: 13 URLs from en_articles, new_scraped
- **Merged from**: topic_en_001, topic_en_021, topic_new_001, topic_new_034, topic_en_013, topic_new_023, topic_new_031

**RU**: Li MEGA — первый полностью электрический автомобиль Li Auto — стал крупнейшим провалом компании. Несмотря на впечатляющие характеристики (710 км, 5C зарядка, Cd 0.215), модель не оправдала ожиданий: целевые продажи 8000/мес не были достигнуты, компания дважды снижала годовой план. В октябре 2025 произошёл пожар, после чего отозвано 11,411 единиц из-за коррозии в охлаждающих контурах. Убытки от отзыва ~1.14 млрд юаней, уволены сотрудники. Class-action иск в США за завышение спроса.

**EN**: Li MEGA — Li Auto's first BEV — became the company's biggest failure. Despite impressive specs (710 km range, 5C charging, 0.215 Cd drag), the model fell far short of 8,000/month sales targets. Li Auto twice lowered annual goals. In Oct 2025, a fire incident led to recall of 11,411 units due to coolant corrosion in battery and motor controller circuits. Recall cost est. RMB 1.14B, employees fired. A US class-action lawsuit alleges inflated demand projections.

**Key facts:**
- 10,000 pre-orders in 1h42m at Guangzhou Auto Show debut (Nov 2023)
- Launch price 559,800 yuan ($77,800), later cut to 529,800
- Annual sales target cut twice: 800K -> 560-640K -> 480K (2024)
- Fire incident Oct 23, 2025 in Shanghai — vehicle engulfed in seconds
- 11,411 units recalled (half of all delivered) — coolant corrosion in battery
- Recall cost ~RMB 1.14 billion, multiple employees fired
- US class-action lawsuit for securities fraud (inflated Mega demand)
- 2026 subsidies: 12% of NEV price (capped at 20K yuan) for scrapping
- RMB 62.5 billion allocated from ultra-long government bonds
- BYD Denza Z9GT: 1,036 km battery range — world record

**Sources:**
- https://carnewschina.com/2024/03/01/li-auto-mega-enters-chinese-market-with-a-starting-price-of-77800-usd
- https://carnewschina.com/2024/06/05/li-auto-lowers-annual-sales-goal-for-second-time-as-things-didnt-go-as-planned
- https://www.carscoops.com/2024/05/li-auto-sued-in-the-u-s-for-inflating-demand-for-mega-ev
- https://cnevpost.com/2025/10/31/li-auto-recalls-mega-mpvs-battery-risk/
- https://cnevpost.com/2025/11/14/li-auto-fires-employees-mega-recall/
- https://cnevpost.com/2025/12/30/china-to-continue-trade-in-subsidies-2026-auto-consumption/
- https://cnevpost.com/2026/02/27/byd-denza-teases-updated-z9gt-1036-km-battery-range/
- https://cnevpost.com/2026/03/02/xpeng-launches-updated-x9-electric-mpv-boost-premium-sales/

---

#### unified_door_handle: Безопасность электромобилей в Китае — голосовые команды, двери, отзывы
*EV Safety in China — Voice Command Glitches, Door Handles, Recalls*

- **Confidence**: MEDIUM
- **Models**: 
- **Systems**: electronics
- **Layer**: electronics
- **Season**: all
- **Sources**: 2 URLs from en_articles
- **Merged from**: topic_en_020

**RU**: Серия инцидентов безопасности на китайском рынке EV: голосовая команда «выключить все огни» отключила фары Lynk & Co Z20 во время движения (то же у Zeekr, Deepal). Xiaomi SU7: скрытые дверные ручки не открылись после аварии из-за отключения 12V — водитель погиб. Призывы к отзыву 370K SU7. Mercedes отозвал 19,481 EV из-за риска пожара батарей.

**EN**: Series of safety incidents in China's EV market: voice command 'turn off all lights' disabled Lynk & Co Z20 headlights while driving (same issue found in Zeekr, Deepal). Xiaomi SU7: hidden door handles failed to open after crash due to 12V shutdown — driver died. Calls to recall 370K SU7s. Mercedes recalled 19,481 EVs for battery fire risk.

**Key facts:**
- Lynk & Co Z20: 'turn off all reading lights' accidentally killed headlights
- Multiple brands affected: Zeekr, Deepal bypass safety with 'turn off all lights'
- Xiaomi SU7: fatal crash — electronic door handles disabled after power failure
- Yicai (top financial media) publicly called for 370K SU7 recall
- Mercedes recalled 19,481 EQA/EQB for battery fire risk in China
- Nio recalled 246,229 EVs for software-related dashboard blackouts

**Sources:**
- https://cnevpost.com/2026/02/27/voice-command-glitch-plunging-evs-into-darkness/
- https://cnevpost.com/2026/02/27/xiaomi-pressured-to-recall-370000-evs-door-handle-safety-hazard/

---

#### unified_spontaneous_combustion: Li ONE — пожар в салоне за 9 секунд, исключён дефект авто
*Li ONE — Cabin Fire in 9 Seconds, Vehicle Quality Issue Ruled Out*

- **Confidence**: MEDIUM
- **Models**: L7, Li ONE
- **Systems**: battery, electronics, ev
- **Layer**: battery
- **Season**: all
- **Sources**: 2 URLs from en_articles, ru_articles
- **Merged from**: topic_en_008, topic_ru_028

**RU**: Несколько владельцев на drom.ru жалуются на постоянные головные боли от езды на Li L7, связывая их с «сильным электромагнитным излучением» батареи и генератора. Утверждается, что «экранирование открыто, нет защитного слоя». Также упоминаются случаи самовозгорания в Дагестане, Краснодаре, Ставрополе. Эти утверждения не подтверждены независимыми источниками.

**EN**: Several owners on drom.ru complain of constant headaches from driving Li L7, attributing them to 'strong electromagnetic radiation' from battery and generator. Claimed 'shielding is open, no protective layer'. Also mentions spontaneous combustion cases in Dagestan, Krasnodar, Stavropol. These claims are not confirmed by independent sources.

**Key facts:**
- Fire on Aug 1, 2022 on Chengdu-Chongqing highway
- Cabin temperature surged from 32.5°C to 85°C in 2 seconds
- PM 2.5 inside car spiked, suggesting internal combustion source
- Battery pack intact, no deformation, foam cushion unburned
- Fuel tank intact, no leakage detected
- Li Auto ruled out vehicle quality issue — suggested flammable items
- Несколько жалоб на головные боли от ЭМИ (не подтверждено)
- Утверждения о самовозгорании (не подтверждено независимо)
- Один владелец продал авто из-за головных болей
- Экранирование батареи — спорная тема

**Sources:**
- https://cnevpost.com/2022/08/05/li-auto-says-recent-li-one-fire-not-caused-by-vehicle-quality-issue/
- https://www.drom.ru/reviews/li/l7/5kopeek/

---

#### unified_unique_topic_ru_021: Безопасность — ДТП, блокировка после срабатывания подушек, формальдегид
*Safety — Accidents, Airbag Deployment Lockout, Formaldehyde*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: body, electronics
- **Layer**: body
- **Season**: all
- **Sources**: 2 URLs from ru_articles
- **Merged from**: topic_ru_021

**RU**: После ДТП с срабатыванием подушек безопасности автомобиль полностью блокируется — «кирпичится». В России оживить такое авто пока не научились. Один владелец жалуется на постоянные головные боли от формальдегида из салонных материалов. Лобовое стекло «аномально тонкое» — может пробить жук или шмель на трассе.

**EN**: After accident with airbag deployment, the vehicle completely locks up — becomes a 'brick'. In Russia no one has learned to revive such vehicles yet. One owner complains about constant headaches from formaldehyde off-gassing from interior materials. Windshield is 'anomalously thin' — a bug can penetrate it at highway speed.

**Key facts:**
- После ДТП с подушками — полная блокировка авто
- Разблокировка невозможна в России — нужен дилер в КНР
- Жалобы на формальдегид из салонных материалов
- Лобовое стекло очень тонкое — уязвимо к камням
- Прикуривание 12V может убить BMS (50,000 руб)

**Sources:**
- https://www.drom.ru/reviews/li/l7/5kopeek/
- https://www.drom.ru/reviews/li/l9/5kopeek/

---

#### unified_unique_topic_new_030: Голосовое управление — уязвимость китайских EV (выключение фар командой)
*Voice Control Vulnerability — Chinese EVs Headlights Off by Voice Command*

- **Confidence**: LOW
- **Models**: 
- **Systems**: infotainment
- **Layer**: infotainment
- **Season**: all
- **Sources**: 1 URLs from new_scraped
- **Merged from**: topic_new_030

**RU**: Lynk & Co Z20: голосовая команда «выключи все лампочки для чтения» отключила фары на ходу. Автомобиль врезался в барьер. Тесты Zeekr и Deepal показали: команда «выключи все огни» обходит защиту. Проблема общая для EV без физических переключателей фар.

**EN**: Lynk & Co Z20: voice command 'turn off all reading lights' deactivated headlights while driving. Car hit a barrier. Tests on Zeekr and Deepal showed: 'turn off all lights' bypasses safety restrictions. Industry-wide issue for EVs without physical headlight switches.

**Key facts:**
- Lynk & Co Z20: headlights turned off by ambiguous voice command
- No physical headlight switch — driver helpless
- Zeekr, Deepal also vulnerable to 'turn off all lights'
- Direct 'turn off headlights' blocked, but broad commands bypass
- Lynk & Co pushed emergency OTA: headlights can only be manually turned off

**Sources:**
- https://cnevpost.com/2026/02/27/voice-command-glitch-plunging-evs-into-darkness/

---

### OWNER_EXPERIENCE

#### unified_multimedia_ota: Режим топлива / электро / гибрид — алгоритмы работы ДВС
*Fuel / Electric / Hybrid Mode — ICE Operating Algorithms*

- **Confidence**: CONFIRMED
- **Models**: L6, L7, L9
- **Systems**: battery, brakes, electrical, electronics, engine, ev, general, infotainment, interior, suspension
- **Layer**: engine
- **Season**: all
- **Sources**: 25 URLs from new_scraped, ru_articles, telegram
- **Merged from**: topic_tg_003, topic_tg_008, topic_new_004, topic_new_026, topic_ru_003, topic_ru_016, topic_tg_013, topic_tg_022

**RU**: Множество вопросов и обсуждений о том, когда и как машина сама включает/выключает ДВС. В режиме Fuel машина может не заводить мотор при высоком заряде (>80-95%). В электро режиме ДВС включается зимой при низком заряде (~15%) или для прогрева масла. Прошивка 8.0 и 8.3 изменили алгоритмы — поведение стало менее предсказуемым. Ключевое: ДВС работает только как генератор (2500-3800 об/мин), не крутит колеса. На трассе при 130+ км/ч генератор может не успевать заряжать, идет разряд батареи.

**EN**: Extensive discussions on ICE start/stop algorithms across driving modes. In Fuel mode, ICE may not start above 80-95% charge. In Electric mode, ICE starts in winter at ~15% charge or for oil warming. Firmware 8.0/8.3 changed algorithms unpredictably. Key fact: ICE is a generator only (2500-3800 RPM), never drives wheels. At 130+ km/h on highway, generator cannot keep up — battery discharges.

**Key facts:**
- ДВС работает в диапазоне 2500-3800 об/мин как генератор
- Турбина дует максимум 0.66 бара
- При скорости выше 150 км/ч генератор не поддерживает заряд, идет активный разряд
- Максимальная скорость ограничена 180 км/ч
- В гибридном режиме мотор заводится при заряде ниже ~80%
- Холодный запуск ДВС на трассе: прогрев на 1200 об/мин, потом рабочий режим
- 12V аккумулятор литиевый — НЕЛЬЗЯ прикуривать!
- При прикуривании срабатывает защита BMS — может быть необратимо
- При полном разряде 12V авто полностью блокируется
- Гарантия на 12V: 3 года или 80,000 км

**Sources:**
- https://t.me/lixiangautorussia/1530022
- https://t.me/lixiangautorussia/1479309
- https://t.me/lixiangautorussia/1151387
- https://t.me/lixiangautorussia/1108373
- https://t.me/lixiangautorussia/1530029
- https://t.me/lixiangautorussia/1690064
- https://t.me/lixiangautorussia/1667477
- https://t.me/lixiangautorussia/1675470

---

#### unified_maintenance: Техническое обслуживание — регламент, стоимость, рекомендации по маслам и фильтрам
*Maintenance — Schedule, Costs, Oil and Filter Recommendations*

- **Confidence**: HIGH
- **Models**: L6, L7, L8, L9
- **Systems**: drivetrain, engine
- **Layer**: engine
- **Season**: all
- **Sources**: 7 URLs from new_scraped, telegram
- **Merged from**: topic_tg_001, topic_new_008

**RU**: Владельцы активно обсуждают стоимость и состав ТО. Нулевое ТО (масло + фильтр) стоит ~11,575-13,000 руб (Studio 27). ТО-1 (масло, воздушный, салонный фильтр, диагностика) — 22,200 руб. Масло в ДВС 3.7л, рекомендуется 0W-30 или 5W-30 (Motul 8100, ZIC TOP, Polymerium, Mobil 1 ESP). Замена масла в редукторах по регламенту — раз в 80,000 км или 4 года (передний), задний не обслуживается. Клуб советует не торопиться с заменой масла в редукторах раньше срока. Свечи менять на 20-30 тыс. км работы ДВС.

**EN**: Owners actively discuss maintenance costs and procedures. Zero-mileage service (oil + filter) costs ~11,575-13,000 RUB. First service (oil, air, cabin filters, diagnostics) — 22,200 RUB. Engine oil capacity 3.7L, 0W-30 or 5W-30 recommended (Motul 8100, ZIC TOP, Polymerium, Mobil 1 ESP). Reducer oil change per OEM schedule — every 80,000 km or 4 years (front only), rear is non-serviceable. Club advises against premature reducer oil changes. Spark plugs at 20-30K km of ICE operation.

**Key facts:**
- Нулевое ТО: масло + фильтр = 11,575 руб + 230 руб кольцо + 1,100 руб защита
- ТО-1: 22,200 руб (Studio 27)
- ТО в неофициальных сервисах: 9,000-14,000 руб
- Масло ДВС: 3.7л, вязкость 0W-30 или 5W-30
- Редуктор передний: замена масла каждые 80,000 км или 4 года
- Задний редуктор не обслуживается
- Свечи: замена каждые 20-30 тыс. км работы ДВС
- Engine oil: 3.7L, API SP or ACEA C2 0W-30
- Front reducer: Wei Rui TZ180XS, rear 80kW vs front 65kW
- Small TO: oil + filter; Big TO: + cabin filter + air filter

**Sources:**
- https://t.me/lixiangautorussia/1712989
- https://t.me/lixiangautorussia/1712929
- https://t.me/lixiangautorussia/1715460
- https://t.me/lixiangautorussia/1701007
- https://t.me/lixiangautorussia/918789
- https://autoplt.ru/reglament-to-lixiang-l7-l8-l9/
- https://autoplt.ru/maslo-v-dvigatel-i-reduktor-korobku-lixiang/

---

#### unified_steering: Высоковольтная батарея — зарядка, деградация, LFP рекомендации
*HV Battery — Charging, Degradation, LFP Best Practices*

- **Confidence**: MEDIUM
- **Models**: L6, L7, L9
- **Systems**: battery
- **Layer**: ev
- **Season**: all
- **Sources**: 4 URLs from telegram
- **Merged from**: topic_tg_009

**RU**: Обширные обсуждения правил эксплуатации батареи. LFP (L6 Pro/Max): заряжать в диапазоне 20-80% для повседневного использования, раз в 1-2 месяца заряжать до 100% для калибровки BMS. Не хранить на 0-10%. Быстрая зарядка — не более 80%. Lixiang заряжается только от одной фазы (не 3-фазная). При езде в режиме fuel батарея 'колбасится' в 90-95% — это изнашивает последние 5 ячеек быстрее остальных.

**EN**: Extensive battery management discussions. LFP (L6 Pro/Max): charge 20-80% daily, charge to 100% monthly for BMS calibration. Don't store at 0-10%. Fast charging — up to 80%. Lixiang charges single-phase only (not 3-phase). Driving in fuel mode keeps battery oscillating at 90-95% — this wears last 5 cells faster than others, potentially causing imbalance.

**Key facts:**
- LFP батареи: оптимальный диапазон 20-80%, полная зарядка раз в 1-2 месяца для калибровки
- Быстрая зарядка — не более 80%
- Lixiang заряжается только от одной фазы
- Режим Fuel: батарея болтается в 90-95%, износ последних ячеек
- При -21°C и 14% заряда не оставлять на ночь без подзарядки
- 3 месяца хранения без обслуживания батареи — потеря гарантии

**Sources:**
- https://t.me/lixiangautorussia/1173038
- https://t.me/lixiangautorussia/1364002
- https://t.me/lixiangautorussia/1337291
- https://t.me/lixiangautorussia/9

---

#### unified_unique_topic_new_014: Все минусы Lixiang L7 по отзывам владельцев
*All Lixiang L7 Downsides from Owner Reviews*

- **Confidence**: MEDIUM
- **Models**: L7
- **Systems**: infotainment, body, suspension
- **Layer**: interior
- **Season**: all
- **Sources**: 2 URLs from new_scraped
- **Merged from**: topic_new_014

**RU**: Собранные минусы L7: лёгкий «оторванный» руль, слабая ремонтопригодность (мало сервисов в России), платформа завязана на кодировке компонентов к VIN, мелкие эргономические просчёты, перебор с электронными опциями. Плюсов больше, но идеальной машину не назовет даже китаец.

**EN**: Compiled L7 downsides: light 'disconnected' steering, limited repairability (few authorized services in Russia), platform component-to-VIN coding dependency, minor ergonomic issues, excessive electronic options. Pros outweigh cons, but even a Chinese owner wouldn't call it perfect.

**Key facts:**
- Steering feels 'disconnected from wheels'
- Very few service centers outside Moscow/SPB
- All components coded to specific VIN — complicates third-party repair
- Multimedia overwhelming in first firmware versions
- No guarantee any Russian service can actually fix it

**Sources:**
- https://autoplt.ru/vse-minusy-v-otzyvah-vladelczev-lixiang-l7/
- https://kz.kursiv.media/2026-01-06/rmnm-kazakhstanets-nazval-lixiang-l7-pro-novoy-camry-no-s-nim-ne-soglasilis

---

#### unified_unique_topic_ru_005: Расход топлива — реальный vs заявленный, оптимизация
*Fuel Consumption — Real-World vs Advertised, Optimization*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: engine
- **Layer**: engine
- **Season**: all
- **Sources**: 3 URLs from ru_articles
- **Merged from**: topic_ru_005

**RU**: Реальный расход на трассе при 125 км/ч — 11 л/100 км (заявлено 5.9 по CLTC). Город зимой — 10-12 л/100 км. Максимальный пробег ~700 км (заявлено 1,315). На 37,000 км расход вырастает до 12 л. AI-92 снижает пробег на 20%. Рекомендуют RON-100, держать батарею заряженной, в городе значительно экономичнее (5-7 л/100 км).

**EN**: Real highway consumption at 125 km/h is 11 L/100km (advertised 5.9 CLTC). City winter 10-12 L/100km. Max range ~700 km (advertised 1,315). At 37K km consumption rises to 12L. AI-92 drops range by 20%. Recommended: RON-100, keep battery charged, city driving much more efficient (5-7 L/100km).

**Key facts:**
- Трасса 125 км/ч: 11 л/100 км реально vs 5.9 CLTC
- Город зимой: 10-12 л/100 км
- RON-100 — рекомендуемое топливо для ресурса двигателя
- Город EV-режим: 5-7 л/100 км — значительно экономичнее
- При 37,000 км пробега расход растёт до 12 л/100 км

**Sources:**
- https://www.drom.ru/reviews/li/l7/5kopeek/
- https://www.drom.ru/reviews/li/l9/5kopeek/
- https://getcar.ru/blog/lixiang-l9-ne-edet/

---

#### unified_unique_topic_ru_024: Комфорт и салон — L7/L9 как семейный автомобиль
*Comfort and Interior — L7/L9 as a Family Vehicle*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: interior
- **Layer**: interior
- **Season**: all
- **Sources**: 2 URLs from ru_articles
- **Merged from**: topic_ru_024

**RU**: Владельцы единодушно хвалят комфорт: капитанские кресла с массажем и вентиляцией, HUD с дополненной реальностью, 3-зонный климат, холодильник, потолочный экран 21.4" для пассажиров, Dolby Atmos 21 динамик. Минусы: экокожа быстро изнашивается (не Nappa), крошки попадают в щели, голосовой помощник «тупой». Электроподножки удобнее фиксированных.

**EN**: Owners unanimously praise comfort: captain seats with massage and ventilation, HUD with augmented reality, 3-zone climate, fridge, 21.4" ceiling display for passengers, Dolby Atmos 21 speakers. Cons: eco-leather wears quickly (not Nappa), crumbs get in crevices, voice assistant is 'dumb'. Electric running boards more convenient than fixed.

**Key facts:**
- Капитанские кресла с массажем, вентиляцией, подогревом
- HUD 13.3" с дополненной реальностью
- Потолочный экран 21.4" 3K для пассажиров
- Dolby Atmos 21 динамик + 4D-вибрация кресел
- 256-цветная интерьерная подсветка

**Sources:**
- https://www.drom.ru/reviews/li/l7/5kopeek/
- https://www.drom.ru/catalog/li/l9/g_2025_22507/

---

#### unified_unique_topic_ru_033: 110km.ru — независимые обзоры и тест-драйвы Li Auto
*110km.ru — Independent Reviews and Test Drives of Li Auto*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: 
- **Layer**: None
- **Season**: all
- **Sources**: 2 URLs from ru_articles
- **Merged from**: topic_ru_033

**RU**: 110km.ru публикует независимые обзоры Li Auto. 7 статей с отзывами и тест-драйвами. L9 — 8 обзоров + 2 комментария, L7 — 8 обзоров + 3 комментария. Фокус на реальном опыте эксплуатации в российских условиях: зима, метель, дороги, сервис.

**EN**: 110km.ru publishes independent Li Auto reviews. 7 articles with reviews and test drives. L9 — 8 reviews + 2 comments, L7 — 8 reviews + 3 comments. Focus on real-world experience in Russian conditions: winter, blizzards, roads, service.

**Key facts:**
- Независимые обзоры для российского рынка
- L9: 8 обзоров, L7: 8 обзоров
- Фокус на реальной эксплуатации в РФ

**Sources:**
- https://110km.ru/opinion/lixiang/l9/
- https://110km.ru/opinion/lixiang/l7/

---

#### unified_unique_topic_tg_011: Блок телематики — черные экраны, SOS-вызов, перепайка
*Telematics Unit — Black Screens, SOS Call, Re-soldering*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: infotainment, electrical
- **Layer**: infotainment
- **Season**: all
- **Sources**: 2 URLs from telegram
- **Merged from**: topic_tg_011

**RU**: Серьезная проблема: после мойки или спонтанно начинаются SOS-вызовы, затем авто полностью блокируется — черные экраны, не реагирует на ключ. Ремонт: снятие блока телематики, заказ донора, перепайка 'пары' (flash + процессор), прописка в облаке, повторный мастер-аккаунт. Дорогой ремонт. Причина у многих — неквалифицированная установка SIM-карт продавцами (пластырь, изолента, скотч на блоках). Также прикуривание при транспортировке может повредить блок.

**EN**: Serious issue: after car wash or spontaneously, SOS calls start, then car locks out completely — black screens, no response to key. Repair: remove telematics unit, order donor, re-solder 'pair' (flash + CPU), register in cloud, re-accept master account. Expensive repair. Root cause for many: unqualified SIM card installation by sellers (tape, bandages on telematics units). Jump-starting during transport can also damage the unit.

**Key facts:**
- SOS-вызовы могут предшествовать полной блокировке авто
- Ремонт: перепайка пары flash+CPU из блока-донора
- После ремонта обязательно: прописка блока, мастер-аккаунт, приложения заново
- Причина: кривая установка SIM продавцами — пластырь, изолента на блоках
- Прикуривание при транспортировке повреждает блок телематики

**Sources:**
- https://t.me/lixiangautorussia/1667477
- https://t.me/lixiangautorussia/1695725

---

#### unified_unique_topic_tg_012: Система охлаждения ДВС — электропомпа, антифриз, вентилятор
*ICE Cooling System — Electric Water Pump, Coolant, Fan*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: engine, hvac
- **Layer**: engine
- **Season**: all
- **Sources**: 2 URLs from telegram
- **Merged from**: topic_tg_012

**RU**: Антифриз может попасть в разъем блока управления электропомпой (моторный щит слева). Симптомы: постоянно работающий вентилятор, закрытые жалюзи, температура воздуха -50°C в инженерном меню. У некоторых помпа перестает работать → перегрев мотора. Также: металлическая скобка попала в вентилятор — вибрация и 'звуки китов', устранено удалением посторонней детали.

**EN**: Coolant can leak into electric water pump control unit connector (left side of firewall). Symptoms: constantly running fan, closed shutters, -50C air temperature in engineering menu. In some cases pump stops — engine overheating. Also: metal clip found in cooling fan — caused vibration and 'whale sounds', fixed by removing foreign object.

**Key facts:**
- Антифриз в разъеме электропомпы: постоянный вентилятор + закрытые жалюзи + -50°C в меню
- Электропомпа на моторном щите слева (вид спереди)
- Металлический предмет в вентиляторе может вызвать вибрацию

**Sources:**
- https://t.me/lixiangautorussia/1302410
- https://t.me/lixiangautorussia/1685974

---

#### unified_unique_topic_tg_015: Трассовая эксплуатация — расход, скорость, расход батареи на скорости
*Highway Driving — Consumption, Speed, Battery Drain at Speed*

- **Confidence**: MEDIUM
- **Models**: L6, L7, L9
- **Systems**: engine, battery
- **Layer**: engine
- **Season**: all
- **Sources**: 3 URLs from telegram
- **Merged from**: topic_tg_015

**RU**: Детальные замеры владельцев на трассе. При 180 км/ч батарея 100→20% за 1-2 часа. При 150 км/ч — поддержание заряда. При 130 км/ч на круизе — зарядка батареи (+40% за 2 часа). Расход топлива на L6 Max при 150-160 км/ч в форсированном режиме: 12 л/100 км. Трасса 800 км с полным зарядом и скоростью 150-160 — вполне реально. Диапазон работы ДВС на трассе: 2000-3800 об/мин.

**EN**: Detailed owner measurements on highway. At 180 km/h battery drains 100→20% in 1-2 hours. At 150 — charge holds steady. At 130 on cruise — battery charges (+40% in 2 hours). Fuel consumption L6 Max at 150-160 km/h forced mode: 12 L/100km. 800 km trip with full charge at 150-160 — feasible. ICE operating range on highway: 2000-3800 RPM.

**Key facts:**
- 180 км/ч: батарея 100→20% за 1-2 часа
- 150 км/ч: заряд держится на одном уровне
- 130 км/ч круиз: +40% заряда за 2 часа
- Расход топлива при 150-160 км/ч: ~12 л/100 км (L6 Max)
- Круиз работает максимум до 130 км/ч

**Sources:**
- https://t.me/lixiangautorussia/1711593
- https://t.me/lixiangautorussia/1530022
- https://t.me/lixiangautorussia/1337291

---

#### unified_unique_topic_tg_016: Вибрация и шум ДВС — нормы и проблемы
*ICE Vibration and Noise — Normal vs Problem*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: engine
- **Layer**: engine
- **Season**: all
- **Sources**: 4 URLs from telegram
- **Merged from**: topic_tg_016

**RU**: Частый вопрос: нормально ли вибрирует/шумит ДВС? Вибрация при прогреве и запуске на месте — нормально. При запуске на ходу — вибрации нет. Шумнее после ТО (возможно другое масло). Завывание при подзарядке от мотора — нормально (генератор). После ТО на 15 тыс. км: звук детонации при нажатии газа, хлюпание — возможно проблема с маслом или фильтром.

**EN**: Common question: is ICE vibration/noise normal? Vibration during warm-up and stationary start — normal. No vibration when starting while driving. Louder after service (possibly different oil). Whining during generator charging — normal. After 15K service: detonation sound on throttle, gurgling — possibly oil or filter issue.

**Key facts:**
- Вибрация ДВС при запуске на месте — нормально
- Вибрации при запуске на ходу нет — так и должно быть
- Звук завывания при подзарядке — нормальная работа генератора
- Двигатель может шуметь иначе после замены масла

**Sources:**
- https://t.me/lixiangautorussia/1427957
- https://t.me/lixiangautorussia/1269809
- https://t.me/lixiangautorussia/494947
- https://t.me/lixiangautorussia/1204249

---

#### unified_unique_topic_tg_023: Масло 'оригинал' Shell vs альтернативы — подделки и реальность
*Original Shell Oil vs Alternatives — Fakes and Reality*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: engine
- **Layer**: engine
- **Season**: all
- **Sources**: 4 URLs from telegram
- **Merged from**: topic_tg_023

**RU**: Развернутая дискуссия о масле 'оригинал Li Auto' (Shell). Масло продается массово, но Shell официально не подтвердил оригинальность. Многие канистры с кривыми этикетками, непонятные QR. Клуб готовит собственное масло с характеристиками выше Shell. Важно: 'оригинальное' масло BMW делает тот же Castrol (BP). Рекомендация: лить хорошее масло и менять своевременно, а не гнаться за 'оригиналом'. Объем заправки 3.7л — анализ одной канистры ничего не дает.

**EN**: Extended discussion about 'original Li Auto' oil (Shell). Oil sold massively but Shell hasn't officially confirmed authenticity. Many cans with crooked labels, unclear QR. Club preparing own oil with better specs than Shell. Key insight: BMW 'original' oil is made by same Castrol (BP). Recommendation: use good oil and change on time, don't chase 'originals'. Fill volume 3.7L — analyzing one can proves nothing.

**Key facts:**
- Shell официально не подтвердил оригинальность масла 'Li Auto'
- Многие канистры с кривыми этикетками — подделки?
- BMW 'оригинальное' масло делает Castrol (BP)
- Объем заправки ДВС: 3.7л
- Клуб готовит собственное масло для Li Auto

**Sources:**
- https://t.me/lixiangautorussia/1677728
- https://t.me/lixiangautorussia/1578733
- https://t.me/lixiangautorussia/494947
- https://t.me/lixiangautorussia/1318242

---

#### unified_tax_power: Транспортный налог на Lixiang в России — номинальная vs максимальная мощность
*Vehicle Tax in Russia — Nominal vs Maximum Power for Lixiang*

- **Confidence**: LOW
- **Models**: L7, L8, L9
- **Systems**: 
- **Layer**: ev
- **Season**: all
- **Sources**: 1 URLs from new_scraped
- **Merged from**: topic_new_012

**RU**: Налоговая пытается начислить налог по максимальной мощности 449 л.с. Однако по закону электромоторы облагаются по номинальной мощности (не максимальной). Минфин и ВС РФ подтвердили это в письмах. Реальная номинальная мощность существенно ниже 449 л.с., что позволяет сильно снизить налог.

**EN**: Russian tax authorities attempt to charge tax based on max power of 449 hp. However, by law electric motors are taxed on nominal (not peak) power. Russian Ministry of Finance and Supreme Court confirmed this. Actual nominal power is significantly below 449 hp, enabling major tax savings.

**Key facts:**
- Max power: 449 hp (200kW front + 130kW rear motors)
- Nominal power significantly lower (taxable)
- Ministry of Finance + Supreme Court letters confirm nominal power basis
- Tax authority attempts to add ICE power on top — illegal
- SBKTS document values may vary — key for registration

**Sources:**
- https://autoplt.ru/transportnyj-nalog-lixiang-l7-l8-l9/

---

#### unified_unique_topic_tg_017: Подвеска — скрип сайлентблоков, 20 тыс. км
*Suspension — Bushing Squeaks at 20K km*

- **Confidence**: LOW
- **Models**: L6
- **Systems**: suspension
- **Layer**: chassis
- **Season**: winter
- **Sources**: 1 URLs from telegram
- **Merged from**: topic_tg_017

**RU**: На пробеге 20 тыс. км на L6 начала скрипеть подвеска. Замена сайлентблоков устранила проблему, но через 3 месяца скрип вернулся. Предположение: зимой снег и реагенты забивают подвеску, нужна мойка.

**EN**: At 20K km on L6, suspension started squeaking. Bushing replacement fixed it, but squeak returned after 3 months. Hypothesis: winter snow and road chemicals clog suspension, needs washing.

**Key facts:**
- Скрип подвески на L6 после 20 тыс. км
- Замена сайлентблоков помогает временно — 3 месяца
- Зимой скрип возвращается — возможно из-за снега и реагентов

**Sources:**
- https://t.me/lixiangautorussia/1706627

---

### MAINTENANCE

#### unified_russification: SIM-карта и русификация — установка, совместимость, операторы
*SIM Card and Russification — Installation, Compatibility, Carriers*

- **Confidence**: CONFIRMED
- **Models**: L6, L7, L9
- **Systems**: electronics, infotainment
- **Layer**: infotainment
- **Season**: all
- **Sources**: 8 URLs from new_scraped, ru_articles, telegram
- **Merged from**: topic_ru_019, topic_tg_014, topic_new_006

**RU**: Машина спроектирована для китайского рынка — за пределами Китая нет подключения к сети, OTA, гарантии. Сервис в Казахстане (дилер Алматы). Локализация включает: установку SIM-слота, русификацию, оформление китайского номера, мастер-аккаунт. Клубный магазин предоставляет: навигатор, Кинопоиск, Окко, Яндекс Музыка, HUD Speed. Пользователи предупреждают: русский блокирует порт ADB, танцы с бубном.

**EN**: Car designed for Chinese market — outside China: no network, no OTA, no warranty. Service available in Kazakhstan (Almaty dealer). Localization includes: SIM slot installation, russification, Chinese number registration, master account. Club store provides: navigator, Kinopoisk, Okko, Yandex Music, HUD Speed. Users warn: Russian blocks ADB port, requires workarounds.

**Key facts:**
- SIM впаяна в TCU — пайка рискованна
- Безопасный метод установки без пайки найден
- BAND 1,3,7 — МТС и Билайн совместимы
- Лимит трафика: 20 ГБ/мес
- Русификация неполная, русский язык — отдельная услуга
- Авто разработано только для материкового Китая
- За рубежом: нет сети, OTA, гарантии, послепродажного обслуживания
- Дилер в Алматы (Казахстан) — единственный офи центр за пределами Китая
- Русификация блокирует ADB порт
- Клубный магазин: навигация, потоковые сервисы, HUD

**Sources:**
- https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
- https://habr.com/ru/articles/827524/
- https://t.me/lixiangautorussia/1712989
- https://t.me/lixiangautorussia/1712929
- https://t.me/lixiangautorussia/1079728
- https://t.me/lixiangautorussia/1090765
- https://t.me/lixiangautorussia/1711593
- https://lixiang-sto.ru/blog/obnovlenie-carmods-na-lixiang-l7/

---

#### unified_unique_topic_ru_012: Зарядная инфраструктура для PHEV/EV в России — GB/T совместимость
*Charging Infrastructure for PHEV/EV in Russia — GB/T Compatibility*

- **Confidence**: MEDIUM
- **Models**: L6, L7, L8, L9
- **Systems**: battery
- **Layer**: battery
- **Season**: all
- **Sources**: 2 URLs from ru_articles
- **Merged from**: topic_ru_012

**RU**: Li Auto использует китайский стандарт GB/T для зарядки. В России 65,183 электромобиля + 73,280 гибридов (июль 2025). Зарядных станций — 1 на 7 авто (улучшение с 1:9). Федеральная программа: 121.6 млрд руб до 2030. Зарядные устройства GB/T AC 7.4 кВт от 4,500 грн (Украина). DC быстрая зарядка — ~40 мин до 80%.

**EN**: Li Auto uses Chinese GB/T charging standard. Russia has 65,183 EVs + 73,280 hybrids (July 2025). Charging stations ratio: 1 per 7 vehicles (improved from 1:9). Federal program: 121.6 billion RUB until 2030. GB/T AC 7.4 kW chargers from 4,500 UAH (Ukraine). DC fast charging ~40 min to 80%.

**Key facts:**
- GB/T стандарт — нужна совместимая зарядка
- 65,183 EV + 73,280 гибридов в РФ (июль 2025)
- 1 зарядная станция на 7 электромобилей
- Федеральная программа: 121.6 млрд руб до 2030
- DC быстрая зарядка: ~40 мин до 80%

**Sources:**
- https://autoreview.ru/articles/kak-eto-rabotaet/elektroekspluataciya
- https://kitaec.ua/vse-dlya-elektromobiley/podbor-po-avto/li/l9

---

#### unified_unique_topic_ru_015: Коррозия кузова и защита от реагентов
*Body Corrosion and Protection from Road Chemicals*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: body
- **Layer**: body
- **Season**: winter
- **Cost**: 6,000 - 15,000 руб
- **Sources**: 2 URLs from ru_articles
- **Merged from**: topic_ru_015

**RU**: Выдвижные пороги подвержены коррозии от дорожных реагентов, механизм может заклинивать. Обзор abw.by показал L9 без антикора через 2 года и 50,000 км — состояние в целом хорошее, но пороги и бампер в зоне риска. Антикоррозийная обработка — 6,000-15,000 руб. Установка брызговиков рекомендуется.

**EN**: Retractable running boards are prone to corrosion from road chemicals, mechanism can jam. Review by abw.by showed L9 without anti-corrosion after 2 years and 50K km — generally good condition, but running boards and bumper in risk zone. Anti-corrosion treatment 6,000-15,000 RUB. Mud flaps recommended.

**Key facts:**
- Выдвижные пороги — главная зона коррозии
- Антикор: 6,000-15,000 руб
- L9 без антикора через 2 года/50,000 км — в целом норм (abw.by)
- Брызговики снижают риск

**Sources:**
- https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
- https://abw.by/news/experience/2025/04/24/chto-sluchilos-s-lixiang-l9-bez-antikora-za-dva-goda-rassmatrivaem-na-podemnike

---

#### unified_unique_topic_ru_022: Деградация бензина в баке при редком использовании ДВС
*Fuel Degradation in Tank from Infrequent ICE Use*

- **Confidence**: LOW
- **Models**: L7, L9
- **Systems**: engine
- **Layer**: engine
- **Season**: all
- **Sources**: 1 URLs from ru_articles
- **Merged from**: topic_ru_022

**RU**: При частой езде в EV-режиме бензин «умирает» в баке — теряет октановое число, вызывает детонацию и ускоренный износ двигателя. Двигатель работает под постоянной нагрузкой как генератор (3,500-4,000 об/мин). Рекомендуют регулярно запускать генератор, не давать бензину застаиваться, использовать качественный бензин RON-100.

**EN**: With frequent EV-mode driving, fuel 'dies' in the tank — loses octane rating, causes detonation and accelerated engine wear. Engine operates under constant load as generator (3,500-4,000 RPM). Recommendations: regularly run the generator, don't let fuel sit, use quality RON-100 fuel.

**Key facts:**
- Бензин теряет октановое число при длительном хранении в баке
- Детонация — основной риск застоявшегося топлива
- Генератор работает на 3,500-4,000 об/мин — постоянная нагрузка
- AI-92 снижает пробег на 20%
- RON-100 — оптимальное топливо

**Sources:**
- https://www.drive2.ru/l/717411272110386402/

---

### TECHNOLOGY

#### unified_ai_strategy: Li Auto — AI-стратегия: Livis очки, роботы, VLA Driver
*Li Auto AI Strategy — Livis Smart Glasses, Humanoid Robots, VLA Driver*

- **Confidence**: HIGH
- **Models**: L9
- **Systems**: adas, electronics
- **Layer**: adas
- **Season**: all
- **Sources**: 6 URLs from en_articles, new_scraped
- **Merged from**: topic_en_012, topic_en_023, topic_new_028

**RU**: Li Auto позиционирует себя как AI-компанию. CEO заявил: 2026 — последнее окно для становления ведущей AI-компанией. Ключевые направления: (1) Livis smart glasses (от 1,999 юаней, 36г, Sony IMX681, Zeiss линзы, голосовой ассистент Lixiang Tongxue); (2) проект Nexus — гуманоидные роботы, первый двухколёсный робот для заводов в середине 2026; (3) VLA Driver — end-to-end автопилот нового поколения.

**EN**: Li Auto positions itself as an AI company. CEO stated: 2026 is the final window to become a leading AI firm. Key directions: (1) Livis smart glasses (from RMB 1,999, 36g, Sony IMX681, Zeiss lenses, Lixiang Tongxue voice assistant); (2) Project Nexus — humanoid robots, first two-wheeled factory robot in mid-2026; (3) VLA Driver — next-gen end-to-end autonomous driving model.

**Key facts:**
- Livis smart glasses: RMB 1,999, 36g weight, 18.8h battery, Zeiss lenses
- Project Nexus: secret robotics initiative, two-wheeled + bipedal robots planned
- Two-wheeled robot 'ready' — targeting mid-2026 release for factory use
- VLA Driver: vision-language-action model for autonomous driving
- OTA 8.3: VLA Driver large model, smart cockpit upgrades
- Li Xiang: 'We will not produce smartphones, AI glasses is enough'
- Xpeng: 110,000 sqm robot factory in Guangzhou, mass delivery target 2026
- Xpeng Iron: 178cm, 70kg, solid-state batteries, in-house Turing AI chips
- Xiaomi: robot achieved 90.2% success rate in die-casting workshop
- Xiaomi robot uses VLA model (Xiaomi-Robotics-0, 4.7B parameters)

**Sources:**
- https://cnevpost.com/2025/12/03/li-auto-launches-smart-glasses-livis/
- https://cnevpost.com/2026/02/13/li-autos-self-driving-head-to-leave-after-brief-role-humanoid-robot/
- https://cnevpost.com/2026/03/06/li-auto-pivots-to-robotics-with-secret-nexus-project/
- https://cnevpost.com/2026/02/25/xpeng-to-break-ground-on-humanoid-robot-factory-q1/
- https://cnevpost.com/2026/03/02/xiaomi-deploys-humanoid-robots-ev-factory/
- https://cnevpost.com/2025/11/27/li-auto-to-launch-smart-glasses-livis-dec-3-bets-ai/

---

#### unified_battery_supplier: Sunwoda vs CATL — скандал с качеством батарей, иск на $330M
*Sunwoda vs CATL — Battery Quality Scandal, $330M Lawsuit and Impact on Li Auto*

- **Confidence**: HIGH
- **Models**: L7, L9, i6
- **Systems**: battery
- **Layer**: battery
- **Season**: all
- **Sources**: 6 URLs from en_articles, new_scraped
- **Merged from**: topic_en_014, topic_new_020, topic_new_035

**RU**: Geely/Vremt подали иск на Sunwoda на 2.31 млрд юаней за дефектные батареи 2021-2023. Zeekr отозвал 38,277 EVs из-за риска теплового разгона батарей Sunwoda. Иск урегулирован (500-800M юаней), но имидж Sunwoda подорван. Li Auto использует Sunwoda в i6 и предлагает покупателям переход на эти батареи для ускорения поставок — большинство отказывается.

**EN**: Geely/Vremt sued Sunwoda for RMB 2.31B over defective battery cells supplied 2021-2023. Zeekr recalled 38,277 EVs for thermal runaway risk in Sunwoda batteries. Lawsuit settled (RMB 500-800M impact), but Sunwoda brand severely damaged. Li Auto uses Sunwoda in i6 and offers buyers switch to Sunwoda batteries for faster delivery — most refuse.

**Key facts:**
- Vremt (Geely subsidiary) sued Sunwoda EVB for RMB 2.31 billion
- Battery cells supplied Jun 2021 - Dec 2023 alleged defective
- Settlement: RMB 500-800M impact on Sunwoda 2025 net income
- Zeekr recalled 38,277 Zeekr 001 WE Edition for thermal runaway risk
- Li Auto i6 uses both CATL and Sunwoda — buyers refuse Sunwoda option
- Sunwoda ranks 6th in China EV battery market (3.17% share)
- Li i8: launched July 29, relaunched Aug 5 with price cuts
- Li i6: 20,000 firm orders within hours of launch
- i6 starting price: 249,800 CNY (with 35K limited-time benefits)
- CATL battery supply constrained — 4-6 week delays

**Sources:**
- https://cnevpost.com/2025/12/26/sunwoda-sued-by-geely-unit-over-battery-cell-issues/
- https://cnevpost.com/2026/02/06/sunwoda-geely-vremt-settle-battery-quality-lawsuit/
- https://cnevpost.com/2026/02/09/zeekr-recalls-38277-evs-thermal-runaway-risk-batteries/
- https://cnevpost.com/2025/09/26/li-auto-20000-orders-i6/
- https://cnevpost.com/2025/09/26/li-auto-launches-i6-suv/
- https://cnevpost.com/2026/01/29/li-auto-still-grapples-with-battery-supply-constraints-i6-suv/

---

#### unified_charging_800v: Обновлённый Li L9 2026 — батарея 73 кВт*ч, 800В, чипы M100, рулевое по проводам
*Updated Li L9 2026 — 73 kWh Battery, 800V, M100 Chips, Steer-by-Wire*

- **Confidence**: HIGH
- **Models**: L9, MEGA, i6, i8
- **Systems**: adas, battery, charging, ev, steering, suspension
- **Layer**: ev
- **Season**: all
- **Sources**: 5 URLs from en_articles, new_scraped
- **Merged from**: topic_new_019, topic_en_009, topic_new_033

**RU**: Li MEGA стал первым автомобилем с 5C батареей CATL Qilin (102.7 кВт·ч) на 800V платформе. Зарядка 500 км за 12 минут, 400 км за 9.5 минут, максимальная мощность 552 кВт. Расход 15.9 кВт·ч/100км — лучше конкурентов (Zeekr 009: 18.3, Denza D9: 18.4). Сеть: 4,001 суперзарядных станций к февралю 2026, 22,447 зарядных точек.

**EN**: Li MEGA became the first vehicle with CATL Qilin 5C battery (102.7 kWh) on 800V platform. Charges 500 km in 12 min, 400 km in 9.5 min, peak power 552 kW. Energy consumption 15.9 kWh/100km — better than rivals (Zeekr 009: 18.3, Denza D9: 18.4). Network: 4,001 supercharging stations by Feb 2026, 22,447 charging stalls.

**Key facts:**
- Battery: 52 kWh → 73 kWh CATL, 5C charging
- EV range: 400+ km (was ~215 km)
- M100 chips: 2560 TOPS total (3x Nvidia Thor-U)
- 360-degree LiDAR coverage
- Steer-by-wire, 4-wheel steering, EMB brakes
- L9 Livis ultimate: 559,800 CNY (~$80,670)
- Standard L9: from 409,800 CNY
- 5C CATL Qilin battery: first in any production vehicle
- Peak charging capacity: 552 kW (leaked test data)
- 6%-80% charge in 11 minutes (leak test result)

**Sources:**
- https://cnevpost.com/2026/02/06/li-auto-files-for-l9-livis/
- https://cnevpost.com/2026/02/06/li-auto-unveils-updated-l9-suv/
- https://kz.kursiv.media/2026-02-06/rmnm-li-auto-l9-2026-stal-krupnee-tekhnologichnee-i-dorozhe
- https://carnewschina.com/2023/06/17/li-mega-mpv-is-li-autos-first-pure-electric-vehicle-with-latest-catl-battery-and-800v-platform
- https://cnevpost.com/2026/02/09/li-auto-reaches-4000-supercharging-stations/

---

#### unified_i_series_bev: Li i8 и i6 — переход к электрическим SUV, проблемы запуска
*Li i8 and i6 — BEV SUV Transition, Launch Struggles and Battery Supply Issues*

- **Confidence**: MEDIUM
- **Models**: i6, i8
- **Systems**: battery, drivetrain
- **Layer**: ev
- **Season**: all
- **Sources**: 3 URLs from en_articles
- **Merged from**: topic_en_003

**RU**: Li Auto запустила серию чисто электрических SUV: i8 (6 мест, июль 2025, от 339,800 юаней) и i6 (5 мест, сентябрь 2025, от 249,800 юаней). Обе модели разочаровали: i8 перезапущена с понижением цены через неделю после старта. i6 получил 20,000 заказов за часы, но столкнулся с дефицитом батарей CATL. Покупателям предлагают перейти на Sunwoda (со скандалом с Geely). Цель: 6K i8 + 10K i6/мес к концу года.

**EN**: Li Auto launched BEV SUV series: i8 (6-seat, Jul 2025, from RMB 339,800) and i6 (5-seat, Sep 2025, from RMB 249,800). Both disappointed: i8 relaunched with price cut one week after debut. i6 got 20K orders in hours but hit CATL battery supply constraints 4 months after launch. Buyers encouraged to switch to Sunwoda batteries (embroiled in Geely quality lawsuit). Target: 6K i8 + 10K i6/month by year-end.

**Key facts:**
- i8: Li Auto's first all-electric SUV, 97.8 kWh 5C battery, up to 690 km CLTC
- i8 relaunched Aug 5 with price cut after disappointing initial reception
- i6: 20,000+ firm orders within hours of Sep 26 launch
- Battery supply constraint: CATL production ramp slower than expected
- Sunwoda offered as alternative — tainted by RMB 2.31B Geely/Vremt lawsuit
- i8 priced 25% higher than competitor Onvo L90
- Li Xiang target: 18-20K BEV units/month (i8+i6+Mega) by year-end

**Sources:**
- https://cnevpost.com/2025/07/17/li-auto-starts-pre-orders-i8/
- https://cnevpost.com/2025/09/26/li-auto-launches-i6-suv/
- https://cnevpost.com/2026/01/29/li-auto-still-grapples-with-battery-supply-constraints-i6-suv/

---

#### unified_l9_2026_update: L9 Livis 2026 — флагманский EREV с чипом M100 и EMB тормозами
*L9 Livis 2026 — Flagship EREV with M100 Chip, EMB Brakes and 800V Suspension*

- **Confidence**: MEDIUM
- **Models**: L9
- **Systems**: adas, brakes, electronics, suspension
- **Layer**: adas
- **Season**: all
- **Sources**: 2 URLs from en_articles
- **Merged from**: topic_en_005

**RU**: Li Auto представила обновлённый L9 с версией Livis (559,800 юаней) — значительное удорожание vs текущие 409-439K. Ключевые технологии: собственный чип M100 (5 нм, 2560 TOPS — втрое мощнее Nvidia Thor-U), 360° LiDAR, электромеханические тормоза (EMB), подруль с электрическим приводом (steer-by-wire), полноуправляемое шасси, батарея 72.7 кВт·ч CATL. Запуск во 2 квартале 2026.

**EN**: Li Auto unveiled updated L9 with Livis variant (RMB 559,800) — significant price jump vs current 409-439K. Key technologies: in-house M100 chip (5nm, 2,560 TOPS — 3x Nvidia Thor-U), 360-degree LiDAR coverage, electromechanical braking (EMB), steer-by-wire, four-wheel steering, 800V active suspension with 10,000N lift per wheel, 72.7 kWh CATL battery. Launch planned for Q2 2026.

**Key facts:**
- M100 chip: Li Auto's own 5nm processor, 2,560 TOPS effective computing power
- 360-degree LiDAR coverage — world's most powerful smart driving brain
- EMB (electromechanical brakes) — addressing L7/L9 spongy brake complaints
- Steer-by-wire + four-wheel steering for flagship driving dynamics
- 800V fully active suspension with 10,000N lift force per wheel
- Price: RMB 559,800 — 27-36% higher than current L9
- 72.7 kWh CATL ternary battery, 332-340 km EV range

**Sources:**
- https://cnevpost.com/2026/02/06/li-auto-files-for-l9-livis/
- https://cnevpost.com/2026/02/06/li-auto-unveils-updated-l9-suv/

---

### MARKET

#### unified_sales_market: Продажи Li Auto — рекордный рост 2023, спад 2025, 8 месяцев падения
*Li Auto Sales Trajectory — Record 2023 Growth, 2025 Decline, 8-Month Slump*

- **Confidence**: CONFIRMED
- **Models**: L6, L7, L8, L9, Li ONE, MEGA, i8
- **Systems**: battery, body, drivetrain, engine, hvac
- **Layer**: general
- **Season**: all
- **Sources**: 26 URLs from en_articles, new_scraped, ru_articles, telegram
- **Merged from**: topic_en_002, topic_en_004, topic_new_002, topic_new_025, topic_new_029, topic_ru_010, topic_ru_023, topic_ru_031, topic_tg_007, topic_en_011, topic_en_024, topic_en_025, topic_new_021, topic_ru_006

**RU**: Распространенная зимняя проблема: ошибка чек U009387-FF при температуре ниже -8°C и прогреве ДВС выше 70-80°C. Диагностика показывает 'компрессор кондиционера', но реальная причина — жалюзи радиатора. Жалюзи шумно работают, могут заклинивать от мороза. Решения: силиконовая обработка жалюзи, снятие защитных сеток с бампера. Ошибка пропадает в теплом гараже. Отдельные случаи реальной поломки компрессора кондиционера — ремонт ~1000 USD.

**EN**: Li Auto showed phenomenal growth in 2023: from 133K to 376K deliveries (+190%), first exceeding 30K/month. 2024 growth slowed as MEGA disappointed. 2025 brought decline: annual deliveries 406K (-18.8%), 8 consecutive months of YoY decline. L6 leads sales (47% of deliveries), L9 losing share (-47% Jan-Apr 2025). Company returned to quarterly loss in Q3 2025 for first time in 3 years (RMB 624M loss).

**Key facts:**
- 2023: 376,030 deliveries, +190% YoY, avg price >350K yuan (comparable to Audi)
- 600,000th vehicle delivered Dec 2023 in 48 months
- 2025: 406,343 deliveries, -18.8% YoY — first annual decline
- 8 consecutive months of YoY delivery decline (Jun 2025 - Jan 2026)
- Q3 2025: net loss RMB 624M, first loss since Q4 2022
- L6 contributes ~47% of deliveries; L9 dropped to ~12%
- Jan 2026: only 27,668 deliveries — lowest since Mar 2025
- Onvo L90 pre-sales starting at RMB 279,900 — significantly below Li L9's 409,800
- L90 dimensions larger than i8 in all measurements
- Onvo posted direct comparison photos with Li L9 on Weibo

**Sources:**
- https://cnevpost.com/2025/11/26/li-auto-earnings-q3-2025/
- https://cnevpost.com/2026/01/01/li-auto-delivers-44246-cars-dec-2025/
- https://cnevpost.com/2026/02/01/li-auto-delivers-27668-cars-jan-2026/
- https://cnevpost.com/2026/03/01/li-auto-snaps-8-month-sales-decline-feb-deliveries-steady/
- https://cnevpost.com/2025/02/25/nio-onvo-1st-official-image-l90/
- https://cnevpost.com/2025/02/26/nio-onvo-new-image-l90-comparison-li-l9/
- https://cnevpost.com/2025/07/11/nio-onvo-begins-pre-sales-l90/
- https://cnevpost.com/2025/12/01/li-auto-deliveries-nov-2025/

---

#### unified_global_expansion: Экспансия Li Auto — Европа, Ближний Восток, Центральная Азия
*Li Auto Global Expansion — Europe, Middle East, Central Asia and Africa*

- **Confidence**: MEDIUM
- **Models**: L6, L7, L9
- **Systems**: 
- **Layer**: general
- **Season**: all
- **Sources**: 1 URLs from en_articles, new_scraped
- **Merged from**: topic_en_016, topic_new_032

**RU**: Li Auto расширяет глобальное присутствие: R&D центр в Мюнхене (дизайн, полупроводники, шасси), вступление в CCCEU (лоббистская организация в ЕС). В декабре 2025 вышли на рынки Египта, Казахстана, Азербайджана. Подготовка к преодолению тарифов ЕС на китайские EVs. Однако темпы интернационализации медленнее конкурентов (BYD, Nio, Xpeng).

**EN**: Li Auto expands globally: R&D center in Munich (design, semiconductors, chassis), joined CCCEU (EU lobbying body). In Dec 2025, entered Egypt, Kazakhstan, Azerbaijan markets. Preparing to navigate EU tariffs on Chinese EVs. However, internationalization pace slower than peers (BYD, Nio, Xpeng).

**Key facts:**
- Munich R&D center established Jan 2025: styling, power semiconductors, chassis, certification
- Joined CCCEU alongside BYD, Nio, Xpeng, Geely, CATL
- Dec 2025: L9, L7, L6 launched in Egypt, Kazakhstan, Azerbaijan
- China-EU tariff dispute: reached consensus on price undertakings Jan 2026
- Li Auto internationalization slower than BYD, Nio, Xpeng
- CCCEU full member since Feb 2026
- Munich R&D center since Jan 2025
- R&D covers: styling, power semiconductors, chassis, regulatory
- China-EU EV tariff dispute settled via price undertakings
- Behind BYD/Nio/Xpeng in internationalization

**Sources:**
- https://cnevpost.com/2026/02/24/li-auto-joins-ccceu/

---

#### unified_unique_topic_en_017: Ранняя история Li Auto — от стартапа к IPO, инвестиции Meituan
*Li Auto Early History — From Startup to IPO, Meituan Investment*

- **Confidence**: MEDIUM
- **Models**: Li ONE
- **Systems**: 
- **Layer**: general
- **Season**: all
- **Sources**: 2 URLs from en_articles
- **Merged from**: topic_en_017

**RU**: Li Auto основана в 2015 году Li Xiang (родился 1981, основатель pcpop.com и Auto Home). Первая модель Li ONE (2019, 328,000 юаней) — серийный гибрид EREV с 800 км NEDC. Meituan инвестировала $500M (серия D), оценка $4.05 млрд. К маю 2020 выпущено 10,000 Li ONE. IPO на NASDAQ. 6-местная версия — 96% покупателей.

**EN**: Li Auto founded 2015 by Li Xiang (born 1981, founder of pcpop.com and Auto Home). First model Li ONE (2019, RMB 328,000) — series-hybrid EREV with 800 km NEDC. Meituan invested $500M (Series D) at $4.05B valuation. By May 2020, 10,000th Li ONE produced. IPO on NASDAQ. 6-seat version chosen by 96% of buyers.

**Key facts:**
- Li Xiang: founded pcpop.com (2000) and Auto Home (2005, NYSE-listed 2013)
- Meituan (food delivery giant) invested $500M in Series D
- Total funding exceeded $2 billion before IPO
- Li ONE: 96% chose 6-seat version, gray metallic most popular color
- Wang Xing (Meituan CEO): 'The #1 EV will probably be Chinese, not American'

**Sources:**
- https://cnevpost.com/2020/04/11/lixiang-one-becomes-bestselling-phev-in-china-in-march/
- https://cnevpost.com/2020/06/24/chinese-food-delivery-firm-meituan-plans-500m-investment-in-ev-maker-lixiang/

---

#### unified_unique_topic_ru_026: Ценообразование и утильсбор — влияние на стоимость Li Auto в РФ
*Pricing and Recycling Fee — Impact on Li Auto Cost in Russia*

- **Confidence**: LOW
- **Models**: L6, L7, L9
- **Systems**: 
- **Layer**: None
- **Season**: all
- **Sources**: 1 URLs from ru_articles
- **Merged from**: topic_ru_026

**RU**: Утильсбор — основной фактор роста цен в 2025. Повышения в октябре, ноябре, декабре вызвали ажиотажный спрос перед каждым этапом. L6 от 5,690,000 руб, L7 Pro от 6,590,000, L9 Ultra 8,590,000. Цена нового L9 выросла на 20-30% за год. Б/у L9: от 5,250,000. Альтернативный импорт подорожал, но всё ещё работает. «Серый» импорт — 156,000 авто в 2025 (не сдался под утильсбором).

**EN**: Recycling fee is the main price growth factor in 2025. Increases in Oct/Nov/Dec caused rush demand before each stage. L6 from 5,690K RUB, L7 Pro from 6,590K, L9 Ultra 8,590K. New L9 price up 20-30% over the year. Used L9: from 5,250K. Parallel import got more expensive but still operates. 156K 'gray' imports in 2025.

**Key facts:**
- L6: от 5,690,000 руб
- L7 Pro: от 6,590,000 руб
- L9 Ultra: 8,590,000 руб
- Утильсбор — основной драйвер роста цен
- Серый импорт: 156,000 авто в 2025 (не умер)

**Sources:**
- https://autoreview.ru/articles/avtorynok/util-effekt

---

### SPECS

#### unified_lidar: Обзоры Li L9 — «семейный SUV без компромиссов»
*Li L9 Reviews — 'No-Compromise Family SUV' with Premium Features*

- **Confidence**: CONFIRMED
- **Models**: L7, L8, L9
- **Systems**: adas, electronics, interior, suspension
- **Layer**: interior
- **Season**: all
- **Sources**: 8 URLs from en_articles, new_scraped, ru_articles
- **Merged from**: topic_en_018, topic_en_022, topic_new_027, topic_ru_013, topic_new_013

**RU**: Сложнейшая электронная архитектура: два Snapdragon 8155, два Nvidia Orin, 11 камер, 12 сонаров, 1-5 радаров, 1 лидар (Max). Все блоки связаны несколькими шинами данных — замена любого компонента требует прописки. Универсальный сканер видит только Prince ДВС. Trick: если представиться как Omoda, видны дополнительные подсистемы. Полноценной диагностики в России нет.

**EN**: Complex electronic architecture: dual Snapdragon 8155, dual Nvidia Orin, 11 cameras, 12 sonars, 1-5 radars, 1 lidar (Max). All ECUs connected via multiple data buses — any component replacement requires registration. Universal scanner only sees Prince ICE. Trick: if pretending to be Omoda, additional subsystems become visible. No full diagnostics capability in Russia.

**Key facts:**
- Four screens: 2x 15.7" dashboard + 1x 15.7" rear + steering wheel mini display
- Hesai AT128 LiDAR on roof, dual Nvidia Orin X chips (Max version)
- 10,000 production milestone achieved in record industry time
- 30,000+ orders within 72 hours of launch
- 50,000+ orders by August 2022
- Deliveries started Aug 30, 2022 after brief Sichuan power delay
- L9 Pro: no LiDAR, Horizon Journey 5 chip (128 TOPS)
- L9 Max: Hesai AT128 LiDAR + 2x Nvidia Orin X (508 TOPS total)
- Price delta: 30,000 yuan between Pro and Max
- AD Pro: highway NOA, LCC, automatic parking, AEB

**Sources:**
- https://www.carscoops.com/2022/07/the-l9-suv-from-li-auto-proves-that-the-chinese-really-are-on-a-roll
- https://topelectricsuv.com/first-look-review/li-auto-l9-hybrid/
- https://cnevpost.com/2023/06/16/li-auto-files-for-li-l9-without-lidar/
- https://cnevpost.com/2023/08/03/li-auto-launches-li-l9-pro-no-lidar-cheaper/
- https://kz.kursiv.media/2025-10-14/rmnm-chery-predstavila-ubiytsu-lixiang-l9-polnorazmerniy-krossover-fulwin-t11
- https://autoreview.ru/articles/kak-eto-rabotaet/apropriaciya
- https://autoplt.ru/sravnenie-lixiang-l7-l8-l9/
- https://autoplt.ru/obzor-lixiang-l9/

---

#### unified_winter_issues: Тяговая батарея Lixiang — тернарный литий, характеристики, зарядка
*Lixiang Traction Battery — Ternary Lithium, Specs, Charging*

- **Confidence**: HIGH
- **Models**: L7, L8, L9
- **Systems**: battery, drivetrain, engine, hvac
- **Layer**: battery
- **Season**: all
- **Sources**: 11 URLs from new_scraped, telegram
- **Merged from**: topic_new_010, topic_tg_006, topic_tg_024, topic_tg_025

**RU**: Детальные обсуждения зимней эксплуатации. Догреватель (Heater) потребляет до 10 кВт/ч из батареи при температуре ДВС ниже 75°C. Обогрев задних рядов — до 2.7 кВт/ч. Жалюзи радиатора забиваются снегом — мотор переходит на минимальные обороты и не может заряжать батарею. Батарея при -25°C плохо заряжается и отдает. Холодный воздух может задувать в салон на поворотах зимой. Сетки на бампер могут вызвать ошибку U009387 при замерзании жалюзи.

**EN**: Detailed winter operation discussions. Heater consumes up to 10 kW/h from battery when ICE temp is below 75C. Rear seat heating — up to 2.7 kW/h. Radiator shutters clog with snow — ICE drops to minimum RPM, cannot charge battery. Battery at -25C charges/discharges poorly. Cold air may blow into cabin during turns in winter. Aftermarket grille nets can trigger U009387 error when shutters freeze.

**Key facts:**
- Ternary lithium battery with thermal protection casing
- L7 EV range: 210 km, safe discharge to 3%
- Fast charge: max 75 kW, 30-40 min to full
- Slow charge preserves battery life better
- CCS2 to GB/T adapter for European charging
- Battery in thermal-protective casing for fire safety
- Догреватель (Heater) потребляет до 10 кВт/ч при температуре ДВС < 75°C
- Обогрев задних рядов: до 2.7 кВт/ч постоянно
- Жалюзи радиатора забиваются снегом — ДВС переходит на минимальные обороты
- При -25°C батарея плохо заряжается и плохо отдает

**Sources:**
- https://autoplt.ru/batareya-lixiang-l7-l8-l9/
- https://autoplt.ru/zaryadka-lixiang-l7-l8-l9/
- https://t.me/lixiangautorussia/1711593
- https://t.me/lixiangautorussia/1151387
- https://t.me/lixiangautorussia/1640893
- https://t.me/lixiangautorussia/174877
- https://t.me/lixiangautorussia/1674572
- https://t.me/lixiangautorussia/1695725

---

#### unified_unique_topic_ru_011: Сравнительные тесты — Li L9 vs Zeekr 9X, Voyah, Exeed, Wey
*Comparison Tests — Li L9 vs Zeekr 9X, Voyah, Exeed, Wey*

- **Confidence**: MEDIUM
- **Models**: L7, L9
- **Systems**: 
- **Layer**: None
- **Season**: all
- **Sources**: 2 URLs from ru_articles
- **Merged from**: topic_ru_011

**RU**: Autoreview проводит профессиональные сравнительные тесты Li Auto с конкурентами. Li L9 Ultra vs Zeekr 9X Max — тест на полигоне. Li L7 vs Wey 07 vs Seres M7 — три подзаряжаемых гибрида. Li L7 vs Voyah Free vs Volvo XC90 — электрифицированные кроссоверы. BYD Tang L vs Li L9 — прямые конкуренты. Fulwin T11 от Chery — позиционируется как «конкурент Li L9».

**EN**: Autoreview conducts professional comparison tests of Li Auto vs competitors. Li L9 Ultra vs Zeekr 9X Max on test track. Li L7 vs Wey 07 vs Seres M7 — three PHEVs. Li L7 vs Voyah Free vs Volvo XC90 — electrified SUVs. BYD Tang L vs Li L9 — direct competitors. Fulwin T11 from Chery — positioned as 'Li L9 competitor'.

**Key facts:**
- Li L9 Ultra vs Zeekr 9X Max — тест на полигоне Autoreview
- Li L7 vs Wey 07 vs Seres M7 — три гибрида в одном классе
- Li L7 vs Voyah Free vs Volvo XC90 — кросс-сегмент
- Chery Fulwin T11 позиционируется как конкурент L9
- Li L9 J.D. Power: 211 штрафных баллов (худший среди гибридных SUV)

**Sources:**
- https://autoreview.ru/articles/kak-eto-rabotaet/apropriaciya
- https://autoreview.ru/articles/kak-eto-rabotaet/elektroekspluataciya

---

#### unified_unique_topic_new_022: Производитель Li Auto — завод в Чанчжоу, история компании, партнёры
*Li Auto Manufacturer — Changzhou Factory, Company History, Partners*

- **Confidence**: LOW
- **Models**: L7, L8, L9
- **Systems**: 
- **Layer**: body
- **Season**: all
- **Sources**: 1 URLs from new_scraped
- **Merged from**: topic_new_022

**RU**: Li Xiang основана в 2015 году Ли Сяном (бывший директор Xpeng). Штаб-квартира в Пекине, производство в Чанчжоу + новый завод в Пекине. Мощность: 750 000 авто/год. Партнёры: Panasonic, Bosch, BorgWarner, Valeo. IPO на NASDAQ в 2020. 3000 зарядных станций к концу 2025.

**EN**: Li Xiang founded in 2015 by Li Xiang (ex-Xpeng executive). HQ in Beijing, production in Changzhou + new Beijing factory. Capacity: 750,000 cars/year. Partners: Panasonic, Bosch, BorgWarner, Valeo. NASDAQ IPO in 2020. 3,000 charging stations by end 2025.

**Key facts:**
- Founded 2015, IPO on NASDAQ 2020
- CEO: Li Xiang, CTO: Ma Donghui
- Changzhou factory + new Beijing factory
- 750,000 unit/year capacity
- Key partners: Panasonic, Bosch, BorgWarner, Valeo
- 800V REEV technology with 12-min charge for 500km

**Sources:**
- https://autoplt.ru/proizvoditel-lixiang-l7-l8-l9/

---

### COMPARISON

#### unified_unique_topic_new_016: Lixiang L7 — тест на дальность 1000+ км без дозаправки (Алматы — Астана)
*Lixiang L7 — Range Test 1000+ km Without Refueling (Almaty-Astana)*

- **Confidence**: LOW
- **Models**: L7
- **Systems**: battery, engine
- **Layer**: ev
- **Season**: winter
- **Sources**: 1 URLs from new_scraped
- **Merged from**: topic_new_016

**RU**: В тесте Kolesa KZ на маршруте Алматы — Астана (1200+ км) L7 прошёл 1000 км без дозаправки. Расход: 15.6 кВт*ч/100 км + 7.8 л/100 км бензина. Победил Rox 01, Deepal S07 и BYD Song Plus DM-i. Зимние шины, кондиционер, круиз — реальные условия.

**EN**: In Kolesa KZ test on Almaty-Astana route (1200+ km), L7 covered 1000 km without refueling. Consumption: 15.6 kWh/100km + 7.8 L/100km petrol. Beat Rox 01, Deepal S07 and BYD Song Plus DM-i. Winter tires, AC, cruise — real-world conditions.

**Key facts:**
- L7 range: 1000+ km without refueling (real test)
- Electric consumption: 15.6 kWh/100km
- Petrol consumption: 7.8 L/100km
- Beat Rox 01, Deepal S07 (813 km), BYD Song Plus DM-i
- Winter tires, climate on, cruise control — realistic

**Sources:**
- https://kz.kursiv.media/2025-12-09/shkv-realniy-zapas-khoda-gibrid-lixiang-l7-rox-deepal-byd-song-plus

---

### LEGAL

#### unified_service_network: Регистрация в ГИБДД — отказы, экспертиза, сертификация Sinomach
*Vehicle Registration — Refusals, Expert Examination, Sinomach Certification*

- **Confidence**: HIGH
- **Models**: L6, L7, L9
- **Sources**: 8 URLs from ru_articles, telegram
- **Merged from**: topic_ru_007, topic_ru_027, topic_tg_002

**RU**: Горячая дискуссия о плюсах и минусах сертифицированных дилеров (Панавто, Авилон) через Синомах. Плюсы: штат механиков, рембаза, гарантия, техкарты производителя, центральный склад запчастей. Минусы: высокая цена. Серый импорт и независимые сервисы (Helper, Графит, ЕНКарс) дешевле. Важное замечание: 

---

### NEWS

#### unified_brakes: Li L9 Livis — новая платформа, EMB тормоза, 5-нм чип
*Li L9 Livis — New Platform, EMB Brakes, 5nm Chip*

- **Confidence**: CONFIRMED
- **Models**: L6, L7, L9
- **Sources**: 13 URLs from new_scraped, ru_articles, telegram
- **Merged from**: topic_tg_020, topic_new_017, topic_ru_017, topic_ru_002, topic_tg_019, topic_tg_010, topic_tg_018

**RU**: Владельцы делятся опытом зимнего вождения. L6 ведет себя 'как заднеприводная' на скользкой дороге — заносы в поворотах. Режим 'скользкая дорога' + шипованная резина. Выбор зимней резины критичен из-за массы авто (>2.5 т). Режим Шоссе — самый адекватный: не душит двигатель при заносе. Рекуперация в с

---
