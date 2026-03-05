#!/usr/bin/env python3
"""
Генератор component-map.json для Li Auto L7 и L9.

Читает GLB-модели, классифицирует ноды по системам,
назначает DTC-коды и создает JSON по схеме component-map.schema.json.
"""

import struct
import json
import os
import re
import sys

# Пути
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Diagnostica/
KB_DIR = os.path.join(BASE_DIR, "knowledge-base")


# ============================================================
# 1. Чтение GLB
# ============================================================

def read_glb_json(path):
    """Прочитать JSON-chunk из GLB файла."""
    with open(path, "rb") as f:
        magic = f.read(4)
        if magic != b"glTF":
            raise ValueError(f"Not a GLB file: {path}")
        version = struct.unpack("<I", f.read(4))[0]
        length = struct.unpack("<I", f.read(4))[0]
        chunk_len = struct.unpack("<I", f.read(4))[0]
        chunk_type = struct.unpack("<I", f.read(4))[0]
        json_data = f.read(chunk_len).decode("utf-8")
        return json.loads(json_data)


def extract_nodes(glb_data):
    """Извлечь mesh-ноды и group-ноды из GLB JSON."""
    nodes = glb_data.get("nodes", [])
    mesh_nodes = []
    group_nodes = []

    for i, node in enumerate(nodes):
        name = node.get("name", f"node_{i}")
        has_mesh = "mesh" in node
        children = node.get("children", [])

        # Найти родителя
        parent_name = None
        for j, pnode in enumerate(nodes):
            if i in pnode.get("children", []):
                parent_name = pnode.get("name", f"node_{j}")
                break

        entry = {
            "name": name,
            "index": i,
            "parent": parent_name,
            "has_mesh": has_mesh,
            "children": [nodes[c].get("name", f"node_{c}") for c in children],
        }

        if has_mesh:
            mesh_nodes.append(entry)
        elif children:
            group_nodes.append(entry)

    return mesh_nodes, group_nodes


# ============================================================
# 2. Системы и ключевые слова
# ============================================================

SYSTEMS = {
    "body": {
        "systemId": "body",
        "label_ru": "Кузов",
        "color": "#4488CC",
        "dtc_prefix": "B1",
        "manualChapters": ["1-19", "1-38"],
    },
    "glass": {
        "systemId": "glass",
        "label_ru": "Остекление",
        "color": "#66CCEE",
        "dtc_prefix": "B1",
        "manualChapters": ["1-23", "1-38"],
    },
    "lighting": {
        "systemId": "lighting",
        "label_ru": "Светотехника",
        "color": "#FFDD00",
        "dtc_prefix": "B1",
        "manualChapters": ["1-32", "1-25"],
    },
    "powertrain": {
        "systemId": "powertrain",
        "label_ru": "Силовой агрегат",
        "color": "#FF4444",
        "dtc_prefix": "P0",
        "manualChapters": ["1-13", "1-30"],
    },
    "energy": {
        "systemId": "energy",
        "label_ru": "Энергосистема",
        "color": "#00CC66",
        "dtc_prefix": "P0A",
        "manualChapters": ["1-35"],
    },
    "chassis": {
        "systemId": "chassis",
        "label_ru": "Шасси",
        "color": "#FF8800",
        "dtc_prefix": "C0",
        "manualChapters": ["1-34", "1-30"],
    },
    "wheels": {
        "systemId": "wheels",
        "label_ru": "Колёса и шины",
        "color": "#888888",
        "dtc_prefix": "C0",
        "manualChapters": ["1-38", "1-30"],
    },
    "interior": {
        "systemId": "interior",
        "label_ru": "Интерьер",
        "color": "#AA66CC",
        "dtc_prefix": "B1",
        "manualChapters": ["1-20", "1-21", "1-24", "1-26"],
    },
    "exterior": {
        "systemId": "exterior",
        "label_ru": "Экстерьер",
        "color": "#66AA44",
        "dtc_prefix": "B1",
        "manualChapters": ["1-10"],
    },
    "electronics": {
        "systemId": "electronics",
        "label_ru": "Электроника",
        "color": "#CC44FF",
        "dtc_prefix": "U0",
        "manualChapters": ["1-33", "1-16"],
    },
}

SYSTEM_COLORS = {
    "body": {"normal": "#4488CC", "warning": "#FFAA00", "critical": "#FF0000"},
    "glass": {"normal": "#66CCEE", "warning": "#FFAA00", "critical": "#FF0000"},
    "lighting": {"normal": "#FFDD00", "warning": "#FFAA00", "critical": "#FF0000"},
    "powertrain": {"normal": "#FF4444", "warning": "#FFAA00", "critical": "#FF0000"},
    "energy": {"normal": "#00CC66", "warning": "#FFAA00", "critical": "#FF0000"},
    "chassis": {"normal": "#FF8800", "warning": "#FFAA00", "critical": "#FF0000"},
    "wheels": {"normal": "#888888", "warning": "#FFAA00", "critical": "#FF0000"},
    "interior": {"normal": "#AA66CC", "warning": "#FFAA00", "critical": "#FF0000"},
    "exterior": {"normal": "#66AA44", "warning": "#FFAA00", "critical": "#FF0000"},
    "electronics": {"normal": "#CC44FF", "warning": "#FFAA00", "critical": "#FF0000"},
}

