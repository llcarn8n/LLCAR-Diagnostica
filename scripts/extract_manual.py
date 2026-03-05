#!/usr/bin/env python3
"""
LLCAR Diagnostica — Phase 1: PDF Manual Extraction Pipeline.

Extracts structured manual sections from Li Auto L7/L9 PDF manuals.
Supports text-based PDFs (PyMuPDF) and scanned PDFs (PaddleOCR).

Output: manual-sections-{vehicle}-{lang}.json (schema: manual-sections.schema.json)

Usage:
    python extract_manual.py                  # Process all PDFs
    python extract_manual.py --pdf L9_RU      # Process single PDF
    python extract_manual.py --list           # List available PDFs
"""

import sys
import io
import os
import json
import re
import time
import argparse
from pathlib import Path
from datetime import date

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import fitz  # PyMuPDF

# Try importing PaddleOCR (optional for text PDFs)
try:
    from paddleocr import PaddleOCR
    HAS_PADDLE = True
except ImportError:
    HAS_PADDLE = False
    print("[WARN] PaddleOCR not installed. Scanned PDF support disabled.")
    print("       Install: pip install paddlepaddle-gpu paddleocr")

# ============================================================
# Paths & Config
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "Руководства пользователя Li Auto"
OUTPUT_DIR = BASE_DIR / "knowledge-base"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# PDF registry: key -> (filename, vehicle, language, doc_type)
PDF_REGISTRY = {
    "L9_RU": (
        "Lixiang L9 Руководство пользователя.pdf",
        "Li Auto L9", "ru", "user_manual"
    ),
    "L9_ZH": (
        "Lixiang L9 Owner's Manual.pdf",
        "Li Auto L9", "zh", "user_manual"
    ),
    "L7_ZH": (
        "Lixiang L7 Owner's Manual.pdf",
        "Li Auto L7", "zh", "user_manual"
    ),
    "L9_EN_PARTS": (
        "Li L9英文版.pdf",
        "Li Auto L9", "en", "parts_manual"
    ),
    "L9_ZH_PARTS": (
        "941362155-2022-2023款理想L9零件手册.pdf",
        "Li Auto L9", "zh", "parts_catalog"
    ),
}

# Minimum text length per page to consider it "text-based" (not scanned)
MIN_TEXT_THRESHOLD = 50

# Chapter header patterns per language
CHAPTER_PATTERNS = {
    "ru": re.compile(r'^(\d+-\d+)\.\s*(.+)$', re.MULTILINE),
    "en": re.compile(r'^(?:Chapter\s+)?(\d+-\d+)[\.\s]+(.+)$', re.MULTILINE),
    "zh": re.compile(r'^(\d+-\d+)\.\s*(.+)$', re.MULTILINE),
}

# Warning patterns per language
WARNING_PATTERNS = {
    "ru": {
        "danger": re.compile(r'(?:ОПАСНОСТЬ|DANGER)[!：:\s]*(.+?)(?=\n\n|\n[А-ЯA-Z])', re.DOTALL),
        "warning": re.compile(r'(?:ВНИМАНИЕ|WARNING)[!：:\s]*(.+?)(?=\n\n|\n[А-ЯA-Z])', re.DOTALL),
        "caution": re.compile(r'(?:ОСТОРОЖНО|CAUTION)[!：:\s]*(.+?)(?=\n\n|\n[А-ЯA-Z])', re.DOTALL),
        "note": re.compile(r'(?:ПРИМЕЧАНИЕ|NOTE)[：:\s]*(.+?)(?=\n\n|\n[А-ЯA-Z])', re.DOTALL),
    },
    "en": {
        "danger": re.compile(r'DANGER[!:\s]*(.+?)(?=\n\n|\n[A-Z]{3,})', re.DOTALL),
        "warning": re.compile(r'WARNING[!:\s]*(.+?)(?=\n\n|\n[A-Z]{3,})', re.DOTALL),
        "caution": re.compile(r'CAUTION[!:\s]*(.+?)(?=\n\n|\n[A-Z]{3,})', re.DOTALL),
        "note": re.compile(r'NOTE[:\s]*(.+?)(?=\n\n|\n[A-Z]{3,})', re.DOTALL),
    },
    "zh": {
        "danger": re.compile(r'(?:危险|DANGER)[！!：:\s]*(.+?)(?=\n\n)', re.DOTALL),
        "warning": re.compile(r'(?:警告|WARNING)[！!：:\s]*(.+?)(?=\n\n)', re.DOTALL),
        "caution": re.compile(r'(?:注意|CAUTION)[！!：:\s]*(.+?)(?=\n\n)', re.DOTALL),
        "note": re.compile(r'(?:说明|备注|NOTE)[：:\s]*(.+?)(?=\n\n)', re.DOTALL),
    },
}

