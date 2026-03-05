#!/usr/bin/env python3
"""
Render missing PDF pages via PyMuPDF and prepare them for OCR.

Some pages are completely missing from MinerU's content_list.json output.
This script:
1. Identifies which pages are missing from content_list
2. Renders them from the original PDF at high DPI
3. Saves as table-like images ready for Qwen2.5-VL OCR
4. Optionally runs OCR directly (if --ocr flag and model available)

Usage:
    python scripts/render_missing_pages.py                     # render only
    python scripts/render_missing_pages.py --ocr --device cuda:0  # render + OCR
    python scripts/render_missing_pages.py --pages 85,125,150  # specific pages
"""
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("render_pages")

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
_PDF_PATH = (
    _BASE_DIR
    / "mineru-output"
    / "941362155-2022-2023款理想L9零件手册"
    / "ocr"
    / "941362155-2022-2023款理想L9零件手册_origin.pdf"
)
_IMAGE_BASE = (
    _BASE_DIR
    / "mineru-output"
    / "941362155-2022-2023款理想L9零件手册"
    / "ocr"
)
_RENDERED_DIR = _IMAGE_BASE / "rendered_missing"

MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_parts_tables import SYSTEMS, SUBS, build_page_system_map


def find_missing_pages(content_list: list[dict]) -> list[int]:
    """Find page indices missing from content_list entirely."""
    cl_pages = set(item.get("page_idx", -1) for item in content_list)
    cl_pages.discard(-1)
    if not cl_pages:
        return []
    all_expected = set(range(min(cl_pages), max(cl_pages) + 1))
    return sorted(all_expected - cl_pages)


def render_pages(pdf_path: Path, pages: list[int], output_dir: Path, dpi: int = 300) -> dict[int, Path]:
    """Render specified PDF pages to PNG images."""
    import fitz  # PyMuPDF

    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    rendered = {}

    for pg_idx in pages:
        if pg_idx >= len(doc):
            log.warning("Page %d out of range (PDF has %d pages)", pg_idx, len(doc))
            continue

        page = doc[pg_idx]
        # Render at high DPI for OCR
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        out_path = output_dir / f"page_{pg_idx:04d}.png"
        pix.save(str(out_path))
        rendered[pg_idx] = out_path
        log.info("Rendered page %d → %s (%dx%d)", pg_idx, out_path.name, pix.width, pix.height)

    doc.close()
    return rendered


def load_model(device: str) -> tuple[Any, Any]:
    """Load Qwen2.5-VL-7B-Instruct (same as reocr_missing_parts.py)."""
    import torch
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    log.info("Loading %s on CPU first, then moving to %s …", MODEL_ID, device)
    t0 = time.time()

    processor = AutoProcessor.from_pretrained(
        MODEL_ID, trust_remote_code=True, use_fast=False,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        attn_implementation="eager",
        device_map=None,
    )
    log.info("Moving model to %s …", device)
    model = model.to(device)
    model.eval()

    elapsed = time.time() - t0
    log.info("Model loaded in %.1f s", elapsed)
    return model, processor


OCR_PROMPT = """This image is a full page from a Li Auto L9 parts catalog PDF.
It may contain:
- An assembly diagram (exploded view with numbered hotspot positions)
- A parts table with columns: 序号 (index), 热点ID (hotspot ID), 零件号码 (part number), 零件名称 (part name)
- Or both on the same page

Extract ALL parts table rows you can see. Return ONLY a JSON array:
[{"idx": 1, "hotspot": "1", "part_number": "X01-12345678", "part_name": "零件名称"}]

Rules:
- Extract EVERY row from any parts table visible on the page
- Part numbers typically start with X01-, M01-, Q-prefixed codes, or 7-digit numbers
- If a cell is empty, use empty string ""
- If there is NO parts table on the page, return: []
- Do NOT describe the diagram — only extract tabular data"""


def ocr_rendered_page(
    model: Any,
    processor: Any,
    image_path: Path,
    device: str,
    max_side: int = 1024,
) -> list[dict]:
    """Run OCR on a rendered PDF page."""
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
                {"type": "text", "text": OCR_PROMPT},
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
        import torch
        torch.cuda.empty_cache()
        return []


def _parse_json_response(response: str) -> list[dict]:
    """Parse JSON array from model response."""
    import re
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
    return []


def _normalize_row(row: dict) -> dict:
    return {
        "idx": str(row.get("idx", row.get("序号", ""))),
        "hotspot": str(row.get("hotspot", row.get("热点ID", row.get("hotspot_id", "")))),
        "part_number": str(row.get("part_number", row.get("零件号码", ""))).strip(),
        "part_name": str(row.get("part_name", row.get("零件名称", ""))).strip(),
    }


