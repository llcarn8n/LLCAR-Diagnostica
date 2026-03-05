#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Quality Audit for sections-*.json and manual-sections-*.json files.
Checks: count, empty sections, language contamination, OCR artifacts,
average length, meaningful content, duplicates, structure quality.
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ── Unicode ranges ──────────────────────────────────────────────────────────
RE_CHINESE   = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df'
                          r'\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf'
                          r'\uf900-\ufaff\u3000-\u303f\uff00-\uffef]')
RE_CYRILLIC  = re.compile(r'[\u0400-\u04ff]')
RE_LATIN     = re.compile(r'[A-Za-z]')
RE_ARABIC    = re.compile(r'[\u0600-\u06ff]')

# ── OCR / TOC artifact patterns ─────────────────────────────────────────────
TOC_DOTS    = re.compile(r'\.{4,}')          # ....... (TOC dots)
TOC_DOTDOT  = re.compile(r'(\.\.\s?){3,}')   # .. .. .. ..
REPEATED_CH = re.compile(r'(.)\1{5,}')       # aaaaaaa / 。。。。。
GARBLED     = re.compile(r'[^\x00-\xff\u0400-\u04ff\u4e00-\u9fff\u3000-\u303f'
                          r'\uff00-\uffef\u0600-\u06ff\s\w\-\_\.\,\!\?\;\:\(\)\[\]\{\}\/\\\"\''
                          r'\+\=\*\&\^\%\$\#\@\~\`\|<>«»""''„\u2019\u2018\u201c\u201d]{3,}')
PAGE_NUM_TITLE = re.compile(r'^\s*(\d{1,4})\s*$')  # title is just a page number
TOC_LINE    = re.compile(r'\d{1,4}\s*$')            # line ending with page num

EMPTY_THRESHOLD       = 50
NEAR_EMPTY_THRESHOLD  = 50
MEANINGFUL_THRESHOLD  = 200
LANG_CONTAMINATION_RATIO = 0.15   # 15% foreign chars → contaminated

FILES = [
    "knowledge-base/sections-l9-ru.json",
    "knowledge-base/sections-l7-ru.json",
    "knowledge-base/sections-l7-zh.json",
    "knowledge-base/sections-l7-zh-full.json",
    "knowledge-base/sections-l9-zh.json",
    "knowledge-base/sections-l9-zh-full.json",
    "knowledge-base/sections-l9-parts-zh.json",
    "knowledge-base/web-sections-l7-zh.json",
    "knowledge-base/manual-sections-l7-ru.json",
    "knowledge-base/manual-sections-l7-zh.json",
    "knowledge-base/manual-sections-l9-ru.json",
    "knowledge-base/manual-sections-l9-zh.json",
    "knowledge-base/manual-sections-l9-en-parts.json",
    "knowledge-base/manual-sections-l9-ru-parts.json",
    "knowledge-base/manual-sections-l9-zh-parts.json",
]

BASE_DIR = Path("C:/Diagnostica-KB-Package")

# ───────────────────────────────────────────────────────────────────────────
def detect_lang_label(filename: str) -> str:
    """Detect declared language from filename."""
    fn = filename.lower()
    if "-en" in fn:  return "EN"
    if "-ru" in fn:  return "RU"
    if "-zh" in fn:  return "ZH"
    return "UNK"

def dominant_script(text: str) -> str:
    """Return the dominant script in text."""
    zh = len(RE_CHINESE.findall(text))
    cy = len(RE_CYRILLIC.findall(text))
    la = len(RE_LATIN.findall(text))
    total = zh + cy + la
    if total == 0:
        return "UNK"
    if zh / total > 0.5:   return "ZH"
    if cy / total > 0.5:   return "RU"
    if la / total > 0.5:   return "EN"
    return "MIX"

def is_contaminated(text: str, declared_lang: str) -> tuple[bool, float]:
    """Return (is_contaminated, foreign_ratio)."""
    if len(text) < 20:
        return False, 0.0
    zh = len(RE_CHINESE.findall(text))
    cy = len(RE_CYRILLIC.findall(text))
    la = len(RE_LATIN.findall(text))
    total = zh + cy + la
    if total == 0:
        return False, 0.0
    if declared_lang == "ZH":
        foreign = cy + la
    elif declared_lang == "RU":
        foreign = zh
    elif declared_lang == "EN":
        foreign = zh + cy
    else:
        return False, 0.0
    ratio = foreign / total if total > 0 else 0.0
    return ratio >= LANG_CONTAMINATION_RATIO, ratio

