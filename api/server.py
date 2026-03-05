#!/usr/bin/env python3
"""
LLCAR Diagnostica KB — FastAPI Server v2.

3-stage hybrid search over SQLite (FTS5 + ColBERT) and LanceDB (dense vectors).

Endpoints:
  GET  /health              — health check with DB stats
  POST /search              — 3-stage hybrid search
  POST /search/semantic     — dense-only search (LanceDB)
  POST /search/keyword      — keyword-only search (FTS5 BM25)
  GET  /chunk/{chunk_id}    — full chunk with metadata
  GET  /dtc/{code}          — DTC code lookup with linked chunks
  POST /glossary/search     — glossary term search
  GET  /stats               — detailed KB statistics
  POST /embed               — compute query embedding (optional, GPU required)
  GET  /parts/search        — search parts catalog by number/name/system
  GET  /parts/{part_number} — get part details by exact number
  GET  /parts/stats         — parts catalog statistics by system

Architecture:
  Stage 1: LanceDB dense (content_emb + title_emb) + FTS5 BM25 → RRF fusion → top-20
  Stage 2: ColBERT MaxSim reranking (BGE-M3 token vectors, FP16 BLOBs) on top-20
  Stage 3: Full content retrieval from SQLite + metadata enrichment

Run:
  uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from itertools import combinations
import struct
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Path as FPath, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("kb.server")


# ===========================================================================
# Configuration
# ===========================================================================

_BASE_DIR    = Path(__file__).resolve().parent.parent          # project root
_KB_DIR      = _BASE_DIR / "knowledge-base"
_DB_PATH     = _KB_DIR / "kb.db"
_LANCEDB_DIR = _KB_DIR / "lancedb"

API_HOST     = os.getenv("KB_API_HOST", "0.0.0.0")
API_PORT     = int(os.getenv("KB_API_PORT", "8000"))
FORCE_CPU    = os.getenv("FORCE_CPU_EMBED", "").strip() == "1"
SKIP_PPLX    = os.getenv("SKIP_PPLX_EMBED", "").strip() == "1"

EMBED_DIM    = 2560    # pplx-embed-v1-4B output dimension
COLBERT_DIM  = 1024    # BGE-M3 ColBERT token vector dimension

RRF_K        = 60      # RRF fusion constant (standard value)
STAGE1_LIMIT = 20      # candidates after Stage 1
MAX_LIMIT    = 100


# ===========================================================================
# Pydantic models — request / response
# ===========================================================================

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Search query text")
    brand: str = Field("li_auto", description="Vehicle brand filter")
    model: str | None = Field(None, description="Vehicle model filter: l7, l9")
    language: str | None = Field(None, description="Source language filter: ru, en, zh")
    layer: str | None = Field(None, description="Layer filter: engine, ev, body, …")
    content_type: str | None = Field(None, description="Content type filter: manual, parts")
    limit: int = Field(10, ge=1, le=MAX_LIMIT, description="Max results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")
    include_translations: bool = Field(False, description="Include translated content variants")

    @field_validator("query")
    @classmethod
    def strip_query(cls, v: str) -> str:
        return v.strip()


class GlossarySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    language: str | None = Field(None, description="Language to search: ru, en, zh")
    limit: int = Field(20, ge=1, le=100)


class EmbedRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=64)
    model: str = Field("content", description="Which model: 'content' (pplx) or 'colbert' (bge)")


class SearchResult(BaseModel):
    chunk_id: str
    title: str
    content: str
    brand: str
    model: str
    source_language: str
    layer: str
    content_type: str
    score: float
    source: str
    page_start: int
    page_end: int
    has_procedures: bool
    has_warnings: bool
    dtc_codes: list[str]
    glossary_terms: list[str]
    translations: list[dict] | None = None
    # Situation tags (from situation_tags table)
    urgency: int = 1
    situation_type: str = "learning"
    trust_level: int = 2
    season: str = "all"
    events: list[str] = []
    mileage_ranges: list[str] = []


class SearchResponse(BaseModel):
    query: str
    total: int
    offset: int
    results: list[SearchResult]
    search_mode: str
    latency_ms: float


# ===========================================================================
# ColBERT BLOB serialisation (mirrors build_embeddings.py exactly)
# ===========================================================================

def decode_colbert_blob(blob: bytes) -> np.ndarray:
    """
    Deserialise a ColBERT BLOB written by build_embeddings.py.

    Wire format:
      bytes 0-1: uint16 num_tokens (little-endian)
      bytes 2-3: uint16 dim        (little-endian)
      bytes 4+ : FP16 raw bytes, row-major, shape (num_tokens, dim)

    Returns float32 array of shape (num_tokens, dim).
    """
    num_tokens, dim = struct.unpack_from("<HH", blob, 0)
    arr = np.frombuffer(blob, dtype=np.float16, offset=4)
    return arr.reshape(num_tokens, dim).astype(np.float32)


# ===========================================================================
# RRF fusion
# ===========================================================================

def rrf_score(ranks: list[int], k: int = RRF_K) -> float:
    """Reciprocal Rank Fusion score for a document that appeared at *ranks*."""
    return sum(1.0 / (k + r) for r in ranks)


def rrf_fuse(
    result_lists: list[list[str]],
    k: int = RRF_K,
) -> list[tuple[str, float]]:
    """
    Fuse multiple ranked result lists via RRF.

    Each list in *result_lists* is an ordered sequence of chunk_ids (rank 1 = index 0).
    Returns a list of (chunk_id, rrf_score) sorted descending by score.
    """
    scores: dict[str, float] = {}
    for ranked in result_lists:
        for rank_0, chunk_id in enumerate(ranked):
            rank_1 = rank_0 + 1  # 1-based rank for the formula
            scores[chunk_id] = scores.get(chunk_id, 0.0) + rrf_score([rank_1], k)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ===========================================================================
# ColBERT MaxSim reranking
# ===========================================================================

def colbert_maxsim(query_vectors: np.ndarray, doc_vectors: np.ndarray) -> float:
    """
    Compute ColBERT MaxSim score between query and document token vectors.

    Args:
        query_vectors: float32 array (Q, dim)
        doc_vectors:   float32 array (D, dim)

    Returns:
        Scalar score: mean of per-query-token maximum similarities.
    """
    # sim_matrix[i, j] = cosine similarity between query token i and doc token j
    # (vectors are already L2-normalised from BGE-M3)
    sim_matrix = query_vectors @ doc_vectors.T  # (Q, D)
    max_per_query = sim_matrix.max(axis=1)       # (Q,)
    return float(max_per_query.mean())


# ===========================================================================
# SQLite connection management
# ===========================================================================

@contextmanager
def get_db_conn() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager yielding a WAL-mode SQLite connection with Row factory.
    Each request gets its own connection (simple, safe for async FastAPI).
    """
    conn = sqlite3.connect(str(_DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-32768")   # 32 MB page cache
    conn.execute("PRAGMA temp_store=MEMORY")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ===========================================================================
# LanceDB — lazy initialisation (graceful degradation if unavailable)
# ===========================================================================

_lancedb_db: Any | None = None
_lancedb_content_tbl: Any | None = None
_lancedb_title_tbl: Any | None = None
_lancedb_available: bool = False
_lancedb_init_attempted: bool = False


def _try_init_lancedb() -> bool:
    """
    Attempt to open the LanceDB database and both tables.

    Stores results in module-level singletons.
    Sets _lancedb_available = True if both tables are accessible.
    Safe to call multiple times (idempotent after first attempt).
    """
    global _lancedb_db, _lancedb_content_tbl, _lancedb_title_tbl
    global _lancedb_available, _lancedb_init_attempted

    if _lancedb_init_attempted:
        return _lancedb_available

    _lancedb_init_attempted = True

    if not _LANCEDB_DIR.exists():
        log.warning("LanceDB directory not found at %s — dense search disabled.", _LANCEDB_DIR)
        return False

    try:
        import lancedb  # noqa: PLC0415  (lazy import)

        log.info("Connecting to LanceDB at %s …", _LANCEDB_DIR)
        _lancedb_db = lancedb.connect(str(_LANCEDB_DIR))

        table_names = _lancedb_db.table_names()
        log.info("LanceDB tables: %s", table_names)

        if "content_emb" not in table_names:
            log.warning("LanceDB table 'content_emb' missing — dense search disabled.")
            return False

        if "title_emb" not in table_names:
            log.warning("LanceDB table 'title_emb' missing — dense search disabled.")
            return False

        _lancedb_content_tbl = _lancedb_db.open_table("content_emb")
        _lancedb_title_tbl   = _lancedb_db.open_table("title_emb")
        _lancedb_available   = True
        log.info(
            "LanceDB ready: content_emb=%d rows, title_emb=%d rows",
            _lancedb_content_tbl.count_rows(),
            _lancedb_title_tbl.count_rows(),
        )
    except Exception as exc:
        log.warning("LanceDB initialisation failed: %s — dense search disabled.", exc)
        _lancedb_available = False

    return _lancedb_available


# ===========================================================================
# Embedding models — optional, lazy-loaded for /embed endpoint
# ===========================================================================

_embed_models_loaded: bool = False
_embed_models_available: bool = False
_pplx_embedder: Any | None = None
_bge_embedder:  Any | None = None


def _select_devices() -> tuple[str, str]:
    """
    Pick devices for pplx (dense) and bge-m3 (ColBERT) models.

    Rules:
        FORCE_CPU_EMBED=1          → both on cpu
        2+ GPUs, enough VRAM       → pplx on cuda:0, bge on cuda:1
        1 GPU with ≥16 GB VRAM     → both on cuda:0
        1 GPU with <16 GB VRAM     → pplx on cpu, bge on cuda:0
        No GPU                     → both on cpu
    """
    if FORCE_CPU:
        log.info("FORCE_CPU_EMBED=1 → all models on CPU")
        return "cpu", "cpu"

    try:
        import torch as _torch  # noqa: PLC0415
        if not _torch.cuda.is_available():
            return "cpu", "cpu"
        n_gpus = _torch.cuda.device_count()
        if n_gpus >= 2:
            return "cuda:0", "cuda:1"
        vram_mb = _torch.cuda.get_device_properties(0).total_memory // (1024 * 1024)
        if vram_mb >= 16_000:
            return "cuda:0", "cuda:0"
        # <16 GB: neither model fits on GPU safely; use CPU for both
        # BGE-M3 (~1.1 GB) loads fine; pplx (~8 GB) may cause OOM on low-RAM systems
        return "cpu", "cpu"
    except Exception:
        return "cpu", "cpu"


def _try_load_embed_models() -> bool:
    """
    Load pplx-embed-v1-4B (dense) + BGE-M3 (ColBERT) for live search.

    Device assignment is auto-detected via _select_devices().
    Idempotent — safe to call multiple times.
    Returns True if at least the dense model loaded successfully.
    """
    global _embed_models_loaded, _embed_models_available, _pplx_embedder, _bge_embedder

    if _embed_models_loaded:
        return _embed_models_available

    _embed_models_loaded = True
    pplx_device, bge_device = _select_devices()
    log.info("Device plan: pplx=%s  bge=%s", pplx_device, bge_device)

    try:
        import sys  # noqa: PLC0415
        scripts_dir = str(_BASE_DIR / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)

        import build_embeddings  # noqa: PLC0415

        # Dense query encoder.
        # Try pplx-embed-v1-4b first; fall back to pplx-embed-context-v1-4b@3597c21f
        # (always cached, same 2560-d embedding space, compatible for ANN search).
        # SKIP_PPLX_EMBED=1 skips loading entirely (for low-RAM systems where 4B model causes OOM).
        if SKIP_PPLX:
            log.info("SKIP_PPLX_EMBED=1 → skipping dense query model (FTS5+ColBERT only)")
        else:
            try:
                _pplx_embedder = build_embeddings.PplxQueryEmbedder(device=pplx_device)
                _embed_models_available = True
                log.info("pplx-embed-v1-4B (dense query) loaded on %s", pplx_device)
            except Exception as exc:
                log.warning("pplx-embed-v1-4B not available (%s) — loading context model as fallback", exc)
                try:
                    _ctx = build_embeddings.PplxContextEmbedder(device=pplx_device)

                    class _ContextQueryAdapter:
                        """Wrap PplxContextEmbedder so each query is a single-chunk doc group."""
                        def __init__(self, ctx):
                            self._ctx = ctx

                        def encode(self, texts: list[str]) -> np.ndarray:
                            # model.encode takes list[list[str]]; one group per query
                            # no_grad not needed — model is in eval mode and encode() handles it
                            raw = self._ctx.model.encode([[t] for t in texts])
                            # Each element of raw is (1, 2560); take row 0
                            vecs = np.vstack([np.asarray(r, dtype=np.float32)[0:1] for r in raw])
                            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                            return vecs / np.where(norms > 0, norms, 1.0)

                    _pplx_embedder = _ContextQueryAdapter(_ctx)
                    _embed_models_available = True
                    log.info("pplx-embed-context-v1-4B (fallback query encoder) loaded on %s", pplx_device)
                except Exception as exc2:
                    log.warning("Could not load any pplx dense model: %s", exc2)

        # ColBERT encoder (BGE-M3)
        try:
            _bge_embedder = build_embeddings.BgeM3Encoder(device=bge_device)
            log.info("BGE-M3 (ColBERT query) loaded on %s", bge_device)
        except Exception as exc:
            log.warning("Could not load BGE-M3: %s — ColBERT reranking disabled", exc)

    except Exception as exc:
        log.warning("Embedding model load failed: %s", exc)
        _embed_models_available = False

    return _embed_models_available


# ===========================================================================
# FTS5 BM25 search
# ===========================================================================


def _build_fts_expr(words: list[str], mode: str = "and") -> str:
    """Build FTS5 match expression from words.
    mode='and': all words must match (precise), mode='or': any word matches (broad).
    Each word also gets a prefix variant for Russian morphology.
    """
    if not words:
        return '""'
    if len(words) == 1:
        sw = words[0].replace('"', '""')
        return f'"{sw}" OR {sw}*'
    joiner = " AND " if mode == "and" else " OR "
    parts = []
    for w in words[:8]:
        sw = w.replace('"', '""')
        # Each word: exact OR prefix (handles Russian morphology)
        parts.append(f'("{sw}" OR {sw}*)')
    return joiner.join(parts)


def fts5_search(
    conn: sqlite3.Connection,
    query: str,
    brand: str | None = None,
    model: str | None = None,
    language: str | None = None,
    layer: str | None = None,
    content_type: str | None = None,
    limit: int = STAGE1_LIMIT,
) -> list[str]:
    """
    Run FTS5 BM25 search against the chunks_fts virtual table.

    The FTS5 table is built on chunk_content (title, content) via triggers,
    so rowids in chunks_fts correspond to rowids of chunk_content rows.
    We join back through chunk_content → chunks to apply metadata filters.

    Returns ordered list of chunk_ids (best BM25 match first).
    """
    # Build the FTS match expression
    # Strategy: AND first (precise), fall back to OR (broad) if AND returns 0
    words = query.strip().split()
    fts_expr = _build_fts_expr(words, mode="and")
    _fts_or_expr = _build_fts_expr(words, mode="or")

    # Build optional WHERE clauses for metadata filters
    filters: list[str] = []
    params: list[Any] = [fts_expr]

    if brand:
        filters.append("c.brand = ?")
        params.append(brand)
    if model:
        filters.append("c.model = ?")
        params.append(model)
    if language:
        filters.append("c.source_language = ?")
        params.append(language)
    if layer:
        filters.append("c.layer = ?")
        params.append(layer)
    if content_type:
        filters.append("c.content_type = ?")
        params.append(content_type)

    where_clause = ("AND " + " AND ".join(filters)) if filters else ""

    # FTS5 rowid matches chunks.rowid (FTS built on chunks table, not chunk_content)
    sql = f"""
        SELECT c.id
        FROM chunks_fts fts
        JOIN chunks c ON c.rowid = fts.rowid
        WHERE chunks_fts MATCH ?
        {where_clause}
        ORDER BY bm25(chunks_fts)
        LIMIT ?
    """
    params.append(limit)

    def _run_fts(expr, p):
        """Run FTS5 query, return list of chunk_ids."""
        p2 = [expr] + p[1:]  # replace first param (fts_expr) with new expr
        try:
            return [row[0] for row in conn.execute(sql, p2).fetchall()]
        except sqlite3.OperationalError:
            return []

    # Strategy: AND first → any-2-of-N → OR → content_fts → LIKE
    result = _run_fts(fts_expr, params)
    if result:
        return result

    # AND returned 0 — try "at least 2 of N" (for 3+ words)
    if len(words) >= 3:
        log.debug("FTS5 AND returned 0, trying any-2-of-%d matching.", len(words))

        combined_ids = []
        seen = set()
        for combo in combinations(words, 2):
            expr2 = _build_fts_expr(list(combo), mode="and")
            ids = _run_fts(expr2, params)
            for cid in ids:
                if cid not in seen:
                    seen.add(cid)
                    combined_ids.append(cid)
        if combined_ids:
            return combined_ids[:limit]

    # Still 0 — try OR (broadest, may be noisy)
    if len(words) > 1:
        log.debug("FTS5 any-2 returned 0, trying OR matching.")
        result = _run_fts(_fts_or_expr, params)
        if result:
            return result

    # Both returned 0 — search translations
    log.debug("FTS5 chunks returned 0, trying content_fts (translations).")
    return _content_fts_search(conn, query, brand, model, language, layer, content_type, limit)


def _content_fts_search(
    conn: sqlite3.Connection,
    query: str,
    brand: str | None,
    model: str | None,
    language: str | None,
    layer: str | None,
    content_type: str | None,
    limit: int,
) -> list[str]:
    """FTS5 search on content_fts (translations table) when chunks_fts returns 0."""
    words = query.strip().split()
    if not words:
        return []
    fts_and = _build_fts_expr(words, mode="and")
    fts_or = _build_fts_expr(words, mode="or")

    filters: list[str] = []
    filter_params: list[Any] = []

    if brand:
        filters.append("c.brand = ?")
        filter_params.append(brand)
    if model:
        filters.append("c.model = ?")
        filter_params.append(model)
    if layer:
        filters.append("c.layer = ?")
        filter_params.append(layer)
    if content_type:
        filters.append("c.content_type = ?")
        filter_params.append(content_type)

    where_clause = ("AND " + " AND ".join(filters)) if filters else ""

    def _run(expr):
        params = [expr] + filter_params + [limit]
        try:
            cur = conn.execute(f"""
                SELECT DISTINCT cf.chunk_id
                FROM content_fts cf
                JOIN chunks c ON c.id = cf.chunk_id
                WHERE content_fts MATCH ?
                {where_clause}
                ORDER BY bm25(content_fts)
                LIMIT ?
            """, params)
            return [row[0] for row in cur.fetchall()]
        except sqlite3.OperationalError:
            return []

    # AND first → any-2-of-N → OR
    result = _run(fts_and)
    if result:
        return result
    if len(words) >= 3:

        combined = []
        seen = set()
        for combo in combinations(words, 2):
            expr2 = _build_fts_expr(list(combo), mode="and")
            for cid in _run(expr2):
                if cid not in seen:
                    seen.add(cid)
                    combined.append(cid)
        if combined:
            return combined[:limit]
    result = _run(fts_or)
    if result:
        return result

    return _fts_fallback(conn, query, brand, model, language, layer, content_type, limit)


def _fts_fallback(
    conn: sqlite3.Connection,
    query: str,
    brand: str | None,
    model: str | None,
    language: str | None,
    layer: str | None,
    content_type: str | None,
    limit: int,
) -> list[str]:
    """LIKE-based fallback when FTS5 query syntax fails or returns 0."""
    # Split query into words for AND-matching (each word must appear in title or content)
    words = query.strip().split()
    if not words:
        return []
    word_filters = []
    params: list[Any] = []
    for w in words[:5]:  # limit to first 5 words to avoid slow queries
        pattern = f"%{w}%"
        word_filters.append("(cc.title LIKE ? OR cc.content LIKE ?)")
        params.extend([pattern, pattern])
    filters: list[str] = [" AND ".join(word_filters)]

    if brand:
        filters.append("c.brand = ?")
        params.append(brand)
    if model:
        filters.append("c.model = ?")
        params.append(model)
    if language:
        # Filter by translation language (cc.lang), not source language
        # This finds ZH articles that have RU translations
        filters.append("cc.lang = ?")
        params.append(language)
    if layer:
        filters.append("c.layer = ?")
        params.append(layer)
    if content_type:
        filters.append("c.content_type = ?")
        params.append(content_type)

    sql = f"""
        SELECT DISTINCT cc.chunk_id
        FROM chunk_content cc
        JOIN chunks c ON c.id = cc.chunk_id
        WHERE {" AND ".join(filters)}
        LIMIT ?
    """
    params.append(limit)
    cur = conn.execute(sql, params)
    return [row[0] for row in cur.fetchall()]


# ===========================================================================
# LanceDB dense search
# ===========================================================================

def lancedb_dense_search(
    query_vector: np.ndarray,
    table: Any,
    brand: str | None = None,
    model: str | None = None,
    language: str | None = None,
    layer: str | None = None,
    content_type: str | None = None,
    limit: int = STAGE1_LIMIT,
) -> list[str]:
    """
    Run ANN dense search on a LanceDB table with optional pre-filters.

    Returns ordered list of chunk_ids (nearest neighbour first).
    The content_emb table has full metadata columns for pre-filtering.
    The title_emb table has only chunk_id + vector.
    """
    # Build pre-filter string (LanceDB SQL-style WHERE clause)
    filter_parts: list[str] = []
    if brand:
        filter_parts.append(f"brand = '{brand}'")
    if model:
        filter_parts.append(f"model = '{model}'")
    if language:
        filter_parts.append(f"source_language = '{language}'")
    if layer:
        filter_parts.append(f"layer = '{layer}'")
    if content_type:
        filter_parts.append(f"content_type = '{content_type}'")

    where_str = " AND ".join(filter_parts) if filter_parts else None

    try:
        q = table.search(query_vector).limit(limit)
        if where_str:
            q = q.where(where_str)
        results = q.to_list()
        return [r["chunk_id"] for r in results]
    except Exception as exc:
        log.warning("LanceDB dense search failed: %s", exc)
        return []


# ===========================================================================
# ColBERT Stage 2 reranking
# ===========================================================================

def rerank_with_colbert(
    conn: sqlite3.Connection,
    query_colbert: np.ndarray,
    candidate_ids: list[str],
) -> list[tuple[str, float]]:
    """
    Rerank *candidate_ids* using ColBERT MaxSim against pre-computed BLOBs.

    Chunks missing from colbert_vectors are kept at their original RRF score
    (mapped to 0.0 ColBERT score so they fall to the bottom).

    Args:
        query_colbert: float32 (Q, COLBERT_DIM) — query token vectors.
        candidate_ids: chunk_ids to rerank (up to STAGE1_LIMIT).

    Returns:
        List of (chunk_id, colbert_score) sorted descending.
    """
    if query_colbert is None or len(candidate_ids) == 0:
        return [(cid, 0.0) for cid in candidate_ids]

    # Fetch BLOBs for all candidates in one query
    placeholders = ",".join("?" * len(candidate_ids))
    sql = f"""
        SELECT chunk_id, colbert_matrix
        FROM colbert_vectors
        WHERE chunk_id IN ({placeholders})
    """
    cur = conn.execute(sql, candidate_ids)
    blob_map: dict[str, bytes] = {row[0]: row[1] for row in cur.fetchall()}

    scored: list[tuple[str, float]] = []
    for chunk_id in candidate_ids:
        blob = blob_map.get(chunk_id)
        if blob is None:
            # No ColBERT vector stored — assign neutral score
            scored.append((chunk_id, 0.0))
            continue
        try:
            doc_vecs = decode_colbert_blob(blob)    # (D, 1024) float32
            score = colbert_maxsim(query_colbert, doc_vecs)
            scored.append((chunk_id, score))
        except Exception as exc:
            log.debug("ColBERT decode/score failed for %s: %s", chunk_id, exc)
            scored.append((chunk_id, 0.0))

    return sorted(scored, key=lambda x: x[1], reverse=True)


# ===========================================================================
# Metadata enrichment helpers
# ===========================================================================

def fetch_chunks_by_ids(
    conn: sqlite3.Connection,
    chunk_ids: list[str],
) -> dict[str, sqlite3.Row]:
    """Fetch full chunk rows for given IDs, keyed by id."""
    if not chunk_ids:
        return {}
    placeholders = ",".join("?" * len(chunk_ids))
    cur = conn.execute(
        f"SELECT * FROM chunks WHERE id IN ({placeholders})",
        chunk_ids,
    )
    return {row["id"]: row for row in cur.fetchall()}


def fetch_dtc_codes(
    conn: sqlite3.Connection,
    chunk_ids: list[str],
) -> dict[str, list[str]]:
    """Fetch DTC codes for a set of chunk_ids. Returns {chunk_id: [code, …]}."""
    if not chunk_ids:
        return {}
    placeholders = ",".join("?" * len(chunk_ids))
    cur = conn.execute(
        f"SELECT chunk_id, dtc_code FROM chunk_dtc WHERE chunk_id IN ({placeholders})",
        chunk_ids,
    )
    result: dict[str, list[str]] = {cid: [] for cid in chunk_ids}
    for row in cur.fetchall():
        result[row[0]].append(row[1])
    return result


def fetch_glossary_terms(
    conn: sqlite3.Connection,
    chunk_ids: list[str],
) -> dict[str, list[str]]:
    """Fetch glossary term IDs for a set of chunk_ids. Returns {chunk_id: [id, …]}."""
    if not chunk_ids:
        return {}
    placeholders = ",".join("?" * len(chunk_ids))
    cur = conn.execute(
        f"SELECT chunk_id, glossary_id FROM chunk_glossary WHERE chunk_id IN ({placeholders})",
        chunk_ids,
    )
    result: dict[str, list[str]] = {cid: [] for cid in chunk_ids}
    for row in cur.fetchall():
        result[row[0]].append(row[1])
    return result


def fetch_situation_tags(
    conn: sqlite3.Connection,
    chunk_ids: list[str],
) -> dict[str, dict]:
    """Fetch situation tags for given chunk_ids. Returns {chunk_id: {urgency, situation_type, ...}}."""
    if not chunk_ids:
        return {}
    placeholders = ",".join("?" * len(chunk_ids))
    try:
        cur = conn.execute(
            f"""SELECT chunk_id, situation_type, urgency, trust_level, season, events, mileage_ranges
                FROM situation_tags WHERE chunk_id IN ({placeholders})""",
            chunk_ids,
        )
    except sqlite3.OperationalError:
        # Table doesn't exist yet — return empty
        return {}
    result: dict[str, dict] = {}
    for row in cur.fetchall():
        result[row[0]] = {
            "situation_type": row[1],
            "urgency": row[2],
            "trust_level": row[3],
            "season": row[4],
            "events": json.loads(row[5]) if row[5] else [],
            "mileage_ranges": json.loads(row[6]) if row[6] else [],
        }
    return result


def fetch_translations(
    conn: sqlite3.Connection,
    chunk_ids: list[str],
) -> dict[str, list[dict]]:
    """
    Fetch all content variants from chunk_content for given chunk_ids.

    Returns {chunk_id: [{lang, title, content, translated_by, quality_score}, …]}
    """
    if not chunk_ids:
        return {}
    placeholders = ",".join("?" * len(chunk_ids))
    cur = conn.execute(
        f"""SELECT chunk_id, lang, title, content, translated_by, quality_score
            FROM chunk_content
            WHERE chunk_id IN ({placeholders})""",
        chunk_ids,
    )
    result: dict[str, list[dict]] = {cid: [] for cid in chunk_ids}
    for row in cur.fetchall():
        result[row[0]].append({
            "lang": row[1],
            "title": row[2],
            "content": row[3],
            "translated_by": row[4],
            "quality_score": row[5],
        })
    return result


def build_search_result(
    chunk: sqlite3.Row,
    score: float,
    dtc_map: dict[str, list[str]],
    glossary_map: dict[str, list[str]],
    translations_map: dict[str, list[dict]] | None,
    situation_map: dict[str, dict] | None = None,
) -> SearchResult:
    """Assemble a SearchResult from row data and enrichment maps."""
    cid = chunk["id"]
    translations = translations_map.get(cid) if translations_map else None
    sit = (situation_map or {}).get(cid, {})
    return SearchResult(
        chunk_id=cid,
        title=chunk["title"] or "",
        content=chunk["content"] or "",
        brand=chunk["brand"] or "",
        model=chunk["model"] or "",
        source_language=chunk["source_language"] or "",
        layer=chunk["layer"] or "",
        content_type=chunk["content_type"] or "",
        score=round(float(score), 6),
        source=chunk["source"] or "",
        page_start=int(chunk["page_start"] or 0),
        page_end=int(chunk["page_end"] or 0),
        has_procedures=bool(chunk["has_procedures"]),
        has_warnings=bool(chunk["has_warnings"]),
        dtc_codes=dtc_map.get(cid, []),
        glossary_terms=glossary_map.get(cid, []),
        translations=translations,
        urgency=sit.get("urgency", 1),
        situation_type=sit.get("situation_type", "learning"),
        trust_level=sit.get("trust_level", 2),
        season=sit.get("season", "all"),
        events=sit.get("events", []),
        mileage_ranges=sit.get("mileage_ranges", []),
    )


# ===========================================================================
# Application
# ===========================================================================

app = FastAPI(
    title="LLCAR Diagnostica KB API",
    description=(
        "3-stage hybrid search over the LLCAR Diagnostica automotive KB. "
        "Stage 1: LanceDB dense + FTS5 BM25 → RRF fusion. "
        "Stage 2: ColBERT MaxSim reranking. "
        "Stage 3: Full content retrieval."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",   # Vite dev server
        "*",                       # Allow all for MVP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static files — serve parts catalog images from mineru-output
# ---------------------------------------------------------------------------
_images_dir = _BASE_DIR / "mineru-output" / "941362155-2022-2023款理想L9零件手册" / "ocr" / "images"
if _images_dir.is_dir():
    app.mount("/images", StaticFiles(directory=str(_images_dir)), name="parts-images")
    log.info("Mounted /images → %s", _images_dir)


# ---------------------------------------------------------------------------
# Request timing middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
    log.info("%s %s  %.1f ms", request.method, request.url.path, elapsed_ms)
    return response


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    log.info("=" * 60)
    log.info("  LLCAR Diagnostica KB API v2.0 starting up")
    log.info("  DB: %s", _DB_PATH)
    log.info("  LanceDB: %s", _LANCEDB_DIR)
    log.info("=" * 60)

    if not _DB_PATH.exists():
        log.error("kb.db NOT FOUND at %s — run build_kb.py first!", _DB_PATH)
    else:
        log.info("kb.db found — OK")

    # Attempt LanceDB init (non-fatal)
    _try_init_lancedb()

    if _lancedb_available:
        log.info("LanceDB: AVAILABLE (dense search enabled)")
    else:
        log.info("LanceDB: NOT AVAILABLE (keyword-only fallback active)")

    # Load embedding models in background so server is immediately available.
    # hybrid_search degrades to keyword-only until models finish loading.
    import asyncio  # noqa: PLC0415
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _try_load_embed_models)
    log.info("Embedding models loading in background …")


# ===========================================================================
# Endpoint: GET /health
# ===========================================================================

@app.get("/health", summary="Health check with DB statistics")
async def health() -> dict:
    """
    Returns server health status and basic KB statistics.
    Always responds with HTTP 200; `status` field indicates actual health.
    """
    status = "ok"
    detail: dict[str, Any] = {}

    if not _DB_PATH.exists():
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "detail": f"kb.db not found at {_DB_PATH}",
                "lancedb_available": False,
            },
        )

    try:
        with get_db_conn() as conn:
            detail["chunks_total"]   = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            detail["dtc_links"]      = conn.execute("SELECT COUNT(*) FROM chunk_dtc").fetchone()[0]
            detail["glossary_links"] = conn.execute("SELECT COUNT(*) FROM chunk_glossary").fetchone()[0]
            detail["colbert_rows"]   = conn.execute("SELECT COUNT(*) FROM colbert_vectors").fetchone()[0]
            detail["content_rows"]   = conn.execute("SELECT COUNT(*) FROM chunk_content").fetchone()[0]

            # Read kb_meta
            meta_rows = conn.execute("SELECT key, value FROM kb_meta").fetchall()
            detail["kb_meta"] = {r[0]: r[1] for r in meta_rows}
    except Exception as exc:
        status = "error"
        detail["db_error"] = str(exc)

    return {
        "status": status,
        "lancedb_available": _lancedb_available,
        "embed_models_available": _embed_models_available,
        "db_path": str(_DB_PATH),
        **detail,
    }


# ===========================================================================
# Endpoint: GET /stats
# ===========================================================================

@app.get("/stats", summary="Detailed KB statistics")
async def stats() -> dict:
    """Detailed statistics broken down by brand, model, language, layer, content_type."""
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found — run build_kb.py first")

    with get_db_conn() as conn:
        def _counts(col: str) -> dict[str, int]:
            rows = conn.execute(
                f"SELECT {col}, COUNT(*) as cnt FROM chunks GROUP BY {col} ORDER BY cnt DESC"
            ).fetchall()
            return {r[0]: r[1] for r in rows}

        total = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        colbert_count = conn.execute("SELECT COUNT(*) FROM colbert_vectors").fetchone()[0]
        fts_count = conn.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0]
        content_count = conn.execute("SELECT COUNT(*) FROM chunk_content").fetchone()[0]

        by_brand        = _counts("brand")
        by_model        = _counts("model")
        by_language     = _counts("source_language")
        by_layer        = _counts("layer")
        by_content_type = _counts("content_type")

        meta_rows = conn.execute("SELECT key, value FROM kb_meta").fetchall()
        kb_meta = {r[0]: r[1] for r in meta_rows}

    return {
        "total_chunks": total,
        "fts5_indexed": fts_count,
        "colbert_vectors": colbert_count,
        "content_translations": content_count,
        "by_brand": by_brand,
        "by_model": by_model,
        "by_language": by_language,
        "by_layer": by_layer,
        "by_content_type": by_content_type,
        "lancedb_available": _lancedb_available,
        "embed_dim": EMBED_DIM,
        "colbert_dim": COLBERT_DIM,
        "kb_meta": kb_meta,
    }


