# Agent 2: Drom.ru, Otzovik, iRecommend -- Owner Reviews Research

> **Date**: 2026-03-06
> **Sources**: drom.ru (5kopeek + reviews), otzovik.com, irecommend.ru, 110km.ru, getcar.ru, autonews.ru, kursiv.media, faq.liautorussia.ru
> **Focus**: Real owner problems, faults, seasonal issues with Li Auto L7 and L9

---

## Aggregate Statistics

| Metric | Li L7 | Li L9 |
|--------|-------|-------|
| Drom rating | 9.3/10 ("отлично!") | 9.1/10 ("отлично") |
| Drom reviews count | 154 | ~88 |
| 110km.ru reviews | 8 + 2 comments | 8 + 3 comments |
| Otzovik.com reviews | Very few (mostly bloggers) | None (only toy car) |
| iRecommend.ru | No car reviews found | No car reviews found |
| Overall satisfaction | HIGH | HIGH |

**Sales in Russia (Jan-Sep 2025)**: L7 = 4,128 units (leader), L6 = 2,478, L9 = 1,629

---

## Issue Patterns Found

### 1. Пневмоподвеска -- отказ компрессора / потеря высоты
- **Models**: Both (L7 more affected with AMK compressor)
- **Mileage**: 10,000--15,000 km (compressor failure); can appear earlier in winter
- **Season**: Winter (below 0C, critical below -15C)
- **Symptoms**: Car "sits down," loses ride height, error message on dashboard, knocking sounds, air leaks. Compressor accumulates moisture; in winter moisture freezes in valves, in summer rust on bearings.
- **Affected Systems**: Pneumatic suspension (air springs, compressor, valves)
- **DTC Codes**: Not specifically mentioned, dashboard error displayed
- **Root Cause**: AMK compressor (some L7 models) is moisture-susceptible. WABCO (L8/L9) is more reliable. Regeneration cannot remove accumulated moisture. Russian road reagents and potholes accelerate wear.
- **Resolution**: Compressor replacement (39,000--100,000 rubles). Check suspension every 5,000 km (5,000--10,000 rubles). Dry system before winter (10,000 rubles). Spare parts wait 2-3 months from China.
- **Frequency**: Most common issue. 70% of 2024 breakdowns are suspension + electronics related (getcar.ru). Listed as #1 problem by Li Auto Club Russia.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drom.ru/reviews/li/l7/5kopeek/
  - https://www.drom.ru/reviews/li/l9/5kopeek/
  - https://getcar.ru/blog/polomki-lixiang-l9-rossiya/
  - https://kz.kursiv.media/2025-06-09/kmlz-li-auto-problems/
  - https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
  - https://faq.liautorussia.ru/known-problems
  - https://www.drive2.ru/l/700705017560044478/
- **How Found**: WebSearch "drom.ru Li L7 5kopeek", "Lixiang L9 L7 косяки пневмоподвеска зимой"

---

### 2. Разряд батареи зимой / потеря запаса хода
- **Models**: Both
- **Mileage**: Any
- **Season**: Winter (critical below -20C)
- **Symptoms**: Battery loses 15--20% capacity in cold. At -30C, heater consumes 8--9 kW; even standing still, charge lasts ~3 hours. If starting at 20% charge without preheating, battery can die in 15--20 minutes. Charging requires 30 min warmup at -20C before battery accepts charge.
- **Affected Systems**: Battery (CATL), thermal management, HVAC
- **DTC Codes**: Not mentioned
- **Root Cause**: Standard lithium battery behavior in extreme cold. Battery heater draws significant power. Range drops ~2x compared to summer.
- **Resolution**: Preheat before driving, keep charge above 20%, use garage parking when possible. L7 battery (40 kWh) gives ~100 km even with heater. L9 (52.3 kWh) gives ~120 km winter range (vs 180 km summer).
- **Frequency**: Universal -- all owners in cold regions report this
- **Confidence**: HIGH
- **Sources**:
  - https://www.drom.ru/reviews/li/l7/5kopeek/
  - https://li-auto.com/news/lisyan-v-ekspluatatsii-zimoy/
  - https://progorod35.ru/novosti-rossii/22418
  - https://www.drom.ru/reviews/li/l9/1458447/
