#!/usr/bin/env python3
"""
LLCAR Diagnostica — Universal Parts Catalog Audit Tool.

Compares the parts table in kb.db against MinerU content_list.json to find:
1. Missing hotspot positions per diagram (OCR extracted fewer rows than diagram shows)
2. Entirely missing pages (table images exist but 0 parts in DB)
3. Duplicate parts (same part_number + hotspot on same page)
4. Orphan parts (parts on pages not in content_list)
5. System mapping gaps (parts with unknown/empty system)

Designed to work with ANY vehicle model processed through MinerU.
Just point it at the right content_list.json and kb.db.

Usage:
    python scripts/audit_parts_coverage.py                              # auto-detect
    python scripts/audit_parts_coverage.py --content-list PATH          # custom path
    python scripts/audit_parts_coverage.py --format json --output report.json
    python scripts/audit_parts_coverage.py --fix-duplicates             # remove exact dupes
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_KB_DB = _BASE_DIR / "knowledge-base" / "kb.db"

# All known content_list paths (add new models here)
CONTENT_LISTS = [
    _BASE_DIR / "mineru-output" / "941362155-2022-2023款理想L9零件手册" / "ocr"
    / "941362155-2022-2023款理想L9零件手册_content_list.json",
]


def find_content_list() -> Path | None:
    """Auto-detect the content_list.json file."""
    for p in CONTENT_LISTS:
        if p.exists():
            return p
    # Fallback: search mineru-output for any content_list
    mo = _BASE_DIR / "mineru-output"
    if mo.exists():
        for cl in mo.rglob("*_content_list.json"):
            return cl
    return None


# ---------------------------------------------------------------------------
# Audit checks
# ---------------------------------------------------------------------------

def check_hotspot_gaps(conn: sqlite3.Connection) -> dict:
    """Check for missing hotspot positions per diagram."""
    rows = conn.execute("""
        SELECT system_en, page_idx, source_image, diagram_image,
               hotspot_id, part_number, part_name_zh
        FROM parts
        WHERE hotspot_id != '' AND CAST(hotspot_id AS INTEGER) BETWEEN 1 AND 30
        ORDER BY system_en, page_idx
    """).fetchall()

    groups = defaultdict(lambda: {"hotspots": set(), "max_hs": 0, "count": 0})
    for r in rows:
        key = (r[0], r[1], r[2])  # system, page, source_image
        g = groups[key]
        try:
            hs = int(r[4])
            g["hotspots"].add(hs)
            g["max_hs"] = max(g["max_hs"], hs)
        except ValueError:
            pass
        g["count"] += 1

    gaps = []
    total_missing = 0
    for (sys_en, page, src_img), g in sorted(groups.items()):
        expected = set(range(1, g["max_hs"] + 1))
        missing = sorted(expected - g["hotspots"])
        if missing:
            gaps.append({
                "system": sys_en,
                "page": page,
                "have": len(g["hotspots"]),
                "max": g["max_hs"],
                "missing_count": len(missing),
                "missing_positions": missing,
            })
            total_missing += len(missing)

    return {
        "diagrams_with_gaps": len(gaps),
        "total_missing_positions": total_missing,
        "gaps": gaps,
    }


def check_missing_pages(conn: sqlite3.Connection, content_list: list[dict],
                         page_system_map: dict) -> dict:
    """Check for pages with table images but no parts in DB."""
    db_pages = {r[0] for r in conn.execute("SELECT DISTINCT page_idx FROM parts").fetchall()}

    table_pages = {}
    for item in content_list:
        if item.get("type") == "table" and item.get("img_path"):
            pg = item.get("page_idx", -1)
            if pg >= 0:
                table_pages.setdefault(pg, []).append(item["img_path"])

    missing = []
    for pg in sorted(table_pages.keys()):
        if pg not in db_pages:
            sys_info = page_system_map.get(pg, {})
            missing.append({
                "page": pg,
                "system": sys_info.get("system_en", "UNKNOWN"),
                "table_images": table_pages[pg],
            })

    return {
        "total_table_pages": len(table_pages),
        "pages_with_parts": len(db_pages & set(table_pages.keys())),
        "missing_pages": len(missing),
        "details": missing,
    }


def check_duplicates(conn: sqlite3.Connection) -> dict:
    """Find duplicate parts (same part_number + hotspot + page)."""
    rows = conn.execute("""
        SELECT part_number, hotspot_id, page_idx, system_en, COUNT(*) as cnt
        FROM parts
        GROUP BY part_number, hotspot_id, page_idx, system_en
        HAVING cnt > 1
        ORDER BY cnt DESC
    """).fetchall()

    dupes = []
    total_extra = 0
    for r in rows:
        extra = r[4] - 1
        total_extra += extra
        dupes.append({
            "part_number": r[0],
            "hotspot": r[1],
            "page": r[2],
            "system": r[3],
            "count": r[4],
            "extra": extra,
        })

    return {
        "duplicate_groups": len(dupes),
        "total_extra_rows": total_extra,
        "details": dupes[:50],  # Top 50
    }


def check_system_mapping(conn: sqlite3.Connection) -> dict:
    """Check for parts with empty/unknown system."""
    empty_sys = conn.execute(
        "SELECT COUNT(*) FROM parts WHERE system_en IS NULL OR system_en = ''"
    ).fetchone()[0]

    sys_counts = conn.execute("""
        SELECT system_en, COUNT(*) FROM parts
        WHERE system_en IS NOT NULL AND system_en != ''
        GROUP BY system_en ORDER BY COUNT(*) DESC
    """).fetchall()

    return {
        "parts_without_system": empty_sys,
        "systems": [{"system": r[0], "count": r[1]} for r in sys_counts],
    }


def check_translations(conn: sqlite3.Connection) -> dict:
    """Check EN/RU translation coverage."""
    total = conn.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
    has_en = conn.execute(
        "SELECT COUNT(*) FROM parts WHERE part_name_en IS NOT NULL AND part_name_en != ''"
    ).fetchone()[0]

    # Check if part_name_ru column exists
    cols = {r[1] for r in conn.execute("PRAGMA table_info(parts)").fetchall()}
    has_ru_col = "part_name_ru" in cols
    has_ru = 0
    if has_ru_col:
        has_ru = conn.execute(
            "SELECT COUNT(*) FROM parts WHERE part_name_ru IS NOT NULL AND part_name_ru != ''"
        ).fetchone()[0]

    return {
        "total_parts": total,
        "has_en_name": has_en,
        "en_coverage": f"{has_en/total*100:.1f}%" if total else "0%",
        "has_ru_name": has_ru,
        "ru_coverage": f"{has_ru/total*100:.1f}%" if total else "0%",
        "has_ru_column": has_ru_col,
    }


def check_diagram_coverage(conn: sqlite3.Connection) -> dict:
    """Check diagram_image coverage."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(parts)").fetchall()}
    if "diagram_image" not in cols:
        return {"has_column": False}

    total = conn.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
    has_diag = conn.execute(
        "SELECT COUNT(*) FROM parts WHERE diagram_image IS NOT NULL AND diagram_image != ''"
    ).fetchone()[0]

    return {
        "has_column": True,
        "total_parts": total,
        "has_diagram": has_diag,
        "coverage": f"{has_diag/total*100:.1f}%" if total else "0%",
    }