# ===========================================================================
# Endpoint: POST /search  (3-stage hybrid)
# ===========================================================================

@app.post("/search", response_model=SearchResponse, summary="3-stage hybrid search")
async def hybrid_search(req: SearchRequest) -> SearchResponse:
    """
    Full 3-stage hybrid search.

    Stage 1: LanceDB dense (content_emb + title_emb) + FTS5 BM25 → RRF fusion → top-20.
    Stage 2: ColBERT MaxSim reranking on top-20 (if ColBERT vectors available).
    Stage 3: Full content retrieval from SQLite + metadata enrichment.

    Gracefully degrades to keyword-only if LanceDB is unavailable.
    Gracefully degrades to RRF-only if ColBERT BLOBs are absent.
    """
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found — run build_kb.py first")

    t0 = time.perf_counter()
    search_mode = "hybrid"

    # Determine Stage 1 candidates pool (fetch more than limit to allow offset)
    stage1_n = max(STAGE1_LIMIT, req.limit + req.offset)

    with get_db_conn() as conn:

        # ---- Stage 1A: FTS5 BM25 ----
        fts_ids = fts5_search(
            conn,
            query=req.query,
            brand=req.brand,
            model=req.model,
            language=req.language,
            layer=req.layer,
            content_type=req.content_type,
            limit=stage1_n,
        )

        # ---- Stage 1B+1C: LanceDB dense ----
        dense_content_ids: list[str] = []
        dense_title_ids:   list[str] = []
        query_colbert_np:  np.ndarray | None = None

        if _lancedb_available and _embed_models_available and _pplx_embedder is not None:
            try:
                vec = _pplx_embedder.encode([req.query])[0]           # (2560,) float32
                dense_content_ids = lancedb_dense_search(
                    vec,
                    table=_lancedb_content_tbl,
                    brand=req.brand,
                    model=req.model,
                    language=req.language,
                    layer=req.layer,
                    content_type=req.content_type,
                    limit=stage1_n,
                )
                dense_title_ids = lancedb_dense_search(
                    vec,
                    table=_lancedb_title_tbl,
                    limit=stage1_n,
                )
                search_mode = "hybrid_rrf"

                # ColBERT query vector for Stage 2
                if _bge_embedder is not None:
                    colbert_mats = _bge_embedder.encode_colbert([req.query])
                    if colbert_mats:
                        query_colbert_np = colbert_mats[0]  # (T, 1024) float32

            except Exception as exc:
                log.exception("Dense embedding failed — keyword fallback")
                search_mode = "keyword_only"
        elif _lancedb_available:
            search_mode = "keyword_only_no_query_vector"
            # Still try ColBERT query encoding if BGE-M3 is available (for reranking FTS results)
            if _bge_embedder is not None:
                try:
                    colbert_mats = _bge_embedder.encode_colbert([req.query])
                    if colbert_mats:
                        query_colbert_np = colbert_mats[0]
                except Exception:
                    pass
        else:
            search_mode = "keyword_only"

        # ---- Stage 1 RRF fusion ----
        result_lists: list[list[str]] = [lst for lst in [fts_ids, dense_content_ids, dense_title_ids] if lst]
        fused = rrf_fuse(result_lists)                           # [(chunk_id, rrf_score)]
        candidate_ids = [cid for cid, _ in fused[:stage1_n]]

        # ---- Stage 2: ColBERT MaxSim reranking ----
        colbert_available = conn.execute(
            "SELECT COUNT(*) FROM colbert_vectors LIMIT 1"
        ).fetchone()[0] > 0

        if query_colbert_np is not None and colbert_available:
            reranked = rerank_with_colbert(conn, query_colbert_np, candidate_ids)
            search_mode = "hybrid_colbert"

            rrf_map = {cid: s for cid, s in fused}
            final_ranked: list[tuple[str, float]] = []
            for chunk_id, colbert_s in reranked:
                rrf_s = rrf_map.get(chunk_id, 0.0)
                blended = 0.7 * colbert_s + 0.3 * (rrf_s / (rrf_s + 1.0))
                final_ranked.append((chunk_id, blended))
            final_ranked.sort(key=lambda x: x[1], reverse=True)
        else:
            final_ranked = [(cid, score) for cid, score in fused]

        # Apply pagination
        page = final_ranked[req.offset : req.offset + req.limit]
        page_ids = [cid for cid, _ in page]
        score_map = {cid: score for cid, score in page}

        if not page_ids:
            return SearchResponse(
                query=req.query,
                total=0,
                offset=req.offset,
                results=[],
                search_mode=search_mode,
                latency_ms=round((time.perf_counter() - t0) * 1000, 2),
            )

        # ---- Stage 3: Full content + metadata ----
        chunk_map  = fetch_chunks_by_ids(conn, page_ids)
        dtc_map    = fetch_dtc_codes(conn, page_ids)
        gloss_map  = fetch_glossary_terms(conn, page_ids)
        trans_map  = fetch_translations(conn, page_ids) if req.include_translations else None
        sit_map    = fetch_situation_tags(conn, page_ids)

        results: list[SearchResult] = []
        for chunk_id, score in page:
            chunk = chunk_map.get(chunk_id)
            if chunk is None:
                continue
            results.append(
                build_search_result(chunk, score, dtc_map, gloss_map, trans_map, sit_map)
            )

    return SearchResponse(
        query=req.query,
        total=len(fused),
        offset=req.offset,
        results=results,
        search_mode=search_mode,
        latency_ms=round((time.perf_counter() - t0) * 1000, 2),
    )


