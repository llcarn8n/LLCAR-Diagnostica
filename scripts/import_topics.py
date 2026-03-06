#!/usr/bin/env python3
"""
Import unified topics (from article analysis) into KB (chunks + chunk_content).

Each topic becomes:
  - 1 row in `chunks` (source='article_analysis', layer from topic)
  - 2 rows in `chunk_content` (ru + en translations)

Usage:
  python scripts/import_topics.py                    # dry-run
  python scripts/import_topics.py --commit           # insert
  python scripts/import_topics.py --commit --force   # overwrite existing
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "knowledge-base" / "kb.db"
JSON_PATH = Path(__file__).parent.parent / "research" / "unified_topics.json"

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
    "infotainment": "infotainment",
    "drivetrain": "drivetrain",
    "lighting": "lighting",
    "cooling": "engine",
    "legal": "body",
    "infrastructure": "body",
    "wheels": "chassis",
    "chassis": "chassis",
    "ev": "ev",
    "sensors": "sensors",
    "market": "body",
    "safety": "body",
}

CONFIDENCE_RU = {
    "CONFIRMED": "ПОДТВЕРЖДЕНО (3+ источника)",
    "HIGH": "ВЫСОКАЯ (2+ источника)",
    "MEDIUM": "СРЕДНЯЯ",
    "LOW": "НИЗКАЯ",
}
CONFIDENCE_EN = {
    "CONFIRMED": "CONFIRMED (3+ sources)",
    "HIGH": "HIGH (2+ sources)",
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
}

CATEGORY_RU = {
    "troubleshooting": "Диагностика",
    "owner_experience": "Опыт владельцев",
    "maintenance": "Обслуживание",
    "safety": "Безопасность",
    "technology": "Технологии",
    "market": "Рынок",
    "specs": "Характеристики",
    "comparison": "Сравнение",
    "news": "Новости",
    "legal": "Юридические",
}
CATEGORY_EN = {
    "troubleshooting": "Troubleshooting",
    "owner_experience": "Owner Experience",
    "maintenance": "Maintenance",
    "safety": "Safety",
    "technology": "Technology",
    "market": "Market",
    "specs": "Specifications",
    "comparison": "Comparison",
    "news": "News",
    "legal": "Legal",
}


def make_chunk_id(topic: dict) -> str:
    raw = topic["topic_id"] + topic.get("title_ru", "") + topic.get("title_en", "")
    h = hashlib.sha256(raw.encode()).hexdigest()[:8]
    return f"topic_{topic['topic_id']}_{h}"


def make_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build_content_ru(topic: dict) -> str:
    parts = []

    # Category + confidence badges
    cat = CATEGORY_RU.get(topic["category"], topic["category"])
    conf = CONFIDENCE_RU.get(topic["confidence"], topic["confidence"])
    parts.append(f"[{cat}] [{conf}]")
    parts.append("")

    # Models
    models = ", ".join(topic.get("models", []))
    if models:
        parts.append(f"Модели: Li {models}")

    # Systems
    systems = ", ".join(topic.get("systems", []))
    if systems:
        parts.append(f"Системы: {systems}")

    season = topic.get("season", "all")
    if season and season != "all":
        season_map = {"winter": "Зима", "summer": "Лето", "spring": "Весна"}
        parts.append(f"Сезон: {season_map.get(season, season)}")

    parts.append("")

    # Summary
    parts.append("## Описание")
    parts.append(topic.get("summary_ru", ""))
    parts.append("")

    # Key facts
    facts = topic.get("key_facts", [])
    if facts:
        parts.append("## Ключевые факты")
        for fact in facts:
            parts.append(f"- {fact}")
        parts.append("")

    # Repair cost
    if topic.get("repair_cost_range"):
        parts.append(f"Стоимость: {topic['repair_cost_range']}")
        parts.append("")

    # Methodology
    contrib = ", ".join(topic.get("contributing_sources", []))
    merged = len(topic.get("merged_from", []))
    parts.append("## Методология")
    parts.append(f"Объединено из {merged} топиков ({contrib})")
    parts.append("Метод: анализ 394+ статей из 18 источников (drom.ru, autonews, cnevpost, kursiv, telegram и др.)")
    parts.append("")

    # Sources
    urls = topic.get("source_urls", [])
    if urls:
        parts.append("## Источники")
        for i, url in enumerate(urls[:15], 1):
            parts.append(f"{i}. {url}")

    return "\n".join(parts)


def build_content_en(topic: dict) -> str:
    parts = []

    cat = CATEGORY_EN.get(topic["category"], topic["category"])
    conf = CONFIDENCE_EN.get(topic["confidence"], topic["confidence"])
    parts.append(f"[{cat}] [{conf}]")
    parts.append("")

    models = ", ".join(topic.get("models", []))
    if models:
        parts.append(f"Models: Li {models}")

    systems = ", ".join(topic.get("systems", []))
    if systems:
        parts.append(f"Systems: {systems}")

    season = topic.get("season", "all")
    if season and season != "all":
        parts.append(f"Season: {season.capitalize()}")

    parts.append("")

    parts.append("## Description")
    parts.append(topic.get("summary_en", ""))
    parts.append("")

    facts = topic.get("key_facts", [])
    if facts:
        parts.append("## Key Facts")
        for fact in facts:
            parts.append(f"- {fact}")
        parts.append("")

    if topic.get("repair_cost_range"):
        parts.append(f"Cost: {topic['repair_cost_range']}")
        parts.append("")

    contrib = ", ".join(topic.get("contributing_sources", []))
    merged = len(topic.get("merged_from", []))
    parts.append("## Methodology")
    parts.append(f"Merged from {merged} topics ({contrib})")
    parts.append("Method: analysis of 394+ articles from 18 sources (drom.ru, autonews, cnevpost, kursiv, telegram, etc.)")
    parts.append("")

    urls = topic.get("source_urls", [])
    if urls:
        parts.append("## Sources")
        for i, url in enumerate(urls[:15], 1):
            parts.append(f"{i}. {url}")

    return "\n".join(parts)


def determine_content_type(topic: dict) -> str:
    cat = topic.get("category", "")
    if cat in ("troubleshooting", "maintenance"):
        return "troubleshooting"
    if cat in ("safety",):
        return "troubleshooting"
    return "owner_review"


def determine_model(topic: dict) -> str:
    models = [m.lower() for m in topic.get("models", [])]
    if not models or len(models) >= 3:
        return "l7_l9"
    if "l7" in models and "l9" in models:
        return "l7_l9"
    if "l7" in models:
        return "l7"
    if "l9" in models:
        return "l9"
    if "mega" in models:
        return "l7_l9"  # store under general
    return "l7_l9"


def run(commit: bool = False, force: bool = False):
    if not JSON_PATH.exists():
        print(f"ERROR: {JSON_PATH} not found")
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found")
        sys.exit(1)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        topics = json.load(f)

    print(f"Loaded {len(topics)} topics from {JSON_PATH.name}")

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("SELECT id FROM chunks WHERE id LIKE 'topic_%'")
    existing = {r[0] for r in cur.fetchall()}
    print(f"Existing topic chunks in DB: {len(existing)}")

    inserted = 0
    skipped = 0
    updated = 0

    for topic in topics:
        chunk_id = make_chunk_id(topic)
        title_ru = topic.get("title_ru", "")[:200]
        title_en = topic.get("title_en", "")[:200]
        content_ru = build_content_ru(topic)
        content_en = build_content_en(topic)
        content_hash = make_content_hash(content_ru)
        content_type = determine_content_type(topic)
        model = determine_model(topic)
        raw_layer = topic.get("layer") or "body"
        layer = LAYER_MAP.get(raw_layer, raw_layer) or "body"
        source_url = topic["source_urls"][0] if topic.get("source_urls") else ""
        source = "article_analysis"

        has_procedures = bool(topic.get("repair_cost_range"))
        has_warnings = topic.get("category") == "safety"

        if chunk_id in existing and not force:
            skipped += 1
            continue

        if chunk_id in existing and force:
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

        if commit:
            cur.execute(
                """INSERT OR REPLACE INTO chunk_content
                   (chunk_id, lang, title, content, translated_by)
                   VALUES (?,?,?,?,?)""",
                (chunk_id, "ru", title_ru, content_ru, "article_analysis"),
            )
            cur.execute(
                """INSERT OR REPLACE INTO chunk_content
                   (chunk_id, lang, title, content, translated_by)
                   VALUES (?,?,?,?,?)""",
                (chunk_id, "en", title_en, content_en, "article_analysis"),
            )

    if commit:
        conn.commit()
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
    parser = argparse.ArgumentParser(description="Import unified topics into KB")
    parser.add_argument("--commit", action="store_true", help="Actually write to DB")
    parser.add_argument("--force", action="store_true", help="Overwrite existing entries")
    args = parser.parse_args()
    run(commit=args.commit, force=args.force)