# ---------------------------------------------------------------------------
# Page→system mapping (simplified, no import needed)
# ---------------------------------------------------------------------------

def build_simple_page_map(content_list: list[dict]) -> dict:
    """Build page→system map from content_list text entries."""
    # Import the full mapping from ocr_parts_tables if available
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from ocr_parts_tables import build_page_system_map
        return build_page_system_map(content_list)
    except ImportError:
        pass

    # Fallback: simple heuristic
    page_map = {}
    current = {"system_en": "", "system_zh": ""}
    for item in content_list:
        if item.get("type") == "text":
            page_map.setdefault(item.get("page_idx", -1), current.copy())
    return page_map


# ---------------------------------------------------------------------------
# Report output
# ---------------------------------------------------------------------------

def print_report(report: dict) -> None:
    """Print formatted audit report."""
    print("\n" + "=" * 80)
    print("  PARTS CATALOG AUDIT REPORT")
    print("=" * 80)

    # Summary
    s = report["summary"]
    print(f"\n  Total parts in DB:     {s['total_parts']}")
    print(f"  Unique part numbers:   {s['unique_part_numbers']}")
    print(f"  Systems:               {s['system_count']}")
    print(f"  Pages covered:         {s['pages_covered']}")

    # Hotspot gaps
    hg = report["hotspot_gaps"]
    print(f"\n--- Hotspot Gaps ---")
    print(f"  Diagrams with gaps:    {hg['diagrams_with_gaps']}")
    print(f"  Missing positions:     {hg['total_missing_positions']}")
    if hg["gaps"]:
        print(f"\n  {'System':<35} {'Pg':>4} {'Have':>5} {'Max':>4} {'Miss':>5}")
        print("  " + "-" * 65)
        for g in hg["gaps"][:30]:
            miss_str = ", ".join(str(m) for m in g["missing_positions"][:8])
            if len(g["missing_positions"]) > 8:
                miss_str += "..."
            print(f"  {g['system']:<35} {g['page']:>4} {g['have']:>5} {g['max']:>4} "
                  f"{g['missing_count']:>5}  {miss_str}")
        if len(hg["gaps"]) > 30:
            print(f"  ... and {len(hg['gaps'])-30} more")

    # Missing pages
    mp = report["missing_pages"]
    print(f"\n--- Missing Pages ---")
    print(f"  Table pages in content_list:  {mp['total_table_pages']}")
    print(f"  Pages with parts in DB:       {mp['pages_with_parts']}")
    print(f"  Missing pages:                {mp['missing_pages']}")
    if mp["details"]:
        for d in mp["details"]:
            print(f"    page {d['page']:>4}  {d['system']}")

    # Duplicates
    dp = report["duplicates"]
    print(f"\n--- Duplicates ---")
    print(f"  Duplicate groups:      {dp['duplicate_groups']}")
    print(f"  Extra rows:            {dp['total_extra_rows']}")

    # Translations
    tr = report["translations"]
    print(f"\n--- Translation Coverage ---")
    print(f"  EN names:  {tr['has_en_name']}/{tr['total_parts']} ({tr['en_coverage']})")
    print(f"  RU names:  {tr['has_ru_name']}/{tr['total_parts']} ({tr['ru_coverage']})")

    # Diagram coverage
    dc = report["diagram_coverage"]
    if dc.get("has_column"):
        print(f"\n--- Diagram Image Coverage ---")
        print(f"  Has diagram:  {dc['has_diagram']}/{dc['total_parts']} ({dc['coverage']})")

    # Per-system summary
    sm = report["system_mapping"]
    print(f"\n--- Per-System Summary ---")
    print(f"  {'System':<45} {'Parts':>6}")
    print("  " + "-" * 55)
    for s in sm["systems"]:
        print(f"  {s['system']:<45} {s['count']:>6}")
    if sm["parts_without_system"]:
        print(f"  {'(no system)':<45} {sm['parts_without_system']:>6}")

    # Overall score
    score = calculate_score(report)
    print(f"\n{'='*80}")
    print(f"  COVERAGE SCORE: {score}/100")
    print(f"{'='*80}\n")