# ===========================================================================
# Endpoint: POST /search/semantic  (dense-only)
# ===========================================================================

@app.post("/search/semantic", response_model=SearchResponse, summary="Dense vector search only")
async def semantic_search(req: SearchRequest) -> SearchResponse:
    """
    Dense-only search via LanceDB (content_emb + title_emb).

    Requires LanceDB to be available and a query vector to be provided.
    In MVP mode (no live embedding), returns 503 if LanceDB is unavailable.

    Currently operates in content_emb + title_emb RRF fusion mode.
    Query vectorisation requires the /embed endpoint to be called first,
    or embedding models to be loaded at server startup.
    """
    if not _lancedb_available:
        raise HTTPException(
            503,
            detail={
                "error": "LanceDB not available",
                "hint": (
                    "Run build_embeddings.py to populate LanceDB, "
                    "then restart the server."
                ),
            },
        )

    if not (_embed_models_available and _pplx_embedder is not None):
        raise HTTPException(
            503,
            detail={
                "error": "Query embedding models not loaded yet",
                "hint": "Wait a moment after server start for models to load, then retry.",
            },
        )

    t0 = time.perf_counter()
    stage1_n = max(STAGE1_LIMIT, req.limit + req.offset)

    try:
        vec = _pplx_embedder.encode([req.query])[0]
    except Exception as exc:
        log.exception("Semantic search — embedding failed")
        raise HTTPException(500, detail={"error": f"Embedding failed: {exc}"})

    dense_content_ids = lancedb_dense_search(
        vec,
        table=_lancedb_content_tbl,
        brand=req.brand,
        model=req.model,
        language=req.language,
        layer=req.layer,
        content_type=req.content_type,
        limit=stage1_n,
    )
    dense_title_ids = lancedb_dense_search(
        vec,
        table=_lancedb_title_tbl,
        limit=stage1_n,
    )

    result_lists = [lst for lst in [dense_content_ids, dense_title_ids] if lst]
    fused = rrf_fuse(result_lists) if result_lists else []
    page = fused[req.offset : req.offset + req.limit]
    page_ids = [cid for cid, _ in page]

    if not page_ids:
        return SearchResponse(
            query=req.query,
            total=0,
            offset=req.offset,
            results=[],
            search_mode="dense_only",
            latency_ms=round((time.perf_counter() - t0) * 1000, 2),
        )

    with get_db_conn() as conn:
        chunk_map  = fetch_chunks_by_ids(conn, page_ids)
        dtc_map    = fetch_dtc_codes(conn, page_ids)
        gloss_map  = fetch_glossary_terms(conn, page_ids)
        trans_map  = fetch_translations(conn, page_ids) if req.include_translations else None
        sit_map    = fetch_situation_tags(conn, page_ids)

    results: list[SearchResult] = []
    for chunk_id, score in page:
        chunk = chunk_map.get(chunk_id)
        if chunk is None:
            continue
        results.append(build_search_result(chunk, score, dtc_map, gloss_map, trans_map, sit_map))

    return SearchResponse(
        query=req.query,
        total=len(fused),
        offset=req.offset,
        results=results,
        search_mode="dense_only",
        latency_ms=round((time.perf_counter() - t0) * 1000, 2),
    )


