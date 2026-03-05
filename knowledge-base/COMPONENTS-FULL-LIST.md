# Li Auto L7/L9 — Полный перечень компонентов и систем

> Автоматически сгенерировано из `i18n-glossary-data.json`, `system-components.json`, `layer-definitions.json` и `kb.db`

## Сводка

| Метрика | Значение |
|---------|----------|
| Всего компонентов | **1636** |
| Привязаны к 3D мешам | 107 |
| Привязаны к KB (чанки) | 306 |
| Имеют DTC коды | 102 |
| Слоёв визуализации | 8 |
| Диагностических групп | 5 |
| Языков | 5 (EN, RU, ZH, AR, ES) |

## Слои визуализации (8)

| # | Слой | Цвет | Компоненты | Описание (EN) | Описание (RU) |
|---|------|------|-----------|---------------|---------------|
| 1 | **body** | #4FC3F7 | 235 | Body & Frame | Силовой кузов |
| 2 | **engine** | #FF7043 | 329 | Engine, Fuel, Air & Exhaust | Двигатель, топливо, воздух и выхлоп |
| 3 | **drivetrain** | #AB47BC | 331 | Drivetrain & Suspension | Привод и подвеска |
| 4 | **ev** | #66BB6A | 191 | EV Electrical: Charging, Inverters, Motors, Regen | Электрика: зарядка, инверторы, электромоторы, рекуперация |
| 5 | **brakes** | #EF5350 | 152 | Steering & Braking System | Рулевое управление и тормозная система |
| 6 | **sensors** | #FFA726 | 113 | Sensors & ADAS | Датчики и системы помощи водителю (ADAS) |
| 7 | **hvac** | #26C6DA | 101 | HVAC & Thermal Management | Климат-контроль и терморегулирование |
| 8 | **interior** | #8D6E63 | 184 | Doors, Trunk & Interior | Двери, багажник и салон |

**Итого: 1636 компонентов**

## Диагностические группы (5)

| Группа | KB слои | Viz слои |
|--------|---------|----------|
| **electric** — Электрическая система | ev, battery | ev |
| **fuel** — Топливо и привод | engine, drivetrain | engine, drivetrain |
| **suspension** — Подвеска и тормоза | chassis, brakes | brakes |
| **cabin** — Кабина | body, interior, hvac | body, interior, hvac |
| **tech** — Технологии | infotainment, adas, sensors, lighting | sensors |

---

## 1. BODY — Силовой кузов (235 компонентов)

*Панели кузова, рама, бамперы, крылья, крыша, стойки, остекление, стеклоочистители, зеркала и наружное освещение*

**Подсистемы:** frame_structure, exterior_panels, glazing, wipers_washers, exterior_lighting, mirrors

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `adaptive_headlights@body` | adaptive headlights / cornering lights | адаптивная оптика (поворот фар) | 自适应大灯 / 转向辅助灯 | 0 | — | — | — |
| 2 | `apillar@body` | A-pillar | А-стойка | A柱 | 7 | — | — | — |
| 3 | `apillar_trim@body` | A-pillar trim | накладка стойки A | A柱饰板 | 0 | — | — | — |
| 4 | `body@body` | body / bodywork / car body | кузов автомобиля | 车身 | 29 | — | — | — |
| 5 | `body_control_module@body` | body control module (BCM) | модуль управления кузовом (BCM) | 车身控制模块（BCM） | 0 | — | — | — |
| 6 | `body_panel@body` | body panel | панель кузова | 车身面板 | 0 | — | — | — |
| 7 | `body_shell@body` | Body R — Panel | кузов (несущий) | 车身右 — 面板 | 0 | 26 | 15 | B1011, B1012, B1250, B1251, B1260 |
| 8 | `body_structure@body` | body structure / body cage | силовой каркас кузова | 车身结构 / 车身框架 | 0 | — | — | — |
| 9 | `body_trim@body` | body trim / moulding | молдинг кузова | 车身饰条 | 0 | — | — | — |
| 10 | `body_trim_moulding@body` | body trim / moulding | молдинг кузова | 车身饰条 | 0 | — | 4 | B1011, B1012 |
| 11 | `bodyonframe@body` | body-on-frame | кузов на раме (рамная конструкция) | 非承载式车身（BOF） | 0 | — | — | — |
| 12 | `bonnet@body` | Hood / Bonnet | капот | 发动机罩 | 0 | — | — | — |
| 13 | `bonnet_hinge@body` | bonnet hinge / hood hinge | петля капота | 发动机盖铰链 | 0 | — | — | — |
| 14 | `bonnet_hood@body` | bonnet / hood | капот | 发动机罩 | 19 | 1 | 1 | B1011 |
| 15 | `bonnet_latch@body` | bonnet latch / hood latch | замок капота | 发动机盖锁扣 | 1 | — | — | — |
| 16 | `bonnet_strut@body` | bonnet strut / hood support rod / hood prop | упор капота | 发动机盖支撑杆 | 0 | — | — | — |
| 17 | `boot@body` | boot / trunk | багажник | 后备箱 | 0 | — | — | — |
| 18 | `boot_trunk@body` | boot / trunk | багажник | 后备箱 | 60 | — | 1 | B1019, B1020 |
| 19 | `bpillar@body` | B-pillar | В-стойка | B柱 | 8 | — | — | — |
| 20 | `bpillar_trim@body` | B-pillar trim | накладка стойки B | B柱饰板 | 0 | — | — | — |
| 21 | `bumper_cover@body` | bumper cover | накладка бампера | 保险杠面板 | 0 | — | — | — |
| 22 | `bumper_reinforcement@body` | Rear Bumper — Molding | бампер (усилитель) | 后保险杠 — 饰条 | 0 | — | 2 | B1011, B1012 |
| 23 | `chetvertnye_paneli@body` | Quarter Panels R — Panel | Четвертные панели#2 — Панель | 后翼子板右 — 面板 | 0 | — | — | — |
| 24 | `cowl_panel@body` | cowl panel | панель ветрового стекла (жабо) | 前围板 | 1 | — | — | — |
| 25 | `cpillar@body` | C-pillar | С-стойка | C柱 | 4 | — | — | — |
| 26 | `cpillar_trim@body` | C-pillar trim | накладка стойки C | C柱饰板 | 0 | — | — | — |
| 27 | `cross_member@body` | cross member | поперечина | 横梁 | 8 | — | — | — |
| 28 | `defroster@body` | defroster / demister | обогрев стекла | 除霜器 | 0 | — | — | — |
| 29 | `diffuser@body` | diffuser / rear diffuser | диффузор | 扩散器 / 后扩散器 | 0 | — | — | — |
| 30 | `door_glass@body` | Door Glass RR | стекло двери | 门玻璃右后 | 0 | 4 | 4 | B1011, B1012, B1013, B1014 |
| 31 | `door_handle@body` | door handle | ручка двери | 门把手 | 70 | 4 | — | B1011, B1012 |
| 32 | `door_hinge@body` | door hinges | петли дверей | 车门铰链 | 0 | — | — | — |
| 33 | `door_inner_handle@body` | door inner handle / interior door handle | ручка двери внутренняя | 车门内开手柄 | 0 | — | — | — |
| 34 | `door_lock_system@body` | door lock system | система замков дверей | 门锁系统 | 0 | — | — | — |
| 35 | `door_outer_handle@body` | door outer handle / exterior door handle | ручка двери наружная | 车门外开手柄 | 0 | — | — | — |
| 36 | `door_seal@body` | door seals | уплотнители дверей | 车门密封条 | 0 | — | — | — |
| 37 | `door_sill@body` | door sill / window sill | порог двери / нижняя кромка окна двери | 门槛 / 窗台 | 0 | — | — | — |
| 38 | `door_trim_panel@body` | door trim panel / door card | дверная карта / обшивка двери | 车门内饰板 | 0 | 2 | 3 | B1011, B1012 |
| 39 | `dopolnitelnyy_element@body` | Dopolnitelnyy Element | Дополнительный элемент | Дополнительный элемент | 0 | — | — | — |
| 40 | `dpillar@body` | D-pillar | стойка D | D柱 | 5 | — | — | — |
| 41 | `dpillar_trim@body` | D-pillar trim | накладка стойки D | D柱饰板 | 0 | — | — | — |
| 42 | `drip_rail@body` | drip rail / gutter | водосточный жёлоб крыши | 车顶排水槽 | 0 | — | — | — |
| 43 | `drl_lights@body` | daytime running lights (DRL) | дневные ходовые огни (ДХО) | 日间行车灯 | 0 | — | — | — |
| 44 | `dvernaya_karta_pl@body` | Door Panel FL | Дверная карта ПЛ | 门板左前 | 0 | — | — | — |
| 45 | `dvernaya_karta_pp@body` | Door Panel FR | Дверная карта ПП | 门板右前 | 0 | — | — | — |
| 46 | `element_kuzova@body` | Element Kuzova | Элемент кузова | Элемент кузова | 0 | — | — | — |
| 47 | `element_kuzova_arka@body` | Element Kuzova Arka | Элемент кузова (арка) | Элемент кузова (арка) | 0 | — | — | — |
| 48 | `element_kuzova_bokovoy@body` | Element Kuzova Bokovoy | Элемент кузова (боковой) | Элемент кузова (боковой) | 0 | — | — | — |
| 49 | `element_kuzova_bokovoy_l@body` | Element Kuzova Bokovoy L | Элемент кузова (боковой Л) | Элемент кузова (боковой Л) | 0 | — | — | — |
| 50 | `element_kuzova_bokovoy_p@body` | Element Kuzova Bokovoy P | Элемент кузова (боковой П) | Элемент кузова (боковой П) | 0 | — | — | — |
| 51 | `element_kuzova_krysha@body` | Element Kuzova Krysha | Элемент кузова (крыша) | Элемент кузова (крыша) | 0 | — | — | — |
| 52 | `element_kuzova_molding@body` | Element Kuzova Molding | Элемент кузова (молдинг) | Элемент кузова (молдинг) | 0 | — | — | — |
| 53 | `element_kuzova_nakladka@body` | Element Kuzova Nakladka | Элемент кузова (накладка) | Элемент кузова (накладка) | 0 | — | — | — |
| 54 | `element_kuzova_nizhniy@body` | Element Kuzova Nizhniy | Элемент кузова (нижний) | Элемент кузова (нижний) | 0 | — | — | — |
| 55 | `element_kuzova_osnovnoy@body` | Element Kuzova Osnovnoy | Элемент кузова (основной) | Элемент кузова (основной) | 0 | — | — | — |
| 56 | `element_kuzova_peredniy@body` | Element Kuzova Peredniy | Элемент кузова (передний) | Элемент кузова (передний) | 0 | — | — | — |
| 57 | `element_kuzova_porogi@body` | Element Kuzova Porogi | Элемент кузова (пороги) | Элемент кузова (пороги) | 0 | — | — | — |
| 58 | `element_kuzova_ramka@body` | Element Kuzova Ramka | Элемент кузова (рамка) | Элемент кузова (рамка) | 0 | — | — | — |
| 59 | `element_kuzova_stoyki@body` | Element Kuzova Stoyki | Элемент кузова (стойки) | Элемент кузова (стойки) | 0 | — | — | — |
| 60 | `element_kuzova_zadniy@body` | Element Kuzova Zadniy | Элемент кузова (задний) | Элемент кузова (задний) | 0 | — | — | — |
| 61 | `element_kuzova_zadnyaya_chast@body` | Element Kuzova Zadnyaya Chast | Элемент кузова (задняя часть) | Элемент кузова (задняя часть) | 0 | — | — | — |
| 62 | `element_shassi@body` | Element Shassi | Элемент шасси | Элемент шасси | 0 | — | — | — |
| 63 | `element_shassi_bokovoy@body` | Element Shassi Bokovoy | Элемент шасси (боковой) | Элемент шасси (боковой) | 0 | — | — | — |
| 64 | `element_shassi_nizhniy@body` | Element Shassi Nizhniy | Элемент шасси (нижний) | Элемент шасси (нижний) | 0 | — | — | — |
| 65 | `element_shassi_osnovnoy@body` | Element Shassi Osnovnoy | Элемент шасси (основной) | Элемент шасси (основной) | 0 | — | — | — |
| 66 | `element_shassi_peredniy@body` | Element Shassi Peredniy | Элемент шасси (передний) | Элемент шасси (передний) | 0 | — | — | — |
| 67 | `element_shassi_poperechnyy@body` | Element Shassi Poperechnyy | Элемент шасси (поперечный) | Элемент шасси (поперечный) | 0 | — | — | — |
| 68 | `element_shassi_sredniy@body` | Element Shassi Sredniy | Элемент шасси (средний) | Элемент шасси (средний) | 0 | — | — | — |
| 69 | `element_shassi_zadniy@body` | Element Shassi Zadniy | Элемент шасси (задний) | Элемент шасси (задний) | 0 | — | — | — |
| 70 | `emblem@body` | emblem / badge | эмблема / значок | 徽标 | 0 | 4 | 1 | B1501, B1502 |
| 71 | `engine_bay@body` | engine bay / engine compartment | моторный отсек | 发动机舱 | 4 | — | — | — |
| 72 | `fara_levaya@body` | Headlight — High Beam Module | Фара левая#2 — Модуль дальнего | 大灯 — 远光模组 | 0 | — | — | — |
| 73 | `fara_pravaya@body` | Headlight — High Beam Module | Фара правая#2 — Модуль дальнего | 大灯 — 远光模组 | 0 | — | — | — |
| 74 | `fascia_panel@body` | fascia panel | панель приборов | 仪表面板 | 0 | — | — | — |
| 75 | `fender@body` | fender / wing | крыло | 翼子板 | 0 | — | — | — |
| 76 | `fender_liner@body` | fender liner | подкрылок | 翼子板内衬 | 0 | — | 1 | B1011, B1012 |
| 77 | `fender_wing@body` | fender / wing | крыло | 翼子板 | 7 | 6 | 2 | B1011, B1012 |
| 78 | `filler_cap@body` | filler cap | крышка заливной горловины | 加油口盖 | 0 | — | — | — |
| 79 | `firewall@body` | firewall / bulkhead / engine bay divider | моторный щит | 防火墙 / 发动机舱隔板 | 0 | — | — | — |
| 80 | `flitch_panel@body` | flitch panel | панель брызговика | 翼子板内板 | 0 | — | — | — |
| 81 | `floor_pan@body` | Floor — Heat Shield | пол кузова | 底板 — 隔热板 | 0 | 1 | 1 | B1011, B1012 |
| 82 | `foam_impact_absorber@body` | foam impact absorber / crash box | поглотитель удара / пенопластовый вкладыш | 泡沫吸能块 / 碰撞吸能盒 | 0 | — | — | — |
| 83 | `fog_light_front@body` | front fog light | передняя противотуманная фара | 前雾灯 | 0 | — | — | — |
| 84 | `fog_light_rear@body` | rear fog light | задняя противотуманная фара | 后雾灯 | 42 | — | — | — |
| 85 | `fonar_kryshki_bagazhnika@body` | Fonar Kryshki Bagazhnika | Фонарь крышки багажника | Фонарь крышки багажника | 0 | — | — | — |
| 86 | `frame@body` | frame | рама | 车架 | 4 | — | — | — |
| 87 | `front_bumper@body` | front bumper | передний бампер | 前保险杠 | 3 | 4 | 1 | B1011, B1012 |
| 88 | `front_bumper_cover@body` | front bumper cover | накладка бампера (перед.) | 前保险杠面板 | 0 | — | — | — |
| 89 | `front_bumper_reinforcement@body` | front bumper reinforcement | усилитель бампера (перед.) | 前保险杠加强梁 | 0 | — | — | — |
| 90 | `front_crossmember@body` | front crossmember / radiator support | передний брус кузова | 前横梁 / 散热器支架 | 0 | — | — | — |
| 91 | `front_door@body` | front door | передняя дверь | 前车门 | 16 | 2 | 2 | B1011, B1012 |
| 92 | `front_left_fender@body` | front left fender | крыло (перед., лев.) | 左前翼子板 | 0 | — | — | — |
| 93 | `front_left_fender_liner@body` | front left fender liner | подкрылок (перед., лев.) | 左前翼子板内衬 | 0 | — | — | — |
| 94 | `front_left_window_glass@body` | front left window glass | стекло (перед., лев.) | 左前车窗玻璃 | 0 | — | — | — |
| 95 | `front_left_window_regulator@body` | front left window regulator | стеклоподъёмник (перед., лев.) | 左前车窗升降器 | 0 | — | — | — |
| 96 | `front_left_window_switch@body` | front left window switch | кнопка стеклоподъёмника (перед., лев.) | 左前车窗升降开关 | 0 | — | — | — |
| 97 | `front_lip@body` | front lip / air splitter / chin spoiler | передний спойлер / сплиттер | 前唇 / 分流器 / 下巴扰流板 | 0 | — | — | — |
| 98 | `front_right_fender@body` | front right fender | крыло (перед., прав.) | 右前翼子板 | 0 | — | — | — |
| 99 | `front_right_fender_liner@body` | front right fender liner | подкрылок (перед., прав.) | 右前翼子板内衬 | 0 | — | — | — |
| 100 | `front_right_window_glass@body` | front right window glass | стекло (перед., прав.) | 右前车窗玻璃 | 0 | — | — | — |
| 101 | `front_right_window_regulator@body` | front right window regulator | стеклоподъёмник (перед., прав.) | 右前车窗升降器 | 0 | — | — | — |
| 102 | `front_right_window_switch@body` | front right window switch | кнопка стеклоподъёмника (перед., прав.) | 右前车窗开关 | 0 | — | — | — |
| 103 | `grille@body` | grille | решётка радиатора | 进气格栅 | 38 | — | 7 | B1501, B1502 |
| 104 | `grille_position_light@body` | grille position light | габаритный огонь в решётке радиатора | 格栅位置灯 | 1 | — | — | — |
| 105 | `grille_trim@body` | grille trim / grille molding | молдинг решётки радиатора | 格栅装饰条 | 0 | — | — | — |
| 106 | `gutter@body` | gutter | водосток | 水槽 | 1 | — | — | — |
| 107 | `headlight@body` | headlight | фара | 前大灯 | 15 | 12 | 1 | B1250, B1251, B1260 |
| 108 | `headlight_lens@body` | headlight lens | стекло фары | 大灯透镜 | 0 | 8 | 1 | B1250, B1251, B1260 |
| 109 | `headlight_levelling@body` | headlight levelling / headlamp adjuster | корректор положения фар | 前照灯调平器 | 0 | — | — | — |
| 110 | `headlight_washer@body` | headlight washer | омыватель фар | 前照灯清洗器 | 0 | — | — | — |
| 111 | `heat_shield@body` | heat shield | теплозащитный экран | 隔热板 | 13 | — | 1 | B1011, B1012 |
| 112 | `heated_rear_window_element@body` | heated rear window element | нить обогрева заднего стекла | 后窗加热丝 | 0 | — | — | — |
| 113 | `highmount_brake_light@body` | high-mount brake light | дополнительный стоп-сигнал | 高位制动灯 | 29 | — | — | — |
| 114 | `inner_wing@body` | inner wing | внутренний брызговик | 内翼子板 | 0 | — | — | — |
| 115 | `interior_trim@body` | interior trim | обшивка салона | 内饰装饰 | 0 | 9 | — | B1011, B1012, B1250, B1251 |
| 116 | `jacking_point@body` | jacking point | точка установки домкрата | 举升点 | 5 | — | — | — |
| 117 | `kolyosnye_arki@body` | Kolyosnye Arki | Колёсные арки | Колёсные арки | 0 | — | — | — |
| 118 | `kryshka_dnishcha@body` | Underbody Cover | Крышка днища | 底盘盖 | 0 | — | — | — |
| 119 | `ladder_frame@body` | ladder frame / chassis frame | рама лестничного типа | 梯形车架 | 0 | — | — | — |
| 120 | `left_apillar_trim@body` | left A-pillar trim | накладка стойки A (лев.) | 左A柱饰板 | 0 | — | — | — |
| 121 | `left_bpillar_trim@body` | left B-pillar trim | накладка стойки B (лев.) | 左B柱饰板 | 0 | — | — | — |
| 122 | `left_cpillar_trim@body` | left C-pillar trim | накладка стойки C (лев.) | 左C柱饰板 | 0 | — | — | — |
| 123 | `left_dpillar_trim@body` | left D-pillar trim | накладка стойки D (лев.) | 左D柱饰板 | 0 | — | — | — |
| 124 | `left_subframe@body` | left subframe | подрамник (лев.) | 左副车架 | 0 | — | — | — |
| 125 | `licence_plate@body` | licence plate | номерной знак | 车牌 | 2 | 2 | — | B1501, B1502 |
| 126 | `licence_plate_bracket@body` | licence-plate bracket | рамка номерного знака | 车牌框 | 0 | 1 | — | B1501, B1502 |
| 127 | `longitudinal_member@body` | longitudinal member / rail | лонжерон | 纵梁 | 3 | — | — | — |
| 128 | `lyuk@body` | Sunroof L — Glass | Люк#2 — Стекло | 天窗左 — 玻璃 | 0 | — | — | — |
| 129 | `monocoque@body` | monocoque / unibody | несущий кузов (монокок) | 承载式车身 | 0 | — | — | — |
| 130 | `mud_flap@body` | mud flap / splash guard | брызговик | 挡泥板 | 0 | — | — | — |
| 131 | `nadpis@body` | Badge | Надпись "+" | 标识 | 0 | — | — | — |
| 132 | `nadpis_chyornaya@body` | Badge | Надпись чёрная | 标识 | 0 | — | — | — |
| 133 | `nadpis_d@body` | Badge | Надпись "D" | 标识 | 0 | — | — | — |
| 134 | `nadpis_khrom@body` | Badge | Надпись хром | 标识 | 0 | — | — | — |
| 135 | `nadpis_modeli@body` | Badge | Надпись модели | 标识 | 10 | — | — | — |
| 136 | `nakladka_lyuka@body` | Sunroof Trim | Накладка люка | 天窗饰条 | 0 | — | — | — |
| 137 | `nakladki_kuzova@body` | Nakladki Kuzova | Накладки кузова | Накладки кузова | 0 | — | — | — |
| 138 | `nomernoy_znak_peredniy@body` | License Plate | Номерной знак передний | 车牌 | 0 | — | — | — |
| 139 | `nomernoy_znak_zadniy@body` | License Plate | Номерной знак задний | 车牌 | 0 | — | — | — |
| 140 | `panel_dveri_pp_element@body` | Panel Dveri Pp Element | Панель двери ПП (элемент) | Панель двери ПП (элемент) | 0 | — | — | — |
| 141 | `panel_dveri_pp_element_2@body` | Panel Dveri Pp Element 2 | Панель двери ПП (элемент 2) | Панель двери ПП (элемент 2) | 0 | — | — | — |
| 142 | `panel_dveri_zl@body` | Panel Dveri Zl | Панель двери ЗЛ | Панель двери ЗЛ | 0 | — | — | — |
| 143 | `panoramic_roof@body` | panoramic roof | панорамная крыша | 全景天窗 | 0 | — | — | — |
| 144 | `panoramic_sunroof@body` | panoramic sunroof / panoramic roof | панорамный люк | 全景天窗 | 0 | — | — | — |
| 145 | `pillar_a@body` | pillar (A/B/C/D) | стойка кузова (A/B/C/D) | 立柱 (A/B/C/D) | 0 | — | — | — |
| 146 | `podkrylki@body` | Podkrylki | Подкрылки | Подкрылки | 0 | — | — | — |
| 147 | `poverkhnost_kuzova@body` | Poverkhnost Kuzova | Поверхность кузова | Поверхность кузова | 0 | — | — | — |
| 148 | `power_liftgate@body` | power liftgate | электропривод багажника | 电动尾门 | 1 | — | — | — |
| 149 | `quarter_panel@body` | quarter panel | задняя боковина | 后侧围板 | 0 | 4 | — | B1011, B1012, B1250, B1251 |
| 150 | `radiator@body` | Radiator — Frame | Радиатор#2 — Каркас | 散热器 — 框架 | 0 | 1 | — | P0A7F |
| 151 | `rain_sensor@body` | rain sensor | датчик дождя | 雨量传感器 | 0 | — | — | — |
| 152 | `ramka_nomera@body` | License Plate Frame | Рамка номера | 车牌框 | 0 | — | — | — |
| 153 | `rear_bumper@body` | rear bumper | задний бампер | 后保险杠 | 0 | 5 | 1 | B1011, B1012 |
| 154 | `rear_bumper_cover@body` | rear bumper cover | накладка бампера (зад.) | 后保险杠护板 | 0 | — | — | — |
| 155 | `rear_bumper_reinforcement@body` | rear bumper reinforcement | усилитель бампера (зад.) | 后保险杠加强件 | 0 | — | — | — |
| 156 | `rear_door@body` | Door | Дверь задняя правая | 车门 | 42 | 2 | 2 | B1013, B1014 |
| 157 | `rear_left_fender@body` | rear left fender | крыло (зад., лев.) | 后左翼子板 | 0 | — | — | — |
| 158 | `rear_left_fender_liner@body` | rear left fender liner | подкрылок (зад., лев.) | 后左轮罩衬板 | 0 | — | — | — |
| 159 | `rear_left_window_glass@body` | rear left window glass | стекло (зад., лев.) | 后左车窗玻璃 | 0 | — | — | — |
| 160 | `rear_left_window_regulator@body` | rear left window regulator | стеклоподъёмник (зад., лев.) | 后左车窗升降器 | 0 | — | — | — |
| 161 | `rear_left_window_switch@body` | rear left window switch | кнопка стеклоподъёмника (зад., лев.) | 后左车窗开关 | 0 | — | — | — |
| 162 | `rear_panel@body` | rear panel / tail panel | задняя панель кузова | 后围板 | 0 | — | — | — |
| 163 | `rear_right_door_handle@body` | Door Handle RR | Ручка двери ЗП | 门把手右后 | 0 | — | — | — |
| 164 | `rear_right_fender@body` | Fender R — Panel | крыло (зад., прав.) | 翼子板右 — 面板 | 0 | — | — | — |
| 165 | `rear_right_fender_liner@body` | rear right fender liner | подкрылок (зад., прав.) | 后右轮罩衬板 | 0 | — | — | — |
| 166 | `rear_right_window_glass@body` | rear right window glass | стекло (зад., прав.) | 后右车窗玻璃 | 0 | — | — | — |
| 167 | `rear_right_window_regulator@body` | rear right window regulator | стеклоподъёмник (зад., прав.) | 后右车窗升降器 | 0 | — | — | — |
| 168 | `rear_right_window_switch@body` | rear right window switch | кнопка стеклоподъёмника (зад., прав.) | 后右车窗开关 | 0 | — | — | — |
| 169 | `rear_seat@body` | rear seat | заднее сиденье | 后座椅 | 13 | 3 | — | B1011, B1012 |
| 170 | `rear_view_mirror@body` | rear view mirror / interior mirror | зеркало заднего вида (внутреннее) | 室内后视镜 | 0 | — | — | — |
| 171 | `rear_window@body` | rear window | заднее стекло | 后挡风玻璃 | 117 | 1 | 1 | B1019, B1020 |
| 172 | `rear_window_heater@body` | rear window heater / rear demister | подогрев заднего стекла | 后窗除雾加热器 | 0 | — | — | — |
| 173 | `rear_wing@body` | rear wing / spoiler wing | антикрыло | 后扰流翼 / 尾翼 | 0 | — | — | — |
| 174 | `retractable_hardtop@body` | retractable hardtop / folding hardtop | жёсткая складная крыша | 可收折硬顶 | 0 | — | — | — |
| 175 | `right_apillar_trim@body` | right A-pillar trim | накладка стойки A (прав.) | 右A柱饰板 | 0 | — | — | — |
| 176 | `right_bpillar_trim@body` | right B-pillar trim | накладка стойки B (прав.) | 右B柱饰板 | 0 | — | — | — |
| 177 | `right_cpillar_trim@body` | right C-pillar trim | накладка стойки C (прав.) | 右C柱饰板 | 0 | — | — | — |
| 178 | `right_dpillar_trim@body` | right D-pillar trim | накладка стойки D (прав.) | 右D柱饰板 | 0 | — | — | — |
| 179 | `right_headlight@body` | Headlight | Фара | 大灯 | 26 | — | — | — |
| 180 | `right_subframe@body` | right subframe | подрамник (прав.) | 右副车架 | 0 | — | — | — |
| 181 | `right_taillight@body` | Right Taillight | Задний фонарь левый | Задний фонарь левый | 0 | — | — | — |
| 182 | `rocker_panel@body` | rocker panel (sill) | порог кузова | 门槛板 | 0 | — | — | — |
| 183 | `roof@body` | Roof | крыша | 车顶 | 3 | 1 | 1 | B1011, B1012 |
| 184 | `roof_panel@body` | roof panel | панель крыши | 车顶板 | 0 | — | — | — |
| 185 | `roof_rack@body` | roof rack | рейлинги на крыше | 车顶行李架 | 0 | — | — | — |
| 186 | `safety_cell@body` | safety cell / safety cage | силовая ячейка безопасности | 安全笼 / 安全车身骨架 | 0 | — | — | — |
| 187 | `scuttle@body` | scuttle | щиток передка | 前围上盖板 | 0 | — | — | — |
| 188 | `side_impact_beam@body` | side impact beam | брус безопасности двери | 侧面防撞梁 | 0 | — | — | — |
| 189 | `side_skirts@body` | side skirts / side sills | боковые юбки | 侧裙板 | 0 | — | — | — |
| 190 | `side_window@body` | Side Window — Glass | боковое стекло | 侧窗 — 玻璃 | 0 | 4 | 2 | — |
| 191 | `sidenya_zadnie@body` | Rear Seats — Lining | Сиденья задние#2 — Обшивка | 后排座椅 — 衬里 | 0 | — | — | — |
| 192 | `sill@body` | sill / rocker panel | порог | 门槛板 | 0 | — | — | — |
| 193 | `sill_rocker_panel@body` | sill / rocker panel | порог | 门槛板 | 9 | — | 1 | B1011, B1012 |
| 194 | `space_frame@body` | space frame | пространственная рама | 空间框架 | 0 | — | — | — |
| 195 | `spoiler@body` | spoiler | спойлер | 扰流板 | 8 | — | — | — |
| 196 | `subframe@body` | subframe | подрамник | 副车架 | 0 | — | 8 | B1011, B1012 |
| 197 | `sunroof@body` | sunroof / sliding roof | люк / откидной люк | 天窗 / 滑动车顶 | 0 | — | — | — |
| 198 | `sunroof_glass@body` | sunroof glass | стекло люка | 天窗玻璃 | 2 | 2 | — | — |
| 199 | `sunroof_motor@body` | sunroof motor | мотор люка | 天窗电机 | 0 | — | — | — |
| 200 | `sunroof_panel@body` | sunroof | люк крыши | 天窗 | 3 | 3 | — | B1011, B1012 |
| 201 | `tail_light_lens@body` | tail light lens | стекло фонаря | 尾灯透镜 | 0 | — | 3 | B1019, B1020, B1260, B1261, B1262, B1263 |
| 202 | `tailgate@body` | tailgate | задняя дверь (лифтбек) | 尾门 | 5 | — | — | — |
| 203 | `taillight@body` | taillight | задний фонарь | 尾灯 | 1 | — | 2 | B1260, B1261, B1262, B1263 |
| 204 | `teplozashchita@body` | Teplozashchita | Теплозащита | Теплозащита | 0 | — | — | — |
| 205 | `tow_hook@body` | tow hook / towing eye | буксировочная проушина | 拖车钩 | 75 | — | — | — |
| 206 | `transmission_tunnel@body` | transmission tunnel / center tunnel | туннель трансмиссии | 传动轴隧道 / 中央通道 | 0 | — | — | — |
| 207 | `trunk_lid@body` | trunk lid | крышка багажника | 后备箱盖 | 16 | 1 | 1 | B1019, B1020 |
| 208 | `underbody_cover@body` | Underbody Protection | защита днища | 底盘护板 | 0 | 2 | 1 | B1011, B1012 |
| 209 | `usilenie_peredney_chasti@body` | Usilenie Peredney Chasti | Усиление передней части | Усиление передней части | 0 | — | — | — |
| 210 | `valance@body` | valance | нижняя панель бампера | 裙板 / 保险杠下饰板 | 0 | — | — | — |
| 211 | `washer_fluid@body` | washer fluid tank | бачок омывателя | 雨刮液壶 | 1 | — | — | — |
| 212 | `washer_fluid_reservoir@body` | washer fluid reservoir / screenwash reservoir | бачок омывателя | 洗涤液储液壶 | 0 | — | — | — |
| 213 | `washer_nozzle@body` | washer nozzle / spray nozzle | форсунка омывателя | 洗涤喷嘴 | 0 | — | — | — |
| 214 | `washer_pump@body` | washer pump | насос омывателя | 洗涤泵 | 0 | — | — | — |
| 215 | `wheel_arch_liner@body` | wheel arch liner | подкрылок / колёсные арки | 轮拱衬板 | 0 | — | 2 | B1011, B1012 |
| 216 | `wheelarch@body` | wheelarch | арка колеса | 轮拱 | 0 | — | — | — |
| 217 | `window_channel@body` | window channel / window guide | направляющая стекла | 车窗导槽 | 0 | — | — | — |
| 218 | `window_glass@body` | window glass | стекло | 车窗玻璃 | 84 | — | — | — |
| 219 | `window_regulator@body` | window regulator | стеклоподъёмник | 车窗升降器 | 0 | — | — | — |
| 220 | `window_switch@body` | window switch | кнопка стеклоподъёмника | 车窗开关 | 72 | — | — | — |
| 221 | `windowmounted_antenna@body` | window-mounted antenna / film antenna | плёночная антенна | 车窗贴膜天线 | 0 | — | — | — |
| 222 | `windscreen@body` | Windshield L — Glass | лобовое стекло | 前挡风玻璃左 — 玻璃 | 0 | — | — | — |
| 223 | `windscreen_washer@body` | windscreen washer | омыватель лобового стекла | 挡风玻璃清洗器 | 1 | — | — | — |
| 224 | `windscreen_windshield@body` | windscreen / windshield | лобовое стекло | 前挡风玻璃 | 87 | 3 | 1 | — |
| 225 | `windscreen_wiper@body` | windscreen wiper | стеклоочиститель | 雨刷 | 5 | — | — | — |
| 226 | `windshield@body` | windshield / windscreen | ветровое стекло (лобовое) | 挡风玻璃 | 235 | — | — | — |
| 227 | `windshield_washer@body` | windshield washer | стеклоомыватель | 挡风玻璃清洗器 | 0 | — | — | — |
| 228 | `windshield_wiper@body` | windshield wipers | стеклоочистители | 雨刮器 | 124 | — | — | — |
| 229 | `wing_mirror@body` | wing mirror / door mirror / side mirror | зеркало боковое / наружное | 外后视镜 / 侧后视镜 | 0 | — | — | — |
| 230 | `wing_mirror_door_mirror_side_mirror@body` | wing mirror / door mirror / side mirror | зеркало боковое / наружное | 外后视镜 / 侧后视镜 | 0 | 12 | 2 | B1260, B1501, B1502 |
| 231 | `wiper_blade@body` | wiper blade | щётка стеклоочистителя | 雨刷片 | 0 | — | — | — |
| 232 | `wiper_linkage@body` | wiper linkage | трапеция стеклоочистителей | 雨刷连杆机构 | 0 | — | — | — |
| 233 | `zadnyaya_panel_element@body` | Zadnyaya Panel Element | Задняя панель (элемент) | Задняя панель (элемент) | 0 | — | — | — |
| 234 | `zerkalo_levoe@body` | Mirror R — Panel | Зеркало левое#2 — Панель | 后视镜右 — 面板 | 0 | — | — | — |
| 235 | `zerkalo_pravoe@body` | Mirror R — Panel | Зеркало правое#2 — Панель | 后视镜右 — 面板 | 0 | — | — | — |