def has_ocr_artifacts(text: str) -> list[str]:
    """Return list of artifact types found."""
    found = []
    if TOC_DOTS.search(text):    found.append("TOC_DOTS")
    if TOC_DOTDOT.search(text):  found.append("TOC_DOTDOT")
    if REPEATED_CH.search(text): found.append("REPEATED_CHARS")
    # Count TOC-like lines (≥30% of lines end with digit)
    lines = [l for l in text.split('\n') if l.strip()]
    if lines:
        toc_lines = sum(1 for l in lines if TOC_LINE.search(l.strip()))
        if toc_lines / len(lines) > 0.3 and len(lines) > 3:
            found.append("TOC_PAGE")
    return found

def title_quality(title: str) -> str:
    """Rate title quality."""
    if not title or not title.strip():
        return "EMPTY"
    t = title.strip()
    if PAGE_NUM_TITLE.match(t):
        return "PAGE_NUM_ONLY"
    if len(t) < 3:
        return "TOO_SHORT"
    if len(t) > 300:
        return "TOO_LONG"
    return "OK"

def extract_sections(data) -> list[dict]:
    """Normalize various JSON structures into list of {title, content} dicts."""
    sections = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                title   = item.get("title", item.get("heading", item.get("name", "")))
                content = item.get("content", item.get("text", item.get("body", "")))
                # content might be a list
                if isinstance(content, list):
                    content = "\n".join(str(c) for c in content)
                sections.append({"title": str(title or ""), "content": str(content or "")})
    elif isinstance(data, dict):
        # Could be {sections: [...]} or {key: {title, content}, ...}
        if "sections" in data:
            return extract_sections(data["sections"])
        for key, val in data.items():
            if isinstance(val, dict):
                title   = val.get("title", val.get("heading", key))
                content = val.get("content", val.get("text", val.get("body", "")))
                if isinstance(content, list):
                    content = "\n".join(str(c) for c in content)
                sections.append({"title": str(title or key), "content": str(content or "")})
            elif isinstance(val, str):
                sections.append({"title": str(key), "content": val})
    return sections

