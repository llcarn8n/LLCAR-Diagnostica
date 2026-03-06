# Agent 3: Drive2.ru, GetCar.ru, Russian Forums — Li Auto L7/L9 Research

**Date:** 2026-03-06
**Agent:** 3 (Drive2 + Russian Forums specialist)
**Sources covered:** drive2.ru, getcar.ru, liautorussia.ru (faq), autoreview.ru, chinamobil.ru, kitaec.ua, autopilotclub.ru, kursiv.media, autonews.ru, autoplt.ru, lixiang-sto.ru

---

## Existing Data in KB

Before research, the KB already contained:
- **41 autoreview_ru** articles (mostly news, some comparative tests)
- **4 getcar_ru** articles (L9 comfort, reliability, breakdowns, air suspension)
- **4 kitaec** articles (parts catalogs for L6/L7/L8/L9)
- **54 drom_reviews** (owner review pages for L6/L7/L8/L9)

---

## Issues Found

### 1. Пневмоподвеска AMK — замерзание клапанов зимой (Air Suspension AMK Compressor Freezing)
- **Models**: L7 (primary), also L8/L9 to lesser extent
- **Mileage**: 10,000-15,000 km and beyond
- **Season**: Winter (first symptoms at sub-zero temperatures)
- **Symptoms**: Car "sits down" and loses ground clearance at sub-zero temperatures. Dashboard records suspension error. Compressor runs but cannot inflate bags.
- **Affected Systems**: Pneumatic suspension (air suspension), AMK compressor
- **DTC Codes**: Not specified in sources
- **Root Cause**: AMK compressor design flaw — the intake/exhaust line allows excess moisture to enter the pneumatic system. In summer this causes rust on bearings, in winter — valve freezing. The system's regeneration cycle cannot remove accumulated moisture. Constructive features of AMK compressor location exacerbate the issue.
- **Resolution**: Annual drying and vacuuming of the system (like A/C). Some owners relocate the intake tube. Compressor replacement costs 39,000-100,000 RUB. Full suspension repair from 15,000-20,000 RUB (labor) plus parts. Wabco compressors (standard on L8/L9, some L7s) are significantly more reliable and practically problem-free.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/700705017560044478/ (Lixiang L7, L9 — практика ремонта пневмоподвески)
  - https://www.drive2.ru/l/697330341496494867/ (Решаем проблемы с пневмоподвеской)
  - https://www.drive2.ru/l/688364373927796623/ (Ошибка пневмоподвески Li 7)
  - https://faq.liautorussia.ru/aggregation/specs/air_suspention_partial_solution
  - https://getcar.ru/blog/problemy-pnevmopodveski-lixiang-l9/
  - https://lixiang-sto.ru/blog/remont-pnevmopodveski-lixiang-l7/
- **How Found**: WebSearch "drive2.ru lixiang L7 L9 пневмоподвеска проблема зимой ремонт"

---

### 2. Двигатель 1.5T — проблемы с поршнями и масложор (Engine 1.5T Piston Oil Consumption)
- **Models**: L9 (primary, early production), also L7/L8
- **Mileage**: Under 30,000 km for severe cases
- **Season**: All
- **Symptoms**: Excessive oil consumption. Engine burning more oil than expected for a new unit with low mileage.
- **Affected Systems**: Engine (L2E15M 1.5T), pistons, oil drain holes
- **DTC Codes**: Not specified
- **Root Cause**: Early piston design had only 4 small oil drain holes instead of 8 large ones, causing excessive oil passage past pistons. Approximately 4 piston variants have been produced, with each iteration improving the design.
- **Resolution**: Piston replacement (newer revision). Some owners drilled additional holes as temporary DIY fix. Li Auto produced multiple piston revisions. Current production pistons are improved.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/681493250887921808/ (Вскрытие двигателя Lixiang L9)
  - https://www.drive2.ru/l/674845603586396382/ (Положили мотор на Lixiang L9)
  - https://www.drive2.ru/l/717411272110386402/ (Почему двигатель выходит из строя)
- **How Found**: WebSearch "drive2.ru Lixiang L9 вскрытие двигателя поршни масложор"