# ===========================================================================
# Endpoint: POST /search/keyword  (FTS5 BM25 only)
# ===========================================================================

@app.post("/search/keyword", response_model=SearchResponse, summary="Keyword BM25 search only")
async def keyword_search(req: SearchRequest) -> SearchResponse:
    """
    Keyword-only search using SQLite FTS5 BM25.

    No GPU required. Works immediately after build_kb.py.
    Best for exact term matching and diagnostic code queries.
    """
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found — run build_kb.py first")

    t0 = time.perf_counter()
    stage1_n = max(STAGE1_LIMIT, req.limit + req.offset)

    with get_db_conn() as conn:
        fts_ids = fts5_search(
            conn,
            query=req.query,
            brand=req.brand,
            model=req.model,
            language=req.language,
            layer=req.layer,
            content_type=req.content_type,
            limit=stage1_n,
        )

        total = len(fts_ids)
        page_ids = fts_ids[req.offset : req.offset + req.limit]

        if not page_ids:
            return SearchResponse(
                query=req.query,
                total=total,
                offset=req.offset,
                results=[],
                search_mode="keyword_bm25",
                latency_ms=round((time.perf_counter() - t0) * 1000, 2),
            )

        # Score: descending BM25 rank (1.0 for rank 1, 1/2 for rank 2, …)
        # We use the RRF formula for a single list to produce a meaningful score.
        score_map = {cid: rrf_score([i + 1]) for i, cid in enumerate(fts_ids)}

        chunk_map = fetch_chunks_by_ids(conn, page_ids)
        dtc_map   = fetch_dtc_codes(conn, page_ids)
        gloss_map = fetch_glossary_terms(conn, page_ids)
        trans_map = fetch_translations(conn, page_ids) if req.include_translations else None
        sit_map   = fetch_situation_tags(conn, page_ids)

        results: list[SearchResult] = []
        for chunk_id in page_ids:
            chunk = chunk_map.get(chunk_id)
            if chunk is None:
                continue
            results.append(
                build_search_result(
                    chunk, score_map.get(chunk_id, 0.0), dtc_map, gloss_map, trans_map, sit_map
                )
            )

    return SearchResponse(
        query=req.query,
        total=total,
        offset=req.offset,
        results=results,
        search_mode="keyword_bm25",
        latency_ms=round((time.perf_counter() - t0) * 1000, 2),
    )


# ===========================================================================
# Endpoint: GET /browse  — list articles by layer without text search
# ===========================================================================

@app.get("/browse", summary="Browse articles by layer/model without text search")
async def browse_articles(
    layer: str | None = None,
    model: str | None = None,
    content_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    include_translations: bool = False,
) -> dict:
    """Return articles filtered by layer/model, ordered by urgency desc + trust desc."""
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found")

    with get_db_conn() as conn:
        filters: list[str] = []
        params: list = []

        if layer:
            filters.append("c.layer = ?")
            params.append(layer)
        if model:
            filters.append("c.model = ?")
            params.append(model)
        if content_type:
            filters.append("c.content_type = ?")
            params.append(content_type)

        where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

        # Count total
        total = conn.execute(
            f"SELECT COUNT(*) FROM chunks c {where_clause}", params
        ).fetchone()[0]

        # Fetch IDs ordered by urgency (from situation_tags) then trust
        sql = f"""
            SELECT c.id
            FROM chunks c
            LEFT JOIN situation_tags st ON st.chunk_id = c.id
            {where_clause}
            ORDER BY COALESCE(st.urgency, 1) DESC, COALESCE(st.trust_level, 2) DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        chunk_ids = [row[0] for row in conn.execute(sql, params).fetchall()]

        if not chunk_ids:
            return {"total": total, "results": [], "offset": offset}

        chunk_map = fetch_chunks_by_ids(conn, chunk_ids)
        dtc_map = fetch_dtc_codes(conn, chunk_ids)
        gloss_map = fetch_glossary_terms(conn, chunk_ids)
        trans_map = fetch_translations(conn, chunk_ids) if include_translations else None
        sit_map = fetch_situation_tags(conn, chunk_ids)

        results = []
        for cid in chunk_ids:
            chunk = chunk_map.get(cid)
            if chunk is None:
                continue
            results.append(
                build_search_result(chunk, 0.0, dtc_map, gloss_map, trans_map, sit_map)
            )

    return {"total": total, "results": results, "offset": offset}


# ===========================================================================
# Endpoint: GET /chunk/{chunk_id}
# ===========================================================================

@app.get("/chunk/{chunk_id}", summary="Retrieve a single chunk with full metadata")
async def get_chunk(
    chunk_id: str = FPath(..., description="Chunk ID (e.g. li_auto_l9_ru_0bcefc06)"),
    include_translations: bool = False,
) -> dict:
    """
    Retrieve a chunk by its ID with full metadata including DTC codes,
    glossary term links, and optional translations.
    """
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found")

    with get_db_conn() as conn:
        row = conn.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,)).fetchone()
        if row is None:
            raise HTTPException(404, f"Chunk not found: {chunk_id}")

        dtc_codes = conn.execute(
            "SELECT dtc_code FROM chunk_dtc WHERE chunk_id = ? ORDER BY dtc_code",
            (chunk_id,),
        ).fetchall()

        glossary_ids = conn.execute(
            "SELECT glossary_id FROM chunk_glossary WHERE chunk_id = ? ORDER BY glossary_id",
            (chunk_id,),
        ).fetchall()

        images = conn.execute(
            "SELECT image_path, thumbnail_path, caption, page_idx FROM chunk_images WHERE chunk_id = ?",
            (chunk_id,),
        ).fetchall()

        # Situation tags
        sit_row = conn.execute(
            "SELECT situation_type, urgency, trust_level, season, events, mileage_ranges FROM situation_tags WHERE chunk_id = ?",
            (chunk_id,),
        ).fetchone()
        sit = {}
        if sit_row:
            sit = {
                "situation_type": sit_row[0], "urgency": sit_row[1], "trust_level": sit_row[2],
                "season": sit_row[3], "events": json.loads(sit_row[4]) if sit_row[4] else [],
                "mileage_ranges": json.loads(sit_row[5]) if sit_row[5] else [],
            }

        translations: list[dict] = []
        if include_translations:
            trans_rows = conn.execute(
                """SELECT lang, title, content, translated_by, quality_score, terminology_score
                   FROM chunk_content WHERE chunk_id = ? ORDER BY lang""",
                (chunk_id,),
            ).fetchall()
            translations = [
                {
                    "lang": r[0],
                    "title": r[1],
                    "content": r[2],
                    "translated_by": r[3],
                    "quality_score": r[4],
                    "terminology_score": r[5],
                }
                for r in trans_rows
            ]
        else:
            # Always include original language content
            orig = conn.execute(
                "SELECT lang, title, content, translated_by FROM chunk_content WHERE chunk_id = ?",
                (chunk_id,),
            ).fetchone()
            if orig:
                translations = [
                    {"lang": orig[0], "title": orig[1], "content": orig[2], "translated_by": orig[3]}
                ]

    return {
        "chunk_id":         row["id"],
        "brand":            row["brand"],
        "model":            row["model"],
        "source_language":  row["source_language"],
        "layer":            row["layer"],
        "content_type":     row["content_type"],
        "title":            row["title"],
        "content":          row["content"],
        "source":           row["source"],
        "source_url":       row["source_url"],
        "page_start":       row["page_start"],
        "page_end":         row["page_end"],
        "has_procedures":   bool(row["has_procedures"]),
        "has_warnings":     bool(row["has_warnings"]),
        "is_current":       bool(row["is_current"]),
        "edition_year":     row["edition_year"],
        "manual_version":   row["manual_version"],
        "ocr_tool":         row["ocr_tool"],
        "created_at":       row["created_at"],
        "updated_at":       row["updated_at"],
        "dtc_codes":        [r[0] for r in dtc_codes],
        "glossary_terms":   [r[0] for r in glossary_ids],
        "images":           [
            {
                "image_path": r[0],
                "thumbnail_path": r[1],
                "caption": r[2],
                "page_idx": r[3],
            }
            for r in images
        ],
        "translations":     translations,
        "urgency":          sit.get("urgency", 1),
        "situation_type":   sit.get("situation_type", "learning"),
        "trust_level":      sit.get("trust_level", 2),
        "season":           sit.get("season", "all"),
        "events":           sit.get("events", []),
        "mileage_ranges":   sit.get("mileage_ranges", []),
    }


# ===========================================================================
# Endpoint: GET /dtc/{code}
# ===========================================================================

@app.get("/dtc/{code}", summary="DTC code lookup with linked chunks")
async def get_dtc(
    code: str = FPath(..., description="DTC code, e.g. P0010 or p0010"),
    brand: str = "li_auto",
    limit: int = 20,
    include_translations: bool = False,
) -> dict:
    """
    Look up a Diagnostic Trouble Code (DTC) and return all KB chunks that
    reference it.

    The code is normalised to uppercase. Partial prefix search is supported
    for codes ending in '*' (e.g. P001*).
    """
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found")

    code_upper = code.strip().upper()
    t0 = time.perf_counter()

    with get_db_conn() as conn:

        # Exact or prefix search
        if code_upper.endswith("*"):
            prefix = code_upper[:-1]
            rows = conn.execute(
                """SELECT DISTINCT cd.chunk_id
                   FROM chunk_dtc cd
                   JOIN chunks c ON c.id = cd.chunk_id
                   WHERE cd.dtc_code LIKE ?
                     AND c.brand = ?
                   LIMIT ?""",
                (prefix + "%", brand, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT DISTINCT cd.chunk_id
                   FROM chunk_dtc cd
                   JOIN chunks c ON c.id = cd.chunk_id
                   WHERE cd.dtc_code = ?
                     AND c.brand = ?
                   LIMIT ?""",
                (code_upper, brand, limit),
            ).fetchall()

        chunk_ids = [r[0] for r in rows]
        total = len(chunk_ids)

        if not chunk_ids:
            # Fall back to FTS keyword search for the code string
            fts_ids = fts5_search(conn, query=code_upper, brand=brand, limit=limit)
            chunk_ids = fts_ids
            search_mode = "fts_fallback"
        else:
            search_mode = "exact_dtc_link"

        chunk_map = fetch_chunks_by_ids(conn, chunk_ids)
        dtc_map   = fetch_dtc_codes(conn, chunk_ids)
        gloss_map = fetch_glossary_terms(conn, chunk_ids)
        trans_map = fetch_translations(conn, chunk_ids) if include_translations else None
        sit_map   = fetch_situation_tags(conn, chunk_ids)

        results = [
            build_search_result(chunk_map[cid], 1.0, dtc_map, gloss_map, trans_map, sit_map)
            for cid in chunk_ids
            if cid in chunk_map
        ]

    return {
        "code": code_upper,
        "brand": brand,
        "total": total,
        "search_mode": search_mode,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        "chunks": [r.model_dump() for r in results],
    }


# ===========================================================================
# Endpoint: POST /glossary/search
# ===========================================================================

@app.post("/glossary/search", summary="Search glossary term links in the KB")
async def glossary_search(req: GlossarySearchRequest) -> dict:
    """
    Search for KB chunks associated with a glossary term ID or term string.

    Two modes:
    1. If query looks like a glossary ID (contains '@' or '_'), do an exact
       match against chunk_glossary.glossary_id.
    2. Otherwise do a LIKE prefix search on glossary_id.

    Also returns which chunks have the matching glossary links.
    """
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found")

    t0 = time.perf_counter()
    query = req.query.strip()

    with get_db_conn() as conn:
        # Strategy 1: exact ID match
        rows = conn.execute(
            """SELECT cg.chunk_id, cg.glossary_id
               FROM chunk_glossary cg
               JOIN chunks c ON c.id = cg.chunk_id
               WHERE cg.glossary_id = ?
               LIMIT ?""",
            (query, req.limit),
        ).fetchall()

        if not rows:
            # Strategy 2: prefix / LIKE match
            rows = conn.execute(
                """SELECT cg.chunk_id, cg.glossary_id
                   FROM chunk_glossary cg
                   JOIN chunks c ON c.id = cg.chunk_id
                   WHERE cg.glossary_id LIKE ?
                   LIMIT ?""",
                (f"%{query}%", req.limit),
            ).fetchall()

        chunk_ids = list({r[0] for r in rows})
        glossary_links: dict[str, list[str]] = {}
        for chunk_id, gid in rows:
            glossary_links.setdefault(chunk_id, []).append(gid)

        chunk_map = fetch_chunks_by_ids(conn, chunk_ids)
        dtc_map   = fetch_dtc_codes(conn, chunk_ids)
        trans_map = fetch_translations(conn, chunk_ids)
        gloss_map = fetch_glossary_terms(conn, chunk_ids)

        results = []
        for chunk_id in chunk_ids:
            chunk = chunk_map.get(chunk_id)
            if chunk is None:
                continue
            results.append({
                "chunk_id":      chunk["id"],
                "title":         chunk["title"],
                "content":       chunk["content"],
                "source":        chunk["source"],
                "brand":         chunk["brand"],
                "model":         chunk["model"],
                "layer":         chunk["layer"],
                "content_type":  chunk["content_type"],
                "source_language": chunk["source_language"],
                "page_start":    chunk["page_start"],
                "glossary_ids":  glossary_links.get(chunk_id, []),
                "glossary_terms": gloss_map.get(chunk_id, []),
                "dtc_codes":     dtc_map.get(chunk_id, []),
                "translations":  trans_map.get(chunk_id, []),
                "has_procedures": bool(chunk["has_procedures"]),
                "has_warnings":  bool(chunk["has_warnings"]),
            })

    # Collect all unique matched glossary IDs for the response header
    all_matched_ids = sorted({r[1] for r in rows})

    return {
        "query": query,
        "matched_glossary_ids": all_matched_ids,
        "total_chunks": len(results),
        "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        "chunks": results,
    }


