#!/usr/bin/env python3
"""Quick status check for all KB processes."""
import sqlite3, os
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB = ROOT / "knowledge-base" / "kb.db"
KB_DIR = ROOT / "knowledge-base"

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row

# Chunks
chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
src = conn.execute("SELECT source_language, COUNT(*) FROM chunks GROUP BY source_language").fetchall()

# Translations
total_cc = conn.execute("SELECT COUNT(*) FROM chunk_content").fetchone()[0]
orig = conn.execute("SELECT COUNT(*) FROM chunk_content WHERE translated_by = 'original'").fetchone()[0]
trans = total_cc - orig
by_lang = conn.execute("SELECT lang, COUNT(*) FROM chunk_content WHERE translated_by != 'original' GROUP BY lang ORDER BY lang").fetchall()
good = conn.execute("SELECT COUNT(*) FROM chunk_content WHERE translated_by != 'original' AND quality_score > 0").fetchone()[0]
haiku = conn.execute("SELECT COUNT(*) FROM chunk_content WHERE translated_by LIKE '%haiku%' OR translated_by LIKE '%claude%'").fetchone()[0]
utrobin = conn.execute("SELECT COUNT(*) FROM chunk_content WHERE translated_by LIKE '%utrobin%' OR translated_by LIKE '%m2m%'").fetchone()[0]

# Images
imgs = conn.execute("SELECT COUNT(*) FROM chunk_images").fetchone()[0]
cols = [r[1] for r in conn.execute("PRAGMA table_info(chunk_images)").fetchall()]
imgs_cap = conn.execute("SELECT COUNT(*) FROM chunk_images WHERE caption IS NOT NULL AND caption != ''").fetchone()[0] if "caption" in cols else 0
imgs_emb = conn.execute("SELECT COUNT(*) FROM chunk_images WHERE clip_embedding IS NOT NULL").fetchone()[0] if "clip_embedding" in cols else 0

conn.close()

# LanceDB
ldb_path = KB_DIR / "lancedb"
ldb_size = 0
if ldb_path.exists():
    for d, _, fs in os.walk(ldb_path):
        for f in fs:
            ldb_size += os.path.getsize(os.path.join(d, f))
ldb_size_mb = ldb_size // 1024 // 1024

# Training pairs files
print("=" * 60)
print("  DIAGNOSTICA KB — STATUS REPORT")
print("=" * 60)

print(f"\n[1] KNOWLEDGE BASE (kb.db)")
print(f"    Chunks total : {chunks:,}")
for lang, cnt in src:
    pct = cnt * 100 // chunks
    print(f"    src={lang}        : {cnt:,} ({pct}%)")

print(f"\n[2] TRANSLATIONS (chunk_content)")
print(f"    Originals    : {orig:,}")
print(f"    Translations : {trans:,}")
for lang, cnt in by_lang:
    pct = cnt * 100 // trans if trans else 0
    print(f"    lang={lang}       : {cnt:,} ({pct}%)")
print(f"    quality>0    : {good:,} / {trans:,} ({good*100//trans if trans else 0}%)")
print(f"    by Claude    : {haiku:,}")
print(f"    by Utrobin   : {utrobin:,}")

print(f"\n[3] IMAGES")
print(f"    chunk_images : {imgs:,} rows")
print(f"    captioned    : {imgs_cap:,}")
print(f"    CLIP emb     : {imgs_emb:,}")

print(f"\n[4] VECTOR DB (LanceDB)")
print(f"    vectors.lancedb : {ldb_size_mb} MB")
if ldb_path.exists():
    tables = [d.name for d in ldb_path.iterdir() if d.is_dir()]
    print(f"    tables : {tables}")

print(f"\n[5] TRAINING PAIRS FILES")
for f in sorted(KB_DIR.glob("training_pairs*.jsonl")):
    n = sum(1 for _ in open(f, encoding="utf-8"))
    print(f"    {f.name:<45} {n:>6} pairs")

print(f"\n[6] SCRIPTS STATUS")
scripts = [
    ("build_kb.py", "DONE"),
    ("translation_ab_test.py", "DONE — Utrobin M2M wins"),
    ("build_embeddings.py", "DONE — LanceDB + ColBERT"),
    ("translate_kb.py", "RUNNING — ZH->EN+RU tier 1"),
    ("fix_data_quality.py", "DONE"),
    ("fix_zh_residuals.py", "DONE — 108 ZH fixes"),
    ("link_images.py", "DONE — 1079 chunk_images"),
    ("caption_images.py", "WRITTEN — pending run"),
    ("embed_images.py", "WRITTEN — pending run"),
    ("api/server.py", "DONE — 10 endpoints"),
    ("frontend/knowledge-base.js", "DONE — API client v2"),
    ("run_all_translators.sh", "READY — 5-lang bridge plan"),
    ("test_ocr_debug.py", "DONE — OCR fixed!"),
]
for name, status in scripts:
    print(f"    {name:<35} {status}")
print("=" * 60)