# Procedure patterns (numbered steps)
STEP_PATTERN = re.compile(r'^\s*(\d+)[\.）\)]\s+(.+)$', re.MULTILINE)


# ============================================================
# PaddleOCR wrapper
# ============================================================
_paddle_ocr = None

def get_paddle_ocr(lang="ch"):
    """Lazy-initialize PaddleOCR."""
    global _paddle_ocr
    if _paddle_ocr is None:
        if not HAS_PADDLE:
            raise RuntimeError("PaddleOCR not installed")
        print("  Initializing PaddleOCR (first run downloads models ~150MB)...")
        _paddle_ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=True,
            show_log=False,
        )
    return _paddle_ocr


def ocr_page_image(doc, page_idx):
    """Run PaddleOCR on a page rendered as image."""
    ocr = get_paddle_ocr()
    page = doc[page_idx]
    # Render page at 300 DPI for OCR quality
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")

    # PaddleOCR accepts file path or numpy array
    import numpy as np
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    img_np = np.array(img)

    result = ocr.ocr(img_np, cls=True)
    if not result or not result[0]:
        return ""

    # Sort by Y coordinate (top to bottom), then X (left to right)
    lines = []
    for line in result[0]:
        bbox = line[0]
        text = line[1][0]
        confidence = line[1][1]
        if confidence > 0.5:  # Filter low-confidence results
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            x_center = (bbox[0][0] + bbox[2][0]) / 2
            lines.append((y_center, x_center, text))

    # Sort by Y, then X
    lines.sort(key=lambda t: (t[0], t[1]))

    # Group lines by Y proximity (same row)
    if not lines:
        return ""

    rows = []
    current_row = [lines[0]]
    for i in range(1, len(lines)):
        if abs(lines[i][0] - current_row[-1][0]) < 15:  # Same row (within 15px)
            current_row.append(lines[i])
        else:
            current_row.sort(key=lambda t: t[1])  # Sort row by X
            rows.append(" ".join(t[2] for t in current_row))
            current_row = [lines[i]]
    if current_row:
        current_row.sort(key=lambda t: t[1])
        rows.append(" ".join(t[2] for t in current_row))

    return "\n".join(rows)


# ============================================================
# Text extraction
# ============================================================
def extract_page_text(doc, page_idx, lang="en"):
    """Extract text from a single page, using OCR if needed."""
    page = doc[page_idx]
    text = page.get_text().strip()

    if len(text) >= MIN_TEXT_THRESHOLD:
        return text, "pymupdf_text"

    # Page has no/little text — try OCR
    if HAS_PADDLE and lang in ("zh", "ch"):
        try:
            text = ocr_page_image(doc, page_idx)
            if text:
                return text, "paddleocr_scan"
        except Exception as e:
            print(f"    OCR error on page {page_idx + 1}: {e}")

    return text, "pymupdf_text"


