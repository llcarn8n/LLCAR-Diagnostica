#!/usr/bin/env python3
"""
build_kb.py - Main Knowledge Base builder for LLCAR Diagnostica.

Reads sections-*.json and web-sections-*.json from the knowledge-base/
directory, creates a fully normalised SQLite database with FTS5 virtual
table, chunked content, DTC linkage, and glossary term linkage.

Key properties:
 - Deterministic chunk IDs via SHA256 (idempotent: INSERT OR IGNORE)
 - Skip-on-same-hash: re-computes content_hash and skips unchanged chunks
 - Unicode NFKC normalisation on ALL text fields
 - Transaction batching every 100 chunks
 - Progress bars via tqdm
 - Detailed statistics on completion
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Optional tqdm – graceful fallback so the script runs even without it
# ---------------------------------------------------------------------------
try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover

    def tqdm(iterable=None, **kwargs):  # type: ignore[misc]
        """Minimal no-op replacement when tqdm is not installed."""
        if iterable is not None:
            return iterable
        # When used as a context manager (tqdm.tqdm()) return a dummy object
        class _Dummy:
            def update(self, *a, **kw):
                pass
            def close(self):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *a):
                pass
        return _Dummy()


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("build_kb")


# ---------------------------------------------------------------------------
# Layer classification keywords (RU + EN + ZH)
# ---------------------------------------------------------------------------
LAYER_KEYWORDS: dict[str, list[str]] = {
    "engine": [
        # RU
        "двигатель", "мотор", "топлив", "бензин", "дизель", "впуск",
        "выхлоп", "глушитель", "турбо", "масл", "зажиган", "свеч",
        "генератор", "range extender", "увеличитель хода", "усилитель хода",
        "охлаждение двигателя", "систем охлаждения",
        # EN
        "engine", "fuel", "exhaust", "intake", "oil", "ignition",
        "turbo", "range extender", "coolant",
        # ZH
        "发动机", "增程", "燃油", "排气", "进气", "机油",
    ],
    "drivetrain": [
        # RU
        "трансмисс", "привод", "подвеск", "амортизатор", "пружин", "рычаг",
        "колес", "шин", "дифференциал", "карданн", "ШРУС", "ступиц", "рессор",
        "редуктор",
        # EN
        "transmission", "suspension", "wheel", "tire", "differential",
        "drivetrain", "axle", "driveshaft",
        # ZH
        "变速", "悬架", "车轮", "轮胎", "差速器", "驱动",
    ],
    "ev": [
        # RU
        "аккумулятор", "батаре", "зарядк", "зарядн", "электрич", "инвертор",
        "проводк", "предохранитель", "реле", "ЭБУ", "ECU", "BMS",
        "высоковольтн", "12В", "высоковольт",
        # EN
        "battery", "charging", "electric", "ev", "DC-DC", "12V",
        "inverter", "bms", "hv battery", "high voltage",
        # ZH
        "电池", "充电", "电动", "逆变器", "高压",
    ],
    "brakes": [
        # RU
        "тормоз", "ABS", "ESC", "ESP", "суппорт", "колодк",
        "рулевой", "руле", "электроусилитель рулевого",
        # EN
        "brake", "abs", "esc", "esp", "caliper", "steering",
        # ZH
        "制动", "刹车", "转向", "方向盘",
    ],
    "sensors": [
        # RU
        "камер", "радар", "лидар", "датчик", "ADAS", "подушк",
        "airbag", "ремень безопасн", "ультразвук", "парков",
        "предупрежден", "распознаван", "помощ при",
        # EN
        "camera", "radar", "lidar", "sensor", "adas", "airbag",
        "seatbelt", "ultrasonic", "parking",
        # ZH
        "摄像头", "雷达", "激光雷达", "传感器", "安全气囊", "安全带",
    ],
    "hvac": [
        # RU
        "кондиционер", "климат", "отоплен", "вентиляц", "печк", "HVAC",
        "тепловой насос", "хладагент", "фильтр салон", "охлажден салон",
        "обогрев", "температур",
        # EN
        "hvac", "air conditioning", "climate", "heating", "ventilation",
        "heat pump", "refrigerant",
        # ZH
        "空调", "暖风", "通风", "热泵", "制冷剂",
    ],
    "interior": [
        # RU
        "сиден", "двер", "багажник", "зеркал", "панел", "приборн",
        "экран", "мультимедиа", "рул", "педал", "окн", "стекл",
        "освещ", "свет", "подсветк", "замок", "ключ", "карточк",
        "интерьер", "обивк", "ковр", "потолок",
        # EN
        "seat", "door", "trunk", "mirror", "dashboard", "infotainment",
        "screen", "pedal", "window", "glass", "lock", "key", "interior",
        # ZH
        "座椅", "车门", "后备箱", "后视镜", "仪表", "屏幕", "多媒体",
        "方向盘", "踏板", "车窗",
    ],
    "body": [
        # RU
        "кузов", "бампер", "крыл", "крыш", "стойк", "капот",
        "лобов", "стеклоочистител", "дворник", "фар", "фонар", "наружн",
        # EN
        "body", "bumper", "fender", "roof", "pillar", "hood",
        "windshield", "wiper", "headlight", "taillight",
        # ZH
        "车身", "保险杠", "翼子板", "车顶", "车柱", "发动机盖",
        "挡风玻璃", "雨刮", "大灯",
    ],
}

# ---------------------------------------------------------------------------
# Warning markers used in has_warnings()
# ---------------------------------------------------------------------------
WARNING_PATTERNS_RU = [
    r"внимание",
    r"предупрежден",
    r"опасн",
    r"осторожн",
    r"запрещ",
    r"не допуск",
]
WARNING_PATTERNS_EN = [
    r"\bwarning\b",
    r"\bcaution\b",
    r"\bdanger\b",
    r"\bdo not\b",
    r"\bnote\b",
]
WARNING_PATTERNS_ZH = [
    r"警告",
    r"注意",
    r"危险",
    r"禁止",
    r"请勿",
]
_WARNING_RE = re.compile(
    "|".join(
        WARNING_PATTERNS_RU + WARNING_PATTERNS_EN + WARNING_PATTERNS_ZH
    ),
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# SQL DDL
# ---------------------------------------------------------------------------
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    source_language TEXT NOT NULL,
    layer TEXT NOT NULL,
    content_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT DEFAULT '',
    page_start INTEGER DEFAULT 0,
    page_end INTEGER DEFAULT 0,
    has_procedures BOOLEAN DEFAULT 0,
    has_warnings BOOLEAN DEFAULT 0,
    content_hash TEXT NOT NULL,
    is_current BOOLEAN DEFAULT 1,
    superseded_by TEXT REFERENCES chunks(id),
    edition_year INTEGER,
    manual_version TEXT,
    glossary_version TEXT DEFAULT 'v1.0',
    ocr_tool TEXT,
    ocr_confidence REAL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chunk_content (
    chunk_id TEXT NOT NULL REFERENCES chunks(id),
    lang TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    translated_by TEXT DEFAULT 'original',
    quality_score REAL,
    terminology_score REAL,
    glossary_version TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (chunk_id, lang)
);

CREATE TABLE IF NOT EXISTS chunk_dtc (
    chunk_id TEXT NOT NULL REFERENCES chunks(id),
    dtc_code TEXT NOT NULL,
    PRIMARY KEY (chunk_id, dtc_code)
);
CREATE INDEX IF NOT EXISTS idx_chunk_dtc_code ON chunk_dtc(dtc_code);

CREATE TABLE IF NOT EXISTS chunk_glossary (
    chunk_id TEXT NOT NULL REFERENCES chunks(id),
    glossary_id TEXT NOT NULL,
    PRIMARY KEY (chunk_id, glossary_id)
);
CREATE INDEX IF NOT EXISTS idx_chunk_glossary_id ON chunk_glossary(glossary_id);

CREATE TABLE IF NOT EXISTS chunk_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT NOT NULL REFERENCES chunks(id),
    image_path TEXT NOT NULL,
    thumbnail_path TEXT,
    caption TEXT,
    page_idx INTEGER,
    width INTEGER,
    height INTEGER
);

CREATE TABLE IF NOT EXISTS translation_cache (
    cache_key TEXT PRIMARY KEY,
    source_text TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    glossary_version TEXT,
    model_id TEXT DEFAULT 'claude-haiku-4-5',
    quality_score REAL,
    terminology_score REAL,
    token_cost_input INTEGER,
    token_cost_output INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_trans_cache_lang ON translation_cache(target_lang);

CREATE TABLE IF NOT EXISTS glossary_versions (
    version TEXT PRIMARY KEY,
    created_at TEXT DEFAULT (datetime('now')),
    changes_count INTEGER,
    breaking_changes TEXT
);

CREATE TABLE IF NOT EXISTS colbert_vectors (
    chunk_id TEXT PRIMARY KEY REFERENCES chunks(id),
    colbert_matrix BLOB NOT NULL,
    token_count INTEGER
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    title,
    content,
    content='',
    tokenize='unicode61'
);

CREATE TABLE IF NOT EXISTS kb_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

TRIGGER_SQL = """
CREATE TRIGGER IF NOT EXISTS chunk_content_ai AFTER INSERT ON chunk_content BEGIN
    INSERT INTO chunks_fts(rowid, title, content) VALUES (new.rowid, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS chunk_content_ad AFTER DELETE ON chunk_content BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, title, content) VALUES('delete', old.rowid, old.title, old.content);