## 2. ENGINE — Двигатель, топливо, воздух и выхлоп (329 компонентов)

*ДВС, топливная система, впуск, выхлоп, турбо/компрессор, охлаждение, смазка, зажигание и контроль выбросов*

**Подсистемы:** engine_block, valve_train, fuel_system, air_intake, exhaust_system, turbo_supercharger, cooling_system, lubrication, ignition, emission_control

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `accelerator_pump@engine` | accelerator pump | ускорительный насос карбюратора | 加速泵 | 0 | — | — | — |
| 2 | `active_grille_shutters@engine` | active grille shutters / radiator shutters | жалюзи радиатора | 主动进气格栅挡板 | 0 | — | — | — |
| 3 | `air_cleaner@engine` | air cleaner | воздухоочиститель | 空气滤清器 | 26 | — | — | — |
| 4 | `air_filter@engine` | air filter | воздушный фильтр | 空气滤清器 | 1 | — | — | — |
| 5 | `air_filter_element@engine` | air filter element | фильтрующий элемент воздушного фильтра | 空滤芯 | 0 | — | — | — |
| 6 | `air_filter_housing@engine` | air filter housing / airbox | корпус воздушного фильтра | 空滤器壳体 | 0 | — | — | — |
| 7 | `air_intake@engine` | air intake | воздухозаборник | 进气口 | 4 | — | — | — |
| 8 | `aircooled_system@engine` | air-cooled system | воздушная система охлаждения | 风冷系统 | 0 | — | — | — |
| 9 | `alternator_ann@engine` | alternator / generator | генератор | 发电机 | 18 | — | — | — |
| 10 | `balance_shaft@engine` | balance shaft | балансировочный вал | 平衡轴 | 0 | — | — | — |
| 11 | `bigend_bearing@engine` | big-end bearing | шатунный вкладыш | 连杆大端轴承 | 0 | — | — | — |
| 12 | `blowoff_valve@engine` | blow-off valve / bypass valve / dump valve | байпасный клапан / blow-off valve | 泄压阀／旁通阀 | 0 | — | — | — |
| 13 | `body_shell@engine` | Body L — Fuel Door | Кузов#2 — Лючок бака | 车身左 — 油箱盖 | 0 | 1 | — | P0171, P0300 |
| 14 | `boost_pressure_sensor@engine` | boost pressure sensor | датчик давления наддува | 增压压力传感器 | 0 | — | — | — |
| 15 | `brake_proportioning_valve@engine` | brake proportioning valve | регулятор тормозных сил | 制动力比例阀 | 0 | — | — | — |
| 16 | `bypass_hose@engine` | bypass hose | байпасный патрубок | 旁通软管 | 0 | — | — | — |
| 17 | `cam_lobe@engine` | cam lobe | кулачок распредвала | 凸轮瓣 | 0 | — | — | — |
| 18 | `camchain@engine` | camchain | цепь ГРМ | 正时链条 | 1 | — | — | — |
| 19 | `camshaft@engine` | camshaft | распределительный вал | 凸轮轴 | 7 | — | — | — |
| 20 | `camshaft_bearing_journal@engine` | camshaft bearing journal | опорная шейка распредвала | 凸轮轴轴颈 | 0 | — | — | — |
| 21 | `camshaft_drive@engine` | camshaft drive | привод распределительного вала | 凸轮轴传动机构 | 0 | — | — | — |
| 22 | `camshaft_position_sensor@engine` | camshaft position sensor (CMP) | датчик положения распредвала (ДПРВ) | 凸轮轴位置传感器 (CMP) | 0 | — | — | — |
| 23 | `camshaft_seal@engine` | camshaft seal | сальник распредвала | 凸轮轴密封件 | 0 | — | — | — |
| 24 | `camshaft_timing_sprocket@engine` | camshaft timing sprocket | шестерня распредвала (ГРМ) | 凸轮轴正时链轮 | 0 | — | — | — |
| 25 | `carburetor_venturi@engine` | carburetor venturi | диффузор карбюратора | 化油器文丘里管 | 0 | — | — | — |
| 26 | `carburettor@engine` | carburettor / carburetor | карбюратор | 化油器 | 0 | — | — | — |
| 27 | `catalytic_converter@engine` | catalytic converter | каталитический нейтрализатор (катализатор) | 催化转化器 | 0 | — | — | — |
| 28 | `catalytic_converter_ann@engine` | catalytic converter | каталитический нейтрализатор | 催化转化器 | 4 | — | — | — |
| 29 | `center_electrode@engine` | center electrode | центральный электрод свечи | 中心电极 | 0 | — | — | — |
| 30 | `centrifugal_supercharger@engine` | centrifugal supercharger | центробежный нагнетатель | 离心式机械增压器 | 0 | — | — | — |
| 31 | `chain_guide@engine` | chain guide / chain damper | успокоитель цепи | 链条导板／链条减振器 | 0 | — | — | — |
| 32 | `charcoal_canister@engine` | charcoal canister / EVAP canister | адсорбер паров топлива / угольный адсорбер | 活性炭罐／蒸发排放控制罐 | 0 | — | — | — |
| 33 | `choke@engine` | choke | воздушная заслонка | 阻风门 | 0 | — | — | — |
| 34 | `coilpercylinder@engine` | coil-per-cylinder / coil pack | индивидуальная катушка зажигания / модуль катушек зажигания | 单缸独立点火线圈／线圈组 | 0 | — | — | — |
| 35 | `combustion_chamber@engine` | combustion chamber | камера сгорания | 燃烧室 | 0 | — | — | — |
| 36 | `common_rail_injector@engine` | common rail injector | топливная форсунка Common Rail | 共轨喷油器 | 0 | — | — | — |
| 37 | `compression_ring@engine` | compression ring | компрессионное кольцо | 压缩环 | 0 | — | — | — |
| 38 | `compressor_housing@engine` | compressor housing / compressor scroll | корпус компрессора турбины | 压气机蜗壳 | 0 | — | — | — |
| 39 | `compressor_wheel@engine` | compressor wheel / compressor impeller | крыльчатка компрессора | 压气机叶轮 | 0 | — | — | — |
| 40 | `connecting_rod_bearing@engine` | connecting rod bearing | шатунный подшипник | 连杆轴承 | 1 | — | — | — |
| 41 | `connecting_rod_bearing_shell@engine` | connecting rod bearing shell | вкладыш шатунного подшипника | 连杆轴瓦 | 0 | — | — | — |
| 42 | `connecting_rod_bolt@engine` | connecting rod bolt | болт шатуна | 连杆螺栓 | 1 | — | — | — |
| 43 | `connecting_rod_cap@engine` | connecting rod cap / big end cap | крышка шатуна | 连杆盖 / 大端盖 | 0 | — | — | — |
| 44 | `conrod@engine` | con-rod (connecting rod) | шатун | 连杆 | 6 | — | — | — |
| 45 | `contact_breaker@engine` | contact breaker / points | прерыватель | 断电器 | 0 | — | — | — |
| 46 | `coolant_expansion_tank@engine` | coolant expansion tank / overflow reservoir | расширительный бачок охлаждающей жидкости | 膨胀水箱 | 0 | — | — | — |
| 47 | `coolant_pump@engine` | coolant pump | водяной насос (помпа) | 冷却液泵 | 0 | — | — | — |
| 48 | `coolant_temperature_sensor@engine` | coolant temperature sensor (ECT) | датчик температуры охлаждающей жидкости (ДТОЖ) | 冷却液温度传感器 (ECT) | 0 | — | — | — |
| 49 | `crankcase@engine` | crankcase | картер двигателя | 曲轴箱 | 0 | — | — | — |
| 50 | `crankcase_breather@engine` | crankcase breather / breather valve | сапун картера | 曲轴箱通气管 | 0 | — | — | — |
| 51 | `crankcase_ventilation_system@engine` | crankcase ventilation system | система вентиляции картера | 曲轴箱通风系统 | 0 | — | — | — |
| 52 | `crankpin@engine` | crankpin / rod journal | шатунная шейка | 曲轴销 / 连杆轴颈 | 0 | — | — | — |
| 53 | `crankshaft@engine` | crankshaft | коленчатый вал | 曲轴 | 5 | — | — | — |
| 54 | `crankshaft_counterweight@engine` | crankshaft counterweight | противовес коленвала | 曲轴平衡重 | 0 | — | — | — |
| 55 | `crankshaft_journal@engine` | crankshaft journal | шейка коленвала | 曲轴轴颈 | 0 | — | — | — |
| 56 | `crankshaft_position_sensor@engine` | crankshaft position sensor (CKP) | датчик положения коленвала (ДПКВ) | 曲轴位置传感器 (CKP) | 0 | — | — | — |
| 57 | `crankshaft_pulley@engine` | crankshaft pulley | шкив коленвала | 曲轴皮带轮 | 2 | — | — | — |
| 58 | `crankshaft_seal@engine` | crankshaft seal | сальник коленвала | 曲轴油封 | 0 | — | — | — |
| 59 | `crankshaft_thrust_bearing@engine` | crankshaft thrust bearing | упорный подшипник коленвала | 曲轴止推轴承 | 0 | — | — | — |
| 60 | `crankshaft_timing_sprocket@engine` | crankshaft timing sprocket | шестерня коленвала (ГРМ) | 曲轴正时链轮 | 0 | — | — | — |
| 61 | `crankshaft_web@engine` | crankshaft web / crank web | щека коленвала | 曲轴臂 / 曲柄臂 | 0 | — | — | — |
| 62 | `cylinder_block@engine` | cylinder block | блок цилиндров | 气缸体 | 6 | — | — | — |
| 63 | `cylinder_head@engine` | cylinder head | головка блока цилиндров (ГБЦ) | 气缸盖 | 6 | — | — | — |
| 64 | `cylinder_liner@engine` | cylinder liner | гильза цилиндра | 缸套 | 0 | — | — | — |
| 65 | `def_injector@engine` | DEF injector / urea injector | инжектор AdBlue (SCR) | 尿素喷射器 / AdBlue喷射器 | 0 | — | — | — |
| 66 | `def_level_sensor@engine` | DEF level sensor | датчик уровня AdBlue | 尿素液位传感器 | 0 | — | — | — |
| 67 | `def_pump@engine` | DEF pump / AdBlue dosing pump | насос AdBlue | 尿素泵 / AdBlue计量泵 | 0 | — | — | — |
| 68 | `def_tank@engine` | DEF tank / AdBlue tank | бак AdBlue | 尿素箱 / AdBlue储液箱 | 0 | — | — | — |
| 69 | `diesel_engine@engine` | diesel engine | дизельный двигатель | 柴油发动机 | 0 | — | — | — |
| 70 | `diesel_particulate_filter@engine` | diesel particulate filter (DPF) | сажевый фильтр (DPF) | 柴油颗粒过滤器 (DPF) | 0 | — | — | — |
| 71 | `direct_injection_injector@engine` | direct injection injector / GDI injector | форсунка прямого впрыска | 直喷喷油器 / GDI喷油器 | 0 | — | — | — |
| 72 | `distributor@engine` | distributor | трамблёр / распределитель зажигания | 分电器 | 1 | — | — | — |
| 73 | `distributor_cap@engine` | distributor cap | крышка трамблёра | 分电器盖 | 0 | — | — | — |
| 74 | `distributor_coil@engine` | distributor coil / barrel coil | катушка зажигания (для распределителя) / цилиндрическая катушка зажигания | 分电器线圈 / 筒形线圈 | 0 | — | — | — |
| 75 | `distributor_rotor@engine` | distributor rotor | бегунок трамблёра | 分电器转子 | 0 | — | — | — |
| 76 | `downpipe@engine` | downpipe / front pipe | приёмная труба / даунпайп | 排气前管 / 头段排气管 | 0 | — | — | — |
| 77 | `downstream_o2_sensor@engine` | downstream O2 sensor / post-cat lambda | лямбда-зонд после катализатора | 催化器后氧传感器 | 0 | — | — | — |
| 78 | `dpf_ash_loading@engine` | DPF ash loading | зольность DPF | DPF灰分负载 | 0 | — | — | — |
| 79 | `dpf_clogging@engine` | DPF clogging / soot loading | засорение DPF | DPF堵塞 / 碳烟负载 | 0 | — | — | — |
| 80 | `dpf_pressure_sensor@engine` | DPF pressure sensor / DPF differential pressure sensor | датчик давления DPF | DPF压力传感器 / DPF差压传感器 | 0 | — | — | — |
| 81 | `drain_plug@engine` | drain plug / sump plug | пробка сливного отверстия картера | 放油螺塞 | 0 | — | — | — |
| 82 | `drain_plug_gasket@engine` | drain plug gasket / sump plug washer | прокладка сливной пробки | 放油螺塞垫片 / 油底壳螺塞垫圈 | 0 | — | — | — |
| 83 | `dry_sump@engine` | dry sump | сухой картер | 干式油底壳 | 0 | — | — | — |
| 84 | `dual_mass_flywheel@engine` | dual mass flywheel (DMF) | двухмассовый маховик (ДМФ) | 双质量飞轮 | 0 | — | — | — |
| 85 | `egr@engine` | EGR (exhaust gas recirculation) | рециркуляция отработавших газов | 废气再循环 | 0 | — | — | — |
| 86 | `egr_cooler@engine` | EGR cooler | охладитель EGR | EGR冷却器 | 0 | — | — | — |
| 87 | `egr_differential_pressure_sensor@engine` | EGR differential pressure sensor | датчик перепада давления EGR | EGR差压传感器 | 0 | — | — | — |
| 88 | `egr_valve@engine` | EGR valve (Exhaust Gas Recirculation valve) | клапан EGR | 废气再循环阀（EGR阀） | 0 | — | — | — |
| 89 | `electric_cooling_fan@engine` | electric cooling fan | электровентилятор охлаждения | 电动冷却风扇 | 0 | — | — | — |
| 90 | `electric_fuel_pump@engine` | electric fuel pump / in-tank fuel pump | электрический топливный насос | 电动燃油泵 / 箱内燃油泵 | 0 | — | — | — |
| 91 | `electronic_thermostat@engine` | electronic thermostat / map-controlled thermostat | электронный термостат | 电子节温器 / 电控节温器 | 0 | — | — | — |
| 92 | `engine@engine` | engine | двигатель | 发动机 | 64 | 1 | — | P0171, P0300, P0A0F |
| 93 | `engine_assembly@engine` | engine assembly | двигатель в сборе | 发动机总成 | 2 | — | — | — |
| 94 | `engine_mount@engine` | engine mount / motor mount / engine torque strut | кронштейн / подушка двигателя | 发动机支架 | 0 | 1 | 1 | P0171, P0300 |
| 95 | `evap_purge_valve@engine` | EVAP purge valve | клапан продувки адсорбера | 碳罐清洗阀 | 0 | — | — | — |
| 96 | `evap_vent_valve@engine` | EVAP vent valve / canister vent solenoid | клапан вентиляции системы EVAP / электромагнитный клапан вентиляции адсорбера | 蒸发排放通气阀 / 碳罐通气电磁阀 | 0 | — | — | — |
| 97 | `evaporative_emission_control_system@engine` | evaporative emission control system | система рекуперации паров топлива | 蒸发排放控制系统 | 0 | — | — | — |
| 98 | `exhaust_clamp@engine` | exhaust clamp / U-bolt clamp | хомут выхлопной системы | 排气管卡箍 / U形螺栓卡箍 | 0 | — | — | — |
| 99 | `exhaust_cutout_valve@engine` | exhaust cutout valve / exhaust flap | клапан отсечки выхлопа / заслонка выхлопной системы | 排气截止阀 / 排气蝶阀 | 0 | — | — | — |
| 100 | `exhaust_gas_recirculation_system@engine` | exhaust gas recirculation system | система рециркуляции отработавших газов | 废气再循环系统 | 0 | — | — | — |
| 101 | `exhaust_gas_temperature_sensor@engine` | exhaust gas temperature sensor (EGT) | датчик температуры выхлопных газов (EGT) | 排气温度传感器 | 0 | — | — | — |
| 102 | `exhaust_gasket@engine` | exhaust gasket / donut gasket | прокладка выхлопная | 排气管垫片 / 环形垫片 | 0 | — | — | — |
| 103 | `exhaust_hanger@engine` | exhaust hanger / rubber exhaust mount | подвеска выхлопной системы | 排气管吊架 / 橡胶排气支架 | 0 | — | — | — |
| 104 | `exhaust_manifold@engine` | exhaust manifold | выпускной коллектор | 排气歧管 | 2 | 1 | — | P0420, P0430 |
| 105 | `exhaust_manifold_gasket@engine` | exhaust manifold gasket | прокладка выпускного коллектора | 排气歧管垫片 | 0 | — | — | — |
| 106 | `exhaust_manifold_stud@engine` | exhaust manifold stud | шпилька выпускного коллектора | 排气歧管螺柱 | 0 | — | — | — |
| 107 | `exhaust_manifold_stud_nut@engine` | exhaust manifold stud nut | гайка шпильки выпускного коллектора | 排气歧管螺柱螺母 | 0 | — | — | — |
| 108 | `exhaust_pipe@engine` | Exhaust | выхлопная труба | 排气 | 0 | — | — | — |
| 109 | `exhaust_pipe_tailpipe@engine` | exhaust pipe / tailpipe | выхлопная труба | 排气管/尾管 | 0 | 1 | — | P0420, P0430 |
| 110 | `exhaust_system@engine` | Exhaust | выхлопная система | 排气 | 2 | 1 | 3 | P0420, P0430 |
| 111 | `exhaust_tip@engine` | exhaust tip | насадка глушителя | 排气管尾嘴 | 0 | — | — | — |
| 112 | `exhaust_valve@engine` | exhaust valve | выпускной клапан | 排气门 | 1 | — | — | — |
| 113 | `expansion_tank@engine` | coolant expansion tank | расширительный бачок | 冷却液膨胀罐 | 0 | — | — | — |
| 114 | `expansion_tank_cap@engine` | expansion tank cap | крышка расширительного бачка | 膨胀箱盖 | 0 | — | — | — |
| 115 | `external_wastegate@engine` | external wastegate | внешний вестгейт | 外置废气旁通阀 | 0 | — | — | — |
| 116 | `fan_switch@engine` | fan switch / coolant temperature switch | датчик включения вентилятора | 风扇开关／冷却液温度开关 | 0 | — | — | — |
| 117 | `flat_engine@engine` | flat engine / boxer engine / horizontally opposed engine | оппозитный двигатель / боксёр | 水平对置发动机 / 对置发动机 | 0 | — | — | — |
| 118 | `flex_pipe@engine` | flex pipe / exhaust flex joint | гофра выхлопной трубы | 排气软连接 | 0 | — | — | — |
| 119 | `float@engine` | float | поплавок карбюратора | 浮子 | 0 | — | — | — |
| 120 | `float_chamber@engine` | float chamber | поплавковая камера | 浮子室 | 0 | — | — | — |
| 121 | `flywheel@engine` | flywheel | маховик | 飞轮 | 1 | — | — | — |
| 122 | `front_crankshaft_seal@engine` | front crankshaft seal | сальник коленвала передний | 前曲轴密封件 | 0 | — | — | — |
| 123 | `front_exhaust_tip@engine` | front exhaust tip | насадка глушителя (перед.) | 前排气管尾嘴 | 0 | — | — | — |
| 124 | `front_left_engine_mount@engine` | front left engine mount | опора двигателя (перед., лев.) | 前左发动机安装座 | 0 | — | — | — |
| 125 | `front_right_engine_mount@engine` | front right engine mount | опора двигателя (перед., прав.) | 前右发动机安装座 | 0 | — | — | — |
| 126 | `fuel_cap@engine` | fuel cap | крышка бензобака | 油箱盖 | 38 | — | — | — |
| 127 | `fuel_check_valve@engine` | fuel check valve / fuel return valve | обратный клапан топливной системы | 燃油单向阀 / 燃油回油阀 | 0 | — | — | — |
| 128 | `fuel_door@engine` | fuel door | лючок бензобака | 加油口盖 | 2 | — | — | — |
| 129 | `fuel_filler_cap@engine` | fuel filler cap / gas cap | крышка горловины топливного бака | 油箱盖 / 加油口盖 | 0 | 2 | — | P0171, P0300 |
| 130 | `fuel_filler_neck@engine` | fuel filler neck | заливная горловина | 加油口颈管 | 0 | — | — | — |
| 131 | `fuel_filter@engine` | fuel filter | топливный фильтр | 燃油滤清器 | 14 | — | — | — |
| 132 | `fuel_injector@engine` | fuel injector | форсунка / топливная форсунка | 喷油器 | 1 | — | — | — |
| 133 | `fuel_injector_array@engine` | fuel injectors | топливные форсунки | 燃油喷射器 | 0 | — | — | — |
| 134 | `fuel_level_sensor@engine` | fuel level sensor / fuel gauge sender | датчик уровня топлива | 燃油液位传感器 / 油量表发送器 | 0 | — | — | — |
| 135 | `fuel_line@engine` | fuel line | топливопровод | 燃油管路 | 1 | — | — | — |
| 136 | `fuel_pressure_regulator@engine` | fuel pressure regulator | регулятор давления топлива | 燃油压力调节器 | 0 | — | — | — |
| 137 | `fuel_pump@engine` | fuel pump | топливный насос | 燃油泵 | 1 | — | — | — |
| 138 | `fuel_pump_module@engine` | fuel pump module | модуль топливного насоса | 燃油泵模块 | 0 | — | — | — |
| 139 | `fuel_pump_relay@engine` | fuel pump relay | реле топливного насоса | 燃油泵继电器 | 0 | — | — | — |
| 140 | `fuel_pump_strainer@engine` | fuel pump strainer / sock filter | сетчатый фильтр топливного насоса | 燃油泵滤网 / 袜式滤清器 | 0 | — | — | — |
| 141 | `fuel_rail@engine` | fuel rail / fuel manifold | топливная рейка | 燃油分配管 | 0 | — | — | — |
| 142 | `fuel_strainer@engine` | fuel strainer | сетка топливного фильтра | 燃油滤网 | 0 | — | — | — |
| 143 | `fuel_system@engine` | fuel system | топливная система | 燃油系统 | 20 | — | — | — |
| 144 | `fuel_tank@engine` | fuel tank | топливный бак | 油箱 | 9 | 1 | 1 | P0171, P0300 |
| 145 | `fuel_tank_pressure_sensor@engine` | fuel tank pressure sensor | датчик давления паров топлива | 燃油箱压力传感器 | 0 | — | — | — |
| 146 | `gasket@engine` | gasket | прокладка | 垫片 | 7 | — | — | — |
| 147 | `gearbox@engine` | gearbox | коробка передач | 变速箱 | 1 | — | — | — |
| 148 | `geartype_oil_pump@engine` | gear-type oil pump | шестерёнчатый масляный насос | 齿轮式机油泵 | 0 | — | — | — |
| 149 | `glow_plug@engine` | glow plug / heater plug | свеча накаливания (дизель) | 预热塞 | 0 | — | — | — |
| 150 | `glow_plug_control_unit@engine` | glow plug control unit | блок управления свечами накаливания | 预热塞控制单元 | 0 | — | — | — |
| 151 | `glow_plug_relay@engine` | glow plug relay / glow plug control module | реле свечей накаливания | 预热塞继电器 / 预热塞控制模块 | 0 | — | — | — |
| 152 | `ground_electrode@engine` | ground electrode / side electrode | боковой электрод свечи | 接地电极 / 侧电极 | 0 | — | — | — |
| 153 | `harmonic_balancer@engine` | harmonic balancer / crankshaft damper / torsional damper | демпфер крутильных колебаний | 曲轴减振器 / 扭转减振器 | 0 | — | — | — |
| 154 | `head_bolt@engine` | head bolt / cylinder head bolt | болт ГБЦ | 缸盖螺栓／气缸盖螺栓 | 0 | — | — | — |
| 155 | `head_gasket@engine` | head gasket | прокладка ГБЦ | 气缸垫 | 1 | — | — | — |
| 156 | `heater_hose@engine` | heater hose | патрубок отопителя | 暖风软管 | 0 | — | — | — |
| 157 | `heater_valve@engine` | heater valve | клапан печки | 暖风水阀 | 0 | — | — | — |
| 158 | `high_pressure_fuel_pump@engine` | high pressure fuel pump (HPFP) | топливный насос высокого давления (ТНВД) | 高压燃油泵 | 0 | — | — | — |
| 159 | `hotfilm_maf_sensor@engine` | hot-film MAF sensor | пленочный расходомер воздуха | 热膜式空气流量传感器 | 0 | — | — | — |
| 160 | `hpfp@engine` | high-pressure fuel pump (HPFP) | топливный насос высокого давления (ТНВД) | 高压燃油泵 | 0 | — | — | — |
| 161 | `hybrid_powertrain@engine` | hybrid powertrain | гибридная силовая установка | 混合动力总成 | 0 | — | — | — |
| 162 | `hydraulic_lifter@engine` | hydraulic lifter / hydraulic tappet | гидрокомпенсатор | 液压挺柱 | 0 | — | — | — |
| 163 | `hydraulic_valve_lifter@engine` | hydraulic valve lifter / hydraulic tappet / HLA | гидрокомпенсатор зазора клапана | 液压挺柱 | 1 | — | — | — |
| 164 | `idle_air_control_valve@engine` | idle air control valve (IAC) | клапан холостого хода (IAC) | 怠速控制阀 | 0 | — | — | — |
| 165 | `idle_jet@engine` | idle jet / pilot jet | жиклёр холостого хода | 怠速量孔 / 慢车量孔 | 0 | — | — | — |
| 166 | `ignition_coil@engine` | ignition coil | катушка зажигания | 点火线圈 | 0 | — | — | — |
| 167 | `ignition_coil_array@engine` | ignition coils | катушки зажигания | 点火线圈 | 1 | — | — | — |
| 168 | `ignition_condenser@engine` | ignition condenser / capacitor | конденсатор системы зажигания | 点火电容器 | 0 | — | — | — |
| 169 | `ignition_control_module@engine` | ignition control module | блок управления зажиганием | 点火控制模块 | 0 | — | — | — |
| 170 | `ignition_module@engine` | ignition module | модуль зажигания | 点火模块 | 0 | — | — | — |
| 171 | `ignition_system@engine` | ignition system | система зажигания | 点火系统 | 0 | — | — | — |
| 172 | `ignition_wire@engine` | ignition wire / spark plug wire | высоковольтный провод | 高压线 | 39 | — | — | — |
| 173 | `indikatory_priborov@engine` | Instrument Indicators — Fuel Indicator | Индикаторы приборов#2 — Инд. топливо | 仪表指示器 — 燃油指示 | 0 | — | — | — |
| 174 | `indikatory_priborov_2@engine` | Instrument Indicators — Oil Indicator | Индикаторы приборов 2#2 — Инд. масло | 仪表指示器 — 机油指示 | 0 | — | — | — |
| 175 | `injection_timing@engine` | injection timing / injection advance | угол опережения впрыска | 喷射正时 / 喷射提前角 | 0 | — | — | — |
| 176 | `inline_engine@engine` | inline engine / straight engine | рядный двигатель | 直列式发动机 | 0 | — | — | — |
| 177 | `instrument_cluster@engine` | instrument cluster | щиток приборов | 组合仪表 | 0 | 2 | — | B1450, B1460 |
| 178 | `intake_air_temperature_sensor@engine` | intake air temperature sensor (IAT) | датчик температуры воздуха (IAT) | 进气温度传感器（IAT） | 0 | — | — | — |
| 179 | `intake_manifold@engine` | intake manifold | впускной коллектор | 进气歧管 | 3 | 1 | — | P0171 |
| 180 | `intake_valve@engine` | intake valve / inlet valve | впускной клапан | 进气门 | 1 | — | — | — |
| 181 | `intercooler@engine` | intercooler / charge air cooler | интеркулер / промежуточный охладитель наддувочного воздуха | 中冷器 | 0 | — | — | — |
| 182 | `intercooler_ann@engine` | intercooler | интеркулер | 中冷器 | 2 | — | — | — |
| 183 | `internal_combustion_engine@engine` | internal combustion engine (ICE) | двигатель внутреннего сгорания (ДВС) | 内燃机 | 0 | — | — | — |
| 184 | `internal_wastegate@engine` | internal wastegate | внутренний вестгейт | 内置废气旁通阀 | 0 | — | — | — |
| 185 | `iridium_spark_plug@engine` | iridium spark plug | свеча зажигания с иридиевым электродом | 铱金火花塞 | 0 | — | — | — |
| 186 | `jet@engine` | jet (carburettor) | жиклёр | 量孔（化油器） | 0 | — | — | — |
| 187 | `knock_sensor@engine` | knock sensor | датчик детонации | 爆震传感器 | 1 | — | — | — |
| 188 | `kreplenie_emotora@engine` | E-Motor Mount | Крепление э/мотора | 电机支架 | 0 | — | — | — |
| 189 | `lambda_excess_air_coefficient@engine` | lambda (λ) — excess air coefficient | лямбда (λ) | 空气过量系数（λ） | 0 | — | — | — |
| 190 | `lambda_sensor@engine` | lambda sensor | лямбда-зонд | 氧传感器 | 2 | — | — | — |
| 191 | `liquid_cooling_system@engine` | liquid cooling system / water-cooled system | жидкостная система охлаждения | 液冷系统 / 水冷系统 | 0 | — | — | — |
| 192 | `low_pressure_fuel_pump@engine` | low pressure fuel pump / lift pump | топливный насос низкого давления / подкачивающий насос | 低压燃油泵 / 输油泵 | 0 | — | — | — |
| 193 | `lubrication_system@engine` | lubrication system | система смазки | 润滑系统 | 0 | — | — | — |
| 194 | `lysholm_screw_supercharger@engine` | Lysholm screw supercharger / twin-vortex supercharger | нагнетатель Лысхольм / TVS | 螺杆式机械增压器（利斯霍姆） | 0 | — | — | — |
| 195 | `lyuchok_baka@engine` | Fuel Door R — Panel | Лючок бака#2 — Панель | 油箱盖右 — 面板 | 0 | — | — | — |
| 196 | `maf_sensor@engine` | MAF sensor (mass air flow) | датчик массового расхода воздуха (ДМРВ) | 空气流量传感器 (MAF) | 0 | — | — | — |
| 197 | `maf_sensor_ann@engine` | mass airflow sensor (MAF) | датчик массового расхода воздуха (MAF) | 空气质量流量传感器 | 0 | — | — | — |
| 198 | `main_bearing@engine` | main bearing | коренной подшипник | 主轴承 | 5 | — | — | — |
| 199 | `main_bearing_shell@engine` | main bearing shell / main bearing insert | вкладыш коренного подшипника | 主轴承瓦 | 0 | — | — | — |
| 200 | `main_jet@engine` | main jet | главный жиклёр | 主量孔 | 0 | — | — | — |
| 201 | `main_journal@engine` | main journal / main bearing journal | коренная шейка | 曲轴主轴颈 | 0 | — | — | — |
| 202 | `manifold_absolute_pressure_sensor@engine` | manifold absolute pressure sensor | датчик давления во впускном коллекторе | 进气歧管绝对压力传感器（MAP） | 0 | — | — | — |
| 203 | `map_sensor@engine` | MAP sensor (manifold absolute pressure) | датчик абсолютного давления (ДАД) | 进气歧管绝对压力传感器 (MAP) | 0 | — | — | — |
| 204 | `muffler@engine` | muffler / silencer | глушитель | 消声器 | 2 | — | — | — |
| 205 | `naturally_aspirated_engine@engine` | naturally aspirated engine | атмосферный двигатель | 自然吸气发动机 | 0 | — | — | — |
| 206 | `needle_valve@engine` | needle valve | игольчатый клапан карбюратора | 针阀 | 0 | — | — | — |
| 207 | `o2_sensor_downstream@engine` | O₂ sensor (downstream) | датчик кислорода (нижний) | 下游氧传感器 | 0 | — | — | — |
| 208 | `o2_sensor_upstream@engine` | O₂ sensor (upstream) | датчик кислорода (верхний) | 上游氧传感器 | 0 | — | — | — |
| 209 | `oil_control_ring@engine` | oil control ring | маслосъёмное кольцо | 油环 | 0 | — | — | — |
| 210 | `oil_cooler@engine` | oil cooler | масляный радиатор | 机油冷却器 | 0 | — | — | — |
| 211 | `oil_dipstick@engine` | oil dipstick | щуп уровня масла | 机油尺 | 1 | — | — | — |
| 212 | `oil_filler_cap@engine` | oil filler cap | крышка маслозаливной горловины | 机油加注口盖 | 0 | — | — | — |
| 213 | `oil_filler_neck@engine` | oil filler neck | маслозаливная горловина | 机油加注口管 | 0 | — | — | — |
| 214 | `oil_filter@engine` | oil filter | масляный фильтр | 机油滤清器 | 0 | — | — | — |
| 215 | `oil_filter_ann@engine` | oil filter | масляный фильтр | 机油滤清器 | 15 | — | — | — |
| 216 | `oil_filter_bypass_valve@engine` | oil filter bypass valve | перепускной клапан масляного фильтра | 机油滤清器旁通阀 | 0 | — | — | — |
| 217 | `oil_filter_element@engine` | oil filter element / filter cartridge | сменный элемент масляного фильтра | 机油滤芯 | 0 | — | — | — |
| 218 | `oil_gallery@engine` | oil gallery / oil passage | масляный канал | 油道 | 2 | — | — | — |
| 219 | `oil_level_sensor@engine` | oil level sensor | датчик уровня масла | 机油液位传感器 | 0 | — | — | — |
| 220 | `oil_pan@engine` | oil pan / sump | масляный поддон / картер | 油底壳 | 0 | — | — | — |
| 221 | `oil_pickup_tube@engine` | oil pickup tube / oil strainer | маслоприёмник | 机油吸油管 / 机油集滤器 | 0 | — | — | — |
| 222 | `oil_pressure_relief_valve@engine` | oil pressure relief valve | редукционный клапан масляного насоса | 机油限压阀 | 0 | — | — | — |
| 223 | `oil_pressure_sensor@engine` | oil pressure sensor | датчик давления масла | 机油压力传感器 | 34 | — | — | — |
| 224 | `oil_pump@engine` | oil pump | масляный насос | 油泵 | 4 | — | — | — |
| 225 | `oil_seal@engine` | oil seal | сальник | 油封 | 4 | — | — | — |
| 226 | `oil_separator@engine` | oil separator / oil catch can | маслоотделитель | 油气分离器 | 0 | — | — | — |
| 227 | `oiltowater_heat_exchanger@engine` | oil-to-water heat exchanger / oil cooler | охладитель масла (теплообменник) | 油水热交换器 / 机油冷却器 | 0 | — | — | — |
| 228 | `oxygen_sensor@engine` | oxygen sensor / lambda sensor | кислородный датчик / лямбда-зонд | 氧传感器 / λ传感器 | 0 | — | — | — |
| 229 | `pcv_valve@engine` | PCV valve | клапан вентиляции картерных газов | 曲轴箱强制通风阀（PCV阀） | 0 | — | — | — |
| 230 | `performance_air_filter@engine` | performance air filter / pod filter | спортивный воздушный фильтр / фильтр нулевого сопротивления | 高性能空气滤清器 / 蘑菇头滤清器 | 0 | — | — | — |
| 231 | `petrol_engine@engine` | petrol engine / gasoline engine | бензиновый двигатель | 汽油发动机 | 0 | — | — | — |
| 232 | `piezo_injector@engine` | piezo injector | пьезоэлектрическая форсунка | 压电式喷油器 | 0 | — | — | — |
| 233 | `piston@engine` | piston | поршень | 活塞 | 2 | — | — | — |
| 234 | `piston_crown@engine` | piston crown / piston top | днище поршня | 活塞顶 | 0 | — | — | — |
| 235 | `piston_pin@engine` | piston pin / gudgeon pin | поршневой палец | 活塞销 | 5 | — | — | — |
| 236 | `piston_pin_circlip@engine` | piston pin circlip / wrist pin retainer | стопорное кольцо поршневого пальца | 活塞销卡簧 | 0 | — | — | — |
| 237 | `piston_ring@engine` | piston ring | поршневое кольцо | 活塞环 | 6 | — | — | — |
| 238 | `piston_skirt@engine` | piston skirt | юбка поршня | 活塞裙部 | 0 | — | — | — |
| 239 | `platinum_spark_plug@engine` | platinum spark plug | свеча зажигания с платиновым электродом | 铂金火花塞 | 0 | — | — | — |
| 240 | `port_injector@engine` | port injector / MPI injector | форсунка MPI | 进气道喷油器（MPI） | 0 | — | — | — |
| 241 | `preheating_system@engine` | pre-heating system (diesel) | система предпускового подогрева (дизель) | 预热系统（柴油） | 0 | — | — | — |
| 242 | `pushrod@engine` | pushrod | штанга толкателя | 推杆 | 0 | — | — | — |
| 243 | `radiator@engine` | radiator / engine radiator | радиатор системы охлаждения | 散热器 | 11 | — | — | — |
| 244 | `radiator_core@engine` | radiator core | сердцевина радиатора | 散热器芯体 | 0 | — | — | — |
| 245 | `radiator_fan@engine` | radiator fan / cooling fan | вентилятор охлаждения радиатора | 散热器风扇 | 0 | — | — | — |
| 246 | `radiator_shroud@engine` | radiator shroud / fan shroud | диффузор радиатора | 散热器导风罩 | 0 | — | — | — |
| 247 | `rail_pressure_control_valve@engine` | rail pressure control valve / metering unit | регулятор давления Common Rail | 共轨压力控制阀 / 计量单元 | 0 | — | — | — |
| 248 | `range_extender@engine` | range extender | увеличитель запаса хода | 增程器 | 1 | — | 1 | P0171, P0300, P0A0F |
| 249 | `rear_cover_plate@engine` | rear cover plate | задняя крышка двигателя | 后盖板 | 0 | — | — | — |
| 250 | `rear_exhaust_tip@engine` | rear exhaust tip | насадка глушителя (зад.) | 后部排气管尾喉 | 0 | — | — | — |
| 251 | `rear_left_engine_mount@engine` | rear left engine mount | опора двигателя (зад., лев.) | 后左发动机安装座 | 0 | — | — | — |
| 252 | `rear_main_seal@engine` | rear main seal / rear crankshaft seal | сальник коленвала задний | 曲轴后油封 | 0 | — | — | — |
| 253 | `rear_muffler@engine` | rear muffler / main muffler | задний глушитель | 后消声器 | 0 | — | — | — |
| 254 | `rear_right_engine_mount@engine` | rear right engine mount | опора двигателя (зад., прав.) | 后右发动机安装座 | 0 | — | — | — |
| 255 | `reed_valve@engine` | reed valve | лепестковый клапан | 簧片阀 | 0 | — | — | — |
| 256 | `reluctor_wheel@engine` | reluctor wheel / trigger wheel | задающий диск / реперный диск | 曲轴信号盘 / 触发齿盘 | 0 | — | — | — |
| 257 | `resonator@engine` | resonator / front muffler / pre-muffler | передний глушитель / резонатор | 共鸣器 / 前消声器 | 0 | — | — | — |
| 258 | `ring_gear@engine` | ring gear / flywheel ring gear | зубчатый венец маховика | 齿圈／飞轮齿圈 | 0 | — | — | — |
| 259 | `rocker_arm@engine` | rocker arm | коромысло | 摇臂 | 2 | — | — | — |
| 260 | `rocker_shaft@engine` | rocker shaft | ось коромысла | 摇臂轴 | 0 | — | — | — |
| 261 | `roots_supercharger@engine` | Roots supercharger | нагнетатель Рутс | 鲁特式机械增压器 | 0 | — | — | — |
| 262 | `rotary_engine@engine` | rotary engine / Wankel engine | роторный двигатель Ванкеля | 转子发动机（旺克尔发动机） | 0 | — | — | — |
| 263 | `rotortype_oil_pump@engine` | rotor-type oil pump / gerotor pump | роторный масляный насос | 转子式机油泵（次摆线泵） | 0 | — | — | — |
| 264 | `scr@engine` | SCR (selective catalytic reduction) | система SCR (селективная каталитическая нейтрализация) | 选择性催化还原 (SCR) | 0 | — | — | — |
| 265 | `solenoid_injector@engine` | solenoid injector | электромагнитная форсунка | 电磁式喷油器 | 0 | — | — | — |
| 266 | `spark_plug@engine` | spark plug | свеча зажигания | 火花塞 | 0 | — | — | — |
| 267 | `spark_plug_array@engine` | spark plugs | свечи зажигания | 火花塞 | 32 | — | — | — |
| 268 | `spark_plug_boot@engine` | spark plug boot / plug cap | свечной наконечник / колпачок свечи | 火花塞护套 / 火花塞帽 | 0 | — | — | — |
| 269 | `spark_plug_electrode@engine` | spark plug electrode | электрод свечи зажигания | 火花塞电极 | 0 | — | — | — |
| 270 | `spark_plug_thread@engine` | spark plug thread | резьба свечи зажигания | 火花塞螺纹 | 0 | — | — | — |
| 271 | `stoichiometric_airfuel_ratio@engine` | stoichiometric air-fuel ratio (λ=1) | стехиометрическое соотношение (λ=1) | 化学计量空燃比（λ=1） | 0 | — | — | — |
| 272 | `sump@engine` | sump | поддон картера | 油底壳 | 1 | — | — | — |
| 273 | `supercharger@engine` | supercharger | нагнетатель / компрессор | 机械增压器 | 0 | — | — | — |
| 274 | `tailpipe@engine` | tailpipe / exhaust tip | задняя выхлопная труба / насадок | 排气管尾管 / 尾喉 | 0 | — | — | — |
| 275 | `tappet@engine` | tappet | толкатель | 挺柱 | 2 | — | — | — |
| 276 | `thermostat_ann@engine` | thermostat | термостат | 恒温器 | 0 | — | — | — |
| 277 | `thermostat_housing_gasket@engine` | thermostat housing gasket | прокладка корпуса термостата | 节温器壳体密封垫 | 0 | — | — | — |
| 278 | `thermostat_valve@engine` | thermostat valve | клапан термостата | 节温器阀 | 0 | — | — | — |
| 279 | `threeway_catalytic_converter@engine` | three-way catalytic converter | катализатор трёхкомпонентный (TWC) | 三元催化转化器 | 1 | — | — | — |
| 280 | `throttle_body@engine` | throttle body | дроссельная заслонка | 节气门 | 2 | — | 1 | P0121, P0122 |
| 281 | `throttle_plate@engine` | throttle plate / butterfly valve | заслонка дросселя | 节气门板 / 蝶形阀 | 0 | — | — | — |
| 282 | `throttle_position_sensor@engine` | throttle position sensor (TPS) | датчик положения дроссельной заслонки (ДПДЗ) | 节气门位置传感器 (TPS) | 0 | — | — | — |
| 283 | `thrust_washer@engine` | thrust washer / half moon washer | упорное полукольцо | 止推垫片 / 半月形垫片 | 0 | — | — | — |
| 284 | `timing_belt@engine` | timing belt / cam belt | ремень ГРМ | 正时皮带 / 凸轮皮带 | 0 | — | — | — |
| 285 | `timing_belt_tensioner@engine` | timing belt tensioner | натяжитель ремня ГРМ | 正时皮带张紧器 | 0 | — | — | — |
| 286 | `timing_chain_tensioner@engine` | timing chain tensioner | натяжитель цепи ГРМ | 正时链条张紧器 | 0 | — | — | — |
| 287 | `timing_cover@engine` | timing cover / front cover | передняя крышка двигателя | 正时盖 | 0 | — | — | — |
| 288 | `timing_tensioner@engine` | timing tensioner | натяжитель ГРМ | 正时张紧器 | 1 | — | — | — |
| 289 | `toothed_timing_belt@engine` | toothed timing belt | зубчатый ремень ГРМ | 齿形正时皮带 | 0 | — | — | — |
| 290 | `traction_motor@engine` | traction motor / electric drive motor | электродвигатель тяговый | 牵引电机 / 电动驱动电机 | 0 | — | — | — |
| 291 | `transmission@engine` | Transmission | Трансмиссия | Трансмиссия | 0 | — | — | — |
| 292 | `transmission_drivetrain_powertrain@engine` | transmission / drivetrain / powertrain | трансмиссия | 动力系统 | 71 | — | 1 | P0700, P0715 |
| 293 | `turbine_housing@engine` | turbine housing / turbine scroll | корпус турбины | 涡轮壳体 / 涡轮蜗壳 | 0 | — | — | — |
| 294 | `turbine_wheel@engine` | turbine wheel | турбинное колесо | 涡轮叶轮 | 0 | — | — | — |
| 295 | `turbo_oil_feed@engine` | turbo oil feed | подвод масла к турбине | 涡轮增压器供油 | 0 | — | — | — |
| 296 | `turbo_oil_feed_line@engine` | turbo oil feed line / turbo oil drain line | маслопровод турбины | 涡轮供油管 / 涡轮回油管 | 0 | — | — | — |
| 297 | `turbocharged_engine@engine` | turbocharged engine / turbo engine | турбированный двигатель | 涡轮增压发动机 | 0 | — | — | — |
| 298 | `turbocharger@engine` | turbocharger / turbo | турбокомпрессор | 涡轮增压器 | 0 | — | — | — |
| 299 | `turbocharger_ann@engine` | turbocharger | турбокомпрессор | 涡轮增压器 | 0 | — | — | — |
| 300 | `turbocharger_shaft@engine` | turbocharger shaft | вал турбокомпрессора | 涡轮增压器轴 | 0 | — | — | — |
| 301 | `upstream_o2_sensor@engine` | upstream O2 sensor / pre-cat lambda | лямбда-зонд до катализатора | 前氧传感器 / 催化器前氧传感器 | 0 | — | — | — |
| 302 | `valve_cover@engine` | valve cover / rocker cover / cam cover | крышка клапанов / клапанная крышка | 气门室盖 | 0 | — | — | — |
| 303 | `valve_guide@engine` | valve guide | направляющая клапана | 气门导管 | 0 | — | — | — |
| 304 | `valve_head@engine` | valve head / valve face | тарелка клапана | 气门头 / 气门密封面 | 0 | — | — | — |
| 305 | `valve_intake@engine` | valve (intake / exhaust) | клапан (впускной / выпускной) | 气门（进气/排气） | 0 | — | — | — |
| 306 | `valve_keeper@engine` | valve keeper / valve collet / split keeper | сухарь клапана | 气门锁夹 / 气门卡瓦 / 开口卡夹 | 0 | — | — | — |
| 307 | `valve_lifter@engine` | valve lifter / tappet | толкатель клапана | 气门挺柱 | 0 | — | — | — |
| 308 | `valve_seat@engine` | valve seat | седло клапана | 气门座 | 0 | — | — | — |
| 309 | `valve_spring@engine` | valve spring | пружина клапана | 气门弹簧 | 1 | — | — | — |
| 310 | `valve_spring_retainer@engine` | valve spring retainer / valve spring cap | опорная тарелка пружины клапана | 气门弹簧座 / 气门弹簧帽 | 0 | — | — | — |
| 311 | `valve_stem@engine` | valve stem | стержень клапана | 气门杆 | 0 | — | — | — |
| 312 | `valve_stem_seal@engine` | valve stem seal | маслосъёмный колпачок | 气门油封 | 1 | — | — | — |
| 313 | `valve_train@engine` | valve train / valve gear | газораспределительный механизм | 配气机构 / 气门传动组 | 0 | — | — | — |
| 314 | `variable_geometry_turbo@engine` | variable geometry turbo | турбина с изменяемой геометрией | 可变几何涡轮增压器 | 0 | — | — | — |
| 315 | `variable_valve_lift_system@engine` | variable valve lift system | система изменения хода клапана | 可变气门升程系统 | 0 | — | — | — |
| 316 | `variable_valve_timing_system@engine` | variable valve timing system | система изменения фаз газораспределения | 可变气门正时系统 | 0 | — | — | — |
| 317 | `vengine@engine` | V-engine | V-образный двигатель | V型发动机 | 0 | — | — | — |
| 318 | `vgt_vanes@engine` | VGT vanes / variable nozzle vanes | направляющие лопатки ВГТ | VGT导向叶片 / 可变喷嘴叶片 | 0 | — | — | — |
| 319 | `viscous_fan_clutch@engine` | viscous fan clutch / viscofan | вискомуфта вентилятора | 液力风扇离合器 / 粘性风扇离合器 | 0 | — | — | — |
| 320 | `vvt_actuator@engine` | VVT actuator (variable valve timing) | фазовращатель (VVT) | 可变气门正时执行器 (VVT) | 0 | — | — | — |
| 321 | `vykhlop_i4_15_benzin@engine` | Exhaust | Выхлоп I4 1.5 бензин | 排气 | 11 | — | — | — |
| 322 | `wastegate@engine` | wastegate | перепускной клапан турбины (вейстгейт) | 废气旁通阀 | 0 | — | — | — |
| 323 | `wastegate_actuator@engine` | wastegate actuator | актуатор вестгейта | 废气旁通阀执行器 | 0 | — | — | — |
| 324 | `water_pump@engine` | water pump / coolant pump | водяной насос / помпа | 水泵／冷却液泵 | 0 | — | — | — |
| 325 | `water_pump_bearing@engine` | water pump bearing | подшипник водяного насоса | 水泵轴承 | 0 | — | — | — |
| 326 | `water_pump_impeller@engine` | water pump impeller | крыльчатка водяного насоса | 水泵叶轮 | 0 | — | — | — |
| 327 | `water_pump_seal@engine` | water pump seal | сальник водяного насоса | 水泵密封件 | 0 | — | — | — |
| 328 | `wet_sump@engine` | wet sump | мокрый картер | 湿式油底壳 | 0 | — | — | — |
| 329 | `wideband_oxygen_sensor@engine` | wideband oxygen sensor / AFR sensor | широкополосный лямбда-зонд | 宽带氧传感器 | 0 | — | — | — |