def extract_tables(doc, page_idx):
    """Extract tables from a page using PyMuPDF TableFinder."""
    page = doc[page_idx]
    tables = []
    try:
        tab_finder = page.find_tables()
        for i, table in enumerate(tab_finder.tables):
            data = table.extract()
            if not data or len(data) < 2:
                continue

            headers = [str(cell or "").strip() for cell in data[0]]
            rows = []
            for row in data[1:]:
                rows.append([str(cell or "").strip() for cell in row])

            if any(h for h in headers):  # At least one non-empty header
                tables.append({
                    "tableId": f"p{page_idx + 1}_t{i + 1}",
                    "headers": headers,
                    "rows": rows,
                })
    except Exception:
        pass  # TableFinder may fail on some pages

    return tables


# ============================================================
# Section detection
# ============================================================
def detect_chapters_from_bookmarks(doc, target_level=4):
    """Use PDF built-in bookmarks (doc.get_toc()) for section detection.

    Many Chinese PDFs have rich bookmark trees (L7: 3867 entries).
    We use bookmarks at ``target_level`` as chapter boundaries because
    lower levels are too granular and higher levels are category groupings.

    Returns list of dicts with sectionId, title, start_page, level.
    """
    toc = doc.get_toc()  # [(level, title, page), ...]
    if not toc:
        return []

    chapters = []
    idx = 0
    for level, title, page in toc:
        if level != target_level:
            continue
        if page < 1:
            continue  # Skip entries without real page numbers
        title = title.strip()
        if not title or len(title) < 2:
            continue

        idx += 1
        chapters.append({
            "sectionId": f"bk-{idx}",
            "title": title,
            "start_page": page,
            "level": level,
        })

    return chapters


def detect_chapters_from_toc(doc, lang, max_toc_pages=12):
    """Parse Table of Contents from the first N pages (text-based fallback)."""
    toc_text = ""
    for i in range(min(max_toc_pages, len(doc))):
        toc_text += doc[i].get_text() + "\n"

    chapters = []
    seen_ids = set()

    # Parse line by line for chapter headers like " 1-1. Карты в автомобиле"
    for line in toc_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Match chapter header: "1-N. Title" or "1-N.Title" (ZH has no space)
        match = re.match(r'^(\d+-\d+)\.\s*(.+)$', line)
        if match:
            chapter_id = match.group(1)
            title = match.group(2).strip()
            # Clean trailing dots and page numbers
            title = re.sub(r'\s*\.{2,}\s*\d+\s*$', '', title)
            title = re.sub(r'\s+\d+\s*$', '', title)
            if title and len(title) > 1 and chapter_id not in seen_ids:
                chapters.append({
                    "sectionId": chapter_id,
                    "title": title,
                })
                seen_ids.add(chapter_id)
            continue

        # Also parse sub-sections with page refs: "Title ....... 123"
        if chapters:
            sec_match = re.match(r'^(.+?)\s*\.{2,}\s*(\d+)\s*$', line)
            if sec_match:
                title = sec_match.group(1).strip()
                page = int(sec_match.group(2))
                if title and len(title) > 2 and not title.isdigit():
                    chapters[-1].setdefault("subsections", []).append({
                        "title": title,
                        "page": page,
                    })

    # Assign start_page from first subsection
    for ch in chapters:
        subs = ch.get("subsections", [])
        if subs:
            ch["start_page"] = subs[0]["page"]

    return chapters


def detect_chapter_on_page(text, lang):
    """Detect if a page starts with a chapter header."""
    pattern = CHAPTER_PATTERNS.get(lang)
    if not pattern:
        return None

    # Check first 3 lines of the page
    first_lines = text.split('\n')[:5]
    for line in first_lines:
        match = pattern.match(line.strip())
        if match:
            return {
                "sectionId": match.group(1),
                "title": match.group(2).strip(),
            }
    return None


# ============================================================
# Content parsing
# ============================================================
def extract_warnings(text, lang):
    """Extract warning/caution/danger/note blocks from text."""
    warnings = []
    patterns = WARNING_PATTERNS.get(lang, WARNING_PATTERNS["en"])

    for warn_type, pattern in patterns.items():
        for match in pattern.finditer(text):
            warn_text = match.group(1).strip()
            if warn_text and len(warn_text) > 5:
                warnings.append({
                    "type": warn_type,
                    "text": warn_text[:500],  # Limit length
                })

    return warnings