- **How Found**: WebSearch "Li Auto L7 проблемы зимой батарея", "drom.ru Li L7 отзыв расход зимой"

---

### 3. Расход топлива выше заявленного
- **Models**: Both
- **Mileage**: Any
- **Season**: All (worse in winter)
- **Symptoms**: Real highway consumption at 125 km/h = 11 L/100km (vs factory claims). Max range ~700 km highway (vs claimed 1100 km). In city winter "gasoline mode" = 10--12 L/100km. By 37,000 km, consumption rises to 12 L. Using AI-92 fuel drops range by 20%.
- **Affected Systems**: Range extender engine (1.5L 3-cylinder)
- **DTC Codes**: None
- **Root Cause**: 3-cylinder range extender is noisy and fuel-hungry under load. Heavy vehicle (2.5+ tons). Cold weather increases consumption.
- **Resolution**: Use only RON-100 fuel for engine longevity. Keep battery charged to minimize engine use. City driving is much more economical (5--7 L/100km mixed).
- **Frequency**: Very common complaint. Multiple drom/getcar reviewers mention it.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drom.ru/reviews/li/l7/5kopeek/
  - https://www.drom.ru/reviews/li/l9/1458447/
  - https://getcar.ru/blog/lixiang-l9-ne-edet/
  - https://progorod35.ru/novosti-rossii/22418
- **How Found**: WebSearch "drom.ru Li L7 расход зимой", "Li Auto L9 проблемы владельцев"

---

### 4. Цепь ГРМ -- растяжение и обрыв
- **Models**: Both (same 1.5L engine)
- **Mileage**: 200,000--376,000 km (durability test showed failure at 376K)
- **Season**: All
- **Symptoms**: Timing chain stretches, tensioner fails, chain skips phases. Valves crash into pistons, destroying cylinder head. Engine becomes inoperable.
- **Affected Systems**: Engine (1.5L range extender), timing chain, tensioner
- **DTC Codes**: Engine failure codes (specific codes not documented)
- **Root Cause**: Lixiang uses a thinner Morse-type timing chain vs original design. In hybrid mode, engine runs under constant load as generator at 3,500--4,000 RPM, accelerating wear. Oil changes every 10--12K km insufficient for hybrid duty cycle. Timing chain never inspected per service schedule.
- **Resolution**: Inspect timing chain every 100--120K km. Change oil every 7--8K km for heavy highway use. Use RON-100 fuel. Capital engine repair cost: less than a contract replacement motor.
- **Frequency**: Rare at normal mileage (<100K km). Critical risk at 200K+ km without chain inspection.
- **Confidence**: HIGH (documented durability test by Faker group in Russia)
- **Sources**:
  - https://carexpo.ru/2025/12/08/li-auto-l9-proshel-v-rf-367-tysyach-km-i-slomalsya-skolko-stoit-remont/
  - https://kz.kursiv.media/2026-02-16/rmnm-motor-lixiang-raskritikovali-iz-za-nenadezhnoy-konstrukcii-cepi-grm/
  - https://auto.mail.ru/article/112737-gibrid-li-auto-l9-proshel-367-tyisyach-km-i-slomalsya-prichinyi-i-stoimost-remonta/
  - https://av.by/news/entiziasti_proverili_dolgovechnost_gibrida_li_auto_l9
- **How Found**: WebSearch "Li Auto L9 367000 км поломка двигатель цепь ГРМ"

---

### 5. Шумоизоляция недостаточная для премиума
- **Models**: Both
- **Mileage**: Any (from new)
- **Season**: All
- **Symptoms**: Excessive road noise at highway speeds. Cabin squeaks and rattles, especially at high speed. Wind noise noticeable. Some mention the 3-cylinder range extender is noisy when engaged.
- **Affected Systems**: Body, insulation, range extender
- **DTC Codes**: None
- **Root Cause**: Insufficient factory sound deadening for a vehicle in the 7+ million ruble price class. 3-cylinder engine inherently noisier than 4-cylinder.
- **Resolution**: Aftermarket sound deadening (additional insulation). Keep battery charged to minimize engine run time.
- **Frequency**: Very common in drom 5kopeek. Consistently listed as a top disadvantage.
- **Confidence**: HIGH
- **Sources**:
  - https://www.drom.ru/reviews/li/l7/5kopeek/
  - https://www.drom.ru/reviews/li/l9/5kopeek/
  - https://getcar.ru/blog/shum-lixiang-l9-prichiny/