# Ключевые слова для классификации (русские имена Li7)
KEYWORD_RULES_RU = [
    # energy
    (r"(?i)батаре|battery|проводка|инвертор|охлаждение батаре|battery.cooling|wiring|lючок зарядки|зарядк", "energy"),
    # wheels
    (r"(?i)шина|колесо|wheel|tire|_wheel_|hub_lf", "wheels"),
    # chassis - physical steering/suspension/brake (BEFORE interior to catch steeringbox)
    (r"(?i)тормоз|brake|амортизатор|shock|пружина|spring|рычаг\b|arm|стабилизатор|swaybar|подрамник|subframe|стойка передн|strut|рулев.*механ|steeringbox|полуось|halfshaft|ступиц|hub_|подвеск|suspension|пневмоподвеска|air.suspension|дифференциал|diff|кардан|driveshaft|раздатк|transfercase|тяга|tierod", "chassis"),
    # interior (steering wheel, screens, seats etc.)
    (r"(?i)сиденье|seat|руль|li9_steer|педаль|экран|приборн|panel|бардачок|козырёк|зеркало салон|ароматизат|индикатор|монитор|dash|salon|салон|подрулев|подушка сиденья|подголовник|кнопк|кожан|обивк|ковролин|потолок|аварийк|HUD|спидометр|дисплей|center.screen", "interior"),
    # powertrain
    (r"(?i)двигатель|engine|мотор|emotor|коллектор|exhaust|выхлоп|генератор|топливн|fuel|бак|лючок бака|трансмиссия|transmission|впуск|дроссел|крепление э/мотор|emotor.mount", "powertrain"),
    # lighting
    (r"(?i)фар[аыеу]|headlight|фонар|taillight|ДХО|ходов|повторитель|поворотник|огн[иьей]|подсветк|плафон|свет", "lighting"),
    # glass
    (r"(?i)стекло|glass|windshield|лобов|тонировк|маркировк", "glass"),
    # body
    (r"(?i)капот|hood|крыш[аеку]|roof|дверь|door|багажник|tailgate|бампер|bumper|крыло|fender|кузов|body|каркас|порог|уплотнитель|reinforcement|днищ|underbody|dno|tubs|prorabot|четвертн|накладка люка|шильдик|декор|кронштейн|арка|подкрылок|воздуховод|молдинг", "body"),
    # exterior
    (r"(?i)зеркало прав|зеркало лев|mirror|номерн|lettering|надпись|рамка номер|grill|grille|решётк", "exterior"),
    # electronics
    (r"(?i)датчик|камер|lidar|radar|блок управл|xcu\b|hu\b|sensor", "electronics"),
    # energy (additional)
    (r"(?i)радиатор|radiator", "energy"),
]

# Ключевые слова для классификации (английские имена Li9)
KEYWORD_RULES_EN = KEYWORD_RULES_RU  # Same rules work for both


def classify_node(name):
    """Классифицировать ноду по имени в систему."""
    for pattern, system in KEYWORD_RULES_RU:
        if re.search(pattern, name):
            return system
    return "body"  # По умолчанию — кузов


# ============================================================
# 3. DTC-коды
# ============================================================

DTC_BY_SYSTEM = {
    "energy": ["P0A80", "P0A7F", "P3000", "P0AA6", "P0A09"],
    "powertrain": ["P0300", "P0171", "P0A0F", "P0A1A"],
    "chassis": ["C0035", "C0036", "C0037", "C0038", "C0500", "C0550"],
    "lighting": ["B1250", "B1251", "B1260", "B1261", "B1262", "B1263"],
    "body": ["B1011", "B1012", "B1013", "B1014", "B1019", "B1020"],
    "interior": ["B1450", "B1460", "B1400"],
    "glass": [],
    "wheels": [],
    "exterior": ["B1501", "B1502"],
    "electronics": ["U0100", "U0155"],
}

# Specific DTC assignment per keyword
DTC_SPECIFIC = {
    # Energy
    r"(?i)батаре|battery": ["P0A80", "P0A7F", "P3000", "P0AA6"],
    r"(?i)проводка|wiring": ["P0A09", "P0AA6"],
    r"(?i)инвертор": ["P0A09"],
    r"(?i)охлаждение|cooling": ["P0A7F"],
    r"(?i)радиатор|radiator": ["P0A7F"],
    r"(?i)зарядк": ["P0A80", "P3000"],
    # Powertrain
    r"(?i)двигатель|engine": ["P0300", "P0171", "P0A0F"],
    r"(?i)мотор.*передн|emotor.f": ["P0A1A"],
    r"(?i)мотор.*задн|emotor.r": ["P0A1A"],
    r"(?i)выхлоп|exhaust": ["P0420", "P0430"],
    r"(?i)коллектор|впуск": ["P0171"],
    r"(?i)топливн|fuel|бак": ["P0171", "P0300"],
    r"(?i)трансмисс|transmission": ["P0700", "P0715"],
    r"(?i)дроссел": ["P0121", "P0122"],
    # Chassis
    r"(?i)тормоз.*ПЛ|brake.*FL": ["C0035", "C0040"],
    r"(?i)тормоз.*ПП|brake.*FR": ["C0036", "C0041"],
    r"(?i)тормоз.*ЗЛ|brake.*RL": ["C0037", "C0042"],
    r"(?i)тормоз.*ЗП|brake.*RR": ["C0038", "C0043"],
    r"(?i)тормоз|brake": ["C0035", "C0036", "C0037", "C0038"],
    r"(?i)рулев|steer": ["C0500"],
    r"(?i)подвеск|suspension|пневмоподвеск|air.suspension": ["C0550", "C0500"],
    r"(?i)стабилиз|swaybar": ["C0550"],
    r"(?i)амортизат|shock": ["C0550"],
    r"(?i)пружин|spring": ["C0550"],
    r"(?i)рычаг|arm": ["C0550"],
    r"(?i)подрамник|subframe": ["C0550"],
    r"(?i)ступиц|hub": ["C0035", "C0036"],
    r"(?i)полуось|halfshaft": ["C0550"],
    r"(?i)тяга|tierod": ["C0500"],
    r"(?i)раздатк|transfercase": ["P0841"],
    r"(?i)дифференциал|diff": ["C0550"],
    r"(?i)кардан|driveshaft": ["P0500"],
    # Lighting
    r"(?i)фара.*прав|headlight.*R": ["B1251"],
    r"(?i)фара.*лев|headlight.*L|headlight(?!.*R)": ["B1250"],
    r"(?i)фонар.*лев|taillight.*L": ["B1260", "B1262"],
    r"(?i)фонар.*прав|taillight.*R": ["B1261", "B1263"],
    r"(?i)ДХО|ходов": ["B1260"],
    r"(?i)повторитель|поворотник": ["B1260"],
    # Body
    r"(?i)дверь.*передн.*лев|door.*FL": ["B1011"],
    r"(?i)дверь.*передн.*прав|door.*FR": ["B1012"],
    r"(?i)дверь.*задн.*лев|door.*RL": ["B1013"],
    r"(?i)дверь.*задн.*прав|door.*RR": ["B1014"],
    r"(?i)багажник|tailgate": ["B1019", "B1020"],
    r"(?i)капот|hood": ["B1011"],
    # Interior
    r"(?i)сиденье.*ПЛ|seat.*FL": ["B1450"],
    r"(?i)сиденье.*ПП|seat.*FR": ["B1460"],
    r"(?i)руль|steer.*wheel": ["C0500"],
    r"(?i)экран.*центр|center.screen|приборн": ["U0100"],
    # Exterior
    r"(?i)зеркало.*прав|mirror.*R": ["B1502"],
    r"(?i)зеркало.*лев|mirror.*L": ["B1501"],
    # Electronics
    r"(?i)блок управл|xcu|hu\b": ["U0100", "U0155"],
}