def extract_procedures(text):
    """Extract numbered procedures from text."""
    steps = []
    for match in STEP_PATTERN.finditer(text):
        step_num = int(match.group(1))
        instruction = match.group(2).strip()
        if instruction and len(instruction) > 3:
            steps.append({
                "stepNumber": step_num,
                "instruction": instruction,
            })

    if len(steps) < 2:
        return []  # Not a real procedure

    # Group consecutive steps into procedures
    procedures = []
    current = {"title": "Процедура", "steps": []}
    prev_num = 0

    for step in steps:
        if step["stepNumber"] == 1 and current["steps"]:
            # New procedure starts
            procedures.append(current)
            current = {"title": "Процедура", "steps": []}
        current["steps"].append(step)
        prev_num = step["stepNumber"]

    if current["steps"]:
        procedures.append(current)

    # Assign IDs
    for i, proc in enumerate(procedures):
        proc["procedureId"] = f"proc_{i + 1}"

    return procedures


def chunk_text(text, section_id, max_tokens=800):
    """Split long text into chunks for RAG indexing."""
    # Rough approximation: 1 token ≈ 4 chars for English, ~2 chars for Chinese
    max_chars = max_tokens * 3  # Safe estimate

    if len(text) <= max_chars:
        return []  # No chunking needed

    chunks = []
    paragraphs = text.split('\n\n')
    current_chunk = ""
    chunk_idx = 0

    for para in paragraphs:
        if len(current_chunk) + len(para) > max_chars and current_chunk:
            chunks.append({
                "chunkId": f"{section_id}_c{chunk_idx}",
                "text": current_chunk.strip(),
            })
            chunk_idx += 1
            current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append({
            "chunkId": f"{section_id}_c{chunk_idx}",
            "text": current_chunk.strip(),
        })

    return chunks


