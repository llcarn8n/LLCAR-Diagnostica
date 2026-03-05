#!/usr/bin/env python3
"""
Build situation tags for all KB articles.

Автоматическая разметка 11 398 статей тегами:
- urgency (1-5)
- situation_type (emergency/maintenance/troubleshooting/learning/specification)
- trust_level (1-5)
- season (winter/summer/all)
- events (warning_light/noise/vibration/etc.)
- mileage_ranges (0-10k/10-30k/30-60k/60k+)

Чистый SQL + regex, без ML. Работает ~30 секунд.

Usage:
    python scripts/build_situation_tags.py
    python scripts/build_situation_tags.py --db knowledge-base/kb.db --output knowledge-base/situation_tags.json
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent
_DB = _BASE / "knowledge-base" / "kb.db"
_OUTPUT = _BASE / "knowledge-base" / "situation_tags.json"

# ═══════════════════════════════════════════════════════════
# Trust level mapping: source → 1-5
# ═══════════════════════════════════════════════════════════

SOURCE_TRUST = {
    # 5 = Official manual, original language
    "pdf_l9_ru": 5,
    "pdf_l7_ru": 5,
    "mineru_l9_ru": 5,
    # 4 = Official manual, translated or English
    "pdf_l9_zh": 4,
    "pdf_l7_zh": 4,
    "pdf_l9_zh_full": 4,
    "pdf_l7_zh_full": 4,
    "mineru_l9_zh_owners": 4,
    "mineru_l7_zh_owners": 4,
    "mineru_l9_en": 4,
    "mineru_l9_en_config": 4,
    "mineru_l7_zh_config": 4,
    "mineru_l9_zh_parts": 4,
    "parts_l9_zh": 4,
    # 4 = DTC database (structured, reliable)
    "dtc_database": 4,
    "dtc_db": 4,
    # 3 = Official Li Auto website / press
    "web_l7_zh": 3,
    "lixiang_com": 3,
    "liautocn_news": 3,
    # 3 = Major automotive media
    "autohome_cn": 3,
    # 2 = User reviews, forums
    "drom_ru": 2,
    "drom.ru": 2,
    # 2 = Other web sources (default)
    "web": 2,
}

# ═══════════════════════════════════════════════════════════
# Keyword patterns (ZH + RU + EN)
# ═══════════════════════════════════════════════════════════

# Emergency / danger keywords
_EMERGENCY_WORDS = re.compile(
    r"danger|fatal|fire|explosion|high.voltage|electric.shock|"
    r"危险|致命|火灾|爆炸|高压|触电|"
    r"опасно|смертельн|пожар|взрыв|высок.напряжени|поражени.током|"
    r"немедленно.остановит|do.not.drive|禁止行驶",
    re.IGNORECASE,
)

# Winter keywords
_WINTER_WORDS = re.compile(
    r"winter|cold.weather|freeze|antifreeze|ice|snow|de-?ic|"
    r"冬季|防冻|冰|雪|除冰|低温|"
    r"зим[а-яё]|мороз|антифриз|обогрев|снег|лёд|замерз",
    re.IGNORECASE,
)

# Summer keywords
_SUMMER_WORDS = re.compile(
    r"summer|hot.weather|overheat|cooling.system|air.condition|refrigerant|"
    r"夏季|过热|冷却|空调|制冷|高温|"
    r"лет[а-яё]{0,3}\b|перегрев|охлажден|кондиционер|хладагент",
    re.IGNORECASE,
)

# Event patterns
_EVENT_PATTERNS = {
    "warning_light": re.compile(
        r"warning.light|indicator|dashboard.light|故障灯|指示灯|警告灯|"
        r"индикатор|сигнал.лампа|загор[а-яё]*\s*лампа|контрольн.лампа",
        re.IGNORECASE,
    ),
    "noise": re.compile(
        r"noise|sound|squeal|grind|rattle|click|knock|"
        r"噪音|声音|异响|咯吱|咔嗒|敲击|"
        r"шум|скрип|скрежет|стук|треск|хруст|щелч|дребезж|гул",
        re.IGNORECASE,
    ),
    "vibration": re.compile(
        r"vibrat|shake|wobble|pulsat|shimmy|"
        r"振动|抖动|晃动|脉动|"
        r"вибрац|биение|дрожан|тряс",
        re.IGNORECASE,
    ),
    "smell": re.compile(
        r"smell|odor|burn|fume|"
        r"气味|烧焦|冒烟|"
        r"запах|горел|дым|вонь|гарь",
        re.IGNORECASE,
    ),
    "leak": re.compile(
        r"leak|drip|seep|puddle|"
        r"泄漏|渗漏|滴漏|"
        r"утечк|подтёк|подтек|течь|капа[еющ]",
        re.IGNORECASE,
    ),
    "no_start": re.compile(
        r"won.t.start|no.start|crank|dead.battery|"
        r"无法启动|打不着|启动困难|"
        r"не заводит|не запуск|стартер.не|аккумулятор.разряж",
        re.IGNORECASE,
    ),
    "performance": re.compile(
        r"reduced|weak|slow|poor|fail|loss.of.power|"
        r"降低|减弱|动力不足|失速|"
        r"снижен|слаб|плох|потер.мощност|не тянет",
        re.IGNORECASE,
    ),
    "maintenance": re.compile(
        r"maintenance|service|inspect|schedule|interval|replace|change|"
        r"保养|维护|检查|定期|更换|"
        r"обслуживан|проверк|осмотр|интервал|замен[аиять]|регламент",
        re.IGNORECASE,
    ),
}

# Mileage keywords
_BREAKIN = re.compile(r"break.in|run.in|磨合|обкатк|новый.автомобил", re.IGNORECASE)
_MAJOR_SERVICE = re.compile(r"overhaul|rebuild|大修|капитальн|timing.chain|цепь.грм", re.IGNORECASE)


# ═══════════════════════════════════════════════════════════
# Tagging functions
# ═══════════════════════════════════════════════════════════


def tag_situation_type(chunk: dict) -> str:
    """Determine situation_type from content."""
    content_lower = (chunk["content"] or "")[:3000].lower()

    # Emergency: has_warnings + danger keywords
    if chunk["has_warnings"] and _EMERGENCY_WORDS.search(content_lower):
        return "emergency"

    # DTC = troubleshooting
    if chunk["content_type"] == "dtc":
        return "troubleshooting"

    # Has procedures = maintenance
    if chunk["has_procedures"]:
        return "maintenance"

    # Specification keywords
    spec_words = ("specification", "规格", "参数", "характеристик", "параметр", "момент затяжки", "torque")
    if any(w in content_lower for w in spec_words):
        return "specification"

    # Has warnings but not emergency = troubleshooting
    if chunk["has_warnings"]:
        return "troubleshooting"

    return "learning"


def tag_urgency(chunk: dict, situation_type: str) -> int:
    """Compute urgency 1-5."""
    content_lower = (chunk["content"] or "")[:3000].lower()

    # 5 = Critical safety (fire, explosion, HV shock)
    if _EMERGENCY_WORDS.search(content_lower):
        return 5

    # 4 = High-risk systems with warnings
    if chunk["layer"] in ("battery", "ev") and chunk["has_warnings"]:
        return 4
    if chunk["layer"] == "brakes" and chunk["has_warnings"]:
        return 4

    # 3 = DTC or troubleshooting
    if situation_type == "troubleshooting" or chunk["content_type"] == "dtc":
        return 3

    # 2 = Maintenance / procedures
    if situation_type == "maintenance":
        return 2

    # 1 = Informational
    return 1


def tag_trust_level(source: str) -> int:
    """Map source to trust level 1-5."""
    return SOURCE_TRUST.get(source, 2)


def tag_season(chunk: dict) -> str:
    """Determine season relevance."""
    content = (chunk["content"] or "")[:3000]
    title = chunk["title"] or ""
    text = f"{title} {content}"

    is_winter = bool(_WINTER_WORDS.search(text))
    is_summer = bool(_SUMMER_WORDS.search(text))

    if is_winter and not is_summer:
        return "winter"
    if is_summer and not is_winter:
        return "summer"
    return "all"


def tag_events(chunk: dict) -> list[str]:
    """Determine relevant event types."""
    content = (chunk["content"] or "")[:3000]
    title = chunk["title"] or ""
    text = f"{title} {content}"

    events = []
    for event_name, pattern in _EVENT_PATTERNS.items():
        if pattern.search(text):
            events.append(event_name)

    # Default: maintenance
    if not events:
        events = ["maintenance"]

    return events


def tag_mileage_ranges(chunk: dict) -> list[str]:
    """Determine relevant mileage ranges."""
    content = (chunk["content"] or "")[:3000]
    title = chunk["title"] or ""
    text = f"{title} {content}"

    ranges = []

    # Break-in / new vehicle
    if _BREAKIN.search(text):
        ranges.append("0-10k")

    # Regular replacement (brakes, oil, filters)
    replace_words = ("replace", "change", "更换", "замен")
    if any(w in text.lower() for w in replace_words):
        if chunk["layer"] in ("brakes", "engine"):
            ranges.extend(["10-30k", "30-60k"])
        else:
            ranges.extend(["30-60k", "60k+"])

    # Major overhaul
    if _MAJOR_SERVICE.search(text):
        ranges.append("60k+")

    # If nothing specific — relevant for all
    if not ranges:
        ranges = ["0-10k", "10-30k", "30-60k", "60k+"]

    return sorted(set(ranges))


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════


def build_tags(db_path: Path) -> list[dict]:
    """Build situation tags for all chunks."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT id, source, layer, content_type, title, content,
               has_procedures, has_warnings, source_language, model
        FROM chunks
        WHERE is_current = 1 OR is_current IS NULL
    """).fetchall()

    # Load DTC links
    dtc_map: dict[str, list[str]] = {}
    for r in conn.execute("SELECT chunk_id, dtc_code FROM chunk_dtc"):
        dtc_map.setdefault(r[0], []).append(r[1])

    conn.close()

    tags_list = []
    for row in rows:
        chunk = dict(row)

        situation_type = tag_situation_type(chunk)
        urgency = tag_urgency(chunk, situation_type)
        trust_level = tag_trust_level(chunk["source"] or "")
        season = tag_season(chunk)
        events = tag_events(chunk)
        mileage_ranges = tag_mileage_ranges(chunk)
        dtc_codes = dtc_map.get(chunk["id"], [])

        tags = {
            "chunk_id": chunk["id"],
            "situation_type": situation_type,
            "urgency": urgency,
            "trust_level": trust_level,
            "season": season,
            "events": events,
            "mileage_ranges": mileage_ranges,
            "dtc_codes": dtc_codes,
            "layer": chunk["layer"],
            "model": chunk["model"],
            "has_procedures": bool(chunk["has_procedures"]),
            "has_warnings": bool(chunk["has_warnings"]),
        }
        tags_list.append(tags)

    return tags_list


def save_to_db(db_path: Path, tags_list: list[dict]):
    """Save tags to situation_tags table in kb.db."""
    conn = sqlite3.connect(str(db_path))

    conn.execute("DROP TABLE IF EXISTS situation_tags")
    conn.execute("""
        CREATE TABLE situation_tags (
            chunk_id TEXT PRIMARY KEY,
            situation_type TEXT NOT NULL,
            urgency INTEGER NOT NULL,
            trust_level INTEGER NOT NULL,
            season TEXT NOT NULL DEFAULT 'all',
            events TEXT NOT NULL DEFAULT '["maintenance"]',
            mileage_ranges TEXT NOT NULL DEFAULT '["0-10k","10-30k","30-60k","60k+"]',
            dtc_codes TEXT NOT NULL DEFAULT '[]'
        )
    """)

    for t in tags_list:
        conn.execute("""
            INSERT INTO situation_tags (chunk_id, situation_type, urgency, trust_level, season, events, mileage_ranges, dtc_codes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["chunk_id"],
            t["situation_type"],
            t["urgency"],
            t["trust_level"],
            t["season"],
            json.dumps(t["events"]),
            json.dumps(t["mileage_ranges"]),
            json.dumps(t["dtc_codes"]),
        ))

    conn.commit()
    conn.close()


