#!/usr/bin/env python3
"""
LLCAR Diagnostica — Re-OCR missing parts from table images.

Analyzes gaps in the parts table (missing hotspot positions per diagram),
then re-runs Qwen2.5-VL-7B on the corresponding table images with an
enhanced prompt that provides context about already-known parts and
asks specifically for missing positions.

Usage:
    python scripts/reocr_missing_parts.py                        # full run
    python scripts/reocr_missing_parts.py --analyze-only         # just show gaps
    python scripts/reocr_missing_parts.py --limit 5 --dry-run    # test 5 tables
    python scripts/reocr_missing_parts.py --device cuda:1        # specific GPU

Run on the WORKSTATION (192.168.50.2) which has Qwen2.5-VL-7B + 2x RTX 3090.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("reocr_parts")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_BASE_DIR = Path(__file__).resolve().parent.parent
_KB_DB = _BASE_DIR / "knowledge-base" / "kb.db"
_CONTENT_LIST = (
    _BASE_DIR
    / "mineru-output"
    / "941362155-2022-2023款理想L9零件手册"
    / "ocr"
    / "941362155-2022-2023款理想L9零件手册_content_list.json"
)
_IMAGE_BASE = (
    _BASE_DIR
    / "mineru-output"
    / "941362155-2022-2023款理想L9零件手册"
    / "ocr"
)

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

# Import system mappings from original OCR script
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_parts_tables import SYSTEMS, SUBS, ALL_NAMES, build_page_system_map


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------

def analyze_gaps(conn: sqlite3.Connection) -> list[dict]:
    """
    Find all diagrams where hotspot positions are missing.
    Returns list of gap records:
    [{system_en, page_idx, source_image, diagram_image,
      existing_hotspots: set, max_hotspot: int, missing_hotspots: list,
      existing_parts: list[dict]}]
    """
    # Get all parts grouped by system + diagram_image
    rows = conn.execute("""
        SELECT system_en, page_idx, source_image, diagram_image,
               hotspot_id, part_number, part_name_zh, part_name_en
        FROM parts
        WHERE hotspot_id != '' AND CAST(hotspot_id AS INTEGER) BETWEEN 1 AND 30
        ORDER BY system_en, page_idx, CAST(hotspot_id AS INTEGER)
    """).fetchall()

    # Group by (system, source_image) since that represents one OCR table
    groups = defaultdict(lambda: {
        "pages": set(),
        "diagram_image": None,
        "hotspots": set(),
        "max_hs": 0,
        "parts": [],
    })

    for r in rows:
        sys_en, page, src_img, diag_img, hs, pn, name_zh, name_en = r
        key = (sys_en, src_img or f"page_{page}")
        g = groups[key]
        g["pages"].add(page)
        g["diagram_image"] = diag_img
        hs_int = int(hs)
        g["hotspots"].add(hs_int)
        g["max_hs"] = max(g["max_hs"], hs_int)
        g["parts"].append({
            "hotspot": hs,
            "part_number": pn,
            "part_name_zh": name_zh,
            "part_name_en": name_en,
        })

    gaps = []
    for (sys_en, src_img), g in sorted(groups.items()):
        expected = set(range(1, g["max_hs"] + 1))
        missing = sorted(expected - g["hotspots"])
        if not missing:
            continue

        gaps.append({
            "system_en": sys_en,
            "page_idx": min(g["pages"]),
            "source_image": src_img if not src_img.startswith("page_") else None,
            "diagram_image": g["diagram_image"],
            "existing_hotspots": g["hotspots"],
            "max_hotspot": g["max_hs"],
            "missing_hotspots": missing,
            "missing_count": len(missing),
            "existing_parts": g["parts"],
        })

    return sorted(gaps, key=lambda x: -x["missing_count"])


def find_missing_pages(conn: sqlite3.Connection, content_list: list[dict]) -> list[dict]:
    """
    Find pages from content_list that have table images but no parts in DB.
    These are entire pages that the original OCR skipped or failed on.
    """
    # All pages with parts in DB
    db_pages = set()
    for row in conn.execute("SELECT DISTINCT page_idx FROM parts").fetchall():
        db_pages.add(row[0])

    # All pages with table images in content_list
    table_pages = {}
    for item in content_list:
        if item.get("type") == "table" and item.get("img_path"):
            pg = item.get("page_idx", -1)
            if pg >= 0:
                table_pages[pg] = item["img_path"]

    # Pages with tables but no parts
    missing = []
    page_map = build_page_system_map(content_list)
    for pg, img_path in sorted(table_pages.items()):
        if pg not in db_pages:
            sys_info = page_map.get(pg, {})
            missing.append({
                "page_idx": pg,
                "source_image": img_path,
                "system_en": sys_info.get("system_en", "UNKNOWN"),
                "system_zh": sys_info.get("system_zh", ""),
                "subsystem_en": sys_info.get("subsystem_en", ""),
                "subsystem_zh": sys_info.get("subsystem_zh", ""),
            })

    return missing


# ---------------------------------------------------------------------------
# Enhanced OCR prompt
# ---------------------------------------------------------------------------

def make_reocr_prompt(existing_parts: list[dict], missing_positions: list[int]) -> str:
    """Create a focused OCR prompt that tells the model what's already known."""
    known_lines = []
    for p in sorted(existing_parts, key=lambda x: int(x.get("hotspot", 0) or 0)):
        known_lines.append(f"  #{p['hotspot']}: {p['part_number']} ({p['part_name_zh']})")

    known_str = "\n".join(known_lines) if known_lines else "(none)"
    missing_str = ", ".join(f"#{m}" for m in missing_positions)

    return f"""This image shows a parts catalog table from a Li Auto L9 vehicle manual.

I already have these parts from this table:
{known_str}

But I'm MISSING positions: {missing_str}

Please extract ALL rows from the table, especially the missing positions listed above.
Each row has columns: 序号 (index), 热点ID (hotspot ID), 零件号码 (part number), 零件名称 (part name in Chinese).

Return ONLY a JSON array:
[{{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "零件名称"}}]

Rules:
- Extract EVERY row you can see, including ones I already have
- Part numbers typically start with X01-, M01-, Q-prefixed codes, or 7-digit numbers
- If a cell is empty, use empty string ""
- Pay special attention to rows for positions: {missing_str}
- If the image is not a parts table, return: []"""