## 3. DRIVETRAIN — Привод и подвеска (331 компонентов)

*КПП, сцепление, карданный вал, дифференциал, ШРУСы, рычаги подвески, пружины, амортизаторы, колёса, шины*

**Подсистемы:** transmission, clutch, driveshaft_axles, differential, suspension_front, suspension_rear, wheels_tires

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `abs_wheel_speed_sensor@drivetrain` | ABS wheel speed sensor | датчик ABS | ABS轮速传感器 | 0 | — | — | — |
| 2 | `active_suspension@drivetrain` | active suspension | активная подвеска | 主动悬架 | 0 | — | — | — |
| 3 | `adaptive_suspension@drivetrain` | adaptive suspension / semi-active suspension / CDC | адаптивная подвеска | 自适应悬架 / 半主动悬架 / CDC | 0 | — | — | — |
| 4 | `adhesive_wheel_weight@drivetrain` | adhesive wheel weight / stick-on weight | клеящийся балансировочный груз | 粘贴式平衡块 | 1 | — | — | — |
| 5 | `adjustable_shock_absorber@drivetrain` | adjustable shock absorber / adjustable damper | регулируемый амортизатор | 可调节减震器 | 0 | — | — | — |
| 6 | `air_reservoir@drivetrain` | air reservoir | воздушный ресивер | 储气罐 | 12 | — | — | — |
| 7 | `air_spring@drivetrain` | air spring / airbag / air strut | пневматическая рессора / пневмобаллон | 空气弹簧 / 气囊弹簧 / 气动支柱 | 0 | — | — | — |
| 8 | `air_spring_fl@drivetrain` | air spring (FL) | пневмобаллон (ПЛ) | 空气弹簧(左前) | 0 | — | — | — |
| 9 | `air_spring_fr@drivetrain` | air spring (FR) | пневмобаллон (ПП) | 空气弹簧(右前) | 0 | — | — | — |
| 10 | `air_spring_rl@drivetrain` | air spring (RL) | пневмобаллон (ЗЛ) | 空气弹簧(左后) | 0 | — | — | — |
| 11 | `air_suspension@drivetrain` | Air Suspension R | пневмоподвеска | 空气悬架右 | 0 | 1 | 1 | C0500, C0550 |
| 12 | `air_suspension_compressor@drivetrain` | air suspension compressor | компрессор пневмоподвески | 空气悬架压缩机 | 8 | — | — | — |
| 13 | `air_suspension_valve_block@drivetrain` | air suspension valve block / solenoid block | клапанный блок пневмоподвески | 空气悬架阀块 / 电磁阀块 | 0 | — | — | — |
| 14 | `alloy_wheel@drivetrain` | alloy wheel / cast alloy wheel | литой алюминиевый диск | 合金轮毂 / 铸造合金轮毂 | 0 | — | — | — |
| 15 | `allseason_tire@drivetrain` | all-season tire | всесезонная шина | 全季轮胎 | 0 | — | — | — |
| 16 | `antiroll_bar_bushing@drivetrain` | anti-roll bar bushing / sway bar bushing | втулка стабилизатора | 防倾杆衬套 / 横向稳定杆衬套 | 0 | — | — | — |
| 17 | `atf@drivetrain` | ATF (automatic transmission fluid) | масло АКПП (ATF) | 自动变速箱油 (ATF) | 0 | — | — | — |
| 18 | `automated_manual_transmission@drivetrain` | automated manual transmission / robotised gearbox | роботизированная КПП (РКПП) | 自动化手动变速箱 / AMT变速箱 | 0 | — | — | — |
| 19 | `automatic_transmission@drivetrain` | automatic transmission (AT) | автоматическая коробка передач (АКПП) | 自动变速箱 (AT) | 0 | — | — | — |
| 20 | `ball_joint@drivetrain` | ball joint | шаровая опора | 球头 | 0 | — | — | — |
| 21 | `ball_joint_dust_boot@drivetrain` | ball joint dust boot | пыльник шаровой опоры | 球头防尘罩 | 0 | — | — | — |
| 22 | `ball_seat_wheel_nut@drivetrain` | ball seat wheel nut | сфероконусная гайка | 球面座轮毂螺母 | 0 | — | — | — |
| 23 | `bead@drivetrain` | bead / bead bundle | борт шины | 胎圈 / 钢丝束 | 0 | — | — | — |
| 24 | `belt@drivetrain` | belt / breaker belt | брекер / подушечный слой | 带束层 / 缓冲层 | 0 | — | — | — |
| 25 | `bevel_gear@drivetrain` | bevel gear | коническая шестерня | 锥齿轮 | 0 | — | — | — |
| 26 | `bevel_gears@drivetrain` | bevel gears / ring gear and pinion | конические шестерни главной передачи | 锥齿轮 / 环形齿轮与小齿轮 | 0 | — | — | — |
| 27 | `blocking_ring@drivetrain` | blocking ring / synchro ring | блокирующее кольцо синхронизатора | 同步器锁止环 | 0 | — | — | — |
| 28 | `breather_valve@drivetrain` | breather valve | сапун (клапан вентиляции) | 透气阀 | 1 | — | — | — |
| 29 | `bump_stop@drivetrain` | bump stop / jounce bumper / compression stop | буфер сжатия / отбойник | 缓冲限位块 / 压缩限位块 | 0 | — | — | — |
| 30 | `bush@drivetrain` | bush (bushing) | сайлентблок, втулка | 衬套 | 5 | — | — | — |
| 31 | `bushing@drivetrain` | bushing / rubber bushing / silent block | сайлентблок | 衬套 / 橡胶衬套 / 减振块 | 0 | — | — | — |
| 32 | `carbon_fibre_wheel@drivetrain` | carbon fibre wheel | карбоновый диск | 碳纤维轮毂 | 0 | — | — | — |
| 33 | `carcass@drivetrain` | carcass / tyre casing | каркас шины | 轮胎胎体 | 0 | — | — | — |
| 34 | `center_support_bearing@drivetrain` | center support bearing / carrier bearing | промежуточная опора карданного вала | 中间支撑轴承 / 托架轴承 | 0 | — | — | — |
| 35 | `centre_cap@drivetrain` | centre cap / hub cap / wheel cover | декоративный колпак / заглушка центра | 中心盖 / 轮毂盖 / 轮盖 | 0 | — | — | — |
| 36 | `centre_differential@drivetrain` | centre differential | межосевой дифференциал | 中央差速器 | 0 | — | — | — |
| 37 | `chassis@drivetrain` | chassis | шасси / ходовая часть | 底盘 | 4 | — | — | — |
| 38 | `clipon_wheel_weight@drivetrain` | clip-on wheel weight | набивной балансировочный груз | 夹式平衡块 | 0 | — | — | — |
| 39 | `clock_spring@drivetrain` | clock spring | шлейф рулевой колонки | 气囊游丝 / 方向盘螺旋电缆 | 0 | — | — | — |
| 40 | `clutch@drivetrain` | clutch | сцепление | 离合器 | 2 | — | — | — |
| 41 | `clutch_cable@drivetrain` | clutch cable | трос сцепления | 离合器拉索 | 0 | — | — | — |
| 42 | `clutch_disc@drivetrain` | clutch disc / clutch plate | диск сцепления | 离合器片 | 0 | — | — | — |
| 43 | `clutch_disc_damper_springs@drivetrain` | clutch disc damper springs / torsional springs | демпфирующие пружины диска сцепления | 离合器盘阻尼弹簧 / 扭转弹簧 | 0 | — | — | — |
| 44 | `clutch_disc_lining@drivetrain` | clutch disc lining / clutch facing | накладки диска сцепления | 离合器片摩擦衬片 | 0 | — | — | — |
| 45 | `clutch_fork@drivetrain` | clutch fork | вилка выключения сцепления | 离合器拨叉 | 0 | — | — | — |
| 46 | `clutch_master_cylinder@drivetrain` | clutch master cylinder | главный цилиндр сцепления | 离合器主缸 | 0 | — | — | — |
| 47 | `clutch_pack@drivetrain` | clutch pack / friction pack (automatic transmission) | фрикционный пакет АКПП | 离合器组 / 摩擦片组（自动变速箱） | 0 | — | — | — |
| 48 | `clutch_pedal@drivetrain` | clutch pedal | педаль сцепления | 离合器踏板 | 0 | — | — | — |
| 49 | `clutch_release_bearing@drivetrain` | clutch release bearing / throw-out bearing | выжимной подшипник | 分离轴承 | 0 | — | — | — |
| 50 | `clutch_slave_cylinder@drivetrain` | clutch slave cylinder | рабочий цилиндр сцепления | 离合器从缸 | 0 | — | — | — |
| 51 | `coil_spring@drivetrain` | coil spring | пружина (витая) | 螺旋弹簧 | 0 | 2 | 1 | C0550 |
| 52 | `concentric_slave_cylinder@drivetrain` | concentric slave cylinder | концентрический рабочий цилиндр сцепления | 同心式离合器分泵 | 0 | — | — | — |
| 53 | `conical_wheel_nut@drivetrain` | conical wheel nut | конусная гайка | 锥形轮毂螺母 | 0 | — | — | — |
| 54 | `constant_velocity_joint@drivetrain` | constant velocity joint (CV) | ШРУС (шарнир равных угловых скоростей) | 等速万向节 | 0 | — | — | — |
| 55 | `control_arm_bushing@drivetrain` | control arm bushing / rubber-metal bushing | сайлентблок рычага | 控制臂衬套 / 橡胶金属衬套 | 0 | — | — | — |
| 56 | `countershaft@drivetrain` | countershaft / layshaft / intermediate shaft | промежуточный вал / контрвал | 副轴 / 中间轴 | 0 | — | — | — |
| 57 | `cv_boot@drivetrain` | CV boot | пыльник ШРУСа | 球笼防尘套 | 0 | — | — | — |
| 58 | `cv_boot_clamp@drivetrain` | CV boot clamp | хомут пыльника ШРУСа | 等速万向节防尘套卡箍 | 0 | — | — | — |
| 59 | `cv_joint@drivetrain` | CV joint (constant velocity) | шарнир равных угловых скоростей (ШРУС) | 等速万向节 | 0 | — | — | — |
| 60 | `cvt@drivetrain` | CVT (continuously variable transmission) | вариатор (CVT) | 无级变速器 (CVT) | 0 | — | — | — |
| 61 | `cvt_belt@drivetrain` | CVT belt / drive belt | ремень вариатора | 无级变速器传动带 | 0 | — | — | — |
| 62 | `cvt_fluid@drivetrain` | CVT fluid / CVTF | жидкость вариатора (CVTF) | CVT变速箱油 | 0 | — | — | — |
| 63 | `cvt_pulley@drivetrain` | CVT pulley | шкив вариатора | 无级变速器皮带轮 | 0 | — | — | — |
| 64 | `de_dion_axle@drivetrain` | De Dion axle | мост Де-Дион | 德迪昂车桥 | 0 | — | — | — |
| 65 | `diaphragm_spring@drivetrain` | diaphragm spring | диафрагменная пружина | 膜片弹簧 | 0 | — | — | — |
| 66 | `differential@drivetrain` | differential | дифференциал | 差速器 | 0 | — | 3 | C0550 |
| 67 | `differential_bearing@drivetrain` | differential bearing | подшипник дифференциала | 差速器轴承 | 0 | — | — | — |
| 68 | `differential_lock@drivetrain` | differential lock / locker / locking diff | блокировка дифференциала | 差速器锁 | 0 | — | — | — |
| 69 | `differential_pinion_gears@drivetrain` | differential pinion gears / spider gears | сателлиты дифференциала | 差速器小齿轮 / 行星齿轮 | 0 | — | — | — |
| 70 | `differential_pinion_seal@drivetrain` | differential pinion seal / axle shaft seal | сальник дифференциала | 差速器油封 / 半轴油封 | 0 | — | — | — |
| 71 | `double_row_angular_contact_bearing@drivetrain` | double row angular contact bearing (gen 2) | ступичный подшипник второго поколения (двухрядный) | 双列角接触轴承（第二代） | 0 | — | — | — |
| 72 | `drive_shaft@drivetrain` | drive shaft / propeller shaft | карданный вал | 传动轴 | 0 | — | — | — |
| 73 | `drive_shaft_lock_nut@drivetrain` | drive shaft lock nut | гайка крепления приводного вала | 驱动轴锁紧螺母 | 1 | — | — | — |
| 74 | `driveshaft@drivetrain` | driveshaft | приводной вал | 驱动轴 | 2 | — | — | — |
| 75 | `dsg_fluid@drivetrain` | DSG fluid / DCT fluid | жидкость DSG / преселективной КПП | DSG变速箱油 / 双离合变速箱油 | 0 | — | — | — |
| 76 | `dual_clutch_transmission@drivetrain` | dual clutch transmission / direct shift gearbox | преселективная КПП / DSG | 双离合变速箱 / 直接换挡变速箱 | 0 | — | — | — |
| 77 | `dual_motor_with_reducer_assembly@drivetrain` | dual motor with reducer assembly | двойной электромотор с редуктором | 双电机带减速器总成 | 1 | — | — | — |
| 78 | `dynamic_damper@drivetrain` | dynamic damper / vibration absorber | динамический демпфер / гаситель вибраций | 动力减振器 / 振动吸收器 | 0 | — | — | — |
| 79 | `electromagnetic_coupling@drivetrain` | electromagnetic coupling / Haldex coupling | электромагнитная муфта подключения полного привода | 电磁联轴器 / 哈尔德克斯联轴器 | 0 | — | — | — |
| 80 | `electronic_differential_lock@drivetrain` | electronic differential lock / XDS / eTorsen | электронная блокировка дифференциала | 电子差速锁 / XDS / eTorsen | 0 | — | — | — |
| 81 | `element_kolesa_pl@drivetrain` | Element Kolesa Pl | Элемент колеса ПЛ | Элемент колеса ПЛ | 0 | — | — | — |
| 82 | `element_kolesa_pl_3@drivetrain` | Element Kolesa Pl 3 | Элемент колеса ПЛ (3) | Элемент колеса ПЛ (3) | 0 | — | — | — |
| 83 | `element_kolesa_pp@drivetrain` | Element Kolesa Pp | Элемент колеса ПП | Элемент колеса ПП | 0 | — | — | — |
| 84 | `element_kolesa_pp_3@drivetrain` | Element Kolesa Pp 3 | Элемент колеса ПП (3) | Элемент колеса ПП (3) | 0 | — | — | — |
| 85 | `element_kolesa_zl@drivetrain` | Element Kolesa Zl | Элемент колеса ЗЛ | Элемент колеса ЗЛ | 0 | — | — | — |
| 86 | `element_kolesa_zl_3@drivetrain` | Element Kolesa Zl 3 | Элемент колеса ЗЛ (3) | Элемент колеса ЗЛ (3) | 0 | — | — | — |
| 87 | `element_kolesa_zp@drivetrain` | Element Kolesa Zp | Элемент колеса ЗП | Элемент колеса ЗП | 0 | — | — | — |
| 88 | `element_kolesa_zp_3@drivetrain` | Element Kolesa Zp 3 | Элемент колеса ЗП (3) | Элемент колеса ЗП (3) | 0 | — | — | — |
| 89 | `final_drive@drivetrain` | final drive | главная передача | 主减速器 | 0 | — | — | — |
| 90 | `floor_pan@drivetrain` | Floor R — Привод | Днище#2 — Привод | 底板右 — Привод | 0 | 1 | — | B1011, B1012 |
| 91 | `forged_wheel@drivetrain` | forged wheel | кованый диск | 锻造轮毂 | 0 | — | — | — |
| 92 | `front_abs_wheel_speed_sensor@drivetrain` | front ABS wheel speed sensor | датчик ABS (перед.) | 前轮ABS轮速传感器 | 0 | — | — | — |
| 93 | `front_anti_roll_bar@drivetrain` | front anti-roll bar | передний стабилизатор | 前防倾杆 | 0 | 1 | 1 | C0550 |
| 94 | `front_antiroll_bar@drivetrain` | front anti-roll bar | передний стабилизатор | 前防倾杆 | 0 | — | — | — |
| 95 | `front_axle@drivetrain` | front axle | передний мост | 前桥 | 0 | — | — | — |
| 96 | `front_axle_shaft@drivetrain` | front axle shaft | приводной вал (перед.) | 前驱动轴 | 1 | — | — | — |
| 97 | `front_clock_spring@drivetrain` | front clock spring | шлейф рулевой колонки (перед.) | 前气囊游丝 | 0 | — | — | — |
| 98 | `front_hubcap@drivetrain` | front hubcap | колпак (перед.) | 前轮轮毂盖 | 0 | — | — | — |
| 99 | `front_inner_cv_joint@drivetrain` | front inner CV joint | ШРУС (внутр.) (перед.) | 前内侧等速万向节 | 0 | — | — | — |
| 100 | `front_left_bushing@drivetrain` | front left bushing | сайлентблок (перед., лев.) | 前左衬套 | 0 | — | — | — |
| 101 | `front_left_coil_spring@drivetrain` | front left coil spring | пружина (перед., лев.) | 前左螺旋弹簧 | 0 | — | — | — |
| 102 | `front_left_control_arm@drivetrain` | front left control arm | рычаг подвески (перед., лев.) | 前左悬架控制臂 | 0 | 1 | 1 | C0550 |
| 103 | `front_left_cv_joint@drivetrain` | front left CV joint | ШРУС (перед., лев.) | 前左等速万向节 | 0 | — | — | — |
| 104 | `front_left_shock_absorber@drivetrain` | front left shock absorber | амортизатор (перед., лев.) | 前左减震器 | 0 | — | — | — |
| 105 | `front_left_stabilizer_bushing@drivetrain` | front left stabilizer bushing | втулка стабилизатора (перед., лев.) | 前左稳定杆衬套 | 0 | — | — | — |
| 106 | `front_left_strut@drivetrain` | front left strut | стойка (перед., лев.) | 前左支柱 | 0 | — | — | — |
| 107 | `front_left_strut_mount@drivetrain` | front left strut mount | опора стойки (перед., лев.) | 前左支柱安装座 | 0 | — | — | — |
| 108 | `front_left_tire@drivetrain` | front left tire | шина (перед., лев.) | 前左轮胎 | 0 | — | — | — |
| 109 | `front_left_wheel@drivetrain` | front left wheel | колесо (перед., лев.) | 前左轮 | 0 | — | — | — |
| 110 | `front_left_wheel_bearing@drivetrain` | front left wheel bearing | подшипник ступицы (перед., лев.) | 前左轮轴承 | 0 | — | — | — |
| 111 | `front_outer_cv_joint@drivetrain` | front outer CV joint | ШРУС (наруж.) (перед.) | 前外侧等速万向节 | 0 | — | — | — |
| 112 | `front_right_bushing@drivetrain` | front right bushing | сайлентблок (перед., прав.) | 前右衬套 | 0 | — | — | — |
| 113 | `front_right_coil_spring@drivetrain` | front right coil spring | пружина (перед., прав.) | 前右螺旋弹簧 | 0 | — | — | — |
| 114 | `front_right_control_arm@drivetrain` | front right control arm | рычаг подвески (перед., прав.) | 前右悬架控制臂 | 0 | 2 | 1 | C0550 |
| 115 | `front_right_cv_joint@drivetrain` | front right CV joint | ШРУС (перед., прав.) | 前右等速万向节 | 0 | — | — | — |
| 116 | `front_right_shock_absorber@drivetrain` | front right shock absorber | амортизатор (перед., прав.) | 前右减震器 | 0 | — | — | — |
| 117 | `front_right_stabilizer_bushing@drivetrain` | front right stabilizer bushing | втулка стабилизатора (перед., прав.) | 前右稳定杆衬套 | 0 | — | — | — |
| 118 | `front_right_strut@drivetrain` | front right strut | стойка (перед., прав.) | 前右支柱 | 0 | — | — | — |
| 119 | `front_right_strut_mount@drivetrain` | front right strut mount | опора стойки (перед., прав.) | 前右支柱安装座 | 0 | — | — | — |
| 120 | `front_right_tire@drivetrain` | front right tire | шина (перед., прав.) | 前右轮胎 | 0 | — | — | — |
| 121 | `front_right_wheel@drivetrain` | front right wheel | колесо (перед., прав.) | 前右轮 | 0 | — | — | — |
| 122 | `front_right_wheel_bearing@drivetrain` | front right wheel bearing | подшипник ступицы (перед., прав.) | 前右轮轴承 | 0 | — | — | — |
| 123 | `front_shock_tower_brace@drivetrain` | front shock tower brace | распорка передних стоек | 前减震塔连接横梁 | 1 | — | — | — |
| 124 | `front_suspension@drivetrain` | front suspension | передняя подвеска | 前悬架 | 0 | — | — | — |
| 125 | `front_transmission_mount@drivetrain` | front transmission mount | опора коробки передач (перед.) | 前变速箱安装座 | 0 | — | — | — |
| 126 | `front_trunk_strut@drivetrain` | front trunk strut | упор багажника (перед.) | 前行李箱支柱 | 0 | — | — | — |
| 127 | `front_wheel_hub@drivetrain` | front wheel hub | ступица (перед.) | 前轮轮毂 | 0 | — | — | — |
| 128 | `front_wheel_rim@drivetrain` | front wheel rim | диск колеса (перед.) | 前轮轮辋 | 0 | — | — | — |
| 129 | `front_wheel_stud@drivetrain` | front wheel stud | шпилька колеса (перед.) | 前轮螺柱 | 0 | — | — | — |
| 130 | `fullsize_spare_wheel@drivetrain` | full-size spare wheel | полноразмерная запаска | 全尺寸备胎 | 0 | — | — | — |
| 131 | `gaiter@drivetrain` | gaiter (boot) | пыльник | 防尘套 | 5 | — | — | — |
| 132 | `gasfilled_shock_absorber@drivetrain` | gas-filled shock absorber | газовый амортизатор | 充气式减震器 | 0 | — | — | — |
| 133 | `gear_lever@drivetrain` | gear lever / gear shift / shifter | рычаг переключения передач | 变速杆 / 换挡杆 | 7 | — | — | — |
| 134 | `gear_oil@drivetrain` | gear oil / transmission fluid | масло КПП трансмиссионное | 齿轮油 / 变速箱液 | 0 | — | — | — |
| 135 | `gear_selector_position_sensor@drivetrain` | gear selector position sensor / transmission range sensor | датчик выбора передачи | 换挡位置传感器 / 变速箱档位传感器 | 0 | — | — | — |
| 136 | `gear_selector_rod@drivetrain` | gear selector rod / shift linkage | тяга кулисы | 换挡拉杆 / 换挡连杆机构 | 0 | — | — | — |
| 137 | `half_shaft@drivetrain` | half shaft / CV axle | полуось / ШРУС | 半轴 / 等速驱动轴 | 0 | — | — | — |
| 138 | `half_shaft_cv_axle@drivetrain` | half shaft / CV axle | полуось / ШРУС | 半轴 / 等速驱动轴 | 0 | 2 | 2 | C0550 |
| 139 | `halfshaft_oil_seal@drivetrain` | halfshaft oil seal | сальник полуоси | 半轴油封 | 1 | — | — | — |
| 140 | `helical_gear@drivetrain` | helical gear | косозубая шестерня | 斜齿轮 | 0 | — | — | — |
| 141 | `hub_assembly@drivetrain` | hub assembly | ступичный узел | 轮毂总成 | 0 | — | — | — |
| 142 | `hub_cap@drivetrain` | hub cap / centre cap | колпак / заглушка ступицы | 轮毂盖 | 0 | — | — | — |
| 143 | `hub_centric_ring@drivetrain` | hub centric ring / centring ring | центровочное кольцо | 轮毂定心环 | 0 | — | — | — |
| 144 | `hub_unit_bearing@drivetrain` | hub unit bearing (gen 3) | ступичный подшипник третьего поколения (интегрированный) | 轮毂单元轴承（第三代） | 0 | — | — | — |
| 145 | `hypoid_gear_set@drivetrain` | hypoid gear set | гипоидная передача | 准双曲面齿轮组 | 0 | — | — | — |
| 146 | `idler_gear@drivetrain` | idler gear | промежуточная шестерня | 惰轮 | 0 | — | — | — |
| 147 | `inner_cv_joint@drivetrain` | inner CV joint | ШРУС (внутр.) | 内侧等速万向节 | 0 | — | — | — |
| 148 | `input_shaft@drivetrain` | input shaft / primary shaft | первичный (входной) вал | 输入轴 / 一轴 | 0 | — | — | — |
| 149 | `input_shaft_oil_seal@drivetrain` | input shaft oil seal | сальник входного вала | 输入轴油封 | 1 | — | — | — |
| 150 | `input_shaft_speed_sensor@drivetrain` | input shaft speed sensor / turbine speed sensor | датчик скорости входного вала КПП | 输入轴转速传感器／涡轮转速传感器 | 0 | — | — | — |
| 151 | `king_pin@drivetrain` | king pin | шкворень | 主销 | 1 | — | — | — |
| 152 | `lateral_link@drivetrain` | lateral link / transverse arm | поперечный рычаг | 横向连杆／横臂 | 0 | — | — | — |
| 153 | `lateral_links@drivetrain` | lateral links / transverse links | поперечные рычаги | 横向连杆组 | 0 | — | — | — |
| 154 | `lateral_tyre_slip@drivetrain` | lateral tyre slip / cornering stiffness | боковое скольжение шины / боковая жёсткость | 轮胎侧向滑移／过弯刚度 | 0 | — | — | — |
| 155 | `leaf_spring@drivetrain` | leaf spring | рессора | 板簧 | 5 | — | — | — |
| 156 | `leaf_spring_clip@drivetrain` | leaf spring clip / U-bolt | хомут рессоры | 钢板弹簧卡箍／U形螺栓 | 0 | — | — | — |
| 157 | `limitedslip_differential@drivetrain` | limited-slip differential (LSD) | дифференциал повышенного трения (LSD) | 限滑差速器 (LSD) | 0 | — | — | — |
| 158 | `lowered_suspension@drivetrain` | lowered suspension / lowering kit | занижение подвески | 降低悬架／降低套件 | 0 | — | — | — |
| 159 | `lowering_springs@drivetrain` | lowering springs | пружины занижения | 降低弹簧 | 0 | — | — | — |
| 160 | `macpherson_strut@drivetrain` | MacPherson strut | стойка Макферсон | 麦弗逊支柱 | 0 | — | — | — |
| 161 | `magnetorheological_damper@drivetrain` | magnetorheological damper / MagneRide | магнитореологический амортизатор | 磁流变减振器／MagneRide | 0 | — | — | — |
| 162 | `main_leaf@drivetrain` | main leaf / master leaf | коренной лист рессоры | 主簧片 | 0 | — | — | — |
| 163 | `manual_transmission@drivetrain` | manual transmission (MT) | механическая коробка передач (МКПП) | 手动变速箱 (MT) | 0 | — | — | — |
| 164 | `monotube_shock_absorber@drivetrain` | mono-tube shock absorber | однотрубный амортизатор | 单筒式减振器 | 0 | — | — | — |
| 165 | `multiplate_clutch@drivetrain` | multi-plate clutch / friction clutch pack | многодисковая муфта | 多片式离合器／摩擦片组 | 0 | — | — | — |
| 166 | `nizhniy_rychag_pa_shir@drivetrain` | Lower Control Arm R | Нижний рычаг ПА (шир.) | 下控制臂右 | 0 | — | — | — |
| 167 | `nizhniy_rychag_pb@drivetrain` | Lower Control Arm R | Нижний рычаг ПБ | 下控制臂右 | 0 | — | — | — |
| 168 | `nizhniy_rychag_pb_shir@drivetrain` | Lower Control Arm R | Нижний рычаг ПБ (шир.) | 下控制臂右 | 0 | — | — | — |
| 169 | `nizhniy_rychag_peredniy_a@drivetrain` | Lower Control Arm | Нижний рычаг передний А | 下控制臂 | 0 | — | — | — |
| 170 | `nizhniy_rychag_peredniy_b@drivetrain` | Lower Control Arm | Нижний рычаг передний Б | 下控制臂 | 0 | — | — | — |
| 171 | `nizhniy_rychag_z_shir@drivetrain` | Lower Control Arm | Нижний рычаг З (шир.) | 下控制臂 | 0 | — | — | — |
| 172 | `nizhniy_rychag_zadniy@drivetrain` | Lower Control Arm | Нижний рычаг задний | 下控制臂 | 0 | — | — | — |
| 173 | `nordic_tyre@drivetrain` | Nordic tyre / friction tyre / Scandinavian tyre | нешипованная зимняя шина (скандинавская) | 北欧型轮胎／无钉冬季轮胎 | 0 | — | — | — |
| 174 | `open_differential@drivetrain` | open differential | открытый дифференциал | 开放式差速器 | 0 | — | — | — |
| 175 | `outer_cv_joint@drivetrain` | outer CV joint | ШРУС (наруж.) | 外等速万向节 | 0 | — | — | — |
| 176 | `output_shaft@drivetrain` | output shaft / secondary shaft / mainshaft | вторичный (выходной) вал | 输出轴 / 二轴 | 0 | — | — | — |
| 177 | `output_shaft_speed_sensor@drivetrain` | output shaft speed sensor / vehicle speed sensor | датчик скорости выходного вала КПП | 输出轴转速传感器／车速传感器 | 0 | — | — | — |
| 178 | `peredniy_differentsial@drivetrain` | Peredniy Differentsial | Передний дифференциал | Передний дифференциал | 0 | — | — | — |
| 179 | `peredniy_differentsial_gruppa@drivetrain` | Peredniy Differentsial Gruppa | Передний дифференциал (группа) | Передний дифференциал (группа) | 0 | — | — | — |
| 180 | `peredniy_kardan@drivetrain` | Peredniy Kardan | Передний кардан | Передний кардан | 0 | — | — | — |
| 181 | `pinion@drivetrain` | pinion | шестерня (ведущая) | 小齿轮 | 0 | — | — | — |
| 182 | `planet_carrier@drivetrain` | planet carrier | водило | 行星架 | 1 | — | — | — |
| 183 | `planet_gears@drivetrain` | planet gears / planetary gears | сателлиты | 行星齿轮 | 0 | — | — | — |
| 184 | `planetary_gearset@drivetrain` | planetary gearset | планетарная передача | 行星齿轮组 | 0 | — | — | — |
| 185 | `pressure_plate@drivetrain` | pressure plate / clutch cover assembly | ведущий диск / корзина сцепления | 压力板 / 离合器盖总成 | 0 | — | — | — |
| 186 | `primary_pulley@drivetrain` | primary pulley / drive pulley | ведущий шкив вариатора | 主动滑轮／驱动滑轮 | 0 | — | — | — |
| 187 | `propeller_shaft@drivetrain` | drive shaft / propeller shaft | карданный вал | 传动轴 | 1 | — | 2 | P0500 |
| 188 | `pump@drivetrain` | pump / impeller (torque converter) | насосное колесо гидротрансформатора | 液力变矩器泵轮／叶轮 | 0 | — | — | — |
| 189 | `rack_and_pinion@drivetrain` | rack and pinion | реечная передача | 齿条齿轮 | 0 | — | — | — |
| 190 | `rear_abs_wheel_speed_sensor@drivetrain` | rear ABS wheel speed sensor | датчик ABS (зад.) | 后侧ABS轮速传感器 | 0 | — | — | — |
| 191 | `rear_anti_roll_bar@drivetrain` | rear anti-roll bar | задний стабилизатор | 后横向稳定杆 | 1 | 1 | 1 | C0550 |
| 192 | `rear_antiroll_bar@drivetrain` | rear anti-roll bar | задний стабилизатор | 后横向稳定杆 | 0 | — | — | — |
| 193 | `rear_axle@drivetrain` | rear axle | задний мост | 后桥 | 1 | — | — | — |
| 194 | `rear_axle_housing@drivetrain` | rear axle housing / axle beam | балка заднего моста | 后桥壳／桥梁 | 0 | — | — | — |
| 195 | `rear_axle_shaft@drivetrain` | Half Shaft R | полуось (зад.) | 半轴右 | 0 | — | — | — |
| 196 | `rear_clock_spring@drivetrain` | rear clock spring | шлейф рулевой колонки (зад.) | 后侧气囊游丝（方向盘线圈） | 0 | — | — | — |
| 197 | `rear_differential@drivetrain` | rear differential / rear axle housing | дифференциал задний / картер заднего моста | 后差速器 / 后桥壳 | 0 | — | — | — |
| 198 | `rear_hubcap@drivetrain` | rear hubcap | колпак (зад.) | 后侧轮毂盖 | 0 | — | — | — |
| 199 | `rear_inner_cv_joint@drivetrain` | rear inner CV joint | ШРУС (внутр.) (зад.) | 后内等速万向节 | 0 | — | — | — |
| 200 | `rear_left_bushing@drivetrain` | rear left bushing | сайлентблок (зад., лев.) | 后左衬套 | 0 | — | — | — |
| 201 | `rear_left_coil_spring@drivetrain` | rear left coil spring | пружина (зад., лев.) | 后左螺旋弹簧 | 0 | — | — | — |
| 202 | `rear_left_control_arm@drivetrain` | rear left control arm | рычаг подвески (зад., лев.) | 左后控制臂 | 0 | 3 | 1 | C0550 |
| 203 | `rear_left_cv_joint@drivetrain` | rear left CV joint | ШРУС (зад., лев.) | 后左等速万向节 | 0 | — | — | — |
| 204 | `rear_left_shock_absorber@drivetrain` | rear left shock absorber | амортизатор (зад., лев.) | 后左减震器 | 0 | — | — | — |
| 205 | `rear_left_stabilizer_bushing@drivetrain` | rear left stabilizer bushing | втулка стабилизатора (зад., лев.) | 左后稳定杆衬套 | 0 | — | — | — |
| 206 | `rear_left_strut@drivetrain` | rear left strut | стойка (зад., лев.) | 后左支柱 | 0 | — | — | — |
| 207 | `rear_left_strut_mount@drivetrain` | rear left strut mount | опора стойки (зад., лев.) | 后左支柱安装座 | 0 | — | — | — |
| 208 | `rear_left_tire@drivetrain` | rear left tire | шина (зад., лев.) | 后左轮胎 | 0 | — | — | — |
| 209 | `rear_left_wheel@drivetrain` | rear left wheel | колесо (зад., лев.) | 后左轮 | 0 | — | — | — |
| 210 | `rear_left_wheel_bearing@drivetrain` | rear left wheel bearing | подшипник ступицы (зад., лев.) | 后左轮轴承 | 0 | — | — | — |
| 211 | `rear_outer_cv_joint@drivetrain` | rear outer CV joint | ШРУС (наруж.) (зад.) | 后外等速万向节 | 0 | — | — | — |
| 212 | `rear_right_bushing@drivetrain` | rear right bushing | сайлентблок (зад., прав.) | 后右衬套 | 0 | — | — | — |
| 213 | `rear_right_coil_spring@drivetrain` | Spring R | пружина (зад., прав.) | 弹簧右 | 0 | — | — | — |
| 214 | `rear_right_control_arm@drivetrain` | rear right control arm | рычаг подвески (зад., прав.) | 右后控制臂 | 0 | 1 | 1 | C0550 |
| 215 | `rear_right_cv_joint@drivetrain` | rear right CV joint | ШРУС (зад., прав.) | 后右等速万向节 | 0 | — | — | — |
| 216 | `rear_right_shock_absorber@drivetrain` | Shock Absorber | амортизатор (зад., прав.) | 减震器 | 0 | — | — | — |
| 217 | `rear_right_stabilizer_bushing@drivetrain` | rear right stabilizer bushing | втулка стабилизатора (зад., прав.) | 右后稳定杆衬套 | 0 | — | — | — |
| 218 | `rear_right_strut@drivetrain` | rear right strut | стойка (зад., прав.) | 后右支柱 | 0 | — | — | — |
| 219 | `rear_right_strut_mount@drivetrain` | rear right strut mount | опора стойки (зад., прав.) | 后右支柱安装座 | 0 | — | — | — |
| 220 | `rear_right_tire@drivetrain` | rear right tire | шина (зад., прав.) | 后右轮胎 | 0 | — | — | — |
| 221 | `rear_right_wheel@drivetrain` | rear right wheel | колесо (зад., прав.) | 后右轮 | 0 | — | — | — |
| 222 | `rear_right_wheel_bearing@drivetrain` | rear right wheel bearing | подшипник ступицы (зад., прав.) | 后右轮轴承 | 0 | — | — | — |
| 223 | `rear_suspension@drivetrain` | rear suspension | задняя подвеска | 后悬架 | 0 | — | — | — |
| 224 | `rear_transmission_mount@drivetrain` | rear transmission mount | опора коробки передач (зад.) | 后变速箱安装座 | 0 | — | — | — |
| 225 | `rear_trunk_strut@drivetrain` | rear trunk strut | упор багажника (зад.) | 后行李箱支柱 | 0 | — | — | — |
| 226 | `rear_wheel_hub@drivetrain` | rear wheel hub | ступица (зад.) | 后轮轮毂 | 0 | — | — | — |
| 227 | `rear_wheel_rim@drivetrain` | rear wheel rim | диск колеса (зад.) | 后轮轮辋 | 0 | — | — | — |
| 228 | `rear_wheel_stud@drivetrain` | rear wheel stud | шпилька колеса (зад.) | 后轮螺柱 | 0 | — | — | — |
| 229 | `reduction_gear@drivetrain` | reduction gear | редуктор | 减速器 | 20 | — | — | — |
| 230 | `ride_height_sensor@drivetrain` | ride height sensor | датчик высоты кузова | 车身高度传感器 | 0 | — | — | — |
| 231 | `right_subframe@drivetrain` | Subframe R | Подрамник задний (шир.) | 副车架右 | 1 | — | — | — |
| 232 | `rim@drivetrain` | rim / alloy wheel | диск колеса / легкосплавный диск | 轮辋 / 铝合金轮毂 | 0 | — | — | — |
| 233 | `ring_gear@drivetrain` | ring gear / annulus gear | коронная шестерня / кольцевая шестерня | 环形齿轮／齿圈 | 0 | — | — | — |
| 234 | `rubber_mounting@drivetrain` | rubber mounting | резиновая опора | 橡胶支座 | 0 | — | — | — |
| 235 | `runflat_tyre@drivetrain` | run-flat tyre | шина RunFlat (самонесущая) | 防爆轮胎（缺气保用轮胎） | 0 | — | — | — |
| 236 | `secondary_pulley@drivetrain` | secondary pulley / driven pulley | ведомый шкив вариатора | 从动滑轮／被动滑轮 | 0 | — | — | — |
| 237 | `selector_fork@drivetrain` | selector fork | вилка переключения передач | 拨叉 | 0 | — | — | — |
| 238 | `semitrailing_arms@drivetrain` | semi-trailing arms | косые рычаги | 半纵臂 | 0 | — | — | — |
| 239 | `shackle@drivetrain` | shackle / spring shackle | серьга рессоры | 弹簧吊耳 | 0 | — | — | — |
| 240 | `shift_gate@drivetrain` | shift gate / selector housing | кулиса переключения передач | 换挡导槽／选挡器壳体 | 0 | — | — | — |
| 241 | `shina_pl@drivetrain` | Tire FL | Шина ПЛ | 轮胎左前 | 0 | — | — | — |
| 242 | `shina_pp@drivetrain` | Tire FR | Шина ПП | 轮胎右前 | 0 | — | — | — |
| 243 | `shina_zl@drivetrain` | Tire RL | Шина ЗЛ | 轮胎左后 | 0 | — | — | — |
| 244 | `shina_zp@drivetrain` | Tire RR | Шина ЗП | 轮胎右后 | 0 | — | — | — |
| 245 | `shock_absorber@drivetrain` | shock absorber / damper | амортизатор | 减震器 | 0 | — | — | — |
| 246 | `shock_absorber_damper@drivetrain` | shock absorber / damper | амортизатор | 减震器 | 3 | 2 | 1 | C0550 |
| 247 | `shock_absorber_dust_cover@drivetrain` | shock absorber dust cover / dust boot | пыльник штока амортизатора | 减振器防尘罩 | 0 | — | — | — |
| 248 | `side_gear@drivetrain` | side gear / axle side gear | полуосевая шестерня | 半轴齿轮 | 0 | — | — | — |
| 249 | `solid_axle@drivetrain` | solid axle / live axle | неразрезная балка | 整体车桥／驱动桥 | 0 | — | — | — |
| 250 | `spacesaver_spare@drivetrain` | space-saver spare / compact spare | докатка (компактное запасное колесо) | 应急备胎 | 0 | — | — | — |
| 251 | `spare_tyre@drivetrain` | spare tyre / spare wheel | запасное колесо | 备用轮胎／备用车轮 | 0 | — | — | — |
| 252 | `spider_shaft@drivetrain` | spider shaft / pinion shaft | ось сателлитов | 差速器十字轴／小齿轮轴 | 0 | — | — | — |
| 253 | `spigot_bearing@drivetrain` | spigot bearing | направляющий подшипник | 导向轴承 | 0 | — | — | — |
| 254 | `spline@drivetrain` | spline | шлиц | 花键 | 0 | — | — | — |
| 255 | `spring_eye_bushing@drivetrain` | spring eye bushing | сайлентблок рессоры | 钢板弹簧衬套 | 0 | — | — | — |
| 256 | `stabilizator_p_shir@drivetrain` | Stabilizer Bar R | Стабилизатор П (шир.) | 稳定杆右 | 1 | — | — | — |
| 257 | `stabilizator_peredniy@drivetrain` | Stabilizer Bar | Стабилизатор передний | 稳定杆 | 2 | — | — | — |
| 258 | `stabilizator_z_shir@drivetrain` | Stabilizer Bar | Стабилизатор З (шир.) | 稳定杆 | 0 | — | — | — |
| 259 | `stabilizator_zadniy@drivetrain` | Stabilizer Bar | Стабилизатор задний | 稳定杆 | 0 | — | — | — |
| 260 | `stabilizer_bar@drivetrain` | stabilizer bar / anti-roll bar | стабилизатор поперечной устойчивости | 防倾杆 | 0 | — | — | — |
| 261 | `stabilizer_bar_anti_roll_bar@drivetrain` | stabilizer bar / anti-roll bar | стабилизатор поперечной устойчивости | 防倾杆 | 0 | 2 | — | C0550 |
| 262 | `stator@drivetrain` | stator / reactor (torque converter) | реактор гидротрансформатора | 定子 / 导轮（液力变矩器） | 0 | — | — | — |
| 263 | `steel_wheel@drivetrain` | steel wheel | стальной диск | 钢制轮辋 | 0 | — | — | — |
| 264 | `steering_knuckle@drivetrain` | steering knuckle | поворотный кулак | 转向节 | 5 | — | — | — |
| 265 | `strut@drivetrain` | Strut | стойка амортизатора | 减震支柱 | 0 | 3 | 1 | C0035, C0036, C0550 |
| 266 | `strut_mount@drivetrain` | strut mount | опора стойки | 支柱安装座 | 0 | — | — | — |
| 267 | `strut_mount_bearing@drivetrain` | strut mount bearing / bearing plate | подшипник опоры стойки | 支柱安装座轴承 / 轴承板 | 0 | — | — | — |
| 268 | `stub_axle@drivetrain` | stub axle | цапфа поворотного кулака | 转向节轴 | 0 | — | — | — |
| 269 | `stud@drivetrain` | stud / tyre stud | шип | 轮胎防滑钉 | 0 | — | — | — |
| 270 | `studded_tyre@drivetrain` | studded tyre | шипованная шина | 带钉轮胎 | 0 | — | — | — |
| 271 | `subframe@drivetrain` | subframe | подрамник | 副车架 | 8 | 3 | 3 | B1011, B1012, C0550 |
| 272 | `subframe_bushing@drivetrain` | subframe bushing | сайлентблок подрамника | 副车架衬套 | 0 | — | — | — |
| 273 | `summer_tire@drivetrain` | summer tire | летняя шина | 夏季轮胎 | 12 | — | — | — |
| 274 | `sun_gear@drivetrain` | sun gear | солнечная шестерня | 太阳轮 | 0 | — | — | — |
| 275 | `suspension@drivetrain` | suspension | подвеска | 悬架 | 15 | — | — | — |
| 276 | `suspension_link@drivetrain` | suspension link / rod | тяга подвески | 悬架拉杆 | 0 | — | — | — |
| 277 | `sway_bar_bracket@drivetrain` | sway bar bracket / anti-roll bar clamp | скоба стабилизатора | 横向稳定杆支架 | 0 | — | — | — |
| 278 | `sway_bar_link@drivetrain` | sway bar link / drop link / anti-roll bar link | тяга стабилизатора / стойка стабилизатора | 稳定杆连杆 | 0 | — | — | — |
| 279 | `synchroniser@drivetrain` | synchroniser / synchromesh | синхронизатор | 同步器 | 0 | — | — | — |
| 280 | `synchroniser_sleeve@drivetrain` | synchroniser sleeve / shifter sleeve | муфта синхронизатора | 同步器套筒 | 0 | — | — | — |
| 281 | `tapered_roller_wheel_bearing@drivetrain` | tapered roller wheel bearing (gen 1) | ступичный подшипник первого поколения (конический) | 圆锥滚子轮毂轴承（第一代） | 0 | — | — | — |
| 282 | `tierod@drivetrain` | tie-rod | рулевая тяга | 转向横拉杆 | 0 | — | — | — |
| 283 | `tire@drivetrain` | tire / tyre | шина | 轮胎 | 0 | — | — | — |
| 284 | `tire_sidewall@drivetrain` | tire sidewall | боковина шины | 轮胎侧壁 | 0 | — | — | — |
| 285 | `tire_tyre@drivetrain` | tire / tyre | шина | 轮胎 | 39 | 4 | — | — |
| 286 | `torque_converter@drivetrain` | torque converter | гидротрансформатор | 液力变矩器 | 0 | — | — | — |
| 287 | `torque_converter_lockup@drivetrain` | torque converter lock-up | блокировка гидротрансформатора | 变矩器锁止 | 0 | — | — | — |
| 288 | `torsen_differential@drivetrain` | Torsen differential (torque-sensing) | дифференциал Torsen | 托森差速器（扭矩感应式） | 0 | — | — | — |
| 289 | `torsion_bar@drivetrain` | torsion bar | торсион | 扭杆 | 0 | — | — | — |
| 290 | `torsion_beam@drivetrain` | torsion beam / twist beam / semi-independent | торсионная балка | 扭力梁悬架／半独立悬架 | 0 | — | — | — |
| 291 | `tpms@drivetrain` | TPMS (tire pressure monitoring) | система контроля давления в шинах (TPMS) | 胎压监测系统 (TPMS) | 2 | — | — | — |
| 292 | `tpms_sensor@drivetrain` | TPMS sensor / tyre pressure sensor | датчик давления TPMS | 胎压传感器 | 17 | — | — | — |
| 293 | `trailing_arm@drivetrain` | trailing arm | продольный рычаг | 纵臂 | 0 | — | — | — |
| 294 | `trailing_arms@drivetrain` | trailing arms | продольные рычаги (трейлинг-армы) | 纵臂 | 0 | — | — | — |
| 295 | `transfer_case@drivetrain` | transfer case | раздаточная коробка | 分动箱 | 0 | — | 1 | P0841 |
| 296 | `transmission@drivetrain` | transmission / drivetrain / powertrain | трансмиссия | 动力系统 | 0 | — | — | — |
| 297 | `transmission_control_module@drivetrain` | transmission control module (TCM) | блок управления трансмиссией (TCM) | 变速箱控制模块（TCM） | 0 | — | — | — |
| 298 | `transmission_mount@drivetrain` | transmission mount | опора коробки передач | 变速箱安装座 | 0 | — | — | — |
| 299 | `transmission_shaft_seal@drivetrain` | transmission shaft seal / output shaft seal | сальник вала КПП | 变速箱输出轴油封 | 0 | — | — | — |
| 300 | `tread_wear_indicator@drivetrain` | tread wear indicator / TWI | индикатор износа протектора | 胎纹磨损指示器（TWI） | 0 | — | — | — |
| 301 | `trunk_strut@drivetrain` | trunk strut | упор багажника | 行李箱支柱 | 0 | — | — | — |
| 302 | `turbine_wheel@drivetrain` | turbine wheel (torque converter) | турбинное колесо гидротрансформатора | 液力变矩器涡轮 | 0 | — | — | — |
| 303 | `twintube_shock_absorber@drivetrain` | twin-tube shock absorber | двухтрубный амортизатор | 双管减振器 | 0 | — | — | — |
| 304 | `tyre_repair_kit@drivetrain` | tyre repair kit / tyre inflation kit | ремкомплект шин | 轮胎修补套件 | 0 | — | — | — |
| 305 | `tyre_sealant@drivetrain` | tyre sealant | герметик для шин | 轮胎密封剂 | 1 | — | — | — |
| 306 | `tyre_tread@drivetrain` | tyre tread / tread pattern | протектор шины | 轮胎花纹 | 1 | — | — | — |
| 307 | `universal_joint@drivetrain` | universal joint / U-joint / cardan joint | крестовина карданного вала | 万向节 | 1 | — | — | — |
| 308 | `valve_body@drivetrain` | valve body (automatic transmission) | гидравлический блок управления АКПП | 液压阀体（自动变速箱） | 0 | — | — | — |
| 309 | `valve_cap@drivetrain` | valve cap | колпачок вентиля | 气门嘴帽 | 0 | — | — | — |
| 310 | `valve_core@drivetrain` | valve core | золотник | 气门芯 | 0 | — | — | — |
| 311 | `valve_stem@drivetrain` | valve stem / tyre valve | вентиль / ниппель | 气门嘴 | 16 | — | — | — |
| 312 | `verkhniy_rychag_z_shir@drivetrain` | Upper Control Arm | Верхний рычаг З (шир.) | 上控制臂 | 0 | — | — | — |
| 313 | `verkhniy_rychag_zadniy@drivetrain` | Upper Control Arm | Верхний рычаг задний | 上控制臂 | 0 | — | — | — |
| 314 | `viscous_coupling@drivetrain` | viscous coupling / viscous LSD | вискомуфта дифференциала | 粘性联轴器／粘性限滑差速器 | 0 | — | — | — |
| 315 | `wheel@drivetrain` | wheel | колесо | 车轮 | 33 | 12 | 16 | — |
| 316 | `wheel_bearing@drivetrain` | wheel bearing / hub bearing | подшипник ступицы | 轮毂轴承 | 2 | — | — | — |
| 317 | `wheel_bolt@drivetrain` | wheel bolt / lug bolt | болт колёсный | 车轮螺栓 / 轮毂螺栓 | 0 | — | — | — |
| 318 | `wheel_hub@drivetrain` | wheel hub / hub | ступица колеса | 轮毂 | 0 | — | 4 | C0035, C0036 |
| 319 | `wheel_hub_hub@drivetrain` | wheel hub / hub | ступица колеса | 轮毂 | 8 | 2 | 2 | C0035, C0036 |
| 320 | `wheel_nut@drivetrain` | wheel nut / lug nut | гайка колёсная | 车轮螺母 / 轮毂螺母 | 0 | — | — | — |
| 321 | `wheel_spacer@drivetrain` | wheel spacer | проставочное кольцо | 车轮垫片 | 0 | — | — | — |
| 322 | `wheel_speed_fl@drivetrain` | wheel speed sensor (FL) | датчик скорости колеса (ПЛ) | 轮速传感器(左前) | 0 | — | — | — |
| 323 | `wheel_speed_fr@drivetrain` | wheel speed sensor (FR) | датчик скорости колеса (ПП) | 轮速传感器(右前) | 0 | — | — | — |
| 324 | `wheel_speed_rl@drivetrain` | wheel speed sensor (RL) | датчик скорости колеса (ЗЛ) | 轮速传感器(左后) | 0 | — | — | — |
| 325 | `wheel_speed_rr@drivetrain` | wheel speed sensor (RR) | датчик скорости колеса (ЗП) | 轮速传感器(右后) | 0 | — | — | — |
| 326 | `wheel_stud@drivetrain` | wheel stud / hub stud | шпилька колёсная | 轮螺柱 / 轮毂螺柱 | 0 | — | — | — |
| 327 | `wheel_weight@drivetrain` | wheel weight / balance weight | балансировочный груз | 平衡块 | 6 | — | — | — |
| 328 | `winter_tire@drivetrain` | winter tire / snow tire | зимняя шина | 冬季轮胎 | 24 | — | — | — |
| 329 | `wishbone@drivetrain` | wishbone | рычаг подвески (А-образный) | 叉臂 | 0 | — | — | — |
| 330 | `zadniy_differentsial@drivetrain` | Zadniy Differentsial | Задний дифференциал | Задний дифференциал | 0 | — | — | — |
| 331 | `zadniy_kardan@drivetrain` | Zadniy Kardan | Задний кардан | Задний кардан | 0 | — | — | — |