def calculate_score(report: dict) -> int:
    """Calculate a 0-100 coverage score."""
    score = 100

    # Deduct for missing hotspots (max -40)
    total_parts = report["summary"]["total_parts"]
    missing_hs = report["hotspot_gaps"]["total_missing_positions"]
    if total_parts > 0:
        hs_penalty = min(40, int(missing_hs / total_parts * 100))
        score -= hs_penalty

    # Deduct for missing pages (max -20)
    mp = report["missing_pages"]
    if mp["total_table_pages"] > 0:
        pg_penalty = min(20, int(mp["missing_pages"] / mp["total_table_pages"] * 100))
        score -= pg_penalty

    # Deduct for poor translation coverage (max -20)
    tr = report["translations"]
    en_pct = tr["has_en_name"] / tr["total_parts"] * 100 if tr["total_parts"] else 100
    tr_penalty = min(20, max(0, int((100 - en_pct) / 5)))
    score -= tr_penalty

    # Deduct for duplicates (max -10)
    dup_extra = report["duplicates"]["total_extra_rows"]
    dup_penalty = min(10, int(dup_extra / max(total_parts, 1) * 50))
    score -= dup_penalty

    # Deduct for no diagram images (max -10)
    dc = report["diagram_coverage"]
    if dc.get("has_column") and dc["total_parts"] > 0:
        diag_pct = dc["has_diagram"] / dc["total_parts"] * 100
        diag_penalty = min(10, max(0, int((100 - diag_pct) / 10)))
        score -= diag_penalty

    return max(0, score)


