# Agent 6: Technical Data, DTC Codes, Diagnostic Tools & Specifications

**Research Date**: 2026-03-06
**Scope**: Li Auto L7 / L9 — DTC codes, diagnostic tools, repair procedures, technical specifications, maintenance schedules
**Sources**: YouTube/Bilibili repair channels, GitHub DTC databases, technical forums, service manuals, OEM documentation, Russian service centers

---

## DTC Code Catalog

### Important Context: Li Auto DTC Availability

Li Auto does not publicly release a comprehensive DTC code list. Unlike traditional automakers that publish TSBs through NHTSA/SAMR with specific P/C/B/U codes, Li Auto's diagnostic system is largely proprietary. Key findings:

1. **No public DTC code list exists** for Li Auto L7/L9 in any English, Russian, or Chinese source searched
2. **OBDb (github.com/OBDb)** does NOT have a Li Auto / Lixiang repository — the database covers Toyota, Nissan, Honda, MINI and other international brands but no Chinese EV makers
3. **GitHub DTC databases** (mytrile/obd-trouble-codes, todrobbins/dtcdb, wzr1337 gist) contain only generic SAE J2012 OBD-II codes, no manufacturer-specific Li Auto codes
4. Li Auto uses a **proprietary diagnostic system** — the official tool costs ~$9,200 (see Diagnostic Tools section)

### Generic OBD-II Codes Applicable to Li Auto (EREV Platform)

Since the L7/L9 have a 1.5T gasoline range extender, standard powertrain P-codes apply to the ICE component:

| Code Range | Category | Relevance to Li Auto |
|------------|----------|---------------------|
| P0xxx | Generic Powertrain | Range extender engine faults — ignition, fuel, emissions |
| P0300-P0304 | Misfire | 4-cylinder 1.5T range extender misfire detection |
| P0171/P0172 | Fuel trim | Lean/rich conditions on range extender |
| P0420 | Catalyst efficiency | Catalytic converter monitoring |
| C0xxx | Chassis | Air suspension, ABS, stability control |
| B0xxx | Body | Airbags, seat belt, interior electronics |
| U0xxx | Network | CAN bus communication errors between ECUs |

### Known Li Auto Warning Messages (from owner reports and service centers)

These are dashboard/infotainment messages rather than standard OBD-II codes:

| Warning Message (ZH) | Translation | System | Frequency |
|----------------------|-------------|--------|-----------|
| 增程器冷却液液位低 | Range extender coolant level low | Cooling | Common |
| 驱动电机冷却液液位低 | Drive motor coolant level low | EV drivetrain | Common |
| 排放系统异常 | Emission system abnormal | Range extender | Reported |
| 高压系统警告 | High voltage system warning | Battery/HV | ~30% battery-related |
| 驱动系统异常 | Drive system abnormal | Motor/inverter | Reported |
| 空气悬挂故障 | Air suspension fault | Suspension | Reported (see below) |