## 4. EV — Электрика: зарядка, инверторы, электромоторы, рекуперация (191 компонентов)

*Тяговая батарея, БМС, порты зарядки, инвертор, DC-DC преобразователь, электромоторы, стартер/генератор, АКБ 12В, проводка, предохранители, реле, электроника освещения, ЭБУ*

**Подсистемы:** hv_battery, charging, inverter_converter, electric_motors, 12v_system, wiring_fuses, ecus_modules, lighting_electronics

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `12v_battery@ev` | 12V battery | 12В аккумулятор | 12V蓄电池 | 0 | — | — | — |
| 2 | `12v_battery_ann@ev` | 12V auxiliary battery | 12В аккумулятор | 12V辅助电池 | 0 | — | — | — |
| 3 | `a@ev` | A/C relay | реле кондиционера | 空调继电器 | 0 | — | — | — |
| 4 | `abs@ev` | ABS/ESC control module / EBCM | блок управления ABS / ESC | ABS/ESC控制模块 / EBCM | 0 | — | — | — |
| 5 | `ac@ev` | AC/DC charging HV harness | ВВ жгут AC/DC зарядки | 交直流充电高压线束总成 | 1 | — | — | — |
| 6 | `agm_battery@ev` | AGM battery (Absorbent Glass Mat) | AGM-аккумулятор | AGM蓄电池（吸附式玻璃纤维隔板） | 0 | — | — | — |
| 7 | `airbag_control_module@ev` | airbag control module / SRS ECU | блок управления подушками безопасности | 安全气囊控制模块 / SRS电控单元 | 0 | — | — | — |
| 8 | `aircooled_battery@ev` | air-cooled battery | охлаждение батареи воздушное | 风冷蓄电池 | 0 | — | — | — |
| 9 | `alkaline_battery@ev` | alkaline battery | щелочной элемент | 碱性电池 | 0 | — | — | — |
| 10 | `alternator@ev` | alternator / generator | генератор | 发电机 | 0 | — | — | — |
| 11 | `alternator_belt_tensioner@ev` | alternator belt tensioner | натяжитель ремня генератора | 发电机皮带张紧器 | 0 | — | — | — |
| 12 | `alternator_brushes@ev` | alternator brushes | щётки генератора | 发电机电刷 | 0 | — | — | — |
| 13 | `alternator_drive_belt@ev` | alternator drive belt / serpentine belt / ribbed belt | ремень привода генератора | 发电机驱动皮带 / 多楔带 / 肋形皮带 | 0 | — | — | — |
| 14 | `alternator_rotor@ev` | alternator rotor | ротор генератора | 发电机转子 | 0 | — | — | — |
| 15 | `alternator_stator@ev` | alternator stator | статор генератора | 发电机定子 | 0 | — | — | — |
| 16 | `aluminiumion_battery@ev` | aluminium-ion battery | алюминий-ионный аккумулятор | 铝离子电池 | 0 | — | — | — |
| 17 | `automotive_battery@ev` | automotive battery | автомобильный аккумулятор | 汽车蓄电池 | 0 | — | — | — |
| 18 | `ballast_resistor@ev` | ballast resistor | балластный резистор | 镇流电阻 | 0 | — | — | — |
| 19 | `battery@ev` | battery / lead-acid battery | аккумуляторная батарея | 蓄电池 / 铅酸蓄电池 | 8 | — | — | — |
| 20 | `battery_cell@ev` | battery cell | ячейка аккумулятора | 电芯 | 1 | — | — | — |
| 21 | `battery_coolant@ev` | battery coolant | охлаждающая жидкость батареи | 电池冷却液 | 0 | — | — | — |
| 22 | `battery_enclosure@ev` | battery enclosure / tray | корпус / поддон батареи | 电池壳体 / 托盘 | 0 | — | — | — |
| 23 | `battery_heater@ev` | battery heater | нагреватель батареи | 电池加热器 | 0 | — | — | — |
| 24 | `battery_module@ev` | battery module | модуль аккумулятора | 电池模组 | 0 | — | — | — |
| 25 | `battery_terminal@ev` | battery terminal | клемма аккумулятора | 蓄电池端子 | 0 | — | — | — |
| 26 | `battery_thermal_management@ev` | battery thermal management | терморегулирование батареи | 电池热管理 | 0 | — | — | — |
| 27 | `battery_thermal_management_system@ev` | Battery Thermal Management System | система термоуправления батареи (BTMS) | 电池热管理系统 | 0 | — | — | — |
| 28 | `bcm@ev` | BCM (Body Control Module) | блок управления кузовом | 车身控制模块 | 0 | — | — | — |
| 29 | `bms@ev` | BMS (battery management system) | система управления батареей (BMS) | 电池管理系统 (BMS) | 0 | — | — | — |
| 30 | `bms_ann@ev` | battery management system (BMS) | система управления батареей (BMS) | 电池管理系统 | 0 | — | — | — |
| 31 | `busbar@ev` | busbar | шина (токопроводящая) | 汇流排 | 0 | — | — | — |
| 32 | `ccs1_dc_fast_charge@ev` | CCS1 (Combined Charging System 1) — DC fast charge | CCS1 — быстрая зарядка DC (Северная Америка) | CCS1组合充电系统 — 直流快充（北美） | 0 | — | — | — |
| 33 | `ccs2_dc_fast_charge@ev` | CCS2 (Combined Charging System 2) — DC fast charge | CCS2 — быстрая зарядка DC (Европа) | CCS2组合充电系统 — 直流快充（欧洲） | 0 | — | — | — |
| 34 | `ccs_connector@ev` | CCS connector (Combined Charging System) | разъём CCS | CCS充电接口 | 0 | — | — | — |
| 35 | `chademo_charging_connector@ev` | CHAdeMO charging connector | разъём CHAdeMO | CHAdeMO充电接口 | 0 | — | — | — |
| 36 | `chademo_dc_fast_charge@ev` | CHAdeMO — DC fast charge (Japanese standard) | CHAdeMO — быстрая зарядка DC (японский стандарт) | CHAdeMO — 直流快充（日本标准） | 0 | — | — | — |
| 37 | `charge_connector_lock@ev` | charge connector lock | блокировка зарядного разъёма | 充电枪锁止 | 0 | — | — | — |
| 38 | `charge_port@ev` | charge port / inlet | зарядный разъём / порт | 充电口 | 139 | — | — | — |
| 39 | `charge_port_door@ev` | charging flap / charge port door | крышка зарядного порта | 充电口盖 | 117 | 2 | — | P0A80, P3000 |
| 40 | `charging_cable@ev` | charging cable / EVSE cable | зарядный кабель | 充电电缆 | 4 | — | — | — |
| 41 | `charging_flap@ev` | charging flap / charge port door | крышка зарядного порта | 充电口盖 | 0 | — | — | — |
| 42 | `charging_inlet@ev` | charging inlet / charge port | зарядный порт / розетка автомобиля | 车载充电口 | 0 | — | — | — |
| 43 | `circuit_breaker@ev` | circuit breaker / auto-resetting fuse | предохранитель-автомат | 断路器 / 自复位保险丝 | 0 | — | — | — |
| 44 | `coil@ev` | coil | катушка | 线圈 | 1 | — | — | — |
| 45 | `condenser@ev` | condenser (capacitor) | конденсатор | 电容器 | 1 | — | — | — |
| 46 | `connector_seal@ev` | connector seal / weather seal | уплотнитель разъёма | 接插件密封圈 / 防水密封件 | 0 | — | — | — |
| 47 | `contact_breaker@ev` | contact breaker | прерыватель (контакты) | 断电器 | 0 | — | — | — |
| 48 | `cooling_fan_relay@ev` | cooling fan relay | реле вентилятора охлаждения | 冷却风扇继电器 | 0 | — | — | — |
| 49 | `cylindrical_cell@ev` | cylindrical cell | цилиндрический элемент | 圆柱电芯 | 0 | — | — | — |
| 50 | `dc_charge_port@ev` | DC fast charge port | разъём быстрой зарядки DC | 直流快充口 | 0 | — | — | — |
| 51 | `dc_fast_charger@ev` | DC fast charger (DCFC) / Mode 4 | быстрое зарядное устройство DC / режим 4 | 直流快速充电桩 (DCFC) / 模式4 | 0 | — | — | — |
| 52 | `dcdc_converter@ev` | DC-DC converter | DC-DC преобразователь | DC-DC转换器 | 0 | — | — | — |
| 53 | `desulfator@ev` | desulfator / battery reconditioner | десульфатор | 电池去硫化装置 / 电池修复仪 | 0 | — | — | — |
| 54 | `digital_instrument_cluster@ev` | digital instrument cluster / virtual cockpit | цифровая панель приборов | 数字仪表盘 / 虚拟座舱 | 0 | — | — | — |
| 55 | `diode@ev` | diode | диод | 二极管 | 0 | — | — | — |
| 56 | `direct_tpms_sensor@ev` | direct TPMS sensor (wheel-mounted) | датчик TPMS прямой (встроен в колесо) | 直接式胎压传感器（车轮安装） | 0 | — | — | — |
| 57 | `door_control_module@ev` | door control module / access control unit | блок управления доступом | 车门控制模块 / 门禁控制单元 | 0 | — | — | — |
| 58 | `dual_motor_controller@ev` | dual motor controller | контроллер двухмоторной системы | 双电机控制器 | 12 | — | — | — |
| 59 | `efb_battery@ev` | EFB battery (Enhanced Flooded Battery) | EFB-аккумулятор | EFB蓄电池（增强型富液电池） | 0 | — | — | — |
| 60 | `electric_motor@ev` | electric motor | электродвигатель / электромотор | 电动机 | 0 | — | — | — |
| 61 | `electric_vehicle_battery@ev` | electric vehicle battery | аккумулятор электромобиля | 电动车电池 | 0 | — | — | — |
| 62 | `electric_vehicle_supply_equipment@ev` | Electric Vehicle Supply Equipment | зарядная станция (EVSE) | 电动汽车供电设备 | 0 | — | — | — |
| 63 | `electrical_connector@ev` | electrical connector / plug | разъём электрический | 电气接插件 / 插头 | 0 | — | — | — |
| 64 | `elektromotor_peredniy@ev` | Electric Motor | Электромотор передний | 电动机 | 0 | — | — | — |
| 65 | `elektromotor_zadniy@ev` | Electric Motor | Электромотор задний | 电动机 | 0 | — | — | — |
| 66 | `engine_control_module@ev` | engine control module / powertrain control module | блок управления двигателем (ECM/PCM) | 发动机控制模块 / 动力总成控制模块 | 0 | — | — | — |
| 67 | `field_winding@ev` | field winding (starter) | обмотка возбуждения стартера | 励磁绕组（起动机） | 0 | — | — | — |
| 68 | `flow_battery@ev` | flow battery | проточная батарея | 液流电池 | 0 | — | — | — |
| 69 | `front_electric_motor@ev` | front electric motor | передний электромотор | 前电机 | 3 | 1 | 1 | P0A1A |
| 70 | `front_headlight_bulb@ev` | front headlight bulb | лампа фары (перед.) | 前大灯灯泡 | 0 | — | — | — |
| 71 | `fuse@ev` | fuse | предохранитель | 保险丝 | 42 | — | — | — |
| 72 | `fuse_box@ev` | fuse box / fuse panel / relay box / PDU | блок предохранителей и реле | 保险丝盒 / 继电器盒 / 配电单元 | 0 | — | — | — |
| 73 | `fusible_link@ev` | fusible link | плавкая вставка | 熔断丝 | 0 | — | — | — |
| 74 | `gateway_module@ev` | gateway module / central gateway | шлюзовой блок | 网关模块 / 中央网关 | 0 | — | — | — |
| 75 | `gb@ev` | GB/T 20234.3 — DC fast charging (China) | GB/T 20234.3 — быстрая зарядка DC (Китай) | GB/T 20234.3 — 直流快充接口（中国标准） | 0 | — | — | — |
| 76 | `ground@ev` | ground / body earth / chassis ground | масса (заземление кузова) | 搭铁 / 车身接地 / 底盘接地 | 0 | — | — | — |
| 77 | `hazard_lights@ev` | hazard lights / emergency flashers | аварийная сигнализация | 危险警告灯 / 双闪灯 | 0 | — | — | — |
| 78 | `headlight_bulb@ev` | headlight bulb | лампа фары | 大灯灯泡 | 0 | — | — | — |
| 79 | `heat_pump@ev` | heat pump (EV climate system) | тепловой насос (климат EV) | 热泵 | 0 | — | — | — |
| 80 | `heated_mirrors@ev` | heated mirrors | подогрев зеркал | 加热后视镜 | 0 | — | — | — |
| 81 | `high_voltage_wiring@ev` | high voltage wiring / HV harness (EV/hybrid) | проводка высокого напряжения (EV/HEV) | 高压线束（电动/混合动力车） | 0 | 2 | 2 | P0A09, P0A7F, P0A80, P0AA6, P3000 |
| 82 | `highmounted_stop_lamp@ev` | high-mounted stop lamp / CHMSL | третий стоп-сигнал (центральный) | 高位刹车灯 / CHMSL | 0 | — | — | — |
| 83 | `highvoltage_harness@ev` | high-voltage harness | высоковольтный жгут проводов | 高压线束 | 39 | — | — | — |
| 84 | `highvoltage_interlock_loop@ev` | High-Voltage Interlock Loop | петля блокировки высокого напряжения | 高压互锁回路 | 0 | — | — | — |
| 85 | `hv_charging_distribution_assembly@ev` | HV charging distribution assembly | ВВ зарядно-распределительный блок | 高压充配电总成 | 1 | — | — | — |
| 86 | `hv_contactor@ev` | HV contactor (main relay) | контактор ВН (главное реле) | 高压接触器 | 0 | — | — | — |
| 87 | `hv_fuse_box@ev` | HV fuse box | предохранительный блок ВН | 高压保险丝盒 | 0 | — | — | — |
| 88 | `hv_interlock@ev` | HV interlock | блокировка ВВ-цепи (интерлок) | 高压互锁 | 0 | — | — | — |
| 89 | `hv_service_disconnect@ev` | HV service disconnect / manual service disconnect | разъединитель высоковольтной сети (сервисный разъём) | 高压维修断开器 / 手动维修断开器 | 0 | — | — | — |
| 90 | `hybrid_module@ev` | hybrid module (P0 mild hybrid, P2 full hybrid...) | гибридный модуль (P0 / P1 / P2...) | 混合动力模块（P0轻混、P2全混……） | 0 | — | — | — |
| 91 | `idler_pulley@ev` | idler pulley | обводной ролик | 惰轮 / 导向轮 | 0 | — | — | — |
| 92 | `induction_motor@ev` | induction motor / asynchronous motor | асинхронный (индукционный) мотор | 感应电机 / 异步电机 | 0 | — | — | — |
| 93 | `instrument_cluster@ev` | instrument cluster / gauge cluster / instrument panel | комбинация приборов | 仪表盘 | 0 | — | — | — |
| 94 | `insulated_gate_bipolar_transistor@ev` | Insulated Gate Bipolar Transistor | биполярный транзистор с изолированным затвором (IGBT) | 绝缘栅双极型晶体管 (IGBT) | 0 | — | — | — |
| 95 | `insulation_monitoring_device@ev` | Insulation Monitoring Device | устройство контроля изоляции (IMD) | 绝缘监测装置 (IMD) | 0 | — | — | — |
| 96 | `integrated_startergenerator@ev` | integrated starter-generator / belt-integrated starter-generator | стартер-генератор интегрированный / стартер-генератор с ременным приводом | 集成式起动发电机 / 皮带集成式起动发电机 | 0 | — | — | — |
| 97 | `inverter@ev` | inverter | инвертор | 逆变器 | 0 | — | — | — |
| 98 | `inverter_ann@ev` | traction inverter | тяговый инвертор | 驱动逆变器 | 0 | — | — | — |
| 99 | `isolation_monitoring@ev` | isolation monitoring | контроль изоляции ВВ-системы | 绝缘监测 | 0 | — | — | — |
| 100 | `key_transponder@ev` | key transponder / RFID chip key | транспондер ключа | 钥匙应答器 / RFID芯片钥匙 | 0 | — | — | — |
| 101 | `keyless_entry_system@ev` | keyless entry system | система безключевого доступа | 无钥匙进入系统 | 0 | — | — | — |
| 102 | `laser_headlights@ev` | laser headlights | лазерные фары | 激光大灯 | 0 | — | — | — |
| 103 | `leadacid_battery@ev` | lead–acid battery | свинцово-кислотный аккумулятор | 铅酸蓄电池 | 0 | — | — | — |
| 104 | `led_headlights@ev` | LED headlights (Light Emitting Diode) | светодиодные фары (LED) | LED大灯（发光二极管） | 0 | — | — | — |
| 105 | `left_headlight@ev` | left headlight | фара (лев.) | 左大灯 | 0 | — | — | — |
| 106 | `left_taillight@ev` | left taillight | задний фонарь (лев.) | 左尾灯 | 0 | — | — | — |
| 107 | `light_sensor@ev` | light sensor / auto lights | датчик света / автоматический свет | 光线传感器 / 自动照明 | 0 | — | — | — |
| 108 | `liquid_cooling_plate@ev` | liquid cooling plate | жидкостная охлаждающая пластина | 液冷板 | 0 | — | — | — |
| 109 | `liquidcooled_battery@ev` | liquid-cooled battery | охлаждение батареи жидкостное | 液冷电池 | 0 | — | — | — |
| 110 | `lithium_battery@ev` | lithium battery | литиевый элемент питания | 锂电池 | 6 | — | — | — |
| 111 | `lithium_iron_phosphate_battery@ev` | lithium iron phosphate battery | литий-железо-фосфатный аккумулятор | 磷酸铁锂电池 | 1 | — | — | — |
| 112 | `lithium_polymer_battery@ev` | lithium polymer battery | литий-полимерный аккумулятор | 锂聚合物电池 | 0 | — | — | — |
| 113 | `lithium_titanate_battery@ev` | lithium titanate battery | литий-титанатный аккумулятор | 钛酸锂电池 | 0 | — | — | — |
| 114 | `lithiumsulfur_battery@ev` | lithium–sulfur battery | литий-серный аккумулятор | 锂硫电池 | 0 | — | — | — |
| 115 | `lowfrequency_antenna@ev` | low-frequency antenna (in-car) | низкочастотная антенна (салонная) | 车内低频天线 | 3 | — | — | — |
| 116 | `lyuchok_zaryadki@ev` | Charging Port R — Panel | Лючок зарядки#2 — Панель | 充电口右 — 面板 | 0 | — | — | — |
| 117 | `main_contactor@ev` | main contactor | главный контактор | 主接触器 | 0 | — | — | — |
| 118 | `manual_service_disconnect@ev` | manual service disconnect (MSD) | ручной разъём обслуживания (MSD) | 手动维修断电器 (MSD) | 0 | — | — | — |
| 119 | `matrix_led_headlights@ev` | matrix LED headlights / adaptive LED | матричные фары / адаптивная оптика | 矩阵LED大灯 / 自适应LED大灯 | 0 | — | — | — |
| 120 | `molten_salt_battery@ev` | molten salt battery | батарея на расплавах солей | 熔盐电池 | 0 | — | — | — |
| 121 | `motor_control_unit@ev` | Motor Control Unit | блок управления электродвигателем (MCU) | 电机控制器 (MCU) | 0 | — | — | — |
| 122 | `motor_controller@ev` | motor controller | контроллер электромотора | 电机控制器 | 12 | — | — | — |
| 123 | `nacs_north_american_charging_standard@ev` | NACS (North American Charging Standard / SAE J3400) | NACS (Северо-американский стандарт зарядки / SAE J3400) | NACS（北美充电标准 / SAE J3400） | 0 | — | — | — |
| 124 | `negative_terminal@ev` | negative terminal (-) / ground terminal | отрицательный вывод (-) / масса | 负极端子（-）/ 搭铁端子 | 0 | — | — | — |
| 125 | `nickelcadmium_battery@ev` | nickel–cadmium battery | никель-кадмиевый аккумулятор | 镍镉电池 | 0 | — | — | — |
| 126 | `nickelhydrogen_battery@ev` | nickel–hydrogen battery | никель-водородный аккумулятор | 镍氢气电池 | 0 | — | — | — |
| 127 | `nickeliron_battery@ev` | nickel–iron battery | железо-никелевый аккумулятор | 镍铁电池 | 0 | — | — | — |
| 128 | `nickelmetal_hydride_battery@ev` | nickel–metal hydride battery | никель-металл-гидридный аккумулятор | 镍氢电池 | 1 | — | — | — |
| 129 | `nickelzinc_battery@ev` | nickel–zinc battery | никель-цинковый аккумулятор | 镍锌电池 | 0 | — | — | — |
| 130 | `obc_charger@ev` | on-board charger (OBC) | бортовое зарядное устройство (OBC) | 车载充电器 | 0 | — | — | — |
| 131 | `onboard_charger@ev` | on-board charger (OBC) | бортовое зарядное устройство (OBC) | 车载充电机 | 0 | — | — | — |
| 132 | `permanent_magnet_motor@ev` | permanent magnet motor (PMSM) | синхронный электродвигатель на постоянных магнитах (PMSM) | 永磁同步电机（PMSM） | 0 | — | — | — |
| 133 | `permanent_magnet_synchronous_motor@ev` | Permanent Magnet Synchronous Motor | синхронный электродвигатель с постоянными магнитами (СДПМ) | 永磁同步电机 (PMSM) | 0 | — | — | — |
| 134 | `pmsm@ev` | PMSM (permanent magnet synchronous motor) | синхронный двигатель с постоянными магнитами (СДПМ) | 永磁同步电机 (PMSM) | 0 | — | — | — |
| 135 | `points@ev` | points | контакты прерывателя | 白金触点 | 0 | — | — | — |
| 136 | `positive_terminal@ev` | positive terminal (+) | положительный вывод (+) | 正极端子（+） | 0 | — | — | — |
| 137 | `pouch_cell@ev` | pouch cell | пакетный (мешочный) элемент | 软包电芯 | 0 | — | — | — |
| 138 | `power_control_unit@ev` | power control unit | блок управления мощностью (PCU) | 功率控制单元 | 0 | — | — | — |
| 139 | `power_distribution_unit@ev` | power distribution unit | блок распределения питания (PDU) | 电源分配单元 | 0 | — | — | — |
| 140 | `power_window@ev` | power window / electric window | стеклоподъёмник электрический | 电动车窗 | 0 | — | — | — |
| 141 | `powerfolding_mirrors@ev` | power-folding mirrors | электроскладывание зеркал | 电动折叠后视镜 | 0 | — | — | — |
| 142 | `precharge_circuit@ev` | pre-charge circuit | цепь предзаряда | 预充电回路 | 0 | — | — | — |
| 143 | `precharge_relay@ev` | precharge relay / contactor | реле предзаряда / контактор | 预充继电器/接触器 | 0 | — | — | — |
| 144 | `prismatic_cell@ev` | prismatic cell | призматический элемент | 方形电芯 | 0 | — | — | — |
| 145 | `provodka_batarei@ev` | Battery Wiring R | Проводка батареи | 电池线束右 | 0 | — | — | — |
| 146 | `provodka_emotora@ev` | E-Motor Wiring R | Проводка э/мотора | 电机线束右 | 0 | — | — | — |
| 147 | `pushbutton_start@ev` | push-button start / Start/Stop button | кнопка Start/Stop | 一键启动按钮 / 启停按钮 | 0 | — | — | — |
| 148 | `range_extender@ev` | range extender (REX) | генератор-удлинитель пробега (REX) | 增程器 | 238 | — | — | — |
| 149 | `rear_electric_drive_assembly@ev` | rear electric drive assembly | задний электропривод в сборе | 后电驱动总成 | 1 | — | — | — |
| 150 | `rear_electric_motor@ev` | rear electric motor | задний электромотор | 后电机 | 18 | 1 | 1 | P0A1A |
| 151 | `rear_headlight_bulb@ev` | rear headlight bulb | лампа фары (зад.) | 后大灯灯泡 | 0 | — | — | — |
| 152 | `rechargeable_battery@ev` | rechargeable battery | электрический аккумулятор | 可充电电池 | 0 | — | — | — |
| 153 | `rectifier@ev` | rectifier | выпрямитель | 整流器 | 0 | — | — | — |
| 154 | `rectifier_bridge@ev` | rectifier bridge / diode bridge | диодный мост генератора | 整流桥 / 二极管桥 | 0 | — | — | — |
| 155 | `regulator@ev` | regulator | регулятор | 调节器 | 1 | — | — | — |
| 156 | `relay@ev` | relay | реле | 继电器 | 12 | — | — | — |
| 157 | `right_headlight@ev` | right headlight | фара (прав.) | 右大灯 | 0 | — | — | — |
| 158 | `right_taillight@ev` | right taillight | задний фонарь (прав.) | 右尾灯 | 0 | — | — | — |
| 159 | `rotor@ev` | rotor | ротор | 转子 | 1 | — | — | — |
| 160 | `service_disconnect@ev` | service disconnect | сервисный разъединитель ВВБ | 维修断开装置 | 0 | — | — | — |
| 161 | `silicon_carbide_mosfet@ev` | Silicon Carbide MOSFET | siC-транзистор (карбид кремния) | 碳化硅 MOSFET (SiC) | 0 | — | — | — |
| 162 | `silverzinc_battery@ev` | silver-zinc battery | серебряно-цинковый аккумулятор | 银锌电池 | 0 | — | — | — |
| 163 | `smart_key@ev` | smart key / proximity key / keyless entry fob | смарт-ключ / ключ с дистанционным управлением | 智能钥匙 | 0 | — | — | — |
| 164 | `sodiumion_battery@ev` | sodium-ion battery | натрий-ионный аккумулятор | 钠离子电池 | 0 | — | — | — |
| 165 | `sodiumsulfur_battery@ev` | sodium–sulfur battery | натриево-серный аккумулятор | 钠硫电池 | 0 | — | — | — |
| 166 | `solenoid@ev` | solenoid / starter solenoid | втягивающее реле стартера | 起动机电磁开关 | 0 | — | — | — |
| 167 | `starter_brushes@ev` | starter brushes | щётки стартера | 起动机电刷 | 0 | — | — | — |
| 168 | `starter_drive@ev` | starter drive / Bendix drive | бендикс стартера / механизм привода | 起动机驱动器 / 本迪克斯驱动器 | 0 | — | — | — |
| 169 | `starter_motor@ev` | starter motor | стартер | 起动机 | 2 | — | — | — |
| 170 | `starter_relay@ev` | starter relay | реле стартера | 起动机继电器 | 0 | — | — | — |
| 171 | `startergenerator_isg@ev` | starter-generator (ISG / BSG) | стартер-генератор (ISG / BSG) | 启动发电一体机 (ISG/BSG) | 0 | — | — | — |
| 172 | `stator@ev` | stator | статор | 定子 | 2 | — | — | — |
| 173 | `terminal@ev` | terminal / connector pin | контакт разъёма | 端子 / 连接器插针 | 0 | — | — | — |
| 174 | `tesla_proprietary_connector@ev` | Tesla proprietary connector / NACS | разъём Tesla | 特斯拉专用充电接口 / NACS | 0 | — | — | — |
| 175 | `traction_battery@ev` | traction battery / HV battery | тяговая батарея (ВВБ) | 动力电池 | 0 | — | — | — |
| 176 | `traction_battery_hv_battery@ev` | traction battery / HV battery | тяговая батарея (ВВБ) | 动力电池 | 245 | 1 | 1 | P0A7F, P0A80, P0AA6, P3000 |
| 177 | `traction_motor@ev` | traction motor / e-motor | тяговый электродвигатель | 牵引电机 / 电动机 | 0 | — | — | — |
| 178 | `turn_signal@ev` | turn signal / indicator / blinker | указатель поворота | 转向灯 / 方向指示灯 | 7 | — | — | — |
| 179 | `type_1_connector_ac_singlephase@ev` | Type 1 connector (SAE J1772) — AC single-phase | разъём Type 1 (SAE J1772) — AC однофазный | type 1接口（SAE J1772）— 单相交流 | 0 | — | — | — |
| 180 | `type_2_charging_connector@ev` | Type 2 charging connector (Mennekes) | разъём зарядки Type 2 | type 2充电接口（门内克斯） | 0 | — | — | — |
| 181 | `type_2_connector_ac_single@ev` | Type 2 connector (Mennekes) — AC single/three-phase | разъём Type 2 (Mennekes) — AC одно/трёхфазный | type 2接口（Mennekes）— 单/三相交流 | 0 | — | — | — |
| 182 | `ultrafast_charger@ev` | ultra-fast charger / HPC | сверхбыстрое зарядное устройство (HPC) | 超快充电桩 (HPC) | 0 | — | — | — |
| 183 | `valveregulated_leadacid_battery@ev` | valve-regulated lead-acid battery | свинцово-кислотный аккумулятор с клапанным регулированием (VRLA) | 阀控密封铅酸蓄电池 | 0 | — | — | — |
| 184 | `voltage_regulator@ev` | voltage regulator / alternator regulator | реле-регулятор напряжения | 电压调节器 | 0 | — | — | — |
| 185 | `window_regulator_motor@ev` | window regulator motor | мотор стеклоподъёмника | 车窗调节器电机 | 0 | — | — | — |
| 186 | `wiring_harness@ev` | wiring harness | жгут проводов | 线束 | 42 | — | — | — |
| 187 | `xenon@ev` | xenon / HID headlights (High Intensity Discharge) | ксеноновые фары (HID) | 氙气大灯 / 高强度放电大灯（HID） | 0 | — | — | — |
| 188 | `zebra_battery@ev` | ZEBRA battery | никель-солевой аккумулятор | 钠氯化镍电池 | 0 | — | — | — |
| 189 | `zincair_battery@ev` | zinc–air battery | воздушно-цинковый элемент | 锌空气电池 | 0 | — | — | — |
| 190 | `zincbromine_battery@ev` | zinc–bromine battery | цинк-бромный аккумулятор | 锌溴液流电池 | 0 | — | — | — |
| 191 | `zinccarbon_battery@ev` | zinc–carbon battery | угольно-цинковый элемент | 锌碳电池 | 0 | — | — | — |