---

### 3. Двигатель — деградация топлива в баке (Fuel Degradation in Tank)
- **Models**: Both L7 and L9
- **Mileage**: Any (low mileage especially affected)
- **Season**: All (worse in city EV-only driving)
- **Symptoms**: Engine failure, detonation, piston partition destruction at under 30,000 km. Poor engine performance when generator kicks in after long EV-only driving.
- **Affected Systems**: Engine, fuel system
- **DTC Codes**: Not specified
- **Root Cause**: EREV architecture means the ICE runs infrequently (mostly EV mode in city). Fuel sits in tank for months, loses octane number, becomes source of detonation. Compounded by low-quality fuel at Russian gas stations (nominal AI-95 but actually degraded AI-92).
- **Resolution**: Only refuel at verified high-turnover gas stations. Use AI-98 exclusively. Run the engine periodically even in city driving. Don't let fuel sit for months.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/717411272110386402/ (Почему бензиновый двигатель выходит из строя)
  - https://getcar.ru/blog/obsluzhivanie-lixiang-l9-rossiya/
- **How Found**: WebSearch "drive2.ru Lixiang L9 бензин топливо двигатель малый пробег"

---

### 4. Цепь ГРМ — ненадежная конструкция (Timing Chain Reliability Concern)
- **Models**: Both L7 and L9 (all models with L2E15M engine)
- **Mileage**: Long-term concern, unclear exact failure mileage
- **Season**: All
- **Symptoms**: Chain wear, stretching, potential breakage
- **Affected Systems**: Engine timing system
- **DTC Codes**: Not specified
- **Root Cause**: Chinese engines use a thinner Morse-type chain compared to the original design specification. The thinner chain is more prone to wear and stretching.
- **Resolution**: Use only high-octane gasoline (100 RON recommended by some experts). Regularly start the engine for proper lubrication of all components. Monitor chain condition at maintenance intervals.
- **Confidence**: MEDIUM (concern raised by media, limited real failure reports)
- **Sources**:
  - https://kz.kursiv.media/2026-02-16/rmnm-motor-lixiang-raskritikovali-iz-za-nenadezhnoy-konstrukcii-cepi-grm/
- **How Found**: WebSearch "kursiv.media мотор Lixiang цепь ГРМ порваться"

---

### 5. Лидар — влага и повреждения (Lidar Moisture Ingress and Damage)
- **Models**: Both L7 and L9 (pre-facelift especially)
- **Mileage**: Any
- **Season**: Winter (ice impacts), all year (moisture)
- **Symptoms**: Lidar malfunction, autopilot errors, water visible inside lidar housing. Located in high-risk zone on roof.
- **Affected Systems**: ADAS / Lidar sensor
- **DTC Codes**: Not specified
- **Root Cause**: Insufficient sealing of lidar housing. Moisture and dirt enter through gaps. Ice stones from road strike the exposed sensor.
- **Resolution**: Preventive sealing with film (14,000 RUB for sealing + rear camera washer). Cover lidar completely with overlapping protective film. No new lidars in stock in Moscow or Russia — must order from China. Multiple lidar variants exist; which fits can only be determined after removal.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/718609464906756662/ (Герметизация лидара)
  - https://faq.liautorussia.ru/known-problems
  - https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
- **How Found**: WebSearch "drive2.ru Li Auto L7 лидар замена зима"

---

### 6. Рулевой модуль — массовый отказ кнопок (Steering Wheel Module Failure)
- **Models**: L7 (mass failure), possibly L9
- **Mileage**: Various
- **Season**: All
- **Symptoms**: Buttons on steering wheel stop glowing. Car does not respond to steering wheel commands. Loss of cruise control, wiper control, and other steering-wheel-based functions.
- **Affected Systems**: Steering wheel electronics module
- **DTC Codes**: Not specified
- **Root Cause**: Manufacturing defect in steering wheel module electronics.
- **Resolution**: Module replacement. Parts must be ordered from China. Limited availability in Russia.
- **Confidence**: HIGH
- **Sources**:
  - https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd (15 проблем кроссоверов)
  - https://faq.liautorussia.ru/known-problems