- **How Found**: WebSearch "drom.ru Li L7 5kopeek недостатки"

---

### 6. Тормоза -- ватные / неравномерный износ колодок
- **Models**: Both (L9 especially)
- **Mileage**: From new (braking feel); 8,000 km (premature pad wear)
- **Season**: All
- **Symptoms**: L9 brakes described as "ватные" (spongy). Long stopping distance on highway. Inner brake pads can wear to zero after only 8,000 km. Uneven pad wear indicates caliper not releasing properly.
- **Affected Systems**: Brakes (calipers, pads, discs)
- **DTC Codes**: None
- **Root Cause**: Regenerative braking calibration may cause uneven mechanical brake usage. Caliper sticking issue on some units.
- **Resolution**: Replace pads (required 2 full replacements in one case). Check brake pad/disc condition every 10--15K km. Standard pad replacement interval: 40--50K km per manufacturer.
- **Frequency**: MEDIUM -- several reviewers on drom and 110km.ru mention spongy brakes
- **Confidence**: MEDIUM
- **Sources**:
  - https://110km.ru/opinion/lixiang/l9/
  - https://www.drive2.ru/l/679038866056810905/
  - https://www.drive2.ru/l/688693127904509635/
- **How Found**: WebSearch "Lixiang L7 L9 тормоза колодки диски износ скрип"

---

### 7. Электроника / мультимедиа -- сбои, зависания
- **Models**: Both
- **Mileage**: Any
- **Season**: All
- **Symptoms**: Multimedia system freezing, screen reboots. Connection to mobile app drops. Digital key locks after OTA update. Snapdragon chip and OLED screens fail due to poor compatibility with Russian SIM cards and voltage fluctuations. OTA 4.6.5 caused autopilot errors for 10% of owners. OTA 8.0 caused autopilot to lose lane marking visibility.
- **Affected Systems**: Infotainment, connectivity, OTA system
- **DTC Codes**: Not mentioned
- **Root Cause**: Software incompatibility with Russian networks. Aggressive OTA update schedule (31 updates in one month). No rollback mechanism.
- **Resolution**: Service center firmware reflash (25,000 rubles). Wait for next OTA fix. Master account issues require Chinese phone number.
- **Frequency**: Common -- multiple sources report software glitches
- **Confidence**: HIGH
- **Sources**:
  - https://getcar.ru/blog/problemy-lixiang-l9-2024/
  - https://faq.liautorussia.ru/known-problems
  - https://www.drive2.ru/l/714032747756141707/
  - https://progorod35.ru/novosti-rossii/22418
- **How Found**: WebSearch "Lixiang Li Auto ADAS автопилот проблемы ошибки"

---

### 8. LiDAR -- повреждения и загрязнение
- **Models**: Both (pre-facelift L7 has lidar seal issue)
- **Mileage**: Any
- **Season**: Winter (ice impact), all seasons (stone chips)
- **Symptoms**: LiDAR positioned in high-risk zone on roof. Ice buildup and small stone damage. Pre-facelift L7 has seal problems allowing moisture ingress. False ADAS warnings.
- **Affected Systems**: ADAS, LiDAR sensor
- **DTC Codes**: Not mentioned
- **Root Cause**: LiDAR placement on roof edge exposes it to road debris and ice. Design vulnerability.
- **Resolution**: Protective film/cover. Seal replacement on pre-facelift L7.
- **Frequency**: MEDIUM -- mentioned by Li Auto Club Russia and Autonews
- **Confidence**: HIGH
- **Sources**:
  - https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
  - https://kz.kursiv.media/2025-06-09/kmlz-li-auto-problems/
  - https://faq.liautorussia.ru/known-problems
- **How Found**: WebSearch "autonews.ru 15 проблем кроссоверов Lixiang"

---