## 5. BRAKES — Рулевое управление и тормозная система (152 компонентов)

*Рулевая колонка, рейка, ГУР/ЭУР, суппорты, диски, барабаны, колодки, АБС/ESC, ручной тормоз, тормозные магистрали*

**Подсистемы:** steering_column, steering_rack, power_steering, disc_brakes, drum_brakes, brake_hydraulics, abs_esc, parking_brake

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `abs@brakes` | ABS (anti-lock braking system) | антиблокировочная система (АБС) | 防抱死制动系统 (ABS) | 0 | — | — | — |
| 2 | `abs_esc_module@brakes` | ABS/ESC module | блок ABS/ESC | ABS/ESC模块 | 0 | — | — | — |
| 3 | `abs_hydraulic_unit@brakes` | ABS hydraulic unit / ABS modulator / HCU | гидравлический блок ABS | ABS液压单元 / ABS调节器 / HCU | 0 | — | — | — |
| 4 | `abs_module@brakes` | ABS module | блок ABS | ABS模块 | 0 | — | — | — |
| 5 | `abs_tone_ring@brakes` | ABS tone ring / reluctor ring | зубчатое колесо импульсного датчика | ABS齿圈 / 磁阻环 | 0 | — | — | — |
| 6 | `abs_wheel_speed_sensor@brakes` | ABS wheel speed sensor / tone ring sensor | датчик скорости вращения колеса (ABS) | ABS车轮速度传感器 / 齿圈传感器 | 0 | — | — | — |
| 7 | `active_steering@brakes` | active steering / variable steering ratio | активное рулевое управление | 主动转向 / 可变转向比 | 0 | — | — | — |
| 8 | `adjustable_steering_column@brakes` | adjustable steering column | регулируемая рулевая колонка | 可调节转向柱 | 0 | — | — | — |
| 9 | `adjuster@brakes` | adjuster / auto-adjuster / star wheel adjuster | регулятор зазора / автоматический регулятор / звёздчатый регулятор | 调节器 / 自动调节器 / 星形轮调节器 | 0 | — | — | — |
| 10 | `auto_hold@brakes` | auto hold / hill hold assist | автоматическое удержание на уклоне (Auto Hold) | 自动保持 / 坡道保持辅助 | 0 | — | — | — |
| 11 | `bleed_nipple@brakes` | bleed nipple | штуцер прокачки тормозов | 放气螺栓 | 0 | — | — | — |
| 12 | `brake_assist_ba@brakes` | brake assist (BA/EBA) | система экстренного торможения (BA) | 制动辅助 (BA) | 0 | — | — | — |
| 13 | `brake_assist_system@brakes` | brake assist system / emergency brake assist | усилитель экстренного торможения (BA/BAS) | 制动辅助系统 / 紧急制动辅助 | 0 | — | — | — |
| 14 | `brake_booster@brakes` | brake booster / servo | вакуумный усилитель тормозов | 制动助力器 | 0 | — | — | — |
| 15 | `brake_booster_vacuum_sensor@brakes` | brake booster vacuum sensor | датчик вакуума усилителя тормозов | 制动助力器真空传感器 | 0 | — | — | — |
| 16 | `brake_caliper@brakes` | brake caliper | тормозной суппорт | 制动卡钳 | 0 | 4 | 4 | C0035, C0036, C0037, C0038, C0040, C0041, C0042, C0043 |
| 17 | `brake_disc@brakes` | brake disc / rotor | тормозной диск | 制动盘 | 31 | — | — | — |
| 18 | `brake_disc_fl@brakes` | brake disc (FL) | тормозной диск (ПЛ) | 制动盘(左前) | 0 | — | — | — |
| 19 | `brake_disc_fr@brakes` | brake disc (FR) | тормозной диск (ПП) | 制动盘(右前) | 0 | — | — | — |
| 20 | `brake_disc_rl@brakes` | brake disc (RL) | тормозной диск (ЗЛ) | 制动盘(左后) | 0 | — | — | — |
| 21 | `brake_disc_rr@brakes` | brake disc (RR) | тормозной диск (ЗП) | 制动盘(右后) | 0 | — | — | — |
| 22 | `brake_drum@brakes` | brake drum | тормозной барабан | 制动鼓 | 0 | — | — | — |
| 23 | `brake_dust_shield@brakes` | brake dust shield | пыльник тормозного диска | 制动防尘罩 | 0 | — | — | — |
| 24 | `brake_fluid_reservoir@brakes` | brake fluid reservoir | бачок тормозной жидкости | 制动液储液罐 | 0 | — | — | — |
| 25 | `brake_hose@brakes` | brake hose / flexible brake hose | тормозной шланг | 制动软管 / 挠性制动软管 | 0 | — | — | — |
| 26 | `brake_line@brakes` | brake line / brake pipe | тормозная трубка | 制动管路 / 制动管道 | 0 | — | — | — |
| 27 | `brake_lining@brakes` | brake lining | тормозная накладка | 制动衬片 | 8 | — | — | — |
| 28 | `brake_master_cylinder@brakes` | brake master cylinder | главный тормозной цилиндр (ГТЦ) | 制动主缸 | 0 | — | — | — |
| 29 | `brake_pedal@brakes` | brake pedal | педаль тормоза | 制动踏板 | 423 | 1 | — | C0035, C0036, C0037, C0038 |
| 30 | `brake_pedal_switch@brakes` | brake pedal switch | датчик педали тормоза | 制动踏板开关 | 0 | — | — | — |
| 31 | `brake_pressure_proportioning_valve@brakes` | brake pressure proportioning valve / pressure regulator | регулятор тормозных сил (РТС) | 制动压力比例阀 / 压力调节器 | 0 | — | — | — |
| 32 | `brake_servo_vacuum_hose@brakes` | brake servo vacuum hose | вакуумный трубопровод усилителя | 制动伺服真空软管 | 0 | — | — | — |
| 33 | `brake_shoe@brakes` | brake shoe | тормозная колодка (барабан) | 制动蹄 | 0 | — | — | — |
| 34 | `brake_shoe_return_spring@brakes` | brake shoe return spring / shoe retract spring | стяжная пружина тормозных колодок | 制动蹄回位弹簧 / 制动蹄收缩弹簧 | 0 | — | — | — |
| 35 | `brake_shoes@brakes` | brake shoes | тормозные колодки барабанного тормоза | 制动蹄片 | 0 | — | — | — |
| 36 | `brake_system@brakes` | brake system | тормозная система | 制动系统 | 168 | — | — | — |
| 37 | `brake_wear_sensor@brakes` | brake wear sensor | датчик износа тормозных колодок | 制动磨损传感器 | 0 | — | — | — |
| 38 | `brakebywire@brakes` | brake-by-wire | электронное управление тормозами (brake-by-wire) | 线控制动 | 0 | — | — | — |
| 39 | `caliper@brakes` | caliper | суппорт | 制动卡钳 | 0 | — | — | — |
| 40 | `caliper_bracket@brakes` | caliper bracket | скоба суппорта | 卡钳支架 | 0 | — | — | — |
| 41 | `caliper_guide_pins@brakes` | caliper guide pins / slide pins | направляющие суппорта | 卡钳导向销 | 0 | — | — | — |
| 42 | `calliper_guide_pins@brakes` | calliper guide pins / slide pins / slide bolts | направляющие (пальцы) суппорта | 制动钳导向销 / 滑动销 / 滑动螺栓 | 0 | — | — | — |
| 43 | `calliper_piston@brakes` | calliper piston | поршень суппорта | 制动钳活塞 | 0 | — | — | — |
| 44 | `carbonceramic_brake_disc@brakes` | carbon-ceramic brake disc / PCCB disc | карбон-керамический тормозной диск | 碳陶瓷制动盘 / PCCB制动盘 | 0 | — | — | — |
| 45 | `ceramic_brake_pads@brakes` | ceramic brake pads | керамические тормозные колодки | 陶瓷制动片 | 0 | — | — | — |
| 46 | `column_switch@brakes` | column switch / combination switch | подрулевой переключатель | 组合开关 | 1 | 3 | — | C0500 |
| 47 | `cross_track_rod@brakes` | cross track rod / steering tie rod | поперечная рулевая тяга | 横向拉杆 / 转向横拉杆 | 0 | — | — | — |
| 48 | `drag_link@brakes` | drag link / centre link | продольная рулевая тяга | 纵向拉杆 / 中间连杆 | 0 | — | — | — |
| 49 | `drilled_brake_disc@brakes` | drilled brake disc | перфорированный тормозной диск | 打孔制动盘 | 0 | — | — | — |
| 50 | `drum_brake@brakes` | drum brake | барабанный тормоз | 鼓式制动 | 0 | — | — | — |
| 51 | `dust_boot@brakes` | dust boot / piston boot | пыльник поршня суппорта | 防尘罩 / 活塞防尘罩 | 0 | — | — | — |
| 52 | `ebd@brakes` | EBD (electronic brakeforce distribution) | система распределения тормозных усилий (EBD) | 电子制动力分配 (EBD) | 0 | — | — | — |
| 53 | `electric_vacuum_pump@brakes` | electric vacuum pump | электровакуумный насос | 电动真空泵 | 0 | — | — | — |
| 54 | `electrohydraulic_brake_booster@brakes` | electro-hydraulic brake booster / iBooster | электрогидравлический усилитель тормозов | 电液制动助力器 / iBooster | 0 | — | — | — |
| 55 | `electrohydraulic_power_steering@brakes` | electro-hydraulic power steering | электрогидроусилитель руля (ЭГУР) | 电液助力转向 | 0 | — | — | — |
| 56 | `electronic_brakeforce_distribution@brakes` | electronic brakeforce distribution | электронное распределение тормозных усилий (EBD) | 电子制动力分配 (EBD) | 0 | — | — | — |
| 57 | `epb@brakes` | EPB (electronic parking brake) | электрический стояночный тормоз (EPB) | 电子驻车制动 (EPB) | 0 | — | — | — |
| 58 | `epb_actuator@brakes` | EPB actuator / EPB caliper | актуатор электрического стояночного тормоза | 电动驻车制动执行器 / EPB制动钳 | 0 | — | — | — |
| 59 | `eps@brakes` | EPS (electric power steering) | электроусилитель руля (ЭУР) | 电动助力转向 (EPS) | 0 | — | — | — |
| 60 | `eps_motor@brakes` | EPS motor / steering assist motor | мотор ЭУР | 电动助力转向电机 / 转向辅助电机 | 0 | — | — | — |
| 61 | `esc@brakes` | ESC / ESP (electronic stability control) | электронная система стабилизации (ESC) | 电子稳定控制 (ESC) | 0 | — | — | — |
| 62 | `fixed_calliper@brakes` | fixed calliper | фиксированный суппорт | 固定式制动钳 | 0 | — | — | — |
| 63 | `front_abs_tone_ring@brakes` | front ABS tone ring | зубчатый венец ABS (перед.) | 前轮ABS齿圈 | 0 | — | — | — |
| 64 | `front_brake_light@brakes` | front brake light | стоп-сигнал (перед.) | 前制动灯 | 0 | — | — | — |
| 65 | `front_caliper_bracket@brakes` | front caliper bracket | скоба суппорта (перед.) | 前卡钳支架 | 0 | — | — | — |
| 66 | `front_left_brake_caliper@brakes` | front left brake caliper | тормозной суппорт (перед., лев.) | 前左制动卡钳 | 0 | — | — | — |
| 67 | `front_left_brake_disc@brakes` | front left brake disc | тормозной диск (перед., лев.) | 前左制动盘 | 0 | — | — | — |
| 68 | `front_left_brake_hose@brakes` | front left brake hose | тормозной шланг (перед., лев.) | 前左制动软管 | 0 | — | — | — |
| 69 | `front_left_brake_line@brakes` | front left brake line | тормозная трубка (перед., лев.) | 左前制动管路 | 0 | — | — | — |
| 70 | `front_left_brake_pad@brakes` | front left brake pad | тормозная колодка (перед., лев.) | 前左制动片 | 0 | — | — | — |
| 71 | `front_parking_brake_cable@brakes` | front parking brake cable | трос стояночного тормоза (перед.) | 前驻车制动拉索 | 0 | — | — | — |
| 72 | `front_right_brake_caliper@brakes` | front right brake caliper | тормозной суппорт (перед., прав.) | 前右制动卡钳 | 0 | — | — | — |
| 73 | `front_right_brake_disc@brakes` | front right brake disc | тормозной диск (перед., прав.) | 前右制动盘 | 0 | — | — | — |
| 74 | `front_right_brake_hose@brakes` | front right brake hose | тормозной шланг (перед., прав.) | 前右制动软管 | 0 | — | — | — |
| 75 | `front_right_brake_line@brakes` | front right brake line | тормозная трубка (перед., прав.) | 右前制动管路 | 0 | — | — | — |
| 76 | `front_right_brake_pad@brakes` | front right brake pad | тормозная колодка (перед., прав.) | 前右制动片 | 0 | — | — | — |
| 77 | `front_steering_axle@brakes` | front steering axle | управляемый передний мост | 前转向车轴 | 0 | — | — | — |
| 78 | `handbrake_cable@brakes` | handbrake cable / parking brake cable | трос стояночного тормоза | 手刹拉索 / 驻车制动拉索 | 0 | — | — | — |
| 79 | `handbrake_lever@brakes` | handbrake lever | рычаг стояночного тормоза | 手刹拉杆 | 0 | — | — | — |
| 80 | `handbrake_ratchet_mechanism@brakes` | handbrake ratchet mechanism | механизм трещотки стояночного тормоза | 手刹棘轮机构 | 0 | — | — | — |
| 81 | `hill_descent_control@brakes` | hill descent control (HDC) | система спуска с горы (HDC) | 陡坡缓降 (HDC) | 0 | — | — | — |
| 82 | `hill_start_assist@brakes` | hill start assist (HSA) | система помощи при подъёме (HSA) | 上坡辅助 (HSA) | 0 | — | — | — |
| 83 | `hydraulic_power_steering@brakes` | hydraulic power steering (HPS) | гидроусилитель руля (ГУР) | 液压助力转向 | 0 | — | — | — |
| 84 | `ibooster@brakes` | iBooster / integrated power brake | электромеханический усилитель тормозов (iBooster) | 集成动力制动 (iBooster) | 0 | — | — | — |
| 85 | `ibooster_ann@brakes` | iBooster (brake booster) | электроусилитель тормозов (iBooster) | iBooster制动助力器 | 0 | — | — | — |
| 86 | `idler_arm@brakes` | idler arm | маятниковый рычаг | 惰臂 | 0 | — | — | — |
| 87 | `indikatory_priborov_2@brakes` | Instrument Indicators — Инд. ABS | Индикаторы приборов 2#2 — Инд. ABS | 仪表指示器 — Инд. ABS | 0 | — | — | — |
| 88 | `instrument_cluster@brakes` | instrument cluster | щиток приборов | 组合仪表 | 0 | 1 | — | B1450, B1460 |
| 89 | `intermediate_shaft@brakes` | intermediate shaft | промежуточный вал рулевого управления | 转向中间轴 | 1 | — | — | — |
| 90 | `manifold_absolute_pressure_sensor@brakes` | manifold absolute pressure sensor (MAP) | датчик MAP | 进气歧管绝对压力传感器 (MAP) | 0 | — | — | — |
| 91 | `multipiston_calliper@brakes` | multi-piston calliper | многопоршневой суппорт | 多活塞制动钳 | 0 | — | — | — |
| 92 | `nonasbestos_organic_brake_pads@brakes` | non-asbestos organic (NAO) brake pads | безасбестовые органические колодки | 无石棉有机制动片 (NAO) | 0 | — | — | — |
| 93 | `outer_tie_rod_end@brakes` | outer tie rod end / tie rod end | наружный наконечник рулевой тяги | 横拉杆球头 | 0 | — | — | — |
| 94 | `paddle_shifter@brakes` | paddle shifter | подрулевой лепесток | 换挡拨片 | 0 | 2 | — | C0500 |
| 95 | `parking_brake@brakes` | parking brake / handbrake / emergency brake | стояночный тормоз / ручной тормоз | 驻车制动器 / 手刹 / 紧急制动器 | 0 | — | — | — |
| 96 | `performance_brake_pad@brakes` | performance brake pad / race pad | спортивная тормозная колодка | 高性能制动片 / 赛车制动片 | 0 | — | — | — |
| 97 | `piston_seal@brakes` | piston seal / calliper piston seal | уплотнительное кольцо поршня суппорта | 活塞密封圈 / 制动钳活塞密封圈 | 0 | — | — | — |
| 98 | `pitman_arm@brakes` | pitman arm | сошка рулевого управления | 转向摇臂 | 0 | — | — | — |
| 99 | `podrulevoy_lepestok_l@brakes` | Paddle Shifter R | Подрулевой лепесток Л | 换挡拨片右 | 0 | — | — | — |
| 100 | `podrulevoy_lepestok_p@brakes` | Paddle Shifter R | Подрулевой лепесток П | 换挡拨片右 | 0 | — | — | — |
| 101 | `power_steering@brakes` | power steering | усилитель рулевого управления | 助力转向 | 12 | — | — | — |
| 102 | `power_steering_highpressure_hose@brakes` | power steering high-pressure hose | шланг гидроусилителя высокого давления | 动力转向高压软管 | 0 | — | — | — |
| 103 | `power_steering_pump@brakes` | power steering pump | насос гидроусилителя | 助力转向泵 | 0 | — | — | — |
| 104 | `power_steering_reservoir@brakes` | power steering reservoir | бачок ГУР | 助力转向油壶 | 0 | — | — | — |
| 105 | `power_steering_return_hose@brakes` | power steering return hose | шланг гидроусилителя низкого давления | 动力转向回油软管 | 0 | — | — | — |
| 106 | `proportioning_valve@brakes` | proportioning valve | пропорциональный клапан тормозов | 比例阀 | 0 | — | — | — |
| 107 | `rack@brakes` | rack / steering rack bar | зубчатая рейка | 齿条 / 转向齿条杆 | 0 | — | — | — |
| 108 | `rack_boot@brakes` | rack boot / steering rack gaiter / bellows | кожух рулевой рейки / пыльник рейки | 转向齿条防尘罩 / 转向齿条护套 / 波纹管 | 0 | — | — | — |
| 109 | `rack_pinion@brakes` | rack pinion / steering pinion | шестерня рулевой рейки | 齿条小齿轮 / 转向小齿轮 | 0 | — | — | — |
| 110 | `rear_abs_tone_ring@brakes` | rear ABS tone ring | зубчатый венец ABS (зад.) | 后轮ABS齿圈 | 0 | — | — | — |
| 111 | `rear_brake_light@brakes` | rear brake light | стоп-сигнал (зад.) | 后制动灯 | 0 | — | — | — |
| 112 | `rear_caliper_bracket@brakes` | rear caliper bracket | скоба суппорта (зад.) | 后卡钳支架 | 0 | — | — | — |
| 113 | `rear_left_brake_caliper@brakes` | rear left brake caliper | тормозной суппорт (зад., лев.) | 后左制动卡钳 | 0 | — | — | — |
| 114 | `rear_left_brake_disc@brakes` | rear left brake disc | тормозной диск (зад., лев.) | 后左制动盘 | 0 | — | — | — |
| 115 | `rear_left_brake_hose@brakes` | rear left brake hose | тормозной шланг (зад., лев.) | 后左制动软管 | 0 | — | — | — |
| 116 | `rear_left_brake_line@brakes` | rear left brake line | тормозная трубка (зад., лев.) | 左后制动管路 | 0 | — | — | — |
| 117 | `rear_left_brake_pad@brakes` | rear left brake pad | тормозная колодка (зад., лев.) | 后左制动片 | 0 | — | — | — |
| 118 | `rear_parking_brake_cable@brakes` | rear parking brake cable | трос стояночного тормоза (зад.) | 后驻车制动拉索 | 0 | — | — | — |
| 119 | `rear_right_brake_caliper@brakes` | rear right brake caliper | тормозной суппорт (зад., прав.) | 后右制动卡钳 | 0 | — | — | — |
| 120 | `rear_right_brake_disc@brakes` | rear right brake disc | тормозной диск (зад., прав.) | 后右制动盘 | 0 | — | — | — |
| 121 | `rear_right_brake_hose@brakes` | rear right brake hose | тормозной шланг (зад., прав.) | 后右制动软管 | 0 | — | — | — |
| 122 | `rear_right_brake_line@brakes` | rear right brake line | тормозная трубка (зад., прав.) | 右后制动管路 | 0 | — | — | — |
| 123 | `rear_right_brake_pad@brakes` | rear right brake pad | тормозная колодка (зад., прав.) | 后右制动片 | 0 | — | — | — |
| 124 | `rear_wheel_steering@brakes` | rear wheel steering / rear-wheel steering | управляемый задний мост | 后轮转向 | 0 | — | — | — |
| 125 | `semimetallic@brakes` | semi-metallic / metallic brake pads | полуметаллические / металлические тормозные колодки | 半金属 / 金属制动片 | 0 | — | — | — |
| 126 | `slave_cylinder@brakes` | slave cylinder | рабочий тормозной цилиндр | 制动分泵 | 0 | — | — | — |
| 127 | `sliding_calliper@brakes` | sliding calliper / floating calliper | плавающий суппорт | 滑动式制动钳 / 浮动式制动钳 | 0 | — | — | — |
| 128 | `slotted_brake_rotor@brakes` | slotted brake rotor | насечённый тормозной диск | 开槽制动盘 | 0 | — | — | — |
| 129 | `steering_angle_sensor@brakes` | steering angle sensor | датчик угла поворота руля | 转向角传感器 | 0 | — | — | — |
| 130 | `steering_box@brakes` | Steering Gear | рулевой механизм (редуктор) | 转向机构 | 0 | 1 | 1 | C0500 |
| 131 | `steering_column@brakes` | steering column / steering shaft | рулевая колонка / рулевой вал | 转向柱 / 转向轴 | 0 | — | — | — |
| 132 | `steering_damper@brakes` | steering damper | рулевой демпфер | 转向阻尼器 | 0 | — | — | — |
| 133 | `steering_gearbox@brakes` | steering gearbox / recirculating ball gearbox | рулевой редуктор | 转向器 / 循环球式转向器 | 0 | — | — | — |
| 134 | `steering_rack@brakes` | steering rack / rack and pinion | рулевая рейка | 转向齿条 | 0 | — | — | — |
| 135 | `steering_rack_boot@brakes` | steering rack boot / gaiter | пыльник рулевой рейки | 转向机防尘套 | 0 | — | — | — |
| 136 | `steering_system@brakes` | steering system | рулевое управление | 转向系统 | 27 | — | — | — |
| 137 | `steering_torque_sensor@brakes` | steering torque sensor | датчик крутящего момента на руле | 转向力矩传感器 | 0 | — | — | — |
| 138 | `steering_universal_joint@brakes` | steering universal joint / intermediate shaft U-joint | кардан рулевого вала | 转向万向节 / 中间轴万向节 | 0 | — | — | — |
| 139 | `steering_wheel@brakes` | steering wheel | рулевое колесо / руль | 方向盘 | 0 | — | 1 | C0500 |
| 140 | `steering_wheel_spoke@brakes` | steering wheel spoke | спица рулевого колеса | 转向盘辐条 | 0 | — | — | — |
| 141 | `tcs@brakes` | TCS (traction control system) | антипробуксовочная система (TCS) | 牵引力控制系统 (TCS) | 0 | — | — | — |
| 142 | `tie_rod@brakes` | tie-rod | рулевая тяга | 转向横拉杆 | 0 | 4 | 2 | C0500 |
| 143 | `tie_rod_adjusting_sleeve@brakes` | tie rod adjusting sleeve | регулировочная муфта рулевой тяги | 横拉杆调节套管 | 0 | — | — | — |
| 144 | `tierod@brakes` | Tie Rod | Рулевая тяга З (шир.) | 转向拉杆 | 1 | — | — | — |
| 145 | `tormoz_pl@brakes` | Brake FL | Тормоз ПЛ | 制动器左前 | 0 | — | — | — |
| 146 | `tormoz_pp@brakes` | Brake FR | Тормоз ПП | 制动器右前 | 0 | — | — | — |
| 147 | `tormoz_zl@brakes` | Brake RL | Тормоз ЗЛ | 制动器左后 | 0 | — | — | — |
| 148 | `tormoz_zp@brakes` | Brake RR | Тормоз ЗП | 制动器右后 | 0 | — | — | — |
| 149 | `track_rod_end@brakes` | track rod end | наконечник рулевой тяги | 横拉杆端头 | 0 | — | — | — |
| 150 | `upper_steering_shaft@brakes` | upper steering shaft | верхняя часть рулевого вала | 上转向轴 | 0 | — | — | — |
| 151 | `ventilated_disc@brakes` | ventilated disc | вентилируемый тормозной диск | 通风制动盘 | 0 | — | — | — |
| 152 | `wheel_cylinder@brakes` | wheel cylinder | рабочий цилиндр тормоза | 轮缸 | 0 | — | — | — |