FRESH_OCR_PROMPT = """This image shows a parts catalog table from a Li Auto L9 vehicle manual.
Extract ALL rows from the table. Each row has columns:
- 序号 (index number)
- 热点ID (hotspot ID)
- 零件号码 (part number)
- 零件名称 (part name in Chinese)

Return ONLY a JSON array, no other text:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "零件名称"}]

Rules:
- Extract EVERY row, including multi-line cells
- Part numbers typically start with X01-, M01-, Q-prefixed codes
- If a cell is empty, use empty string ""
- Read carefully — do NOT skip any rows
- If the image is not a parts table, return: []"""


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(device: str) -> tuple[Any, Any]:
    """Load Qwen2.5-VL-7B-Instruct.

    CRITICAL: On the workstation (2x RTX 3090, transformers 5.2):
    - MUST use bfloat16 (float16 produces garbage)
    - MUST use attn_implementation="eager" (default crashes)
    - MUST NOT use device_map — load on CPU first, then .to(device)
    """
    import torch
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    log.info("Loading %s on CPU first, then moving to %s …", MODEL_ID, device)
    t0 = time.time()

    processor = AutoProcessor.from_pretrained(
        MODEL_ID, trust_remote_code=True, use_fast=False,
    )

    # Step 1: Load on CPU (no device_map!)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        attn_implementation="eager",
        device_map=None,  # Explicit: do NOT auto-map
    )

    # Step 2: Move to GPU manually
    log.info("Moving model to %s …", device)
    model = model.to(device)
    model.eval()

    elapsed = time.time() - t0
    vram = 0.0
    if torch.cuda.is_available():
        dev_idx = int(device.split(":")[-1]) if ":" in device else 0
        vram = torch.cuda.memory_allocated(dev_idx) / 1024 ** 3
    log.info("Model loaded in %.1f s (VRAM: %.1f GB)", elapsed, vram)
    return model, processor