### 9. Автопилот (ADAS) -- ошибки на российских дорогах
- **Models**: Both
- **Mileage**: Any
- **Season**: All (worse in rain/snow)
- **Symptoms**: NOA 6.0 cannot correctly perform lane changes on Russian roads (incomplete maps). Adaptive cruise maxes out at 130 km/h (insufficient for Russian highways). Phantom braking for trucks in adjacent lanes. Autopilot loses reliability in rain/snow. Auto high beam activates into oncoming traffic. After airbag deployment, vehicle becomes immobilized ("brick mode").
- **Affected Systems**: ADAS, NOA, LCC, auto high beam
- **DTC Codes**: Not mentioned
- **Root Cause**: Maps not fully adapted for Russia. Sensor fusion issues in precipitation. Post-crash lockdown by design.
- **Resolution**: Disable auto high beam manually. Wait for better OTA map data. Post-crash: diagnostic equipment needed to clear airbag codes.
- **Frequency**: MEDIUM -- several drive2 and drom reviews mention this
- **Confidence**: HIGH
- **Sources**:
  - https://www.drive2.ru/l/714032747756141707/
  - https://www.drive2.ru/l/683166707585399571/
  - https://www.ixbt.com/news/2024/01/18/vladelcy-populjarnyh-v-rossii-avtomobilej-li-auto-stolknulis-s-bolshimi-problemami-posle-dtp-avtomobil-prevrashaetsja-v.html
  - https://carnewschina.com/2023/01/27/li-l9-user-claimed-driving-assistance-system-failed-resulting-in-an-accident/
- **How Found**: WebSearch "Lixiang Li Auto ADAS автопилот проблемы ошибки ДТП Россия"

---

### 10. Запчасти -- дефицит и долгое ожидание
- **Models**: Both
- **Mileage**: Any
- **Season**: All
- **Symptoms**: Replacement parts and tires hard to find in Russia. Spare parts wait 2-3 months from China. Few authorized service centers (basically 2-3 in all of Russia). Vehicle platform is heavily coded -- each component tied to specific VIN, making third-party repair difficult.
- **Affected Systems**: All (aftermarket supply chain)
- **DTC Codes**: None
- **Root Cause**: No official Lixiang dealer network in Russia. Grey market imports. Component VIN binding.
- **Resolution**: Order parts from China in advance. Join Li Auto Club Russia Telegram (37,000 members) for sourcing tips.
- **Frequency**: Very common concern across all review platforms
- **Confidence**: HIGH
- **Sources**:
  - https://www.drom.ru/reviews/li/l9/5kopeek/
  - https://110km.ru/opinion/lixiang/l7/
  - https://getcar.ru/blog/polomki-lixiang-l9-rossiya/
- **How Found**: WebSearch "drom.ru Li L9 5kopeek проблемы"

---

### 11. Кожа салона -- пожелтение и износ
- **Models**: Both
- **Mileage**: 20,000--37,000 km
- **Season**: All
- **Symptoms**: Light-colored leather yellows and wears. Seats show wear marks. Steering wheel shows use. By 37K km, interior loses "new car" feel.
- **Affected Systems**: Interior (leather upholstery)
- **DTC Codes**: None
- **Root Cause**: Light-colored Nappa leather is inherently less durable. Chinese leather processing may be less robust than European alternatives.
- **Resolution**: Professional leather cleaning/conditioning. Seat covers.
- **Frequency**: MEDIUM -- mentioned in 37K km review and others
- **Confidence**: MEDIUM
- **Sources**:
  - https://progorod35.ru/novosti-rossii/22418
  - https://kz.kursiv.media/2026-03-05/rmnm-lixiang-l7-proyekhal-170-tys-km-sgnil-li-krossover/
- **How Found**: WebSearch "Lixiang L9 37000 км отзыв владельца"

---

### 12. Масло в КПП -- течь сальников
- **Models**: L9 (possibly both)
- **Mileage**: 20,000+ km
- **Season**: All
- **Symptoms**: Gearbox oil seal leaks after 20,000 km.
- **Affected Systems**: Transmission
- **DTC Codes**: Not mentioned
- **Root Cause**: Seal material or assembly quality issue
- **Resolution**: Seal replacement, cost ~30,000 rubles
- **Frequency**: LOW-MEDIUM (getcar.ru report)
- **Confidence**: MEDIUM
- **Sources**:
  - https://getcar.ru/blog/polomki-lixiang-l9-rossiya/