**Sources**: [12365auto.com complaint](https://m.12365auto.com/zlts/20250913/1501282.shtml), [max.book118.com L9 drive system diagnosis](https://max.book118.com/html/2024/0509/8065133011006066.shtm), [qcds.com HV warning](https://m.qcds.com/content-detail/l7Ln5)

### L9 Drive System Common Fault Types

From a diagnostic training document (理想L9驱动系统异常报警故障诊断与维修):
- **Motor control unit (MCU) faults** — inverter errors, gate driver failures
- **Transmission abnormalities** — reducer noise, gear engagement issues
- **Power electronics component faults** — DC-DC converter, OBC errors
- **High voltage system warnings** — 30% of cases are battery system related

**Source**: [max.book118.com](https://max.book118.com/html/2024/0509/8065133011006066.shtm)

---

## Repair Procedures Found

### Bilibili Teardown/Repair Videos (Chinese)

| Video | Content | URL |
|-------|---------|-----|
| 换增程器如换刀！理想L9长测拆解 | 100K km teardown: range extender, body materials, structural durability | https://www.bilibili.com/video/BV1kp4y1M73a/ |
| 理想L7拆解定损 | L7 accident damage assessment, rear structural cutting | https://www.bilibili.com/video/BV1Hw4m1k7yL/ |
| 理想L9座椅深度拆解 (上/下) | Deep seat teardown, structure analysis | https://www.bilibili.com/video/BV1Mu4y1d7cp/ and https://www.bilibili.com/video/BV1Hm4y1p7rE/ |
| 理想L7 真十万公里长测 | L7 100K km long-term test report — fuel, braking, disassembly | https://www.bilibili.com/video/BV1HK42117LH/ |
| 大飙车拆解理想L9底盘 | L9 chassis teardown — aluminum double-wishbone front, five-link rear | https://www.xchuxing.com/ins/243187 |

### Russian Service Center Repair Content

| Service Center | Location | Services | URL |
|---------------|----------|----------|-----|
| ЭЛЕКТРОМЭН | Moscow | Diagnostics, repair, video content for L7/L9 | https://elektroman.pro/brands/lixiang/ |
| Li-Auto Центр | Moscow | Multimedia repair for L7/L8/L9 | https://li-auto.com/services/remont-blokov-multimedia/ |
| Li-motors | Russia-wide | Full ТО service, Russification | https://li-motors.ru/service |
| ШИНСЕРВИС | Moscow | L7 suspension repair | https://www.shinservice.ru/service-catalog/suspension-repair/lixiang/lixiang-l7/ |
| EN Service | Russia | Full maintenance L7/L8/L9 | https://service.e-n-cars.ru/tehnicheskoe-obsluzhivanie/lixiang/ |
| SMElectro | Minsk (Belarus) | L6/L7/L9 repair and service | https://remont-elektromobilei.by/lixiang/ |
| lihome.pro | Moscow | General service and maintenance | https://lihome.pro/ |
| Provolta.kz | Almaty (Kazakhstan) | L6/L7/L8/L9 repair and EV charging | https://provolta.kz/remont-i-obsluzhivanie-lixang |

### Key Repair Insight from Minsk Service Center (av.by)

From [av.by article](https://av.by/news/kak_remontiryut_i_skolko_stoit_obsluzhivanie_lixiang):
- Ball joints commonly fail, especially on L6
- Suspension diagnostics recommended every 10,000-15,000 km
- No traditional transmission — focus is on reducer, suspension, brakes
- Russification and firmware updates are common service items

### Brake System Details

- **Stock brakes**: Single-piston floating caliper (front), standard for 2.5+ ton SUV
- **Brake pad wear**: High due to 2,520 kg curb weight (L9)
- **Common upgrades**:
  - TEI Racing brake kit (tested on Bilibili)
  - AP Racing caliper upgrade
  - Inspeed CS8 8-piston front + TE4 4-piston rear with 405mm/380mm rotors
  - Savanini 6-piston forged caliper kit
  - Akebono 10-piston front + Brembo 4-piston rear

**Sources**: [savanini.com](https://www.savanini.com/cnpro_1670397505508954975.html), [autohome forum](https://club.autohome.com.cn/bbs/thread/10b1be7fec503b41/105283941-1.html)

---

## Diagnostic Tools

### 1. Official LiXiang Diagnostic Tester (OEM)

- **Type**: Dealer-level / engineering-level diagnostic tool
- **Price**: ~$9,200 USD
- **Features**: Fault scanning, firmware updates, coding, flash programming, online programming
- **Requires**: One-year online account subscription
- **Supplier**: cars-technical.com / automan.co (Shenzhen Automan Technology)
- **Note**: This is the ONLY tool that provides full access to Li Auto proprietary systems

**Sources**: [cars-technical.com](https://cars-technical.com/product/lixiang-diagnostic-tester/), [automan.co](https://automan.co/productdetail/7016.html)

### 2. Li Auto App (Owner Self-Diagnosis)

- Li Auto provides a mobile app for vehicle monitoring
- OTA updates include safety diagnosis mechanisms that check vehicle health before updates
- Voice assistant "理想同学" (Lixiang Tongxue) can report basic vehicle status
- **NOT a replacement** for professional diagnostic scanning

### 3. Generic OBD-II Scanners (Limited Compatibility)

- **ELM327**: May read basic OBD-II P-codes from the range extender engine only. No confirmed full compatibility with Li Auto CAN bus for chassis/body/network codes
- **Autel/Launch**: Lixiang-specific diagnostic cables and adapters are sold on Alibaba, suggesting aftermarket tools need manufacturer-specific protocols
- **Standard OBD-II port**: Present (required by Chinese GB standards), located under dashboard. Uses CAN bus (ISO 15765-4)
- **Limitation**: EV-specific systems (BMS, motor controller, air suspension, ADAS) are proprietary and NOT accessible via generic OBD-II tools

### 4. Third-Party Diagnostic Solutions (Alibaba/China market)

- Multiple "lixiang obd" and "lixiang scanner" products available on Alibaba
- Diagnostic cables with online programming support
- Price range varies widely ($200-$9,200)

**Key Finding**: Standard ELM327/Torque/Car Scanner apps will have VERY limited access to Li Auto systems. Only the range extender engine's basic OBD-II compliance data is readable. For air suspension, BMS, motor controllers, ADAS — the official tool or compatible aftermarket Chinese tools are required.

---

## Technical Specifications

### Li Auto L9 (2022-2025)

| Parameter | Value |
|-----------|-------|
| **Dimensions (L/W/H)** | 5,218 / 1,998 / 1,800 mm |
| **Wheelbase** | 3,105 mm |
| **Curb weight** | 2,520 kg |
| **Seating** | 6 seats (2+2+2) |
| **Platform** | Li Auto EREV (Extended Range Electric Vehicle) |

#### Powertrain

| Component | Specification |
|-----------|--------------|
| **Range extender engine** | L2E15M (Li-Xinchen), 1.5T 4-cylinder turbocharged |
| **Engine power** | 113 kW (154 hp) |
| **Thermal efficiency** | 40.5% |
| **Engine origin** | Joint venture with Xinchen Power (Mianyang); BMW Prince engine DNA — CE16 short-stroke variant (bore 77mm, stroke ~80.5mm = 1,499 cc) |
| **Fuel type** | 92# RON (China standard) |
| **Fuel consumption (CLTC)** | 5.9 L/100km (fuel mode) |
| **Fuel tank** | 65L |
| **Front motor** | 130 kW (174 hp) permanent magnet synchronous |
| **Rear motor** | 200 kW (268 hp) permanent magnet synchronous |
| **Total system power** | 330 kW (449 hp) |
| **Total torque** | 620 Nm |
| **0-100 km/h** | 5.3 seconds |
| **Top speed** | 180 km/h (electronically limited) |

#### Battery

| Parameter | 2022-2024 | 2025 Smart Refresh | 2026 Livis |
|-----------|-----------|-------------------|------------|
| **Capacity** | 44.5 kWh | 52.3 kWh | 72.7 kWh |
| **Chemistry** | CATL NMC (Ternary Lithium) | CATL NMC | CATL NMC |
| **EV range (CLTC)** | 215 km | ~280 km | 322-340 km |
| **Total range (CLTC)** | 1,315 km | ~1,400 km | TBD |
| **DC fast charge** | 20-80% in ~30 min | 20-80% in ~25 min | TBD |

#### Suspension

| Parameter | Value |
|-----------|-------|
| **Front** | Double wishbone (aluminum alloy) |
| **Rear** | Multi-link (five-link) |
| **Air springs** | Standard on all trims |
| **Ride height adjustment** | 80 mm range |
| **CDC** | Continuous Damping Control (ZF supplier) |
| **Control system** | Li Auto self-developed suspension controller |

##### Air Suspension Suppliers (3 suppliers)

| Supplier | Origin | Max Load Rating | Market Share (2023) |
|----------|--------|----------------|-------------------|
| **Vibracoustic (威巴克)** | Germany | 6.5 tons impact force | 23.3% |
| **Baolong Technology (保隆科技)** | China | 9 tons impact force | Growing |
| **Konghui Technology (孔辉科技)** | China | Not specified | 39.2% (#1 in China) |

**Key fact**: L9 was the first vehicle to use domestic (Chinese) single-chamber air springs as standard. In 2022, Vibracoustic held 35.8% share (80K units), Konghui sold 50K. By 2023, Konghui sold 250K units and became #1.

**Sources**: [pcauto.com.cn](https://www.pcauto.com.cn/jxwd/3774/37744845.html), [lixiang.com community](https://www.lixiang.com/community/detail/article/482963.html), [chejiahao.autohome.com.cn](https://chejiahao.autohome.com.cn/info/10842516)

### Li Auto L7 (2023-2025)

| Parameter | Value |
|-----------|-------|
| **Dimensions (L/W/H)** | 5,050 / 1,995 / 1,750 mm |
| **Wheelbase** | 3,005 mm |
| **Seating** | 5 seats |
| **Range extender** | Same L2E15M 1.5T as L9 (113 kW) |
| **Front motor** | 130 kW |
| **Rear motor** | 200 kW |
| **Total power** | 330 kW (449 hp) |
| **Total torque** | 620 Nm |
| **0-100 km/h** | 5.3 seconds |
| **Battery** | 52.3 kWh CATL NMC (Smart Refresh) |
| **EV range (CLTC)** | 286 km |
| **Total range (CLTC)** | 1,421 km |
| **DC fast charge** | 20-80% in 25 minutes |

### 2026 Li Auto L9 Livis (New Generation)

| Parameter | Value |
|-----------|-------|
| **Battery** | 72.7 kWh CATL NMC |
| **EV range** | 322-340 km (CLTC) |
| **Computing** | 2x Mach 100 chips (5nm), 2,560 TOPS combined |
| **Suspension** | 800V fully active suspension, >10,000 N per wheel, no anti-roll bar |
| **Chassis** | World's first "full-form" by-wire chassis |
| **Steering** | Steer-by-wire + four-wheel steering |
| **Braking** | Full electronic mechanical brake (EMB) |
| **Redundancy** | Multi-layer cross-system safety redundancy |
| **Price** | 559,800 CNY (~$77,000 USD) |

**Sources**: [dailyrevs.com](https://www.dailyrevs.com/cars/2026-li-auto-l9-livis), [carnewschina.com](https://carnewschina.com/2026/02/06/all-new-li-auto-l9-livis-suv-revealed-in-china-with-2560-tops/), [globalchinaev.com](https://globalchinaev.com/post/li-auto-unveils-80000-l9-livis-suv-with-worlds-first-full-by-wire-chassis)

### Fluids & Consumables

| Item | Specification | Notes |
|------|--------------|-------|
| **Engine oil** | 0W-30 fully synthetic | 0W = winter viscosity, 30 = operating temp viscosity |
| **Oil capacity** | ~4.5L (estimated for 1.5T) | Official spec not publicly available |
| **Fuel** | 92# RON minimum | Chinese standard |
| **Brake fluid** | DOT 4 (assumed, standard for ABS-equipped vehicles) | Replace every 2 years or 40,000 km |
| **Coolant** | Two separate systems: range extender + EV motor/battery | Replace every 2 years |
| **Front differential oil** | Replace at 4 years or 80,000 km | Per Li Auto maintenance schedule |
| **Rear differential oil** | Replace at 4 years or 80,000 km | Per Li Auto maintenance schedule |

---

## Maintenance Schedule

### Official Li Auto L-Series Maintenance Schedule

All L-series vehicles (L6, L7, L8, L9) follow the **same maintenance cycle**.

| Interval | Items | Cost (CNY) |
|----------|-------|-----------|
| **Small service** (1 year / 10,000 km RE) | Engine oil + oil filter | 799 |
| **Large service** (2 years / 20,000 km RE) | Engine oil + oil filter + air filter | 929 |
| **Cabin air filter** | Every 1 year or 20,000 km | 238 |
| **Spark plugs** | Every 40,000 km RE | ~300 (estimated) |
| **Front differential oil** | 4 years or 80,000 km | Included in fluid service |
| **Brake fluid** | 4 years or 80,000 km | Included in fluid service |
| **Coolant** | 6 years or 120,000 km | Included in fluid service |

### Total Cost Projection

| Period | Estimated Cost (CNY) |
|--------|---------------------|
| 6 years / 120,000 km total | ~13,277 |
| Average per year | ~2,213 |
| With cabin filter included | ~1,037/small service |

**Note**: Range extender km ≠ total km. The RE only runs when battery is depleted or in specific modes. Owners driving mostly in EV mode may reach time-based intervals before mileage-based ones.

**Sources**: [lixiang.com official guide](https://www.lixiang.com/community/detail/article/711719.html), [12365auto.com](https://www.12365auto.com/news/20220801/484538.shtml), [xchuxing.com](https://www.xchuxing.com/ins/166098)

### Russian Market Maintenance Considerations

From Russian service centers:
- **Suspension diagnostics**: Every 10,000-15,000 km (more frequent than Chinese recommendation due to road conditions)
- **Air suspension filter**: 15,000-30,000 rubles
- **Air suspension compressor drying**: 10,000 rubles/year
- **Compressor failure risk**: Without maintenance, failure within 10,000-15,000 km; repair costs 39,000-100,000 rubles
- **Pneumatic balloon (air spring)**: 51,000 rubles per unit
- **Regular maintenance**: 10,000-20,000 rubles per 5,000 km
- **Full annual cost** (active use): 100,000-200,000 rubles

**Source**: [getcar.ru](https://getcar.ru/blog/polomki-lixiang-l9-rossiya/)

---

## Recall History

| Date | Model | Units | Issue | Action |
|------|-------|-------|-------|--------|
| Nov 2020 | Li ONE | 10,469 | Front suspension control arm ball joint defect | Free replacement (SAMR) |
| Jul 2022 | Li L9 | N/A (test vehicle) | Air suspension spring buffer failure at 90 km/h over 20cm pothole | Warranty extended to 8 years/160,000 km |
| Oct 2025 | Li MEGA | 11,411 | Coolant anti-corrosion deficiency → battery thermal runaway risk | Recall via SAMR |

**Sources**: [ir.lixiang.com](https://ir.lixiang.com/news-releases/news-release-details/li-auto-inc-announces-voluntary-recall), [technode.com](https://technode.com/2022/07/19/li-auto-extends-l9-parts-warranty-after-suspension-failure-incident/), [carnewschina.com](https://carnewschina.com/2025/10/31/li-auto-recalls-over-11000-mega-2024-models-due-to-potential-battery-thermal-runaway-risk/)

---

## Known Common Problems (Technical)

### 1. Air Suspension Issues
- **Type**: Mechanical / pneumatic failure
- **Models**: L9 (all years), L7 (with air suspension option)
- **Details**: Compressor failure reported at 10,000-15,000 km without proper maintenance. Air spring buffer failure under heavy impact (20cm pothole at 90 km/h). Squeaking noises reported.
- **Cost**: Compressor 39,000-100,000 RUB; Air spring (balloon) 51,000 RUB per unit
- **Prevention**: Regular filter cleaning, compressor drying annually

### 2. BMS / Battery Issues
- **Type**: Software / hardware
- **Models**: Both L7/L9
- **Details**: Rapid battery degradation reports, BMS errors affecting charging, uneven power consumption in low temperatures, reduced range in cold climate
- **Dashboard warning**: 高压系统警告 (High voltage system warning)

### 3. Multimedia System Glitches
- **Type**: Software
- **Models**: Both L7/L9
- **Details**: Screen freezing, random reboots, infotainment crashes
- **Fix**: OTA updates, or multimedia board repair/replacement (available at specialized centers like li-auto.com)

### 4. Drive System Abnormalities
- **Type**: Motor controller / inverter
- **Models**: Both
- **Details**: Motor control unit faults, power electronics component failures
- **Dashboard warning**: 驱动系统异常 (Drive system abnormal)

### 5. Range Extender Emission Errors
- **Type**: Engine / exhaust
- **Models**: Both
- **Details**: Emission system abnormal warnings reported
- **Dashboard warning**: 排放系统异常 (Emission system abnormal)

### 6. Service Network Gaps (Russia/CIS)
- No official Li Auto dealerships in Russia
- Spare parts shortage → long repair wait times
- Lack of qualified specialists → diagnostic errors
- Russification and firmware updates require specialized service

**Sources**: [baku.ws](https://baku.ws/en/other/problems-with-lixiang-cars-what-owners-need-to-know), [getcar.ru](https://getcar.ru/en/blog/nadyozhnost-lixiang-l9-ekspluatacziya/), [getcar.ru problems](https://getcar.ru/blog/problemy-lixiang-l9-2024/)

---

## GitHub DTC Database Assessment

### Repositories Checked

| Repository | Content | Li Auto Coverage |
|-----------|---------|-----------------|
| [OBDb](https://github.com/OBDb) | Open source OBD database, daily updates | **No Li Auto/Lixiang repository** |
| [mytrile/obd-trouble-codes](https://github.com/mytrile/obd-trouble-codes) | 5,000+ generic OBD-II codes in JSON/CSV/SQLite | Generic SAE codes only, no manufacturer-specific |
| [todrobbins/dtcdb](https://github.com/todrobbins/dtcdb) | Diagnostic Trouble Code Database | Generic codes only |
| [wzr1337 gist](https://gist.github.com/wzr1337/8af2731a5ffa98f9d506537279da7a0e) | Complete OBD DTC list | Generic P/C/B/U codes |
| [lennykean/OBDII.DTC](https://github.com/lennykean/OBDII.DTC) | ISO/SAE standard codes | Standard only |
| [dsoprea/DtcLookup](https://github.com/dsoprea/DtcLookup) | Web-based DTC lookup | Generic codes |

**Conclusion**: No open-source database contains Li Auto-specific manufacturer codes. The generic P/C/B/U codes in these databases apply to the OBD-II compliant portion of the range extender engine only.

### Relevant External DTC Resources

- [obd-codes.com](https://www.obd-codes.com/) — comprehensive generic OBD-II code reference
- [dtcsearch.com](https://www.dtcsearch.com/) — DTC search engine
- [CSS Electronics DTC Tool](https://www.csselectronics.com/pages/obd-trouble-code-dtc-lookup-converter-tool) — converter and lookup
- [OBDeleven](https://obdeleven.com/obd-codes) — OBD diagnostic codes database

---

## Available Technical Documentation

### Commercial Service Manuals

| Product | Price | Content | Source |
|---------|-------|---------|--------|
| Li Auto Technical Training Manual | ~$800-1,500 | Power battery, body structure, chassis, electrical, diagnostics, intelligent cockpit | [cars-technical.com](https://cars-technical.com/product/li-auto-training/) |
| Li Auto Workshop Service Repair Manual | ~$500-1,000 | Wiring diagrams, repair procedures (2022-2024 L7/L8/L9) | [baochimingche.com](https://baochimingche.com/product/li-auto-workshop-service-repair-manual/) |
| Li Auto Parts Catalogue (EPC) | ~$300-500 | L6/L7/L8/L9/ONE/MEGA spare parts | [cars-technical.com](https://cars-technical.com/product/li-auto-parts-catalogue/) |
| Li Auto 2022 L9 Repair Manual | Not listed | Full repair manual for 2022 L9 EREV | [vixiu.xiuwww.com](http://vixiu.xiuwww.com/Shop/qc/electric/ONE/202405/4594.html) |

### Free Resources

| Resource | Content | URL |
|----------|---------|-----|
| L9 Maintenance Manual (PDF, Russian) | Official maintenance warnings, battery handling | [chinamobil.ru](https://chats.chinamobil.ru/files/lixiang-li-l7-l8-l9/applicationpdf/l9-maintenance.pdf) |
| L9 User Manual (PDF) | Owner's manual | [max.book118.com](https://max.book118.com/html/2023/0523/6211150131005133.shtm) |
| Li Auto Official Maintenance Guide | L-series maintenance schedule and FAQ | [lixiang.com](https://www.lixiang.com/community/detail/article/711719.html) |
| VIN Decoder | Li Auto VIN lookup and parts catalog | [17vin.com](https://en.17vin.com/brand/lixiang.html) |

### Parts Suppliers

| Supplier | Coverage | URL |
|----------|----------|-----|
| CINA AUTO PARTS | L7/L8/L9 wholesale parts | [cinaautoparts.com](https://www.cinaautoparts.com/lixiang-auto-parts.html) |
| Car China Parts | L7/L8/L9 extended-range components | [carchinaparts.com](https://www.carchinaparts.com/li-auto-l7-l8-l9-parts-wholesale/) |
| Sicily EVs | Li Auto brake pads (front/rear) | [sicily-evs.com](https://sicily-evs.com/autoparts/li-auto-brake-pads/) |
| CarModApps | Adapted apps for Lixiang (Russification) | [en.carmodapps.com](http://en.carmodapps.com/) |

---

## Li Auto Vehicle Data Architecture (Technical Note)

Li Auto uses GreptimeDB on-vehicle to unify vehicle-to-cloud telemetry. Data is decoded and structured at the edge, compressed with columnar techniques to reduce bandwidth and cloud processing costs. This suggests a sophisticated proprietary CAN/diagnostic data pipeline that goes beyond standard OBD-II.

**Source**: [greptime.com](https://www.greptime.com/blogs/2026-03-04-lixiang-vehicle-data-architecture)

---

## Methodology

### Search Queries Executed (30+ queries)

**DTC & Diagnostic Codes:**
1. "Li Auto L7 L9 DTC fault codes list diagnostic trouble codes"
2. "Li Auto L9 air suspension DTC code fault diagnostic"
3. "理想L9 故障码 DTC 空气悬挂 报错"
4. "理想汽车 L9 L7 故障码 诊断 P代码 C代码 常见故障"
5. "Li Auto BMS battery management system fault code error P U code EV diagnostic"
6. "Li Auto L7 L9 lixiang common DTC error codes dashboard warning P0 C0 owners forum"

**YouTube/Bilibili Repair Content:**
7. "youtube Li Auto L7 L9 repair service maintenance teardown"
8. "理想L7 L9 维修 拆解 视频 youtube bilibili"
9. "youtube Li Auto L9 disassembly chassis suspension brake teardown video 2024 2025"
10. "youtube ремонт Li Auto L7 L9 подвеска тормоза обслуживание"
11. "youtube lixiang L7 L9 ремонт обслуживание разборка видео русский"
12. "bilibili 理想L9 换刹车片 换机油 保养教程 拆解视频"

**Diagnostic Tools:**
13. "Li Auto OBD diagnostic scanner tool compatible work"
14. "lixiang OBD2 diagnostic scan tool ELM327 Autel Launch compatible"
15. "理想L9 OBD诊断 ELM327 兼容 诊断工具 扫描仪"
16. "cars-technical.com lixiang diagnostic tester scan tool specifications"
17. "Li Auto lixiang diagnostic app official vehicle self-diagnosis system OTA"

**Technical Specifications:**
18. "Li Auto 1.5T range extender engine specifications BMW Honda base"
19. "理想L9 增程器 1.5T 发动机 型号 参数 功率 扭矩 热效率"
20. "Li Auto L9 specifications battery kWh motor power torque weight dimensions"
21. "Li Auto L7 specifications engine 1.5T power battery range"
22. "Li Auto L9 battery CATL ternary lithium NMC specs voltage modules cells BMS"
23. "理想L9 空气悬挂 供应商 威巴克 孔辉 保隆 规格参数"
24. "Li Auto L9 air suspension compressor AMK Continental supplier"
25. "理想L9 L7 刹车 制动 卡钳 供应商 博世 大陆 规格"
26. "Li Auto L9 L7 OBD port location CAN protocol diagnostic connector pinout"
27. "Li Auto L9 Livis 800V active suspension by-wire chassis specifications 2026"

**Maintenance & Service:**
28. "Li Auto L9 L7 maintenance schedule service intervals oil change brake fluid coolant"
29. "理想L9 L7 保养周期 费用 机油滤芯 空调滤芯 变速箱油 前桥油"
30. "理想汽车 保养 前桥油 后桥油 冷却液 刹车液 更换周期 4年8万"
31. "理想汽车 保养手册 机油型号 冷却液 刹车油 规格"
32. "Li Auto L9 engine oil type 0W-30 coolant DOT4 brake fluid specification"

**Recalls & Problems:**
33. "Li Auto L9 recall list 2022 2023 2024 2025 NHTSA SAMR China"
34. "Li Auto L9 suspension failure warranty recall technical bulletin"
35. "Li Auto lixiang problems common issues owner complaints 2023 2024 2025"
36. "getcar.ru надёжность lixiang L9 эксплуатация проблемы отзывы"

**GitHub DTC Databases:**
37. "OBDb github Li Auto lixiang vehicle database"
38. "github DTC database obd trouble codes chinese vehicles EV"
39. "github mytrile obd-trouble-codes chinese vehicle EV specific codes"

### Search Coverage Assessment

| Area | Data Quality | Notes |
|------|-------------|-------|
| DTC Codes (Li Auto specific) | **Poor** | No public Li Auto DTC code list exists anywhere |
| Generic OBD-II Codes | **Good** | Well-documented in GitHub repos |
| Technical Specs (L7/L9) | **Good** | Wikipedia, OEM sites, reviewers |
| Maintenance Schedule | **Good** | Official Li Auto guide available |
| Fluid Specifications | **Fair** | Oil type confirmed (0W-30), others inferred |
| Diagnostic Tools | **Good** | Official tool identified ($9,200), third-party limited |
| Repair Videos (Chinese) | **Good** | Multiple Bilibili teardown videos found |
| Repair Videos (Russian) | **Fair** | Service centers found but no public video links |
| Repair Videos (English YouTube) | **Poor** | Very limited English repair content |
| Air Suspension Suppliers | **Excellent** | Three suppliers identified with market share data |
| Recall History | **Good** | Three recalls documented |
| Parts Numbers | **Poor** | No specific OEM part numbers found in public sources |
| Torque Specifications | **Poor** | Not publicly available |

### Key Gaps Remaining

1. **No Li Auto-specific DTC code table** exists in any public source (EN/RU/ZH)
2. **No torque specifications** found for any component
3. **No specific OEM part numbers** for brake pads, filters, or common wear items
4. **Battery BMS specifics** (cell count, module configuration, voltage) not publicly documented
5. **OBD port CAN bus protocol details** not available — likely uses proprietary extensions over standard CAN
6. **Limited English YouTube content** — most repair/teardown content is Chinese (Bilibili) or Russian