def get_dtc_codes(name, system):
    """Назначить DTC-коды по имени компонента."""
    codes = set()
    for pattern, dtc_list in DTC_SPECIFIC.items():
        if re.search(pattern, name):
            codes.update(dtc_list)
    if not codes:
        codes.update(DTC_BY_SYSTEM.get(system, [])[:2])
    return sorted(codes)


# ============================================================
# 4. Связывание с разделами мануала
# ============================================================

MANUAL_SECTION_MAP = {
    "energy": ["1-35"],
    "powertrain": ["1-13", "1-30"],
    "chassis": ["1-34", "1-30"],
    "lighting": ["1-32"],
    "body": ["1-19", "1-38"],
    "glass": ["1-23"],
    "wheels": ["1-38", "1-30"],
    "interior": ["1-20", "1-21"],
    "exterior": ["1-10"],
    "electronics": ["1-33", "1-16"],
}

# More specific
MANUAL_SPECIFIC = {
    r"(?i)батаре|battery|зарядк": ["1-35"],
    r"(?i)шина|колесо|wheel|tire": ["1-38", "1-30"],
    r"(?i)тормоз|brake": ["1-34"],
    r"(?i)фар|headlight": ["1-32"],
    r"(?i)сиденье|seat": ["1-20"],
    r"(?i)дверь|door": ["1-19"],
    r"(?i)руль|steer": ["1-21"],
    r"(?i)зеркало|mirror": ["1-21"],
    r"(?i)подвеск|suspension|пневмоподвеск": ["1-34"],
    r"(?i)двигатель|engine|мотор|emotor": ["1-13"],
    r"(?i)выхлоп|exhaust": ["1-11"],
    r"(?i)стекло|glass|windshield": ["1-23"],
    r"(?i)капот|hood": ["1-38"],
    r"(?i)экран|монитор|dash|приборн": ["1-16"],
    r"(?i)кондиц|аромат": ["1-24"],
    r"(?i)козыр": ["1-27"],
    r"(?i)люк": ["1-23"],
    r"(?i)багажник|tailgate": ["1-19"],
}


def get_manual_sections(name, system):
    """Получить разделы мануала для компонента."""
    sections = set()
    for pattern, sec_list in MANUAL_SPECIFIC.items():
        if re.search(pattern, name):
            sections.update(sec_list)
    if not sections:
        sections.update(MANUAL_SECTION_MAP.get(system, []))
    return sorted(sections)


# ============================================================
# 5. Спецификации из l9-config.json
# ============================================================

SPECS_MAP = {
    r"(?i)батаре|battery": {
        "capacity": "52.3 кВт·ч",
        "type": "Тернарная литиевая",
        "dc_charge_time": "25 мин (20%-80%)",
        "warranty": "8 лет или 160 000 км",
    },
    r"(?i)шина|tire": {
        "size": "265/45 R21",
        "type": "Silent Tires",
    },
    r"(?i)колесо|wheel|_wheel_": {
        "size": "21\"",
        "options": "Silver-Grey / Black-Grey",
    },
    r"(?i)двигатель|engine": {
        "type": "1.5T I4 Range Extender",
        "fuel": "АИ-95",
        "fuel_tank_l": 65,
    },
    r"(?i)мотор.*передн|emotor.*f": {
        "type": "5-in-1 передний привод",
        "power_kw": 130,
        "torque_nm": 220,
    },
    r"(?i)мотор.*задн|emotor.*r": {
        "type": "3-in-1 задний привод",
        "power_kw": 200,
        "torque_nm": 400,
    },
    r"(?i)пневмоподвеск|air.suspension": {
        "type": "Magic Carpet Air Suspension Max",
        "dual_chamber": True,
        "offroad_raise_mm": 40,
        "warranty": "8 лет или 160 000 км",
    },
    r"(?i)экран.*центр|center.screen": {
        "size": "15.7\" 3K OLED",
        "chip": "Qualcomm Snapdragon 8295P",
    },
    r"(?i)рулев.*механ|steeringbox": {
        "type": "Переменное усилие EPS",
    },
    r"(?i)тормоз|brake": {
        "type": "Вентилируемые дисковые тормоза",
    },
    r"(?i)подвеск.*передн|strut|suspension.*front": {
        "type": "Двухрычажная передняя подвеска",
    },
    r"(?i)подвеск.*задн|suspension.*rear|пружина.*задн|рычаг.*задн": {
        "type": "Пятирычажная задняя подвеска",
    },
}


def get_specs(name):
    """Получить технические характеристики по имени."""
    for pattern, specs in SPECS_MAP.items():
        if re.search(pattern, name):
            return specs
    return None


# ============================================================
# 6. Layer assignment
# ============================================================

LAYER_MAP = {
    "chassis": 0,
    "powertrain": 1,
    "energy": 2,
    "wheels": 3,
    "interior": 4,
    "lighting": 5,
    "glass": 6,
    "exterior": 7,
    "body": 8,
    "electronics": 9,
}

XRAY_SYSTEMS = {"body", "glass", "exterior"}


# ============================================================
# 7. Display name generation
# ============================================================

def make_display_name(mesh_name):
    """Очистить имя для отображения."""
    name = mesh_name
    # Remove #2 suffix
    name = re.sub(r"#\d+$", "", name)
    # Remove " — SubPart" suffix for child meshes
    if " — " in name:
        parts = name.split(" — ")
        return parts[0].strip() + " — " + parts[1].strip()
    return name.strip()