- **How Found**: WebSearch "faq.liautorussia.ru известные проблемы Li Auto"

---

### 7. Панорамная крыша — трещины (Panoramic Roof Cracking)
- **Models**: Both L7 and L9
- **Mileage**: Any
- **Season**: All (especially on highways)
- **Symptoms**: Cracks appearing at the junction between panoramic roof and windshield from minor stone impacts.
- **Affected Systems**: Body / glass
- **DTC Codes**: N/A
- **Root Cause**: Weak point in construction at the seam between panoramic roof and windshield. Windshield glass is reportedly very thin — can be damaged by insects at highway speeds.
- **Resolution**: Windshield replacement. KASKO insurance recommended.
- **Confidence**: HIGH
- **Sources**:
  - https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
  - https://faq.liautorussia.ru/known-problems
  - https://autoplt.ru/vse-minusy-v-otzyvah-vladelczev-lixiang-l7/
- **How Found**: WebSearch "autonews.ru 15 проблем кроссоверов Lixiang"

---

### 8. Омыватель — замерзание форсунок в EV режиме (Washer Fluid Freezing in EV Mode)
- **Models**: Both L7 and L9
- **Mileage**: Any
- **Season**: Winter
- **Symptoms**: Winter washer fluid rated to -10C freezes in nozzles at -3C. Washer hoses burst at -7C. Washer sprays with noticeable delay — dirty wipers complete full swipe before fluid appears.
- **Affected Systems**: Washer system, windshield
- **DTC Codes**: N/A
- **Root Cause**: When driving in full EV mode, there is no heat from the engine. The washer nozzles and lines lack sufficient heating, causing fluid to freeze at temperatures well above its rated limit.
- **Resolution**: Use -20C or -30C washer fluid even in mild frost. Avoid long EV-only drives in winter without periodically running the engine to heat engine bay components. Some owners heat nozzles manually.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/694649732147982468/ (Косяки Lixiang и их решение)
  - https://autoplt.ru/vse-minusy-v-otzyvah-vladelczev-lixiang-l7/
- **How Found**: WebSearch "drive2.ru Li Auto L9 косяки решение"

---

### 9. Дверные ручки — скрип и поломки (Door Handle Squeaking and Breakage)
- **Models**: Both L7 and L9
- **Mileage**: Various
- **Season**: Winter (freezing), all year (squeaking)
- **Symptoms**: Door handles squeak. Handles can break if frozen while in open position. Mechanism failure requiring replacement.
- **Affected Systems**: Body / door mechanism
- **DTC Codes**: N/A
- **Root Cause**: Flush door handles with electric pop-out mechanism are sensitive to cold and moisture.
- **Resolution**: Mechanism replacement costs ~4,000 RUB for just the mechanism from parts suppliers. Silicone lubricant does not help if handle is frozen open.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/667905486191862402/ (Если сломались ручки)
  - https://faq.liautorussia.ru/known-problems
- **How Found**: WebSearch "drive2.ru Li Auto L7 L9 косяки проблемы список"

---

### 10. Выдвижные пороги — коррозия (Retractable Steps Corrosion)
- **Models**: Both L7 and L9 (equipped with retractable steps)
- **Mileage**: After 1-2 winters
- **Season**: Winter (road reagents)
- **Symptoms**: Visible corrosion on retractable step platforms (выдвижные пороги). Mechanism degradation.
- **Affected Systems**: Body, step mechanism
- **DTC Codes**: N/A
- **Root Cause**: Russian road reagents (salt, chemicals) attack the step mechanism and metal components, which lack sufficient anti-corrosion protection.
- **Resolution**: Anti-corrosion treatment (bitumen resins + polymers). Professional anti-corrosion services available in Moscow starting from 6,000-15,000 RUB.
- **Confidence**: HIGH
- **Sources**:
  - https://faq.liautorussia.ru/known-problems
  - https://germanyservice.ru/anticor/antikorrozijnaya-obrabotka-avtomobilya-lixiang-(li-auto).html
  - https://www.drive2.ru/o/b/700126124688015377/
