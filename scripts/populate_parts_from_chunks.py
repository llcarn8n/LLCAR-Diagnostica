#!/usr/bin/env python3
"""
LLCAR Diagnostica — Populate `parts` table from existing chunks.

Instead of running Qwen2.5-VL OCR (requires >8GB VRAM), this script
extracts structured part data from the 253 existing parts chunks in kb.db
(created by extract_parts_catalog.py via PyMuPDF text extraction).

Each chunk contains lines like:
    X01-21010001 — 动力电池包总成

The script:
1. Reads all parts chunks from kb.db
2. Parses part_number — part_name_zh pairs via regex
3. Maps each chunk's page_start to a system (via content_list.json)
4. Looks up EN translations from SUBS dict
5. Inserts into the `parts` table

Usage:
    python scripts/populate_parts_from_chunks.py
    python scripts/populate_parts_from_chunks.py --verbose
    python scripts/populate_parts_from_chunks.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("populate_parts")

_BASE_DIR = Path(__file__).resolve().parent.parent
_KB_DB = _BASE_DIR / "knowledge-base" / "kb.db"
_CONTENT_LIST = (
    _BASE_DIR
    / "mineru-output"
    / "941362155-2022-2023款理想L9零件手册"
    / "ocr"
    / "941362155-2022-2023款理想L9零件手册_content_list.json"
)

# ---------------------------------------------------------------------------
# System / subsystem mappings (from gen_l9_catalog.py / ocr_parts_tables.py)
# ---------------------------------------------------------------------------
SYSTEMS = {
    '动力电池系统': 'Power Battery System',
    '动力驱动系统': 'Power Drive System',
    '进气装置': 'Intake System',
    '排气装置': 'Exhaust System',
    '燃油供给装置': 'Fuel Supply System',
    '发动机装置': 'Engine Assembly',
    '悬置装置': 'Engine/Drivetrain Mounts',
    '前悬架装置': 'Front Suspension',
    '后悬架装置': 'Rear Suspension',
    '转向装置': 'Steering System',
    '行车制动装置': 'Service Brake System',
    '空调热管理系统': 'HVAC & Thermal Management',
    '电器附件系统': 'Electrical Accessories',
    '内饰系统': 'Interior Trim System',
    '电源和信号分配系统': 'Power & Signal Distribution',
    '灯具系统': 'Lighting System',
    '座椅系统': 'Seat System',
    '被动安全系统': 'Passive Safety System',
    '外饰系统': 'Exterior Trim System',
    '自动驾驶系统': 'Autonomous Driving System',
    '智能空间系统': 'Smart Cabin / Infotainment',
    '开闭件系统': 'Closures (Doors, Hood, Tailgate)',
    '车身装置': 'Body Structure',
    '整车附件装置': 'Vehicle Accessories & Consumables',
}

SUBS = {
    '动力电池装置': 'Power Battery Assembly',
    '驱动轴装置': 'Drive Shaft Assembly',
    '前电驱动装置': 'Front Electric Drive Assembly',
    '后电驱动装置': 'Rear Electric Drive Assembly',
    '电源装置': 'Power Supply Unit',
    '增程器': 'Range Extender',
    '空气滤清器部件': 'Air Filter Assembly',
    '进气管路部件': 'Intake Duct Assembly',
    '燃油箱及管路部件': 'Fuel Tank & Lines',
    '燃油箱总成': 'Fuel Tank Assembly',
    '发动机总成部件': 'Engine Assembly Parts',
    '发动机总成附件部件': 'Engine Assembly Accessories',
    '扭矩限制器部件': 'Torque Limiter Assembly',
    '气缸盖部件': 'Cylinder Head Assembly',
    '气缸体部件': 'Cylinder Block Assembly',
    '凸轮轴部件': 'Camshaft Assembly',
    '机油泵部件': 'Oil Pump Assembly',
    '配气机构部件': 'Valve Train Assembly',
    '进排歧管部件': 'Intake/Exhaust Manifold',
    '油底壳及润滑部件': 'Oil Pan & Lubrication',
    '机油滤清器部件': 'Oil Filter Assembly',
    '曲轴通风系统部件': 'Crankcase Ventilation',
    '正时齿轮机构部件': 'Timing Gear Mechanism',
    '皮带轮及张紧轮部件': 'Pulley & Tensioner',
    '燃油管路及连接部件': 'Fuel Lines & Connectors',
    '电子节气门体部件': 'Electronic Throttle Body',
    '增压部件': 'Turbocharger Assembly',
    '蒸发器部件': 'Evaporator Assembly',
    '隔热罩部件': 'Heat Shield Assembly',
    '冷却系统装置部件': 'Cooling System Assembly',
    '水泵部件': 'Water Pump Assembly',
    '发动机系统传感器部件': 'Engine Sensors',
    '火花塞及点火线圈部件': 'Spark Plugs & Ignition Coils',
    '排气歧管部件': 'Exhaust Manifold Assembly',
    '排气管部件': 'Exhaust Pipe Assembly',
    '消声器部件': 'Muffler Assembly',
    '三元催化器部件': 'Three-way Catalytic Converter',
    '悬置部件': 'Engine/Drivetrain Mount Parts',
    '前悬架减震器部件': 'Front Suspension Shock Absorber',
    '前悬架弹簧部件': 'Front Suspension Spring',
    '前稳定杆装置': 'Front Stabilizer Bar',
    '前悬架控制臂部件': 'Front Suspension Control Arm',
    '前轮毂及轴承部件': 'Front Hub & Bearing',
    '后悬架减震器部件': 'Rear Suspension Shock Absorber',
    '后悬架弹簧部件': 'Rear Suspension Spring',
    '后稳定杆装置': 'Rear Stabilizer Bar',
    '后悬架控制臂部件': 'Rear Suspension Control Arm',
    '后轮毂及轴承部件': 'Rear Hub & Bearing',
    '空气悬架供给部件': 'Air Suspension Supply',
    '转向柱部件': 'Steering Column Assembly',
    '电动助力转向部件': 'Electric Power Steering',
    '转向拉杆部件': 'Steering Tie Rod',
    '转向机装置': 'Steering Gear Assembly',
    '制动管路部件': 'Brake Lines Assembly',
    '前制动器部件': 'Front Brake Assembly',
    '后制动器部件': 'Rear Brake Assembly',
    '驻车制动部件': 'Parking Brake Assembly',
    '制动踏板部件': 'Brake Pedal Assembly',
    '前端冷却部件装置': 'Front-end Cooling Assembly',
    '前HVAC本体部件': 'Front HVAC Core Assembly',
    '后HVAC本体部件': 'Rear HVAC Core Assembly',
    '空调管路装置': 'HVAC Lines Assembly',
    '空调压缩机装置': 'AC Compressor Assembly',
    '电池热管理装置': 'Battery Thermal Management',
    '副仪表板总成部件': 'Sub-instrument Panel Assembly',
    '地毯装置': 'Carpet Assembly',
    '隔热垫装置': 'Insulation Pad Assembly',
    '行李箱装置': 'Trunk Trim Assembly',
    '仪表板本体部件': 'Instrument Panel Assembly',
    '手套箱部件': 'Glove Box Assembly',
    '组合仪表装置': 'Instrument Cluster',
    '副仪表板冰箱本体部件': 'Sub-panel Refrigerator Assembly',
    '左前门装饰板部件': 'Left Front Door Trim Panel',
    '右前门装饰板部件': 'Right Front Door Trim Panel',
    '左后门装饰板部件': 'Left Rear Door Trim Panel',
    '右后门装饰板部件': 'Right Rear Door Trim Panel',
    '顶棚装置': 'Headliner Assembly',
    '后风挡装饰板部件': 'Rear Window Trim Panel',
    '行李箱侧围装饰板': 'Trunk Side Trim Panel',
    '遮阳板装置': 'Sun Visor Assembly',
    '低压蓄电池装置': 'Low-voltage Battery Assembly',
    '高压线束装置': 'High-voltage Wiring Harness',
    '低压控制线束部件': 'Low-voltage Control Wiring',
    '低压线束部件': 'Low-voltage Wiring Harness',
    '车身线束部件': 'Body Wiring Harness',
    '轮速传感器线束部件': 'Wheel Speed Sensor Wiring',
    '保险丝装置': 'Fuse Assembly',
    '前组合灯部件': 'Front Combination Lamp',
    '后组合灯部件': 'Rear Combination Lamp',
    '日间行车灯部件': 'Daytime Running Lamp',
    '雾灯部件': 'Fog Lamp Assembly',
    '室内灯装置': 'Interior Lamp Assembly',
    '牌照灯部件': 'License Plate Lamp',
    '驾驶员座椅分总成': 'Driver Seat Sub-assembly',
    '副驾驶员座椅分总成': 'Passenger Seat Sub-assembly',
    '第二排左侧座椅分总成部件': 'Second Row Left Seat',
    '第二排右侧座椅分总成部件': 'Second Row Right Seat',
    '第三排座椅分总成': 'Third Row Seat Sub-assembly',
    '安全带装置': 'Seatbelt Assembly',
    '安全气囊装置': 'Airbag Assembly',
    '前保险杠装置': 'Front Bumper Assembly',
    '后保险杠装置': 'Rear Bumper Assembly',
    '翼子板装置': 'Fender Assembly',
    '行李架装置': 'Roof Rack Assembly',
    '后视镜装置': 'Rearview Mirror Assembly',
    '侧踏板装置': 'Side Step Assembly',
    '外饰装置': 'Exterior Trim Assembly',
    '摄像头装置': 'Camera Assembly',
    '超声波雷达装置': 'Ultrasonic Radar Assembly',
    '毫米波雷达装置': 'Millimeter Wave Radar Assembly',
    '激光雷达装置': 'LiDAR Assembly',
    '音响装置': 'Audio System Assembly',
    '屏幕装置': 'Display/Screen Assembly',
    '天线装置': 'Antenna Assembly',
    '左前门装置': 'Left Front Door Assembly',
    '右前门装置': 'Right Front Door Assembly',
    '左后门装置': 'Left Rear Door Assembly',
    '右后门装置': 'Right Rear Door Assembly',
    '发动机盖附件装置': 'Hood Accessories Assembly',
    '尾门装置': 'Tailgate Assembly',
    '前舱装置': 'Front Cabin Assembly',
    '尾门附件装置': 'Tailgate Accessories',
    '车身骨架装置': 'Body Frame Assembly',
    '前保险杠骨架装置': 'Front Bumper Frame',
    '后保险杠骨架装置': 'Rear Bumper Frame',
    '前围挡板部件': 'Front Bulkhead Panel',
    '雨刮装置': 'Wiper Assembly',
    '前风挡玻璃装置': 'Front Windshield Assembly',
    '后风挡玻璃装置': 'Rear Windshield Assembly',
    '车窗玻璃装置': 'Window Glass Assembly',
    '天窗装置': 'Sunroof Assembly',
    '轮胎部件': 'Tire Assembly',
    '备胎装置': 'Spare Tire Assembly',
    '电动充电口装置': 'Electric Charging Port',
    '充电装置': 'Charging Assembly',
}


def build_page_system_map() -> dict[int, tuple[str, str]]:
    """
    Build page_idx → (system_zh, system_en) mapping from content_list.json.
    Uses text entries to detect system headers, forward-fills to cover all pages.
    """
    if not _CONTENT_LIST.exists():
        log.warning("content_list.json not found, falling back to chunk layer")
        return {}

    with open(_CONTENT_LIST, "r", encoding="utf-8") as f:
        content_list = json.load(f)

    page_system: dict[int, tuple[str, str]] = {}
    current_system = None

    for item in content_list:
        if item.get("type") == "text":
            text = item.get("text", "").strip()
            page_idx = item.get("page_idx", -1)

            for sys_zh, sys_en in SYSTEMS.items():
                if sys_zh in text:
                    current_system = (sys_zh, sys_en)
                    break

            if current_system and page_idx >= 0:
                if page_idx not in page_system:
                    page_system[page_idx] = current_system

    # Forward-fill
    if not page_system:
        return {}

    max_page = max(page_system.keys())
    filled: dict[int, tuple[str, str]] = {}
    prev = None
    for p in range(max_page + 1):
        if p in page_system:
            prev = page_system[p]
        if prev:
            filled[p] = prev

    return filled


def find_subsystem_en(title_zh: str) -> str | None:
    """Try to find EN translation for a subsystem title."""
    # Exact match
    if title_zh in SUBS:
        return SUBS[title_zh]

    # Strip date suffixes like "(20220804)" or "-2022-11-1" or "-1"
    cleaned = re.sub(r'[（(]\d{6,8}[）)]', '', title_zh).strip()
    cleaned = re.sub(r'-\d{4}-\d{1,2}-\d{1,2}$', '', cleaned).strip()
    cleaned = re.sub(r'-\d+$', '', cleaned).strip()
    # Remove .svg suffixes
    cleaned = re.sub(r'\.svg[\d-]*\.svg', '', cleaned).strip()

    if cleaned in SUBS:
        return SUBS[cleaned]

    # Substring match: find longest matching key
    best = None
    best_len = 0
    for sub_zh, sub_en in SUBS.items():
        if sub_zh in cleaned or cleaned in sub_zh:
            if len(sub_zh) > best_len:
                best = sub_en
                best_len = len(sub_zh)

    return best


def create_parts_table(conn: sqlite3.Connection) -> None:
    """Ensure the parts table exists."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number TEXT NOT NULL,
            part_name_zh TEXT NOT NULL,
            part_name_en TEXT,
            hotspot_id TEXT,
            system_zh TEXT,
            system_en TEXT,
            subsystem_zh TEXT,
            subsystem_en TEXT,
            page_idx INTEGER,
            source_image TEXT,
            confidence REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_number ON parts(part_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_system ON parts(system_zh)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_parts_name ON parts(part_name_zh)")
    conn.commit()


def parse_parts_from_content(content: str) -> list[dict]:
    """
    Parse part entries from chunk content.

    Handles multiple part number formats:
        X01-21010001 — 动力电池包总成       (standard Li Auto)
        1003324 — 缸体前端线束支架           (numeric, engine supplier)
        ST00076 — 六角法兰面螺栓             (ST-prefix, standard parts)
        Q1840616F70 — 六角法兰面螺栓         (Q-prefix, fasteners)
    """
    parts = []
    for match in re.finditer(
        r'^\s*([\dA-Z][\dA-Za-z\-]{4,})\s*[\u2014\u2013\u2015\-]+\s*([\u4e00-\u9fff].+)$',
        content,
        re.MULTILINE,
    ):
        pn = match.group(1).strip()
        name = match.group(2).strip()
        parts.append({"part_number": pn, "part_name_zh": name})
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate parts table from existing chunks in kb.db",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Parse but don't insert")
    parser.add_argument("--db-path", default=str(_KB_DB))
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    db_path = Path(args.db_path)
    if not db_path.exists():
        log.error("kb.db not found at %s", db_path)
        sys.exit(1)

    # Build page→system mapping
    log.info("Building page→system map...")
    page_system_map = build_page_system_map()
    log.info("  Pages mapped: %d, Systems: %d",
             len(page_system_map), len(set(page_system_map.values())))

    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row

    # Create/ensure table
    create_parts_table(conn)

    # Check if table already has data
    existing = conn.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
    if existing > 0:
        log.warning("parts table already has %d rows. Clearing...", existing)
        conn.execute("DELETE FROM parts")
        conn.commit()

    # Load parts chunks
    log.info("Loading parts chunks from kb.db...")
    rows = conn.execute("""
        SELECT id, title, content, layer, page_start, page_end
        FROM chunks WHERE content_type = 'parts'
        ORDER BY page_start
    """).fetchall()
    log.info("  Parts chunks: %d", len(rows))

    # Parse and insert
    all_parts = []
    seen_numbers: set[str] = set()
    skipped_dupes = 0

    for row in rows:
        chunk_id = row["id"]
        title = row["title"] or ""
        content = row["content"] or ""
        layer = row["layer"] or ""
        page_start = row["page_start"]

        # Parse part entries
        parts = parse_parts_from_content(content)
        if not parts:
            log.debug("No parts in chunk %s (page %s)", chunk_id, page_start)
            continue

        # Get system from page mapping
        sys_zh, sys_en = "", ""
        if page_start and page_start in page_system_map:
            sys_zh, sys_en = page_system_map[page_start]
        elif page_start:
            # Try nearby pages
            for offset in range(1, 5):
                for p in [page_start - offset, page_start + offset]:
                    if p in page_system_map:
                        sys_zh, sys_en = page_system_map[p]
                        break
                if sys_zh:
                    break

        # Subsystem from chunk title
        subsystem_zh = title
        subsystem_en = find_subsystem_en(title) or ""

        for part in parts:
            pn = part["part_number"]
            if pn in seen_numbers:
                skipped_dupes += 1
                continue
            seen_numbers.add(pn)

            all_parts.append((
                pn,
                part["part_name_zh"],
                None,           # part_name_en (no translation yet)
                None,           # hotspot_id (not in chunk text format)
                sys_zh,
                sys_en,
                subsystem_zh,
                subsystem_en,
                page_start,
                None,           # source_image
                0.9,            # confidence (text extraction, not VLM OCR)
            ))

    log.info("Parsed %d unique parts (%d duplicates skipped)", len(all_parts), skipped_dupes)

    if args.dry_run:
        log.info("[DRY RUN] Would insert %d parts. Exiting.", len(all_parts))
        # Show stats
        systems = {}
        for p in all_parts:
            s = p[5] or p[4] or "unknown"  # sys_en or sys_zh
            systems[s] = systems.get(s, 0) + 1
        for s, c in sorted(systems.items(), key=lambda x: -x[1]):
            log.info("  %s: %d parts", s, c)
        conn.close()
        return

    # Insert
    log.info("Inserting into parts table...")
    conn.executemany("""
        INSERT INTO parts (part_number, part_name_zh, part_name_en, hotspot_id,
                          system_zh, system_en, subsystem_zh, subsystem_en,
                          page_idx, source_image, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, all_parts)
    conn.commit()

    # Verify
    count = conn.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
    log.info("=" * 60)
    log.info("  Parts inserted: %d", count)

    # Stats by system
    sys_stats = conn.execute("""
        SELECT system_en, COUNT(*) as cnt
        FROM parts WHERE system_en != ''
        GROUP BY system_en ORDER BY cnt DESC
    """).fetchall()
    for row in sys_stats:
        log.info("  %s: %d", row[0], row[1])

    unmapped = conn.execute(
        "SELECT COUNT(*) FROM parts WHERE system_zh = '' OR system_zh IS NULL"
    ).fetchone()[0]
    if unmapped:
        log.warning("  Unmapped (no system): %d", unmapped)

    log.info("=" * 60)
    conn.close()


if __name__ == "__main__":
    main()
