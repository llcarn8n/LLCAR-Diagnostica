"""Phase 1: Parts data cleanup — system assignment, translations, fastener flags."""
import sqlite3
import json
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "knowledge-base" / "kb.db"
GLOSSARY_PATH = BASE / "frontend" / "data" / "architecture" / "i18n-glossary-data.json"

# ===== Step 1.1: Nearest-neighbor system assignment for unmapped parts =====
def fix_unmapped_systems(conn):
    print("=" * 60)
    print("Step 1.1: Fix unmapped systems (nearest-neighbor)")
    print("=" * 60)

    c = conn.cursor()

    # Build page→system map from existing mapped pages
    c.execute("""
        SELECT page_idx, system_zh, system_en
        FROM parts
        WHERE system_en IS NOT NULL AND system_en != ''
        GROUP BY page_idx
        ORDER BY page_idx
    """)
    page_system = {}
    for page, szh, sen in c.fetchall():
        page_system[page] = (szh, sen)

    # Get unmapped pages
    c.execute("""
        SELECT DISTINCT page_idx
        FROM parts
        WHERE system_en IS NULL OR system_en = ''
        ORDER BY page_idx
    """)
    unmapped_pages = [r[0] for r in c.fetchall()]

    if not unmapped_pages:
        print("  No unmapped pages found!")
        return 0

    print(f"  Mapped pages: {len(page_system)}")
    print(f"  Unmapped pages: {len(unmapped_pages)}")

    mapped_page_list = sorted(page_system.keys())

    # For each unmapped page, find nearest mapped page
    fixes = {}
    for page in unmapped_pages:
        best_dist = float('inf')
        best_sys = None
        for mp in mapped_page_list:
            dist = abs(page - mp)
            if dist < best_dist:
                best_dist = dist
                best_sys = page_system[mp]
        if best_sys:
            fixes[page] = best_sys

    # Apply fixes
    total_fixed = 0
    for page, (szh, sen) in sorted(fixes.items()):
        c.execute(
            "UPDATE parts SET system_zh = ?, system_en = ? WHERE page_idx = ? AND (system_en IS NULL OR system_en = '')",
            (szh, sen, page)
        )
        cnt = c.rowcount
        total_fixed += cnt
        print(f"  Page {page:3d} → {sen} ({cnt} parts, dist={min(abs(page - mp) for mp in mapped_page_list)})")

    conn.commit()
    print(f"\n  TOTAL FIXED: {total_fixed} parts across {len(fixes)} pages")
    return total_fixed


# ===== Step 1.2: Fastener pattern translation =====
FASTENER_DICT = {
    # Bolts
    '六角法兰面螺栓': 'Hex Flange Bolt',
    '六角螺栓': 'Hex Bolt',
    '内六角圆柱头螺栓': 'Socket Head Cap Screw',
    '内六角花形盘头法兰面自攻螺钉': 'Torx Pan Head Flange Self-Tapping Screw',
    '内六角花形沉头螺钉': 'Torx Flat Head Screw',
    '内六角花形盘头螺钉': 'Torx Pan Head Screw',
    '十字盘头自攻螺钉': 'Phillips Pan Head Self-Tapping Screw',
    '十字槽盘头自攻螺钉': 'Phillips Pan Head Self-Tapping Screw',
    '十字沉头自攻螺钉': 'Phillips Flat Head Self-Tapping Screw',
    '十字盘头螺钉': 'Phillips Pan Head Screw',
    '焊接螺栓': 'Weld Bolt',
    '焊接螺母': 'Weld Nut',
    '自攻螺钉': 'Self-Tapping Screw',
    '法兰面螺栓': 'Flange Bolt',
    '膨胀螺栓': 'Expansion Bolt',
    '双头螺柱': 'Stud Bolt',

    # Nuts
    '六角法兰面螺母': 'Hex Flange Nut',
    '六角法兰面锁紧螺母': 'Hex Flange Lock Nut',
    '六角螺母': 'Hex Nut',
    '锁紧螺母': 'Lock Nut',
    '盖形螺母': 'Cap Nut',
    '卡式螺母': 'Clip Nut',
    '板簧螺母': 'Spring Nut',

    # Clips & Fasteners
    '子母扣': 'Push-in Rivet',
    '卡扣': 'Clip',
    '塑料卡扣': 'Plastic Clip',
    '金属卡扣': 'Metal Clip',
    '尼龙扎带': 'Nylon Cable Tie',
    '扎带': 'Cable Tie',
    '铆钉': 'Rivet',
    '拉铆螺母': 'Rivet Nut',
    '弹簧卡扣': 'Spring Clip',
    '弹性销': 'Spring Pin',
    '开口销': 'Cotter Pin',
    '圆柱销': 'Dowel Pin',

    # Washers & Gaskets
    '平垫圈': 'Flat Washer',
    '弹簧垫圈': 'Spring Washer',
    '垫圈': 'Washer',
    '密封垫': 'Seal Gasket',
    '密封圈': 'Seal Ring',
    'O型圈': 'O-Ring',
    '油封': 'Oil Seal',
    '密封垫片': 'Seal Gasket',
    '垫片': 'Gasket',

    # Generic parts
    '堵盖': 'Plug Cap',
    '护盖': 'Protective Cover',
    '装饰盖': 'Decorative Cover',
    '防尘罩': 'Dust Cover',
    '防噪毛毡': 'Anti-Noise Felt',
    '隔音棉': 'Sound Insulation',
    '减震垫': 'Vibration Damper Pad',
    '橡胶垫': 'Rubber Pad',
    '缓冲块': 'Bumper Block',
    '贴片': 'Adhesive Patch',
    '保险丝': 'Fuse',
    '继电器': 'Relay',
    '传感器': 'Sensor',
    '线束': 'Wiring Harness',
    '接插件': 'Connector',
    '支架': 'Bracket',
    '安装支架': 'Mounting Bracket',
    '固定支架': 'Fixing Bracket',
    '管夹': 'Pipe Clamp',
    '卡箍': 'Hose Clamp',
    '弹簧': 'Spring',
}