- **How Found**: WebSearch "Li Auto Lixiang коррозия ржавчина Россия подножки"

---

### 11. Тормозные колодки — редкие ZF суппорты, дорогие колодки (Brake Pads Rarity and Cost)
- **Models**: L7 (early production, first 6 months)
- **Mileage**: ~80,000 km (when pad replacement is needed)
- **Season**: All
- **Symptoms**: Cannot find compatible brake pads for rare ZF calipers installed on early L7s. Three different brake disc/pad variants exist across L7 production, impossible to determine variant by VIN.
- **Affected Systems**: Brakes
- **DTC Codes**: N/A
- **Root Cause**: Early L7s received rare ZF brake calipers used only in the first 6 months of production. Parts are scarce.
- **Resolution**: Front pads found at 40,000 RUB. Full set replacement ~70,000 RUB. Must physically inspect calipers to determine variant before ordering. Pad replacement needed at ~80,000 km.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/688693127904509635/ (Заказал ТОРМОЗА)
  - https://www.drive2.ru/l/673823332650457133/ (Заказал тормоза)
  - https://www.drive2.ru/l/670567678720630046/ (Тормоза)
- **How Found**: WebSearch "drive2.ru Li Auto L7 тормоза колодки расход масла ТО"

---

### 12. Подвеска — стук при неровностях (Suspension Knocking on Uneven Roads)
- **Models**: L7, L8, L9 (all models, "congenital defect")
- **Mileage**: From 12,000 km
- **Season**: All
- **Symptoms**: Knocking sounds only on very uneven roads (not speed bumps). Clicking sounds in suspension.
- **Affected Systems**: Suspension, front control arm
- **DTC Codes**: N/A
- **Root Cause**: Described as "congenital suspension defect" on L7-L9 models. Related to control arm bushings or ball joints.
- **Resolution**: Right front control arm replacement resolved one owner's issue. Ball joint wear observed as early as 3,000 km on L6.
- **Confidence**: MEDIUM
- **Sources**:
  - https://www.drive2.ru/l/706632484745383761/ (Купил и сразу ремонт)
  - https://www.drive2.ru/l/688119182834803439/ (Китайца починили, едем дальше)
- **How Found**: WebSearch "drive2.ru Li Auto L7 подвеска стук рычаг нижний"

---

### 13. Фары — слабое освещение (Poor Headlight Illumination)
- **Models**: Both L7 and L9
- **Mileage**: N/A (design issue)
- **Season**: All (worse in winter darkness)
- **Symptoms**: Poor road illumination at night. Automatic high-beam sometimes flashes oncoming traffic. Quality described as "complete garbage" compared to Audi Matrix lighting.
- **Affected Systems**: Lighting
- **DTC Codes**: N/A
- **Root Cause**: China has excellent road lighting infrastructure, so Li Auto did not invest in power-hungry headlights. The headlights are designed for Chinese road conditions, not Russian unlit highways.
- **Resolution**: No factory fix available. Some owners install aftermarket headlight upgrades.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/694649732147982468/ (Косяки Lixiang и их решение)
  - https://autoplt.ru/vse-minusy-v-otzyvah-vladelczev-lixiang-l7/
- **How Found**: WebSearch "drive2.ru Li Auto L9 косяки проблемы список"

---

### 14. Телематический модуль и SIM-карта (Telematics Module / SIM Card Issues)
- **Models**: Both L7 and L9
- **Mileage**: Any (from new)
- **Season**: All
- **Symptoms**: Vehicle loses internet connectivity. OTA updates stop arriving. Telematics module fails when installing Russian SIM card. App stops receiving data from vehicle.
- **Affected Systems**: Telematics / connectivity
- **DTC Codes**: N/A
- **Root Cause**: Telematics modules sometimes fail during SIM card installation. SIM may need resoldering due to poor initial installation work. Chinese-spec module not fully compatible with Russian networks.
- **Resolution**: SIM card resoldering at service center. Firmware version check (some OTA versions broke connectivity). 5 reasons for missing OTA updates documented by community.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/706362004884950860/ (5 причин почему не приходит OTA)
  - https://www.drive2.ru/l/671610015743748069/ (Установка сим карты)
  - https://www.drive2.ru/l/701924925711077946/ (не работает приложение)
  - https://faq.liautorussia.ru/known-problems