# ===========================================================================
# Endpoint: POST /embed  (optional — returns 503 if models not loaded)
# ===========================================================================

@app.post("/embed", summary="Compute query embeddings (requires GPU + models)")
async def embed(req: EmbedRequest) -> dict:
    """
    Compute dense embeddings for input texts using pplx-embed-v1-4B.

    This endpoint is optional — it returns HTTP 503 if the embedding models
    are not loaded (MVP mode without live inference).

    When available, the returned vectors can be used directly with the
    LanceDB tables for semantic search.

    Args:
        texts: List of strings to embed (max 64).
        model: 'content' for pplx-embed-v1-4B (2560d), 'colbert' for BGE-M3 (planned).
    """
    if not _try_load_embed_models():
        raise HTTPException(
            503,
            detail={
                "error": "Embedding models not available",
                "hint": (
                    "Ensure CUDA is available and pplx-embed-v1-4B is cached. "
                    "The model will be loaded on first call to this endpoint. "
                    "Check server logs for load errors."
                ),
            },
        )

    if req.model != "content":
        raise HTTPException(
            400,
            detail={
                "error": f"Model '{req.model}' not supported via /embed",
                "supported": ["content"],
            },
        )

    t0 = time.perf_counter()

    if _pplx_embedder is None:
        raise HTTPException(503, "pplx embedder is None despite successful init — restart server")

    try:
        vectors: np.ndarray = _pplx_embedder.encode(req.texts, batch_size=8, desc="api/embed")
    except Exception as exc:
        log.error("Embedding failed: %s", exc, exc_info=True)
        raise HTTPException(500, f"Embedding failed: {exc}") from exc

    return {
        "model": "pplx-embed-v1-4B",
        "dim": int(vectors.shape[1]),
        "count": int(vectors.shape[0]),
        "vectors": vectors.tolist(),
        "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
    }


# ===========================================================================
# Endpoint: POST /search/hybrid_with_vector  (full 3-stage with client vector)
# ===========================================================================

class VectorSearchRequest(BaseModel):
    """Extended search request that accepts a pre-computed query vector."""
    query: str = Field(..., min_length=1, max_length=2000)
    query_vector: list[float] = Field(
        ...,
        description=f"Pre-computed query embedding, dim={EMBED_DIM}",
    )
    query_colbert: list[list[float]] | None = Field(
        None,
        description=f"Pre-computed ColBERT token vectors, shape (Q, {COLBERT_DIM})",
    )
    brand: str = Field("li_auto")
    model: str | None = None
    language: str | None = None
    layer: str | None = None
    content_type: str | None = None
    limit: int = Field(10, ge=1, le=MAX_LIMIT)
    offset: int = Field(0, ge=0)
    include_translations: bool = False

    @field_validator("query_vector")
    @classmethod
    def validate_vector_dim(cls, v: list[float]) -> list[float]:
        if len(v) != EMBED_DIM:
            raise ValueError(f"query_vector must have {EMBED_DIM} dimensions, got {len(v)}")
        return v


@app.post(
    "/search/vector",
    response_model=SearchResponse,
    summary="Full 3-stage hybrid search with client-provided query vector",
)
async def vector_search(req: VectorSearchRequest) -> SearchResponse:
    """
    Full 3-stage hybrid search using a pre-computed query vector.

    Use this endpoint when you have already called /embed to get the query
    vector, or when you compute embeddings client-side.

    Stages:
    1. LanceDB dense (content_emb + title_emb) + FTS5 BM25 → RRF → top-20
    2. ColBERT MaxSim reranking (if query_colbert provided)
    3. Full content from SQLite
    """
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found — run build_kb.py first")

    if not _lancedb_available:
        raise HTTPException(
            503,
            detail={
                "error": "LanceDB not available",
                "hint": "Use POST /search (keyword fallback) or run build_embeddings.py.",
            },
        )

    t0 = time.perf_counter()
    query_vec = np.array(req.query_vector, dtype=np.float32)

    # Normalise (in case client sent non-normalised vector)
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm

    stage1_n = max(STAGE1_LIMIT, req.limit + req.offset)

    with get_db_conn() as conn:

        # ---- Stage 1A: FTS5 ----
        fts_ids = fts5_search(
            conn,
            query=req.query,
            brand=req.brand,
            model=req.model,
            language=req.language,
            layer=req.layer,
            content_type=req.content_type,
            limit=stage1_n,
        )

        # ---- Stage 1B: LanceDB content_emb ----
        dense_content_ids = lancedb_dense_search(
            query_vec,
            table=_lancedb_content_tbl,
            brand=req.brand,
            model=req.model,
            language=req.language,
            layer=req.layer,
            content_type=req.content_type,
            limit=stage1_n,
        )

        # ---- Stage 1C: LanceDB title_emb (title-only vectors) ----
        dense_title_ids = lancedb_dense_search(
            query_vec,
            table=_lancedb_title_tbl,
            limit=stage1_n,
        )

        # ---- Stage 1 RRF fusion ----
        result_lists = [fts_ids, dense_content_ids, dense_title_ids]
        result_lists = [lst for lst in result_lists if lst]  # drop empty
        fused = rrf_fuse(result_lists)
        candidate_ids = [cid for cid, _ in fused[:stage1_n]]

        # ---- Stage 2: ColBERT MaxSim reranking ----
        search_mode = "hybrid_vector_rrf"
        query_colbert_np: np.ndarray | None = None

        if req.query_colbert is not None:
            query_colbert_np = np.array(req.query_colbert, dtype=np.float32)
            if query_colbert_np.shape[1] != COLBERT_DIM:
                raise HTTPException(
                    400,
                    f"query_colbert dim {query_colbert_np.shape[1]} != {COLBERT_DIM}",
                )

        colbert_available = conn.execute(
            "SELECT COUNT(*) FROM colbert_vectors LIMIT 1"
        ).fetchone()[0] > 0

        if query_colbert_np is not None and colbert_available:
            reranked = rerank_with_colbert(conn, query_colbert_np, candidate_ids)
            search_mode = "hybrid_vector_colbert"

            # Blend RRF score (for tie-breaking) with ColBERT score
            rrf_map = {cid: s for cid, s in fused}
            final_ranked: list[tuple[str, float]] = []
            for chunk_id, colbert_s in reranked:
                rrf_s = rrf_map.get(chunk_id, 0.0)
                # Weighted blend: 70% ColBERT + 30% RRF (normalised to [0,1])
                blended = 0.7 * colbert_s + 0.3 * (rrf_s / (rrf_s + 1.0))
                final_ranked.append((chunk_id, blended))
            final_ranked.sort(key=lambda x: x[1], reverse=True)
        else:
            final_ranked = fused

        # ---- Pagination ----
        page = final_ranked[req.offset : req.offset + req.limit]
        page_ids = [cid for cid, _ in page]
        score_map = {cid: score for cid, score in page}

        if not page_ids:
            return SearchResponse(
                query=req.query,
                total=0,
                offset=req.offset,
                results=[],
                search_mode=search_mode,
                latency_ms=round((time.perf_counter() - t0) * 1000, 2),
            )

        # ---- Stage 3: Full content retrieval ----
        chunk_map = fetch_chunks_by_ids(conn, page_ids)
        dtc_map   = fetch_dtc_codes(conn, page_ids)
        gloss_map = fetch_glossary_terms(conn, page_ids)
        trans_map = fetch_translations(conn, page_ids) if req.include_translations else None
        sit_map   = fetch_situation_tags(conn, page_ids)

        results: list[SearchResult] = []
        for chunk_id, score in page:
            chunk = chunk_map.get(chunk_id)
            if chunk is None:
                continue
            results.append(build_search_result(chunk, score, dtc_map, gloss_map, trans_map, sit_map))

    return SearchResponse(
        query=req.query,
        total=len(final_ranked),
        offset=req.offset,
        results=results,
        search_mode=search_mode,
        latency_ms=round((time.perf_counter() - t0) * 1000, 2),
    )


# ===========================================================================
# Endpoint: GET /chunk/{chunk_id}/images
# ===========================================================================

@app.get("/chunk/{chunk_id}/images", summary="Get images linked to a chunk")
async def get_chunk_images(
    chunk_id: str = FPath(..., description="Chunk ID"),
) -> dict:
    """Return all images (with captions) linked to a chunk via chunk_images table."""
    if not _DB_PATH.exists():
        raise HTTPException(503, "kb.db not found")

    with get_db_conn() as conn:
        rows = conn.execute(
            """SELECT id, image_path, thumbnail_path, caption, page_idx, width, height
               FROM chunk_images
               WHERE chunk_id = ?
               ORDER BY page_idx, id""",
            (chunk_id,),
        ).fetchall()

    return {
        "chunk_id": chunk_id,
        "total": len(rows),
        "images": [
            {
                "id": r[0],
                "image_path": r[1],
                "thumbnail_path": r[2],
                "caption": r[3],
                "page_idx": r[4],
                "width": r[5],
                "height": r[6],
            }
            for r in rows
        ],
    }


# ===========================================================================
# Endpoint: POST /search/image  (CLIP text-to-image search)
# ===========================================================================

# Lazy-loaded CLIP encoder (only used when image_emb table is populated)
_clip_encoder: Any | None = None
_clip_loaded: bool = False


def _try_load_clip() -> bool:
    """Attempt to load CLIP ViT-L/14 for text-to-image search."""
    global _clip_encoder, _clip_loaded
    if _clip_loaded:
        return _clip_encoder is not None

    _clip_loaded = True
    try:
        import sys  # noqa: PLC0415
        scripts_dir = str(_BASE_DIR / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)

        import torch  # noqa: PLC0415
        from transformers import CLIPModel, CLIPProcessor, CLIPTokenizer  # noqa: PLC0415

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        model_id = "openai/clip-vit-large-patch14"
        processor = CLIPProcessor.from_pretrained(model_id)
        model = CLIPModel.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if "cuda" in device else torch.float32,
        ).to(device)
        model.eval()

        _clip_encoder = {"model": model, "processor": processor,
                         "device": device, "torch": torch}
        log.info("CLIP ViT-L/14 loaded for /search/image endpoint.")
    except Exception as exc:
        log.warning("CLIP load failed: %s — /search/image disabled.", exc)
        _clip_encoder = None

    return _clip_encoder is not None


def _embed_text_clip(text: str) -> "np.ndarray | None":
    """Encode a text query using CLIP and return L2-normalised 768-d vector."""
    if not _try_load_clip() or _clip_encoder is None:
        return None
    import numpy as _np  # noqa: PLC0415
    enc = _clip_encoder
    inputs = enc["processor"](text=[text], return_tensors="pt", padding=True).to(enc["device"])
    with enc["torch"].no_grad():
        feat = enc["model"].get_text_features(**inputs)
    vec = feat.float().cpu().numpy()[0]
    norm = _np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


class ImageSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Text query for image search")
    limit: int = Field(10, ge=1, le=50)
    layer: str | None = None
    language: str | None = None


@app.post("/search/image", summary="Text-to-image search via CLIP")
async def image_search(req: ImageSearchRequest) -> dict:
    """
    Search images by text description using CLIP ViT-L/14 embeddings.

    Requires embed_images.py to have been run (populates LanceDB image_emb table).
    Gracefully returns 503 if image_emb is not available.
    """
    if not _lancedb_available:
        raise HTTPException(503, detail={"error": "LanceDB not available"})

    try:
        if "image_emb" not in _lancedb_db.table_names():
            raise HTTPException(
                503,
                detail={
                    "error": "image_emb table not found",
                    "hint": "Run scripts/embed_images.py to build CLIP embeddings.",
                },
            )
    except Exception:
        raise HTTPException(503, detail={"error": "image_emb table not available"})

    query_vec = _embed_text_clip(req.query)
    if query_vec is None:
        raise HTTPException(
            503,
            detail={
                "error": "CLIP model not available",
                "hint": "CLIP ViT-L/14 must be loaded. Check server logs.",
            },
        )

    tbl = _lancedb_db.open_table("image_emb")
    q = tbl.search(query_vec).limit(req.limit)
    filter_parts: list[str] = []
    if req.layer:
        filter_parts.append(f"layer = '{req.layer}'")
    if req.language:
        filter_parts.append(f"source_lang = '{req.language}'")
    if filter_parts:
        q = q.where(" AND ".join(filter_parts))

    results = q.to_list()

    # Enrich with chunk data
    chunk_ids = list({r["chunk_id"] for r in results})
    with get_db_conn() as conn:
        chunk_map = fetch_chunks_by_ids(conn, chunk_ids)

    return {
        "query": req.query,
        "total": len(results),
        "results": [
            {
                "image_id":    r["image_id"],
                "image_path":  r["image_path"],
                "caption":     r.get("caption", ""),
                "score":       round(float(r.get("_distance", 0)), 6),
                "chunk_id":    r["chunk_id"],
                "chunk_title": chunk_map[r["chunk_id"]]["title"] if r["chunk_id"] in chunk_map else "",
                "layer":       r.get("layer", ""),
                "source_lang": r.get("source_lang", ""),
            }
            for r in results
        ],
    }


# ===========================================================================
# Parts catalog endpoints
# ===========================================================================


