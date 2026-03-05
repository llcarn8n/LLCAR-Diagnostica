#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('C:/Diagnostica-KB-Package/knowledge-base/kb.db')

BASE_WHERE = (
    "cc.lang = 'ru' AND cc.translated_by != 'original' "
    "AND c.has_warnings = 1"
)

def count_label(like_pattern):
    return conn.execute(
        "SELECT COUNT(DISTINCT cc.chunk_id) "
        "FROM chunk_content cc "
        "JOIN chunks c ON c.id = cc.chunk_id "
        f"WHERE {BASE_WHERE} AND cc.content LIKE ?",
        (like_pattern,)
    ).fetchone()[0]

print("=== Метки предупреждений (CAPS vs смешанный регистр) ===")
print(f"  ПРЕДУПРЕЖДЕНИЕ (CAPS): {count_label('%ПРЕДУПРЕЖДЕНИЕ%')}")
print(f"  Предупреждение (Title): {count_label('%Предупреждение%')}")
print(f"  ВНИМАНИЕ (CAPS): {count_label('%ВНИМАНИЕ%')}")
print(f"  Внимание (Title): {count_label('%Внимание%')}")
print(f"  ПРИМЕЧАНИЕ (CAPS): {count_label('%ПРИМЕЧАНИЕ%')}")
print(f"  Примечание (Title): {count_label('%Примечание%')}")
print(f"  ОПАСНОСТЬ (CAPS): {count_label('%ОПАСНОСТЬ%')}")
print(f"  Подсказка: {count_label('%Подсказка%')}")
print(f"  Warning (EN): {count_label('%Warning%')}")
print(f"  Note (EN): {count_label('%Note%')}")
print()

# Bold метки
print("=== Bold метки (**Label**) ===")
print(f"  **Предупреждение**: {count_label('%**Предупреждение**%')}")
print(f"  **Внимание**: {count_label('%**Внимание**%')}")
print(f"  **Примечание**: {count_label('%**Примечание**%')}")
print(f"  **Подсказка**: {count_label('%**Подсказка**%')}")
print()

# Примеры «пожалуйста» в контексте
pozh = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "  AND cc.content LIKE '%пожалуйста%' "
    "LIMIT 9"
).fetchall()
print(f"=== пожалуйста (все {len(pozh)} примеров) ===")
for r in pozh:
    m = re.search(r'.{0,30}пожалуйста.{0,100}', r[1], re.IGNORECASE)
    if m:
        print(f"  [{r[0]}] q={r[2]:.2f}: {m.group()}")
print()

# Проверить «во время вождения» конкретные примеры
vozhd = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "  AND cc.content LIKE '%во время вождения%' "
    "LIMIT 10"
).fetchall()
print(f"=== во время вождения ({len(vozhd)} примеров) ===")
for r in vozhd:
    m = re.search(r'.{0,50}во\s+время\s+вождения.{0,100}', r[1])
    if m:
        print(f"  [{r[0]}] q={r[2]:.2f}: {m.group()}")
print()

# Выборка лучших (quality=1.0) примеров для понимания эталона
good = conn.execute(
    "SELECT cc.chunk_id, cc.content "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 AND cc.quality_score = 1.0 "
    "LIMIT 4"
).fetchall()
print("=== Эталон quality=1.0 (первые 400 символов) ===")
for r in good:
    print(f"\n[{r[0]}]")
    print(r[1][:400])

conn.close()