- **How Found**: WebSearch "getcar.ru поломки LiXiang L9 Россия"

---

### 13. Панорамная крыша -- трещины
- **Models**: Both
- **Mileage**: Any
- **Season**: All
- **Symptoms**: Panoramic roof cracks at junction with windshield when hit by small stones. Windshield itself is weak and scratches easily.
- **Affected Systems**: Body (glass)
- **DTC Codes**: None
- **Root Cause**: Glass quality and mounting design
- **Resolution**: Windshield replacement (expensive, long wait for parts)
- **Frequency**: MEDIUM
- **Confidence**: MEDIUM
- **Sources**:
  - https://kz.kursiv.media/2025-06-09/kmlz-li-auto-problems/
  - https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd
- **How Found**: WebSearch "kursiv.media поломки LiXiang"

---

### 14. Выдвижные пороги -- коррозия
- **Models**: Both
- **Mileage**: 15,000+ km (in Russian conditions)
- **Season**: Winter (road reagents)
- **Symptoms**: Extending door thresholds/running boards develop corrosion from Russian road salt and chemical treatments
- **Affected Systems**: Body (extending steps mechanism)
- **DTC Codes**: None
- **Root Cause**: Mechanism not designed for aggressive road chemicals used in Russia
- **Resolution**: Anti-corrosion treatment. Regular cleaning.
- **Frequency**: LOW-MEDIUM
- **Confidence**: MEDIUM
- **Sources**:
  - https://kz.kursiv.media/2025-06-09/kmlz-li-auto-problems/
- **How Found**: WebSearch "kursiv.media поломки LiXiang"

---

### 15. Автоматические шторки радиатора -- обледенение
- **Models**: Both
- **Mileage**: Any
- **Season**: Winter
- **Symptoms**: Automatic shutters in front bumper clog with snow/ice, restricting air intake and preventing efficient charging while driving
- **Affected Systems**: Cooling system, charging
- **DTC Codes**: Not mentioned
- **Root Cause**: Design not optimized for Russian winter conditions
- **Resolution**: Manual cleaning. Some owners disable automatic mode.
- **Frequency**: LOW-MEDIUM
- **Confidence**: MEDIUM
- **Sources**:
  - https://kz.kursiv.media/2025-06-09/kmlz-li-auto-problems/
- **How Found**: WebSearch "kursiv.media поломки LiXiang"

---

### 16. Кондиционер -- поломка компрессора летом
- **Models**: Both
- **Mileage**: Variable
- **Season**: Summer
- **Symptoms**: Air conditioner compressor failure in hot weather
- **Affected Systems**: HVAC (A/C compressor)
- **DTC Codes**: Not mentioned
- **Root Cause**: Compressor reliability issue under high thermal load
- **Resolution**: Compressor replacement
- **Frequency**: LOW-MEDIUM
- **Confidence**: MEDIUM
- **Sources**:
  - https://kz.kursiv.media/2025-06-09/kmlz-li-auto-problems/
- **How Found**: WebSearch "kursiv.media поломки LiXiang"

---

### 17. Рулевая рейка -- люфт
- **Models**: Both
- **Mileage**: Variable
- **Season**: All
- **Symptoms**: Steering rack develops play/slack
- **Affected Systems**: Steering
- **DTC Codes**: Not mentioned
- **Root Cause**: Wear or assembly tolerance issue
- **Resolution**: Tightening steering rack at specialized service center
- **Frequency**: LOW (singular cases per Li Auto Club)
- **Confidence**: MEDIUM
- **Sources**:
  - https://faq.liautorussia.ru/known-problems
- **How Found**: WebSearch "faq.liautorussia.ru известные проблемы"

---

### 18. Утечка хладагента кондиционера
- **Models**: Both
- **Mileage**: Variable
- **Season**: All
- **Symptoms**: A/C refrigerant loss, reduced cooling performance
- **Affected Systems**: HVAC (A/C system)
- **DTC Codes**: Not mentioned
- **Root Cause**: Defective one-time use valve in A/C system
- **Resolution**: Valve replacement and refrigerant recharge
- **Frequency**: LOW (singular cases per Li Auto Club)
- **Confidence**: MEDIUM
- **Sources**:
  - https://faq.liautorussia.ru/known-problems