def _parts_table_exists(conn: sqlite3.Connection) -> bool:
    """Check if the parts table exists in the database."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='parts'"
    )
    return cur.fetchone() is not None


@app.get("/parts/search", summary="Search parts by number, name, or system")
async def search_parts(
    q: str = "",
    system: str = "",
    subsystem: str = "",
    lang: str = "zh",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """
    Search the parts catalog.

    - **q**: search query (matches part_number, part_name_zh, part_name_en, part_name_ru)
    - **system**: filter by system_en (e.g. "Engine Assembly")
    - **subsystem**: filter by subsystem_en
    - **lang**: response language preference (zh, en, ru)
    - **limit**: max results (1-1000)
    - **offset**: skip first N results (for pagination)
    """
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)

    with get_db_conn() as conn:
        if not _parts_table_exists(conn):
            raise HTTPException(
                503,
                detail={
                    "error": "parts table not found",
                    "hint": "Run scripts/ocr_parts_tables.py to build the parts catalog.",
                },
            )

        where_parts: list[str] = []
        params: list[Any] = []

        if q:
            # SQLite LIKE is case-insensitive for ASCII but not for Unicode/Cyrillic
            # Search both original and capitalized variants
            q_low = q.lower()
            q_cap = q.capitalize()
            where_parts.append(
                "(part_number LIKE ? OR part_name_zh LIKE ?"
                " OR part_name_en LIKE ? OR part_name_en LIKE ?"
                " OR part_name_ru LIKE ? OR part_name_ru LIKE ?)"
            )
            params.extend([
                f"%{q}%", f"%{q}%",
                f"%{q_low}%", f"%{q_cap}%",
                f"%{q_low}%", f"%{q_cap}%",
            ])

        if system:
            where_parts.append("(system_en LIKE ? OR system_zh LIKE ?)")
            params.extend([f"%{system}%", f"%{system}%"])

        if subsystem:
            where_parts.append("(subsystem_en LIKE ? OR subsystem_zh LIKE ?)")
            params.extend([f"%{subsystem}%", f"%{subsystem}%"])

        sql = "SELECT * FROM parts"
        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)
        sql += " ORDER BY system_zh, subsystem_zh, part_number"
        sql += f" LIMIT {limit + 1} OFFSET {offset}"

        rows = conn.execute(sql, params).fetchall()
        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        results = []
        col_names = [desc[0] for desc in conn.execute("PRAGMA table_info(parts)").fetchall()]
        _cols = {r[1] for r in conn.execute("PRAGMA table_info(parts)").fetchall()}
        has_ru = "part_name_ru" in _cols
        has_fastener = "is_fastener" in _cols
        has_diagram = "diagram_image" in _cols
        for row in rows:
            item = {
                "id": row["id"],
                "part_number": row["part_number"],
                "part_name_zh": row["part_name_zh"],
                "part_name_en": row["part_name_en"],
                "hotspot_id": row["hotspot_id"],
                "system_zh": row["system_zh"],
                "system_en": row["system_en"],
                "subsystem_zh": row["subsystem_zh"],
                "subsystem_en": row["subsystem_en"],
                "page_idx": row["page_idx"],
                "source_image": row["source_image"],
                "diagram_image": row["diagram_image"] if has_diagram else None,
            }
            if has_ru:
                item["part_name_ru"] = row["part_name_ru"]
            if has_fastener:
                item["is_fastener"] = bool(row["is_fastener"])
            results.append(item)

        return {
            "query": q,
            "system": system,
            "total": len(results),
            "offset": offset,
            "has_more": has_more,
            "results": results,
        }


@app.get("/parts/stats", summary="Parts catalog statistics by system")
async def parts_stats() -> dict:
    """Return part count grouped by system."""
    with get_db_conn() as conn:
        if not _parts_table_exists(conn):
            raise HTTPException(503, detail={"error": "parts table not found"})

        total = conn.execute("SELECT COUNT(*) FROM parts").fetchone()[0]
        unique_pn = conn.execute(
            "SELECT COUNT(DISTINCT part_number) FROM parts"
        ).fetchone()[0]

        rows = conn.execute("""
            SELECT system_zh, system_en,
                   COUNT(*) as part_count,
                   COUNT(DISTINCT part_number) as unique_parts,
                   COUNT(DISTINCT subsystem_zh) as subsystem_count
            FROM parts
            GROUP BY system_zh
            ORDER BY part_count DESC
        """).fetchall()

        systems = []
        for row in rows:
            systems.append({
                "system_zh": row["system_zh"],
                "system_en": row["system_en"],
                "part_count": row["part_count"],
                "unique_parts": row["unique_parts"],
                "subsystem_count": row["subsystem_count"],
            })

        return {
            "total_parts": total,
            "unique_part_numbers": unique_pn,
            "systems_count": len(systems),
            "systems": systems,
        }


@app.get("/parts/{part_number}", summary="Get part details by exact part number")
async def get_part(part_number: str = FPath(..., description="Part number")) -> dict:
    """Look up one or more parts by exact part number."""
    with get_db_conn() as conn:
        if not _parts_table_exists(conn):
            raise HTTPException(503, detail={"error": "parts table not found"})

        rows = conn.execute(
            "SELECT * FROM parts WHERE part_number = ?", (part_number,)
        ).fetchall()

        if not rows:
            raise HTTPException(404, detail={"error": f"Part {part_number} not found"})

        results = []
        _cols2 = {r[1] for r in conn.execute("PRAGMA table_info(parts)").fetchall()}
        has_ru = "part_name_ru" in _cols2
        has_fastener = "is_fastener" in _cols2
        has_diagram = "diagram_image" in _cols2
        for row in rows:
            item = {
                "id": row["id"],
                "part_number": row["part_number"],
                "part_name_zh": row["part_name_zh"],
                "part_name_en": row["part_name_en"],
                "hotspot_id": row["hotspot_id"],
                "system_zh": row["system_zh"],
                "system_en": row["system_en"],
                "subsystem_zh": row["subsystem_zh"],
                "subsystem_en": row["subsystem_en"],
                "page_idx": row["page_idx"],
                "source_image": row["source_image"],
                "diagram_image": row["diagram_image"] if has_diagram else None,
                "confidence": row["confidence"],
            }
            if has_ru:
                item["part_name_ru"] = row["part_name_ru"]
            if has_fastener:
                item["is_fastener"] = bool(row["is_fastener"])
            results.append(item)

        return {"part_number": part_number, "count": len(results), "results": results}


@app.get("/parts/subsystems/{system}", summary="Get subsystems with illustration images for a system")
async def get_subsystems(system: str = FPath(..., description="System name (EN or ZH)")) -> dict:
    """Return subsystems grouped with their first illustration image."""
    with get_db_conn() as conn:
        if not _parts_table_exists(conn):
            raise HTTPException(503, detail={"error": "parts table not found"})

        rows = conn.execute(
            """SELECT subsystem_zh, subsystem_en, COUNT(*) as part_count,
                      MIN(source_image) as illustration, MIN(page_idx) as first_page
               FROM parts
               WHERE system_en LIKE ? OR system_zh LIKE ?
               GROUP BY subsystem_zh
               ORDER BY MIN(page_idx)""",
            (f"%{system}%", f"%{system}%"),
        ).fetchall()

        subs = []
        for r in rows:
            subs.append({
                "subsystem_zh": r["subsystem_zh"],
                "subsystem_en": r["subsystem_en"],
                "part_count": r["part_count"],
                "illustration": r["illustration"],
                "first_page": r["first_page"],
            })

        return {"system": system, "subsystems": subs, "total": len(subs)}


# ===========================================================================
# Exception handlers
# ===========================================================================

@app.exception_handler(sqlite3.OperationalError)
async def sqlite_error_handler(request: Request, exc: sqlite3.OperationalError):
    log.error("SQLite error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"error": "database_error", "detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    log.error("Unhandled error on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )


# ===========================================================================
# Scraper Management API
# ===========================================================================

import threading
import subprocess

# Active scraper runs (thread-safe)
_scraper_runs: dict[str, dict] = {}
_scraper_lock = threading.Lock()

ALL_SCRAPERS = [
    # Scraper script names (for running)
    "lixiang", "autohome", "ru", "drom", "drom_reviews",
    "drive2", "liforum", "dongchedi", "carnewschina",
    "wikipedia", "electrek", "ru_auto", "autoreview", "news",
    "getcar", "autochina_blog", "ev_forums", "autonews",
]

# DB source_names that differ from scraper names — auto-discovered
_DB_SOURCE_ALIASES = {
    "carnewschina_en": "carnewschina",
    "drom_ru": "drom",
    "drom.ru": "drom",
    "getcar_ru": "getcar",
    "dongchedi_cn": "dongchedi",
    "autohome_cn": "autohome",
    "autonews_ru": "autonews",
    "topelectricsuv": "electrek",
    "insideevs": "electrek",
}


@app.get("/scrapers/list")
async def scrapers_list():
    """List all scrapers with their stats from DB."""
    with get_db_conn() as conn:
        # Get stats per source
        rows = conn.execute("""
            SELECT source_name, lang, COUNT(*) total,
                   SUM(CASE WHEN imported=1 THEN 1 ELSE 0 END) imported,
                   AVG(relevance) avg_relevance,
                   MAX(scraped_at) last_scraped,
                   AVG(LENGTH(content)) avg_length
            FROM scraped_content
            GROUP BY source_name
            ORDER BY source_name
        """).fetchall()

    stats_by_source = {}
    for r in rows:
        stats_by_source[r[0]] = {
            "source_name": r[0],
            "lang": r[1],
            "total": r[2],
            "imported": r[3] or 0,
            "avg_relevance": round(r[4] or 0, 2),
            "last_scraped": r[5],
            "avg_length": int(r[6] or 0),
        }

    # Merge DB source_names into ALL_SCRAPERS (include DB-only sources)
    all_names = list(ALL_SCRAPERS)
    for db_name in stats_by_source:
        if db_name not in all_names and db_name not in _DB_SOURCE_ALIASES:
            all_names.append(db_name)

    # Aggregate aliased stats into parent scraper
    for db_name, parent in _DB_SOURCE_ALIASES.items():
        if db_name in stats_by_source:
            alias_stats = stats_by_source[db_name]
            if parent in stats_by_source:
                ps = stats_by_source[parent]
                ps["total"] += alias_stats["total"]
                ps["imported"] += alias_stats["imported"]
            else:
                stats_by_source[parent] = dict(alias_stats)
                stats_by_source[parent]["source_name"] = parent

    scrapers = []
    seen = set()
    for name in all_names:
        if name in seen or name in _DB_SOURCE_ALIASES:
            continue
        seen.add(name)
        info = stats_by_source.get(name, {})
        with _scraper_lock:
            run_info = _scraper_runs.get(name)
        scrapers.append({
            "name": name,
            "lang": info.get("lang", "?"),
            "total": info.get("total", 0),
            "imported": info.get("imported", 0),
            "avg_relevance": info.get("avg_relevance", 0),
            "last_scraped": info.get("last_scraped"),
            "avg_length": info.get("avg_length", 0),
            "status": run_info["status"] if run_info else "idle",
            "run_result": run_info.get("result") if run_info else None,
        })

    return {"scrapers": scrapers}


@app.post("/scrapers/run/{name}")
async def scraper_run(name: str):
    """Start a scraper in a background thread."""
    if name not in ALL_SCRAPERS and name != "all":
        raise HTTPException(404, f"Unknown scraper: {name}")

    with _scraper_lock:
        existing = _scraper_runs.get(name)
        if existing and existing["status"] == "running":
            return {"status": "already_running", "name": name}

    def _run_scraper(scraper_name: str):
        with _scraper_lock:
            _scraper_runs[scraper_name] = {"status": "running", "started": time.time()}
        try:
            scripts_dir = Path(__file__).resolve().parents[1] / "scripts" / "scrapers"
            if scraper_name == "all":
                cmd = ["python", str(scripts_dir / "run_scrapers.py"), "--sources", "all"]
            else:
                cmd = ["python", str(scripts_dir / "run_scrapers.py"), "--sources", scraper_name]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600,
                cwd=str(scripts_dir),
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            with _scraper_lock:
                _scraper_runs[scraper_name] = {
                    "status": "done",
                    "result": result.stdout[-2000:] if result.stdout else "",
                    "error": result.stderr[-1000:] if result.returncode != 0 else "",
                    "returncode": result.returncode,
                    "finished": time.time(),
                }
        except subprocess.TimeoutExpired:
            with _scraper_lock:
                _scraper_runs[scraper_name] = {"status": "timeout", "finished": time.time()}
        except Exception as exc:
            with _scraper_lock:
                _scraper_runs[scraper_name] = {
                    "status": "error", "error": str(exc), "finished": time.time(),
                }

    t = threading.Thread(target=_run_scraper, args=(name,), daemon=True)
    t.start()
    return {"status": "started", "name": name}


@app.get("/scrapers/status/{name}")
async def scraper_status(name: str):
    """Check status of a running/completed scraper."""
    with _scraper_lock:
        run_info = _scraper_runs.get(name)
    if not run_info:
        return {"name": name, "status": "idle"}
    return {"name": name, **run_info}


@app.get("/scrapers/content")
async def scrapers_content(
    source: str = "",
    page: int = 1,
    per_page: int = 20,
    imported: str = "",  # "", "0", "1"
    sort: str = "newest",  # newest, oldest, relevance, length
):
    """Browse scraped content with pagination and filters."""
    with get_db_conn() as conn:
        where = []
        params = []
        if source:
            # Resolve aliases: "drom" should match "drom", "drom_ru", "drom.ru"
            alias_names = [source]
            for db_name, parent in _DB_SOURCE_ALIASES.items():
                if parent == source:
                    alias_names.append(db_name)
            placeholders = ",".join("?" * len(alias_names))
            where.append(f"source_name IN ({placeholders})")
            params.extend(alias_names)
        if imported in ("0", "1"):
            where.append("imported = ?")
            params.append(int(imported))

        where_sql = "WHERE " + " AND ".join(where) if where else ""

        order_map = {
            "newest": "scraped_at DESC",
            "oldest": "scraped_at ASC",
            "relevance": "relevance DESC",
            "length": "LENGTH(content) DESC",
        }
        order_sql = order_map.get(sort, "scraped_at DESC")

        total = conn.execute(
            f"SELECT COUNT(*) FROM scraped_content {where_sql}", params
        ).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(f"""
            SELECT id, url, source_name, lang, title, LENGTH(content) content_len,
                   relevance, dtc_codes, content_class, imported, scraped_at,
                   SUBSTR(content, 1, 300) preview
            FROM scraped_content {where_sql}
            ORDER BY {order_sql}
            LIMIT ? OFFSET ?
        """, params + [per_page, offset]).fetchall()

        items = []
        for r in rows:
            items.append({
                "id": r[0], "url": r[1], "source_name": r[2], "lang": r[3],
                "title": r[4], "content_length": r[5],
                "relevance": r[6], "dtc_codes": r[7], "content_class": r[8],
                "imported": bool(r[9]), "scraped_at": r[10],
                "preview": r[11],
            })

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@app.delete("/scrapers/content/{item_id}")
async def scrapers_delete_content(item_id: int):
    """Delete a scraped content item."""
    with get_db_conn() as conn:
        conn.execute("DELETE FROM scraped_content WHERE id = ?", (item_id,))
    return {"deleted": item_id}


@app.post("/scrapers/import")
async def scrapers_import():
    """Import unimported scraped content to KB chunks."""
    import sys
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts" / "scrapers"
    sys.path.insert(0, str(scripts_dir))
    from run_scrapers import import_scraped_to_kb
    import_scraped_to_kb()
    # Return updated stats
    with get_db_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM scraped_content").fetchone()[0]
        imported = conn.execute("SELECT COUNT(*) FROM scraped_content WHERE imported=1").fetchone()[0]
        pending = total - imported
    return {"total": total, "imported": imported, "pending": pending}


@app.get("/scrapers/content/{item_id}/full")
async def scrapers_content_full(item_id: int):
    """Get full content of a scraped item (for editing)."""
    with get_db_conn() as conn:
        r = conn.execute(
            "SELECT id, url, source_name, lang, title, content, relevance, dtc_codes, content_class, imported, scraped_at FROM scraped_content WHERE id=?",
            (item_id,)
        ).fetchone()
    if not r:
        raise HTTPException(404, "Item not found")
    return {
        "id": r[0], "url": r[1], "source_name": r[2], "lang": r[3],
        "title": r[4], "content": r[5], "relevance": r[6], "dtc_codes": r[7],
        "content_class": r[8], "imported": bool(r[9]), "scraped_at": r[10],
    }


@app.put("/scrapers/content/{item_id}")
async def scrapers_update_content(item_id: int, request: Request):
    """Update title/content/class of a scraped item before import."""
    body = await request.json()
    updates = []
    params = []
    for field in ("title", "content", "content_class"):
        if field in body:
            updates.append(f"{field} = ?")
            params.append(body[field])
    if not updates:
        raise HTTPException(400, "Nothing to update")
    params.append(item_id)
    with get_db_conn() as conn:
        conn.execute(f"UPDATE scraped_content SET {', '.join(updates)} WHERE id = ?", params)
    return {"updated": item_id}


def _fetch_html(url: str) -> str:
    """Fetch a URL and return HTML string."""
    import httpx
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,zh;q=0.7",
    }
    try:
        r = httpx.get(url, headers=headers, timeout=25, follow_redirects=True)
        if r.status_code != 200:
            raise HTTPException(502, f"HTTP {r.status_code} fetching {url}")
    except httpx.TimeoutException:
        raise HTTPException(504, f"Timeout fetching {url}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, f"Error fetching URL: {exc}")
    return r.text


def _detect_lang(text: str) -> str:
    """Detect language from text sample."""
    import re as _re
    sample = text[:500]
    ru_chars = len(_re.findall(r'[а-яА-ЯёЁ]', sample))
    zh_chars = len(_re.findall(r'[\u4e00-\u9fff]', sample))
    if ru_chars > 20:
        return "ru"
    elif zh_chars > 20:
        return "zh"
    return "en"


def _extract_article(html: str, url: str, method: str = "auto") -> dict:
    """Extract article title+content from HTML using the specified method.

    Methods:
      - "auto": pick best method based on domain (site-specific → trafilatura → bs4 → regex)
      - "trafilatura": trafilatura with balanced settings
      - "trafilatura_precision": trafilatura with favor_precision=True
      - "bs4": BeautifulSoup — extracts <article>, <main>, or largest text block
      - "bs4_article": BeautifulSoup — site-specific CSS selectors for known domains
      - "regex": raw <p> tag extraction (last resort)

    Returns: {"title": str, "content": str, "method_used": str}
    """
    import re as _re
    from urllib.parse import urlparse
    from bs4 import BeautifulSoup

    domain = urlparse(url).netloc.replace("www.", "")
    results = {}

    # --- Site-specific BS4 extractor ---
    def _bs4_site_specific() -> dict | None:
        soup = BeautifulSoup(html, 'html.parser')
        title = ""
        content = ""

        # Drom.ru single review
        if "drom.ru" in domain and "/reviews/" in url and url.count("/") > 5:
            editable = soup.select_one('.b-editable-area')
            if editable and len(editable.get_text()) > 200:
                content = editable.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                if not title:
                    title = content.split('\n')[0][:100]
                return {"title": title, "content": content}

        # Drom.ru review listing (5kopeek) — structured JSON data
        if "drom.ru" in domain and "5kopeek" in url:
            import json as _json
            for script in soup.find_all('script', type='application/json'):
                if script.string and len(script.string) > 10000:
                    try:
                        data = _json.loads(script.string)
                    except Exception:
                        continue
                    short_reviews = data.get('shortReviews', [])
                    parts = []
                    for sr in short_reviews:
                        tp = sr.get('titleParams', {})
                        line = []
                        if tp.get('firm') and tp.get('model'):
                            line.append(f"{tp['firm']} {tp['model']} {tp.get('year', '')}")
                        if sr.get('advantages'):
                            line.append(f"Плюсы: {sr['advantages']}")
                        if sr.get('disadvantages'):
                            line.append(f"Минусы: {sr['disadvantages']}")
                        if sr.get('breakages'):
                            line.append(f"Поломки: {sr['breakages']}")
                        if line:
                            parts.append(" | ".join(line))
                    if parts:
                        h1 = soup.select_one('h1')
                        title = h1.get_text(strip=True) if h1 else "Отзывы владельцев"
                        content = "\n\n".join(parts)
                        return {"title": title, "content": content}

        # Carnewschina.com
        if "carnewschina" in domain:
            article = soup.select_one('article .entry-content, article .post-content, .article-content')
            if article:
                # Remove share buttons, ads, related posts
                for rm in article.select('.sharedaddy, .jp-relatedposts, .ad-container, script, style, .social-share'):
                    rm.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1.entry-title, h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # GetCar.ru
        if "getcar" in domain:
            article = soup.select_one('.entry-content, .post-content, article .content')
            if article:
                for rm in article.select('script, style, .related-posts, .social, .comments'):
                    rm.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # TopElectricSUV / InsideEVs
        if "topelectricsuv" in domain or "insideevs" in domain:
            article = soup.select_one('article .entry-content, .article-body, .post-content')
            if article:
                for rm in article.select('script, style, .related, .comments, .social, nav'):
                    rm.decompose()
                content = article.get_text(separator='\n', strip=True)
                # Remove breadcrumbs from beginning
                lines = content.split('\n')
                while lines and ('»' in lines[0] or 'Home' in lines[0] or len(lines[0]) < 5):
                    lines.pop(0)
                content = '\n'.join(lines)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # Lixiang.com — product pages are JS-rendered, extract what we can
        if "lixiang.com" in domain or "li.auto" in domain:
            # These pages are mostly JS-rendered spec sheets
            main = soup.select_one('main, .main-content, #app')
            if main:
                content = main.get_text(separator='\n', strip=True)
                # Trim navigation/footer junk
                lines = [l for l in content.split('\n') if len(l.strip()) > 10]
                # Remove common nav items
                lines = [l for l in lines if not any(x in l for x in ['400-686-0900', 'press@lixiang', 'compliance@', '©20', '扫码'])]
                content = '\n'.join(lines[:200])  # cap at 200 lines
                title = soup.title.string.strip() if soup.title else ""
                return {"title": title, "content": content}

        # AutoReview / Autonews / Motor.ru — Russian news sites
        if any(d in domain for d in ["autoreview.ru", "autonews.ru", "motor.ru", "autostat.ru"]):
            article = soup.select_one('article, .article-text, .article__text, .b-text, .post-content')
            if article:
                for rm in article.select('script, style, .social, .comments, .related, .banner'):
                    rm.decompose()
                content = article.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        return None

    # --- Trafilatura extractor ---
    def _trafilatura_extract(precision: bool = False) -> dict:
        try:
            import trafilatura
            extracted = trafilatura.extract(
                html, include_comments=False, include_tables=True,
                no_fallback=precision, favor_precision=precision, favor_recall=not precision,
            )
            metadata = trafilatura.extract_metadata(html)
            title = (metadata.title if metadata and metadata.title else "") or ""
            content = extracted or ""
            return {"title": title, "content": content}
        except Exception:
            return {"title": "", "content": ""}

    # --- BS4 generic extractor ---
    def _bs4_generic() -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        # Remove script, style, nav, footer, header
        for tag in soup.select('script, style, nav, footer, header, .sidebar, .comments, .social, .related, .ad, .advertisement, .banner'):
            tag.decompose()

        # Try: article > main > biggest div
        for sel in ['article', 'main', '[role="main"]']:
            el = soup.select_one(sel)
            if el and len(el.get_text()) > 200:
                content = el.get_text(separator='\n', strip=True)
                h1 = soup.select_one('h1')
                title = h1.get_text(strip=True) if h1 else ""
                return {"title": title, "content": content}

        # Fallback: find biggest text-heavy div
        best = None
        best_len = 0
        for div in soup.find_all('div'):
            text = div.get_text(separator='\n', strip=True)
            # Prefer divs with high text-to-html ratio
            if len(text) > best_len and len(text) > 200:
                best_len = len(text)
                best = text
        title = ""
        h1 = soup.select_one('h1')
        if h1:
            title = h1.get_text(strip=True)
        if not title and soup.title:
            title = soup.title.string.strip() if soup.title.string else ""
        return {"title": title, "content": best or ""}

    # --- Regex extractor ---
    def _regex_extract() -> dict:
        m_h1 = _re.search(r'<h1[^>]*>(.*?)</h1>', html, _re.S | _re.I)
        title = _re.sub(r'<[^>]+>', '', m_h1.group(1)).strip() if m_h1 else ""
        if not title:
            m_t = _re.search(r'<title[^>]*>(.*?)</title>', html, _re.S | _re.I)
            if m_t:
                title = _re.sub(r'\s+', ' ', m_t.group(1)).strip()
        parts = []
        for m in _re.finditer(r'<p[^>]*>(.*?)</p>', html, _re.S | _re.I):
            text = _re.sub(r'<[^>]+>', '', m.group(1)).strip()
            text = _re.sub(r'\s+', ' ', text)
            if len(text) > 40:
                parts.append(text)
        return {"title": title, "content": "\n\n".join(parts)}

    # --- Execute based on method ---
    if method == "auto":
        # Try site-specific first
        result = _bs4_site_specific()
        if result and len(result.get("content", "")) > 100:
            result["method_used"] = "bs4_article"
            return result
        # Then trafilatura
        result = _trafilatura_extract(precision=False)
        if len(result.get("content", "")) > 100:
            result["method_used"] = "trafilatura"
            return result
        # Then BS4 generic
        result = _bs4_generic()
        if len(result.get("content", "")) > 100:
            result["method_used"] = "bs4"
            return result
        # Last resort: regex
        result = _regex_extract()
        result["method_used"] = "regex"
        return result
    elif method == "trafilatura":
        result = _trafilatura_extract(precision=False)
        result["method_used"] = "trafilatura"
        return result
    elif method == "trafilatura_precision":
        result = _trafilatura_extract(precision=True)
        result["method_used"] = "trafilatura_precision"
        return result
    elif method == "bs4_article":
        result = _bs4_site_specific()
        if result and len(result.get("content", "")) > 50:
            result["method_used"] = "bs4_article"
            return result
        # Fallback to generic BS4
        result = _bs4_generic()
        result["method_used"] = "bs4"
        return result
    elif method == "bs4":
        result = _bs4_generic()
        result["method_used"] = "bs4"
        return result
    elif method == "regex":
        result = _regex_extract()
        result["method_used"] = "regex"
        return result
    else:
        raise HTTPException(400, f"Unknown extraction method: {method}. Use: auto, trafilatura, trafilatura_precision, bs4_article, bs4, regex")


def _clean_extracted_content(content: str) -> str:
    """Post-process extracted content: remove junk lines, normalize whitespace."""
    import re as _re
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        # Skip common navigation/boilerplate patterns
        if any(p in line.lower() for p in [
            'cookie', 'javascript', 'подписаться', 'subscribe',
            'политика конфиденциальности', 'privacy policy',
            'все права защищены', 'all rights reserved',
        ]):
            continue
        # Skip very short lines that are likely menu items
        if len(line) < 5 and not any(c.isdigit() for c in line):
            continue
        cleaned.append(line)
    # Remove trailing empty lines
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return '\n'.join(cleaned)


@app.post("/scrapers/scrape-url")
async def scrapers_scrape_url(request: Request):
    """Scrape a single URL: fetch, extract title+content, save to scraped_content.

    Body: {"url": str, "source": str, "lang": str, "method": str}
    method: auto|trafilatura|trafilatura_precision|bs4_article|bs4|regex
    """
    body = await request.json()
    url = body.get("url", "").strip()
    source = body.get("source", "").strip() or "manual"
    lang = body.get("lang", "").strip() or "auto"
    method = body.get("method", "auto").strip()

    if not url or not url.startswith("http"):
        raise HTTPException(400, "Valid URL required")

    # Check if already scraped
    with get_db_conn() as conn:
        exists = conn.execute("SELECT id FROM scraped_content WHERE url = ?", (url,)).fetchone()
        if exists:
            return {"status": "duplicate", "id": exists[0], "message": "URL already in database"}

    html = _fetch_html(url)
    result = _extract_article(html, url, method)
    title = result.get("title", "")
    content = _clean_extracted_content(result.get("content", ""))
    method_used = result.get("method_used", method)

    if len(content) < 50:
        raise HTTPException(422, f"Could not extract content (method={method_used}). Try a different method.")

    if not lang or lang == "auto":
        lang = _detect_lang(content)

    import hashlib
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    with get_db_conn() as conn:
        cur = conn.execute("""
            INSERT INTO scraped_content (url_hash, url, source_name, lang, title, content, relevance, content_class, imported, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))
        """, (url_hash, url, source, lang, title[:300], content, 0.5, "article"))
        new_id = cur.lastrowid

    return {
        "status": "ok",
        "id": new_id,
        "title": title[:200],
        "content_length": len(content),
        "lang": lang,
        "source": source,
        "method_used": method_used,
        "preview": content[:300],
    }


@app.post("/scrapers/preview-extract")
async def scrapers_preview_extract(request: Request):
    """Preview extraction from URL without saving. Try all methods and compare.

    Body: {"url": str, "methods": ["auto","trafilatura","bs4_article","bs4","regex"]}
    Returns results for each method so user can pick the best one.
    """
    body = await request.json()
    url = body.get("url", "").strip()
    methods = body.get("methods", ["auto", "trafilatura", "trafilatura_precision", "bs4_article", "bs4", "regex"])

    if not url or not url.startswith("http"):
        raise HTTPException(400, "Valid URL required")

    html = _fetch_html(url)
    previews = []
    for m in methods:
        try:
            result = _extract_article(html, url, m)
            content = _clean_extracted_content(result.get("content", ""))
            previews.append({
                "method": m,
                "method_used": result.get("method_used", m),
                "title": result.get("title", "")[:200],
                "content_length": len(content),
                "preview_start": content[:500],
                "preview_end": content[-300:] if len(content) > 300 else "",
            })
        except Exception as exc:
            previews.append({"method": m, "error": str(exc), "content_length": 0})

    return {"url": url, "previews": previews}


@app.post("/scrapers/rescrape/{item_id}")
async def scrapers_rescrape_item(item_id: int, request: Request):
    """Re-fetch and re-extract content for an existing scraped item.

    Body: {"method": "auto"|"trafilatura"|"bs4_article"|"bs4"|"regex"}
    """
    body = await request.json()
    method = body.get("method", "auto").strip()

    with get_db_conn() as conn:
        row = conn.execute("SELECT url, source_name, lang FROM scraped_content WHERE id = ?", (item_id,)).fetchone()
    if not row:
        raise HTTPException(404, f"Item {item_id} not found")

    url, source, lang = row
    html = _fetch_html(url)
    result = _extract_article(html, url, method)
    content = _clean_extracted_content(result.get("content", ""))
    title = result.get("title", "")
    method_used = result.get("method_used", method)

    if len(content) < 50:
        raise HTTPException(422, f"Re-extraction failed (method={method_used})")

    new_lang = _detect_lang(content) if not lang else lang

    with get_db_conn() as conn:
        conn.execute("""
            UPDATE scraped_content SET title = ?, content = ?, lang = ?, scraped_at = datetime('now')
            WHERE id = ?
        """, (title[:300], content, new_lang, item_id))

    return {
        "status": "ok",
        "id": item_id,
        "title": title[:200],
        "content_length": len(content),
        "old_length": None,
        "method_used": method_used,
        "preview": content[:300],
    }


@app.post("/scrapers/rescrape-all")
async def scrapers_rescrape_all(request: Request):
    """Re-scrape all items (or filtered by source). Returns summary of changes.

    Body: {"source": str (optional), "method": "auto", "dry_run": bool}
    """
    body = await request.json()
    source_filter = body.get("source", "").strip()
    method = body.get("method", "auto").strip()
    dry_run = body.get("dry_run", False)

    with get_db_conn() as conn:
        if source_filter:
            alias_names = [source_filter]
            for db_name, parent in _DB_SOURCE_ALIASES.items():
                if parent == source_filter:
                    alias_names.append(db_name)
            placeholders = ",".join("?" * len(alias_names))
            rows = conn.execute(f"SELECT id, url, source_name, lang, LENGTH(content) FROM scraped_content WHERE source_name IN ({placeholders})", alias_names).fetchall()
        else:
            rows = conn.execute("SELECT id, url, source_name, lang, LENGTH(content) FROM scraped_content").fetchall()

    results = {"total": len(rows), "updated": 0, "failed": 0, "skipped": 0, "details": []}
    import httpx

    for item_id, url, src, lang, old_len in rows:
        try:
            html = _fetch_html(url)
            result = _extract_article(html, url, method)
            content = _clean_extracted_content(result.get("content", ""))
            title = result.get("title", "")
            method_used = result.get("method_used", method)

            if len(content) < 50:
                results["skipped"] += 1
                results["details"].append({"id": item_id, "status": "skip", "reason": "content too short"})
                continue

            new_lang = _detect_lang(content) if not lang else lang

            if not dry_run:
                with get_db_conn() as conn:
                    conn.execute("""
                        UPDATE scraped_content SET title = ?, content = ?, lang = ?, scraped_at = datetime('now')
                        WHERE id = ?
                    """, (title[:300], content, new_lang, item_id))

            results["updated"] += 1
            results["details"].append({
                "id": item_id,
                "status": "updated" if not dry_run else "would_update",
                "method": method_used,
                "old_len": old_len,
                "new_len": len(content),
                "title": title[:80],
            })
        except Exception as exc:
            results["failed"] += 1
            results["details"].append({"id": item_id, "status": "error", "error": str(exc)})

    return results


def _find_scraper_file(name: str) -> Path | None:
    """Find the Python file for a scraper by name."""
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts" / "scrapers"
    candidates = [
        scripts_dir / f"{name}_scraper.py",
        scripts_dir / f"{name}.py",
        scripts_dir / f"{name}_com.py",
        scripts_dir / f"lixiang_com.py" if name == "lixiang" else None,
        scripts_dir / f"liautocn_news.py" if name == "news" else None,
        scripts_dir / f"ru_sources_scraper.py" if name == "ru" else None,
    ]
    for cand in candidates:
        if cand and cand.exists():
            return cand
    return None


@app.get("/scrapers/sources")
async def scrapers_sources_info():
    """Get source URLs from scraper files."""
    import re as _re
    result = {}
    for name in ALL_SCRAPERS:
        info = {"name": name, "seed_urls": [], "file": "", "domain": ""}
        fp = _find_scraper_file(name)
        if fp:
            info["file"] = fp.name
            try:
                text = fp.read_text(encoding="utf-8")
                urls = _re.findall(r'"(https?://[^"]+)"', text)
                info["seed_urls"] = urls[:30]
                # Extract primary domain
                if urls:
                    from urllib.parse import urlparse
                    info["domain"] = urlparse(urls[0]).netloc
            except Exception:
                pass
        result[name] = info
    return result


@app.post("/scrapers/sources/{name}/add-url")
async def scrapers_add_url(name: str, request: Request):
    """Add a URL to a scraper's SEED_URLS / URL list in the Python file."""
    import re as _re
    body = await request.json()
    url = body.get("url", "").strip()
    if not url or not url.startswith("http"):
        raise HTTPException(400, "Valid URL required")

    fp = _find_scraper_file(name)
    if not fp:
        raise HTTPException(404, f"Scraper file for '{name}' not found")

    text = fp.read_text(encoding="utf-8")

    # Try to find a URL list: SEED_URLS = [...], DIRECT_URLS = [...], etc.
    # Insert new URL after the opening bracket of the first list found
    patterns = [
        r'(SEED_URLS\s*=\s*\[)',
        r'(DIRECT_URLS\s*=\s*\[)',
        r'(SEARCH_QUERIES\s*=\s*\[)',
        r'(URLS\s*=\s*\[)',
    ]
    inserted = False
    for pat in patterns:
        m = _re.search(pat, text)
        if m:
            insert_pos = m.end()
            text = text[:insert_pos] + f'\n    "{url}",' + text[insert_pos:]
            inserted = True
            break

    if not inserted:
        raise HTTPException(400, "Could not find SEED_URLS or similar list in scraper file")

    fp.write_text(text, encoding="utf-8")
    return {"added": url, "file": fp.name, "scraper": name}


