#!/usr/bin/env python3
"""
translate_kb.py - Claude Haiku 4.5 Batch translation pipeline for LLCAR Diagnostica KB.

Translates full sections stored in kb.db (chunk_content table) using the
Anthropic Batch API with prompt caching, a 3374-term automotive glossary,
and terminology-match quality validation.

Translation directions (source_language of chunk → target langs):
  ru  → en, zh
  zh  → ru, en
  en  → ru, zh  (only 244 chunks, low priority)

3-Tier priority:
  Tier 1  — all titles (~5%)           → sync (immediate, one chunk at a time)
  Tier 2  — top-200 critical sections  → priority queue (has_procedures OR has_warnings)
  Tier 3  — remaining content          → bulk Batch API

Usage examples:
    python scripts/translate_kb.py --dry-run
    python scripts/translate_kb.py --tier 1
    python scripts/translate_kb.py --tier 2 --brand li_auto --verbose
    python scripts/translate_kb.py --tier all --batch-size 50
    python scripts/translate_kb.py --tier 3 --target-langs en,zh --db-path knowledge-base/kb.db

Dependencies:
    pip install anthropic tqdm tenacity

Environment:
    ANTHROPIC_API_KEY  — required (Claude API key)
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import os
import re
import sqlite3
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

# ---------------------------------------------------------------------------
# Windows: force UTF-8 output so Cyrillic / CJK render correctly in console
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Optional imports — graceful fallback with clear error messages
# ---------------------------------------------------------------------------
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None  # type: ignore[assignment]

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

    class _TqdmFallback:
        """Minimal no-op tqdm replacement."""

        def __init__(self, iterable=None, **kwargs):
            self._it = iterable

        def __iter__(self):
            return iter(self._it) if self._it is not None else iter([])

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def update(self, *a, **kw):
            pass

        def set_postfix(self, *a, **kw):
            pass

        def close(self):
            pass

    tqdm = _TqdmFallback  # type: ignore[misc,assignment]

try:
    from tenacity import (
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("translate_kb")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_ID = "claude-haiku-4-5-20251001"
GLOSSARY_VERSION = "3.1"

# Cost per 1M tokens (USD) — Claude Haiku 4.5, Batch API prices
# Standard: $1.00/M input, $5.00/M output
# Batch API: 50 % discount → $0.50/M input, $2.50/M output
# Prompt cache write: $1.25/M; cache read: $0.10/M
# Source: https://platform.claude.com/docs/en/about-claude/pricing
COST_INPUT_PER_M = 0.50      # $0.50/M (Batch API input)
COST_OUTPUT_PER_M = 2.50     # $2.50/M (Batch API output)
COST_CACHE_WRITE_PER_M = 1.25  # $1.25/M (prompt cache write)
COST_CACHE_READ_PER_M = 0.10   # $0.10/M (prompt cache read)

# How many requests to pack into a single Batch API call
DEFAULT_BATCH_SIZE = 50

# Terminology validation threshold (below → flag for human review)
TERMINOLOGY_THRESHOLD = 0.75

# Max tokens per translation response
MAX_RESPONSE_TOKENS = 4096

# Batch poll interval (seconds)
BATCH_POLL_INTERVAL = 5

# Language display names for prompts
LANG_NAMES = {
    "en": "English",
    "ru": "Russian",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
    "es": "Spanish",
}

# Source → default target languages
DEFAULT_TARGET_LANGS: dict[str, list[str]] = {
    "ru": ["en", "zh"],
    "zh": ["ru", "en"],
    "en": ["ru", "zh"],
}

# Tier 2: top-200 critical sections ranked by procedures + warnings
TIER2_LIMIT = 200

# Transaction commit interval
COMMIT_EVERY = 25


# ===========================================================================
# Utility helpers
# ===========================================================================

def nfkc(text: str) -> str:
    """Unicode NFKC normalisation."""
    return unicodedata.normalize("NFKC", text) if isinstance(text, str) else ""


def make_cache_key(chunk_id: str, target_lang: str, content: str) -> str:
    """Deterministic SHA256 cache key for a translation unit."""
    raw = f"{chunk_id}|{target_lang}|{content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def approx_tokens(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 chars (Latin/CJK mix)."""
    return max(1, len(text) // 4)


def now_utc() -> str:
    """UTC timestamp string for DB storage."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ===========================================================================
# Glossary loading and XML formatting
# ===========================================================================

class GlossaryTerm(NamedTuple):
    en: str
    ru: str
    zh: str
    ar: str
    es: str
    category: str


def load_glossary(glossary_path: Path) -> list[GlossaryTerm]:
    """
    Load automotive-glossary-5lang.json and flatten all categories into a list
    of GlossaryTerm named tuples.

    JSON structure:
      { "meta": {...}, "categories": { "body_frame": { "label": "...", "terms": [...] }, ... } }
    Each term: { "en": "...", "ru": "...", "zh": "...", "ar": "...", "es": "..." }
    """
    log.info("Loading glossary from: %s", glossary_path)
    with glossary_path.open(encoding="utf-8") as f:
        data = json.load(f)

    categories: dict[str, Any] = data.get("categories", {})
    terms: list[GlossaryTerm] = []

    for cat_key, cat_val in categories.items():
        raw_terms = cat_val.get("terms", [])
        for t in raw_terms:
            if not isinstance(t, dict):
                continue
            terms.append(GlossaryTerm(
                en=nfkc(t.get("en", "")),
                ru=nfkc(t.get("ru", "")),
                zh=nfkc(t.get("zh", "")),
                ar=nfkc(t.get("ar", "")),
                es=nfkc(t.get("es", "")),
                category=cat_key,
            ))

    log.info("Loaded %d glossary terms across %d categories.", len(terms), len(categories))
    return terms


def filter_glossary_for_prompt(
    terms: list[GlossaryTerm],
    max_terms: int,
) -> list[GlossaryTerm]:
    """
    Return at most max_terms terms, preserving category balance.

    Terms are sorted by category so that all 11 automotive categories
    remain represented when the list is truncated.  When max_terms=0,
    all terms are returned unchanged.
    """
    if max_terms <= 0 or max_terms >= len(terms):
        return terms

    # Distribute slots proportionally across categories
    from collections import defaultdict
    by_cat: dict[str, list[GlossaryTerm]] = defaultdict(list)
    for t in terms:
        by_cat[t.category].append(t)

    total_cats = len(by_cat)
    per_cat = max(1, max_terms // total_cats)
    selected: list[GlossaryTerm] = []
    remainder = max_terms

    for cat_terms in by_cat.values():
        take = min(per_cat, len(cat_terms), remainder)
        selected.extend(cat_terms[:take])
        remainder -= take
        if remainder <= 0:
            break

    log.info(
        "Glossary limited to %d / %d terms for system prompt.",
        len(selected), len(terms),
    )
    return selected


def build_glossary_xml(terms: list[GlossaryTerm]) -> str:
    """
    Format glossary terms as XML for injection into system prompt.

    Example output:
      <term><en>brake pad</en><ru>тормозная колодка</ru><zh>刹车片</zh><ar>وسادة الفرامل</ar><es>pastilla de freno</es></term>
    """
    lines: list[str] = ["<automotive_glossary>"]
    for t in terms:
        parts = []
        if t.en:
            parts.append(f"<en>{t.en}</en>")
        if t.ru:
            parts.append(f"<ru>{t.ru}</ru>")
        if t.zh:
            parts.append(f"<zh>{t.zh}</zh>")
        if t.ar:
            parts.append(f"<ar>{t.ar}</ar>")
        if t.es:
            parts.append(f"<es>{t.es}</es>")
        if parts:
            lines.append(f"<term>{''.join(parts)}</term>")
    lines.append("</automotive_glossary>")
    return "\n".join(lines)


# ===========================================================================
# System prompt construction
# ===========================================================================

SYSTEM_PROMPT_TEMPLATE = """\
You are an expert automotive technical translator with deep knowledge of vehicle \
diagnostics, repair procedures, and automotive engineering.

{glossary_xml}

TRANSLATION RULES — FOLLOW EXACTLY:
1. Use the EXACT translated terms from the glossary above whenever a source term appears.
2. Preserve document structure: numbered steps, bullet lists, tables, Markdown headings.
3. Do NOT translate or modify technical parameters: torque values (Nm), pressures (kPa, bar),
   temperatures (°C, °F), voltages (V), capacities (L, mL), percentages (%), distances (km, mm).
4. Do NOT translate DTC/OBD fault codes (e.g., P0420, C1234, U0100, B0001).
5. Do NOT translate part numbers, model names (Li Auto L9, L7), or brand names.
6. Preserve all Markdown formatting: **bold**, *italic*, `code`, # headings, > blockquotes.
7. Preserve line breaks and paragraph structure exactly as in the source.
8. Output ONLY the translated text — no explanations, no meta-commentary.
9. For Chinese output: use Simplified Chinese (mainland standard).
10. For technical terms not in the glossary, use the most precise automotive industry term.
"""

def build_system_prompt(glossary_xml: str) -> str:
    """Inject glossary XML into the system prompt template."""
    return SYSTEM_PROMPT_TEMPLATE.format(glossary_xml=glossary_xml)


# ===========================================================================
# Terminology match validation
# ===========================================================================

def compute_terminology_score(
    source_text: str,
    translated_text: str,
    source_lang: str,
    target_lang: str,
    glossary_terms: list[GlossaryTerm],
) -> float:
    """
    Measure how many glossary terms present in the source have a correct
    translation in the output.

    Algorithm:
      1. Find all terms whose source-language label appears in source_text.
      2. For each matched term, check if the target-language label appears
         in translated_text.
      3. Score = matched_in_output / total_matched_in_source
         (returns 1.0 when no terms from the glossary appear in source)

    Both comparisons are case-insensitive after NFKC normalisation.
    """
    source_lower = nfkc(source_text).lower()
    translated_lower = nfkc(translated_text).lower()

    found_in_source = 0
    found_in_output = 0

    for term in glossary_terms:
        src_label = getattr(term, source_lang, "").lower()
        tgt_label = getattr(term, target_lang, "").lower()

        if not src_label or len(src_label) < 3:
            continue
        if src_label not in source_lower:
            continue

        found_in_source += 1
        if tgt_label and tgt_label in translated_lower:
            found_in_output += 1

    if found_in_source == 0:
        return 1.0  # No relevant terms — cannot penalise

    return round(found_in_output / found_in_source, 4)


# ===========================================================================
# Database helpers
# ===========================================================================

def open_db(db_path: Path) -> sqlite3.Connection:
    """Open SQLite connection with WAL mode and foreign key enforcement."""
    conn = sqlite3.connect(str(db_path), timeout=60)   # wait up to 60s if locked
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=60000")          # 60s busy wait
    return conn


def ensure_translation_cache_table(conn: sqlite3.Connection) -> None:
    """Create translation_cache if it doesn't already exist (idempotent)."""
    conn.executescript("""
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
        CREATE INDEX IF NOT EXISTS idx_trans_cache_lang
            ON translation_cache(target_lang);
    """)
    conn.commit()


class ChunkRecord(NamedTuple):
    """A chunk row with all fields needed for translation."""
    chunk_id: str
    source_language: str
    title: str
    content: str
    has_procedures: int
    has_warnings: int
    content_type: str
    brand: str
    model: str


def fetch_untranslated_chunks(
    conn: sqlite3.Connection,
    brand: str,
    target_langs: list[str],
    tier: str,
) -> list[tuple[ChunkRecord, str]]:
    """
    Return (ChunkRecord, target_lang) pairs that need translation.

    A chunk needs translation for a target_lang when:
      - chunk_content row for (chunk_id, target_lang) does NOT exist yet
      - target_lang != source_language of the chunk

    Tier filtering:
      tier "1"   → only titles (short content <= 300 chars)
      tier "2"   → top-200 chunks ranked by (has_procedures + has_warnings)
      tier "3"   → everything not covered by tiers 1 & 2
      tier "all" → all untranslated chunks

    Returns list sorted by priority (procedures + warnings desc, then chunk_id).
    """
    # Build subquery: existing translations
    existing_sql = """
        SELECT chunk_id || '|' || lang AS pair_key
        FROM chunk_content
        WHERE translated_by != 'original'
    """

    base_query = f"""
        SELECT
            c.id              AS chunk_id,
            c.source_language AS source_language,
            c.title           AS title,
            c.content         AS content,
            c.has_procedures  AS has_procedures,
            c.has_warnings    AS has_warnings,
            c.content_type    AS content_type,
            c.brand           AS brand,
            c.model           AS model
        FROM chunks c
        WHERE c.brand = ?
          AND c.is_current = 1
        ORDER BY (c.has_procedures + c.has_warnings) DESC,
                 c.has_procedures DESC,
                 c.id ASC
    """

    rows = conn.execute(base_query, (brand,)).fetchall()
    existing_pairs: set[str] = {
        r[0] for r in conn.execute(existing_sql).fetchall()
    }

    pairs: list[tuple[ChunkRecord, str]] = []
    tier2_count: dict[str, int] = {}  # track per-lang count for tier 2

    for row in rows:
        chunk = ChunkRecord(
            chunk_id=row["chunk_id"],
            source_language=row["source_language"],
            title=row["title"],
            content=row["content"],
            has_procedures=row["has_procedures"],
            has_warnings=row["has_warnings"],
            content_type=row["content_type"],
            brand=row["brand"],
            model=row["model"],
        )

        for tgt_lang in target_langs:
            # Skip same-language translation
            if tgt_lang == chunk.source_language:
                continue
            # Skip if already translated
            pair_key = f"{chunk.chunk_id}|{tgt_lang}"
            if pair_key in existing_pairs:
                continue

            # Tier filtering
            content_len = len(chunk.content)
            is_title_only = content_len <= 300
            is_critical = bool(chunk.has_procedures or chunk.has_warnings)

            if tier == "1":
                if not is_title_only:
                    continue
            elif tier == "2":
                if is_title_only:
                    continue  # Tier 1 handles these
                if not is_critical:
                    continue
                cnt = tier2_count.get(tgt_lang, 0)
                if cnt >= TIER2_LIMIT:
                    continue
                tier2_count[tgt_lang] = cnt + 1
            elif tier == "3":
                if is_title_only:
                    continue
                if is_critical:
                    # Already covered by tier 2; skip unless --tier all
                    cnt = tier2_count.get(tgt_lang, 0)
                    if cnt < TIER2_LIMIT:
                        tier2_count[tgt_lang] = cnt + 1
                        continue
            # tier "all" → no filtering

            pairs.append((chunk, tgt_lang))

    log.info(
        "Found %d chunk×lang pairs needing translation (tier=%s).",
        len(pairs), tier,
    )
    return pairs


def lookup_cache(
    conn: sqlite3.Connection,
    cache_key: str,
) -> tuple[str, float, float] | None:
    """Return (translated_text, quality_score, terminology_score) or None."""
    row = conn.execute(
        "SELECT translated_text, quality_score, terminology_score "
        "FROM translation_cache WHERE cache_key = ?",
        (cache_key,),
    ).fetchone()
    if row:
        return str(row[0]), float(row[1] or 0.0), float(row[2] or 0.0)
    return None


def save_to_db(
    conn: sqlite3.Connection,
    *,
    chunk: ChunkRecord,
    target_lang: str,
    translated_title: str,
    translated_content: str,
    terminology_score: float,
    model_id: str,
    tokens_input: int,
    tokens_output: int,
    cache_key: str,
    flagged_for_review: bool,
) -> None:
    """
    Write translation results to chunk_content and translation_cache.

    chunk_content PRIMARY KEY is (chunk_id, lang) — INSERT OR REPLACE so we
    can overwrite a previous machine translation when quality improves.
    """
    ts = now_utc()
    quality_score = 1.0 if not flagged_for_review else terminology_score

    # 1. chunk_content
    conn.execute(
        """
        INSERT OR REPLACE INTO chunk_content (
            chunk_id, lang, title, content,
            translated_by, quality_score, terminology_score,
            glossary_version, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chunk.chunk_id, target_lang,
            translated_title, translated_content,
            model_id, quality_score, terminology_score,
            GLOSSARY_VERSION, ts,
        ),
    )

    # 2. translation_cache (full content only — skip very short titles to save space)
    if len(chunk.content) > 50:
        conn.execute(
            """
            INSERT OR REPLACE INTO translation_cache (
                cache_key, source_text, target_lang, translated_text,
                glossary_version, model_id,
                quality_score, terminology_score,
                token_cost_input, token_cost_output, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cache_key,
                chunk.content, target_lang, translated_content,
                GLOSSARY_VERSION, model_id,
                quality_score, terminology_score,
                tokens_input, tokens_output, ts,
            ),
        )


# ===========================================================================
# Training pair export
# ===========================================================================

def save_training_pair(
    pairs_file: Path,
    source_lang: str,
    target_lang: str,
    source_text: str,
    translated_text: str,
    terminology_score: float,
    chunk_id: str,
) -> None:
    """Append one JSONL training pair to the output file."""
    record = {
        "id": chunk_id,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "source": source_text,
        "translation": translated_text,
        "terminology_score": terminology_score,
        "model": MODEL_ID,
        "glossary_version": GLOSSARY_VERSION,
        "created_at": now_utc(),
    }
    with pairs_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ===========================================================================
# Cost tracking
# ===========================================================================

class CostTracker:
    """Accumulates token usage and computes estimated USD cost."""

    def __init__(self) -> None:
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.cache_write_tokens: int = 0
        self.cache_read_tokens: int = 0
        self.translated_count: int = 0
        self.cache_hits: int = 0
        self.flagged_count: int = 0
        self.skipped_count: int = 0
        self.error_count: int = 0

    def add_usage(
        self,
        input_t: int,
        output_t: int,
        cache_write_t: int = 0,
        cache_read_t: int = 0,
    ) -> None:
        self.input_tokens += input_t
        self.output_tokens += output_t
        self.cache_write_tokens += cache_write_t
        self.cache_read_tokens += cache_read_t

    @property
    def estimated_cost_usd(self) -> float:
        cost = (
            self.input_tokens / 1_000_000 * COST_INPUT_PER_M
            + self.output_tokens / 1_000_000 * COST_OUTPUT_PER_M
            + self.cache_write_tokens / 1_000_000 * COST_CACHE_WRITE_PER_M
            + self.cache_read_tokens / 1_000_000 * COST_CACHE_READ_PER_M
        )
        return round(cost, 4)

    def report(self) -> str:
        lines = [
            "=" * 60,
            "  TRANSLATION SUMMARY",
            "=" * 60,
            f"  Translated        : {self.translated_count}",
            f"  Cache hits        : {self.cache_hits}",
            f"  Flagged (review)  : {self.flagged_count}",
            f"  Skipped (errors)  : {self.error_count}",
            f"  Input tokens      : {self.input_tokens:,}",
            f"  Output tokens     : {self.output_tokens:,}",
            f"  Cache write tokens: {self.cache_write_tokens:,}",
            f"  Cache read tokens : {self.cache_read_tokens:,}",
            f"  Estimated cost    : ${self.estimated_cost_usd:.4f} USD",
            "=" * 60,
        ]
        return "\n".join(lines)


# ===========================================================================
# Dry-run cost estimation
# ===========================================================================

def dry_run_estimate(
    pairs: list[tuple[ChunkRecord, str]],
    system_prompt_tokens: int,
) -> None:
    """Print cost estimate without calling the API."""
    # user_input: only the user message (not the system prompt — it is cached)
    total_user_input = 0
    total_output = 0
    n = len(pairs)

    for chunk, tgt_lang in pairs:
        user_msg_tokens = approx_tokens(
            f"Translate to {LANG_NAMES.get(tgt_lang, tgt_lang)}:\n\n{chunk.content}"
        )
        resp_tokens = min(approx_tokens(chunk.content) * 2, MAX_RESPONSE_TOKENS)
        total_user_input += user_msg_tokens
        total_output += resp_tokens

    # With prompt caching:
    #   Request 1: 1x cache write (system prompt) + 1x user input
    #   Requests 2..N: each reads system prompt from cache + 1x user input
    cache_write_tokens = system_prompt_tokens        # one-time write
    cache_read_tokens = system_prompt_tokens * max(0, n - 1)   # all subsequent reads
    # Regular input = user messages only (system is fully cached after request 1)
    regular_input_tokens = total_user_input

    cost_input = regular_input_tokens / 1_000_000 * COST_INPUT_PER_M
    cost_output = total_output / 1_000_000 * COST_OUTPUT_PER_M
    cost_cache_w = cache_write_tokens / 1_000_000 * COST_CACHE_WRITE_PER_M
    cost_cache_r = cache_read_tokens / 1_000_000 * COST_CACHE_READ_PER_M
    total_cost = cost_input + cost_output + cost_cache_w + cost_cache_r

    # Tip: estimate cost without full glossary (500 terms ≈ 3000 tokens)
    tip_tokens = 3000 + approx_tokens(SYSTEM_PROMPT_TEMPLATE)
    tip_cache_w = tip_tokens / 1_000_000 * COST_CACHE_WRITE_PER_M
    tip_cache_r = tip_tokens * max(0, n - 1) / 1_000_000 * COST_CACHE_READ_PER_M
    tip_total = cost_input + cost_output + tip_cache_w + tip_cache_r

    print("\n" + "=" * 64)
    print("  DRY-RUN ESTIMATE  (Claude Haiku 4.5 Batch API)")
    print("=" * 64)
    print(f"  Total pairs to translate : {n:>10,}")
    print(f"  System prompt tokens     : {system_prompt_tokens:>10,}  (glossary = {system_prompt_tokens - approx_tokens(SYSTEM_PROMPT_TEMPLATE):,} tokens)")
    print(f"  User input tokens (total): {regular_input_tokens:>10,}")
    print(f"  Output tokens (est.)     : {total_output:>10,}")
    print(f"  Cache WRITE tokens       : {cache_write_tokens:>10,}  (one-time)")
    print(f"  Cache READ tokens        : {cache_read_tokens:>10,}  ({n-1:,} reads)")
    print("-" * 64)
    print(f"  User input  ($0.50/M)    : ${cost_input:>10.4f}")
    print(f"  Output      ($2.50/M)    : ${cost_output:>10.4f}")
    print(f"  Cache write ($1.25/M)    : ${cost_cache_w:>10.4f}")
    print(f"  Cache read  ($0.10/M)    : ${cost_cache_r:>10.4f}")
    print("-" * 64)
    print(f"  TOTAL ESTIMATE           : ${total_cost:>10.4f} USD")
    print("=" * 64)
    if n > 0:
        print(f"\n  With --max-glossary-terms 500:")
        print(f"  TOTAL ESTIMATE           : ${tip_total:>10.4f} USD")
        print(f"  (saves ~${total_cost - tip_total:.4f} USD in cache costs)")
    print("=" * 64 + "\n")


# ===========================================================================
# Batch item builder
# ===========================================================================

def build_batch_requests(
    batch_pairs: list[tuple[ChunkRecord, str]],
    system_prompt: str,
) -> list[dict[str, Any]]:
    """
    Build list of Anthropic Batch API request dicts.

    custom_id format: ``{chunk_id}__LANG__{target_lang}``
    Uses double-underscore separator (Anthropic custom_id only allows [a-zA-Z0-9_-]).
    """
    requests = []
    for chunk, tgt_lang in batch_pairs:
        lang_name = LANG_NAMES.get(tgt_lang, tgt_lang)
        user_content = f"Translate to {lang_name}:\n\n{chunk.content}"

        requests.append({
            "custom_id": f"{chunk.chunk_id}__LANG__{tgt_lang}",
            "params": {
                "model": MODEL_ID,
                "max_tokens": MAX_RESPONSE_TOKENS,
                "system": [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                "messages": [
                    {
                        "role": "user",
                        "content": user_content,
                    }
                ],
            },
        })
    return requests


# ===========================================================================
# Batch polling and result processing
# ===========================================================================

def _poll_batch(client: Any, batch_id: str) -> Any:
    """
    Poll Anthropic batch until it reaches a terminal state.

    States: in_progress → ended | errored | canceled | expired
    """
    log.info("Polling batch %s ...", batch_id)
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        status = batch.processing_status
        rc = batch.request_counts
        log.info(
            "  Batch %s: status=%s  processing=%s  succeeded=%s  errored=%s",
            batch_id, status,
            getattr(rc, "processing", "?"),
            getattr(rc, "succeeded", "?"),
            getattr(rc, "errored", "?"),
        )
        if status == "ended":
            break
        if status in ("errored", "canceled", "expired"):
            raise RuntimeError(f"Batch {batch_id} terminated with status: {status}")
        time.sleep(BATCH_POLL_INTERVAL)
    return batch


def process_batch_results(
    client: Any,
    batch_id: str,
    chunk_map: dict[str, tuple[ChunkRecord, str]],
    conn: sqlite3.Connection,
    glossary_terms: list[GlossaryTerm],
    tracker: CostTracker,
    training_pairs_file: Path | None,
    verbose: bool,
) -> None:
    """
    Stream batch results and save each translation to the database.

    chunk_map: custom_id → (ChunkRecord, target_lang)
    """
    commit_counter = 0

    for result in client.messages.batches.results(batch_id):
        custom_id: str = result.custom_id
        key = custom_id  # custom_id IS the lookup key

        if key not in chunk_map:
            log.warning("Unknown custom_id in batch result: %s", custom_id)
            tracker.error_count += 1
            continue

        chunk, tgt_lang = chunk_map[key]

        if result.result.type == "error":
            err = result.result.error
            log.warning(
                "Batch error for %s -> %s: %s",
                chunk.chunk_id, tgt_lang, err,
            )
            tracker.error_count += 1
            continue

        msg = result.result.message

        # --- Extract text ---
        translated_content = ""
        for block in msg.content:
            if hasattr(block, "text"):
                translated_content += block.text

        translated_content = translated_content.strip()
        if not translated_content:
            log.warning("Empty translation for %s -> %s", chunk.chunk_id, tgt_lang)
            tracker.error_count += 1
            continue

        # --- Token usage ---
        usage = msg.usage
        input_t = getattr(usage, "input_tokens", 0)
        output_t = getattr(usage, "output_tokens", 0)
        cache_write_t = getattr(usage, "cache_creation_input_tokens", 0)
        cache_read_t = getattr(usage, "cache_read_input_tokens", 0)
        tracker.add_usage(input_t, output_t, cache_write_t, cache_read_t)

        # --- Terminology score ---
        terminology_score = compute_terminology_score(
            source_text=chunk.content,
            translated_text=translated_content,
            source_lang=chunk.source_language,
            target_lang=tgt_lang,
            glossary_terms=glossary_terms,
        )
        flagged = terminology_score < TERMINOLOGY_THRESHOLD
        if flagged:
            tracker.flagged_count += 1
            log.warning(
                "LOW TERM SCORE %.3f for %s -> %s (flagged for review)",
                terminology_score, chunk.chunk_id, tgt_lang,
            )

        # --- Translate title separately (sync, reuse same prompt cache) ---
        # For batch mode we approximate title translation by using the first
        # sentence / heading of the translated content.
        # A more accurate approach would be to include title as a separate
        # batch request — implemented in tier 1 (sync) mode below.
        translated_title = _extract_translated_title(
            chunk.title, translated_content, tgt_lang
        )

        # --- Cache key ---
        cache_key = make_cache_key(chunk.chunk_id, tgt_lang, chunk.content)

        if verbose:
            log.debug(
                "[%s -> %s] term_score=%.3f tokens=%d+%d flagged=%s",
                chunk.chunk_id, tgt_lang,
                terminology_score, input_t, output_t, flagged,
            )

        # --- Save to DB ---
        save_to_db(
            conn,
            chunk=chunk,
            target_lang=tgt_lang,
            translated_title=translated_title,
            translated_content=translated_content,
            terminology_score=terminology_score,
            model_id=MODEL_ID,
            tokens_input=input_t,
            tokens_output=output_t,
            cache_key=cache_key,
            flagged_for_review=flagged,
        )
        tracker.translated_count += 1

        # --- Training pair ---
        if training_pairs_file:
            save_training_pair(
                training_pairs_file,
                source_lang=chunk.source_language,
                target_lang=tgt_lang,
                source_text=chunk.content,
                translated_text=translated_content,
                terminology_score=terminology_score,
                chunk_id=chunk.chunk_id,
            )

        # --- Incremental commit ---
        commit_counter += 1
        if commit_counter >= COMMIT_EVERY:
            conn.commit()
            commit_counter = 0
            log.info("Committed %d translations to DB.", tracker.translated_count)

    conn.commit()


def _extract_translated_title(
    original_title: str,
    translated_content: str,
    target_lang: str,
) -> str:
    """
    Best-effort extraction of translated title from the translated content.

    The model is instructed to preserve structure, so if the source title
    appears at the top of the content (which build_kb.py guarantees by
    prepending title to each chunk), the translated content's first line
    is likely the translated title.
    """
    first_line = translated_content.split("\n")[0].strip()
    # Strip Markdown heading markers
    first_line = re.sub(r"^#+\s*", "", first_line).strip()
    if first_line and len(first_line) <= 200:
        return first_line
    # Fallback: use original title untranslated
    return original_title


# ===========================================================================
# Synchronous single-request translation (Tier 1 / fallback)
# ===========================================================================

def translate_single_sync(
    client: Any,
    chunk: ChunkRecord,
    tgt_lang: str,
    system_prompt: str,
    glossary_terms: list[GlossaryTerm],
    tracker: CostTracker,
    verbose: bool,
) -> tuple[str, str, float] | None:
    """
    Translate one chunk synchronously (non-batch).

    Returns (translated_title, translated_content, terminology_score)
    or None on error.

    Uses tenacity retry if available, otherwise simple try/except.
    """
    lang_name = LANG_NAMES.get(tgt_lang, tgt_lang)
    user_content = f"Translate to {lang_name}:\n\n{chunk.content}"

    def _call() -> Any:
        return client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_RESPONSE_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
        )

    try:
        if TENACITY_AVAILABLE:
            # Retry on rate limit / transient errors with exponential backoff
            from tenacity import retry as tenacity_retry, stop_after_attempt, wait_exponential, retry_if_exception_type

            @tenacity_retry(
                retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError)),
                stop=stop_after_attempt(4),
                wait=wait_exponential(multiplier=2, min=2, max=60),
                reraise=True,
            )
            def _call_with_retry() -> Any:
                return _call()

            response = _call_with_retry()
        else:
            response = _call()

    except Exception as exc:
        log.error("Sync translation error for %s -> %s: %s", chunk.chunk_id, tgt_lang, exc)
        tracker.error_count += 1
        return None

    # Extract text
    translated_content = ""
    for block in response.content:
        if hasattr(block, "text"):
            translated_content += block.text
    translated_content = translated_content.strip()

    if not translated_content:
        log.warning("Empty sync translation: %s -> %s", chunk.chunk_id, tgt_lang)
        tracker.error_count += 1
        return None

    # Token usage
    usage = response.usage
    input_t = getattr(usage, "input_tokens", 0)
    output_t = getattr(usage, "output_tokens", 0)
    cache_write_t = getattr(usage, "cache_creation_input_tokens", 0)
    cache_read_t = getattr(usage, "cache_read_input_tokens", 0)
    tracker.add_usage(input_t, output_t, cache_write_t, cache_read_t)

    terminology_score = compute_terminology_score(
        source_text=chunk.content,
        translated_text=translated_content,
        source_lang=chunk.source_language,
        target_lang=tgt_lang,
        glossary_terms=glossary_terms,
    )

    translated_title = _extract_translated_title(
        chunk.title, translated_content, tgt_lang
    )

    if verbose:
        log.debug(
            "[sync] %s -> %s: term_score=%.3f tokens=%d+%d",
            chunk.chunk_id, tgt_lang, terminology_score, input_t, output_t,
        )

    return translated_title, translated_content, terminology_score


