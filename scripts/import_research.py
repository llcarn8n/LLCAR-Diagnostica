#!/usr/bin/env python3
"""
Import consensus research issues into KB (chunks + chunk_content).

Each issue becomes:
  - 1 row in `chunks` (content_type='owner_review', source_language='ru')
  - 2 rows in `chunk_content` (ru + en translations)

Content body includes: symptoms, root cause, resolution, repair cost,
confidence level, confirming agents count, and FULL source URLs at the end.

Usage:
  python scripts/import_research.py                    # dry-run (default)
  python scripts/import_research.py --commit           # actually insert
  python scripts/import_research.py --commit --force   # overwrite existing
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "knowledge-base" / "kb.db"
JSON_PATH = Path(__file__).parent.parent / "research" / "consensus_issues.json"

# Map layer names to DB layer values (match existing layers in chunks table)
LAYER_MAP = {
    "suspension": "chassis",
    "brakes": "brakes",
    "engine": "engine",
    "battery": "battery",
    "hvac": "hvac",
    "adas": "adas",
    "body": "body",
    "interior": "interior",
    "electronics": "infotainment",
    "drivetrain": "drivetrain",
    "lighting": "lighting",
    "cooling": "engine",
    "legal": "body",
    "infrastructure": "body",
    "wheels": "chassis",
}

CONFIDENCE_RU = {
    "confirmed": "ПОДТВЕРЖДЕНО (6+ агентов)",
    "high": "ВЫСОКАЯ (4-5 агентов)",
    "medium": "СРЕДНЯЯ (2-3 агента)",
    "low": "НИЗКАЯ (1 агент)",
}

CONFIDENCE_EN = {
    "confirmed": "CONFIRMED (6+ agents)",
    "high": "HIGH (4-5 agents)",
    "medium": "MEDIUM (2-3 agents)",
    "low": "LOW (1 agent)",
}

SEASON_RU = {
    "winter": "Зима",
    "summer": "Лето",
    "all": "Все сезоны",
    "spring": "Весна",
    "rainy": "Сезон дождей",
}

SEASON_EN = {
    "winter": "Winter",
    "summer": "Summer",
    "all": "All seasons",
    "spring": "Spring",
    "rainy": "Rainy season",
}


def make_chunk_id(issue: dict) -> str:
    """Generate chunk ID: research_{issue_id}_{hash8}."""
    raw = issue["title_ru"] + issue["title_en"] + str(issue["sources"])
    h = hashlib.sha256(raw.encode()).hexdigest()[:8]
    return f"research_{issue['id']}_{h}"


def make_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build_content_ru(issue: dict) -> str:
    """Build full Russian content with structured sections and source links."""
    parts = []

    # Header badges
    badges = []
    if issue.get("is_safety_critical"):
        badges.append("[БЕЗОПАСНОСТЬ]")
    if issue.get("is_winter_specific"):
        badges.append("[ЗИМА]")
    badges.append(f"[{CONFIDENCE_RU[issue['confidence']]}]")
    parts.append(" ".join(badges))
    parts.append("")

    # Models & mileage
    models = ", ".join(issue["models"])
    primary = issue.get("primary_model", "")
    if primary and primary != "both":
        models += f" (основная: {primary})"
    parts.append(f"Модели: {models}")

    if issue.get("mileage_min") is not None or issue.get("mileage_max") is not None:
        mn = issue.get("mileage_min") or 0
        mx = issue.get("mileage_max") or "?"
        parts.append(f"Пробег: {mn:,}-{mx:,} км" if isinstance(mx, int) else f"Пробег: от {mn:,} км")

    parts.append(f"Сезон: {SEASON_RU.get(issue['season'], issue['season'])}")
    parts.append("")

    # Symptoms
    parts.append("## Симптомы")
    parts.append(issue["symptoms_ru"])
    parts.append("")

    # Root cause
    if issue.get("root_cause_ru"):
        parts.append("## Причина")
        parts.append(issue["root_cause_ru"])
        parts.append("")

    # DTC codes
    if issue.get("dtc_codes"):
        parts.append("## Коды DTC")
        parts.append(", ".join(issue["dtc_codes"]))
        parts.append("")

    # Resolution
    if issue.get("resolution_ru"):
        parts.append("## Решение")
        parts.append(issue["resolution_ru"])
        parts.append("")

    # Repair cost
    if issue.get("repair_cost_rub_min") is not None:
        mn = issue["repair_cost_rub_min"]
        mx = issue.get("repair_cost_rub_max")
        if mx:
            parts.append(f"Стоимость ремонта: {mn:,} - {mx:,} руб.")
        else:
            parts.append(f"Стоимость ремонта: от {mn:,} руб.")
        parts.append("")

    # Warranty
    if issue.get("warranty_extension"):
        parts.append(f"Гарантия расширена: {issue['warranty_extension']}")
        parts.append("")

    # Confidence & methodology
    parts.append("## Методология исследования")
    parts.append(f"Уровень уверенности: {CONFIDENCE_RU[issue['confidence']]}")
    parts.append(f"Подтвердили: {issue['confirming_agents']} из 12 независимых агентов-исследователей")
    parts.append("Метод: кросс-валидация 6 агентов по эксклюзивным источникам (Telegram RU, Drom.ru, Drive2.ru, EN media, CN platforms, технические БД)")
    parts.append("")

    # How found — methodology
    hf = issue.get("how_found")
    if hf:
        parts.append("## Как найдено (методология)")
        if hf.get("method"):
            parts.append(hf["method"])
        if hf.get("search_queries"):
            parts.append(f"Поисковые запросы: {'; '.join(hf['search_queries'][:5])}")
        if hf.get("platforms"):
            parts.append(f"Платформы: {', '.join(hf['platforms'])}")
        if hf.get("selectors_or_api"):
            parts.append(f"Навигация/API: {hf['selectors_or_api']}")
        parts.append("")

    # Sources — FULL URLs at the end
    parts.append("## Источники")
    for i, url in enumerate(issue.get("sources", []), 1):
        parts.append(f"{i}. {url}")

    return "\n".join(parts)


def build_content_en(issue: dict) -> str:
    """Build full English content with structured sections and source links."""
    parts = []

    # Header badges
    badges = []
    if issue.get("is_safety_critical"):
        badges.append("[SAFETY]")
    if issue.get("is_winter_specific"):
        badges.append("[WINTER]")
    badges.append(f"[{CONFIDENCE_EN[issue['confidence']]}]")
    parts.append(" ".join(badges))
    parts.append("")

    # Models & mileage
    models = ", ".join(issue["models"])
    primary = issue.get("primary_model", "")
    if primary and primary != "both":
        models += f" (primary: {primary})"
    parts.append(f"Models: {models}")

    if issue.get("mileage_min") is not None or issue.get("mileage_max") is not None:
        mn = issue.get("mileage_min") or 0
        mx = issue.get("mileage_max") or "?"
        parts.append(f"Mileage: {mn:,}-{mx:,} km" if isinstance(mx, int) else f"Mileage: from {mn:,} km")

    parts.append(f"Season: {SEASON_EN.get(issue['season'], issue['season'])}")
    parts.append("")

    # Symptoms
    parts.append("## Symptoms")
    parts.append(issue["symptoms_en"])
    parts.append("")

    # Root cause
    if issue.get("root_cause_en"):
        parts.append("## Root Cause")
        parts.append(issue["root_cause_en"])
        parts.append("")

    # DTC codes
    if issue.get("dtc_codes"):
        parts.append("## DTC Codes")
        parts.append(", ".join(issue["dtc_codes"]))
        parts.append("")

    # Resolution
    if issue.get("resolution_en"):
        parts.append("## Resolution")
        parts.append(issue["resolution_en"])
        parts.append("")

    # Repair cost
    if issue.get("repair_cost_rub_min") is not None:
        mn = issue["repair_cost_rub_min"]
        mx = issue.get("repair_cost_rub_max")
        if mx:
            parts.append(f"Repair cost: {mn:,} - {mx:,} RUB")
        else:
            parts.append(f"Repair cost: from {mn:,} RUB")
        parts.append("")

    # Warranty
    if issue.get("warranty_extension"):
        parts.append(f"Warranty extended: {issue['warranty_extension']}")
        parts.append("")

    # Confidence & methodology
    parts.append("## Research Methodology")
    parts.append(f"Confidence: {CONFIDENCE_EN[issue['confidence']]}")
    parts.append(f"Confirmed by: {issue['confirming_agents']} of 12 independent research agents")
    parts.append("Method: cross-validation of 6 agents with exclusive source pools (Telegram RU, Drom.ru, Drive2.ru, EN media, CN platforms, technical DBs)")
    parts.append("")

    # How found — methodology
    hf = issue.get("how_found")
    if hf:
        parts.append("## How Found (Methodology)")
        if hf.get("method"):
            parts.append(hf["method"])
        if hf.get("search_queries"):
            parts.append(f"Search queries: {'; '.join(hf['search_queries'][:5])}")
        if hf.get("platforms"):
            parts.append(f"Platforms: {', '.join(hf['platforms'])}")
        if hf.get("selectors_or_api"):
            parts.append(f"Navigation/API: {hf['selectors_or_api']}")
        parts.append("")

    # Sources — FULL URLs at the end
    parts.append("## Sources")
    for i, url in enumerate(issue.get("sources", []), 1):
        parts.append(f"{i}. {url}")

    return "\n".join(parts)


def determine_content_type(issue: dict) -> str:
    """Classify as owner_review or troubleshooting based on issue nature."""
    # Technical/diagnostic issues
    tech_layers = {"adas", "electronics"}
    tech_tags = {"dtc", "diagnostic", "ecu", "obd", "firmware"}
    if issue["layer"] in tech_layers:
        return "troubleshooting"
    if issue.get("dtc_codes"):
        return "troubleshooting"
    if any(t in tech_tags for t in issue.get("tags", [])):
        return "troubleshooting"
    return "owner_review"


def determine_model(issue: dict) -> str:
    """Return model string for chunks.model field."""
    models = [m.lower() for m in issue["models"]]
    if len(models) >= 3:
        return "l7+l9"  # multi-model
    if "l7" in models and "l9" in models:
        return "l7+l9"
    if "l7" in models:
        return "l7"
    if "l9" in models:
        return "l9"
    return "l7+l9"


def run(commit: bool = False, force: bool = False):
    if not JSON_PATH.exists():
        print(f"ERROR: {JSON_PATH} not found")
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found")
        sys.exit(1)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        issues = json.load(f)

    print(f"Loaded {len(issues)} issues from {JSON_PATH.name}")

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Check existing research chunks
    cur.execute("SELECT id FROM chunks WHERE id LIKE 'research_%'")
    existing = {r[0] for r in cur.fetchall()}
    print(f"Existing research chunks in DB: {len(existing)}")

    inserted = 0
    skipped = 0
    updated = 0

    for issue in issues:
        chunk_id = make_chunk_id(issue)
        title_ru = issue["title_ru"]
        title_en = issue["title_en"]
        content_ru = build_content_ru(issue)
        content_en = build_content_en(issue)
        content_hash = make_content_hash(content_ru)
        content_type = determine_content_type(issue)
        model = determine_model(issue)
        layer = LAYER_MAP.get(issue["layer"], issue["layer"])
        # Primary source URL (first in list)
        source_url = issue["sources"][0] if issue.get("sources") else ""
        # Source name from research
        source = "research_consensus"

        has_procedures = bool(issue.get("resolution_ru"))
        has_warnings = issue.get("is_safety_critical", False)

        if chunk_id in existing and not force:
            skipped += 1
            continue

        if chunk_id in existing and force:
            # Update existing
            if commit:
                cur.execute(
                    """UPDATE chunks SET title=?, content=?, content_hash=?,
                       layer=?, content_type=?, source_url=?, has_procedures=?,
                       has_warnings=?, updated_at=datetime('now')
                       WHERE id=?""",
                    (title_ru, content_ru, content_hash, layer, content_type,
                     source_url, has_procedures, has_warnings, chunk_id),
                )
                cur.execute("DELETE FROM chunk_content WHERE chunk_id=?", (chunk_id,))
            updated += 1
        else:
            # Insert new chunk
            if commit:
                cur.execute(
                    """INSERT INTO chunks
                       (id, brand, model, source_language, layer, content_type,
                        title, content, source, source_url, page_start, page_end,
                        has_procedures, has_warnings, content_hash, is_current)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (chunk_id, "li_auto", model, "ru", layer, content_type,
                     title_ru, content_ru, source, source_url, 0, 0,
                     has_procedures, has_warnings, content_hash, 1),
                )
            inserted += 1

        # Insert chunk_content for RU and EN
        if commit:
            cur.execute(
                """INSERT OR REPLACE INTO chunk_content
                   (chunk_id, lang, title, content, translated_by)
                   VALUES (?,?,?,?,?)""",
                (chunk_id, "ru", title_ru, content_ru, "research_agents"),
            )
            cur.execute(
                """INSERT OR REPLACE INTO chunk_content
                   (chunk_id, lang, title, content, translated_by)
                   VALUES (?,?,?,?,?)""",
                (chunk_id, "en", title_en, content_en, "research_agents"),
            )

    if commit:
        conn.commit()
        # Update FTS5 index
        try:
            cur.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
            conn.commit()
            print("FTS5 index rebuilt")
        except Exception as e:
            print(f"FTS5 rebuild skipped: {e}")

    conn.close()

    mode = "COMMITTED" if commit else "DRY-RUN"
    print(f"\n=== {mode} ===")
    print(f"Inserted: {inserted}")
    print(f"Updated:  {updated}")
    print(f"Skipped:  {skipped} (already exist)")
    print(f"Total:    {inserted + updated + skipped}")

    if not commit:
        print("\nRun with --commit to actually insert into DB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import research issues into KB")
    parser.add_argument("--commit", action="store_true", help="Actually write to DB")
    parser.add_argument("--force", action="store_true", help="Overwrite existing entries")
    args = parser.parse_args()
    run(commit=args.commit, force=args.force)