@app.post("/scrapers/sources/{name}/discover")
async def scrapers_discover(name: str, request: Request):
    """Discover article URLs by crawling source site with keyword filter.

    Strategy: crawl the source domain's tag/search/listing pages and filter
    links by keywords. More reliable than search engines which block bots.
    """
    import re as _re
    import httpx
    from urllib.parse import urlparse, urljoin

    body = await request.json()
    keywords = body.get("keywords", "").strip()
    if not keywords:
        raise HTTPException(400, "keywords required")

    # Get seed URLs and domain from scraper file
    domain = ""
    seed_urls = []
    fp = _find_scraper_file(name)
    if fp:
        try:
            text = fp.read_text(encoding="utf-8")
            seed_urls = _re.findall(r'"(https?://[^"]+)"', text)
            if seed_urls:
                domain = urlparse(seed_urls[0]).netloc
        except Exception:
            pass

    if not domain:
        raise HTTPException(400, f"No domain found for scraper '{name}'")

    base_url = f"https://{domain}"
    kw_list = [k.strip().lower() for k in keywords.split() if k.strip()]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    found_urls = []
    crawled_pages = []

    try:
        # Build discovery URLs: tag pages, search, category pages
        kw_slug = "-".join(kw_list[:3])
        kw_plus = "+".join(kw_list[:5])
        discover_urls = [
            f"{base_url}/tag/{kw_slug}/",
            f"{base_url}/topics/{kw_slug}/",
            f"{base_url}/category/{kw_slug}/",
            f"{base_url}/?s={kw_plus}",
            f"{base_url}/search?q={kw_plus}",
        ]
        # Also add existing seed URLs (they often are listing pages)
        for su in seed_urls[:5]:
            if su not in discover_urls:
                discover_urls.append(su)

        client = httpx.Client(headers=headers, timeout=12, follow_redirects=True)
        for page_url in discover_urls:
            try:
                r = client.get(page_url)
                if r.status_code != 200:
                    continue
                crawled_pages.append(str(r.url))

                # Extract all links from the page
                _skip_ext = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js', '.xml', '.json', '.pdf', '.webp', '.rss', '.atom')
                _skip_path = ('/wp-content/', '/wp-json/', '/wp-includes/', '/feed', '/xmlrpc', '/wp-login',
                              '/cart', '/checkout', '/tag/', '/topics/', '/category/', '/page/', '/author/',
                              '/glossary', '/about', '/contact', '/privacy', '/terms', '/sitemap')
                for href in _re.findall(r'href="(https?://[^"]+)"', r.text):
                    parsed = urlparse(href)
                    # Only keep links from the same domain
                    if domain not in parsed.netloc:
                        continue
                    path = parsed.path.lower()
                    # Skip static assets and WP internals
                    if any(path.endswith(ext) for ext in _skip_ext):
                        continue
                    if any(skip in path for skip in _skip_path):
                        continue
                    # Must look like an article URL
                    is_article = (
                        _re.search(r'/20\d{2}/', path)  # year in URL (blog post)
                        or _re.search(r'/\d{4}/\d{2}/', path)  # date path
                        or (path.count('/') >= 2 and len(path) > 20)  # long slug
                        or any(kw in path for kw in kw_list)  # keyword in URL
                    )
                    if is_article:
                        found_urls.append(href)
            except Exception:
                continue
        client.close()

    except Exception as exc:
        log.warning("Discover crawl error for %s: %s", name, exc)

    # Deduplicate, strip fragments
    seen = set()
    unique = []
    for u in found_urls:
        clean = u.split("#")[0].rstrip("/")
        if clean not in seen:
            seen.add(clean)
            unique.append(clean)

    # Also check which are already in DB
    already_scraped = set()
    try:
        with get_db_conn() as conn:
            rows = conn.execute("SELECT url FROM scraped_content").fetchall()
            already_scraped = {r[0].split("#")[0].rstrip("/") for r in rows if r[0]}
    except Exception:
        pass

    results = []
    for u in unique:
        results.append({
            "url": u,
            "already_scraped": u.rstrip("/") in already_scraped or u in already_scraped,
        })

    return {
        "scraper": name,
        "keywords": keywords,
        "domain": domain,
        "crawled_pages": crawled_pages,
        "results": results[:50],
        "total": len(results),
    }