# Patterns for fastener identification
FASTENER_KEYWORDS = [
    '螺栓', '螺母', '螺钉', '螺柱',  # bolts, nuts, screws, studs
    '卡扣', '扣', '扎带',              # clips, ties
    '垫圈', '垫片', '密封垫',          # washers, gaskets
    '铆钉', '销',                      # rivets, pins
]

def translate_fasteners(conn):
    print("\n" + "=" * 60)
    print("Step 1.2: Translate fastener names (pattern-based)")
    print("=" * 60)

    c = conn.cursor()
    total_translated = 0

    # Sort by longest key first for greedy matching
    sorted_dict = sorted(FASTENER_DICT.items(), key=lambda x: len(x[0]), reverse=True)

    # Get all parts without English name
    c.execute("SELECT id, part_name_zh FROM parts WHERE part_name_en IS NULL OR part_name_en = ''")
    parts = c.fetchall()
    print(f"  Parts without EN name: {len(parts)}")

    updates = []
    for pid, name_zh in parts:
        name_en = None

        # Try exact match first
        if name_zh in FASTENER_DICT:
            name_en = FASTENER_DICT[name_zh]
        else:
            # Try prefix/contains match with size suffix handling
            for zh, en in sorted_dict:
                if name_zh.startswith(zh) or zh in name_zh:
                    # Preserve size/spec suffix if present
                    suffix = name_zh.replace(zh, '').strip()
                    if suffix:
                        name_en = f"{en} ({suffix})"
                    else:
                        name_en = en
                    break

        if name_en:
            updates.append((name_en, pid))

    if updates:
        c.executemany("UPDATE parts SET part_name_en = ? WHERE id = ?", updates)
        conn.commit()
        total_translated = len(updates)

    print(f"  Translated: {total_translated} parts")

    # Show samples
    c.execute("SELECT part_name_zh, part_name_en FROM parts WHERE part_name_en IS NOT NULL AND part_name_en != '' LIMIT 15")
    for zh, en in c.fetchall():
        print(f"    {zh} → {en}")

    return total_translated


