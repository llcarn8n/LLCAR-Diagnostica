#!/usr/bin/env python3
"""
LLCAR Diagnostica — Phase 1: Configuration PDF Extraction.

Extracts vehicle specifications from Li Auto L7/L9 Configuration PDFs.
Uses PyMuPDF TableFinder for table extraction + PaddleOCR for scanned pages.

Output: config-data-{vehicle}.json (schema: config-data.schema.json)

Usage:
    python extract_config.py              # Process all config PDFs
    python extract_config.py --pdf L9     # Process single PDF
"""

import sys
import io
import json
import re
import argparse
from pathlib import Path
from datetime import date

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import fitz  # PyMuPDF

# Try PaddleOCR for scanned Chinese pages
try:
    from paddleocr import PaddleOCR
    HAS_PADDLE = True
except ImportError:
    HAS_PADDLE = False

# ============================================================
# Paths
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "Руководства пользователя Li Auto"
OUTPUT_DIR = BASE_DIR / "knowledge-base"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PDFS = {
    "L9": (
        "240322-Li-L9-Configuration.pdf",
        "Li Auto L9", "en"
    ),
    "L7": (
        "857694655-241015-L7参数配置中文.pdf",
        "Li Auto L7", "zh"
    ),
}


# ============================================================
# Table extraction
# ============================================================
def extract_all_tables(pdf_path):
    """Extract all tables from a PDF using PyMuPDF TableFinder."""
    doc = fitz.open(str(pdf_path))
    all_tables = []

    for i in range(len(doc)):
        page = doc[i]

        # Try TableFinder
        try:
            tab_finder = page.find_tables()
            for table in tab_finder.tables:
                data = table.extract()
                if data and len(data) >= 1:
                    all_tables.append({
                        "page": i + 1,
                        "data": data,
                    })
        except Exception:
            pass

    doc.close()
    return all_tables


def extract_text_all_pages(pdf_path):
    """Extract text from all pages."""
    doc = fitz.open(str(pdf_path))
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text


# ============================================================
# Spec parsing helpers
# ============================================================
def parse_dimension(text, pattern, default=None):
    """Extract a numeric value from text using pattern."""
    match = re.search(pattern, text)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, IndexError):
            pass
    return default


def parse_float(text, pattern, default=None):
    """Extract a float value from text using pattern."""
    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, IndexError):
            pass
    return default


def tables_to_dict(tables):
    """Convert extracted tables into key-value pairs."""
    kv_pairs = {}
    for table_info in tables:
        for row in table_info["data"]:
            if len(row) >= 2:
                key = str(row[0] or "").strip()
                val = str(row[1] or "").strip()
                if key and val:
                    kv_pairs[key] = val
            if len(row) >= 4:
                # Some tables have 2 key-value pairs per row
                key2 = str(row[2] or "").strip()
                val2 = str(row[3] or "").strip()
                if key2 and val2:
                    kv_pairs[key2] = val2
    return kv_pairs


# ============================================================
# Config extraction
# ============================================================
def extract_config(pdf_key):
    """Extract configuration specs from a PDF."""
    if pdf_key not in CONFIG_PDFS:
        print(f"ERROR: Unknown key '{pdf_key}'. Available: {list(CONFIG_PDFS.keys())}")
        return None

    filename, vehicle, lang = CONFIG_PDFS[pdf_key]
    pdf_path = PDF_DIR / filename

    if not pdf_path.exists():
        print(f"SKIP: {pdf_path} not found")
        return None

    print(f"\n{'=' * 60}")
    print(f"Extracting config: {filename}")
    print(f"Vehicle: {vehicle}, Language: {lang}")
    print(f"{'=' * 60}")

    # Extract tables and text
    tables = extract_all_tables(pdf_path)
    full_text = extract_text_all_pages(pdf_path)
    kv = tables_to_dict(tables)

    print(f"  Tables found: {len(tables)}")
    print(f"  Key-value pairs: {len(kv)}")
    print(f"  Text length: {len(full_text)} chars")

    # Build config from extracted data
    vehicle_prefix = "l9" if "L9" in vehicle else "l7"
    out_name = f"{vehicle_prefix}-config.json"

    # Check if existing config exists (from previous hardcoded extraction)
    existing_path = OUTPUT_DIR / out_name
    existing_data = None
    if existing_path.exists():
        with open(existing_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        print(f"  Existing config loaded: {out_name}")

    # Build output — merge extracted tables into existing config
    config = existing_data or {
        "vehicle": vehicle,
        "language": lang,
    }

    # Update source metadata
    config["source"] = filename
    config["extraction_date"] = str(date.today())
    config["extraction_method"] = "pymupdf_tables"

    # Add raw extracted tables for verification
    config["_raw_tables"] = {
        "total": len(tables),
        "key_value_pairs": kv,
    }

    # Save
    with open(existing_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"  Saved: {existing_path}")
    return config


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="LLCAR Diagnostica: Extract config specs from PDF"
    )
    parser.add_argument(
        "--pdf", type=str, default=None,
        help=f"Config PDF to process. Available: {', '.join(CONFIG_PDFS.keys())}"
    )
    args = parser.parse_args()

    if args.pdf:
        extract_config(args.pdf)
    else:
        for key in CONFIG_PDFS:
            try:
                extract_config(key)
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
