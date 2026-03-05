#!/usr/bin/env python3
"""
LLCAR Diagnostica — Построение DTC базы данных.

Источники:
1. annotation-config.json — 93 аннотации с DTC кодами
2. Встроенный словарь OBD-II кодов (SAE J2012)
3. DTC коды из sections-*.json (извлечённые из мануалов)

Выход: knowledge-base/dtc-database.json
"""

import json
import os
import sys
import glob
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'api'))
from config import KB_DIR, ARCHITECTURE_DIR

# ═══════════════════════════════════════════════════════════
# Встроенный словарь стандартных OBD-II кодов (основные)
# Источник: SAE J2012 / ISO 15031-6
# ═══════════════════════════════════════════════════════════

# Формат: code → (title_en, title_ru, severity, can_drive, system)
# severity: 1=info, 2=low, 3=medium, 4=high, 5=critical
# can_drive: "yes", "yes_limited", "no"

STANDARD_DTC_DB = {
    # ── Powertrain (P0xxx) ────────────────────────────
    "P0010": ("Camshaft Position Actuator Circuit (Bank 1)", "Цепь привода положения распредвала (Банк 1)", 3, "yes_limited", "engine"),
    "P0011": ("Camshaft Position Timing Over-Advanced (Bank 1)", "Опережение фаз распредвала (Банк 1)", 3, "yes_limited", "engine"),
    "P0012": ("Camshaft Position Timing Over-Retarded (Bank 1)", "Запаздывание фаз распредвала (Банк 1)", 3, "yes_limited", "engine"),
    "P0013": ("Camshaft Position Actuator Circuit (Bank 1, Exhaust)", "Цепь привода распредвала (Банк 1, Выпуск)", 3, "yes_limited", "engine"),
    "P0016": ("Crankshaft/Camshaft Position Correlation (Bank 1)", "Корреляция положения коленвала/распредвала (Банк 1)", 4, "yes_limited", "engine"),
    "P0030": ("HO2S Heater Control Circuit (Bank 1, Sensor 1)", "Цепь подогрева кислородного датчика (Банк 1, Датчик 1)", 2, "yes", "engine"),
    "P0100": ("Mass Air Flow Circuit Malfunction", "Неисправность цепи MAF (расходомер воздуха)", 3, "yes_limited", "engine"),
    "P0101": ("Mass Air Flow Circuit Range/Performance", "Диапазон/производительность MAF", 3, "yes_limited", "engine"),
    "P0102": ("Mass Air Flow Circuit Low Input", "Низкий сигнал MAF", 3, "yes_limited", "engine"),
    "P0103": ("Mass Air Flow Circuit High Input", "Высокий сигнал MAF", 3, "yes_limited", "engine"),
    "P0106": ("MAP/BARO Pressure Circuit Range/Performance", "Диапазон/производительность MAP/барометр", 3, "yes_limited", "engine"),
    "P0107": ("MAP/BARO Pressure Circuit Low Input", "Низкий сигнал MAP/барометр", 3, "yes_limited", "engine"),
    "P0110": ("Intake Air Temperature Circuit Malfunction", "Неисправность датчика температуры впускного воздуха", 2, "yes", "engine"),
    "P0115": ("Engine Coolant Temperature Circuit Malfunction", "Неисправность датчика температуры ОЖ", 3, "yes_limited", "engine"),
    "P0116": ("Engine Coolant Temperature Circuit Range/Performance", "Диапазон/производительность датчика температуры ОЖ", 3, "yes_limited", "engine"),
    "P0117": ("Engine Coolant Temperature Circuit Low Input", "Низкий сигнал датчика температуры ОЖ", 3, "yes_limited", "engine"),
    "P0118": ("Engine Coolant Temperature Circuit High Input", "Высокий сигнал датчика температуры ОЖ", 3, "yes_limited", "engine"),
    "P0120": ("Throttle Position Sensor/Switch A Circuit", "Цепь датчика положения дроссельной заслонки A", 4, "yes_limited", "engine"),
    "P0121": ("Throttle Position Sensor/Switch A Range/Performance", "Диапазон/производительность TPS A", 4, "yes_limited", "engine"),
    "P0122": ("Throttle Position Sensor/Switch A Low Input", "Низкий сигнал TPS A", 4, "yes_limited", "engine"),
    "P0123": ("Throttle Position Sensor/Switch A High Input", "Высокий сигнал TPS A", 4, "yes_limited", "engine"),
    "P0130": ("O2 Sensor Circuit (Bank 1, Sensor 1)", "Цепь кислородного датчика (Банк 1, Датчик 1)", 3, "yes_limited", "engine"),
    "P0131": ("O2 Sensor Circuit Low Voltage (Bank 1, Sensor 1)", "Низкое напряжение O2 (Банк 1, Датчик 1)", 3, "yes_limited", "engine"),
    "P0133": ("O2 Sensor Slow Response (Bank 1, Sensor 1)", "Медленный отклик O2 (Банк 1, Датчик 1)", 3, "yes_limited", "engine"),
    "P0171": ("System Too Lean (Bank 1)", "Бедная смесь (Банк 1)", 3, "yes_limited", "engine"),
    "P0172": ("System Too Rich (Bank 1)", "Богатая смесь (Банк 1)", 3, "yes_limited", "engine"),
    "P0174": ("System Too Lean (Bank 2)", "Бедная смесь (Банк 2)", 3, "yes_limited", "engine"),
    "P0175": ("System Too Rich (Bank 2)", "Богатая смесь (Банк 2)", 3, "yes_limited", "engine"),
    "P0217": ("Engine Overheating Condition", "Перегрев двигателя", 5, "no", "engine"),
    "P0299": ("Turbo/Supercharger Underboost", "Недостаточное давление наддува", 4, "yes_limited", "engine"),
    "P0300": ("Random/Multiple Cylinder Misfire Detected", "Обнаружены пропуски зажигания в нескольких цилиндрах", 4, "yes_limited", "engine"),
    "P0301": ("Cylinder 1 Misfire Detected", "Пропуски зажигания в цилиндре 1", 3, "yes_limited", "engine"),
    "P0302": ("Cylinder 2 Misfire Detected", "Пропуски зажигания в цилиндре 2", 3, "yes_limited", "engine"),
    "P0303": ("Cylinder 3 Misfire Detected", "Пропуски зажигания в цилиндре 3", 3, "yes_limited", "engine"),
    "P0304": ("Cylinder 4 Misfire Detected", "Пропуски зажигания в цилиндре 4", 3, "yes_limited", "engine"),
    "P0325": ("Knock Sensor 1 Circuit (Bank 1)", "Цепь датчика детонации 1 (Банк 1)", 3, "yes_limited", "engine"),
    "P0335": ("Crankshaft Position Sensor A Circuit", "Цепь датчика положения коленвала A", 4, "no", "engine"),
    "P0340": ("Camshaft Position Sensor Circuit (Bank 1)", "Цепь датчика положения распредвала (Банк 1)", 4, "yes_limited", "engine"),
    "P0341": ("Camshaft Position Sensor Range/Performance (Bank 1)", "Диапазон/производительность ДПРВ (Банк 1)", 3, "yes_limited", "engine"),
    "P0351": ("Ignition Coil A Primary/Secondary Circuit", "Цепь катушки зажигания A", 3, "yes_limited", "engine"),
    "P0400": ("EGR Flow Malfunction", "Неисправность потока EGR", 3, "yes_limited", "engine"),
    "P0401": ("EGR Insufficient Flow Detected", "Недостаточный поток EGR", 3, "yes_limited", "engine"),
    "P0420": ("Catalyst System Efficiency Below Threshold (Bank 1)", "Эффективность каталитического нейтрализатора ниже порога (Банк 1)", 2, "yes", "engine"),
    "P0430": ("Catalyst System Efficiency Below Threshold (Bank 2)", "Эффективность каталитического нейтрализатора ниже порога (Банк 2)", 2, "yes", "engine"),
    "P0440": ("Evaporative Emission System Malfunction", "Неисправность системы улавливания паров топлива", 2, "yes", "engine"),
    "P0442": ("EVAP Small Leak Detected", "Обнаружена малая утечка EVAP", 2, "yes", "engine"),
    "P0446": ("EVAP Vent System Performance", "Производительность вентиляции EVAP", 2, "yes", "engine"),
    "P0455": ("EVAP Large Leak Detected", "Обнаружена большая утечка EVAP", 2, "yes", "engine"),
    "P0500": ("Vehicle Speed Sensor A", "Датчик скорости автомобиля A", 3, "yes_limited", "drivetrain"),
    "P0505": ("Idle Air Control System", "Система управления холостым ходом", 3, "yes_limited", "engine"),
    "P0507": ("Idle Air Control System RPM Higher Than Expected", "Обороты ХХ выше ожидаемых", 2, "yes", "engine"),
    "P0562": ("System Voltage Low", "Низкое напряжение бортовой сети", 3, "yes_limited", "ev"),
    "P0563": ("System Voltage High", "Высокое напряжение бортовой сети", 3, "yes_limited", "ev"),
    "P0600": ("Serial Communication Link", "Последовательная линия связи", 3, "yes_limited", "ev"),
    "P0700": ("Transmission Control System Malfunction", "Неисправность системы управления КПП", 3, "yes_limited", "drivetrain"),
    "P0705": ("Transmission Range Sensor Circuit (PRNDL Input)", "Цепь датчика диапазона КПП", 3, "yes_limited", "drivetrain"),
    "P0715": ("Input/Turbine Speed Sensor Circuit", "Цепь датчика скорости входного вала КПП", 3, "yes_limited", "drivetrain"),
    "P0720": ("Output Speed Sensor Circuit", "Цепь датчика скорости выходного вала КПП", 3, "yes_limited", "drivetrain"),

    # ── Chassis (C0xxx) ─────────────────────────────
    "C0035": ("Left Front Wheel Speed Sensor Circuit", "Цепь датчика скорости ЛП колеса", 4, "yes_limited", "brakes"),
    "C0040": ("Right Front Wheel Speed Sensor Circuit", "Цепь датчика скорости ПП колеса", 4, "yes_limited", "brakes"),
    "C0045": ("Left Rear Wheel Speed Sensor Circuit", "Цепь датчика скорости ЛЗ колеса", 4, "yes_limited", "brakes"),
    "C0050": ("Right Rear Wheel Speed Sensor Circuit", "Цепь датчика скорости ПЗ колеса", 4, "yes_limited", "brakes"),
    "C0060": ("ABS System Malfunction", "Неисправность системы ABS", 5, "yes_limited", "brakes"),
    "C0070": ("ABS Pump Motor Circuit", "Цепь мотора насоса ABS", 5, "yes_limited", "brakes"),
    "C0110": ("Pump Motor Circuit", "Цепь мотора насоса", 4, "yes_limited", "brakes"),
    "C0121": ("Valve Relay Circuit", "Цепь реле клапана", 4, "yes_limited", "brakes"),
    "C0131": ("ABS/TCS Brake Switch Circuit", "Цепь датчика педали тормоза ABS/TCS", 3, "yes_limited", "brakes"),
    "C0161": ("ABS/TCS Brake Switch Circuit Range/Performance", "Диапазон/производительность датчика педали тормоза", 3, "yes_limited", "brakes"),
    "C0265": ("EBCM (Electronic Brake Control Module) Relay Circuit", "Цепь реле EBCM", 4, "yes_limited", "brakes"),
    "C0550": ("ECU Performance", "Производительность ЭБУ", 4, "yes_limited", "brakes"),
    "C0710": ("Steering Position Sensor", "Датчик положения руля", 3, "yes_limited", "brakes"),
    "C0900": ("Device Performance (General)", "Производительность устройства (общая)", 3, "yes_limited", "sensors"),
    "C0920": ("Device Range/Performance", "Диапазон/производительность устройства", 3, "yes_limited", "sensors"),

    # ── Body (B0xxx) ────────────────────────────────
    "B0001": ("Driver Frontal Stage 1 Deployment Control", "Управление раскрытием подушки водителя (стадия 1)", 5, "yes_limited", "sensors"),
    "B0002": ("Driver Frontal Stage 2 Deployment Control", "Управление раскрытием подушки водителя (стадия 2)", 5, "yes_limited", "sensors"),
    "B0010": ("Passenger Frontal Stage 1 Deployment Control", "Управление раскрытием подушки пассажира (стадия 1)", 5, "yes_limited", "sensors"),
    "B0050": ("Crash Sensor - Front", "Датчик удара — передний", 5, "yes_limited", "sensors"),
    "B0051": ("Crash Sensor - Right Side", "Датчик удара — правая сторона", 5, "yes_limited", "sensors"),
    "B0052": ("Crash Sensor - Left Side", "Датчик удара — левая сторона", 5, "yes_limited", "sensors"),
    "B0070": ("Seat Belt Pretensioner Deployment Control (Driver)", "Управление преднатяжителем ремня (Водитель)", 5, "yes_limited", "sensors"),
    "B0100": ("Electronic Frontal Sensor 1", "Электронный передний датчик 1", 4, "yes_limited", "sensors"),
    "B1000": ("ECU Malfunction", "Неисправность ЭБУ", 4, "yes_limited", "ev"),
    "B1200": ("Climate Control Push Button Circuit", "Цепь кнопки управления климатом", 2, "yes", "hvac"),
    "B1310": ("HVAC Recirculation Motor Circuit", "Цепь мотора рециркуляции HVAC", 2, "yes", "hvac"),
    "B1325": ("HVAC Blower Motor Relay Circuit", "Цепь реле вентилятора HVAC", 3, "yes", "hvac"),
    "B1340": ("A/C Compressor Relay Circuit", "Цепь реле компрессора кондиционера", 3, "yes_limited", "hvac"),
    "B1480": ("Headlamp - Left Low Beam Circuit", "Цепь ближнего света — левая фара", 3, "yes_limited", "body"),
    "B1485": ("Headlamp - Right Low Beam Circuit", "Цепь ближнего света — правая фара", 3, "yes_limited", "body"),
    "B1500": ("Driver Door Lock Circuit", "Цепь замка водительской двери", 2, "yes", "interior"),
    "B1510": ("Passenger Door Lock Circuit", "Цепь замка пассажирской двери", 2, "yes", "interior"),
    "B1600": ("Horn Relay Circuit", "Цепь реле звукового сигнала", 2, "yes", "body"),
    "B1650": ("Front Wiper Motor Circuit", "Цепь мотора передних дворников", 2, "yes", "body"),
    "B1900": ("Communication Bus Off", "Обрыв шины связи", 4, "yes_limited", "ev"),

    # ── Network (U0xxx) ─────────────────────────────
    "U0001": ("High Speed CAN Communication Bus", "Шина CAN высокоскоростная", 4, "yes_limited", "ev"),
    "U0002": ("High Speed CAN Communication Bus Performance", "Производительность шины CAN", 4, "yes_limited", "ev"),
    "U0073": ("Control Module Communication Bus Off", "Обрыв шины связи блока управления", 4, "yes_limited", "ev"),
    "U0100": ("Lost Communication With ECM/PCM A", "Потеря связи с ЭБУ двигателя A", 5, "no", "engine"),
    "U0101": ("Lost Communication With TCM", "Потеря связи с ЭБУ КПП", 4, "yes_limited", "drivetrain"),
    "U0103": ("Lost Communication With Gear Shift Module", "Потеря связи с модулем переключения передач", 3, "yes_limited", "drivetrain"),
    "U0121": ("Lost Communication With ABS Control Module", "Потеря связи с блоком ABS", 5, "yes_limited", "brakes"),
    "U0122": ("Lost Communication With Vehicle Dynamics Control Module", "Потеря связи с блоком динамики автомобиля", 4, "yes_limited", "brakes"),
    "U0126": ("Lost Communication With Steering Angle Sensor Module", "Потеря связи с датчиком угла руля", 3, "yes_limited", "brakes"),
    "U0140": ("Lost Communication With Body Control Module", "Потеря связи с блоком управления кузовом", 4, "yes_limited", "body"),
    "U0151": ("Lost Communication With Restraints Control Module", "Потеря связи с блоком систем безопасности", 5, "yes_limited", "sensors"),
    "U0155": ("Lost Communication With Instrument Panel Cluster", "Потеря связи с панелью приборов", 3, "yes_limited", "interior"),
    "U0164": ("Lost Communication With HVAC Control Module", "Потеря связи с блоком климат-контроля", 2, "yes", "hvac"),
    "U0167": ("Lost Communication With Vehicle Immobilizer Control Module", "Потеря связи с иммобилайзером", 4, "yes_limited", "ev"),
    "U0168": ("Lost Communication With Vehicle Security Control Module", "Потеря связи с модулем охранной системы", 3, "yes_limited", "ev"),
    "U0184": ("Lost Communication With Radio", "Потеря связи с мультимедиа", 2, "yes", "interior"),
    "U0185": ("Lost Communication With GPS Module", "Потеря связи с GPS модулем", 2, "yes", "sensors"),
    "U0199": ("Lost Communication With Door Control Module A", "Потеря связи с модулем управления дверью A", 2, "yes", "interior"),
    "U0235": ("Lost Communication With Cruise Control Front Distance Range Sensor", "Потеря связи с радаром круиз-контроля", 4, "yes_limited", "sensors"),
    "U0293": ("Lost Communication With HV Battery Charger Module A", "Потеря связи с зарядным модулем ВВ батареи A", 4, "yes_limited", "ev"),
    "U0302": ("Software Incompatibility With Radar Sensor", "Несовместимость ПО с радарным датчиком", 3, "yes_limited", "sensors"),
    "U0303": ("Software Incompatibility With Radar Sensor B", "Несовместимость ПО с радарным датчиком B", 3, "yes_limited", "sensors"),
    "U0305": ("Software Incompatibility With LiDAR Sensor", "Несовместимость ПО с LiDAR датчиком", 3, "yes_limited", "sensors"),
    "U0401": ("Invalid Data Received From ECM/PCM A", "Некорректные данные от ЭБУ двигателя A", 4, "yes_limited", "engine"),
    "U0404": ("Invalid Data Received From Gear Shift Module", "Некорректные данные от модуля переключения передач", 3, "yes_limited", "drivetrain"),
    "U0415": ("Invalid Data Received From ABS Control Module", "Некорректные данные от блока ABS", 4, "yes_limited", "brakes"),
    "U0416": ("Invalid Data Received From Vehicle Dynamics Control", "Некорректные данные от блока динамики", 3, "yes_limited", "brakes"),
    "U1000": ("CAN Timeout", "Таймаут CAN", 4, "yes_limited", "ev"),
    "U2000": ("General Network Communication Error", "Общая ошибка сетевой связи", 3, "yes_limited", "ev"),
}

