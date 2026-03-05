#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('C:/Diagnostica-KB-Package/knowledge-base/kb.db')

# Проверить примеры «Подсказка»
podkazka = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "  AND (cc.content LIKE '%Подсказка%' OR cc.content LIKE '%подсказка%') "
    "LIMIT 5"
).fetchall()
print(f'=== Подсказка examples ({len(podkazka)} shown) ===')
for r in podkazka:
    m = re.search(r'.{0,30}[Пп]одсказка.{0,80}', r[1])
    if m:
        print(f'  [{r[0]}] q={r[2]:.2f}: {m.group()}')
print()

# «во время вождения»
vozhd = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "  AND cc.content LIKE '%во время вождения%' "
    "LIMIT 5"
).fetchall()
print(f'=== во время вождения ({len(vozhd)} shown) ===')
for r in vozhd:
    m = re.search(r'.{0,20}во\s+время\s+вождения.{0,60}', r[1])
    if m:
        print(f'  [{r[0]}] q={r[2]:.2f}: {m.group()}')
print()

# «пожалуйста»
pozh = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "  AND cc.content LIKE '%пожалуйста%' "
    "LIMIT 8"
).fetchall()
print(f'=== пожалуйста ({len(pozh)} shown) ===')
for r in pozh:
    m = re.search(r'.{0,20}пожалуйста.{0,100}', r[1], re.IGNORECASE)
    if m:
        print(f'  [{r[0]}] q={r[2]:.2f}: {m.group()}')
print()

# Смешанный регистр меток
lower = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "  AND (cc.content LIKE '%Внимание%' OR cc.content LIKE '%Примечание%' OR cc.content LIKE '%Предупреждение%') "
    "LIMIT 5"
).fetchall()
print(f'=== Смешанный регистр ({len(lower)} shown) ===')
for r in lower:
    m = re.search(r'.{0,10}(Внимание|Примечание|Предупреждение).{0,80}', r[1])
    if m:
        print(f'  [{r[0]}] q={r[2]:.2f}: {m.group()}')

# Проверим пример хорошего и плохого чанка
print('\n=== Пример quality=0.0, хороший текст? ===')
good0 = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 AND cc.quality_score = 0.0 "
    "LIMIT 3"
).fetchall()
for r in good0:
    print(f'\n  [{r[0]}] q={r[2]:.2f}')
    print(f'  {r[1][:300]}')

# Проверим пример quality=1.0
print('\n=== Пример quality=1.0 ===')
good1 = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 AND cc.quality_score = 1.0 "
    "LIMIT 2"
).fetchall()
for r in good1:
    print(f'\n  [{r[0]}] q={r[2]:.2f}')
    print(f'  {r[1][:300]}')

# Проверим 理想同学 в тексте
print('\n=== 理想同学 variants ===')
tx = conn.execute(
    "SELECT cc.chunk_id, cc.content, cc.quality_score "
    "FROM chunk_content cc "
    "JOIN chunks c ON c.id = cc.chunk_id "
    "WHERE cc.lang = 'ru' AND cc.translated_by != 'original' "
    "  AND c.has_warnings = 1 "
    "  AND (cc.content LIKE '%Tongxue%' OR cc.content LIKE '%tongxue%' "
    "    OR cc.content LIKE '%помощник%' OR cc.content LIKE '%Lixiang%') "
    "LIMIT 5"
).fetchall()
for r in tx:
    m = re.search(r'.{0,20}(tongxue|Tongxue|помощник|Lixiang|lixiang).{0,80}', r[1], re.IGNORECASE)
    if m:
        print(f'  [{r[0]}] q={r[2]:.2f}: {m.group()}')

conn.close()