## 6. SENSORS — Датчики и системы помощи водителю (ADAS) (113 компонентов)

*Камеры, радары, LiDAR, ультразвуковые датчики, IMU, GPS, подушки безопасности, ремни, датчики удара, определение пассажиров*

**Подсистемы:** cameras, radar, lidar, ultrasonic, imu_gps, airbags_srs, seatbelts

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `360degree_camera@sensors` | 360-degree camera | камера 360° | 360度全景摄像头 | 0 | — | — | — |
| 2 | `77ghz_mmwave_radar@sensors` | 77GHz mmWave radar | 77 ГГц миллиметровый радар | 77GHz毫米波雷达 | 0 | — | — | — |
| 3 | `abs_antilock_braking_system@sensors` | ABS — anti-lock braking system | ABS (антиблокировочная система) | ABS — 防抱死制动系统 | 0 | — | — | — |
| 4 | `accelerator_pedal_position_sensor@sensors` | accelerator pedal position sensor | датчик положения педали газа | 油门踏板位置传感器 | 0 | — | — | — |
| 5 | `accelerometer@sensors` | accelerometer | акселерометр | 加速度计 | 0 | — | — | — |
| 6 | `active_headrest@sensors` | active headrest / WHIPS headrest (whiplash protection) | активный подголовник | 主动式头枕 / WHIPS头枕（鞭打保护） | 0 | — | — | — |
| 7 | `active_pixel_sensor@sensors` | active pixel sensor | КМОП-матрица | 有源像素传感器 | 0 | — | — | — |
| 8 | `adas_front_camera@sensors` | frontal ADAS camera | фронтальная камера ADAS | 前置ADAS摄像头 | 0 | — | — | — |
| 9 | `airbag@sensors` | airbag | подушка безопасности | 安全气囊 | 162 | — | — | — |
| 10 | `airbag_inflator@sensors` | airbag inflator / pyrotechnic inflator | газогенератор подушки безопасности | 安全气囊充气器 / 烟火式充气器 | 0 | — | — | — |
| 11 | `ambient_light_sensor@sensors` | ambient light sensor | датчик освещённости | 环境光传感器 | 0 | — | — | — |
| 12 | `around_view_monitor@sensors` | Around View Monitor / Surround View | система кругового обзора (AVM / SVM) | 全景影像系统 (AVM) | 0 | — | — | — |
| 13 | `blok_upravleniya_xcu@sensors` | Control Unit | Блок управления XCU | 控制单元 | 14 | — | — | — |
| 14 | `camera_360_front@sensors` | 360° front camera | камера 360° передняя | 360°前置摄像头 | 0 | — | — | — |
| 15 | `camera_360_left@sensors` | 360° left camera | камера 360° левая | 360°左侧摄像头 | 0 | — | — | — |
| 16 | `camera_360_rear@sensors` | 360° rear camera | камера 360° задняя | 360°后置摄像头 | 0 | — | — | — |
| 17 | `camera_360_right@sensors` | 360° right camera | камера 360° правая | 360°右侧摄像头 | 0 | — | — | — |
| 18 | `carbon_monoxide_detector@sensors` | carbon monoxide detector | детектор угарного газа (CO) | 一氧化碳探测器 | 0 | — | — | — |
| 19 | `corner_radar@sensors` | corner radar | угловой радар | 角雷达 | 0 | — | — | — |
| 20 | `corner_radar_fl@sensors` | corner radar front-left | угловой радар передний левый | 左前角雷达 | 0 | — | — | — |
| 21 | `corner_radar_fr@sensors` | corner radar front-right | угловой радар передний правый | 右前角雷达 | 0 | — | — | — |
| 22 | `corner_radar_rl@sensors` | corner radar rear-left | угловой радар задний левый | 左后角雷达 | 0 | — | — | — |
| 23 | `corner_radar_rr@sensors` | corner radar rear-right | угловой радар задний правый | 右后角雷达 | 0 | — | — | — |
| 24 | `crash_sensor@sensors` | crash sensor / impact sensor / accelerometer | датчик удара / акселерометр подушек | 碰撞传感器 / 冲击传感器 / 加速度计 | 0 | — | — | — |
| 25 | `crash_sensor_array@sensors` | crash sensors | датчики удара | 碰撞传感器 | 1 | — | — | — |
| 26 | `curtain_airbag@sensors` | curtain airbag | шторка безопасности (боковая) | 帘式气囊 | 0 | — | — | — |
| 27 | `curtain_airbags@sensors` | curtain airbags / side curtain airbags | шторки безопасности / занавески | 帘式安全气囊 / 侧帘式安全气囊 | 0 | — | — | — |
| 28 | `detector@sensors` | detector | детектор | 检测器 | 0 | — | — | — |
| 29 | `dms_camera@sensors` | driver monitoring camera (DMS) | камера контроля водителя (DMS) | 驾驶员监控摄像头 | 0 | — | — | — |
| 30 | `door_impact_beam@sensors` | door impact beam / side impact bar | защитная балка в двери | 车门防撞梁 / 侧面防撞杆 | 0 | — | — | — |
| 31 | `driver_airbag@sensors` | driver airbag | подушка безопасности водителя | 驾驶员侧安全气囊 | 0 | — | — | — |
| 32 | `driver_monitoring_system@sensors` | driver monitoring system / attention assist | система контроля состояния водителя (DMS) | 驾驶员监控系统 (DMS) | 0 | — | — | — |
| 33 | `electronic_stability_control@sensors` | electronic stability control / program | система стабилизации (ESP/ESC) | 电子稳定控制系统 / 电子稳定程序 | 0 | — | — | — |
| 34 | `embedded_sim@sensors` | embedded SIM (eSIM) | встроенная SIM-карта (eSIM) | 嵌入式SIM卡（eSIM） | 0 | — | — | — |
| 35 | `fiberoptic_sensor@sensors` | fiber-optic sensor | волоконно-оптический датчик | 光纤传感器 | 0 | — | — | — |
| 36 | `forward_camera@sensors` | forward camera | фронтальная камера | 前置摄像头 | 0 | — | — | — |
| 37 | `front_camera@sensors` | front camera | передняя камера | 前置摄像头 | 0 | — | — | — |
| 38 | `front_mmwave_radar@sensors` | front millimeter-wave radar | передний миллиметровый радар | 前毫米波雷达 | 1 | — | — | — |
| 39 | `front_parking_sensor@sensors` | front parking sensor | передний парктроник | 前泊车传感器 | 0 | — | — | — |
| 40 | `front_radar@sensors` | front radar | фронтальный радар | 前置雷达 | 0 | — | — | — |
| 41 | `front_radar_sensor@sensors` | front radar sensor | передний радарный датчик | 前雷达传感器 | 0 | — | — | — |
| 42 | `front_stereo_camera@sensors` | front stereo camera | передняя стереокамера | 前视双目摄像头 | 1 | — | — | — |
| 43 | `frontal_airbag@sensors` | frontal airbag | фронтальная подушка безопасности | 前气囊 | 0 | — | — | — |
| 44 | `fsd_controller@sensors` | FSD controller | контроллер FSD (автопилот) | FSD控制器 | 1 | — | — | — |
| 45 | `gas_detector@sensors` | gas detector | датчик загазованности | 气体探测器 | 0 | — | — | — |
| 46 | `gateway_module@sensors` | gateway module | шлюз CAN | 网关模块 | 0 | — | — | — |
| 47 | `glow_plug_control_unit@sensors` | Control Unit | Блок управления | 控制单元 | 0 | — | — | — |
| 48 | `gnss@sensors` | GNSS / GPS module | модуль ГНСС / GPS | 卫星定位模块 (GNSS/GPS) | 0 | — | — | — |
| 49 | `golovnoe_ustroystvo@sensors` | Golovnoe Ustroystvo | Головное устройство | Головное устройство | 0 | — | — | — |
| 50 | `gps@sensors` | GPS / GNSS antenna | антенна GPS / GNSS | GPS/GNSS天线 | 0 | — | — | — |
| 51 | `gps_module@sensors` | GPS / GNSS module | модуль GPS / GNSS | GPS/GNSS模块 | 0 | — | — | — |
| 52 | `gyroscope@sensors` | gyroscope | гироскоп | 陀螺仪 | 0 | — | — | — |
| 53 | `head_unit@sensors` | head unit / infotainment unit | головное устройство | 主机 / 信息娱乐系统 | 0 | — | 1 | U0100, U0155 |
| 54 | `headup_display@sensors` | head-up display (HUD) | проекционный дисплей | 抬头显示器 | 15 | — | — | — |
| 55 | `headup_display_unit@sensors` | head-up display unit | блок проекционного дисплея (HUD) | 抬头显示装置 | 41 | — | — | — |
| 56 | `heat_detector@sensors` | heat detector | датчик тепла | 热探测器 | 0 | — | — | — |
| 57 | `humidity_sensor@sensors` | humidity sensor | датчик влажности | 湿度传感器 | 0 | — | — | — |
| 58 | `image_sensor@sensors` | image sensor | датчик изображения (матрица) | 图像传感器 | 0 | — | — | — |
| 59 | `immo_antenna@sensors` | IMMO antenna | антенна иммобилайзера | IMMO天线 | 1 | — | — | — |
| 60 | `immobiliser@sensors` | immobiliser / immobilizer | иммобилайзер | 防盗锁止系统 | 0 | — | — | — |
| 61 | `imu@sensors` | IMU (inertial measurement unit) | инерциальный модуль (IMU) | 惯性测量单元 (IMU) | 0 | — | — | — |
| 62 | `imu_sensor@sensors` | inertial measurement unit (IMU) | инерциальный измерительный модуль (IMU) | 惯性测量单元 | 0 | — | — | — |
| 63 | `inductive_sensor@sensors` | inductive sensor | индуктивный датчик | 电感式传感器 | 0 | — | — | — |
| 64 | `inertial_measurement_unit@sensors` | Inertial Measurement Unit | инерциальный измерительный блок (ИМБ / IMU) | 惯性测量单元 (IMU) | 0 | — | — | — |
| 65 | `infrared_detector@sensors` | infrared detector | инфракрасный датчик | 红外探测器 | 0 | — | — | — |
| 66 | `knee_airbag@sensors` | knee airbag | коленная подушка безопасности | 膝部气囊 | 0 | — | — | — |
| 67 | `lidar@sensors` | LiDAR | лидар | 激光雷达 | 63 | — | — | — |
| 68 | `lidar_roof@sensors` | roof-mounted LiDAR | лидар на крыше | 车顶激光雷达 | 0 | — | — | — |
| 69 | `limit_switch@sensors` | limit switch | концевой выключатель | 限位开关 | 0 | — | — | — |
| 70 | `magnetic_detector@sensors` | magnetic detector | магнитный датчик | 磁探测器 | 0 | — | — | — |
| 71 | `mass_airflow_sensor@sensors` | mass airflow sensor (MAF) | ДМРВ (MAF) | 质量空气流量传感器（MAF） | 0 | — | — | — |
| 72 | `millimeterwave_radar@sensors` | millimeter-wave radar | радар миллиметрового диапазона | 毫米波雷达 | 76 | — | — | — |
| 73 | `motion_sensor@sensors` | Motion sensor | датчик движения | 运动传感器 | 0 | — | — | — |
| 74 | `motor_control_unit@sensors` | Motor Control Unit | блок управления электродвигателем (MCU) | 电机控制器 (MCU) | 0 | 1 | 1 | U0100, U0155 |
| 75 | `night_vision_system@sensors` | night vision system | система ночного видения | 夜视系统 | 0 | — | — | — |
| 76 | `occupant_detection_sensor@sensors` | occupant detection sensor / seat occupant sensor | детектор присутствия пассажира | 乘员探测传感器 / 座椅乘员传感器 | 0 | — | — | — |
| 77 | `parking_sensor@sensors` | parking sensor / ultrasonic proximity sensor / PDC sensor | парктроник / ультразвуковой датчик парковки | 泊车传感器 / 超声波近距传感器 / PDC传感器 | 0 | — | — | — |
| 78 | `parking_sensor_array_front@sensors` | front parking sensors | передние парктроники | 前泊车传感器 | 0 | — | — | — |
| 79 | `parking_sensor_array_rear@sensors` | rear parking sensors | задние парктроники | 后泊车传感器 | 0 | — | — | — |
| 80 | `passenger_airbag@sensors` | passenger airbag | подушка безопасности пассажира | 副驾驶侧安全气囊 | 0 | — | — | — |
| 81 | `photodetector@sensors` | photodetector | фотодетектор | 光电探测器 | 0 | — | — | — |
| 82 | `proximity_sensor@sensors` | proximity sensor | датчик приближения | 接近传感器 | 0 | — | — | — |
| 83 | `pyrotechnic_pretensioner_seatbelt@sensors` | pyrotechnic pretensioner seatbelt | ремень безопасности с пиропреднатяжителем | 烟火式预紧安全带 | 0 | — | — | — |
| 84 | `radar@sensors` | radar | радар | 雷达 | 33 | — | — | — |
| 85 | `radar_detector@sensors` | radar detector | радар-детектор | 雷达探测器 | 0 | — | — | — |
| 86 | `rain_sensor@sensors` | rain sensor | датчик дождя | 雨量传感器 | 2 | — | — | — |
| 87 | `rear_camera@sensors` | rear camera / backup camera | камера заднего вида | 后置摄像头 / 倒车摄像头 | 1 | — | — | — |
| 88 | `rear_parking_sensor@sensors` | rear parking sensor | задний парктроник | 后泊车传感器 | 0 | — | — | — |
| 89 | `rear_radar_sensor@sensors` | rear radar sensor | задний радарный датчик | 后雷达传感器 | 0 | — | — | — |
| 90 | `remote_key@sensors` | remote key / digital key | удалённый / цифровой ключ | 远程钥匙 / 数字车钥匙 | 0 | — | — | — |
| 91 | `resistance_thermometer@sensors` | resistance thermometer | термометр сопротивления | 电阻温度计 | 0 | — | — | — |
| 92 | `seat_belt@sensors` | seat belt | ремень безопасности | 安全带 | 298 | — | — | — |
| 93 | `seat_belt_pretensioner@sensors` | seat belt pretensioner | преднатяжитель ремня безопасности | 安全带预紧器 | 28 | — | — | — |
| 94 | `seatbelt_load_limiter@sensors` | seatbelt load limiter | ограничитель усилия ремня безопасности | 安全带限力器 | 0 | — | — | — |
| 95 | `sensor@sensors` | sensor | датчик | 传感器 | 268 | — | — | — |
| 96 | `side_airbag@sensors` | side airbag | боковая подушка безопасности | 侧气囊 | 1 | — | — | — |
| 97 | `side_airbags@sensors` | side airbags | боковые подушки безопасности | 侧面安全气囊 | 3 | — | — | — |
| 98 | `side_camera@sensors` | side camera | боковая камера | 侧方摄像头 | 0 | — | — | — |
| 99 | `solidstate_lidar@sensors` | solid-state lidar | твердотельный лидар | 固态激光雷达 | 0 | — | — | — |
| 100 | `srs@sensors` | SRS (supplemental restraint system) | система пассивной безопасности (SRS) | 辅助约束系统 (SRS) | 0 | — | — | — |
| 101 | `supplemental_restraint_system@sensors` | supplemental restraint system | дополнительная система удержания (SRS) | 辅助约束系统（SRS） | 0 | — | — | — |
| 102 | `surround_camera@sensors` | surround camera (×8) | камеры кругового обзора (8 шт.) | 环视摄像头（8颗） | 0 | — | — | — |
| 103 | `surround_view_camera@sensors` | surround view camera | камера кругового обзора | 全景摄像头 | 13 | — | — | — |
| 104 | `telematics_control_unit@sensors` | Telematics Control Unit | телематический блок управления (TCU) | 车载通信控制单元（TCU） | 0 | — | — | — |
| 105 | `temperature_sensor@sensors` | temperature sensor | датчик температуры | 温度传感器 | 4 | — | — | — |
| 106 | `traction_control_system@sensors` | traction control system / ASR | антипробуксовочная система (ASR/TCS) | 牵引力控制系统 / ASR | 0 | — | — | — |
| 107 | `ultrasonic_sensor@sensors` | ultrasonic sensor | ультразвуковой датчик | 超声波传感器 | 23 | — | — | — |
| 108 | `ultrasonic_sensor_system@sensors` | Ultrasonic Sensor System | ультразвуковые датчики (USS) | 超声波传感器系统 (USS) | 0 | — | — | — |
| 109 | `vehicle_speed_sensor@sensors` | vehicle speed sensor (VSS) | датчик скорости (VSS) | 车速传感器（VSS） | 0 | — | — | — |
| 110 | `voltage_detector@sensors` | voltage detector | указатель напряжения (индикатор) | 电压检测器 | 0 | — | — | — |
| 111 | `wideband_oxygen_sensor@sensors` | wideband oxygen sensor | широкополосный датчик кислорода | 宽频氧传感器 | 0 | — | — | — |
| 112 | `xcu_adas_controller@sensors` | ADAS control unit (XCU) | блок управления ADAS (XCU) | ADAS控制单元 | 0 | — | — | — |
| 113 | `yaw_rate_sensor@sensors` | yaw rate sensor | датчик рысканья | 横摆角速度传感器 | 0 | — | — | — |