END;
"""


# ===========================================================================
# Core utility functions
# ===========================================================================

def nfkc(text: str) -> str:
    """Normalise a string to Unicode NFKC form."""
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFKC", text)


def make_chunk_id(brand: str, model: str, lang: str, section_title: str, content: str) -> str:
    """
    Create a deterministic chunk ID.

    Format: {brand}_{model}_{lang}_{sha256[:8]}
    The hash is computed over (brand, model, lang, title, content) so that
    the same logical chunk always gets the same ID regardless of insertion
    order.
    """
    raw = f"{brand}|{model}|{lang}|{section_title}|{content}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    safe_brand = re.sub(r"[^a-z0-9_]", "_", brand.lower())
    safe_model = re.sub(r"[^a-z0-9_]", "_", model.lower())
    safe_lang = re.sub(r"[^a-z0-9_]", "_", lang.lower())
    return f"{safe_brand}_{safe_model}_{safe_lang}_{h[:8]}"


def content_hash(text: str) -> str:
    """SHA256 hex digest of the normalised text (used for idempotency)."""
    return hashlib.sha256(nfkc(text).encode("utf-8")).hexdigest()


def chunk_text(text: str, title: str, max_tokens: int = 2000, overlap: int = 100) -> list[str]:
    """
    Split *text* into chunks of at most *max_tokens* approximate tokens.

    Approximation: 1 token ≈ 4 characters (works reasonably for mixed
    Latin/Cyrillic/CJK text).

    Strategy:
    1. Split by double-newline (paragraph boundary) first.
    2. If a paragraph is still too large, split by single newline, then
       by sentence boundary ('. '/'。').
    3. Accumulate paragraphs into a chunk until the token budget is used.
    4. When a chunk is finalised the last *overlap* tokens of that chunk
       are prepended to the next one as context.

    A chunk always starts with the section title so retrieval context is
    unambiguous.
    """
    max_chars = max_tokens * 4
    overlap_chars = overlap * 4

    text = nfkc(text).strip()
    if not text:
        return []

    # ---- Split into atomic paragraphs ----
    paragraphs: list[str] = []
    for raw_para in re.split(r"\n\s*\n", text):
        raw_para = raw_para.strip()
        if not raw_para:
            continue
        # If a single paragraph already exceeds budget, split by sentence
        if len(raw_para) > max_chars:
            # Try line splits first
            lines = [l.strip() for l in raw_para.splitlines() if l.strip()]
            for line in lines:
                if len(line) > max_chars:
                    # Hard-split on sentence endings
                    pieces = re.split(r"(?<=[.。!?！？])\s+", line)
                    paragraphs.extend(p.strip() for p in pieces if p.strip())
                else:
                    paragraphs.append(line)
        else:
            paragraphs.append(raw_para)

    if not paragraphs:
        return [text[:max_chars]] if text else []

    chunks: list[str] = []
    current_parts: list[str] = []
    current_len: int = 0
    overlap_tail: str = ""

    def flush(parts: list[str], tail: str) -> tuple[list[str], int, str]:
        """Finalise a chunk, compute the overlap tail for the next chunk."""
        body = "\n\n".join(parts)
        full_chunk = f"{title}\n\n{tail}{body}" if tail else f"{title}\n\n{body}"
        chunks.append(full_chunk)
        # Compute new tail (last overlap_chars of body)
        new_tail_raw = body[-overlap_chars:] if len(body) > overlap_chars else body
        # Trim to the start of the nearest word/character boundary
        new_tail = new_tail_raw.lstrip()
        return [], 0, new_tail

    for para in paragraphs:
        para_len = len(para)
        # Would adding this paragraph overflow the chunk?
        projected = current_len + para_len + (2 if current_parts else 0)
        if projected > max_chars and current_parts:
            current_parts, current_len, overlap_tail = flush(current_parts, overlap_tail)
        current_parts.append(para)
        current_len += para_len + 2

    if current_parts:
        flush(current_parts, overlap_tail)

    return chunks if chunks else [f"{title}\n\n{text[:max_chars]}"]


def classify_layer(title: str, content: str) -> str:
    """
    Classify a section into one of 8 layer categories using keyword scoring.

    Returns the layer name with the highest keyword hit count, defaulting
    to 'body' when no keywords match.
    """
    sample = nfkc((title + " " + content[:800])).lower()
    scores: dict[str, int] = {}
    for layer, keywords in LAYER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in sample)
        if score:
            scores[layer] = score
    return max(scores, key=scores.get) if scores else "body"


def extract_dtc_codes(content: str) -> list[str]:
    """
    Extract OBD-II / manufacturer DTC codes from *content*.

    Pattern: letter [PCBU] followed by exactly 4 digits.
    Applies NFKC normalisation first to collapse fullwidth digits (e.g. ０－９).
    Returns a sorted, deduplicated list.
    """
    normalised = nfkc(content)
    raw = re.findall(r"\b[PCBU]\d{4}\b", normalised)
    return sorted(set(raw))


def match_glossary(title: str, content: str, glossary_terms: list[dict[str, Any]]) -> list[str]:
    """
    Return glossary term IDs whose EN/RU/ZH label appears in *title* or
    *content*.

    ID is constructed as:  ``{en_snake}@{layer}``  mirroring the convention
    used in the existing sections files (e.g. ``steering_wheel@interior``).
    When no such field is present in the term entry the EN slug is used as
    fallback ID.

    Case-insensitive matching; minimum term length 3 characters.
    """
    haystack = nfkc((title + " " + content[:2000])).lower()
    matched: list[str] = []
    for term in glossary_terms:
        gid: str = term.get("id", "")
        if not gid:
            en = term.get("en", "")
            if en:
                gid = re.sub(r"[^a-z0-9]+", "_", en.lower()).strip("_")
            else:
                continue
        # Try matching any language representation
        for lang_key in ("en", "ru", "zh"):
            label = nfkc(term.get(lang_key, "")).lower()
            if len(label) >= 3 and label in haystack:
                matched.append(gid)
                break
    return matched[:20]  # cap at 20 to avoid unbounded linkage


def has_procedures(content: str) -> bool:
    """
    Return True when the content contains numbered procedural steps.

    Matches patterns like ``1.``, ``2)`` etc. at the start of a line.
    """
    return bool(re.search(r"^\s*\d+[\.\)]\s", content, re.MULTILINE))


def has_warnings(content: str) -> bool:
    """Return True when the content contains warning/caution markers."""
    return bool(_WARNING_RE.search(nfkc(content)))


# ===========================================================================
# Database helpers
# ===========================================================================

def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables, indexes, virtual tables, and triggers."""
    cur = conn.cursor()
    # Execute statements one by one; sqlite3 doesn't support multi-statement
    # executescript() from a cursor but conn.executescript() works fine.
    conn.executescript(SCHEMA_SQL)
    conn.executescript(TRIGGER_SQL)
    conn.commit()
    log.info("Schema created / verified.")