# ───────────────────────────────────────────────────────────────────────────
def audit_file(rel_path: str) -> dict:
    path = BASE_DIR / rel_path
    result = {
        "file": rel_path,
        "exists": path.exists(),
        "errors": [],
    }
    if not path.exists():
        result["errors"].append("FILE NOT FOUND")
        return result

    # ── Load ──
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)
    except Exception as e:
        result["errors"].append(f"JSON parse error: {e}")
        return result

    sections = extract_sections(data)
    declared = detect_lang_label(rel_path)
    result["declared_lang"] = declared
    result["total_sections"] = len(sections)

    if not sections:
        result["errors"].append("No sections extracted")
        return result

    # ── Per-section analysis ──
    lengths = []
    empty_sections   = []
    contaminated_sections = []
    ocr_artifact_sections = []
    page_num_titles  = []
    empty_titles     = []
    meaningful_count = 0
    all_contents     = []
    title_ok_count   = 0
    total_artifact_types = Counter()

    for i, sec in enumerate(sections):
        title   = sec["title"]
        content = sec["content"]
        full    = (title + " " + content).strip()
        clen    = len(content.strip())
        lengths.append(clen)

        # Empty / near-empty
        if clen < NEAR_EMPTY_THRESHOLD:
            empty_sections.append({
                "idx": i, "title": title[:80], "content": content[:80], "len": clen
            })

        # Language contamination (content only)
        if clen >= 20:
            contaminated, ratio = is_contaminated(content, declared)
            if contaminated:
                contaminated_sections.append({
                    "idx": i, "title": title[:60],
                    "ratio": round(ratio, 3),
                    "snippet": content[:120]
                })

        # OCR artifacts
        artifacts = has_ocr_artifacts(content)
        if artifacts:
            for a in artifacts:
                total_artifact_types[a] += 1
            ocr_artifact_sections.append({
                "idx": i, "title": title[:60],
                "artifacts": artifacts,
                "snippet": content[:120]
            })

        # Title quality
        tq = title_quality(title)
        if tq == "OK":
            title_ok_count += 1
        elif tq == "PAGE_NUM_ONLY":
            page_num_titles.append({"idx": i, "title": title})
        elif tq == "EMPTY":
            empty_titles.append({"idx": i})

        # Meaningful content
        if clen >= MEANINGFUL_THRESHOLD:
            dom = dominant_script(content)
            if declared == "ZH" and dom in ("ZH", "MIX"):
                meaningful_count += 1
            elif declared == "RU" and dom in ("RU", "MIX"):
                meaningful_count += 1
            elif declared == "EN" and dom in ("EN", "MIX"):
                meaningful_count += 1
            elif declared == "UNK":
                meaningful_count += 1

        all_contents.append(content.strip())

    # ── Duplicates ──
    dup_counter = Counter(c for c in all_contents if len(c) > 30)
    duplicates = {c: cnt for c, cnt in dup_counter.items() if cnt > 1}
    dup_groups = sorted([(cnt, c[:80]) for c, cnt in duplicates.items()], reverse=True)

    # ── Stats ──
    total   = len(sections)
    avg_len = sum(lengths) / total if total else 0
    min_len = min(lengths) if lengths else 0
    max_len = max(lengths) if lengths else 0

    result.update({
        "avg_len":          round(avg_len, 1),
        "min_len":          min_len,
        "max_len":          max_len,
        "empty_count":      len(empty_sections),
        "empty_examples":   empty_sections[:5],
        "contaminated_count": len(contaminated_sections),
        "contaminated_examples": contaminated_sections[:5],
        "ocr_artifact_count": len(ocr_artifact_sections),
        "ocr_artifact_types": dict(total_artifact_types),
        "ocr_artifact_examples": ocr_artifact_sections[:5],
        "page_num_title_count": len(page_num_titles),
        "page_num_title_examples": page_num_titles[:5],
        "empty_title_count": len(empty_titles),
        "title_ok_count":   title_ok_count,
        "meaningful_count": meaningful_count,
        "meaningful_pct":   round(meaningful_count / total * 100, 1) if total else 0,
        "dup_group_count":  len(duplicates),
        "dup_top5":         dup_groups[:5],
    })
    return result

# ───────────────────────────────────────────────────────────────────────────
def rate_file(r: dict) -> str:
    """Rate file GREEN/YELLOW/RED based on metrics."""
    if not r.get("exists") or r.get("errors"):
        return "RED"
    total = r.get("total_sections", 0)
    if total == 0:
        return "RED"
    empty_pct     = r["empty_count"]     / total * 100
    contam_pct    = r["contaminated_count"] / total * 100
    artifact_pct  = r["ocr_artifact_count"] / total * 100
    meaningful    = r["meaningful_pct"]
    page_num_pct  = r["page_num_title_count"] / total * 100

    red_conditions = [
        empty_pct     > 40,
        contam_pct    > 30,
        meaningful    < 30,
        artifact_pct  > 40,
    ]
    yellow_conditions = [
        empty_pct     > 15,
        contam_pct    > 10,
        meaningful    < 60,
        artifact_pct  > 15,
        page_num_pct  > 20,
        r["dup_group_count"] > 20,
    ]
    if any(red_conditions):
        return "RED"
    if any(yellow_conditions):
        return "YELLOW"
    return "GREEN"

