#!/usr/bin/env python3
"""Fix DTC content: translate English system/severity/drive values to Russian."""
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

DRIVE_MAP = {
    "yes_limited": "Да, с ограничениями",
    "yes": "Да, безопасно",
    "no": "Нет, опасно!",
}

SEV_MAP = {
    "1": "1 — Низкая",
    "2": "2 — Умеренная",
    "3": "3 — Средняя",
    "4": "4 — Высокая",
    "5": "5 — Критическая",
}

def fix_table(conn, table, content_col, where_extra=""):
    total = 0
    for eng, rus in SYSTEM_MAP.items():
        old = f"Система: {eng}"
        new = f"Система: {rus}"
        n = conn.execute(
            f"UPDATE {table} SET {content_col} = REPLACE({content_col}, ?, ?) "
            f"WHERE {content_col} LIKE ? {where_extra}",
            (old, new, f"%{old}%")
        ).rowcount
        total += n

    for eng, rus in DRIVE_MAP.items():
        old = f"Можно ли ехать: {eng}"
        new = f"Можно ли ехать: {rus}"
        n = conn.execute(
            f"UPDATE {table} SET {content_col} = REPLACE({content_col}, ?, ?) "
            f"WHERE {content_col} LIKE ? {where_extra}",
            (old, new, f"%{old}%")
        ).rowcount
        total += n

    for num, label in SEV_MAP.items():
        old = f"Серьёзность: {num}\n"
        new = f"Серьёзность: {label}\n"
        n = conn.execute(
            f"UPDATE {table} SET {content_col} = REPLACE({content_col}, ?, ?) "
            f"WHERE {content_col} LIKE ? {where_extra}",
            (old, new, f"%{old}%")
        ).rowcount
        total += n

    return total

conn = sqlite3.connect(str(DB))

# Fix chunks table (DTC only)
n1 = fix_table(conn, "chunks", "content", "AND content_type='dtc'")
print(f"chunks: {n1} replacements")

# Fix chunk_content table
n2 = fix_table(conn, "chunk_content", "content",
               "AND chunk_id IN (SELECT id FROM chunks WHERE content_type='dtc')")
print(f"chunk_content: {n2} replacements")

conn.commit()
conn.close()
print(f"Done. Total: {n1 + n2}")