# ===========================================================================
# Main pipeline
# ===========================================================================

def run_tier1_sync(
    client: Any,
    conn: sqlite3.Connection,
    pairs: list[tuple[ChunkRecord, str]],
    system_prompt: str,
    glossary_terms: list[GlossaryTerm],
    tracker: CostTracker,
    training_pairs_file: Path | None,
    verbose: bool,
) -> None:
    """
    Tier 1: Translate titles synchronously (one by one).

    Short content (<=300 chars) — low latency, no need for batch API overhead.
    """
    log.info("=== TIER 1: Translating %d titles (sync) ===", len(pairs))
    commit_counter = 0

    bar = tqdm(pairs, desc="Tier 1 titles", unit="title")
    for chunk, tgt_lang in bar:
        # Check cache first
        cache_key = make_cache_key(chunk.chunk_id, tgt_lang, chunk.content)
        cached = lookup_cache(conn, cache_key)
        if cached:
            translated_content, quality_score, terminology_score = cached
            translated_title = _extract_translated_title(
                chunk.title, translated_content, tgt_lang
            )
            save_to_db(
                conn,
                chunk=chunk,
                target_lang=tgt_lang,
                translated_title=translated_title,
                translated_content=translated_content,
                terminology_score=terminology_score,
                model_id=MODEL_ID + "+cache",
                tokens_input=0,
                tokens_output=0,
                cache_key=cache_key,
                flagged_for_review=False,
            )
            tracker.cache_hits += 1
            tracker.translated_count += 1
            continue

        result = translate_single_sync(
            client, chunk, tgt_lang, system_prompt,
            glossary_terms, tracker, verbose,
        )
        if result is None:
            continue

        translated_title, translated_content, terminology_score = result
        flagged = terminology_score < TERMINOLOGY_THRESHOLD
        if flagged:
            tracker.flagged_count += 1

        save_to_db(
            conn,
            chunk=chunk,
            target_lang=tgt_lang,
            translated_title=translated_title,
            translated_content=translated_content,
            terminology_score=terminology_score,
            model_id=MODEL_ID,
            tokens_input=0,
            tokens_output=0,
            cache_key=cache_key,
            flagged_for_review=flagged,
        )
        tracker.translated_count += 1

        if training_pairs_file:
            save_training_pair(
                training_pairs_file,
                source_lang=chunk.source_language,
                target_lang=tgt_lang,
                source_text=chunk.content,
                translated_text=translated_content,
                terminology_score=terminology_score,
                chunk_id=chunk.chunk_id,
            )

        commit_counter += 1
        if commit_counter >= COMMIT_EVERY:
            conn.commit()
            commit_counter = 0

        # Small delay to avoid synchronous rate limit hits
        time.sleep(0.3)

    conn.commit()
    log.info("Tier 1 complete. Translated: %d", tracker.translated_count)