def make_display_name_en(mesh_name):
    """Создать русское отображаемое имя для английского меша Li9."""
    EN_TO_RU = {
        "li9_krilia": "Подкрылки",
        "li9_bumperbar_F": "Усилитель бампера передний",
        "li9_radiator": "Радиатор",
        "li9_reinforcement_F": "Усиление передней части",
        "x5mf95racing_diff_F": "Передний дифференциал",
        "li9_engine_v8": "Двигатель (увеличитель запаса хода)",
        "li9_transmission": "Трансмиссия",
        "li9_upperarm_R": "Верхний рычаг задний",
        "li9_underbody_cladding": "Защита днища",
        "li9_transfercase": "Раздаточная коробка",
        "li9_tierod_R": "Рулевая тяга задняя",
        "li9_tierod_F": "Рулевая тяга передняя",
        "li9_swaybar_R": "Стабилизатор задний",
        "li9_swaybar_F": "Стабилизатор передний",
        "li9_subframe_R": "Подрамник задний",
        "li9_subframe_F": "Подрамник передний",
        "li9_strut_F": "Стойка передняя",
        "li9_steeringbox": "Рулевой механизм",
        "li9_spring_R": "Пружина задняя",
        "li9_shock_R": "Амортизатор задний",
        "li9_lowerarm_R": "Нижний рычаг задний",
        "li9_lowerarm_F_b": "Нижний рычаг передний Б",
        "li9_lowerarm_F_a": "Нижний рычаг передний А",
        "li9_hub_R": "Ступица задняя",
        "li9_hub_F": "Ступица передняя",
        "li9_heatshield": "Теплозащита",
        "li9_halfshaft_R": "Полуось задняя",
        "li9_halfshaft_F": "Полуось передняя",
        "li9_fueltank": "Топливный бак",
        "li9_exhaust_R": "Выхлопная система правая",
        "li9_exhaust_L_b": "Выхлопная система левая Б",
        "li9_exhaust_L": "Выхлопная система левая",
        "li9_driveshaft_F": "Передний кардан",
        "li9_driveshaft": "Задний кардан",
        "li9_diff": "Задний дифференциал",
        "li9_diff_F": "Передний дифференциал (группа)",
        "li9_prorabot_2": "Подрамник (элемент)",
        "li9_tubs": "Колёсные арки",
        "li9_dno": "Днище",
        "li9_lettering_854": "Надпись модели",
        "li9_seat_FR": "Сиденье переднее правое",
        "li9_taillightglass_R": "Стекло заднего фонаря правого",
        "li9_headlightglass": "Стекло фары",
        "li9_headlight": "Фара",
        "li9_mirror_R": "Зеркало правое",
        "li9_mirror_L": "Зеркало левое",
        "li9_wheel": "Колесо ПЛ",
        "li9_wheel_FR": "Колесо ПП",
        "li9_wheel_RL": "Колесо ЗЛ",
        "li9_wheel_RR": "Колесо ЗП",
        "chassis.006": "Элемент шасси",
        "bodyshell.005": "Элемент кузова",
        "li9_taillightglass_L": "Стекло заднего фонаря левого",
        "li9_bumper_R_a": "Бампер задний",
        "bodyshell.009": "Элемент кузова (задняя часть)",
        "li9_bumper_F_b": "Бампер передний",
        "li9_fender_R": "Крыло правое",
        "li9_fender_L": "Крыло левое",
        "li9_seat_FL": "Сиденье переднее левое",
        "li9_hood": "Капот",
        "_wheel_lf_.005": "Диск колеса ПЛ",
        "_wheel_lf_.005_FR": "Диск колеса ПП",
        "_wheel_lf_.005_RL": "Диск колеса ЗЛ",
        "_wheel_lf_.005_RR": "Диск колеса ЗП",
        "_wheel_lf_.004": "Элемент колеса ПЛ",
        "_wheel_lf_.004_FR": "Элемент колеса ПП",
        "_wheel_lf_.004_RL": "Элемент колеса ЗЛ",
        "_wheel_lf_.004_RR": "Элемент колеса ЗП",
        "_wheel_lf_.003": "Элемент колеса ПЛ (3)",
        "_wheel_lf_.003_FR": "Элемент колеса ПП (3)",
        "_wheel_lf_.003_RL": "Элемент колеса ЗЛ (3)",
        "_wheel_lf_.003_RR": "Элемент колеса ЗП (3)",
        "hub_lf": "Ступица ПЛ",
        "hub_lf_FR": "Ступица ПП",
        "hub_lf_RL": "Ступица ЗЛ",
        "hub_lf_RR": "Ступица ЗП",
        "ycd1.001": "Задняя панель (элемент)",
        "ycd1": "Задняя панель",
        "li9_tailgateglass": "Стекло крышки багажника",
        "li9_windshield": "Лобовое стекло",
        "li9_doorglass_RR": "Стекло двери ЗП",
        "li9_sideglass_R": "Боковое стекло правое",
        "li9_doorglass_FR": "Стекло двери ПП",
        "li9_doorglass_RL": "Стекло двери ЗЛ",
        "li9_sideglass_L": "Боковое стекло левое",
        "li9_doorglass_FL": "Стекло двери ПЛ",
        "li9_taillight_euro_L": "Задний фонарь левый",
        "li9_taillight_euro_R": "Задний фонарь правый",
        "Surfacefg": "Поверхность кузова",
        "li9_steer": "Рулевое колесо",
        "seat2.005": "Сиденье заднее (элемент)",
        "seat2.003": "Сиденье заднее (элемент 2)",
        "li9_seats_R": "Задние сиденья",
        "seat1": "Сиденье (элемент)",
        "landstalker2_grill_b_ng.012": "Решётка радиатора (часть 1)",
        "landstalker2_grill_b_ng.011": "Решётка радиатора (часть 2)",
        "landstalker2_grill_b_ng.010": "Решётка радиатора (часть 3)",
        "landstalker2_grill_b_ng.009": "Решётка радиатора (часть 4)",
        "landstalker2_grill_b_ng.002": "Решётка радиатора (часть 5)",
        "landstalker2_grill_b_ng.001": "Решётка радиатора (часть 6)",
        "landstalker2_grill_b_ng": "Решётка радиатора",
        "extra_4.004": "Дополнительный элемент",
        "li9_door_RR": "Дверь задняя правая",
        "li9_doorpanel_RR": "Дверная карта ЗП",
        "li9_door_FR": "Дверь передняя правая",
        "door_pside_f.007": "Панель двери ПП (элемент)",
        "door_pside_f.005": "Панель двери ПП (элемент 2)",
        "li9_doorpanel_FR": "Дверная карта ПП",
        "li9_door_RL": "Дверь задняя левая",
        "li9_doorpanel_RL": "Дверная карта ЗЛ",
        "door_dside_r": "Панель двери ЗЛ",
        "li9_doorpanel_FL": "Дверная карта ПЛ",
        "li9_door_FL": "Дверь передняя левая",
        "chassis.017": "Элемент шасси (передний)",
        "li9_dash": "Приборная панель",
        "chassis.013": "Элемент шасси (средний)",
        "chassis.011": "Элемент шасси (задний)",
        "chassis.010": "Элемент шасси (боковой)",
        "chassis.009": "Элемент шасси (нижний)",
        "chassis.008": "Элемент шасси (поперечный)",
        "chassis.005": "Элемент шасси (основной)",
        "li9_salon": "Салон",
        "li9_tailgatelightglass": "Стекло фонаря багажника",
        "li9_tailgatelight": "Фонарь крышки багажника",
        "li9_tailgate": "Крышка багажника",
        "bodyshell.003": "Элемент кузова (боковой)",
        "bodyshell.001": "Элемент кузова (нижний)",
        "li9_body": "Кузов",
        "body4.011": "Элемент кузова (крыша)",
        "body4.010": "Элемент кузова (задний)",
        "body4.009": "Элемент кузова (боковой П)",
        "body4.008": "Элемент кузова (боковой Л)",
        "body4.006": "Элемент кузова (стойки)",
        "body4.005": "Элемент кузова (пороги)",
        "body4.003": "Элемент кузова (передний)",
        "body4": "Элемент кузова (основной)",
        "body3.003": "Элемент кузова (арка)",
        "body3.002": "Элемент кузова (рамка)",
        "body2.003": "Элемент кузова (молдинг)",
        "body2.001": "Элемент кузова (накладка)",
        "nissangtr_chiferki": "Накладки кузова",
        "li9_brake_FL": "Тормоз ПЛ",
        "li9_brake_FR": "Тормоз ПП",
        "li9_brake_RL": "Тормоз ЗЛ",
        "li9_brake_RR": "Тормоз ЗП",
        "li9_battery": "Батарея ВН",
        "li9_emotor_f": "Электромотор передний",
        "li9_emotor_r": "Электромотор задний",
        "li9_wiring_battery": "Проводка батареи",
        "li9_wiring_emotor": "Проводка э/мотора",
        "li9_battery_cooling": "Охлаждение батареи",
        "li9_emotor_mount": "Крепление э/мотора",
        "li9_air_suspension": "Пневмоподвеска",
        "li9_center_screen": "Центральный экран",
        "li9_xcu": "Блок управления XCU",
        "li9_hu": "Головное устройство",
        "li9_Дроссельная_заслонка": "Дроссельная заслонка",
    }
    return EN_TO_RU.get(mesh_name, mesh_name)


