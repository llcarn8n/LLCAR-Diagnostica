"""
Phase 2.1-2.2: Build articles + article_chunks tables from SITUATION_CLUSTERS.
Converts frontend hardcoded situations into DB-driven articles with auto-assigned chunks.

Usage: python scripts/build_articles.py [--dry-run]
"""

import sqlite3
import json
import sys
import os
import urllib.request
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db")

# Situations from knowledge-v2.js SITUATION_CLUSTERS + DAILY_TIPS
SITUATIONS = [
    {
        "slug": "overheat",
        "icon": "\U0001F321\uFE0F",
        "urgency": 4,
        "category": "emergency",
        "title_ru": "Перегрев двигателя в пробке",
        "title_en": "Engine Overheating in Traffic",
        "desc_ru": "Температура выше нормы, пар из-под капота",
        "desc_en": "Temperature above normal, steam from under hood",
        "quick_answer_ru": "Остановитесь, заглушите мотор, дождитесь остывания. Не открывайте крышку радиатора на горячую.",
        "quick_answer_en": "Stop, turn off engine, wait for cooling. Do not open radiator cap when hot.",
        "search_queries": ["перегрев двигатель температура охлаждение", "engine overheat coolant temperature"],
        "layers": ["engine"],
        "season": "summer",
    },
    {
        "slug": "brake_noise",
        "icon": "\U0001F6DE",
        "urgency": 3,
        "category": "troubleshooting",
        "title_ru": "Скрип или вибрация при торможении",
        "title_en": "Brake Noise or Vibration",
        "desc_ru": "Посторонние звуки при нажатии на педаль тормоза",
        "desc_en": "Strange sounds when pressing brake pedal",
        "quick_answer_ru": "Проверьте толщину колодок и состояние дисков. При сильной вибрации — обратитесь на СТО.",
        "quick_answer_en": "Check pad thickness and disc condition. If vibration is severe, visit service center.",
        "search_queries": ["тормоз скрип вибрация колодки диск", "brake noise squeal vibration pad"],
        "layers": ["brakes"],
    },
    {
        "slug": "battery_drain",
        "icon": "\U0001F50B",
        "urgency": 3,
        "category": "troubleshooting",
        "title_ru": "Разрядка батареи / снижение запаса хода",
        "title_en": "Battery Drain / Range Reduction",
        "desc_ru": "Быстрая потеря заряда, запас хода ниже ожидаемого",
        "desc_en": "Fast charge loss, range below expected",
        "quick_answer_ru": "Проверьте уровень заряда и состояние ВВБ. Избегайте глубокого разряда ниже 20%.",
        "quick_answer_en": "Check charge level and HV battery health. Avoid deep discharge below 20%.",
        "search_queries": ["батарея разряд запас хода зарядка", "battery drain range charging soc"],
        "layers": ["ev", "battery"],
    },
    {
        "slug": "cold_start",
        "icon": "\u2744\uFE0F",
        "urgency": 2,
        "category": "seasonal",
        "title_ru": "Проблемы с запуском зимой",
        "title_en": "Cold Start Problems in Winter",
        "desc_ru": "Долгий запуск, ошибки при низких температурах",
        "desc_en": "Slow start, errors at low temperatures",
        "quick_answer_ru": "Используйте предпусковой подогрев. Проверьте уровень масла и заряд АКБ.",
        "quick_answer_en": "Use pre-heating. Check oil level and battery charge.",
        "search_queries": ["зима мороз запуск холодный старт обогрев", "cold start winter freeze preheat"],
        "layers": ["engine"],
        "season": "winter",
    },
    {
        "slug": "warning_light",
        "icon": "\u26A0\uFE0F",
        "urgency": 4,
        "category": "emergency",
        "title_ru": "Загорелась контрольная лампа",
        "title_en": "Warning Light On Dashboard",
        "desc_ru": "Индикатор неисправности на приборной панели",
        "desc_en": "Malfunction indicator on dashboard",
        "quick_answer_ru": "Запишите код ошибки. Жёлтый индикатор — можно ехать осторожно. Красный — остановитесь.",
        "quick_answer_en": "Record error code. Yellow = drive carefully. Red = stop immediately.",
        "search_queries": ["индикатор лампа ошибка панель приборов", "warning light indicator malfunction dashboard"],
        "layers": ["sensors"],
    },
    {
        "slug": "adas_fault",
        "icon": "\U0001F916",
        "urgency": 2,
        "category": "troubleshooting",
        "title_ru": "Сбои системы помощи водителю",
        "title_en": "ADAS System Faults",
        "desc_ru": "Не работает ACC, LKA, или камеры",
        "desc_en": "ACC, LKA, or cameras not working",
        "quick_answer_ru": "Перезапустите систему. Проверьте чистоту камер и датчиков. При повторении — диагностика.",
        "quick_answer_en": "Restart system. Check camera/sensor cleanliness. If recurring, run diagnostics.",
        "search_queries": ["adas acc lka камера датчик калибровка", "adas acc lka camera sensor calibration"],
        "layers": ["adas", "sensors"],
    },
    {
        "slug": "tire_pressure",
        "icon": "\U0001F6DE",
        "urgency": 3,
        "category": "troubleshooting",
        "title_ru": "Потеря давления в шинах",
        "title_en": "Tire Pressure Loss",
        "desc_ru": "Индикатор TPMS, неравномерный износ",
        "desc_en": "TPMS indicator, uneven wear",
        "quick_answer_ru": "Проверьте давление во всех колёсах. Норма: 2.3-2.5 бар. При резкой потере — не двигайтесь.",
        "quick_answer_en": "Check all tire pressures. Normal: 2.3-2.5 bar. If sudden loss, do not drive.",
        "search_queries": ["давление шина tpms прокол", "tire pressure tpms flat"],
        "layers": ["chassis"],
    },
    {
        "slug": "maintenance",
        "icon": "\U0001F527",
        "urgency": 1,
        "category": "maintenance",
        "title_ru": "Плановое ТО и обслуживание",
        "title_en": "Scheduled Maintenance",
        "desc_ru": "Замена масла, фильтров, колодок, жидкостей",
        "desc_en": "Oil, filter, brake pad, fluid replacement",
        "quick_answer_ru": "Следуйте регламенту ТО. Основные интервалы: масло — 10 000 км, тормозная жидкость — 2 года.",
        "quick_answer_en": "Follow maintenance schedule. Key intervals: oil — 10,000 km, brake fluid — 2 years.",
        "search_queries": ["замена масло фильтр обслуживание ТО регламент", "maintenance oil filter service schedule"],
        "layers": ["engine", "brakes"],
    },
    {
        "slug": "charging",
        "icon": "\U0001F50C",
        "urgency": 1,
        "category": "daily",
        "title_ru": "Правильная зарядка",
        "title_en": "Proper Charging",
        "desc_ru": "Как и когда заряжать, оптимальный уровень SOC",
        "desc_en": "How and when to charge, optimal SOC level",
        "quick_answer_ru": "Оптимальный уровень заряда — 20–80%. Заряжайте регулярно, не допускайте глубокого разряда.",
        "quick_answer_en": "Optimal charge level is 20-80%. Charge regularly, avoid deep discharge.",
        "search_queries": ["зарядка батарея soc уровень заряд кабель", "charging battery soc level cable plug"],
        "layers": ["ev", "battery"],
    },
    {
        "slug": "climate_control",
        "icon": "\u2744\uFE0F",
        "urgency": 1,
        "category": "daily",
        "title_ru": "Климат-контроль и экономия",
        "title_en": "Climate Control & Efficiency",
        "desc_ru": "Кондиционер, обогрев, рециркуляция, расход энергии",
        "desc_en": "AC, heating, recirculation, energy consumption",
        "quick_answer_ru": "Рециркуляция экономит энергию. Предварительный обогрев на зарядке — бесплатное тепло.",
        "quick_answer_en": "Recirculation saves energy. Pre-heating while charging = free heat.",
        "search_queries": ["климат контроль кондиционер обогрев рециркуляция", "climate control ac heater recirculation"],
        "layers": ["hvac"],
    },
]