def run_batch_tier(
    client: Any,
    conn: sqlite3.Connection,
    pairs: list[tuple[ChunkRecord, str]],
    system_prompt: str,
    glossary_terms: list[GlossaryTerm],
    tracker: CostTracker,
    training_pairs_file: Path | None,
    batch_size: int,
    tier_label: str,
    verbose: bool,
) -> None:
    """
    Tier 2/3: Submit chunks in batches to the Anthropic Batch API.

    Each batch has at most batch_size requests.  Results are polled until
    complete, then streamed and written to DB incrementally.
    """
    log.info(
        "=== %s: Translating %d chunks via Batch API (batch_size=%d) ===",
        tier_label, len(pairs), batch_size,
    )

    # Filter out cache hits first
    live_pairs: list[tuple[ChunkRecord, str]] = []
    for chunk, tgt_lang in pairs:
        cache_key = make_cache_key(chunk.chunk_id, tgt_lang, chunk.content)
        cached = lookup_cache(conn, cache_key)
        if cached:
            translated_content, quality_score, terminology_score = cached
            translated_title = _extract_translated_title(
                chunk.title, translated_content, tgt_lang
            )
            save_to_db(
                conn,
                chunk=chunk,
                target_lang=tgt_lang,
                translated_title=translated_title,
                translated_content=translated_content,
                terminology_score=terminology_score,
                model_id=MODEL_ID + "+cache",
                tokens_input=0,
                tokens_output=0,
                cache_key=cache_key,
                flagged_for_review=False,
            )
            tracker.cache_hits += 1
            tracker.translated_count += 1
        else:
            live_pairs.append((chunk, tgt_lang))

    if tracker.cache_hits > 0:
        conn.commit()
        log.info("Cache hits: %d  Remaining: %d", tracker.cache_hits, len(live_pairs))

    if not live_pairs:
        log.info("All chunks served from cache. Nothing to batch.")
        return

    # Split into batches
    total_batches = (len(live_pairs) + batch_size - 1) // batch_size
    log.info("Submitting %d batches...", total_batches)

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(live_pairs))
        batch_pairs = live_pairs[start:end]

        log.info(
            "  Batch %d/%d: %d requests",
            batch_idx + 1, total_batches, len(batch_pairs),
        )

        requests = build_batch_requests(batch_pairs, system_prompt)

        # Build chunk_map for result lookup (must match custom_id format above)
        chunk_map: dict[str, tuple[ChunkRecord, str]] = {
            f"{chunk.chunk_id}__LANG__{tgt_lang}": (chunk, tgt_lang)
            for chunk, tgt_lang in batch_pairs
        }

        try:
            batch = client.messages.batches.create(requests=requests)
            batch_id: str = batch.id
            log.info("  Submitted batch %s", batch_id)

            # Poll until complete
            _poll_batch(client, batch_id)

            # Process results
            process_batch_results(
                client, batch_id, chunk_map, conn,
                glossary_terms, tracker, training_pairs_file, verbose,
            )

            log.info(
                "  Batch %d/%d done. Total translated: %d",
                batch_idx + 1, total_batches, tracker.translated_count,
            )

        except Exception as exc:
            log.error("Batch %d/%d failed: %s", batch_idx + 1, total_batches, exc)
            tracker.error_count += len(batch_pairs)
            # Continue with next batch instead of aborting entire run
            continue

    conn.commit()