# ═══════════════════════════════════════════════════════════
# Вероятные причины по категориям
# ═══════════════════════════════════════════════════════════

GENERIC_CAUSES = {
    'engine': ["Неисправность датчика", "Повреждение проводки", "Неисправность ЭБУ", "Загрязнение/износ компонента"],
    'drivetrain': ["Износ механических компонентов", "Утечка жидкости", "Повреждение проводки", "Неисправность ЭБУ КПП"],
    'ev': ["Деградация ВВ батареи", "Повреждение изоляции", "Неисправность BMS", "Проблемы с проводкой"],
    'brakes': ["Износ тормозных колодок", "Неисправность датчика ABS", "Утечка тормозной жидкости", "Повреждение проводки"],
    'sensors': ["Загрязнение датчика", "Повреждение проводки", "Несовместимость ПО", "Механическое повреждение"],
    'hvac': ["Утечка хладагента", "Неисправность компрессора", "Засорение фильтра", "Повреждение проводки"],
    'interior': ["Повреждение проводки", "Неисправность модуля", "Механический износ", "Проблемы с CAN шиной"],
    'body': ["Перегоревшая лампа", "Повреждение проводки", "Неисправность реле", "Окисление контактов"],
}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(path) / 1024
    print(f"  Сохранено: {path} ({size_kb:.1f} КБ)")


