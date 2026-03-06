# Agent 4: English-Language Sources Research Report
# Li Auto L7 / L9 — Real-World Problems and Ownership Experience

**Date**: 2026-03-06
**Sources covered**: carnewschina.com, carscoops.com, insideevs.com, Reddit (r/LiAuto, r/EVs, r/ChineseCars), topelectricsuv.com, autoevolution.com, gasgoo.com, cnevpost.com, Top Gear, PistonHeads, J.D. Power China

---

## Table of Contents
1. [Critical Issues Found](#critical-issues-found)
2. [Recall Notices](#recall-notices)
3. [High-Mileage Reports](#high-mileage-reports)
4. [Competitive Context](#competitive-context)
5. [Methodology](#methodology)

---

## Critical Issues Found

### 1. Brake Fade and Poor Stopping Performance (L9)
- **Models**: L9 (likely also L7 given shared platform)
- **Mileage**: Any (design issue, not wear-related)
- **Season**: All, worse in hot conditions
- **Symptoms**: First stop from 60 mph: 35 meters (barely acceptable). Each subsequent stop adds 3 meters. Third stop worse than an Ineos Grenadier. Brakes described as "mushy, vague and -- when they get hot -- unpredictable and unsettling." Pedal feel is spongy and inconsistent.
- **Affected Systems**: Braking system (hydraulic brake design, brake cooling)
- **DTC Codes**: None reported
- **Root Cause**: Insufficient brake thermal management for a 2.5-ton vehicle. Brake design prioritizes regenerative braking over friction brakes, leading to inadequate fade resistance on successive stops.
- **Resolution**: No official fix reported. L9 Livis (2026) introduces electronic mechanical braking system which may address this.
- **Confidence**: HIGH
- **Sources**: [Top Gear L9 First Drive Review](https://www.topgear.com/car-reviews/li-auto/l9/first-drive), [PistonHeads owner thread](https://www.pistonheads.com/gassing/topic.asp?h=0&f=23&t=2027262)
- **How Found**: "Li Auto L9 Top Gear review brake stopping distance test"

---

### 2. Air Suspension Compressor Failure (L9)
- **Models**: L9
- **Mileage**: 10,000-15,000 km (reported in Russia)
- **Season**: Winter (especially with road salt and moisture)
- **Symptoms**: Squeaks from suspension, compressor failures, air spring leaking. In one documented 2022 incident, right front air spring failed completely after hitting a 20cm pothole at 90 km/h.
- **Affected Systems**: Air suspension (compressor, air spring body, air pump, air reservoir)
- **DTC Codes**: None documented in English sources
- **Root Cause**: Air suspension compressor vulnerable to moisture and road salt/reagents. Early production trial components weaker than production spec (2.5x improvement in production version claimed by Li Auto). Russian climate and road treatment chemicals accelerate degradation.
- **Resolution**: Li Auto extended air suspension warranty to 8 years / 160,000 km (from 5yr/100K km). Compressor replacement costs 50,000-100,000 RUB (~$550-1,100 USD).
- **Confidence**: HIGH
- **Sources**: [CnEVPost - L9 suspension breakage](https://cnevpost.com/2022/07/18/li-auto-in-spotlight-for-li-l9-test-car-suspension-breakage/), [TechNode - warranty extension](https://technode.com/2022/07/19/li-auto-extends-l9-parts-warranty-after-suspension-failure-incident/), [GetCar.ru reliability report](https://getcar.ru/en/blog/nadyozhnost-lixiang-l9-ekspluatacziya/)
- **How Found**: "Li Auto L9 air suspension failure compressor problem", "Li Auto L9 Russia owner experience problems winter"

---

### 3. Front Wheel Unusual Noise — 2025 L-Series (L6, L7, L8, L9)
- **Models**: Both (all 2025 L-series EREVs: L6, L7, L8, L9)
- **Mileage**: Shortly after delivery (new vehicles)
- **Season**: All
- **Symptoms**: Unusual noises from front wheels shortly after delivery, impairing driving experience.
- **Affected Systems**: Front suspension/wheel assembly (specific component not publicly identified)
- **DTC Codes**: None reported
- **Root Cause**: Manufacturing/assembly quality issue. Li Auto fired 14 employees in two internal memos and stated the issue "significantly impacted the company's reputation for product quality and safety."
- **Resolution**: Li Auto identified the problem and replaced parts for affected owners, but offered no compensation, sparking dissatisfaction.
- **Confidence**: HIGH
- **Sources**: [CnEVPost - Li Auto fires employees](https://cnevpost.com/2025/11/14/li-auto-fires-employees-mega-recall/), [36Kr - owner reputation damaged](https://eu.36kr.com/en/p/3419265841207424)
- **How Found**: "Li Auto L9 L7 front wheel noise 2025 quality issue employee fired"

---

### 4. Range Extender Engine Failure at 307,000 km (L9)
- **Models**: L9
- **Mileage**: 307,000 km (190,000 miles)
- **Season**: N/A
- **Symptoms**: Catastrophic engine failure. Timing chain tensioner failed, allowing pistons to crash into the head. Valve cover and cylinder head full of camshaft pieces and destroyed valves. Engine completely destroyed.
- **Affected Systems**: 1.5T range extender engine (timing chain tensioner, pistons, cylinder head, valves, camshaft)
- **DTC Codes**: Not reported
- **Root Cause**: Timing chain tensioner failure — a known wear item in ICE engines. At 307K km this is high mileage for any engine but still within the "1 million km" target the Russian test team (Faker Autogroup) set.
- **Resolution**: Engine replaced; car back in service with additional 24,000+ miles added. Notably, the car could still drive on electric power after engine failure. Assessed as "industry average" reliability — comparable to Chevy Volt (engine warped at 147K miles).
- **Confidence**: HIGH
- **Sources**: [InsideEVs - 1 million km test](https://insideevs.com/news/775394/li-auto-l9-russia-erev/)
- **How Found**: "Li Auto L9 307000 km high mileage what broke", "Li Auto EREV range extender engine problems reliability"

---

### 5. Winter Battery Range Loss (L9)
- **Models**: L9 (likely L7 too, same battery platform)
- **Mileage**: Any
- **Season**: Winter (cold weather)
- **Symptoms**: EV-only range drops from ~280 km to 150-180 km in winter conditions (35-46% reduction). Battery loses 15-20% of capacity in cold weather.
- **Affected Systems**: Battery thermal management, Li-ion battery pack (44.5 kWh)
- **DTC Codes**: None
- **Root Cause**: Standard lithium-ion behavior at low temperatures — increased electrolyte viscosity reduces capacity. Li Auto has developed thermal management optimizations (bypassing battery to heat cabin on cold start, storing excess heat during high-speed driving).
- **Resolution**: OTA updates for thermal management optimization. New L9 Livis (2026) has 72.7 kWh battery with 340 km EV range. The EREV architecture mitigates range anxiety via range extender.
- **Confidence**: HIGH
- **Sources**: [GetCar.ru reliability report](https://getcar.ru/en/blog/nadyozhnost-lixiang-l9-ekspluatacziya/), [BitAuto winter optimization](https://www.bitauto.com/global/news/100196590722.html)
- **How Found**: "Li Auto L9 battery degradation winter range real world test"

---

### 6. Steering Feel and Body Roll (L7)
- **Models**: L7 (primarily), L9 shares similar characteristics
- **Mileage**: Any (design characteristic)
- **Season**: All
- **Symptoms**: Vague road feel, oversized steering ratio, no steering feel whatsoever. Quick lane changes cause significant body roll. Heavy suspension is soft; rapid center-of-gravity transfer burdens tires and electronic stability systems. Body oscillates obviously, speed of correction slow.
- **Affected Systems**: Steering, suspension (air suspension calibration)
- **DTC Codes**: N/A (design, not defect)
- **Root Cause**: Li Auto deliberately prioritizes comfort over sporty handling. Marketing positions the vehicle as "sofa, color TV, and refrigerator" — family comfort, not driving dynamics. The 2025 upgrade improved this: dual-chamber air suspension (from single-chamber) provides 30% stiffer spring rate and 20% reduction in body roll.
- **Resolution**: 2025 model year upgrade with dual-chamber air suspension. L9 Livis (2026) has fully active suspension and steer-by-wire.
- **Confidence**: HIGH
- **Sources**: [Bada-Car L7 one-year review](https://bada-car.com/li-l7-one-year-driving-experience-not-bragging-including-advantages-and-disadvantages/), [JinyuAutos - L7 worth buying](https://jinyuautos.com/blog/is-the-li-auto-l7-worth-buying-in-2025/)
- **How Found**: "Li Auto L7 steering soft body roll handling complaint review"

---

### 7. Software / OTA / Firmware Bugs (L9)
- **Models**: L9 (2024 model, firmware 4.6.5)
- **Mileage**: Any
- **Season**: All
- **Symptoms**: Firmware update 4.6.5 caused problems with multimedia system and digital key. Screen freezes reported. Difficulties with Li Auto servers due to poor compatibility of Russian SIM cards (international market issue).
- **Affected Systems**: Infotainment system, digital key, telematics/connectivity
- **DTC Codes**: None
- **Root Cause**: Software quality issue with specific firmware version. Server infrastructure not optimized for international (non-Chinese) SIM cards.
- **Resolution**: Presumed fixed via subsequent OTA update. Li Auto rolled out OTA 7.0 with significant improvements.
- **Confidence**: MEDIUM (reported primarily by Russian owners on Drive2 forum)
- **Sources**: [GetCar.ru reliability report](https://getcar.ru/en/blog/nadyozhnost-lixiang-l9-ekspluatacziya/)
- **How Found**: "Li Auto L9 Russia owner experience problems winter cold weather"

---

### 8. ADAS / NOA System Failure in Accident (L9)
- **Models**: L9
- **Mileage**: Unknown
- **Season**: N/A
- **Symptoms**: User claimed NOA (Navigation on Autopilot) driving assistance system failed, resulting in a crash. The system could not identify a uniquely shaped stopped vehicle on the highway despite the camera seeing it.
- **Affected Systems**: ADAS (AD-Max system), NOA highway autopilot, camera recognition
- **DTC Codes**: None reported
- **Root Cause**: Recognition failure — the system cannot identify vehicles with unusual shapes through feature comparison. This is a known limitation of camera + lidar perception systems across all ADAS providers.
- **Resolution**: Li Auto denied system fault. OTA updates have progressively improved ADAS capabilities. OTA 7.0 includes "all-scenario end-to-end intelligent driving functions."
- **Confidence**: MEDIUM (single incident, disputed by manufacturer)
- **Sources**: [CarNewsChina - L9 ADAS accident](https://carnewschina.com/2023/01/27/li-l9-user-claimed-driving-assistance-system-failed-resulting-in-an-accident/), [CnEVPost - second L9 test car accident](https://cnevpost.com/2022/07/26/li-auto-comes-back-into-spotlight-with-second-li-l9-test-car-accident/)
- **How Found**: "Li Auto L9 driving assistance ADAS accident crash NOA failure"

---

### 9. Parts Availability and Service in International Markets (Both)
- **Models**: Both
- **Mileage**: Any
- **Season**: All
- **Symptoms**: No official Li Auto dealers in Russia. Parts take 2-3 months to arrive from China. No parts warehouses in Russia. Gearbox oil seal replacement costs 30,000 RUB. Suspension repairs up to 100,000 RUB. Diagnostics alone cost 16,500 RUB. Major breakdowns "almost impossible to fix outside China."
- **Affected Systems**: All (service infrastructure, not specific vehicle system)
- **DTC Codes**: N/A
- **Root Cause**: Li Auto's international expansion is still in early stages. Official Middle East launch delayed. Most international vehicles are parallel imports without manufacturer support.
- **Resolution**: Li Auto is slowly expanding, establishing dealer partnerships in Middle East and Central Asia. But official overseas presence remains minimal.
- **Confidence**: HIGH
- **Sources**: [GetCar.ru reliability report](https://getcar.ru/en/blog/nadyozhnost-lixiang-l9-ekspluatacziya/), [CnEVPost - overseas expansion](https://cnevpost.com/2024/10/31/li-auto-puts-overseas-market-expansion-back-on-table-report/), [CarNewsChina - parallel exports](https://carnewschina.com/2024/10/21/li-auto-content-with-10-parallel-exports-as-it-slows-offical-middle-east-export-plan/)
- **How Found**: "Li Auto L7 L9 Middle East UAE Saudi Arabia owner problems"

---

### 10. Battery Supplier Controversy — CATL vs Sunwoda (Brand-wide)
- **Models**: i6 (documented), but raises concerns for L7/L9 battery sourcing
- **Mileage**: N/A (new vehicles)
- **Season**: All
- **Symptoms**: Li Auto adopted a "discriminatory battery supply plan" where early adopters got CATL batteries while later buyers got a mix of CATL and Sunwoda. Only 30% of buyers chose Sunwoda when given the choice. Customers offered 2-year/40,000 km warranty extension to switch to Sunwoda.
- **Affected Systems**: Battery pack (supplier quality variance)
- **DTC Codes**: N/A
- **Root Cause**: Cost optimization and supply constraints. Sunwoda batteries are cheaper but face quality concerns — Geely subsidiary sued Sunwoda for RMB 2.31 billion over battery cell quality defects (2021-2023 supply period).
- **Resolution**: Ongoing controversy. Li Auto formed a joint venture with Sunwoda for "Li Auto Brand" batteries. CATL partnership also deepened with 5-year strategic deal.
- **Confidence**: MEDIUM (documented for i6; L7/L9 implications unclear but relevant to brand quality perception)
- **Sources**: [CnEVPost - i6 battery supply constraints](https://cnevpost.com/2026/01/29/li-auto-still-grapples-with-battery-supply-constraints-i6-suv/), [36Kr - i6 battery controversy](https://eu.36kr.com/en/p/3582350109129858), [CarNewsChina - Geely sues Sunwoda](https://carnewschina.com/2025/12/26/geely-subsidiary-sues-battery-manufacturer-sunwoda-for-323-million-usd-over-quality-issues/)
- **How Found**: "Li Auto i6 battery CATL Sunwoda controversy discriminatory supply"

---

### 11. Infotainment System Lag (L9)
- **Models**: L9 (likely L7 as well)
- **Mileage**: Any
- **Season**: All
- **Symptoms**: In-vehicle interaction system occasionally experiences lag. Screen freezes reported. System responsiveness inconsistent.
- **Affected Systems**: Infotainment / HMI system
- **DTC Codes**: None
- **Root Cause**: Software optimization issue. Complex multi-screen setup (3 large touchscreens + HUD) may tax computing resources.
- **Resolution**: OTA updates. J.D. Power 2025 NEV-IQS study notes infotainment is the most problematic category industry-wide at 31 PP100.
- **Confidence**: MEDIUM
- **Sources**: [BitAuto L9 owner pros/cons](https://www.bitauto.com/wiki/10016042318/), [J.D. Power 2025 NEV-IQS](https://china.jdpower.com/press-releases/2025-china-new-energy-vehicle-initial-quality-study-nev-iqs)
- **How Found**: "reddit Li Auto L9 owner experience issues complaints"

---

### 12. Parking Difficulty Due to Vehicle Size (L9)
- **Models**: L9 (5,218 mm long, 1,998 mm wide)
- **Mileage**: N/A
- **Season**: All
- **Symptoms**: Difficulty parking in urban areas, especially narrow parking spaces. Large turning circle for the vehicle's size.
- **Affected Systems**: Vehicle dimensions / steering geometry
- **DTC Codes**: N/A
- **Root Cause**: Full-size SUV dimensions designed for Chinese highway and suburban use. Not optimized for tight urban parking.
- **Resolution**: L9 Livis (2026) adds rear-wheel steering to improve maneuverability. Auto-park features available.
- **Confidence**: HIGH (physical constraint)
- **Sources**: [BitAuto L9 owner reviews](https://www.bitauto.com/wiki/10016042318/)
- **How Found**: General owner review searches

---

## Recall Notices

### Recall 1: Li ONE Front Suspension Ball Joint (2020)
- **Date**: November 7, 2020
- **Models affected**: 10,469 Li ONE vehicles produced on or before June 1, 2020
- **Issue**: Front suspension lower control arm ball joint could detach
- **Severity**: Safety-critical (loss of steering/suspension integrity)
- **Remedy**: Free replacement of control arm ball joint
- **Timeline**: Within 3 months
- **Controversy**: Li Auto initially called it an "upgrade" rather than a recall, was criticized, then apologized and formally filed it as a recall with SAMR
- **Sources**: [GlobeNewswire - official announcement](https://www.globenewswire.com/news-release/2020/11/06/2121725/0/en/Li-Auto-Inc-Announces-Voluntary-Recall.html), [SCMP - apology](https://www.scmp.com/business/companies/article/3108852/nasdaq-listed-chinese-electric-carmaker-li-auto-apologies)

### Recall 2: Li Mega Battery Thermal Runaway Risk (2025)
- **Date**: November 7, 2025
- **Models affected**: 11,411 Li Mega MPVs produced February 18 - December 27, 2024
- **Issue**: Insufficient coolant anti-corrosion performance could lead to corrosion and leakage in aluminum cooling plates of power battery and front motor controller, risking thermal runaway
- **Severity**: Fire risk (one vehicle caught fire in Shanghai on October 23, 2025)
- **Remedy**: Free replacement of coolant, power battery, and front motor controller. Extended warranty by 2 years / 25,000 miles (to 10yr / 125K miles)
- **Financial impact**: Estimated RMB 1.14 billion reduction in profits. Li Auto turned to net loss in Q3 2025.
- **Internal accountability**: 14 employees dismissed in two internal memos
- **Sources**: [CnEVPost - recall](https://cnevpost.com/2025/10/31/li-auto-recalls-mega-mpvs-battery-risk/), [CarNewsChina - recall](https://carnewschina.com/2025/10/31/li-auto-recalls-over-11000-mega-2024-models-due-to-potential-battery-thermal-runaway-risk/), [CnEVPost - employees fired](https://cnevpost.com/2025/11/14/li-auto-fires-employees-mega-recall/)

### Recall 3 (Informal): L9 Air Suspension Warranty Extension (2022)
- **Date**: July 2022
- **Models affected**: All L9 vehicles
- **Issue**: Air spring failure risk when hitting large potholes. Documented incident: right front air spring leaked after hitting 20cm pothole at 90 km/h.
- **Severity**: Drivability / comfort (not fire risk)
- **Remedy**: Not a formal recall, but warranty extended from 5yr/100K km to 8yr/160K km for air spring body, air pump, and air reservoir
- **Sources**: [TechNode](https://technode.com/2022/07/19/li-auto-extends-l9-parts-warranty-after-suspension-failure-incident/), [CnEVPost](https://cnevpost.com/2022/07/18/li-auto-in-spotlight-for-li-l9-test-car-suspension-breakage/)

### Note on L7/L9 Specific Recalls
No formal SAMR recall was found specifically for the L7 or L9 models. The 2025 front wheel noise issue affecting all L-series EREVs was handled as a warranty repair, not a formal recall.

---

## High-Mileage Reports

### Li Auto L9 — 307,000 km (Faker Autogroup, Russia)
- **Test team**: Faker Autogroup (Russian car dealership and content creator)
- **Goal**: Drive L9 to 1,000,000 km (621,000 miles)
- **What failed at 307K km**: Range extender engine (1.5T turbo 4-cylinder) — timing chain tensioner failure. Catastrophic: pistons crashed into cylinder head, destroying valves, camshaft, and engine internals.
- **What survived**: Electric drivetrain, battery, dual motors, all electronics, suspension, interior — all still functional. Car continued to drive on electric power after engine death.
- **Recovery**: Engine replaced. Vehicle returned to service, accumulated 24,000+ additional miles.
- **Assessment**: InsideEVs assessed this as "industry average" reliability. Compared to first-gen Chevrolet Volt which had engine failure at 147,000 miles (cylinder head warped from overheating).
- **Key insight**: The EREV architecture provides a safety net — even catastrophic engine failure doesn't strand the vehicle.
- **Sources**: [InsideEVs](https://insideevs.com/news/775394/li-auto-l9-russia-erev/)

### Li Auto L9 — Annual Owner Review (China)
- **Source**: GreenFastAuto (translated owner review)
- **Key data points**: One year of ownership, daily family use. Generally positive with minor complaints about brakes and parking.
- **Sources**: [GreenFastAuto](https://greenfastauto.com/my-li-auto-l9-annual-review-purchase-expectations-driving-experience-and-costs/)

---

## Competitive Context

### J.D. Power 2025 NEV Initial Quality Study
- **Li L9 won Premium PHEV SUV segment** in J.D. Power 2025 China NEV-IQS
- Industry average: 226 PP100 (problems per 100 vehicles), up 16 from 2024
- PHEVs (234 PP100) reported more problems than BEVs (220 PP100)
- Infotainment remains #1 problem category at 31 PP100 across all brands
- **Li Auto ranks highest among NEV mass market brands** in brand reputation (46.4 score)
- **Sources**: [J.D. Power 2025 NEV-IQS](https://china.jdpower.com/press-releases/2025-china-new-energy-vehicle-initial-quality-study-nev-iqs)

### Li Auto vs BYD
- BYD focuses on BEVs; Li Auto focuses on EREVs — different technology bets
- BYD has broader model range and scale advantage
- Li Auto's EREV approach eliminates range anxiety but adds ICE engine maintenance complexity
- Both face price war pressures in 2025
- **Sources**: [GreenSpeedX comparison](https://greenspeedx.com/byd-vs-li-auto/)

### Li Auto vs NIO
- NIO emphasizes cutting-edge technology (battery swap, autonomous driving)
- Li Auto emphasizes practicality and reliability
- Both experienced declining sales in 2025
- NIO's Onvo brand directly competes with Li Auto L-series on price
- "Tit-for-tat battle" over three-row SUV segment
- Analysts consider Li Auto the "current winner" for avoiding big mistakes
- **Sources**: [TechNode - NIO vs Li Auto](https://technode.com/2025/08/04/tit-for-tat-battle-flares-between-chinas-nio-and-li-auto-over-three-row-suvs/)

### Li Auto Sales Decline Context
- **Jan-Nov 2025**: 362,097 deliveries, down 18%+ YoY
- **L7**: 74,557 units (down 38.31% YoY)
- **L9**: 42,482 units (down 45.58% YoY)
- **November 2025**: 33,181 deliveries (down 31.92% YoY) — 6th consecutive month of decline
- Dropped from #1 in new-energy challengers (held for 24 consecutive months) to outside top 5 by August 2025
- Causes: increased competition (Huawei AITO, BYD, NIO Onvo), quality complaints, Li Mega failure, market saturation
- **Sources**: [CnEVPost - Nov deliveries](https://cnevpost.com/2025/12/09/li-auto-nov-2025-deliveries-breakdown/), [KR-Asia - sales crown lost](https://kr-asia.com/li-auto-loses-its-sales-crown-as-huawei-and-rivals-crowd-the-ev-market)

### Li Auto Battery Safety Track Record
- CATL claims: "More than one million Li Auto vehicles powered by CATL batteries delivered without a single thermal runaway incident attributed to the cells themselves"
- The Mega fire/recall (coolant issue, not cell defect) is the first battery-related safety incident
- This distinguishes Li Auto from some competitors who have had cell-level thermal events
- **Sources**: [Gasgoo - CATL partnership](https://autonews.gasgoo.com/new_energy/70039104.html)

### Li ONE Discontinuation Backlash (2022)
- Li Auto abruptly discontinued Li ONE less than a month after some owners received vehicles
- Replaced by Li L8, with only 20,000 RMB discount offered
- Owners felt betrayed; significant backlash damaged brand trust
- Company lost over 1 billion RMB in single quarter from sales collapse
- This event remains a cautionary note about Li Auto's product lifecycle management
- **Sources**: [CnEVPost - owner outcry](https://cnevpost.com/2022/09/05/li-auto-owner-outcry-discontinues-li-one-for-li-l8/)

---

## Methodology

### Search Queries Used (30+ queries)
1. "Li Auto L7 L9 problems issues reliability 2024 2025"
2. "Li Auto recall notice 2024 2025 2026"
3. "site:reddit.com Li Auto L7 L9 problems owner review"
4. "Li Auto L9 307000 km high mileage what broke"
5. "site:cnevpost.com Li Auto L7 L9 problems recall quality issues"
6. "site:carnewschina.com Li Auto problems issues recall"
7. "Li Auto L9 air suspension failure compressor problem"
8. "Li Auto L7 L9 brake noise pad wear complaint"
9. "Li Auto EREV range extender engine problems reliability long term"
10. "Li Auto L9 battery degradation winter range real world test"
11. "Li Auto OTA update bugs software problems screen freeze"
12. "site:insideevs.com Li Auto L7 L9 review problems"
13. "site:carscoops.com Li Auto L7 L9"
14. "Li Auto L9 vs BYD NIO comparison problems reliability"
15. "site:autoevolution.com Li Auto"
16. "site:gasgoo.com Li Auto quality problems defect"
17. "Li Auto L9 driving assistance ADAS accident crash NOA failure"
18. "reddit Li Auto L9 owner experience issues complaints"
19. "Li Auto L7 L9 Middle East UAE Saudi Arabia owner problems"
20. "Li Auto L7 suspension noise front wheel unusual noise recall 2025"
21. "Li Auto L9 L7 front wheel noise 2025 quality issue employee fired"
22. "Li Auto discontinue Li ONE owner angry backlash value drop"
23. "Li Auto L9 L7 JD Power quality study China NEV IQS 2025"
24. "Li Auto L7 L9 warranty claim service center issue"
25. "Li Auto L9 Russia owner experience problems winter cold weather"
26. "Li Auto L9 Livis 2026 new model improvements over old L9"
27. "Li Auto L7 infotainment screen lag freeze bug software glitch"
28. "Li Auto Li ONE recall 2020 2021 suspension ball joint"
29. "Li Auto L7 steering soft body roll handling complaint review"
30. "topelectricsuv.com Li Auto L9 L7 review problems"
31. "Li Auto L7 L9 recall China SAMR 2024 2025 defect"
32. "Li Auto L9 timing chain tensioner engine failure details Faker Autogroup"
33. "Li Auto i6 battery CATL Sunwoda controversy discriminatory supply"
34. "Li Auto L9 Top Gear review brake stopping distance test"
35. "Li Auto L9 PistonHeads owner review UK problems experience"
36. "Li Auto recall history complete list all models 2020 2025"
37. "Li Auto sales decline 2025 quality complaints owner dissatisfaction"
38. "Li Auto L7 L9 NVH range extender engine noise vibration harshness"
39. "Li Auto L7 L9 digital key problem firmware update 4.6.5 bug"
40. "Li Auto L9 gearbox oil seal repair cost transmission problem"

### What Worked
- **CnEVPost** was the most valuable single source — thorough coverage of recalls, sales data, quality issues, and employee firings
- **CarNewsChina** provided good coverage of ADAS incidents and product announcements
- **InsideEVs** had the best English-language coverage of the high-mileage L9 test
- **GetCar.ru** (English version) had the most detailed owner reliability report for Russian market
- **Top Gear** provided professional brake testing data not available elsewhere
- **J.D. Power** provided industry benchmark quality data
- **36Kr English** had excellent analysis of brand reputation damage and competitive dynamics

### What Didn't Work
- **Reddit** searches returned almost no relevant results — r/LiAuto and related subreddits appear to have very low activity for Li Auto-specific content
- **autoevolution.com** had minimal Li Auto coverage (mostly BYD and other brands)
- **gasgoo.com** had mostly positive/promotional content, very little critical quality reporting
- **topelectricsuv.com** had a positive first-look review but no problem-focused content
- **Li Auto infotainment bug searches** yielded mostly generic results, not Li Auto-specific
- **WebFetch** was denied, preventing full article reading for detailed extraction

### Gaps in Research
- No access to Chinese-language owner forums (autohome, dongchedi) which would have much more owner complaint data
- No SAMR recall database access for comprehensive recall list
- Reddit content for Li Auto is minimal in English
- Middle East owner experiences not yet documented (market too new)
- No long-term L7-specific high-mileage data found
- Specific DTC codes for reported issues not documented in English sources

---

## Summary of Issues by Severity

| Priority | Issue | Models | Confidence |
|----------|-------|--------|------------|
| CRITICAL | Brake fade on successive stops | L9 | HIGH |
| HIGH | Air suspension compressor failure (winter/salt) | L9 | HIGH |
| HIGH | Front wheel noise (2025 production) | Both + L6/L8 | HIGH |
| HIGH | Parts/service unavailable outside China | Both | HIGH |
| MODERATE | Range extender engine failure at 307K km | L9 | HIGH |
| MODERATE | Winter EV range loss (35-46%) | Both | HIGH |
| MODERATE | Soft steering / body roll | L7 | HIGH |
| MODERATE | ADAS recognition failure | L9 | MEDIUM |
| LOW | Infotainment lag / screen freeze | Both | MEDIUM |
| LOW | Software/firmware bugs (4.6.5) | L9 | MEDIUM |
| CONTEXT | Battery supplier controversy (CATL vs Sunwoda) | Brand-wide | MEDIUM |
| CONTEXT | Li ONE discontinuation backlash | Historical | HIGH |