# ===== Step 1.3: Glossary lookup translation =====
def translate_from_glossary(conn):
    print("\n" + "=" * 60)
    print("Step 1.3: Translate from glossary (direct match)")
    print("=" * 60)

    if not GLOSSARY_PATH.exists():
        print(f"  Glossary not found: {GLOSSARY_PATH}")
        return 0

    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        glossary = json.load(f)

    # Build zh→en mapping from glossary
    zh_to_en = {}
    if isinstance(glossary, dict):
        for gid, entry in glossary.items():
            if isinstance(entry, dict):
                zh = entry.get('zh', '')
                en = entry.get('en', '')
                if zh and en:
                    zh_to_en[zh] = en
    elif isinstance(glossary, list):
        for entry in glossary:
            if isinstance(entry, dict):
                zh = entry.get('zh', '')
                en = entry.get('en', '')
                if zh and en:
                    zh_to_en[zh] = en

    print(f"  Glossary terms loaded: {len(zh_to_en)}")

    c = conn.cursor()
    c.execute("SELECT id, part_name_zh FROM parts WHERE part_name_en IS NULL OR part_name_en = ''")
    parts = c.fetchall()
    print(f"  Parts still without EN name: {len(parts)}")

    updates = []
    for pid, name_zh in parts:
        # Try exact match
        if name_zh in zh_to_en:
            updates.append((zh_to_en[name_zh], pid))
        else:
            # Try substring match (part name contains glossary term)
            for zh, en in zh_to_en.items():
                if len(zh) >= 3 and zh in name_zh:
                    updates.append((en, pid))
                    break

    if updates:
        c.executemany("UPDATE parts SET part_name_en = ? WHERE id = ?", updates)
        conn.commit()

    print(f"  Translated from glossary: {len(updates)} parts")
    for zh, en in [(c.execute("SELECT part_name_zh, part_name_en FROM parts WHERE id = ?", (u[1],)).fetchone()) for u in updates[:10]]:
        print(f"    {zh} → {en}")

    return len(updates)


# ===== Step 1.5: Add is_fastener flag =====
def add_fastener_flag(conn):
    print("\n" + "=" * 60)
    print("Step 1.5: Add is_fastener flag")
    print("=" * 60)

    c = conn.cursor()

    # Check if column exists
    c.execute("PRAGMA table_info(parts)")
    cols = [row[1] for row in c.fetchall()]

    if 'is_fastener' not in cols:
        c.execute("ALTER TABLE parts ADD COLUMN is_fastener INTEGER DEFAULT 0")
        print("  Added column: is_fastener")

    # Build fastener pattern
    patterns = FASTENER_KEYWORDS
    conditions = " OR ".join([f"part_name_zh LIKE '%{kw}%'" for kw in patterns])

    c.execute(f"UPDATE parts SET is_fastener = 1 WHERE {conditions}")
    cnt = c.rowcount
    conn.commit()

    print(f"  Marked {cnt} parts as fasteners")

    # Stats
    c.execute("SELECT is_fastener, COUNT(*) FROM parts GROUP BY is_fastener")
    for flag, count in c.fetchall():
        label = "Fasteners" if flag else "Functional"
        print(f"    {label}: {count}")

    return cnt


# ===== Summary =====
def print_summary(conn):
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM parts")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM parts WHERE system_en IS NOT NULL AND system_en != ''")
    mapped = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM parts WHERE part_name_en IS NOT NULL AND part_name_en != ''")
    has_en = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM parts WHERE part_name_en IS NULL OR part_name_en = ''")
    no_en = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM parts WHERE is_fastener = 1")
    fasteners = c.fetchone()[0]

    print(f"  Total parts:    {total}")
    print(f"  System mapped:  {mapped} ({mapped*100//total}%)")
    print(f"  Has EN name:    {has_en} ({has_en*100//total}%)")
    print(f"  No EN name:     {no_en} ({no_en*100//total}%)")
    print(f"  Fasteners:      {fasteners} ({fasteners*100//total}%)")

    # Remaining untranslated sample
    if no_en > 0:
        print(f"\n  Sample untranslated parts (for M2M on workstation):")
        c.execute("SELECT part_name_zh, system_en FROM parts WHERE (part_name_en IS NULL OR part_name_en = '') AND is_fastener = 0 LIMIT 20")
        for name, sys in c.fetchall():
            print(f"    {name} [{sys}]")


if __name__ == '__main__':
    print(f"Database: {DB_PATH}")
    print(f"Glossary: {GLOSSARY_PATH}")

    conn = sqlite3.connect(str(DB_PATH))

    try:
        fix_unmapped_systems(conn)
        translate_fasteners(conn)
        translate_from_glossary(conn)
        add_fastener_flag(conn)
        print_summary(conn)
    finally:
        conn.close()

    print("\nDone!")