# ───────────────────────────────────────────────────────────────────────────
def print_report(r: dict, rating: str):
    fn = r["file"]
    sep = "=" * 72
    print(f"\n{sep}")
    print(f"  FILE: {fn}")
    print(f"  RATING: {rating}  |  LANG: {r.get('declared_lang','?')}")
    print(sep)

    if not r.get("exists"):
        print("  !! FILE NOT FOUND !!")
        return
    if r.get("errors"):
        for e in r["errors"]:
            print(f"  ERROR: {e}")
        return

    total = r["total_sections"]
    print(f"\n[1] TOTAL SECTIONS:      {total}")
    print(f"    Avg length:          {r['avg_len']} chars")
    print(f"    Min / Max:           {r['min_len']} / {r['max_len']} chars")

    print(f"\n[2] EMPTY/NEAR-EMPTY (<{NEAR_EMPTY_THRESHOLD} chars): {r['empty_count']} "
          f"({r['empty_count']/total*100:.1f}%)")
    for ex in r["empty_examples"]:
        print(f"      idx={ex['idx']}  title={ex['title']!r}  len={ex['len']}")

    print(f"\n[3] LANGUAGE CONTAMINATION: {r['contaminated_count']} "
          f"({r['contaminated_count']/total*100:.1f}%)")
    for ex in r["contaminated_examples"]:
        print(f"      idx={ex['idx']}  ratio={ex['ratio']}  title={ex['title']!r}")
        print(f"        snippet: {ex['snippet']!r}")

    print(f"\n[4] OCR ARTIFACTS: {r['ocr_artifact_count']} "
          f"({r['ocr_artifact_count']/total*100:.1f}%)")
    if r["ocr_artifact_types"]:
        for atype, cnt in r["ocr_artifact_types"].items():
            print(f"      {atype}: {cnt} sections")
    for ex in r["ocr_artifact_examples"]:
        print(f"      idx={ex['idx']}  {ex['artifacts']}  title={ex['title']!r}")
        print(f"        snippet: {ex['snippet']!r}")

    print(f"\n[5] AVG SECTION LENGTH:  {r['avg_len']} chars  (min={r['min_len']}, max={r['max_len']})")

    print(f"\n[6] MEANINGFUL (>{MEANINGFUL_THRESHOLD} chars + correct lang): "
          f"{r['meaningful_count']} / {total} = {r['meaningful_pct']}%")

    print(f"\n[7] DUPLICATES: {r['dup_group_count']} duplicate content groups")
    for cnt, snippet in r["dup_top5"]:
        print(f"      x{cnt}: {snippet!r}")

    print(f"\n[8] TITLE QUALITY:")
    print(f"      OK titles:          {r['title_ok_count']} ({r['title_ok_count']/total*100:.1f}%)")
    print(f"      Page-number only:   {r['page_num_title_count']} ({r['page_num_title_count']/total*100:.1f}%)")
    print(f"      Empty titles:       {r['empty_title_count']} ({r['empty_title_count']/total*100:.1f}%)")
    for ex in r["page_num_title_examples"]:
        print(f"        idx={ex['idx']}  title={ex['title']!r}")

# ───────────────────────────────────────────────────────────────────────────
def print_summary(results: list, ratings: list):
    print("\n" + "=" * 72)
    print("  SUMMARY TABLE")
    print("=" * 72)
    header = f"{'File':<42} {'Sec':>5} {'Empty%':>7} {'Contam%':>8} {'OCR%':>6} {'Mean%':>6} {'Dup':>5} {'Rating':>7}"
    print(header)
    print("-" * 72)
    for r, rating in zip(results, ratings):
        fn  = Path(r["file"]).name
        if not r.get("exists") or r.get("errors"):
            print(f"  {fn:<40}  {'FILE ERROR':>50}  {rating}")
            continue
        total = r["total_sections"]
        ep    = f"{r['empty_count']/total*100:.1f}%" if total else "-"
        cp    = f"{r['contaminated_count']/total*100:.1f}%" if total else "-"
        ap    = f"{r['ocr_artifact_count']/total*100:.1f}%" if total else "-"
        mp    = f"{r['meaningful_pct']}%"
        dup   = str(r["dup_group_count"])
        print(f"  {fn:<40} {total:>5} {ep:>7} {cp:>8} {ap:>6} {mp:>6} {dup:>5}  {rating}")

# ───────────────────────────────────────────────────────────────────────────
def main():
    results = []
    ratings = []
    for rel_path in FILES:
        print(f"\n... auditing {rel_path} ...", file=sys.stderr, flush=True)
        r = audit_file(rel_path)
        rating = rate_file(r)
        results.append(r)
        ratings.append(rating)
        print_report(r, rating)

    print_summary(results, ratings)

if __name__ == "__main__":
    main()