- **How Found**: WebSearch "faq.liautorussia.ru известные проблемы"

---

## Top 10 Most Common Complaints (ranked by frequency)

| # | Problem | Frequency | Models |
|---|---------|-----------|--------|
| 1 | Пневмоподвеска (компрессор, влага, потеря высоты) | Very High | Both (L7 AMK worse) |
| 2 | Разряд батареи зимой / потеря запаса хода | Very High | Both |
| 3 | Расход топлива выше заявленного | High | Both |
| 4 | Недостаточная шумоизоляция | High | Both |
| 5 | Дефицит запчастей / мало сервисов | High | Both |
| 6 | Электроника / мультимедиа / OTA сбои | High | Both |
| 7 | Ошибки ADAS / автопилота | Medium | Both |
| 8 | Тормоза ватные / неравномерный износ | Medium | L9 mostly |
| 9 | LiDAR повреждения | Medium | Both |
| 10 | Кожа салона пожелтение | Medium | Both |

---

## Average Satisfaction Ratings

| Platform | L7 | L9 |
|----------|-----|-----|
| Drom.ru | 9.3/10 | 9.1/10 |
| Overall impression | Positive (reliable daily driver) | Positive (luxury family SUV) |

Despite the issues listed above, the vast majority of owners rate both models as excellent. The Li Auto Club Russia FAQ explicitly states that "most owners consider Li Auto vehicles problem-free for daily use" and that "the power unit, pneumatic suspension, control systems, and multimedia all work stably" for the majority.

---

## Mileage Distribution of Problems

| Mileage Range | Typical Issues |
|---------------|---------------|
| 0--5,000 km | Software/OTA glitches, ADAS learning, brake feel adjustment |
| 5,000--15,000 km | Pneumatic suspension compressor (if AMK), brake pad uneven wear |
| 15,000--30,000 km | Transmission oil seal leak, leather yellowing starts |
| 30,000--50,000 km | Interior wear visible, increased fuel consumption |
| 50,000--100,000 km | Brake disc/pad standard replacement, possible A/C compressor |
| 100,000--200,000 km | Timing chain inspection needed, general wear |
| 200,000+ km | Timing chain failure risk, capital engine repair possible |

---

## L7 vs L9 Differences

| Aspect | L7 | L9 |
|--------|-----|-----|
| Suspension compressor | AMK (problem) or WABCO | WABCO (more reliable) |
| Battery capacity | 40 kWh | 52.3 kWh |
| Winter EV range | ~100 km | ~120 km |
| Braking feel | Normal | "Spongy" (more complaints) |
| LiDAR seal issue | Yes (pre-facelift) | Not reported |
| Price sensitivity | Lower price = higher sales | Higher price = fewer units |
| Long-term reliability (170K km test) | Passed well | Passed well |

---

## Maintenance Costs Summary (Russia)

| Service | Cost (rubles) | Interval |
|---------|---------------|----------|
| TO-0 (first maintenance) | 10,800 | 1,000 km / 1 year |
| Oil + filter change | ~10,000--15,000 | 10,000 km / 1 year |
| Cabin filter | ~3,000--5,000 | 20,000 km / 1 year |
| Spark plugs | ~5,000--8,000 | 40,000 km |
| Transmission fluid | ~15,000--20,000 | 80,000 km / 4 years |
| Brake fluid | ~5,000--8,000 | 80,000 km / 4 years |
| Pneumatic suspension check | 5,000--10,000 | Every 5,000 km |
| Suspension compressor replacement | 39,000--100,000 | If failed |
| Firmware reflash at service | 25,000 | If OTA caused issues |
| Battery repair (major) | Up to 500,000 | Rare |

---

## Notable Long-Term Test Results