def upsert_chunk(
    cur: sqlite3.Cursor,
    *,
    chunk_id: str,
    brand: str,
    model: str,
    source_language: str,
    layer: str,
    content_type: str,
    title: str,
    content: str,
    source: str,
    source_url: str = "",
    page_start: int = 0,
    page_end: int = 0,
    has_proc: bool = False,
    has_warn: bool = False,
    chash: str,
    force: bool = False,
) -> tuple[bool, bool]:
    """
    Insert or update a chunk row.

    Returns (inserted: bool, skipped: bool).
    - inserted=True, skipped=False  → new row
    - inserted=False, skipped=True  → content_hash unchanged, no action
    - inserted=False, skipped=False → content_hash changed, row updated
    """
    existing = cur.execute(
        "SELECT content_hash FROM chunks WHERE id = ?", (chunk_id,)
    ).fetchone()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %human:%M:%S").replace(
        "human", "H"  # keep strftime letter intact (workaround for f-string)
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    if existing is None:
        cur.execute(
            """
            INSERT INTO chunks (
                id, brand, model, source_language, layer, content_type,
                title, content, source, source_url,
                page_start, page_end, has_procedures, has_warnings,
                content_hash, is_current, created_at, updated_at
            ) VALUES (?,?,?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?,?)
            """,
            (
                chunk_id, brand, model, source_language, layer, content_type,
                title, content, source, source_url,
                page_start, page_end, int(has_proc), int(has_warn),
                chash, 1, now, now,
            ),
        )
        return (True, False)

    if not force and existing[0] == chash:
        return (False, True)  # unchanged

    # Content changed – update
    cur.execute(
        """
        UPDATE chunks SET
            layer=?, content_type=?, title=?, content=?,
            source=?, source_url=?, page_start=?, page_end=?,
            has_procedures=?, has_warnings=?,
            content_hash=?, updated_at=?
        WHERE id=?
        """,
        (
            layer, content_type, title, content,
            source, source_url, page_start, page_end,
            int(has_proc), int(has_warn),
            chash, now,
            chunk_id,
        ),
    )
    return (False, False)