# ============================================================
# 8. DTC Index generation
# ============================================================

DTC_INDEX = {
    # Energy
    "P0A80": {
        "code": "P0A80",
        "description_ru": "Замена тяговой батареи",
        "description_en": "Replace Hybrid Battery Pack",
        "severity": "critical",
        "possibleCauses": ["Деградация ячеек батареи", "Внутреннее замыкание", "Перегрев"],
        "procedures": ["Диагностика состояния ячеек", "Проверка системы охлаждения батареи"],
        "manualSections": ["1-35"],
    },
    "P0A7F": {
        "code": "P0A7F",
        "description_ru": "Износ тяговой батареи",
        "description_en": "Hybrid Battery Pack Deterioration",
        "severity": "warning",
        "possibleCauses": ["Естественный износ", "Неправильная зарядка", "Высокие температуры"],
        "procedures": ["Проверка ёмкости батареи", "Контроль температурного режима"],
        "manualSections": ["1-35"],
    },
    "P3000": {
        "code": "P3000",
        "description_ru": "Неисправность системы тяговой батареи",
        "description_en": "Hybrid Battery System",
        "severity": "critical",
        "possibleCauses": ["Ошибка BMS", "Ошибка связи с батареей", "Неисправность ячейки"],
        "procedures": ["Считывание кодов BMS", "Проверка высоковольтных соединений"],
        "manualSections": ["1-35"],
    },
    "P0AA6": {
        "code": "P0AA6",
        "description_ru": "Нарушение изоляции ВВ системы",
        "description_en": "Hybrid Battery Voltage System Isolation Fault",
        "severity": "critical",
        "possibleCauses": ["Повреждение изоляции кабеля", "Попадание влаги", "Механическое повреждение"],
        "procedures": ["Проверка сопротивления изоляции", "Осмотр ВВ проводки"],
        "manualSections": ["1-35"],
    },
    "P0A09": {
        "code": "P0A09",
        "description_ru": "Неисправность DC/DC преобразователя",
        "description_en": "DC/DC Converter Status Circuit",
        "severity": "warning",
        "possibleCauses": ["Перегрузка преобразователя", "Неисправность контура управления"],
        "procedures": ["Проверка напряжения выхода DC/DC", "Проверка цепей управления"],
        "manualSections": ["1-35"],
    },
    # Powertrain
    "P0300": {
        "code": "P0300",
        "description_ru": "Множественные пропуски зажигания",
        "description_en": "Random/Multiple Cylinder Misfire",
        "severity": "warning",
        "possibleCauses": ["Неисправность свечей зажигания", "Проблемы топливной системы", "Утечка вакуума"],
        "procedures": ["Проверка свечей зажигания", "Проверка форсунок", "Проверка компрессии"],
        "manualSections": ["1-13"],
    },
    "P0171": {
        "code": "P0171",
        "description_ru": "Бедная топливная смесь",
        "description_en": "System Too Lean",
        "severity": "warning",
        "possibleCauses": ["Утечка воздуха", "Неисправность MAF-датчика", "Низкое давление топлива"],
        "procedures": ["Проверка герметичности впуска", "Проверка MAF-датчика", "Проверка давления топлива"],
        "manualSections": ["1-13"],
    },
    "P0A0F": {
        "code": "P0A0F",
        "description_ru": "Ошибка запуска двигателя",
        "description_en": "Engine Failed to Start",
        "severity": "critical",
        "possibleCauses": ["Разряд 12В аккумулятора", "Неисправность стартера", "Блокировка иммобилайзера"],
        "procedures": ["Проверка заряда 12В АКБ", "Диагностика стартера", "Проверка иммобилайзера"],
        "manualSections": ["1-13"],
    },
    "P0A1A": {
        "code": "P0A1A",
        "description_ru": "Ошибка датчика скорости э/мотора",
        "description_en": "Motor/Generator Speed Sensor",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика", "Обрыв проводки", "Ошибка контроллера"],
        "procedures": ["Проверка датчика скорости", "Проверка проводки э/мотора"],
        "manualSections": ["1-13"],
    },
    "P0420": {
        "code": "P0420",
        "description_ru": "Низкая эффективность каталитического нейтрализатора",
        "description_en": "Catalyst System Efficiency Below Threshold",
        "severity": "warning",
        "possibleCauses": ["Износ катализатора", "Неисправность лямбда-зонда"],
        "procedures": ["Проверка лямбда-зондов", "Замена катализатора при необходимости"],
        "manualSections": ["1-11"],
    },
    "P0430": {
        "code": "P0430",
        "description_ru": "Низкая эффективность каталитического нейтрализатора (банк 2)",
        "description_en": "Catalyst System Efficiency Below Threshold (Bank 2)",
        "severity": "warning",
        "possibleCauses": ["Износ катализатора", "Неисправность лямбда-зонда"],
        "procedures": ["Проверка лямбда-зондов", "Замена катализатора при необходимости"],
        "manualSections": ["1-11"],
    },
    "P0700": {
        "code": "P0700",
        "description_ru": "Неисправность системы трансмиссии",
        "description_en": "Transmission Control System Malfunction",
        "severity": "warning",
        "possibleCauses": ["Ошибка TCM", "Проблемы проводки"],
        "procedures": ["Считывание кодов TCM", "Проверка проводки трансмиссии"],
        "manualSections": ["1-30"],
    },
    "P0715": {
        "code": "P0715",
        "description_ru": "Ошибка датчика входного вала трансмиссии",
        "description_en": "Input/Turbine Speed Sensor Circuit",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика", "Проблемы проводки"],
        "procedures": ["Проверка датчика", "Проверка разъёмов"],
        "manualSections": ["1-30"],
    },
    "P0500": {
        "code": "P0500",
        "description_ru": "Ошибка датчика скорости автомобиля",
        "description_en": "Vehicle Speed Sensor",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика скорости", "Повреждение проводки"],
        "procedures": ["Проверка датчика VSS", "Проверка проводки"],
        "manualSections": ["1-30"],
    },
    "P0841": {
        "code": "P0841",
        "description_ru": "Ошибка давления в раздаточной коробке",
        "description_en": "Transmission Fluid Pressure Sensor/Switch",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика давления", "Низкий уровень жидкости"],
        "procedures": ["Проверка уровня ATF", "Проверка датчика давления"],
        "manualSections": ["1-30"],
    },
    "P0121": {
        "code": "P0121",
        "description_ru": "Ошибка датчика дроссельной заслонки",
        "description_en": "Throttle Position Sensor Range/Performance",
        "severity": "warning",
        "possibleCauses": ["Неисправность ДПДЗ", "Загрязнение заслонки"],
        "procedures": ["Проверка ДПДЗ", "Чистка дроссельной заслонки"],
        "manualSections": ["1-13"],
    },
    "P0122": {
        "code": "P0122",
        "description_ru": "Низкое напряжение ДПДЗ",
        "description_en": "Throttle Position Sensor Circuit Low",
        "severity": "warning",
        "possibleCauses": ["Обрыв цепи", "Короткое замыкание"],
        "procedures": ["Проверка проводки ДПДЗ", "Замена датчика"],
        "manualSections": ["1-13"],
    },
    # Chassis
    "C0035": {
        "code": "C0035",
        "description_ru": "Ошибка датчика скорости колеса ПЛ",
        "description_en": "Wheel Speed Sensor FL Circuit",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика ABS", "Повреждение задающего кольца", "Обрыв проводки"],
        "procedures": ["Проверка датчика ABS ПЛ", "Осмотр задающего кольца", "Проверка проводки"],
        "manualSections": ["1-34"],
    },
    "C0036": {
        "code": "C0036",
        "description_ru": "Ошибка датчика скорости колеса ПП",
        "description_en": "Wheel Speed Sensor FR Circuit",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика ABS", "Повреждение задающего кольца"],
        "procedures": ["Проверка датчика ABS ПП"],
        "manualSections": ["1-34"],
    },
    "C0037": {
        "code": "C0037",
        "description_ru": "Ошибка датчика скорости колеса ЗЛ",
        "description_en": "Wheel Speed Sensor RL Circuit",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика ABS", "Повреждение задающего кольца"],
        "procedures": ["Проверка датчика ABS ЗЛ"],
        "manualSections": ["1-34"],
    },
    "C0038": {
        "code": "C0038",
        "description_ru": "Ошибка датчика скорости колеса ЗП",
        "description_en": "Wheel Speed Sensor RR Circuit",
        "severity": "warning",
        "possibleCauses": ["Неисправность датчика ABS", "Повреждение задающего кольца"],
        "procedures": ["Проверка датчика ABS ЗП"],
        "manualSections": ["1-34"],
    },
    "C0040": {
        "code": "C0040",
        "description_ru": "Ошибка датчика скорости колеса ПЛ (диапазон)",
        "description_en": "Wheel Speed Sensor FL Range/Performance",
        "severity": "warning",
        "possibleCauses": ["Загрязнение датчика", "Люфт ступичного подшипника"],
        "procedures": ["Очистка датчика", "Проверка ступичного подшипника"],
        "manualSections": ["1-34"],
    },
    "C0041": {
        "code": "C0041",
        "description_ru": "Ошибка датчика скорости колеса ПП (диапазон)",
        "description_en": "Wheel Speed Sensor FR Range/Performance",
        "severity": "warning",
        "possibleCauses": ["Загрязнение датчика"],
        "procedures": ["Очистка датчика"],
        "manualSections": ["1-34"],
    },
    "C0042": {
        "code": "C0042",
        "description_ru": "Ошибка датчика скорости колеса ЗЛ (диапазон)",
        "description_en": "Wheel Speed Sensor RL Range/Performance",
        "severity": "warning",
        "possibleCauses": ["Загрязнение датчика"],
        "procedures": ["Очистка датчика"],
        "manualSections": ["1-34"],
    },
    "C0043": {
        "code": "C0043",
        "description_ru": "Ошибка датчика скорости колеса ЗП (диапазон)",
        "description_en": "Wheel Speed Sensor RR Range/Performance",
        "severity": "warning",
        "possibleCauses": ["Загрязнение датчика"],
        "procedures": ["Очистка датчика"],
        "manualSections": ["1-34"],
    },
    "C0500": {
        "code": "C0500",
        "description_ru": "Неисправность рулевого управления",
        "description_en": "Steering System Malfunction",
        "severity": "critical",
        "possibleCauses": ["Неисправность ЭУР", "Ошибка датчика угла поворота"],
        "procedures": ["Диагностика ЭУР", "Проверка датчика угла поворота руля"],
        "manualSections": ["1-21"],
    },
    "C0550": {
        "code": "C0550",
        "description_ru": "Неисправность блока управления шасси",
        "description_en": "ECU Malfunction (Chassis)",
        "severity": "critical",
        "possibleCauses": ["Ошибка ЭБУ подвески", "Сбой программного обеспечения"],
        "procedures": ["Перезагрузка ЭБУ", "Обновление ПО", "Замена ЭБУ при необходимости"],
        "manualSections": ["1-34"],
    },
    # Lighting
    "B1250": {
        "code": "B1250",
        "description_ru": "Неисправность левой фары",
        "description_en": "Headlight Left Circuit",
        "severity": "warning",
        "possibleCauses": ["Перегорание лампы/LED", "Обрыв цепи", "Неисправность блока управления фарами"],
        "procedures": ["Проверка LED-модуля", "Проверка проводки", "Проверка блока управления"],
        "manualSections": ["1-32"],
    },
    "B1251": {
        "code": "B1251",
        "description_ru": "Неисправность правой фары",
        "description_en": "Headlight Right Circuit",
        "severity": "warning",
        "possibleCauses": ["Перегорание лампы/LED", "Обрыв цепи"],
        "procedures": ["Проверка LED-модуля", "Проверка проводки"],
        "manualSections": ["1-32"],
    },
    "B1260": {
        "code": "B1260",
        "description_ru": "Неисправность заднего фонаря",
        "description_en": "Taillight Circuit",
        "severity": "warning",
        "possibleCauses": ["Перегорание LED", "Обрыв цепи"],
        "procedures": ["Проверка LED-модуля заднего фонаря"],
        "manualSections": ["1-32"],
    },
    "B1261": {
        "code": "B1261",
        "description_ru": "Неисправность правого заднего фонаря",
        "description_en": "Taillight Right Circuit",
        "severity": "warning",
        "possibleCauses": ["Перегорание LED"],
        "procedures": ["Проверка правого заднего фонаря"],
        "manualSections": ["1-32"],
    },
    "B1262": {
        "code": "B1262",
        "description_ru": "Неисправность левого заднего фонаря (внутр.)",
        "description_en": "Taillight Inner Left Circuit",
        "severity": "warning",
        "possibleCauses": ["Перегорание LED"],
        "procedures": ["Проверка внутреннего левого фонаря"],
        "manualSections": ["1-32"],
    },
    "B1263": {
        "code": "B1263",
        "description_ru": "Неисправность правого заднего фонаря (внутр.)",
        "description_en": "Taillight Inner Right Circuit",
        "severity": "warning",
        "possibleCauses": ["Перегорание LED"],
        "procedures": ["Проверка внутреннего правого фонаря"],
        "manualSections": ["1-32"],
    },
    # Body
    "B1011": {
        "code": "B1011",
        "description_ru": "Неисправность системы передней левой двери",
        "description_en": "Door FL System",
        "severity": "info",
        "possibleCauses": ["Неисправность концевика", "Проблема электропривода замка"],
        "procedures": ["Проверка концевика двери", "Проверка электропривода замка"],
        "manualSections": ["1-19"],
    },
    "B1012": {
        "code": "B1012",
        "description_ru": "Неисправность системы передней правой двери",
        "description_en": "Door FR System",
        "severity": "info",
        "possibleCauses": ["Неисправность концевика"],
        "procedures": ["Проверка концевика двери"],
        "manualSections": ["1-19"],
    },
    "B1013": {
        "code": "B1013",
        "description_ru": "Неисправность системы задней левой двери",
        "description_en": "Door RL System",
        "severity": "info",
        "possibleCauses": ["Неисправность концевика"],
        "procedures": ["Проверка концевика двери"],
        "manualSections": ["1-19"],
    },
    "B1014": {
        "code": "B1014",
        "description_ru": "Неисправность системы задней правой двери",
        "description_en": "Door RR System",
        "severity": "info",
        "possibleCauses": ["Неисправность концевика"],
        "procedures": ["Проверка концевика двери"],
        "manualSections": ["1-19"],
    },
    "B1019": {
        "code": "B1019",
        "description_ru": "Неисправность электропривода крышки багажника",
        "description_en": "Tailgate Motor Circuit",
        "severity": "info",
        "possibleCauses": ["Неисправность электропривода", "Заклинивание механизма"],
        "procedures": ["Проверка электропривода", "Смазка механизма"],
        "manualSections": ["1-19"],
    },
    "B1020": {
        "code": "B1020",
        "description_ru": "Неисправность замка крышки багажника",
        "description_en": "Tailgate Lock Circuit",
        "severity": "info",
        "possibleCauses": ["Неисправность замка"],
        "procedures": ["Проверка замка багажника"],
        "manualSections": ["1-19"],
    },
    # Interior
    "B1450": {
        "code": "B1450",
        "description_ru": "Неисправность сиденья водителя",
        "description_en": "Driver Seat System",
        "severity": "info",
        "possibleCauses": ["Неисправность электропривода", "Ошибка датчика положения"],
        "procedures": ["Проверка электроприводов сиденья", "Проверка датчиков"],
        "manualSections": ["1-20"],
    },
    "B1460": {
        "code": "B1460",
        "description_ru": "Неисправность сиденья пассажира",
        "description_en": "Passenger Seat System",
        "severity": "info",
        "possibleCauses": ["Неисправность электропривода"],
        "procedures": ["Проверка электроприводов сиденья"],
        "manualSections": ["1-20"],
    },
    "B1400": {
        "code": "B1400",
        "description_ru": "Неисправность систем интерьера",
        "description_en": "Interior Systems",
        "severity": "info",
        "possibleCauses": ["Общая ошибка систем интерьера"],
        "procedures": ["Расширенная диагностика"],
        "manualSections": ["1-20"],
    },
    # Exterior
    "B1501": {
        "code": "B1501",
        "description_ru": "Неисправность левого зеркала",
        "description_en": "Left Mirror System",
        "severity": "info",
        "possibleCauses": ["Неисправность электропривода складывания", "Ошибка обогрева"],
        "procedures": ["Проверка электропривода", "Проверка обогрева"],
        "manualSections": ["1-21"],
    },
    "B1502": {
        "code": "B1502",
        "description_ru": "Неисправность правого зеркала",
        "description_en": "Right Mirror System",
        "severity": "info",
        "possibleCauses": ["Неисправность электропривода складывания"],
        "procedures": ["Проверка электропривода"],
        "manualSections": ["1-21"],
    },
    # Electronics
    "U0100": {
        "code": "U0100",
        "description_ru": "Потеря связи с ECM/PCM",
        "description_en": "Lost Communication with ECM/PCM",
        "severity": "critical",
        "possibleCauses": ["Обрыв CAN-шины", "Неисправность ECM", "Повреждение проводки"],
        "procedures": ["Проверка CAN-шины", "Проверка разъёмов ECM"],
        "manualSections": ["1-16"],
    },
    "U0155": {
        "code": "U0155",
        "description_ru": "Потеря связи с модулем фар",
        "description_en": "Lost Communication with Headlight Module",
        "severity": "warning",
        "possibleCauses": ["Обрыв CAN-шины к модулю фар"],
        "procedures": ["Проверка проводки к модулю фар"],
        "manualSections": ["1-32"],
    },
}