# ============================================================
# Main extraction
# ============================================================
def extract_manual(pdf_key):
    """Extract structured sections from a PDF manual."""
    if pdf_key not in PDF_REGISTRY:
        print(f"ERROR: Unknown PDF key '{pdf_key}'. Available: {list(PDF_REGISTRY.keys())}")
        return None

    filename, vehicle, lang, doc_type = PDF_REGISTRY[pdf_key]
    pdf_path = PDF_DIR / filename

    if not pdf_path.exists():
        print(f"SKIP: {pdf_path} not found")
        return None

    print(f"\n{'=' * 60}")
    print(f"Extracting: {filename}")
    print(f"Vehicle: {vehicle}, Language: {lang}, Type: {doc_type}")
    print(f"{'=' * 60}")

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    print(f"  Total pages: {total_pages}")
    start_time = time.time()

    # Step 1: Detect chapters — prefer PDF bookmarks, fallback to text TOC
    bookmark_chapters = detect_chapters_from_bookmarks(doc, target_level=4)
    if len(bookmark_chapters) >= 10:
        print(f"  PDF bookmarks (L4): {len(bookmark_chapters)} chapters — using bookmarks")
        toc_chapters = bookmark_chapters
        use_bookmarks = True
    else:
        toc_chapters = detect_chapters_from_toc(doc, lang)
        print(f"  TOC chapters found: {len(toc_chapters)}")
        use_bookmarks = False

    # Step 2: Page-by-page extraction
    pages_data = []
    extraction_method = "pymupdf_text"
    ocr_pages = 0
    text_pages = 0

    for i in range(total_pages):
        text, method = extract_page_text(doc, i, lang)
        tables = extract_tables(doc, i)
        chapter = detect_chapter_on_page(text, lang)

        if method == "paddleocr_scan":
            ocr_pages += 1
        else:
            text_pages += 1

        pages_data.append({
            "page": i + 1,
            "text": text,
            "tables": tables,
            "chapter_header": chapter,
            "method": method,
        })

        # Progress reporting
        if (i + 1) % 50 == 0 or i == total_pages - 1:
            elapsed = time.time() - start_time
            pps = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"  ...page {i + 1}/{total_pages} ({pps:.1f} pages/sec, OCR: {ocr_pages})")

    if ocr_pages > text_pages:
        extraction_method = "paddleocr_scan"

    # Step 3: Build sections from chapters
    sections = build_sections(pages_data, toc_chapters, lang)
    print(f"  Sections built: {len(sections)}")

    # Step 4: Assemble output
    # Determine output filename
    vehicle_prefix = "l9" if "L9" in vehicle else "l7"
    if doc_type == "parts_catalog":
        out_name = f"manual-sections-{vehicle_prefix}-{lang}-parts.json"
        doc_id = f"{vehicle_prefix}_parts_catalog_{lang}"
        title_prefix = "Каталог запчастей" if lang == "zh" else "Parts Catalog"
    elif doc_type == "parts_manual":
        out_name = f"manual-sections-{vehicle_prefix}-{lang}-parts.json"
        doc_id = f"{vehicle_prefix}_parts_manual_{lang}"
        title_prefix = "Parts Manual"
    else:
        out_name = f"manual-sections-{vehicle_prefix}-{lang}.json"
        doc_id = f"{vehicle_prefix}_user_manual_{lang}"
        title_prefix = {
            "ru": "Руководство пользователя",
            "en": "Owner's Manual",
            "zh": "用户手册",
        }.get(lang, "Manual")

    output = {
        "documentId": doc_id,
        "title": f"{title_prefix} {vehicle}",
        "vehicle": vehicle,
        "language": lang,
        "source": {
            "filename": filename,
            "total_pages": total_pages,
            "extraction_method": extraction_method,
            "extraction_date": str(date.today()),
            "text_pages": text_pages,
            "ocr_pages": ocr_pages,
        },
        "sections": sections,
    }

    # Save
    out_path = OUTPUT_DIR / out_name
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    doc.close()

    print(f"\n  Saved: {out_path}")
    print(f"  Sections: {len(sections)}")
    print(f"  Time: {elapsed:.1f}s ({total_pages / elapsed:.1f} pages/sec)")

    return output