def print_stats(tags_list: list[dict]):
    """Print statistics."""
    from collections import Counter

    total = len(tags_list)
    print(f"\n{'='*50}")
    print(f"Total articles tagged: {total}")
    print(f"{'='*50}")

    # Situation types
    st = Counter(t["situation_type"] for t in tags_list)
    print(f"\nSituation types:")
    for k, v in st.most_common():
        print(f"  {k}: {v} ({v*100//total}%)")

    # Urgency
    urg = Counter(t["urgency"] for t in tags_list)
    print(f"\nUrgency levels:")
    for k in sorted(urg.keys(), reverse=True):
        print(f"  {k}: {urg[k]} ({urg[k]*100//total}%)")

    # Trust
    tr = Counter(t["trust_level"] for t in tags_list)
    print(f"\nTrust levels:")
    for k in sorted(tr.keys(), reverse=True):
        print(f"  {k}: {tr[k]} ({tr[k]*100//total}%)")

    # Season
    se = Counter(t["season"] for t in tags_list)
    print(f"\nSeason:")
    for k, v in se.most_common():
        print(f"  {k}: {v} ({v*100//total}%)")

    # Events (multi-valued)
    ev = Counter()
    for t in tags_list:
        for e in t["events"]:
            ev[e] += 1
    print(f"\nEvents (articles with this event):")
    for k, v in ev.most_common():
        print(f"  {k}: {v} ({v*100//total}%)")

    # Emergency stats
    emerg = [t for t in tags_list if t["urgency"] >= 4]
    print(f"\nHigh urgency (4-5): {len(emerg)} articles")
    if emerg:
        layers = Counter(t["layer"] for t in emerg)
        for k, v in layers.most_common(5):
            print(f"  {k}: {v}")


def main():
    parser = argparse.ArgumentParser(description="Build situation tags for KB articles")
    parser.add_argument("--db", default=str(_DB), help="Path to kb.db")
    parser.add_argument("--output", default=str(_OUTPUT), help="Output JSON path")
    args = parser.parse_args()

    db_path = Path(args.db)
    output_path = Path(args.output)

    if not db_path.exists():
        print(f"ERROR: DB not found: {db_path}")
        sys.exit(1)

    print(f"Building situation tags from {db_path}...")
    tags_list = build_tags(db_path)

    # Save JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tags_list, f, ensure_ascii=False, indent=None)
    print(f"Saved {len(tags_list)} tags to {output_path} ({output_path.stat().st_size // 1024} KB)")

    # Save to DB
    save_to_db(db_path, tags_list)
    print(f"Saved situation_tags table to {db_path}")

    print_stats(tags_list)


if __name__ == "__main__":
    main()
