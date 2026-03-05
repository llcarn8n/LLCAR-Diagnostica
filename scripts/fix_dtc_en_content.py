#!/usr/bin/env python3
"""Fix English DTC content: translate labels to Russian."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "knowledge-base" / "kb.db"

SYSTEM_MAP = {
    "engine": "Двигатель",
    "drivetrain": "Трансмиссия",
    "ev": "Электросистема",
    "brakes": "Тормозная система",
    "sensors": "Датчики",
    "hvac": "Климат-контроль",
    "body": "Кузов",
    "interior": "Салон",
    "battery": "Батарея HV",
    "lighting": "Освещение",
    "chassis": "Шасси",
    "infotainment": "Мультимедиа",
    "adas": "ADAS",
}

REPLACEMENTS = [
    # English labels → Russian
    ("Fault Code: ", "Код неисправности: "),
    ("Description: ", "Описание: "),
    ("Can drive: yes_limited", "Можно ли ехать: Да, с ограничениями"),
    ("Can drive: yes", "Можно ли ехать: Да, безопасно"),
    ("Can drive: no", "Можно ли ехать: Нет, опасно!"),
    ("Severity: 1\n", "Серьёзность: 1 — Низкая\n"),
    ("Severity: 2\n", "Серьёзность: 2 — Умеренная\n"),
    ("Severity: 3\n", "Серьёзность: 3 — Средняя\n"),
    ("Severity: 4\n", "Серьёзность: 4 — Высокая\n"),
    ("Severity: 5\n", "Серьёзность: 5 — Критическая\n"),
    ("Probable Causes:", "Возможные причины:"),
]

conn = sqlite3.connect(str(DB))
total = 0

# Fix EN DTC chunks content
for old, new in REPLACEMENTS:
    n = conn.execute(
        "UPDATE chunks SET content = REPLACE(content, ?, ?) "
        "WHERE content_type='dtc' AND source_language='en' AND content LIKE ?",
        (old, new, f"%{old}%")
    ).rowcount
    total += n

# Fix System: in EN DTC
for eng, rus in SYSTEM_MAP.items():
    n = conn.execute(
        "UPDATE chunks SET content = REPLACE(content, 'System: ' || ?, 'Система: ' || ?) "
        "WHERE content_type='dtc' AND source_language='en' AND content LIKE ?",
        (eng, rus, f"%System: {eng}%")
    ).rowcount
    total += n

# Also fix chunk_content for EN DTC
for old, new in REPLACEMENTS:
    n = conn.execute(
        "UPDATE chunk_content SET content = REPLACE(content, ?, ?) "
        "WHERE chunk_id IN (SELECT id FROM chunks WHERE content_type='dtc' AND source_language='en') "
        "AND content LIKE ?",
        (old, new, f"%{old}%")
    ).rowcount
    total += n

for eng, rus in SYSTEM_MAP.items():
    n = conn.execute(
        "UPDATE chunk_content SET content = REPLACE(content, 'System: ' || ?, 'Система: ' || ?) "
        "WHERE chunk_id IN (SELECT id FROM chunks WHERE content_type='dtc' AND source_language='en') "
        "AND content LIKE ?",
        (eng, rus, f"%System: {eng}%")
    ).rowcount
    total += n

conn.commit()
conn.close()
print(f"Done. Total: {total} replacements")
