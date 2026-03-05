#!/usr/bin/env python3
"""
Export parts catalog ZH↔EN translation pairs for fine-tuning.

This is part of the self-learning pipeline:
1. OCR extracts parts (ZH names) from catalog images
2. Translation fills in EN names (via glossary, Qwen, Sonnet)
3. This script exports verified pairs as training data
4. Fine-tune model learns automotive terminology

Training pairs format matches training_pairs_tier1.jsonl schema.
Pairs are deduplicated and filtered for quality.

Usage:
    python scripts/export_parts_training_pairs.py
    python scripts/export_parts_training_pairs.py --min-zh-len 2 --output pairs.jsonl
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from hashlib import md5

_BASE_DIR = Path(__file__).resolve().parent.parent
_KB_DB = _BASE_DIR / "knowledge-base" / "kb.db"
_OUTPUT = _BASE_DIR / "knowledge-base" / "training_pairs_parts.jsonl"


def export_pairs(db_path: Path, output_path: Path, min_zh_len: int = 2) -> int:
    """Export ZH↔EN pairs from parts table."""
    conn = sqlite3.connect(str(db_path))

    rows = conn.execute("""
        SELECT DISTINCT part_name_zh, part_name_en, system_zh, system_en,
                        subsystem_zh, subsystem_en
        FROM parts
        WHERE part_name_zh IS NOT NULL AND part_name_zh != ''
          AND part_name_en IS NOT NULL AND part_name_en != ''
          AND LENGTH(part_name_zh) >= ?
          AND LENGTH(part_name_en) >= 2
    """, (min_zh_len,)).fetchall()

    conn.close()

    # Deduplicate by (zh, en)
    seen = set()
    pairs = []
    for name_zh, name_en, sys_zh, sys_en, sub_zh, sub_en in rows:
        key = (name_zh.strip(), name_en.strip())
        if key in seen:
            continue
        seen.add(key)

        pair_id = md5(f"{name_zh}_{name_en}".encode()).hexdigest()[:12]

        # ZH → EN pair
        pairs.append({
            "id": f"parts_zh_en_{pair_id}",
            "source_lang": "zh",
            "target_lang": "en",
            "source": name_zh.strip(),
            "source_title": f"{sys_zh} / {sub_zh}" if sub_zh else sys_zh,
            "translation": name_en.strip(),
            "translation_title": f"{sys_en} / {sub_en}" if sub_en else sys_en,
            "terminology_score": 1.0,
            "quality_score": 0.9,  # OCR-derived, slightly lower confidence
            "model": "ocr_parts_catalog",
            "domain": "automotive_parts",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

        # EN → ZH pair (reverse)
        pairs.append({
            "id": f"parts_en_zh_{pair_id}",
            "source_lang": "en",
            "target_lang": "zh",
            "source": name_en.strip(),
            "source_title": f"{sys_en} / {sub_en}" if sub_en else sys_en,
            "translation": name_zh.strip(),
            "translation_title": f"{sys_zh} / {sub_zh}" if sub_zh else sys_zh,
            "terminology_score": 1.0,
            "quality_score": 0.9,
            "model": "ocr_parts_catalog",
            "domain": "automotive_parts",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    # Also generate system/subsystem name pairs
    conn2 = sqlite3.connect(str(db_path))
    sys_rows = conn2.execute("""
        SELECT DISTINCT system_zh, system_en FROM parts
        WHERE system_zh != '' AND system_en != ''
        UNION
        SELECT DISTINCT subsystem_zh, subsystem_en FROM parts
        WHERE subsystem_zh != '' AND subsystem_en != ''
    """).fetchall()
    conn2.close()

    for zh, en in sys_rows:
        key = (zh.strip(), en.strip())
        if key in seen:
            continue
        seen.add(key)
        pair_id = md5(f"{zh}_{en}".encode()).hexdigest()[:12]
        pairs.append({
            "id": f"parts_sys_zh_en_{pair_id}",
            "source_lang": "zh",
            "target_lang": "en",
            "source": zh.strip(),
            "translation": en.strip(),
            "terminology_score": 1.0,
            "quality_score": 1.0,
            "model": "ocr_parts_catalog",
            "domain": "automotive_systems",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    # Write
    with open(output_path, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    return len(pairs)


def main():
    parser = argparse.ArgumentParser(description="Export parts training pairs")
    parser.add_argument("--db-path", default=str(_KB_DB))
    parser.add_argument("--output", default=str(_OUTPUT))
    parser.add_argument("--min-zh-len", type=int, default=2, help="Min Chinese name length")
    args = parser.parse_args()

    count = export_pairs(Path(args.db_path), Path(args.output), args.min_zh_len)
    print(f"Exported {count} training pairs to {args.output}")

    # Summary
    zh_en = sum(1 for _ in open(args.output, encoding="utf-8"))
    existing = 0
    for f in Path(args.output).parent.glob("training_pairs_*.jsonl"):
        if f.name != Path(args.output).name:
            existing += sum(1 for _ in open(f, encoding="utf-8"))
    print(f"Total training pairs (all files): {existing + zh_en}")


if __name__ == "__main__":
    main()