# ===========================================================================
# Section-file processor
# ===========================================================================

def _get(obj: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Try multiple key names (camelCase and snake_case variants)."""
    for k in keys:
        if k in obj:
            return obj[k]
    return default


def process_source_file(
    filepath: Path,
    brand: str,
    model: str,
    lang: str,
    content_type: str,
    source_tag: str,
    glossary_terms: list[dict[str, Any]],
    conn: sqlite3.Connection,
    force: bool = False,
    brand_filter: str | None = None,
    model_filter: str | None = None,
) -> dict[str, int]:
    """
    Load one sections-*.json file and insert chunks into the database.

    Returns a stats dict with keys: sections, chunks, inserted, skipped,
    updated, errors.
    """
    if not filepath.exists():
        log.warning("File not found, skipping: %s", filepath)
        return {"sections": 0, "chunks": 0, "inserted": 0, "skipped": 0, "updated": 0, "errors": 0}

    if brand_filter and brand != brand_filter:
        return {"sections": 0, "chunks": 0, "inserted": 0, "skipped": 0, "updated": 0, "errors": 0}
    if model_filter and model != model_filter:
        return {"sections": 0, "chunks": 0, "inserted": 0, "skipped": 0, "updated": 0, "errors": 0}

    log.info("Processing: %s  (brand=%s model=%s lang=%s)", filepath.name, brand, model, lang)

    with open(filepath, encoding="utf-8") as fh:
        raw = json.load(fh)

    # Sections can be top-level list OR nested under a "sections" key
    if isinstance(raw, list):
        sections = raw
    else:
        sections = raw.get("sections", [])

    stats = {"sections": len(sections), "chunks": 0, "inserted": 0, "skipped": 0, "updated": 0, "errors": 0}

    cur = conn.cursor()
    batch = 0
    BATCH_SIZE = 100

    for sec in tqdm(sections, desc=filepath.name[:30], unit="sec", leave=False):
        try:
            raw_title = nfkc(_get(sec, "title", default="")).strip()
            raw_content = nfkc(_get(sec, "content", default="")).strip()

            if not raw_title or not raw_content:
                continue

            # TOC artifact filter: skip sections that are mostly "dots + page number"
            _lines = [l for l in raw_content.split('\n') if l.strip()]
            _toc_lines = sum(1 for l in _lines if re.search(r'\.{3,}\s*\d+', l))
            if _lines and _toc_lines / len(_lines) > 0.5:
                stats["skipped"] += 1
                continue

            page_start = int(_get(sec, "pageStart", "page_start", default=0) or 0)
            page_end = int(_get(sec, "pageEnd", "page_end", default=0) or 0)
            source_url = nfkc(_get(sec, "sourceUrl", "source_url", default="") or "")

            # Layer: prefer existing field, re-classify only if 'general'
            stored_layer = _get(sec, "layer", default="")
            if stored_layer and stored_layer not in ("general", ""):
                layer = stored_layer
            else:
                layer = classify_layer(raw_title, raw_content)

            # DTC codes: prefer existing field, augment with regex scan
            stored_dtc: list[str] = _get(sec, "dtcCodes", "dtc_codes", default=[]) or []
            scanned_dtc = extract_dtc_codes(raw_content)
            dtc_codes = sorted(set(stored_dtc) | set(scanned_dtc))

            # Glossary IDs: prefer existing field, augment with live matching
            stored_gids: list[str] = _get(sec, "glossaryIds", "glossary_ids", default=[]) or []
            live_gids = match_glossary(raw_title, raw_content, glossary_terms)
            glossary_ids = list(dict.fromkeys(stored_gids + live_gids))  # preserve order, dedup

            # Procedure / warning flags
            has_proc = bool(_get(sec, "hasProcedures", "has_procedures", default=False)) or has_procedures(raw_content)
            has_warn = bool(_get(sec, "hasWarnings", "has_warnings", default=False)) or has_warnings(raw_content)

            # Chunk the content
            text_chunks = chunk_text(raw_content, raw_title)

            for chunk_idx, chunk_body in enumerate(text_chunks):
                stats["chunks"] += 1
                cid = make_chunk_id(brand, model, lang, raw_title, chunk_body)
                chash = content_hash(chunk_body)

                inserted, skipped = upsert_chunk(
                    cur,
                    chunk_id=cid,
                    brand=brand,
                    model=model,
                    source_language=lang,
                    layer=layer,
                    content_type=content_type,
                    title=raw_title,
                    content=chunk_body,
                    source=source_tag,
                    source_url=source_url,
                    page_start=page_start,
                    page_end=page_end,
                    has_proc=has_proc,
                    has_warn=has_warn,
                    chash=chash,
                    force=force,
                )

                if skipped:
                    stats["skipped"] += 1
                    continue
                if inserted:
                    stats["inserted"] += 1
                else:
                    stats["updated"] += 1

                # chunk_content (primary language)
                cur.execute(
                    """
                    INSERT OR REPLACE INTO chunk_content
                        (chunk_id, lang, title, content, translated_by)
                    VALUES (?,?,?,?,?)
                    """,
                    (cid, lang, raw_title, chunk_body, "original"),
                )

                # chunk_dtc links
                for dtc in dtc_codes:
                    cur.execute(
                        "INSERT OR IGNORE INTO chunk_dtc (chunk_id, dtc_code) VALUES (?,?)",
                        (cid, dtc),
                    )

                # chunk_glossary links
                for gid in glossary_ids[:20]:
                    cur.execute(
                        "INSERT OR IGNORE INTO chunk_glossary (chunk_id, glossary_id) VALUES (?,?)",
                        (cid, gid),
                    )

                batch += 1
                if batch >= BATCH_SIZE:
                    conn.commit()
                    batch = 0

        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            log.warning("Error processing section in %s: %s", filepath.name, exc)
            continue

    conn.commit()
    log.info(
        "  -> %d sections | %d chunks | +%d inserted | ~%d skipped | ^%d updated | !%d errors",
        stats["sections"],
        stats["chunks"],
        stats["inserted"],
        stats["skipped"],
        stats["updated"],
        stats["errors"],
    )
    return stats


# ===========================================================================
# DTC database → dedicated chunks
# ===========================================================================

def process_dtc_database(
    filepath: Path,
    conn: sqlite3.Connection,
    force: bool = False,
) -> dict[str, int]:
    """
    Convert DTC database entries into standalone diagnostic chunks.

    Each DTC code becomes a chunk with its own row in chunks, chunk_content,
    and chunk_dtc.
    """
    if not filepath.exists():
        log.warning("DTC database not found: %s", filepath)
        return {"dtc_codes": 0, "chunks": 0, "inserted": 0, "skipped": 0}

    log.info("Processing DTC database: %s", filepath.name)

    with open(filepath, encoding="utf-8") as fh:
        raw = json.load(fh)

    codes: dict[str, Any] = raw.get("codes", {})
    stats = {"dtc_codes": len(codes), "chunks": 0, "inserted": 0, "skipped": 0}

    cur = conn.cursor()
    batch = 0

    for code, info in tqdm(codes.items(), desc="DTC codes", unit="code", leave=False):
        title_en = nfkc(info.get("title_en", code))
        title_ru = nfkc(info.get("title_ru", ""))
        title_zh = nfkc(info.get("title_zh", ""))
        severity = info.get("severity", 0)
        can_drive = info.get("can_drive", "")
        causes_raw = info.get("probable_causes", [])
        system = info.get("system", "body")

        causes_text_ru = "\n".join(f"- {c}" for c in causes_raw) if causes_raw else ""
        content_ru = (
            f"Код неисправности: {code}\n"
            f"Описание: {title_ru or title_en}\n"
            f"Система: {system}\n"
            f"Серьёзность: {severity}\n"
            f"Можно ли ехать: {can_drive}\n"
        )
        if causes_text_ru:
            content_ru += f"\nВозможные причины:\n{causes_text_ru}"

        content_en = (
            f"Fault Code: {code}\n"
            f"Description: {title_en}\n"
            f"System: {system}\n"
            f"Severity: {severity}\n"
            f"Can drive: {can_drive}\n"
        )

        for lang, title, content in [
            ("ru", title_ru or code, content_ru),
            ("en", title_en or code, content_en),
        ]:
            cid = make_chunk_id("li_auto", "l9_l7", lang, f"DTC {code}", content)
            chash = content_hash(content)
            stats["chunks"] += 1

            inserted, skipped = upsert_chunk(
                cur,
                chunk_id=cid,
                brand="li_auto",
                model="l9_l7",
                source_language=lang,
                layer=system,
                content_type="dtc",
                title=f"DTC {code}: {title}",
                content=content,
                source="dtc_database",
                chash=chash,
                force=force,
            )

            if skipped:
                stats["skipped"] += 1
                continue
            if inserted:
                stats["inserted"] += 1

            cur.execute(
                """
                INSERT OR REPLACE INTO chunk_content
                    (chunk_id, lang, title, content, translated_by)
                VALUES (?,?,?,?,?)
                """,
                (cid, lang, f"DTC {code}: {title}", content, "original"),
            )
            cur.execute(
                "INSERT OR IGNORE INTO chunk_dtc (chunk_id, dtc_code) VALUES (?,?)",
                (cid, code),
            )

            batch += 1
            if batch >= 100:
                conn.commit()
                batch = 0

    conn.commit()
    log.info(
        "  -> %d DTC codes | %d chunks | +%d inserted | ~%d skipped",
        stats["dtc_codes"],
        stats["chunks"],
        stats["inserted"],
        stats["skipped"],
    )
    return stats


# ===========================================================================
# Main build function
# ===========================================================================

def _load_glossary(glossary_path: Path) -> list[dict[str, Any]]:
    """
    Load glossary terms from either format:
      - Flat:  {"terms": [{"en":..., "ru":..., "zh":...}, ...]}
      - Categorised (5-lang): {"categories": {"cat": {"terms": [...]}, ...},
                                "obd_abbreviations": {"terms": [...]}}
    Returns a flat list of term dicts, each guaranteed to have an 'id' field.
    """
    if not glossary_path.exists():
        log.warning("Glossary not found at %s – skipping term matching", glossary_path)
        return []

    with open(glossary_path, encoding="utf-8") as fh:
        graw = json.load(fh)

    raw_terms: list[dict[str, Any]] = []

    if "terms" in graw and isinstance(graw["terms"], list):
        # Flat format (glossary-unified-trilingual.json)
        raw_terms = graw["terms"]
    elif "categories" in graw:
        # Categorised format (automotive-glossary-5lang.json)
        for _cat_name, cat_data in graw["categories"].items():
            cat_terms = cat_data.get("terms", [])
            if isinstance(cat_terms, list):
                raw_terms.extend(cat_terms)
        # Also pull obd_abbreviations
        obd = graw.get("obd_abbreviations", {})
        if isinstance(obd, dict):
            obd_terms = obd.get("terms", [])
            if isinstance(obd_terms, list):
                raw_terms.extend(obd_terms)
    else:
        log.warning("Unrecognised glossary format in %s", glossary_path)
        return []

    # Inject a synthetic 'id' field based on EN slug where missing
    for term in raw_terms:
        if "id" not in term:
            en_slug = re.sub(r"[^a-z0-9]+", "_", term.get("en", "").lower()).strip("_")
            term["id"] = en_slug

    log.info("Loaded %d glossary terms from %s", len(raw_terms), glossary_path.name)
    return raw_terms


def build_kb(
    kb_dir: Path,
    db_path: Path,
    force: bool = False,
    brand_filter: str | None = None,
    model_filter: str | None = None,
    glossary_path: Path | None = None,
) -> None:
    """
    Entry-point for the full KB build pipeline.

    1. Create / connect SQLite, apply schema
    2. Load glossary terms for matching
    3. Process each source sections file
    4. Process DTC database
    5. Record glossary_version and kb_meta
    6. Print statistics summary
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    log.info("Opening database: %s", db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")

    create_schema(conn)

    # ---- Load glossary ----
    if glossary_path is None:
        glossary_path = kb_dir / "glossary-unified-trilingual.json"
    glossary_terms = _load_glossary(glossary_path)

    # ---- Source file definitions ----
    # Tuple: (filename, brand, model, lang, content_type, source_tag)
    sources = [
        ("sections-l9-ru.json",       "li_auto", "l9", "ru", "manual",  "pdf_l9_ru"),
        # REMOVED: sections-l7-ru.json — 68% corrupt (mixed RU+ZH, garbled text)
        ("sections-l7-zh.json",       "li_auto", "l7", "zh", "manual",  "pdf_l7_zh"),
        ("sections-l7-zh-full.json",  "li_auto", "l7", "zh", "manual",  "pdf_l7_zh_full"),
        ("sections-l9-zh.json",       "li_auto", "l9", "zh", "manual",  "pdf_l9_zh"),
        ("sections-l9-zh-full.json",  "li_auto", "l9", "zh", "manual",  "pdf_l9_zh_full"),
        ("sections-l9-parts-zh.json", "li_auto", "l9", "zh", "parts",   "parts_l9_zh"),
        ("web-sections-l7-zh.json",   "li_auto", "l7", "zh", "manual",  "web_l7_zh"),
        # MinerU OCR sources (added session 16, 2026-03-02)
        ("sections-l9-en-config.json",       "li_auto", "l9", "en", "config", "mineru_l9_en_config"),
        ("sections-l7-zh-config.json",       "li_auto", "l7", "zh", "config", "mineru_l7_zh_config"),
        ("sections-l9-zh-parts-mineru.json", "li_auto", "l9", "zh", "parts",  "mineru_l9_zh_parts"),
        ("sections-l9-en.json",              "li_auto", "l9", "en", "manual", "mineru_l9_en"),
        ("sections-l9-zh-owners-mineru.json","li_auto", "l9", "zh", "manual", "mineru_l9_zh_owners"),
        ("sections-l7-zh-owners-mineru.json","li_auto", "l7", "zh", "manual", "mineru_l7_zh_owners"),
        ("sections-l9-ru-mineru.json",       "li_auto", "l9", "ru", "manual", "mineru_l9_ru"),
    ]

    # ---- Global aggregated statistics ----
    total_stats: dict[str, int] = {
        "sections": 0, "chunks": 0, "inserted": 0, "skipped": 0, "updated": 0, "errors": 0,
    }
    per_source_stats: list[dict[str, Any]] = []
    per_layer_stats: dict[str, int] = {}
    per_lang_stats: dict[str, int] = {}

    # ---- Process each source ----
    for filename, brand, model, lang, content_type, source_tag in sources:
        filepath = kb_dir / filename
        stats = process_source_file(
            filepath,
            brand,
            model,
            lang,
            content_type,
            source_tag,
            glossary_terms,
            conn,
            force=force,
            brand_filter=brand_filter,
            model_filter=model_filter,
        )
        for k in total_stats:
            total_stats[k] += stats.get(k, 0)
        per_source_stats.append({"source": source_tag, "lang": lang, **stats})

    # ---- Process DTC database ----
    dtc_path = kb_dir / "dtc-database.json"
    dtc_stats = process_dtc_database(dtc_path, conn, force=force)
    total_stats["chunks"] += dtc_stats.get("chunks", 0)
    total_stats["inserted"] += dtc_stats.get("inserted", 0)
    total_stats["skipped"] += dtc_stats.get("skipped", 0)

    # ---- Layer & language breakdown from DB ----
    cur = conn.cursor()
    for row in cur.execute("SELECT layer, COUNT(*) FROM chunks GROUP BY layer"):
        per_layer_stats[row[0]] = row[1]
    for row in cur.execute("SELECT source_language, COUNT(*) FROM chunks GROUP BY source_language"):
        per_lang_stats[row[0]] = row[1]

    total_chunks_in_db = cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

    # ---- Glossary version record ----
    gv = "v1.0"
    conn.execute(
        "INSERT OR IGNORE INTO glossary_versions (version, changes_count) VALUES (?,?)",
        (gv, len(glossary_terms)),
    )

    # ---- kb_meta ----
    build_ts = datetime.now(timezone.utc).isoformat()
    meta_rows = [
        ("build_timestamp", build_ts),
        ("total_chunks", str(total_chunks_in_db)),
        ("glossary_version", gv),
        ("glossary_terms", str(len(glossary_terms))),
        ("builder_version", "2.0.0"),
        ("schema_version", "2.0"),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO kb_meta (key, value) VALUES (?,?)", meta_rows
    )
    conn.commit()
    conn.close()

    # ---- Print statistics ----
    print("\n" + "=" * 62)
    print("  DIAGNOSTICA KB BUILD COMPLETE")
    print("=" * 62)
    print(f"  Database      : {db_path}")
    print(f"  Build time    : {build_ts}")
    print(f"  Total chunks  : {total_chunks_in_db:,}")
    print(f"  Inserted      : {total_stats['inserted']:,}")
    print(f"  Skipped (=)   : {total_stats['skipped']:,}")
    print(f"  Updated (~)   : {total_stats['updated']:,}")
    print(f"  Errors        : {total_stats['errors']:,}")
    print()
    print("  Chunks per layer:")
    for layer, cnt in sorted(per_layer_stats.items(), key=lambda x: -x[1]):
        print(f"    {layer:<14} {cnt:>6,}")
    print()
    print("  Chunks per language:")
    for lang, cnt in sorted(per_lang_stats.items()):
        print(f"    {lang:<6} {cnt:>6,}")
    print()
    print("  Per-source breakdown:")
    for s in per_source_stats:
        if s["chunks"]:
            print(
                f"    {s['source']:<22}  {s['chunks']:>5,} chunks  "
                f"+{s['inserted']:>5,} ins  ~{s['skipped']:>5,} skip"
            )
    print("=" * 62 + "\n")


# ===========================================================================
# CLI entry-point
# ===========================================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the LLCAR Diagnostica Knowledge Base SQLite database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--kb-dir",
        default=None,
        help="Path to knowledge-base directory. "
             "Defaults to <script_parent_dir>/../knowledge-base",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Output SQLite file path. "
             "Defaults to <kb-dir>/kb.db",
    )
    parser.add_argument(
        "--brand",
        default=None,
        help="Process only this brand (e.g. li_auto).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Process only this model (e.g. l9).",
    )
    parser.add_argument(
        "--glossary",
        default=None,
        help="Path to glossary JSON file. Supports flat (trilingual) "
             "and categorised (5-lang) formats. "
             "Defaults to <kb-dir>/glossary-unified-trilingual.json",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Re-insert / update chunks even when content_hash is unchanged.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable DEBUG-level logging.",
    )

    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    if args.kb_dir:
        kb_dir = Path(args.kb_dir).resolve()
    else:
        kb_dir = project_root / "knowledge-base"

    if args.db_path:
        db_path = Path(args.db_path).resolve()
    else:
        db_path = kb_dir / "kb.db"

    log.info("Project root : %s", project_root)
    log.info("KB directory : %s", kb_dir)
    log.info("DB path      : %s", db_path)

    if not kb_dir.is_dir():
        log.error("knowledge-base directory not found: %s", kb_dir)
        return 1

    glossary_path = Path(args.glossary).resolve() if args.glossary else None

    build_kb(
        kb_dir=kb_dir,
        db_path=db_path,
        force=args.force,
        brand_filter=args.brand,
        model_filter=args.model,
        glossary_path=glossary_path,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