def ocr_table_image(
    model: Any,
    processor: Any,
    image_path: Path,
    device: str,
    prompt: str,
    max_side: int = 1280,  # Higher resolution than original (1024)
) -> list[dict]:
    """Run Qwen2.5-VL on a single table image with custom prompt."""
    import torch
    from PIL import Image as PILImage

    try:
        pil_image = PILImage.open(image_path).convert("RGB")
    except Exception as exc:
        log.warning("Cannot read image %s: %s", image_path, exc)
        return []

    w, h = pil_image.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        pil_image = pil_image.resize(
            (int(w * scale), int(h * scale)), PILImage.LANCZOS
        )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ],
        }
    ]

    try:
        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
        inputs = processor(
            text=[text], images=[pil_image], return_tensors="pt", padding=True,
        ).to(device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs, max_new_tokens=4096, do_sample=False,
            )

        input_len = inputs["input_ids"].shape[1]
        generated = output_ids[0, input_len:]
        response = processor.decode(generated, skip_special_tokens=True).strip()

        del inputs, output_ids
        torch.cuda.empty_cache()

        return _parse_json_response(response)

    except Exception as exc:
        log.error("Inference failed for %s: %s", image_path, exc)
        torch.cuda.empty_cache()
        return []


def _parse_json_response(response: str) -> list[dict]:
    """Parse JSON array from model response."""
    try:
        data = json.loads(response)
        if isinstance(data, list):
            return [_normalize_row(r) for r in data if isinstance(r, dict)]
    except json.JSONDecodeError:
        pass

    match = re.search(r'\[.*\]', response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return [_normalize_row(r) for r in data if isinstance(r, dict)]
        except json.JSONDecodeError:
            pass

    rows = []
    for line in response.split('\n'):
        line = line.strip().rstrip(',')
        if line.startswith('{'):
            try:
                obj = json.loads(line)
                rows.append(_normalize_row(obj))
            except json.JSONDecodeError:
                continue
    return rows


def _normalize_row(row: dict) -> dict:
    return {
        "idx": str(row.get("idx", row.get("序号", ""))),
        "hotspot": str(row.get("hotspot", row.get("热点ID", row.get("hotspot_id", "")))),
        "part_number": str(row.get("part_number", row.get("零件号码", ""))).strip(),
        "part_name": str(row.get("part_name", row.get("零件名称", ""))).strip(),
    }


# ---------------------------------------------------------------------------
# Database insert (only NEW parts)
# ---------------------------------------------------------------------------

def insert_new_parts(
    conn: sqlite3.Connection,
    rows: list[dict],
    system_info: dict,
    page_idx: int,
    source_image: str,
    existing_hotspots: set[int] | None = None,
) -> tuple[int, int]:
    """
    Insert only NEW parts (not already in DB for this page/system).
    Returns (inserted_count, skipped_count).
    """
    # Get existing (part_number, hotspot_id) for this page
    existing = set()
    for r in conn.execute(
        "SELECT part_number, hotspot_id FROM parts WHERE page_idx = ? AND system_en = ?",
        (page_idx, system_info.get("system_en", "")),
    ).fetchall():
        existing.add((r[0], r[1]))

    inserted = 0
    skipped = 0

    for row in rows:
        pn = row.get("part_number", "").strip()
        name = row.get("part_name", "").strip()
        hs = row.get("hotspot", "").strip()
        if not pn or not name:
            continue

        # Skip if already exists
        if (pn, hs) in existing:
            skipped += 1
            continue

        # Also skip if hotspot already covered (different part number)
        if existing_hotspots and hs:
            try:
                if int(hs) in existing_hotspots:
                    skipped += 1
                    continue
            except ValueError:
                pass

        name_en = SUBS.get(name, "")

        conn.execute(
            """INSERT INTO parts
               (part_number, part_name_zh, part_name_en, hotspot_id,
                system_zh, system_en, subsystem_zh, subsystem_en,
                page_idx, source_image, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                pn,
                name,
                name_en or None,
                hs or None,
                system_info.get("system_zh", ""),
                system_info.get("system_en", ""),
                system_info.get("subsystem_zh", ""),
                system_info.get("subsystem_en", ""),
                page_idx,
                source_image,
                0.8,  # Lower confidence for re-OCR results
            ),
        )
        inserted += 1

    return inserted, skipped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_gap_report(gaps: list[dict], missing_pages: list[dict]) -> None:
    """Print formatted gap analysis report."""
    print("\n" + "=" * 80)
    print("  PARTS TABLE GAP ANALYSIS")
    print("=" * 80)

    print(f"\n{'System':<40} {'Page':>4} {'Have':>5} {'Max':>4} {'Miss':>5}  Missing positions")
    print("-" * 100)

    total_missing = 0
    for g in gaps:
        missing = g["missing_hotspots"]
        total_missing += len(missing)
        miss_str = ", ".join(str(m) for m in missing[:15])
        if len(missing) > 15:
            miss_str += f" ... (+{len(missing)-15})"
        print(f"{g['system_en']:<40} {g['page_idx']:>4} {len(g['existing_hotspots']):>5} "
              f"{g['max_hotspot']:>4} {len(missing):>5}  {miss_str}")

    print("-" * 100)
    print(f"Total diagrams with gaps: {len(gaps)}")
    print(f"Total missing hotspot positions: {total_missing}")

    if missing_pages:
        print(f"\n{'='*80}")
        print("  ENTIRELY MISSING PAGES (table images exist but 0 parts in DB)")
        print("=" * 80)
        print(f"{'Page':>5}  {'System':<40} Table image")
        print("-" * 90)
        for mp in missing_pages:
            print(f"{mp['page_idx']:>5}  {mp['system_en']:<40} {mp['source_image'][-50:]}")
        print(f"Total: {len(missing_pages)} missing pages")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-OCR missing parts from L9 catalog tables",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default=str(_KB_DB), help="Path to kb.db")
    parser.add_argument("--device", default="cuda:0", help="CUDA device")
    parser.add_argument("--limit", type=int, default=None, help="Max tables to re-OCR")
    parser.add_argument("--dry-run", action="store_true", help="OCR but don't write to DB")
    parser.add_argument("--analyze-only", action="store_true", help="Only show gap report")
    parser.add_argument("--output-log", default=None, help="JSONL log for OCR results")
    parser.add_argument("--max-side", type=int, default=1280,
                        help="Max image side (px). Higher = more accurate but slower")
    parser.add_argument("--retry-oom", default=None,
                        help="Path to oom_failed_images.json — retry only those images")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    db_path = Path(args.db_path)
    if not db_path.exists():
        log.error("kb.db not found at %s", db_path)
        sys.exit(1)

    if not _CONTENT_LIST.exists():
        log.error("content_list.json not found at %s", _CONTENT_LIST)
        sys.exit(1)

    # Load content list
    with open(_CONTENT_LIST, "r", encoding="utf-8") as f:
        content_list = json.load(f)

    # Open DB
    conn = sqlite3.connect(str(db_path), timeout=120)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    # Build page→system mapping
    page_map = build_page_system_map(content_list)

    # --- Phase 1: Analyze gaps ---
    gaps = analyze_gaps(conn)
    missing_pages = find_missing_pages(conn, content_list)

    print_gap_report(gaps, missing_pages)

    if args.analyze_only:
        conn.close()
        return

    # --- Phase 2: Build re-OCR task list ---
    tasks = []

    # Task type A: Re-OCR existing table images with enhanced prompt (for gaps)
    for g in gaps:
        if not g["source_image"]:
            continue
        img_path = _IMAGE_BASE / g["source_image"]
        if not img_path.exists():
            log.warning("Table image not found: %s", img_path)
            continue
        tasks.append({
            "type": "reocr",
            "image_path": img_path,
            "source_image": g["source_image"],
            "page_idx": g["page_idx"],
            "system_en": g["system_en"],
            "system_info": page_map.get(g["page_idx"], {}),
            "existing_parts": g["existing_parts"],
            "existing_hotspots": g["existing_hotspots"],
            "missing_hotspots": g["missing_hotspots"],
            "prompt": make_reocr_prompt(g["existing_parts"], g["missing_hotspots"]),
        })

    # Task type B: Fresh OCR on entirely missing pages
    for mp in missing_pages:
        img_path = _IMAGE_BASE / mp["source_image"]
        if not img_path.exists():
            log.warning("Table image not found: %s", img_path)
            continue
        tasks.append({
            "type": "fresh",
            "image_path": img_path,
            "source_image": mp["source_image"],
            "page_idx": mp["page_idx"],
            "system_en": mp["system_en"],
            "system_info": {
                "system_zh": mp["system_zh"],
                "system_en": mp["system_en"],
                "subsystem_zh": mp["subsystem_zh"],
                "subsystem_en": mp["subsystem_en"],
            },
            "existing_parts": [],
            "existing_hotspots": set(),
            "missing_hotspots": [],
            "prompt": FRESH_OCR_PROMPT,
        })

    log.info("Total re-OCR tasks: %d (reocr=%d, fresh=%d)",
             len(tasks),
             sum(1 for t in tasks if t["type"] == "reocr"),
             sum(1 for t in tasks if t["type"] == "fresh"))

    if args.limit:
        tasks = tasks[:args.limit]
        log.info("Limited to %d tasks", args.limit)

    # --- Phase 2b: If --retry-oom, override task list with only OOM failures ---
    if args.retry_oom:
        retry_path = Path(args.retry_oom)
        if not retry_path.exists():
            log.error("OOM retry file not found: %s", retry_path)
            conn.close()
            sys.exit(1)
        with open(retry_path, "r", encoding="utf-8") as f:
            oom_list = json.load(f)
        log.info("Retrying %d OOM-failed images with max_side=%d", len(oom_list), args.max_side)

        oom_images = {entry["image"] for entry in oom_list}
        tasks = [t for t in tasks if t["source_image"] in oom_images]
        log.info("Matched %d tasks from OOM retry list", len(tasks))

    if not tasks:
        log.info("No tasks to process.")
        conn.close()
        return

    # --- Phase 3: Load model and process ---
    model, processor = load_model(args.device)

    log_fh = None
    if args.output_log:
        log_fh = open(args.output_log, "a", encoding="utf-8")

    t_start = time.time()
    total_new = 0
    total_skipped = 0

    for i, task in enumerate(tasks):
        rows = ocr_table_image(
            model, processor, task["image_path"], args.device,
            task["prompt"], max_side=args.max_side,
        )

        new_count = 0
        skip_count = 0

        if rows:
            if not args.dry_run:
                new_count, skip_count = insert_new_parts(
                    conn, rows, task["system_info"], task["page_idx"],
                    task["source_image"], task["existing_hotspots"],
                )
                total_new += new_count
                total_skipped += skip_count
                if (i + 1) % 10 == 0:
                    conn.commit()
            else:
                # In dry-run, estimate new parts
                for row in rows:
                    hs = row.get("hotspot", "")
                    try:
                        if int(hs) not in task["existing_hotspots"]:
                            new_count += 1
                        else:
                            skip_count += 1
                    except (ValueError, TypeError):
                        new_count += 1
                total_new += new_count
                total_skipped += skip_count

        if log_fh:
            log_fh.write(json.dumps({
                "type": task["type"],
                "image": task["source_image"],
                "page_idx": task["page_idx"],
                "system": task["system_en"],
                "ocr_count": len(rows),
                "new_count": new_count,
                "skip_count": skip_count,
                "missing_positions": task["missing_hotspots"],
                "parts": rows,
            }, ensure_ascii=False) + "\n")

        elapsed = time.time() - t_start
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (len(tasks) - i - 1) / rate if rate > 0 else 0
        log.info(
            "  %d/%d  [%s] %s pg=%d  ocr=%d new=%d skip=%d  %.1f/s  ETA %.0fs",
            i + 1, len(tasks), task["type"], task["system_en"][:25],
            task["page_idx"], len(rows), new_count, skip_count, rate, eta,
        )

    # Final commit
    if not args.dry_run:
        conn.commit()

    conn.close()
    if log_fh:
        log_fh.close()

    elapsed_total = time.time() - t_start
    print("\n" + "=" * 60)
    print(f"  Done in {elapsed_total:.1f} s")
    print(f"  Tasks processed: {len(tasks)}")
    print(f"  New parts inserted: {total_new}")
    print(f"  Skipped (already exist): {total_skipped}")
    if args.dry_run:
        print("  *** DRY RUN — no DB writes ***")
    print("=" * 60)


if __name__ == "__main__":
    main()