# ===========================================================================
# Entry point
# ===========================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate LLCAR Diagnostica KB using Claude Haiku 4.5 Batch API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--db-path",
        default="knowledge-base/kb.db",
        help="Path to kb.db (default: knowledge-base/kb.db)",
    )
    parser.add_argument(
        "--glossary",
        default=(
            "дополнительно/полный глоссарий/полный глоссарий"
            "/automotive-glossary-5lang.json"
        ),
        help="Path to automotive-glossary-5lang.json",
    )
    parser.add_argument(
        "--brand",
        default="li_auto",
        help="Brand filter for chunks (default: li_auto)",
    )
    parser.add_argument(
        "--tier",
        choices=["1", "2", "3", "all"],
        default="all",
        help=(
            "Which tier to translate: "
            "1=titles only, 2=top-200 critical, 3=remaining, all=everything "
            "(default: all)"
        ),
    )
    parser.add_argument(
        "--target-langs",
        default="en,ru,zh",
        help="Comma-separated target languages (default: en,ru,zh). "
             "Same-as-source pairs are skipped automatically.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Requests per Batch API call (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--training-pairs",
        default=None,
        help="Path to output JSONL file for training pairs (optional)",
    )
    parser.add_argument(
        "--max-glossary-terms",
        type=int,
        default=0,
        help=(
            "Limit glossary to N most common terms in system prompt. "
            "0 = include all 3322 terms (default). "
            "Use e.g. 500 to reduce prompt caching cost significantly."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be translated with cost estimate, then exit.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging for each translation unit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        log.setLevel(logging.DEBUG)

    # --- Dependency check ---
    if not ANTHROPIC_AVAILABLE and not args.dry_run:
        log.error(
            "anthropic SDK not installed. Run:\n"
            "  pip install anthropic\n"
            "Then set ANTHROPIC_API_KEY environment variable."
        )
        sys.exit(1)

    # --- API key check ---
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and not args.dry_run:
        log.error(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Export it before running:\n"
            "  set ANTHROPIC_API_KEY=sk-ant-..."
        )
        sys.exit(1)

    # --- Resolve paths (relative to CWD or project root) ---
    project_root = Path(__file__).parent.parent.resolve()

    db_path = Path(args.db_path)
    if not db_path.is_absolute():
        db_path = project_root / db_path
    if not db_path.exists():
        log.error("kb.db not found: %s", db_path)
        sys.exit(1)

    glossary_path = Path(args.glossary)
    if not glossary_path.is_absolute():
        glossary_path = project_root / glossary_path
    if not glossary_path.exists():
        log.error("Glossary not found: %s", glossary_path)
        sys.exit(1)

    target_langs = [lang.strip() for lang in args.target_langs.split(",") if lang.strip()]
    if not target_langs:
        log.error("--target-langs must specify at least one language code.")
        sys.exit(1)

    training_pairs_file: Path | None = None
    if args.training_pairs:
        training_pairs_file = Path(args.training_pairs)
        if not training_pairs_file.is_absolute():
            training_pairs_file = project_root / training_pairs_file
        training_pairs_file.parent.mkdir(parents=True, exist_ok=True)

    log.info("DB path    : %s", db_path)
    log.info("Glossary   : %s", glossary_path)
    log.info("Brand      : %s", args.brand)
    log.info("Tier       : %s", args.tier)
    log.info("Target langs: %s", target_langs)
    log.info("Batch size : %d", args.batch_size)
    if training_pairs_file:
        log.info("Training pairs: %s", training_pairs_file)

    # --- Load glossary ---
    glossary_terms = load_glossary(glossary_path)
    prompt_terms = filter_glossary_for_prompt(glossary_terms, args.max_glossary_terms)
    glossary_xml = build_glossary_xml(prompt_terms)
    system_prompt = build_system_prompt(glossary_xml)
    system_prompt_tokens = approx_tokens(system_prompt)
    log.info(
        "System prompt: ~%d tokens (%d terms, %d chars glossary XML)",
        system_prompt_tokens, len(prompt_terms), len(glossary_xml),
    )

    # --- Open DB ---
    conn = open_db(db_path)
    ensure_translation_cache_table(conn)

    # --- Fetch untranslated pairs ---
    all_pairs = fetch_untranslated_chunks(
        conn, args.brand, target_langs, args.tier
    )

    if not all_pairs:
        log.info("Nothing to translate. Database is up to date.")
        conn.close()
        return

    # --- Dry run ---
    if args.dry_run:
        dry_run_estimate(all_pairs, system_prompt_tokens)
        conn.close()
        return

    # --- Split by tier for dispatch ---
    tier1_pairs: list[tuple[ChunkRecord, str]] = []
    tier2_pairs: list[tuple[ChunkRecord, str]] = []
    tier3_pairs: list[tuple[ChunkRecord, str]] = []

    if args.tier == "1":
        tier1_pairs = all_pairs
    elif args.tier == "2":
        tier2_pairs = all_pairs
    elif args.tier == "3":
        tier3_pairs = all_pairs
    else:
        # "all": separate by size / criticality
        for chunk, tgt_lang in all_pairs:
            if len(chunk.content) <= 300:
                tier1_pairs.append((chunk, tgt_lang))
            elif chunk.has_procedures or chunk.has_warnings:
                if len(tier2_pairs) < TIER2_LIMIT * len(target_langs):
                    tier2_pairs.append((chunk, tgt_lang))
                else:
                    tier3_pairs.append((chunk, tgt_lang))
            else:
                tier3_pairs.append((chunk, tgt_lang))

    # --- Build client ---
    client = anthropic.Anthropic(api_key=api_key)
    tracker = CostTracker()

    # --- Execute tiers ---
    try:
        if tier1_pairs:
            run_tier1_sync(
                client, conn, tier1_pairs, system_prompt,
                glossary_terms, tracker, training_pairs_file, args.verbose,
            )

        if tier2_pairs:
            run_batch_tier(
                client, conn, tier2_pairs, system_prompt,
                glossary_terms, tracker, training_pairs_file,
                args.batch_size, "TIER 2 (critical)", args.verbose,
            )

        if tier3_pairs:
            run_batch_tier(
                client, conn, tier3_pairs, system_prompt,
                glossary_terms, tracker, training_pairs_file,
                args.batch_size, "TIER 3 (bulk)", args.verbose,
            )

    finally:
        conn.close()

    # --- Final report ---
    print(tracker.report())

    if tracker.flagged_count > 0:
        log.warning(
            "%d translations flagged for human review "
            "(terminology_score < %.2f). "
            "Query: SELECT chunk_id, lang, terminology_score "
            "FROM chunk_content WHERE terminology_score < %.2f;",
            tracker.flagged_count,
            TERMINOLOGY_THRESHOLD,
            TERMINOLOGY_THRESHOLD,
        )


if __name__ == "__main__":
    main()