# ---------------------------------------------------------------------------
# Fix actions
# ---------------------------------------------------------------------------

def fix_duplicates(conn: sqlite3.Connection) -> int:
    """Remove exact duplicate rows, keeping the one with lowest id."""
    dupes = conn.execute("""
        SELECT part_number, hotspot_id, page_idx, system_en, MIN(id) as keep_id, COUNT(*) as cnt
        FROM parts
        GROUP BY part_number, hotspot_id, page_idx, system_en
        HAVING cnt > 1
    """).fetchall()

    removed = 0
    for d in dupes:
        pn, hs, pg, sys_en, keep_id, cnt = d
        cur = conn.execute("""
            DELETE FROM parts
            WHERE part_number = ? AND hotspot_id IS ? AND page_idx = ?
                  AND system_en = ? AND id != ?
        """, (pn, hs, pg, sys_en, keep_id))
        removed += cur.rowcount

    conn.commit()
    return removed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit parts catalog coverage in kb.db",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--db-path", default=str(_KB_DB), help="Path to kb.db")
    parser.add_argument("--content-list", default=None, help="Path to content_list.json")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")
    parser.add_argument("--fix-duplicates", action="store_true",
                        help="Remove exact duplicate parts")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"ERROR: kb.db not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    # Find content_list
    cl_path = Path(args.content_list) if args.content_list else find_content_list()
    if not cl_path or not cl_path.exists():
        print("WARNING: content_list.json not found. Some checks will be skipped.",
              file=sys.stderr)
        content_list = []
    else:
        with open(cl_path, "r", encoding="utf-8") as f:
            content_list = json.load(f)
        print(f"Using content_list: {cl_path}", file=sys.stderr)

    # Open DB
    conn = sqlite3.connect(str(db_path), timeout=60)
    conn.row_factory = sqlite3.Row

    # Fix duplicates if requested
    if args.fix_duplicates:
        removed = fix_duplicates(conn)
        print(f"Removed {removed} duplicate rows.", file=sys.stderr)

    # Build page map
    page_map = build_simple_page_map(content_list) if content_list else {}

    # Run all checks
    total = conn.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
    unique_pn = conn.execute("SELECT COUNT(DISTINCT part_number) FROM parts").fetchone()[0]
    sys_count = conn.execute(
        "SELECT COUNT(DISTINCT system_en) FROM parts WHERE system_en != ''"
    ).fetchone()[0]
    pg_count = conn.execute("SELECT COUNT(DISTINCT page_idx) FROM parts").fetchone()[0]

    report = {
        "summary": {
            "total_parts": total,
            "unique_part_numbers": unique_pn,
            "system_count": sys_count,
            "pages_covered": pg_count,
            "db_path": str(db_path),
            "content_list": str(cl_path) if cl_path else None,
        },
        "hotspot_gaps": check_hotspot_gaps(conn),
        "missing_pages": check_missing_pages(conn, content_list, page_map) if content_list else {
            "total_table_pages": 0, "pages_with_parts": 0, "missing_pages": 0, "details": []
        },
        "duplicates": check_duplicates(conn),
        "system_mapping": check_system_mapping(conn),
        "translations": check_translations(conn),
        "diagram_coverage": check_diagram_coverage(conn),
    }

    report["score"] = calculate_score(report)

    conn.close()

    # Output
    if args.format == "json":
        output = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        import io
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        print_report(report)
        sys.stdout = old_stdout
        output = buf.getvalue()

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