- **How Found**: WebSearch "drive2.ru Li Auto L9 косяки проблемы поломки список"

---

### 15. Формальдегид в салоне (Formaldehyde Off-Gassing in Cabin)
- **Models**: L7 (reported), likely L9 too
- **Mileage**: New cars
- **Season**: Summer (heat increases off-gassing)
- **Symptoms**: Constant headaches from large amounts of formaldehyde evaporating from interior materials.
- **Affected Systems**: Interior, cabin air quality
- **DTC Codes**: N/A
- **Root Cause**: Interior materials contain formaldehyde-releasing compounds. Standard issue for Chinese-manufactured vehicles with extensive soft interior materials.
- **Resolution**: Extended airing of the vehicle. Some owners use activated carbon air purifiers. Issue diminishes with time.
- **Confidence**: MEDIUM (individual reports, not universally confirmed)
- **Sources**:
  - https://autoplt.ru/vse-minusy-v-otzyvah-vladelczev-lixiang-l7/
- **How Found**: WebSearch "autoplt.ru минусы отзывы владельцев Lixiang L7"

---

### 16. Регистрация в ГИБДД — отказы (Vehicle Registration Refusals)
- **Models**: Both L7 and L9 (gray-import vehicles)
- **Mileage**: N/A (registration issue)
- **Season**: All (wave of refusals in early 2026)
- **Symptoms**: GIBDD inspectors refuse to register vehicles. Vehicles seized for expert examination. Owners given official refusals and prescriptions for VIN plate inspection.
- **Affected Systems**: N/A (bureaucratic/legal issue)
- **DTC Codes**: N/A
- **Root Cause**: Doubts by inspectors about authenticity of VIN identification sticker. Gray-import vehicles have manufacturer plates that raise questions about factory origin. GOST certification obtained by official distributor Sinomach Auto in late 2025, but issue persists.
- **Resolution**: If marking corresponds to factory execution, court can order registration. Otherwise buyer can demand contract cancellation. Purchase from official dealer with OTTS certification recommended.
- **Confidence**: HIGH
- **Sources**:
  - https://www.autonews.ru/news/69983ab49a79474a4af55341
  - https://www.rbcautonews.ru/news/6998bdf29a794715c71d882e
  - https://auto.mail.ru/article/118854-v-rf-idet-volna-otkazov-v-registratsii-li-auto/
- **How Found**: WebSearch "Li Auto Lixiang учет ГИБДД проблема Россия"

---

## Real-World Range and Fuel Consumption Data

### EV-Only Range
- **Summer (city)**: 180-210 km on 42.8 kWh battery (2-4 days without charging/refueling)
- **Winter (Moscow)**: ~1% battery per 1 km in best case (roughly 100-130 km effective range)
- **Highway**: Significantly reduced due to aero drag