## 7. HVAC — Климат-контроль и терморегулирование (101 компонентов)

*Компрессор кондиционера, конденсатор, испаритель, радиатор печки, вентилятор, салонный фильтр, тепловой насос, терморегулирование батареи, контуры охлаждения*

**Подсистемы:** ac_system, heating, ventilation, battery_thermal, motor_thermal, coolant_circuits

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `12v_ptc_heater@hvac` | 12V PTC heater | 12В PTC-нагреватель | 12V PTC加热器 | 0 | — | — | — |
| 2 | `4way_valve@hvac` | 4-way valve / 6-way valve | 4-ходовой / 6-ходовой клапан | 四通阀 / 六通阀 | 0 | — | — | — |
| 3 | `8way_thermal_management_valve@hvac` | 8-way thermal management valve | 8-ходовой клапан системы термоуправления | 八通热管理阀 | 0 | — | — | — |
| 4 | `a@hvac` | A/C lines / refrigerant lines | трубопроводы кондиционера | 空调管路 / 制冷剂管路 | 0 | — | — | — |
| 5 | `ac_compressor@hvac` | A/C compressor | компрессор кондиционера | 空调压缩机 | 0 | — | — | — |
| 6 | `activated_carbon_cabin_filter@hvac` | activated carbon cabin filter / charcoal cabin filter | угольный салонный фильтр | 活性炭车内空气滤清器 | 0 | — | — | — |
| 7 | `air_box@hvac` | air box / HVAC plenum | воздушный короб | 进气箱 / 空调分气室 | 0 | — | — | — |
| 8 | `air_conditioning_a@hvac` | air conditioning (A/C) | кондиционер | 空调 | 68 | — | — | — |
| 9 | `air_conditioning_system@hvac` | air conditioning system | система кондиционирования | 空调系统 | 180 | — | — | — |
| 10 | `air_duct@hvac` | air duct / HVAC duct | воздуховод | 空调风道 / 通风管道 | 0 | — | — | — |
| 11 | `air_ionizer@hvac` | air ionizer | ионизатор воздуха | 空气电离器 | 0 | — | — | — |
| 12 | `air_vent@hvac` | air vent / outlet | дефлектор / воздуховод | 出风口 | 48 | — | — | — |
| 13 | `aircooled_battery@hvac` | Battery Cooling | Охлаждение батареи | 电池冷却 | 12 | — | — | — |
| 14 | `ambient_air_temperature_sensor@hvac` | ambient air temperature sensor | датчик температуры наружного воздуха | 环境温度传感器 | 0 | — | — | — |
| 15 | `automatic_climate_control@hvac` | automatic climate control / auto A/C | климат-контроль (автоматический) | 自动空调 / 自动气候控制 | 0 | — | — | — |
| 16 | `battery_cooling_circuit@hvac` | battery cooling circuit | контур охлаждения батареи | 电池冷却回路 | 0 | — | — | — |
| 17 | `battery_cooling_plate@hvac` | battery cooling plate | плита охлаждения батареи | 电池冷却板 | 0 | — | — | — |
| 18 | `battery_electronic_water_pump@hvac` | battery electronic water pump | электронный водяной насос батареи | 电池电子水泵 | 1 | — | — | — |
| 19 | `battery_heater@hvac` | battery heater (coolant-based) | подогреватель батареи (через охлаждающую жидкость) | 电池加热器（冷却液循环式） | 0 | — | — | — |
| 20 | `battery_thermal_management_system@hvac` | Battery Thermal Management System (BTMS) | BTMS (система термического управления батареей) | BTMS（电池热管理系统） | 0 | — | — | — |
| 21 | `battery_thermal_management_system_btms@hvac` | Battery Thermal Management System (BTMS) | BTMS (система термического управления батареей) | BTMS（电池热管理系统） | 0 | 1 | 1 | P0A7F, P0A80, P0AA6, P3000 |
| 22 | `blend_door_actuator@hvac` | blend door actuator / servo motor | привод заслонки (серводвигатель) | 混风门执行器 / 伺服电机 | 0 | — | — | — |
| 23 | `blower_fan@hvac` | HVAC blower fan | вентилятор отопителя | 鼓风机 | 12 | — | — | — |
| 24 | `blower_motor@hvac` | blower motor / cabin fan motor | вентилятор печки / воздуховодный мотор | 鼓风机电机 | 0 | — | — | — |
| 25 | `blower_motor_resistor@hvac` | blower motor resistor / fan speed module | резистор / модуль управления скоростью вентилятора | 鼓风机电阻 | 0 | — | — | — |
| 26 | `blower_resistor@hvac` | blower resistor | резистор вентилятора печки | 鼓风机电阻 | 0 | — | — | — |
| 27 | `cabin_air_filter@hvac` | cabin air filter / pollen filter / habitacle filter | салонный фильтр / фильтр кабины | 空调滤芯 | 0 | — | — | — |
| 28 | `cabin_air_temperature_sensor@hvac` | cabin air temperature sensor | датчик температуры воздуха в салоне | 座舱温度传感器 | 0 | — | — | — |
| 29 | `cabin_filter@hvac` | cabin air filter | салонный фильтр | 空调滤芯 | 8 | — | — | — |
| 30 | `cabin_heater@hvac` | cabin heater / heating system | отопитель салона | 车厢暖风装置 / 供暖系统 | 0 | — | — | — |
| 31 | `chiller@hvac` | chiller | чиллер (охладитель) | 冷却器（冷水机） | 0 | — | — | — |
| 32 | `climate_control_unit@hvac` | climate control unit / HVAC module | блок управления климатом | 气候控制单元 / 空调模块 | 0 | — | — | — |
| 33 | `compressor_a@hvac` | compressor (A/C) | компрессор кондиционера | 压缩机 | 20 | — | — | — |
| 34 | `condenser@hvac` | condenser / A/C condenser | конденсор кондиционера | 冷凝器 | 14 | — | — | — |
| 35 | `condenser_ann@hvac` | A/C condenser | конденсатор кондиционера | 空调冷凝器 | 11 | — | — | — |
| 36 | `condenser_assembly@hvac` | condenser assembly | конденсор в сборе | 冷凝器总成 | 0 | — | — | — |
| 37 | `coolant_circuit@hvac` | coolant cooling circuit | контур охлаждения | 冷却液回路 | 0 | — | — | — |
| 38 | `coolant_expansion_tank@hvac` | coolant expansion tank | расширительный бачок | 膨胀水箱 | 13 | — | — | — |
| 39 | `coolant_preheater@hvac` | coolant pre-heater / liquid heater | жидкостный предпусковой подогреватель | 冷却液预热器 / 液体加热器 | 0 | — | — | — |
| 40 | `coolant_pump@hvac` | coolant pump (battery circuit) | циркуляционный насос (контур батареи) | 电池回路冷却液水泵 | 0 | — | — | — |
| 41 | `cooling_system@hvac` | cooling system | система охлаждения | 冷却系统 | 24 | — | — | — |
| 42 | `diesel_air_heater@hvac` | diesel air heater / Webasto / Eberspächer | автономный дизельный подогреватель (Вебасто) | 柴油暖风机 / 韦巴斯托 / 埃贝斯派切尔 | 0 | — | — | — |
| 43 | `dualzone_climate_control@hvac` | dual-zone climate control | двухзонный климат-контроль | 双区空调 | 0 | — | — | — |
| 44 | `electric_a@hvac` | electric A/C compressor | электрический компрессор кондиционера (EV) | 电动空调压缩机 | 0 | — | — | — |
| 45 | `electric_compressor@hvac` | electric compressor (e-compressor) | электрический компрессор (e-компрессор) | 电动压缩机（电驱压缩机） | 0 | — | — | — |
| 46 | `electric_preheater@hvac` | electric pre-heater / PTC heater | электрический подогреватель / PTC-нагреватель | PTC加热器 | 0 | — | — | — |
| 47 | `electronic_fan_assembly@hvac` | electronic fan assembly | электровентилятор в сборе | 电子风扇总成 | 1 | — | — | — |
| 48 | `electronic_fourway_valve@hvac` | electronic four-way valve | электронный четырёхходовой клапан | 电子四通阀 | 1 | — | — | — |
| 49 | `electronic_threeway_valve@hvac` | electronic three-way valve | электронный трёхходовой клапан | 电子三通阀 | 3 | — | — | — |
| 50 | `engine_radiator_assembly@hvac` | engine radiator assembly | радиатор двигателя в сборе | 发动机散热器总成 | 0 | — | — | — |
| 51 | `evaporator@hvac` | evaporator | испаритель | 蒸发器 | 0 | — | — | — |
| 52 | `evaporator_ann@hvac` | evaporator | испаритель | 蒸发器 | 14 | — | — | — |
| 53 | `evaporator_core@hvac` | evaporator core | испаритель кондиционера | 蒸发器芯体 | 0 | — | — | — |
| 54 | `expansion_valve@hvac` | expansion valve / thermostatic expansion valve | расширительный клапан (TXV) | 膨胀阀 | 2 | — | — | — |
| 55 | `fan_clutch@hvac` | fan clutch | муфта вентилятора | 风扇离合器 | 0 | — | — | — |
| 56 | `fourzone_climate_control@hvac` | four-zone climate control | четырёхзонный климат-контроль | 四区自动空调 | 0 | — | — | — |
| 57 | `fragrance_system@hvac` | fragrance system | система ароматизации | 香氛系统 | 2 | — | — | — |
| 58 | `heat_pump@hvac` | heat pump | тепловой насос | 热泵 | 0 | — | — | — |
| 59 | `heat_pump_for_evs@hvac` | heat pump (for EVs/hybrids) | тепловой насос (HEV/EV) | 热泵 | 0 | — | — | — |
| 60 | `heated_seats@hvac` | heated seats | подогрев сидений | 座椅加热 | 105 | — | — | — |
| 61 | `heated_steering_wheel@hvac` | heated steering wheel | подогрев руля | 方向盘加热 | 0 | — | — | — |
| 62 | `heated_washer_nozzle@hvac` | heated washer nozzle | форсунка омывателя с подогревом | 加热式清洗喷嘴 | 0 | — | — | — |
| 63 | `heated_windscreen@hvac` | heated windscreen / front glass heating | обогрев лобового стекла | 前挡风玻璃加热 | 0 | — | — | — |
| 64 | `heated_windshield@hvac` | heated windshield | обогреваемое лобовое стекло | 加热挡风玻璃 | 0 | — | — | — |
| 65 | `heater@hvac` | heater | отопитель / печка | 加热器 | 13 | — | — | — |
| 66 | `heater_core@hvac` | heater core | радиатор печки (теплообменник) | 暖风芯体 | 0 | — | — | — |
| 67 | `heater_core_ann@hvac` | heater core | радиатор печки | 暖风芯体 | 1 | — | — | — |
| 68 | `heater_matrix@hvac` | heater matrix | теплообменник отопителя | 暖风芯体 | 0 | — | — | — |
| 69 | `heater_valve@hvac` | heater valve / hot water valve | кран отопителя / клапан печки | 暖风阀 / 热水阀 | 0 | — | — | — |
| 70 | `hepa_filter@hvac` | HEPA filter | HEPA-фильтр | HEPA滤芯 | 0 | — | — | — |
| 71 | `highpressure_refrigerant_sensor@hvac` | high-pressure refrigerant sensor | датчик давления хладагента высокого давления | 高压侧制冷剂压力传感器 | 0 | — | — | — |
| 72 | `hose_clamp@hvac` | hose clamp | хомут шланга | 管卡/管夹 | 0 | — | — | — |
| 73 | `hv_ptc_heater@hvac` | HV PTC heater | высоковольтный PTC-нагреватель | 高压PTC加热器 | 0 | — | — | — |
| 74 | `hvac_system@hvac` | HVAC system (Heating, Ventilation, Air Conditioning) | система климата / HVAC | 暖通空调系统（HVAC） | 0 | — | — | — |
| 75 | `lowpressure_refrigerant_sensor@hvac` | low-pressure refrigerant sensor | датчик давления хладагента низкого давления | 低压侧制冷剂压力传感器 | 0 | — | — | — |
| 76 | `mode_door@hvac` | mode door / air distribution door | заслонка режима воздуха | 模式风门 / 配风风门 | 0 | — | — | — |
| 77 | `motor_cooling_circuit@hvac` | motor cooling circuit | контур охлаждения электромотора | 电机冷却回路 | 0 | — | — | — |
| 78 | `motor_electronic_water_pump@hvac` | motor electronic water pump | электронный водяной насос мотора | 电机电子水泵 | 1 | — | — | — |
| 79 | `orifice_tube@hvac` | orifice tube | дроссельное устройство / трубка с дросселем | 节流管 | 0 | — | — | — |
| 80 | `outdoor_heat_exchanger@hvac` | outdoor heat exchanger (OHE) | наружный теплообменник (OHE) | 室外换热器（OHE） | 0 | — | — | — |
| 81 | `ptc_heater@hvac` | PTC heater (Positive Temperature Coefficient) | PTC-нагреватель (с положительным температурным коэффициентом) | PTC加热器（正温度系数加热器） | 0 | — | — | — |
| 82 | `radiator@hvac` | Radiator — Finish | радиатор | 散热器 — 装饰 | 3 | 1 | 1 | P0A7F |
| 83 | `radiator_cap@hvac` | radiator cap | крышка радиатора | 散热器盖 | 0 | — | — | — |
| 84 | `radiator_fan@hvac` | radiator fan | вентилятор радиатора | 散热器风扇 | 1 | — | — | — |
| 85 | `radiator_hose_upper@hvac` | radiator hose (upper/lower) | патрубок радиатора (верхний/нижний) | 散热器水管（上/下） | 0 | — | — | — |
| 86 | `receiver@hvac` | receiver / drier | ресивер-осушитель | 储液干燥器 | 0 | — | — | — |
| 87 | `recirculation_door@hvac` | recirculation door / fresh air/recirculation flap | заслонка рециркуляции воздуха | 内循环风门 | 0 | — | — | — |
| 88 | `recirculation_flap@hvac` | recirculation flap | заслонка рециркуляции | 内循环风门 | 0 | — | — | — |
| 89 | `refrigerant_pressure_sensor@hvac` | refrigerant pressure sensor | датчик давления хладагента | 制冷剂压力传感器 | 0 | — | — | — |
| 90 | `service_valve@hvac` | service valve / charging port | заправочный клапан | 充注口 / 维修阀 | 0 | — | — | — |
| 91 | `steering_wheel_heating@hvac` | steering wheel heating | подогрев рулевого колеса | 方向盘加热 | 56 | — | — | — |
| 92 | `sun_load_sensor@hvac` | sun load sensor | датчик солнечной инсоляции | 阳光辐射传感器 | 0 | — | — | — |
| 93 | `temperature_blend_door@hvac` | temperature blend door | заслонка смешения воздуха | 温度混合风门 | 0 | — | — | — |
| 94 | `temperature_sensor@hvac` | temperature sensor (exterior) | датчик наружной температуры | 车外温度传感器 | 0 | — | — | — |
| 95 | `thermal_management_system@hvac` | thermal management system | система терморегулирования | 热管理系统 | 0 | — | — | — |
| 96 | `thermostat@hvac` | thermostat | термостат | 节温器 | 1 | — | — | — |
| 97 | `thermostat_housing@hvac` | thermostat housing | корпус термостата | 节温器壳体 | 0 | — | — | — |
| 98 | `trizone@hvac` | tri-zone / quad-zone climate | трёх-/четырёхзонный климат | 三区/四区空调 | 0 | — | — | — |
| 99 | `trizone_climate_control@hvac` | tri-zone climate control | трёхзонный климат-контроль | 三区自动空调 | 0 | — | — | — |
| 100 | `ventilated_seats@hvac` | ventilated seats | вентиляция сидений | 座椅通风 | 0 | — | — | — |
| 101 | `windscreen_heater@hvac` | windscreen heater / defrost | обогрев ветрового стекла | 风挡玻璃加热除霜 | 0 | — | — | — |