# ============================================================
# 9. Main generation
# ============================================================

def get_file_size_mb(path):
    """Get file size in MB."""
    return round(os.path.getsize(path) / (1024 * 1024), 1)


def generate_component_map(glb_path, vehicle_name, source_glb):
    """Генерировать component-map для одной модели."""
    glb_data = read_glb_json(glb_path)
    mesh_nodes, group_nodes = extract_nodes(glb_data)

    stats = {
        "total_nodes": len(glb_data.get("nodes", [])),
        "total_meshes": len(glb_data.get("meshes", [])),
        "total_materials": len(glb_data.get("materials", [])),
        "total_textures": len(glb_data.get("textures", [])),
        "file_size_mb": get_file_size_mb(glb_path),
    }

    # Is this Li9 (English names) or Li7 (Russian names)?
    is_li9 = "Li9" in source_glb

    # Build components
    components = {}
    system_component_ids = {s: [] for s in SYSTEMS}

    for node in mesh_nodes:
        mesh_name = node["name"]
        parent = node["parent"]

        # Classify
        system = classify_node(mesh_name)

        # Display name
        if is_li9:
            display_name = make_display_name_en(mesh_name)
        else:
            display_name = make_display_name(mesh_name)

        # DTC codes
        dtc_codes = get_dtc_codes(mesh_name, system)

        # Manual sections
        manual_secs = get_manual_sections(mesh_name, system)

        # Specs
        specs = get_specs(mesh_name)

        # Layer
        layer_num = LAYER_MAP.get(system, 8)

        # X-ray transparent
        xray = system in XRAY_SYSTEMS

        comp = {
            "meshName": mesh_name,
            "system": system,
            "displayName": display_name,
            "dtcCodes": dtc_codes,
            "manualSections": manual_secs,
            "selectable": True,
            "xray_transparent": xray,
            "layer_num": layer_num,
        }

        if parent:
            comp["parentNode"] = parent

        if specs:
            comp["specs"] = specs

        # Child meshes for group nodes
        children = node.get("children", [])
        if children:
            comp["childMeshes"] = children

        components[mesh_name] = comp
        system_component_ids[system].append(mesh_name)

    # Also process group nodes that have children with meshes
    for gnode in group_nodes:
        gname = gnode["name"]
        if gname in components:
            continue
        # Don't add pure groups like "Li9" or "Колесо ПЛ" as selectable components
        # unless they themselves have a mesh
        if not gnode.get("has_mesh", False):
            continue

    # Build systems dict
    systems_dict = {}
    for sys_id, sys_data in SYSTEMS.items():
        sys_entry = dict(sys_data)
        sys_entry["component_ids"] = system_component_ids.get(sys_id, [])
        systems_dict[sys_id] = sys_entry

    # Build DTC index (only codes actually used)
    used_codes = set()
    for comp in components.values():
        used_codes.update(comp.get("dtcCodes", []))

    dtc_index = {}
    for code in sorted(used_codes):
        if code in DTC_INDEX:
            entry = dict(DTC_INDEX[code])
            # Find components using this code
            entry["components"] = [
                name for name, comp in components.items()
                if code in comp.get("dtcCodes", [])
            ]
            dtc_index[code] = entry

    result = {
        "vehicle": vehicle_name,
        "source_glb": source_glb,
        "coordinate_system": "Y-up",
        "statistics": stats,
        "systemColors": SYSTEM_COLORS,
        "systems": systems_dict,
        "components": components,
        "dtcIndex": dtc_index,
    }

    return result


def main():
    models = [
        {
            "glb": os.path.join(BASE_DIR, "Li7_unified.glb"),
            "vehicle": "Li Auto L7 (2024)",
            "source_glb": "Li7_unified.glb",
            "output": os.path.join(KB_DIR, "li7-component-map.json"),
        },
        {
            "glb": os.path.join(BASE_DIR, "Li9_unified.glb"),
            "vehicle": "Li Auto L9 (2024)",
            "source_glb": "Li9_unified.glb",
            "output": os.path.join(KB_DIR, "li9-component-map.json"),
        },
    ]

    for model in models:
        print(f"Processing {model['vehicle']}...")
        if not os.path.exists(model["glb"]):
            print(f"  WARNING: GLB file not found: {model['glb']}")
            continue

        result = generate_component_map(model["glb"], model["vehicle"], model["source_glb"])

        with open(model["output"], "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        n_comp = len(result["components"])
        n_dtc = len(result["dtcIndex"])
        n_sys = len(result["systems"])
        print(f"  -> {n_comp} components, {n_dtc} DTC codes, {n_sys} systems")
        print(f"  -> Written to {model['output']}")

    print("Done!")


if __name__ == "__main__":
    main()