### L9 -- 376,000 km durability test (Faker group, Russia)
- Engine failed at 376K km: timing chain tensioner broke
- Valves crashed into pistons, cylinder head destroyed
- Cylinder ovality >0.1mm, crack in engine block
- Oil changes were done every 10--12K km but chain never inspected
- Repair was cheaper than contract replacement engine
- **Conclusion**: Timing chain should be inspected at 100--120K km

### L7 -- 170,000 km inspection (kursiv.media, March 2026)
- No serious technical problems found
- Body shows use: sandblasting on mirrors, bumper scuffs, cracked windshield
- Interior: seats not sagging, leather not worn through, steering wheel intact
- Specialists say L7 models routinely reach 150--200K km with normal maintenance
- Second-hand L7 with 80--100K km is safe to consider

---

## Otzovik.com Findings

Only the L7 has a review page on otzovik.com (https://otzovik.com/reviews/avtomobil_lixiang_l7/). Very few real owner reviews exist -- "mostly enthusiastic stories from sellers and paid bloggers." One owner reported 2 years of trouble-free ownership. No L9 reviews found (only a toy car review page exists).

**Key otzovik disadvantages mentioned**:
- "Significant design flaws"
- No widespread repair network in Russia
- Platform heavily VIN-coded, third-party repair extremely difficult

---

## iRecommend.ru Findings

No Li Auto L7 or L9 car reviews found on irecommend.ru. The site has a review page for drom.ru as a platform, but no actual Lixiang vehicle reviews.

---

## Methodology

### Search Queries Used
1. `drom.ru Li Auto L7 отзывы владельцев проблемы недостатки`
2. `drom.ru Li Auto L9 отзывы проблемы поломки 5 копеек`
3. `otzovik.com Li Auto L7 L9 отзыв владельца`
4. `irecommend.ru Li Auto отзыв L7 L9`
5. `site:drom.ru Li L7 5kopeek поломки breakagies`
6. `site:drom.ru Li L9 5kopeek поломки breakagies`
7. `Li Auto L7 проблемы зимой батарея пневмоподвеска расход 2024 2025`
8. `Li Auto L9 поломки проблемы недостатки владельцев обзор`
9. `autonews.ru 15 проблем кроссоверов Lixiang Li Auto`
10. `Lixiang L7 170 тыс км что сломалось`
11. `Li Auto L9 367000 км поломка двигатель цепь ГРМ`
12. `Lixiang L7 L9 тормоза колодки диски износ скрип`
13. `Lixiang Li Auto ADAS автопилот проблемы ошибки ДТП Россия`
14. `faq.liautorussia.ru известные проблемы`
15. `kursiv.media поломки LiXiang`
16. `getcar.ru поломки LiXiang L9 Россия`
17. `site:otzovik.com Lixiang Li Auto`
18. `110km.ru Lixiang L7 L9 отзывы`
19. Various follow-up searches for specific issues

### What Worked
- **WebSearch** yielded rich results across Russian automotive media (drom.ru, getcar.ru, autonews.ru, kursiv.media, 110km.ru)
- Cross-referencing multiple sources confirmed issue patterns with high confidence
- The Li Auto Club Russia FAQ (faq.liautorussia.ru) was an authoritative source of known problems
- Autonews.ru article on "15 problems" provided a structured expert assessment
- Long-term test data (376K km L9, 170K km L7) provided durability evidence

### What Didn't Work
- **WebFetch** was denied -- could not scrape full review pages from drom.ru
- **Bash** was denied -- could not query existing database for the 54 drom_reviews already scraped
- **irecommend.ru** has zero Li Auto vehicle reviews
- **otzovik.com** has almost no real owner reviews (mostly blogger content)
- English search queries returned generic specs rather than owner complaints

### Existing DB Data
The project database already contains 54 drom_reviews entries (scraped earlier), covering L6/L7/L8/L9 5kopeek pages and individual reviews. This research supplements that data with web search findings from a broader range of sources and more recent reviews (2025-2026).

### Data Quality Notes
- Drom.ru data is high quality: structured pros/cons/breakdowns format, real owners
- getcar.ru articles are aggregation/analysis pieces, not primary reviews
- kursiv.media provides excellent technical analysis from Kazakhstan perspective
- Some getcar.ru statistics (e.g., "70% of breakdowns are suspension + electronics") should be verified as they may be editorial estimates rather than hard data