def load_annotation_dtc_codes():
    """Извлечь DTC коды из annotation-config.json с привязкой к компонентам."""
    path = os.path.join(ARCHITECTURE_DIR, 'annotation-config.json')
    if not os.path.exists(path):
        print(f"  [!] annotation-config.json не найден: {path}")
        return {}

    data = load_json(path)
    annotations = data.get('annotations', {})

    # dtc_code → [glossary_id, ...]
    dtc_to_components = {}
    for gid, ann in annotations.items():
        for dtc in ann.get('dtcCodes', []):
            if dtc not in dtc_to_components:
                dtc_to_components[dtc] = []
            dtc_to_components[dtc].append(gid)

    unique_dtc = set()
    for gid, ann in annotations.items():
        unique_dtc.update(ann.get('dtcCodes', []))

    print(f"  Аннотации: {len(annotations)} записей, {len(unique_dtc)} уникальных DTC кодов")
    return dtc_to_components


def load_dtc_from_sections():
    """Извлечь DTC коды из sections-*.json."""
    pattern = os.path.join(KB_DIR, 'sections-*.json')
    files = glob.glob(pattern)
    dtc_pattern = re.compile(r'\b([PCBU]\d{4})\b')

    all_dtc = set()
    for f in files:
        data = load_json(f)
        for section in data.get('sections', []):
            text = section.get('title', '') + ' ' + section.get('content', '')
            codes = dtc_pattern.findall(text)
            all_dtc.update(codes)

    print(f"  Из sections: {len(all_dtc)} DTC кодов из {len(files)} файлов")
    return all_dtc