def search_local(conn, query, limit=10):
    """Search chunks via FTS5 locally (no API needed)."""
    cur = conn.cursor()
    results = []

    # FTS5 search
    words = query.strip().split()[:5]
    for word in words:
        try:
            hits = cur.execute("""
                SELECT c.id, c.has_procedures, c.has_warnings, c.content_type, c.layer
                FROM chunks_fts fts
                JOIN chunks c ON c.rowid = fts.rowid
                WHERE chunks_fts MATCH ?
                AND (c.is_current IS NULL OR c.is_current = 1)
                LIMIT ?
            """, (f'"{word}"', limit * 2)).fetchall()
            for h in hits:
                if h[0] not in [r[0] for r in results]:
                    results.append(h)
        except Exception:
            pass

    # Filter by quality
    quality_ids = set()
    if results:
        ids = [r[0] for r in results]
        ph = ",".join("?" * len(ids))
        try:
            q_rows = cur.execute(
                f"SELECT chunk_id FROM chunk_quality WHERE chunk_id IN ({ph}) AND quality_tier >= 3",
                ids,
            ).fetchall()
            quality_ids = {r[0] for r in q_rows}
        except Exception:
            quality_ids = set(ids)

    # Sort: procedures first, then warnings, filter by quality
    good = [r for r in results if r[0] in quality_ids]
    good.sort(key=lambda r: (r[1] or 0) + (r[2] or 0), reverse=True)
    return good[:limit]