### Fuel Consumption (Hybrid/Generator Mode)
- **City mixed**: 20-22 kWh/100km on EV
- **Highway summer**: 6.5-7.0 L/100km at moderate speed
- **Highway winter**: 9.0-9.5 L/100km at moderate speed
- **Highway at 150 km/h**: 11 L/100km (Moscow-SPb corridor)
- **Total range**: 1,050-1,150 km (less than manufacturer's claim)

### Maintenance Costs
| Item | Interval | Cost (RUB) |
|------|----------|------------|
| Engine oil + filter | 10,000 km (5,000 km recommended in Russia) | Part of ТО |
| Spark plugs | 40,000 km | Included in ТО |
| Front/rear differential oil | 80,000 km | Part of ТО |
| Brake fluid | 80,000 km | Part of ТО |
| ТО-1 (materials + labor) | First service | 37,602 RUB |
| Regular maintenance | Every 5,000 km | 10,000-20,000 RUB |
| Diagnostics | Per visit | 5,000-16,500 RUB |
| Suspension filter | As needed | 15,000-30,000 RUB |
| Suspension drying | Annual | 10,000 RUB |
| Firmware update | As needed | 16,500-55,000 RUB |
| **Total annual** | Active use | **100,000-200,000 RUB** |
| Transport tax (L7) | Annual | 4,588 RUB |

### Recommended Oils (L9)
- Viscosity: 0W-30 (C2/C3 specification)
- Volume: 3.7 liters
- Brands: RAVENOL FES 0W-30, G-ENERGY Synth Super Start 0W-30, LIQUI MOLY HC Special Tec F 0W-30, SHELL Helix Ultra ECT 0W-30

---

## Methodology

### Search Queries That Yielded Results
1. `drive2.ru Li Auto L7 бортжурнал ремонт проблемы` — main Drive2 logbooks
2. `drive2.ru Li Auto L9 бортжурнал поломка обслуживание` — L9 maintenance posts
3. `drive2.ru lixiang L7 L9 пневмоподвеска проблема зимой ремонт` — air suspension specifics
4. `"drive2.ru" Li Auto L9 "косяки" OR "проблемы" OR "поломки" список` — comprehensive issues
5. `drive2.ru Li Auto L7 тормоза колодки расход масла ТО стоимость` — brake and maintenance costs
6. `liautorussia.ru Li Auto клуб форум FAQ` — discovered liautorussia.ru FAQ
7. `faq.liautorussia.ru известные проблемы Li Auto L7 L9 список` — known problems page
8. `autonews.ru 15 проблем кроссоверов Lixiang Li Auto в России` — 15-problem article
9. `drive2.ru Lixiang L9 вскрытие двигателя поршни масложор проблема` — engine teardown
10. `drive2.ru Lixiang L9 бензин топливо "выходит из строя" двигатель малый пробег` — fuel degradation
11. `Lixiang L7 L9 зима запас хода электричестве реальный расход отзыв` — real range data
12. `kursiv.media Lixiang L7 170000 км осмотр что сломалось коррозия` — 170K km inspection
13. `kursiv.media мотор Lixiang цепь ГРМ порваться` — timing chain concerns
14. `Li Auto Lixiang коррозия ржавчина антикоррозия Россия подножки` — corrosion issues
15. `Li Auto Lixiang учет ГИБДД проблема Россия ОТТС` — registration wave
16. `autopilotclub.ru Lixiang L7 реальный расход стоимость владения` — cost of ownership
17. `Li Auto L9 L7 отзыв recall Китай 2024 2025` — recalls

### Methodology Notes
- Drive2.ru blocks direct scraping (403), so all content was found via WebSearch with Google indexing of Drive2 posts
- Most Drive2 content is accessible via search engine snippets and metadata
- liautorussia.ru (faq.liautorussia.ru) proved to be the single most comprehensive source for known issues
- autonews.ru article "15 проблем кроссоверов Lixiang" is a key aggregated source based on club data
- getcar.ru articles already in KB are well-targeted and cover reliability topics thoroughly
- chinamobil.ru has Li Auto L9 reviews/opinions section but limited unique content
- autopilotclub.ru forum has active discussions about ownership costs

---

## Russian Li Auto Community Map

### Primary Communities
| Resource | URL | Type | Members/Size | Language |
|----------|-----|------|-------------|----------|
| Li Auto Club Russia (Telegram) | https://t.me/lixiangautorussia | Telegram group | 37,000+ members | RU |
| Li Auto Club Russia (FAQ/Wiki) | https://faq.liautorussia.ru | Knowledge base | Comprehensive FAQ | RU |
| Li Auto Club Russia (Main) | https://liautorussia.ru | Website + shop | Main hub | RU |
| Drive2.ru Li Auto L7 | https://www.drive2.ru/experience/liauto/g657426865501256680 | Forum/blogs | Active logbooks | RU |
| Drive2.ru Li Auto L9 | https://www.drive2.ru/experience/liauto/g657427415257062407 | Forum/blogs | Active logbooks | RU |
| Drom.ru Li Reviews | https://www.drom.ru/reviews/li/ | Owner reviews | 54+ reviews | RU |
| AutopilotClub.ru Lixiang | https://autopilotclub.ru/forums/topic/4493-lixiang-l7-v-rossii/ | Forum | Active threads | RU |

### News and Review Sources
| Resource | URL | Type | Notes |
|----------|-----|------|-------|
| Autoreview.ru | https://autoreview.ru | Professional reviews | Multiple comparative tests Li L7/L9 |
| GetCar.ru | https://getcar.ru | Blog/reviews | 4+ articles on L9 reliability/problems |
| Autonews.ru | https://www.autonews.ru | News | Key "15 problems" article |
| Kursiv.media (KZ) | https://kz.kursiv.media | News | L7 170K km inspection, timing chain |
| Motor.ru | https://motor.ru | Reviews | L9 test drive |
| Kolesa.ru | https://www.kolesa.ru | Reviews | L7 test drive + BMW X7 vs L9 costs |
| Autoplt.ru | https://autoplt.ru | Reviews | Owner complaints aggregation |
| 110km.ru | https://110km.ru | Reviews | Owner reviews with photos |

### Parts Suppliers
| Resource | URL | Notes |
|----------|-----|-------|
| LiCars | https://licars.ru | 700+ parts, direct from China |
| Major Auto (Lixiang) | https://www.major-auto.ru/zapchasti/lixiang_li_auto/ | Official dealer network |
| Li-Auto.com | https://li-auto.com/services/zakaz-zapchastey/ | Dealer + parts order |

### Chinese Car Forums (General)
| Resource | URL | Li Auto Coverage |
|----------|-----|-----------------|
| chinamobil.ru | https://www.chinamobil.ru/com/ideal/l9/ | L9 opinions/reviews |
| kitaec.ua | https://kitaec.ua/vse-dlya-elektromobiley/podbor-po-avto/li/ | Parts catalog L6-L9 |

---

## Service Infrastructure in Russia

### Official Presence (as of early 2026)
- **Official distributor**: Sinomach Auto (from late 2025)
- **OTTS certification**: Obtained for L6, L7, L9 (GOST-compliant VIN plates)
- **Official dealer network**: 20+ dealers selected, 35+ planned
- **Cities with dealers**: Moscow (7), St. Petersburg, Kazan, Tula, Orenburg, Naberezhnye Chelny, Ufa, Samara, Mineralnye Vody, Kirov, Yekaterinburg, Krasnodar, Stavropol
- **Warranty (official)**: 3 years / 100,000 km (vehicle), 8 years / 160,000 km (battery + electric drive), 6 years / 100,000 km (corrosion-perforation)

### Official Pricing (2026 RRP)
- L6: 6,890,000 - 7,190,000 RUB
- L7: 7,690,000 - 8,390,000 RUB
- L9: from 9,490,000 RUB

### Independent Service Centers (Moscow)
| Service | URL | Specialization |
|---------|-----|---------------|
| Lixiang-STO | https://lixiang-sto.ru | Full service, air suspension repair |
| RUSLIXIANG | https://ruslixiang.ru | Maintenance from 6,000 RUB |
| ЭЛЕКТРОМЭН | https://elektroman.pro | Air suspension from 15,000 RUB |
| E.N.Cars | (Drive2 referenced) | ТО service |
| Li-Motors | https://li-motors.ru/service | Full service + test drives |
| LiHome.pro | https://lihome.pro | Service + repair |

### Parts Availability Issues
- **Delivery time**: 3 weeks minimum (popular parts from Moscow stock), 2-3 months for rare parts ordered from China
- **Future outlook**: By Q4 2025 / 2027, Li Auto may open spare parts warehouses in Russia, reducing wait to 1 month
- **Key concern**: Vehicle components are heavily coded to each specific vehicle — cannot be freely swapped between cars
- **Limited serviceable**: Unlike BMW/Mercedes that can be repaired at many shops, Lixiang can only be properly serviced at a few specialized centers

### Key Takeaway for Service
The Li Auto Club Russia considers the L9 to be the most reliable model in the lineup, with vehicles reaching 200,000 km without significant issues. However, the main risk in Russia is not the car itself but the **service infrastructure** — limited parts availability, specialized knowledge required, and component coding that restricts third-party repairs.