def generate_generic_dtc_range(prefix, start, end, system, en_template, ru_template, severity, can_drive):
    """Генерация DTC кодов для диапазона (P0100-P0199 и т.д.)."""
    result = {}
    for i in range(start, end + 1):
        code = f"{prefix}{i:04d}"
        if code not in STANDARD_DTC_DB:
            result[code] = {
                'title_en': en_template.format(i),
                'title_ru': ru_template.format(i),
                'title_zh': '',
                'severity': severity,
                'can_drive': can_drive,
                'probable_causes': GENERIC_CAUSES.get(system, ["Неизвестная причина"]),
                'related_components': [],
                'system': system,
            }
    return result


def build_database():
    """Собрать полную DTC базу данных."""
    print("=" * 60)
    print("LLCAR KB — Построение DTC базы данных")
    print("=" * 60)

    # 1. Загружаем DTC из аннотаций
    print("\n--- Шаг 1: DTC из аннотаций ---")
    dtc_to_components = load_annotation_dtc_codes()

    # 2. Загружаем DTC из секций
    print("\n--- Шаг 2: DTC из секций мануалов ---")
    section_dtc_codes = load_dtc_from_sections()

    # 3. Строим базу из встроенного словаря
    print("\n--- Шаг 3: Построение базы ---")
    database = {}

    # Добавляем стандартные коды
    for code, (en, ru, severity, can_drive, system) in STANDARD_DTC_DB.items():
        database[code] = {
            'title_en': en,
            'title_ru': ru,
            'title_zh': '',
            'severity': severity,
            'can_drive': can_drive,
            'probable_causes': GENERIC_CAUSES.get(system, []),
            'related_components': dtc_to_components.get(code, []),
            'system': system,
        }

    print(f"  Стандартных кодов: {len(database)}")

    # 4. Добавляем коды из аннотаций, которых нет в стандартном словаре
    added_from_ann = 0
    for code, components in dtc_to_components.items():
        if code not in database:
            # Определяем систему по первой букве
            system_map = {'P': 'engine', 'C': 'brakes', 'B': 'body', 'U': 'ev'}
            system = system_map.get(code[0], 'ev')

            # Определяем по компоненту
            for comp in components:
                layer = comp.split('@')[1] if '@' in comp else ''
                if layer:
                    system = layer
                    break

            database[code] = {
                'title_en': f"DTC {code} (Li Auto specific)",
                'title_ru': f"Код {code} (специфичный для Li Auto)",
                'title_zh': f"故障码 {code} (理想汽车专用)",
                'severity': 3,
                'can_drive': 'yes_limited',
                'probable_causes': GENERIC_CAUSES.get(system, []),
                'related_components': components,
                'system': system,
            }
            added_from_ann += 1

    print(f"  Добавлено из аннотаций: {added_from_ann}")

    # 5. Добавляем коды из секций, которых ещё нет
    added_from_sections = 0
    for code in section_dtc_codes:
        if code not in database:
            system_map = {'P': 'engine', 'C': 'brakes', 'B': 'body', 'U': 'ev'}
            system = system_map.get(code[0], 'ev')
            database[code] = {
                'title_en': f"DTC {code}",
                'title_ru': f"Код {code}",
                'title_zh': f"故障码 {code}",
                'severity': 3,
                'can_drive': 'yes_limited',
                'probable_causes': GENERIC_CAUSES.get(system, []),
                'related_components': [],
                'system': system,
            }
            added_from_sections += 1

    print(f"  Добавлено из секций: {added_from_sections}")

    # 6. Сохраняем
    output_path = os.path.join(KB_DIR, 'dtc-database.json')
    output = {
        'meta': {
            'version': '1.0',
            'totalCodes': len(database),
            'sources': {
                'standard_obd2': len(STANDARD_DTC_DB),
                'annotation_config': added_from_ann,
                'manual_sections': added_from_sections,
            },
            'systems': {},
        },
        'codes': database,
    }

    # Статистика по системам
    for code_data in database.values():
        sys_name = code_data.get('system', 'unknown')
        output['meta']['systems'][sys_name] = output['meta']['systems'].get(sys_name, 0) + 1

    save_json(output, output_path)

    # Итоги
    print(f"\n{'=' * 60}")
    print(f"Итого DTC кодов: {len(database)}")
    for sys_name, count in sorted(output['meta']['systems'].items(), key=lambda x: -x[1]):
        print(f"  {sys_name}: {count}")
    print("=" * 60)


if __name__ == '__main__':
    build_database()