def insert_parts(
    conn: sqlite3.Connection,
    rows: list[dict],
    system_info: dict,
    page_idx: int,
    source_image: str,
) -> tuple[int, int]:
    """Insert only NEW parts for this page."""
    existing = set()
    for r in conn.execute(
        "SELECT part_number, hotspot_id FROM parts WHERE page_idx = ?",
        (page_idx,),
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

        if (pn, hs) in existing:
            skipped += 1
            continue

        name_en = SUBS.get(name, "")

        conn.execute(
            """INSERT INTO parts
               (part_number, part_name_zh, part_name_en, hotspot_id,
                system_zh, system_en, subsystem_zh, subsystem_en,
                page_idx, source_image, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                pn, name, name_en or None, hs or None,
                system_info.get("system_zh", ""),
                system_info.get("system_en", ""),
                system_info.get("subsystem_zh", ""),
                system_info.get("subsystem_en", ""),
                page_idx, source_image, 0.7,  # Lower confidence for rendered pages
            ),
        )
        inserted += 1

    return inserted, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Render missing PDF pages and OCR them")
    parser.add_argument("--pdf", default=str(_PDF_PATH), help="Path to origin PDF")
    parser.add_argument("--db-path", default=str(_KB_DB), help="Path to kb.db")
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI")
    parser.add_argument("--pages", default=None, help="Comma-separated page indices to render")
    parser.add_argument("--ocr", action="store_true", help="Also run OCR on rendered pages")
    parser.add_argument("--device", default="cuda:0", help="CUDA device for OCR")
    parser.add_argument("--max-side", type=int, default=1024, help="Max image side for OCR")
    parser.add_argument("--dry-run", action="store_true", help="OCR but don't write to DB")
    parser.add_argument("--output-log", default=None, help="JSONL log for OCR results")
    parser.add_argument("--render-only", action="store_true", help="Only render, skip OCR")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        log.error("PDF not found at %s", pdf_path)
        sys.exit(1)

    # Load content list
    with open(_CONTENT_LIST, "r", encoding="utf-8") as f:
        content_list = json.load(f)

    page_map = build_page_system_map(content_list)

    # Determine which pages to render
    if args.pages:
        pages = [int(p.strip()) for p in args.pages.split(",")]
    else:
        pages = find_missing_pages(content_list)

    log.info("Missing pages to render: %d — %s", len(pages), pages)

    # Step 1: Render
    rendered = render_pages(pdf_path, pages, _RENDERED_DIR, dpi=args.dpi)
    log.info("Rendered %d pages to %s", len(rendered), _RENDERED_DIR)

    if args.render_only or not args.ocr:
        print(f"\nRendered {len(rendered)} pages. Use --ocr to also run OCR.")
        return

    # Step 2: OCR
    model, processor = load_model(args.device)

    conn = sqlite3.connect(str(args.db_path), timeout=120)
    conn.execute("PRAGMA journal_mode=WAL")

    log_fh = None
    if args.output_log:
        log_fh = open(args.output_log, "a", encoding="utf-8")

    total_new = 0
    total_skipped = 0

    for i, (pg_idx, img_path) in enumerate(sorted(rendered.items())):
        rows = ocr_rendered_page(model, processor, img_path, args.device, args.max_side)

        sys_info = page_map.get(pg_idx, {
            "system_zh": "", "system_en": "UNKNOWN",
            "subsystem_zh": "", "subsystem_en": "",
        })

        new_count = 0
        skip_count = 0

        if rows and not args.dry_run:
            new_count, skip_count = insert_parts(
                conn, rows, sys_info, pg_idx,
                f"rendered_missing/page_{pg_idx:04d}.png",
            )
            total_new += new_count
            total_skipped += skip_count
            conn.commit()

        if log_fh:
            log_fh.write(json.dumps({
                "type": "rendered",
                "image": str(img_path),
                "page_idx": pg_idx,
                "system": sys_info.get("system_en", "UNKNOWN"),
                "ocr_count": len(rows),
                "new_count": new_count,
                "skip_count": skip_count,
                "parts": rows,
            }, ensure_ascii=False) + "\n")

        log.info(
            "  %d/%d  page=%d  sys=%s  ocr=%d new=%d skip=%d",
            i + 1, len(rendered), pg_idx,
            sys_info.get("system_en", "?")[:25],
            len(rows), new_count, skip_count,
        )

    conn.close()
    if log_fh:
        log_fh.close()

    print(f"\nDone: {len(rendered)} pages rendered, {total_new} new parts, {total_skipped} skipped")


if __name__ == "__main__":
    main()