@app.post("/scrapers/create")
async def scrapers_create(request: Request):
    """Generate a new scraper Python file from parameters."""
    body = await request.json()
    name = body.get("name", "").strip()
    lang = body.get("lang", "en")
    urls = body.get("urls", [])
    keywords = body.get("keywords", "")
    selectors = body.get("selectors", ".entry-content p, .post-content p, article p")

    if not name or not urls:
        raise HTTPException(400, "name and urls required")

    import re
    if not re.match(r'^[a-z0-9_]+$', name):
        raise HTTPException(400, "name must be lowercase alphanumeric + underscores")

    scripts_dir = Path(__file__).resolve().parents[1] / "scripts" / "scrapers"
    filepath = scripts_dir / f"{name}_scraper.py"
    if filepath.exists():
        raise HTTPException(409, f"Scraper {name} already exists")

    class_name = ''.join(w.capitalize() for w in name.split('_')) + 'Scraper'
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()] if keywords else ['li-', 'lixiang']
    sel_list = [s.strip() for s in selectors.split(',') if s.strip()]

    code = f'''#!/usr/bin/env python3
"""
{name}_scraper.py — Auto-generated scraper for {name}.
"""
from __future__ import annotations
import logging, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

SEED_URLS = {repr(urls)}


class {class_name}(BaseScraper):
    source_name = "{name}"
    lang = "{lang}"
    delay_range = (2.0, 4.0)
    min_content_length = 500

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()
        for url in SEED_URLS:
            if "?" not in url and url.count("/") >= 4:
                article_urls.add(url.split("#")[0])
                continue
            log.info("Searching: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    clean = link.split("#")[0]
                    if any(kw in clean.lower() for kw in {repr(kw_list)}):
                        full = clean if clean.startswith("http") else url.split("/")[0] + "//" + url.split("/")[2] + clean
                        article_urls.add(full.rstrip("/") + "/")
                self._sleep()
            except Exception as exc:
                log.warning("Search error: %s — %s", url, exc)

        log.info("Found %d article URLs", len(article_urls))
        for url in sorted(article_urls):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue
                title = page.css("h1::text").get() or page.css("title::text").get() or ""
                content_parts = []
                for selector in {repr(sel_list)}:
                    for el in page.css(selector):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 30:
                            content_parts.append(text)
                    if content_parts:
                        break
                if not content_parts:
                    content_parts = extract_text_nodes(page, min_len=30)
                content = "\\n\\n".join(content_parts)
                if len(content) < 300:
                    continue
                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="{lang}", title=title.strip()[:200], content=content,
                )
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = {class_name}()
    count = scraper.run()
    print(f"Done. New items saved: {{count}}")
'''
    filepath.write_text(code, encoding="utf-8")

    # Register in ALL_SCRAPERS (runtime only — for persistence, edit run_scrapers.py manually)
    if name not in ALL_SCRAPERS:
        ALL_SCRAPERS.append(name)

    return {"created": name, "file": filepath.name, "class": class_name}


# ===========================================================================
# Entrypoint
# ===========================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info",
    )
