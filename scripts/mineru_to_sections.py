#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mineru_to_sections.py — Convert MinerU markdown output to sections-*.json format
for import into the Diagnostica KB via build_kb.py.

Usage:
    python scripts/mineru_to_sections.py

Produces sections JSON files in knowledge-base/ for each MinerU document.
"""
from __future__ import annotations
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import re
import unicodedata
from pathlib import Path

KB_DIR = Path("C:/Diagnostica-KB-Package/knowledge-base")

# MinerU markdown files to convert
# (md_path, vehicle, lang, content_type, source_tag, out_filename)
SOURCES = [
    (
        "C:/Diagnostica-KB-Package/mineru-output/240322-Li-L9-Configuration/auto/240322-Li-L9-Configuration.md",
        "l9", "en", "config", "mineru_l9_en_config",
        "sections-l9-en-config.json",
    ),
    (
        "C:/Diagnostica-KB-Package/mineru-output/857694655-241015-L7参数配置中文/ocr/857694655-241015-L7参数配置中文.md",
        "l7", "zh", "config", "mineru_l7_zh_config",
        "sections-l7-zh-config.json",
    ),
    (
        "C:/Diagnostica-KB-Package/mineru-output/941362155-2022-2023款理想L9零件手册/ocr/941362155-2022-2023款理想L9零件手册.md",
        "l9", "zh", "parts", "mineru_l9_zh_parts",
        "sections-l9-zh-parts-mineru.json",
    ),
    (
        "C:/Diagnostica-KB-Package/mineru-output/Li L9英文版/auto/Li L9英文版.md",
        "l9", "en", "manual", "mineru_l9_en",
        "sections-l9-en.json",
    ),
    (
        "C:/Diagnostica-KB-Package/mineru-output/Lixiang L9 Owner's Manual/auto/Lixiang L9 Owner's Manual.md",
        "l9", "zh", "manual", "mineru_l9_zh_owners",
        "sections-l9-zh-owners-mineru.json",
    ),
    (
        "C:/Diagnostica-KB-Package/mineru-output/Lixiang L7 Owner's Manual/auto/Lixiang L7 Owner's Manual.md",
        "l7", "zh", "manual", "mineru_l7_zh_owners",
        "sections-l7-zh-owners-mineru.json",
    ),
    (
        "C:/Diagnostica-KB-Package/mineru-output/Lixiang L9 Руководство пользователя/auto/Lixiang L9 Руководство пользователя.md",
        "l9", "ru", "manual", "mineru_l9_ru",
        "sections-l9-ru-mineru.json",
    ),
]

# Regex to detect image lines (MinerU renders images as markdown links)
RE_IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
RE_HEADING = re.compile(r'^(#{1,4})\s+(.*)')
# LaTeX noise patterns
RE_LATEX = re.compile(r'\$[^$]{1,100}\$')
RE_MATHRM = re.compile(r'\\mathrm\{[^}]+\}')


def nfkc(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def clean_text(text: str, images_base: Path | None = None) -> str:
    """Remove LaTeX, resolve image paths to absolute, keep readable content."""
    text = RE_LATEX.sub('', text)
    text = RE_MATHRM.sub('', text)
    # Replace relative image paths with absolute paths
    if images_base is not None:
        def replace_img(m):
            alt, src = m.group(1), m.group(2)
            if not src.startswith(('http', 'C:', '/')):
                abs_path = (images_base / src).resolve().as_posix()
                return f'![{alt}]({abs_path})'
            return m.group(0)
        text = RE_IMAGE.sub(replace_img, text)
    else:
        text = RE_IMAGE.sub('', text)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return nfkc(text)


def detect_layer(title: str, content: str) -> str:
    combined = (title + ' ' + content).lower()
    if any(w in combined for w in ['battery', '电池', 'аккумулятор', 'зарядк', 'charging', 'high voltage', '高压']):
        return 'battery'
    if any(w in combined for w in ['engine', 'range extender', '增程', 'fuel', 'exhaust', '发动机', 'двигатель']):
        return 'engine'
    if any(w in combined for w in ['brake', 'тормоз', '刹车', '制动', 'abs', 'esp']):
        return 'brakes'
    if any(w in combined for w in ['adas', 'lidar', 'camera', 'radar', 'autopilot', '辅助驾驶', 'автопилот', 'lcc']):
        return 'adas'
    if any(w in combined for w in ['hvac', 'climate', 'air condition', '空调', 'кондиционер', 'heating']):
        return 'hvac'
    if any(w in combined for w in ['infotainment', 'display', 'screen', 'audio', 'bluetooth', '蓝牙', 'блютус', '导航', 'навигац']):
        return 'infotainment'
    if any(w in combined for w in ['door', 'window', 'seat', 'mirror', '车门', '车窗', '座椅', 'дверь', 'окно', 'сиденье']):
        return 'body'
    if any(w in combined for w in ['wheel', 'tire', 'tyre', 'suspension', 'steering', '轮', '悬架', 'колесо', 'подвеск']):
        return 'chassis'
    if any(w in combined for w in ['lamp', 'light', 'led', '灯', 'фара', 'фонарь']):
        return 'lighting'
    if any(w in combined for w in ['part', '零件', 'запчасть', 'запасн', 'component', '部件']):
        return 'parts'
    return 'general'


def has_procedures(text: str) -> bool:
    return bool(re.search(r'\d+\.\s+\w|步骤|шаг|step \d', text, re.IGNORECASE))


def has_warnings(text: str) -> bool:
    return bool(re.search(
        r'warning|caution|danger|警告|注意|危险|осторожно|внимание|предупреждение',
        text, re.IGNORECASE
    ))


def split_markdown_sections(text: str, vehicle: str, lang: str,
                             content_type: str, source_tag: str,
                             images_base: Path | None = None) -> list[dict]:
    """Split markdown by headings into sections."""
    lines = text.splitlines()
    sections = []
    current_title = f"{source_tag}_intro"
    current_lines: list[str] = []
    section_id = 0
    page_num = 1

    def flush(title: str, body_lines: list[str], sid: int) -> dict | None:
        body = '\n'.join(body_lines).strip()
        body = clean_text(body, images_base)
        # Skip sections that are just images or too short
        body_no_img = RE_IMAGE.sub('', body).strip()
        if len(body_no_img) < 30:
            return None
        return {
            "sectionId": str(sid),
            "title": nfkc(title.strip()),
            "content": body,
            "pageStart": page_num,
            "pageEnd": page_num,
            "vehicle": vehicle,
            "language": lang,
            "contentType": content_type,
            "layer": detect_layer(title, body),
            "dtcCodes": [],
            "glossaryIds": [],
            "hasProcedures": has_procedures(body),
            "hasWarnings": has_warnings(body),
            "contentLength": len(body),
            "source": source_tag,
        }

    for line in lines:
        m = RE_HEADING.match(line)
        if m:
            # Flush current section
            if current_lines:
                sec = flush(current_title, current_lines, section_id)
                if sec:
                    sections.append(sec)
                    section_id += 1
            current_title = m.group(2)
            current_lines = []
        else:
            current_lines.append(line)

    # Flush last section
    if current_lines:
        sec = flush(current_title, current_lines, section_id)
        if sec:
            sections.append(sec)

    return sections


def convert(md_path: str, vehicle: str, lang: str, content_type: str,
            source_tag: str, out_filename: str) -> None:
    p = Path(md_path)
    if not p.exists():
        print(f"  SKIP (not found): {md_path}")
        return

    text = p.read_text(encoding='utf-8', errors='replace')
    images_base = p.parent  # MinerU stores images in ./images/ relative to the .md file
    sections = split_markdown_sections(text, vehicle, lang, content_type, source_tag, images_base)

    out = {
        "meta": {
            "vehicle": vehicle,
            "language": lang,
            "contentType": content_type,
            "source": source_tag,
            "totalSections": len(sections),
            "sourceFile": p.name,
        },
        "sections": sections,
    }

    out_path = KB_DIR / out_filename
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"  OK: {out_filename}  ({len(sections)} sections from {p.name})")


def main():
    print("=== MinerU to sections JSON conversion ===")
    KB_DIR.mkdir(exist_ok=True)
    for args in SOURCES:
        convert(*args)
    print("\nDone. Add new sources to build_kb.py and re-run.")


if __name__ == "__main__":
    main()