def main():
    dry_run = "--dry-run" in sys.argv
    db_path = os.path.abspath(DB_PATH)
    print(f"DB: {db_path}")
    if dry_run:
        print("=== DRY RUN ===\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Create tables
    if not dry_run:
        cur.execute("DROP TABLE IF EXISTS article_chunks")
        cur.execute("DROP TABLE IF EXISTS articles")
        cur.execute("""
            CREATE TABLE articles (
                slug TEXT PRIMARY KEY,
                icon TEXT,
                urgency INTEGER DEFAULT 1,
                category TEXT NOT NULL,
                title_ru TEXT NOT NULL,
                title_en TEXT,
                desc_ru TEXT,
                desc_en TEXT,
                quick_answer_ru TEXT,
                quick_answer_en TEXT,
                search_queries TEXT,
                layers TEXT,
                season TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cur.execute("""
            CREATE TABLE article_chunks (
                article_slug TEXT NOT NULL REFERENCES articles(slug),
                chunk_id TEXT NOT NULL REFERENCES chunks(id),
                section TEXT DEFAULT 'content',
                sort_order INTEGER DEFAULT 0,
                PRIMARY KEY (article_slug, chunk_id)
            )
        """)
        cur.execute("CREATE INDEX idx_ac_slug ON article_chunks(article_slug)")
        cur.execute("CREATE INDEX idx_ac_chunk ON article_chunks(chunk_id)")

    total_chunks_assigned = 0

    for i, sit in enumerate(SITUATIONS):
        # Insert article
        if not dry_run:
            cur.execute("""
                INSERT INTO articles (slug, icon, urgency, category,
                    title_ru, title_en, desc_ru, desc_en,
                    quick_answer_ru, quick_answer_en,
                    search_queries, layers, season, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sit["slug"], sit["icon"], sit["urgency"], sit["category"],
                sit["title_ru"], sit.get("title_en", ""),
                sit.get("desc_ru", ""), sit.get("desc_en", ""),
                sit.get("quick_answer_ru", ""), sit.get("quick_answer_en", ""),
                json.dumps(sit["search_queries"]),
                json.dumps(sit["layers"]),
                sit.get("season"),
                i,
            ))

        # Search for related chunks
        all_chunk_ids = []
        for query in sit["search_queries"]:
            results = search_local(conn, query, limit=10)
            for r in results:
                if r[0] not in all_chunk_ids:
                    all_chunk_ids.append(r[0])

        # Deduplicate and limit to 20
        all_chunk_ids = all_chunk_ids[:20]

        # Determine section by chunk properties
        for j, cid in enumerate(all_chunk_ids):
            chunk = cur.execute(
                "SELECT has_procedures, has_warnings, content_type FROM chunks WHERE id=?",
                (cid,),
            ).fetchone()

            if chunk:
                if chunk["has_procedures"]:
                    section = "steps"
                elif chunk["has_warnings"]:
                    section = "warnings"
                elif chunk["content_type"] == "dtc":
                    section = "diagnostics"
                else:
                    section = "content"
            else:
                section = "content"

            if not dry_run:
                cur.execute(
                    "INSERT OR IGNORE INTO article_chunks VALUES (?, ?, ?, ?)",
                    (sit["slug"], cid, section, j),
                )

        total_chunks_assigned += len(all_chunk_ids)
        print(f"  {sit['slug']}: {len(all_chunk_ids)} chunks assigned")

    if not dry_run:
        conn.commit()

    print(f"\n=== Summary ===")
    print(f"  Articles created: {len(SITUATIONS)}")
    print(f"  Total chunk assignments: {total_chunks_assigned}")

    if not dry_run:
        unique_chunks = cur.execute(
            "SELECT COUNT(DISTINCT chunk_id) FROM article_chunks"
        ).fetchone()[0]
        print(f"  Unique chunks linked: {unique_chunks}")

    if dry_run:
        print("\n(Dry run — no changes made)")

    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