## 8. INTERIOR — Двери, багажник и салон (184 компонентов)

*Двери, защёлки, замки, багажник, сиденья, приборная панель, мультимедиа, внутреннее освещение, обивка, кнопки руля, педали*

**Подсистемы:** doors_latches, trunk, seats, dashboard, infotainment, interior_lighting, trim_upholstery, pedals_controls

| # | ID | EN | RU | ZH | KB чанков | 3D (L7) | 3D (L9) | DTC |
|---|----|----|----|----|-----------|---------|---------|-----|
| 1 | `accelerator_pedal@interior` | Pedal R | педаль газа / акселератор | 踏板右 | 0 | — | — | — |
| 2 | `accelerator_pedal_gas_pedal@interior` | accelerator pedal / gas pedal | педаль газа / акселератор | 加速踏板 / 油门踏板 | 0 | 1 | — | B1450, B1460 |
| 3 | `air_freshener@interior` | air freshener / fragrance diffuser | ароматизатор | 香氛系统 | 9 | 1 | — | B1450, B1460 |
| 4 | `air_vent@interior` | air vent / HVAC duct | вентиляционное отверстие / воздуховод системы вентиляции | 空调出风口 / 暖通风管 | 0 | — | — | — |
| 5 | `air_vent_deflector@interior` | air vent deflector / vent louver | дефлектор вентиляции | 出风口导流板 | 0 | — | — | — |
| 6 | `ambient_lighting@interior` | ambient lighting | фоновая подсветка салона | 氛围灯 | 77 | — | — | — |
| 7 | `antenna@interior` | antenna | антенна | 天线 | 5 | — | — | — |
| 8 | `armrest@interior` | armrest | подлокотник | 扶手 | 25 | — | — | — |
| 9 | `aromatizator@interior` | Air Freshener | Ароматизатор | 香氛 | 2 | — | — | — |
| 10 | `ashtray@interior` | ashtray | пепельница | 烟灰缸 | 0 | — | — | — |
| 11 | `autodimming_mirror@interior` | auto-dimming mirror | зеркало с автозатемнением | 自动防眩目后视镜 | 0 | — | — | — |
| 12 | `bcm_module@interior` | body control module (BCM) | блок управления кузовом (BCM) | 车身控制模块 | 0 | — | — | — |
| 13 | `body_shell@interior` | Body — Carpet | Кузов (интерьер) 2#2 — Ковролин | 车身 — 地毯 | 0 | — | — | — |
| 14 | `brake_light@interior` | brake light / stop lamp | стоп-сигнал | 刹车灯 | 2 | — | — | — |
| 15 | `bumper_reinforcement@interior` | Rear Bumper — Buttons | Бампер задний#2 — Кнопки | 后保险杠 — 按钮 | 0 | — | — | — |
| 16 | `cabin_air_filter@interior` | Cabin Air Filter | Салон | Салон | 41 | — | — | — |
| 17 | `car_alarm@interior` | car alarm | сигнализация | 汽车报警器 | 4 | — | — | — |
| 18 | `cargo_net@interior` | cargo net | сетка багажника | 行李网 | 0 | — | — | — |
| 19 | `center_armrest@interior` | center armrest | центральный подлокотник | 中央扶手 | 25 | — | — | — |
| 20 | `center_console@interior` | center console | центральная консоль | 中控台 | 51 | — | — | — |
| 21 | `central_locking@interior` | central locking | центральный замок | 中控锁 | 0 | — | — | — |
| 22 | `child_lock@interior` | child lock | детский замок | 儿童锁 | 22 | — | — | — |
| 23 | `child_seat@interior` | child seat / child safety seat | детское удерживающее устройство | 儿童安全座椅 | 102 | — | — | — |
| 24 | `cigarette_lighter@interior` | cigarette lighter / 12V power outlet | прикуриватель / розетка 12В | 点烟器 / 12V电源插座 | 0 | — | — | — |
| 25 | `courtesy_light@interior` | courtesy light | подсветка салона (при открытии двери) | 礼仪灯 / 门灯 | 0 | — | — | — |
| 26 | `cup_holder@interior` | cup holder | подстаканник | 杯架 | 4 | — | — | — |
| 27 | `dashboard@interior` | dashboard / instrument panel / fascia | передняя панель / торпедо | 仪表板 / 仪表台 | 0 | — | — | — |
| 28 | `dashboard_instrument_panel_fascia@interior` | dashboard / instrument panel / fascia | передняя панель / торпедо | 仪表板 / 仪表台 | 0 | 7 | 1 | B1450, B1460, U0100 |
| 29 | `dashboard_top@interior` | dashboard top / dash top | верхняя часть торпедо | 仪表板上盖 | 1 | — | — | — |
| 30 | `daytime_running_light@interior` | daytime running light (DRL) | дневные ходовые огни (ДХО) | 日间行车灯 (DRL) | 0 | — | — | — |
| 31 | `door@interior` | door | дверь | 车门 | 36 | — | — | — |
| 32 | `door_check_strap@interior` | door check strap | ограничитель открывания двери | 门限位器 | 4 | — | — | — |
| 33 | `door_handle@interior` | door handle | ручка двери | 门把手 | 0 | — | — | — |
| 34 | `door_hinge@interior` | door hinge | петля двери | 门铰链 | 5 | — | — | — |
| 35 | `door_latch@interior` | door latch | защёлка двери | 门闩 | 0 | — | — | — |
| 36 | `door_lock@interior` | door lock | замок двери | 门锁 | 12 | — | — | — |
| 37 | `door_lock_actuator@interior` | door lock actuator | привод замка двери | 车门锁执行器 | 0 | — | — | — |
| 38 | `door_pocket@interior` | door pocket / door bin | карман в двери | 车门储物袋 | 0 | — | — | — |
| 39 | `door_sill_plates@interior` | door sill plates / scuff plates | накладки порогов | 门槛踏板 / 门槛护板 | 0 | — | — | — |
| 40 | `door_trim_panel@interior` | door trim panel | обшивка двери | 门板饰板 | 0 | — | 4 | B1011, B1012, B1013, B1014 |
| 41 | `driver_seat@interior` | driver seat | сиденье водителя | 驾驶座 | 59 | — | — | — |
| 42 | `dvernaya_karta_pl@interior` | Door Panel FL | Дверная карта ПЛ | 门板左前 | 0 | — | — | — |
| 43 | `dvernaya_karta_pp@interior` | Door Panel FR | Дверная карта ПП | 门板右前 | 0 | — | — | — |
| 44 | `dvernaya_karta_zl@interior` | Door Panel RL | Дверная карта ЗЛ | 门板左后 | 0 | — | — | — |
| 45 | `dvernaya_karta_zp@interior` | Door Panel RR | Дверная карта ЗП | 门板右后 | 0 | — | — | — |
| 46 | `ekran_priborov@interior` | Instrument Cluster | Экран приборов | 仪表盘 | 0 | — | — | — |
| 47 | `electric_tailgate@interior` | electric tailgate | электрический привод багажника | 电动尾门 | 0 | — | — | — |
| 48 | `floor_mat@interior` | floor mat / carpet mat | напольный коврик | 脚垫 / 地毯垫 | 0 | — | — | — |
| 49 | `fog_light@interior` | fog light | противотуманная фара | 雾灯 | 3 | — | — | — |
| 50 | `footwell_lighting@interior` | footwell lighting / ambient lighting | подсветка ног | 脚部照明 / 氛围灯 | 2 | — | — | — |
| 51 | `front_armrest@interior` | front armrest | подлокотник (перед.) | 前排扶手 | 0 | — | — | — |
| 52 | `front_door@interior` | front door | дверь (перед.) | 前车门 | 0 | — | — | — |
| 53 | `front_door_hinge@interior` | front door hinge | петля двери (перед.) | 前车门铰链 | 0 | — | — | — |
| 54 | `front_door_latch@interior` | front door latch | защёлка двери (перед.) | 前车门锁扣 | 0 | — | — | — |
| 55 | `front_door_lock@interior` | front door lock | замок двери (перед.) | 前车门锁 | 0 | — | — | — |
| 56 | `front_inner_door_handle@interior` | front inner door handle | ручка двери (внутр.) (перед.) | 前排内门把手 | 0 | — | — | — |
| 57 | `front_left_door_handle@interior` | front left door handle | ручка двери (перед., лев.) | 前左车门把手 | 0 | — | — | — |
| 58 | `front_left_door_seal@interior` | front left door seal | уплотнитель двери (перед., лев.) | 前左车门密封条 | 0 | — | — | — |
| 59 | `front_left_seat_belt@interior` | front left seat belt | ремень безопасности (перед., лев.) | 前左安全带 | 0 | — | — | — |
| 60 | `front_outer_door_handle@interior` | front outer door handle | ручка двери (наруж.) (перед.) | 前车门外把手 | 0 | — | — | — |
| 61 | `front_right_door_handle@interior` | front right door handle | ручка двери (перед., прав.) | 前右车门把手 | 0 | — | — | — |
| 62 | `front_right_door_seal@interior` | front right door seal | уплотнитель двери (перед., прав.) | 前右车门密封条 | 0 | — | — | — |
| 63 | `front_right_seat_belt@interior` | front right seat belt | ремень безопасности (перед., прав.) | 前右安全带 | 0 | — | — | — |
| 64 | `front_seat@interior` | Seat | сиденье (перед.) | 座椅 | 55 | 20 | 3 | B1450, B1460 |
| 65 | `front_seat_belt_buckle@interior` | front seat belt buckle | замок ремня безопасности (перед.) | 前排安全带锁扣 | 0 | — | — | — |
| 66 | `front_sunroof_glass@interior` | front sunroof glass | стекло переднего люка | 前天窗玻璃总成 | 1 | — | — | — |
| 67 | `front_trunk_latch@interior` | front trunk latch | замок багажника (перед.) | 前行李箱锁扣 | 0 | — | — | — |
| 68 | `fuse_box_interior@interior` | interior fuse box | блок предохранителей (салон) | 室内保险丝盒 | 0 | — | — | — |
| 69 | `gear_selector@interior` | gear selector / shifter | селектор передач | 换挡器 | 19 | — | — | — |
| 70 | `glove_box@interior` | glove box / glove compartment | бардачок / перчаточный ящик | 手套箱 / 储物箱 | 0 | — | — | — |
| 71 | `glove_box_glove_compartment@interior` | glove box / glove compartment | бардачок / перчаточный ящик | 手套箱 / 储物箱 | 0 | 2 | — | B1450, B1460 |
| 72 | `grab_handle@interior` | grab handle / assist grip | ручка на крыше / скоба | 抓手 / 扶手 | 0 | — | — | — |
| 73 | `headliner@interior` | headliner / roof lining | обшивка потолка | 顶棚 | 5 | — | — | — |
| 74 | `headlining@interior` | headlining | обивка потолка | 顶棚内衬 | 0 | — | — | — |
| 75 | `headrest@interior` | headrest | подголовник | 头枕 | 28 | — | — | — |
| 76 | `heated_seat@interior` | heated seat / seat heater | подогрев сиденья | 座椅加热 / 加热座椅 | 1 | — | — | — |
| 77 | `hid@interior` | HID / xenon headlight | ксеноновая фара | 氙气大灯 | 0 | — | — | — |
| 78 | `high_beam@interior` | high beam / main beam | дальний свет | 远光灯 | 81 | — | — | — |
| 79 | `horn@interior` | horn | звуковой сигнал / клаксон | 喇叭 | 7 | — | — | — |
| 80 | `hud@interior` | HUD (head-up display) | проекционный дисплей (HUD) | 抬头显示 (HUD) | 0 | — | — | — |
| 81 | `hud_projector@interior` | head-up display (HUD) | проекционный дисплей (HUD) | 抬头显示器 | 0 | — | — | — |
| 82 | `incar_usb_port@interior` | in-car USB port / USB charging port | USB-порт в салоне | 车内USB接口 / USB充电接口 | 0 | — | — | — |
| 83 | `indikatory_priborov@interior` | Instrument Indicators L — Инд. поворотник Л | Индикаторы приборов#2 — Инд. поворотник Л | 仪表指示器左 — Инд. поворотник Л | 0 | — | — | — |
| 84 | `indikatory_priborov_2@interior` | Instrument Indicators — Инд. давление | Индикаторы приборов 2#2 — Инд. давление | 仪表指示器 — Инд. давление | 0 | — | — | — |
| 85 | `infotainment_screen@interior` | infotainment screen / multimedia display | монитор мультимедиа | 车载娱乐屏幕 / 多媒体显示屏 | 0 | — | — | — |
| 86 | `infotainment_screen_multimedia_display@interior` | infotainment screen / multimedia display | монитор мультимедиа | 车载娱乐屏幕 / 多媒体显示屏 | 0 | 5 | 1 | B1450, B1460, U0100 |
| 87 | `infotainment_system@interior` | infotainment system | мультимедийная система | 信息娱乐系统 | 0 | — | — | — |
| 88 | `inner_door_handle@interior` | inner door handle | ручка двери (внутр.) | 车门内把手 | 23 | — | — | — |
| 89 | `instrument_cluster@interior` | instrument cluster | щиток приборов | 组合仪表 | 0 | 16 | — | B1260, B1450, B1460, P0171, P0300, P0A0F, U0100 |
| 90 | `interior_light@interior` | interior light / dome light / cabin lamp | плафон освещения салона | 车内顶灯／室内灯 | 0 | — | — | — |
| 91 | `interior_rear_view_mirror@interior` | interior rear view mirror | зеркало заднего вида (салонное) | 车内后视镜 | 12 | — | — | — |
| 92 | `interior_rearview_mirror@interior` | interior rearview mirror | салонное зеркало заднего вида | 内后视镜总成 | 1 | 2 | — | B1450, B1460 |
| 93 | `interior_trim@interior` | interior trim / upholstery | обивка салона | 内饰面料 | 0 | 7 | 1 | B1450, B1460 |
| 94 | `isofix_system@interior` | ISOFIX system | система ISOFIX | ISOFIX儿童座椅固定系统 | 0 | — | — | — |
| 95 | `kozyryok_levyy@interior` | Sun Visor | Козырёк левый | 遮阳板 | 31 | — | — | — |
| 96 | `kozyryok_pravyy@interior` | Sun Visor | Козырёк правый | 遮阳板 | 0 | — | — | — |
| 97 | `lateral_support@interior` | lateral support / bolster | боковая поддержка | 侧向支撑／侧翼 | 0 | — | — | — |
| 98 | `left_mirror_glass@interior` | left mirror glass | зеркальный элемент (лев.) | 左后视镜镜片 | 0 | — | — | — |
| 99 | `left_mirror_housing@interior` | left mirror housing | корпус зеркала (лев.) | 左后视镜壳体 | 0 | — | — | — |
| 100 | `licence_plate_light@interior` | licence plate light | подсветка номерного знака | 牌照灯 | 14 | — | — | — |
| 101 | `load_limiter@interior` | load limiter / force limiter | ограничитель нагрузки ремня | 安全带限力器 | 0 | — | — | — |
| 102 | `low_beam@interior` | low beam / dipped beam | ближний свет | 近光灯 | 110 | — | — | — |
| 103 | `lumbar_support@interior` | lumbar support | поясничная опора | 腰部支撑 | 36 | — | — | — |
| 104 | `massage_seats@interior` | massage seats | массаж сидений | 座椅按摩 | 58 | — | — | — |
| 105 | `matrix_led_headlight@interior` | matrix LED headlight | матричная светодиодная фара | 矩阵式LED大灯 | 0 | — | — | — |
| 106 | `mirror_glass@interior` | mirror glass | зеркальный элемент | 后视镜镜片 | 11 | — | — | — |
| 107 | `mirror_housing@interior` | mirror housing | корпус зеркала | 后视镜壳体 | 0 | — | — | — |
| 108 | `nfc_card_key@interior` | NFC card key | NFC-ключ карта | NFC卡钥匙 | 0 | — | — | — |
| 109 | `nfc_key@interior` | NFC key | NFC-ключ | NFC钥匙 | 0 | — | — | — |
| 110 | `obd2_port@interior` | OBD-II diagnostic port | диагностический разъём OBD-II | OBD-II诊断接口 | 0 | — | — | — |
| 111 | `obdii_port@interior` | OBD-II port / diagnostic connector (under dash) | разъём OBD-II под торпедо | OBD-II接口／诊断接头（仪表台下方） | 0 | — | — | — |
| 112 | `outer_door_handle@interior` | outer door handle | ручка двери (наруж.) | 车门外侧把手 | 0 | — | — | — |
| 113 | `parcel_shelf@interior` | parcel shelf / tonneau cover | полка багажника / шторка | 后备箱隔板/遮物帘 | 0 | — | — | — |
| 114 | `passenger_screen@interior` | passenger entertainment screen | экран пассажира | 副驾娱乐屏 | 83 | — | — | — |
| 115 | `passenger_seat@interior` | passenger seat / front passenger seat | пассажирское сиденье | 前排乘客座椅 | 20 | — | — | — |
| 116 | `pillar_trim@interior` | pillar trim | обшивка стоек кузова | 车柱装饰板 | 0 | — | — | — |
| 117 | `power_liftgate@interior` | power liftgate | электропривод двери багажника | 电动尾门 | 0 | — | — | — |
| 118 | `power_window_motor@interior` | power window motor | электродвигатель стеклоподъёмника | 车窗电机 | 0 | — | — | — |
| 119 | `poweradjustable_seats@interior` | power-adjustable seats | электрорегулировка сидений | 电动调节座椅 | 0 | — | — | — |
| 120 | `quarter_light@interior` | quarter light | форточка (боковое глухое стекло) | 三角窗 | 3 | — | — | — |
| 121 | `rear_armrest@interior` | rear armrest | подлокотник (зад.) | 后排扶手 | 0 | — | — | — |
| 122 | `rear_bumper@interior` | rear bumper | задний бампер | 后保险杠 | 54 | 1 | — | B1450, B1460 |
| 123 | `rear_door@interior` | rear door | дверь (зад.) | 后门 | 16 | — | — | — |
| 124 | `rear_door_hinge@interior` | rear door hinge | петля двери (зад.) | 后门铰链 | 0 | — | — | — |
| 125 | `rear_door_latch@interior` | rear door latch | защёлка двери (зад.) | 后门锁扣 | 0 | — | — | — |
| 126 | `rear_door_lock@interior` | rear door lock | замок двери (зад.) | 后门门锁 | 0 | — | — | — |
| 127 | `rear_fridge@interior` | rear refrigerator | холодильник (задний ряд) | 后排冰箱 | 0 | — | — | — |
| 128 | `rear_inner_door_handle@interior` | rear inner door handle | ручка двери (внутр.) (зад.) | 后门内拉手 | 11 | — | — | — |
| 129 | `rear_left_door_handle@interior` | rear left door handle | ручка двери (зад., лев.) | 后左门把手 | 0 | — | — | — |
| 130 | `rear_left_door_seal@interior` | rear left door seal | уплотнитель двери (зад., лев.) | 后左门密封条 | 0 | — | — | — |
| 131 | `rear_left_seat_belt@interior` | rear left seat belt | ремень безопасности (зад., лев.) | 后排左侧安全带 | 0 | — | — | — |
| 132 | `rear_outer_door_handle@interior` | rear outer door handle | ручка двери (наруж.) (зад.) | 后门外拉手 | 0 | — | — | — |
| 133 | `rear_right_door_handle@interior` | rear right door handle | ручка двери (зад., прав.) | 后右门把手 | 0 | — | — | — |
| 134 | `rear_right_door_seal@interior` | rear right door seal | уплотнитель двери (зад., прав.) | 后右门密封条 | 0 | — | — | — |
| 135 | `rear_right_seat_belt@interior` | rear right seat belt | ремень безопасности (зад., прав.) | 后排右侧安全带 | 0 | — | — | — |
| 136 | `rear_screen@interior` | rear entertainment screen | задний экран развлечений | 后排娱乐屏 | 13 | — | — | — |
| 137 | `rear_seat@interior` | rear seat | заднее сиденье | 后排座椅 | 24 | 6 | 1 | B1450, B1460 |
| 138 | `rear_seat_belt_buckle@interior` | rear seat belt buckle | замок ремня безопасности (зад.) | 后排安全带卡扣 | 0 | — | — | — |
| 139 | `rear_sunroof_glass@interior` | rear sunroof glass | стекло заднего люка | 后天窗玻璃总成 | 1 | — | — | — |
| 140 | `rear_trunk_latch@interior` | rear trunk latch | замок багажника (зад.) | 后行李箱锁扣 | 0 | — | — | — |
| 141 | `reverse_light@interior` | reverse light / backup light | фонарь заднего хода | 倒车灯 | 12 | — | — | — |
| 142 | `right_mirror_glass@interior` | right mirror glass | зеркальный элемент (прав.) | 右后视镜镜片 | 0 | — | — | — |
| 143 | `right_mirror_housing@interior` | right mirror housing | корпус зеркала (прав.) | 右后视镜壳体 | 0 | — | — | — |
| 144 | `rul@interior` | Steering Wheel R — Dashboard | Руль#2 — Приборная панель | 方向盘右 — 仪表板 | 0 | — | — | — |
| 145 | `rul_alt@interior` | Steering Wheel R — Dashboard | Руль (альт.)#2 — Приборная панель | 方向盘右 — 仪表板 | 0 | — | — | — |
| 146 | `rul_ekran@interior` | Steering Wheel | Руль (экран) | 方向盘 | 0 | — | — | — |
| 147 | `seat@interior` | seat | сиденье | 座椅 | 43 | — | 2 | B1450, B1460 |
| 148 | `seat_adjustment_mechanism@interior` | seat adjustment mechanism | механизм регулировки сиденья | 座椅调整机构 | 0 | — | — | — |
| 149 | `seat_backrest@interior` | seat backrest / seatback | спинка сиденья | 座椅靠背 | 150 | — | — | — |
| 150 | `seat_belt_buckle@interior` | seat belt buckle | замок ремня безопасности | 安全带卡扣 | 0 | — | — | — |
| 151 | `seat_cushion@interior` | seat cushion / seat base | подушка сиденья | 座椅坐垫 | 0 | — | — | — |
| 152 | `seat_cushion_seat_base@interior` | seat cushion / seat base | подушка сиденья | 座椅坐垫 | 2 | 4 | — | B1450, B1460 |
| 153 | `seat_heater@interior` | seat heater / power seat | подогрев / электропривод сиденья | 座椅加热/电动座椅 | 0 | — | — | — |
| 154 | `seat_runners@interior` | seat runners / seat rails / seat slides | направляющие сиденья | 座椅滑轨 | 4 | — | — | — |
| 155 | `seat_ventilation@interior` | seat ventilation | вентиляция сидений | 座椅通风 | 72 | — | — | — |
| 156 | `side_mirror@interior` | side mirror | боковое зеркало | 外后视镜 | 236 | — | — | — |
| 157 | `sidenya_zadnie@interior` | Rear Seats — Leather Insert | Сиденья задние#2 — Кожаная вставка | 后排座椅 — 皮革嵌件 | 0 | — | — | — |
| 158 | `smart_key@interior` | smart key | умный ключ | 智能钥匙 | 240 | — | — | — |
| 159 | `softclose_doors@interior` | soft-close doors | двери с доводчиком | 电吸门 | 0 | — | — | — |
| 160 | `speaker@interior` | speaker | динамик | 扬声器 | 9 | — | — | — |
| 161 | `speaker_fl@interior` | speaker (front-left) | динамик (передний левый) | 扬声器(左前) | 0 | — | — | — |
| 162 | `speaker_fr@interior` | speaker (front-right) | динамик (передний правый) | 扬声器(右前) | 0 | — | — | — |
| 163 | `speaker_rl@interior` | speaker (rear-left) | динамик (задний левый) | 扬声器(左后) | 0 | — | — | — |
| 164 | `speaker_rr@interior` | speaker (rear-right) | динамик (задний правый) | 扬声器(右后) | 0 | — | — | — |
| 165 | `steering_wheel@interior` | steering wheel | рулевое колесо / руль | 方向盘 | 515 | 13 | — | C0500, U0100 |
| 166 | `steering_wheel_control_button@interior` | steering wheel control button | кнопка управления на рулевом колесе | 方向盘控制按钮 | 0 | — | — | — |
| 167 | `steering_wheel_display@interior` | steering wheel display | дисплей на рулевом колесе | 方向盘屏总成 | 1 | — | — | — |
| 168 | `steering_wheel_multifunction_buttons@interior` | steering wheel multifunction buttons | мультифункциональные кнопки руля | 方向盘多功能按键总成 | 1 | — | — | — |
| 169 | `sun_visor@interior` | sun visor | солнцезащитный козырёк | 遮阳板 | 0 | 2 | — | B1450, B1460 |
| 170 | `threepoint_seatbelt@interior` | three-point seatbelt | трёхточечный ремень | 三点式安全带 | 0 | — | — | — |
| 171 | `touchscreen@interior` | touchscreen | сенсорный экран | 触摸屏 | 0 | — | — | — |
| 172 | `trim_panel@interior` | trim panel | декоративная панель (обшивка) | 装饰板 | 11 | — | — | — |
| 173 | `trunk_floor@interior` | trunk floor / cargo area | пол багажника / грузовое отделение | 后备箱底板 | 0 | — | — | — |
| 174 | `trunk_latch@interior` | trunk latch | замок багажника | 行李箱锁扣 | 2 | — | — | — |
| 175 | `turn_signal@interior` | turn signal / indicator | указатель поворота / поворотник | 转向灯 | 175 | — | — | — |
| 176 | `vehicle_interior@interior` | vehicle interior / cabin | салон автомобиля | 车辆内饰 / 驾驶舱 | 1 | — | — | — |
| 177 | `ventilated_seat@interior` | ventilated seat / cooled seat | вентилируемое сиденье / охлаждаемое сиденье | 通风座椅 / 冷却座椅 | 0 | — | — | — |
| 178 | `weather_seal@interior` | weather seal / weatherstrip | уплотнитель двери | 密封条 | 0 | — | — | — |
| 179 | `weatherstrip@interior` | weatherstrip | уплотнитель (погодная лента) | 密封条 | 9 | — | — | — |
| 180 | `window_regulator@interior` | power window regulator | стеклоподъёмник | 车窗升降器 | 0 | — | — | — |
| 181 | `wiper_motor@interior` | wiper motor | электродвигатель стеклоочистителей | 雨刷电机 | 0 | — | — | — |
| 182 | `wireless_charging_pad@interior` | wireless charging pad / Qi charging | беспроводная зарядка (Qi) | 无线充电板 / Qi充电 | 0 | — | — | — |
| 183 | `zadnie_sidenya@interior` | Zadnie Sidenya | Задние сиденья | Задние сиденья | 0 | — | — | — |
| 184 | `zerkalo_salonnoe@interior` | Mirror — Finish | Зеркало салонное#2 — Отделка | 后视镜 — 装饰 | 0 | — | — | — |

---

*Источники данных:*
- `frontend/data/architecture/i18n-glossary-data.json` — 1,636 компонентов × 5 языков
- `frontend/data/architecture/system-components.json` — привязка к 3D мешам + DTC
- `frontend/data/architecture/layer-definitions.json` — 8 слоёв визуализации
- `frontend/data/architecture/kb-layer-bridge.json` — маппинг KB→диагностические группы
- `knowledge-base/kb.db` → `chunk_glossary` — 306 терминов привязаны к чанкам KB