def build_sections(pages_data, toc_chapters, lang):
    """Build structured sections from page data and TOC."""
    sections = []

    # Fast path: bookmark-based chapters already have start_page
    has_start_pages = all("start_page" in ch for ch in toc_chapters) if toc_chapters else False
    if has_start_pages and len(toc_chapters) >= 10:
        print(f"  Building {len(toc_chapters)} sections from bookmark page ranges")
        for i, ch in enumerate(toc_chapters):
            start_page = ch["start_page"]
            # End page = next chapter's start_page - 1 (or last page)
            end_page = (toc_chapters[i + 1]["start_page"] - 1
                        if i + 1 < len(toc_chapters)
                        else pages_data[-1]["page"])
            if end_page < start_page:
                end_page = start_page  # single-page section

            chapter_text = ""
            chapter_tables = []
            for page in pages_data:
                if start_page <= page["page"] <= end_page:
                    chapter_text += page["text"] + "\n\n"
                    chapter_tables.extend(page["tables"])

            chapter_text = chapter_text.strip()
            warnings = extract_warnings(chapter_text, lang)
            procedures = extract_procedures(chapter_text)
            chunks = chunk_text(chapter_text, ch["sectionId"])

            section = {
                "sectionId": ch["sectionId"],
                "title": ch["title"],
                "level": ch.get("level", 1),
                "pageStart": start_page,
                "pageEnd": end_page,
                "content": chapter_text[:50000],
            }
            if chunks:
                section["contentChunks"] = chunks
            if warnings:
                section["warnings"] = warnings
            if procedures:
                section["procedures"] = procedures
            if chapter_tables:
                section["tables"] = chapter_tables

            sections.append(section)

        # Remove empty sections (no text content)
        sections = [s for s in sections if s["content"].strip()]
        print(f"  Non-empty sections: {len(sections)}")
        return sections

    # Build chapter boundaries from inline page headers
    chapter_starts = {}
    for page in pages_data:
        ch = page.get("chapter_header")
        if ch:
            chapter_starts[page["page"]] = ch

    print(f"  Inline chapter headers detected: {len(chapter_starts)}")

    # Strategy: prefer inline detection if it found enough chapters.
    # If TOC found significantly more, match TOC chapters to pages by sectionId.
    if toc_chapters and len(toc_chapters) > len(chapter_starts) * 2:
        print(f"  Using TOC-based section matching (TOC:{len(toc_chapters)} >> inline:{len(chapter_starts)})")

        # Determine TOC page range to skip during regex matching
        toc_end_page = 12  # Default: skip first 12 pages (TOC area)
        if toc_chapters:
            first_start = None
            for ch in toc_chapters:
                if "start_page" in ch:
                    first_start = ch["start_page"]
                    break
            if first_start and first_start > 5:
                toc_end_page = first_start - 1

        # Build a map: sectionId -> page number
        # Priority 1: TOC start_page from subsection page references (skip if 0)
        id_to_page = {}
        for ch in toc_chapters:
            sid = ch["sectionId"]
            if "start_page" in ch and ch["start_page"] > 0:
                id_to_page[sid] = ch["start_page"]

        # Priority 2: inline chapter detection on actual pages
        for pg, ch in chapter_starts.items():
            sid = ch["sectionId"]
            if pg > toc_end_page:  # Only use matches AFTER TOC
                id_to_page[sid] = pg  # Override TOC hint with actual detection

        # Priority 3: regex search on content pages (skip TOC)
        for ch in toc_chapters:
            sid = ch["sectionId"]
            if sid in id_to_page:
                continue
            # Search all pages for this chapter's sectionId in first few lines
            for page in pages_data:
                if page["page"] <= toc_end_page:
                    continue  # Skip TOC pages
                first_lines = page["text"][:500]
                if re.search(rf'(?:^|\n)\s*{re.escape(sid)}[\.\s]', first_lines):
                    id_to_page[sid] = page["page"]
                    break

        print(f"  Matched {len(id_to_page)}/{len(toc_chapters)} chapters to pages")

        # If match rate is too low, abandon TOC and use fallback
        if len(id_to_page) < len(toc_chapters) * 0.3:
            print(f"  [WARN] Low match rate. Falling back to page-range sections.")
            toc_chapters = []  # Force fallback below

        # Build sections from TOC with matched pages
        for i, ch in enumerate(toc_chapters):
            sid = ch["sectionId"]
            start_page = id_to_page.get(sid)

            # Find end page: next chapter's start page - 1
            end_page = None
            for j in range(i + 1, len(toc_chapters)):
                next_sid = toc_chapters[j]["sectionId"]
                if next_sid in id_to_page:
                    end_page = id_to_page[next_sid] - 1
                    break
            if end_page is None and start_page:
                end_page = pages_data[-1]["page"]

            if not start_page or (end_page is not None and start_page > end_page):
                # Chapter not matched or has inverted range (header-only section)
                sections.append({
                    "sectionId": sid,
                    "title": ch["title"],
                    "level": 1,
                    "content": "",
                })
                continue

            # Collect text and tables for this chapter's page range
            chapter_text = ""
            chapter_tables = []
            for page in pages_data:
                if start_page <= page["page"] <= end_page:
                    chapter_text += page["text"] + "\n\n"
                    chapter_tables.extend(page["tables"])

            chapter_text = chapter_text.strip()
            warnings = extract_warnings(chapter_text, lang)
            procedures = extract_procedures(chapter_text)
            chunks = chunk_text(chapter_text, sid)

            section = {
                "sectionId": sid,
                "title": ch["title"],
                "level": 1,
                "pageStart": start_page,
                "pageEnd": end_page,
                "content": chapter_text[:50000],
            }
            if chunks:
                section["contentChunks"] = chunks
            if warnings:
                section["warnings"] = warnings
            if procedures:
                section["procedures"] = procedures
            if chapter_tables:
                section["tables"] = chapter_tables

            sections.append(section)

        if sections:
            return sections
        # else: TOC was emptied due to low match rate, fall through

    # Fallback: use inline chapter boundaries
    sorted_pages = sorted(chapter_starts.keys())

    for idx, start_page in enumerate(sorted_pages):
        ch = chapter_starts[start_page]
        end_page = sorted_pages[idx + 1] - 1 if idx + 1 < len(sorted_pages) else pages_data[-1]["page"]

        chapter_text = ""
        chapter_tables = []
        for page in pages_data:
            if start_page <= page["page"] <= end_page:
                chapter_text += page["text"] + "\n\n"
                chapter_tables.extend(page["tables"])

        chapter_text = chapter_text.strip()
        warnings = extract_warnings(chapter_text, lang)
        procedures = extract_procedures(chapter_text)
        chunks = chunk_text(chapter_text, ch["sectionId"])

        section = {
            "sectionId": ch["sectionId"],
            "title": ch["title"],
            "level": 1,
            "pageStart": start_page,
            "pageEnd": end_page,
            "content": chapter_text[:50000],
        }
        if chunks:
            section["contentChunks"] = chunks
        if warnings:
            section["warnings"] = warnings
        if procedures:
            section["procedures"] = procedures
        if chapter_tables:
            section["tables"] = chapter_tables

        sections.append(section)

    # If no chapters found at all, create one big section per N pages
    if not sections:
        print("  [WARN] No chapters detected. Creating page-range sections...")
        pages_per_section = 20
        for start in range(0, len(pages_data), pages_per_section):
            end = min(start + pages_per_section, len(pages_data))
            text = "\n\n".join(p["text"] for p in pages_data[start:end])
            tables = []
            for p in pages_data[start:end]:
                tables.extend(p["tables"])

            section_id = f"pages_{start + 1}_{end}"
            sections.append({
                "sectionId": section_id,
                "title": f"Pages {start + 1}-{end}",
                "level": 1,
                "pageStart": start + 1,
                "pageEnd": end,
                "content": text[:50000],
                "tables": tables if tables else [],
            })

    return sections


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="LLCAR Diagnostica: Extract manual sections from PDF"
    )
    parser.add_argument(
        "--pdf", type=str, default=None,
        help=f"PDF key to process. Available: {', '.join(PDF_REGISTRY.keys())}"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available PDFs and exit"
    )
    parser.add_argument(
        "--skip-ocr", action="store_true",
        help="Skip PaddleOCR even for scanned pages"
    )
    args = parser.parse_args()

    if args.list:
        print("Available PDFs:")
        for key, (filename, vehicle, lang, doc_type) in PDF_REGISTRY.items():
            path = PDF_DIR / filename
            exists = "OK" if path.exists() else "NOT FOUND"
            size = f"{path.stat().st_size / 1024 / 1024:.1f}MB" if path.exists() else "-"
            print(f"  {key:15s} {vehicle:15s} {lang:3s} {doc_type:15s} {size:>8s}  [{exists}]")
        return

    if args.skip_ocr:
        global HAS_PADDLE
        HAS_PADDLE = False
        print("[INFO] PaddleOCR disabled via --skip-ocr")

    if args.pdf:
        # Process single PDF
        extract_manual(args.pdf)
    else:
        # Process all PDFs
        print(f"PDF directory: {PDF_DIR}")
        print(f"Output directory: {OUTPUT_DIR}")

        for key in PDF_REGISTRY:
            try:
                extract_manual(key)
            except Exception as e:
                print(f"  ERROR processing {key}: {e}")
                import traceback
                traceback.print_exc()

    # Summary
    print(f"\n{'=' * 60}")
    print("Extraction complete!")
    for f in sorted(OUTPUT_DIR.glob("manual-sections-*.json")):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name} ({size_kb:.1f} KB)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
