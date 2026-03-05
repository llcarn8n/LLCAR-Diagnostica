#!/usr/bin/env python3
"""
build_embeddings.py - Vector embedding pipeline for LLCAR Diagnostica KB.

Reads all chunks from the SQLite knowledge base (kb.db), encodes them with
two GPU-parallel models, writes dense vector tables to LanceDB, saves ColBERT
token matrices as BLOBs in SQLite, and builds approximate-nearest-neighbour
indexes for fast retrieval at query time.

Pipeline overview:
 1. GPU #0 (cuda:0) — pplx-embed-context-v1-4B (late chunking, 2560d)
      Encodes: title + content  →  content_emb table  (chunks grouped by source doc)
      Encodes: title only       →  title_emb   table  (chunks grouped by source doc)
 2. GPU #1 (cuda:1) — BGE-M3   (ColBERT, 1024d token matrices)
      Encodes: content          →  colbert_vectors rows in kb.db (BLOB, FP16)
 3. Builds IVF-PQ indexes on both LanceDB tables.
 4. Builds scalar indexes on brand / source_language columns.
 5. Verifies correctness with a random-query search test.

Key properties:
 - Graceful OOM handling: halves batch size and retries.
 - Transaction batching every 500 rows for SQLite ColBERT writes.
 - Idempotent: existing ColBERT rows are skipped (INSERT OR IGNORE).
 - --force flag: wipes LanceDB tables and all ColBERT rows before re-encoding.
 - FTS5 index in kb.db is left untouched.
 - Detailed statistics printed on completion.

FlagEmbedding 1.3.5 / transformers 5.x workaround:
 The FlagEmbedding package's __init__ imports a reranker that in turn tries to
 import `is_torch_fx_available` from transformers.utils.import_utils, which was
 removed in transformers 5.x.  We patch sys.modules with lightweight stubs
 BEFORE importing FlagEmbedding to avoid this hard import error.  The stubs
 only stub out reranker classes; the embedder (BGEM3FlagModel / M3Embedder) is
 loaded from its real implementation.
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import struct
import sys
import time
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Set BEFORE torch/CUDA initialise — prevents allocator fragmentation that
# causes false OOM when the allocator cannot find a contiguous block even
# though enough *total* free memory is available.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import numpy as np
import pyarrow as pa
import torch

# ---------------------------------------------------------------------------
# Optional tqdm — graceful fallback so the script runs even without it
# ---------------------------------------------------------------------------
try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover

    def tqdm(iterable=None, **kwargs):  # type: ignore[misc]
        """Minimal no-op replacement when tqdm is not installed."""
        if iterable is not None:
            return iterable

        class _Dummy:
            def update(self, *a, **kw):
                pass

            def close(self):
                pass

            def set_postfix(self, *a, **kw):
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
log = logging.getLogger("build_embeddings")


# ---------------------------------------------------------------------------
# FlagEmbedding reranker stub — must happen before any FlagEmbedding import
# ---------------------------------------------------------------------------

def _install_flagembedding_stubs() -> None:
    """
    Patch sys.modules with lightweight stubs for the broken reranker subpackage.

    FlagEmbedding 1.3.5 + transformers 5.x raises ImportError when importing
    `is_torch_fx_available` from transformers.utils.import_utils (removed in
    transformers 5.x).  We intercept the broken import path with module stubs
    so that BGEM3FlagModel (the embedder) can be loaded from its own file,
    which has no dependency on the reranker machinery.
    """
    sentinel: Any = None  # placeholder attribute value

    def _stub_pkg(name: str, **attrs: Any) -> types.ModuleType:
        m = types.ModuleType(name)
        m.__path__ = []          # type: ignore[attr-defined]
        m.__package__ = name
        for k, v in attrs.items():
            setattr(m, k, v)
        return m

    # Reranker package + sub-modules
    sys.modules.setdefault(
        "FlagEmbedding.inference.reranker",
        _stub_pkg(
            "FlagEmbedding.inference.reranker",
            FlagReranker=sentinel,
            FlagLLMReranker=sentinel,
            LayerWiseFlagLLMReranker=sentinel,
            LightWeightFlagLLMReranker=sentinel,
            RerankerModelClass=sentinel,
        ),
    )
    sys.modules.setdefault(
        "FlagEmbedding.inference.reranker.model_mapping",
        _stub_pkg(
            "FlagEmbedding.inference.reranker.model_mapping",
            RerankerModelClass=sentinel,
        ),
    )
    sys.modules.setdefault(
        "FlagEmbedding.inference.reranker.decoder_only",
        _stub_pkg(
            "FlagEmbedding.inference.reranker.decoder_only",
            FlagLLMReranker=sentinel,
            LayerWiseFlagLLMReranker=sentinel,
            LightWeightFlagLLMReranker=sentinel,
        ),
    )
    # auto_reranker module that references the broken reranker
    auto_r = types.ModuleType("FlagEmbedding.inference.auto_reranker")
    auto_r.FlagAutoReranker = sentinel  # type: ignore[attr-defined]
    sys.modules.setdefault("FlagEmbedding.inference.auto_reranker", auto_r)


_install_flagembedding_stubs()

# ---------------------------------------------------------------------------
# Deferred heavy imports (after stubs are in place)
# ---------------------------------------------------------------------------
import lancedb  # noqa: E402  (after stub install)

from transformers import AutoModel  # noqa: E402

try:
    from FlagEmbedding import BGEM3FlagModel  # noqa: E402
    _BGEM3_AVAILABLE = True
except Exception as _bge_exc:
    log.warning("Could not import BGEM3FlagModel: %s  — ColBERT will be skipped.", _bge_exc)
    _BGEM3_AVAILABLE = False
    BGEM3FlagModel = None  # type: ignore[assignment,misc]


# ===========================================================================
# Constants
# ===========================================================================

# Context model is used for CHUNK INDEXING (late chunking — chunks grouped by source doc).
# Standard model is used for QUERY EMBEDDING at search time (in api/server.py).
PPLX_CONTEXT_MODEL_ID = "perplexity-ai/pplx-embed-context-v1-4b"  # for indexing
PPLX_QUERY_MODEL_ID   = "perplexity-ai/pplx-embed-v1-4b"           # for queries (server.py)
# Keep alias for kb_meta backward compat
PPLX_MODEL_ID  = PPLX_CONTEXT_MODEL_ID
BGE_MODEL_ID   = "BAAI/bge-m3"
EMBED_DIM      = 2560    # pplx-embed-context-v1-4B output dimension
COLBERT_DIM    = 1024    # BGE-M3 ColBERT token vector dimension
MAX_SEQ_LEN    = 512     # tokenizer truncation length (not used by context model directly)

# Maximum characters per chunk BEFORE sending to pplx-embed-context.
# The context model's 32K-token window fits ~8000 tokens comfortably, but
# very long chunks (up to 8403 chars in this KB) cause KV-cache OOM.
# 2048 chars ≈ 512 tokens; covers 96.8% of chunks without truncation.
MAX_CONTENT_CHARS = 2048

# IVF-PQ index parameters (tuned for ~5-10K chunks; re-tune for >50K)
# num_partitions ≈ sqrt(N), rounded to a power of 2.
# num_sub_vectors must divide EMBED_DIM evenly.  2560 / 32 = 80 byte vectors.
IVF_NUM_PARTITIONS  = 64
IVF_NUM_SUB_VECTORS = 32   # 2560 / 32 = 80 subvectors of 32 floats each

# SQLite ColBERT write batch
COLBERT_BATCH_SIZE = 500


# ===========================================================================
# ColBERT BLOB serialisation
# ===========================================================================

def colbert_to_blob(matrix: np.ndarray) -> bytes:
    """
    Serialise a ColBERT token matrix to a compact BLOB.

    Format:
      - 4-byte header: uint16 num_tokens, uint16 dim  (little-endian)
      - Raw FP16 bytes: num_tokens * dim * 2 bytes

    The matrix is cast to FP16 before serialisation to halve storage.
    """
    matrix = matrix.astype(np.float16)
    num_tokens, dim = matrix.shape
    header = struct.pack("<HH", num_tokens, dim)
    return header + matrix.tobytes()


def blob_to_colbert(blob: bytes) -> np.ndarray:
    """Deserialise a BLOB written by :func:`colbert_to_blob`."""
    num_tokens, dim = struct.unpack_from("<HH", blob, 0)
    data = np.frombuffer(blob, dtype=np.float16, offset=4)
    return data.reshape(num_tokens, dim)


# ===========================================================================
# LanceDB schema definitions
# ===========================================================================

CONTENT_EMB_SCHEMA = pa.schema([
    pa.field("chunk_id",        pa.string()),
    pa.field("vector",          pa.list_(pa.float32(), EMBED_DIM)),
    pa.field("brand",           pa.string()),
    pa.field("model",           pa.string()),
    pa.field("layer",           pa.string()),
    pa.field("content_type",    pa.string()),
    pa.field("source_language", pa.string()),
    pa.field("title",           pa.string()),
    pa.field("content_snippet", pa.string()),   # first 800 chars of content
    pa.field("is_current",      pa.bool_()),
    pa.field("has_procedures",  pa.bool_()),
    pa.field("has_warnings",    pa.bool_()),
    pa.field("source",          pa.string()),
    pa.field("page_start",      pa.int32()),
])

TITLE_EMB_SCHEMA = pa.schema([
    pa.field("chunk_id", pa.string()),
    pa.field("vector",   pa.list_(pa.float32(), EMBED_DIM)),
])


# ===========================================================================
# pplx-embed-v1-4B encoder
# ===========================================================================

class PplxContextEmbedder:
    """
    Wrapper for pplx-embed-context-v1-4B (late chunking / contextual embeddings).

    Encodes document chunks **grouped by source document** so that each chunk's
    embedding is informed by the surrounding chunks in the same document.
    This is the correct model for KB INDEXING; the standard pplx-embed-v1-4B
    should be used for QUERY embedding at search time (see api/server.py).

    The model's built-in ``encode(doc_groups)`` method handles tokenisation,
    late chunking, and mean-pooling internally — no manual pooling needed.

    Args:
        device:   Target CUDA device string, e.g. ``"cuda:0"``.
        verbose:  Enable debug-level log messages.
    """

    def __init__(
        self,
        device: str = "cuda:0",
        verbose: bool = False,
    ) -> None:
        self.device = device
        self.verbose = verbose

        log.info("Loading pplx-embed-context-v1-4B on %s …", device)
        t0 = time.time()
        self.model = AutoModel.from_pretrained(
            PPLX_CONTEXT_MODEL_ID,
            revision="3597c21f3ad8c8886abf47a9157a5b038b5a6b4f",  # pinned: all 4 shards cached locally
            torch_dtype=torch.float16,
            device_map=device,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )
        self.model.eval()
        log.info(
            "pplx-embed-context-v1-4B loaded in %.1f s  (device=%s)",
            time.time() - t0,
            device,
        )

    # ------------------------------------------------------------------

    def encode_grouped(
        self,
        doc_groups: list[list[str]],
        max_chunks_per_encode: int = 16,
        desc: str = "pplx-ctx-embed",
    ) -> list[np.ndarray]:
        """
        Encode document groups using late chunking.

        Each inner list of *doc_groups* represents all chunks from one source
        document.  The model encodes them together so each chunk's embedding
        is conditioned on its neighbours within the same document.

        Documents with more than *max_chunks_per_encode* chunks are split into
        sequential windows of that size.  Cross-window context is lost, but
        within each window all chunks benefit from mutual context.  This is
        necessary to stay within the model's 32K-token context limit.

        Args:
            doc_groups:            List of document groups.
            max_chunks_per_encode: Max chunks per ``model.encode()`` call.
                                   16 chunks × MAX_CONTENT_CHARS(2048 chars≈512 tok)
                                   ≈ 8K tokens — well within the 32K limit even
                                   for worst-case long chunks.
            desc:                  tqdm progress bar label.

        Returns:
            List of float32 numpy arrays, one per document group.
            ``results[k].shape == (len(doc_groups[k]), 2560)``.
        """
        results: list[np.ndarray] = []
        total_chunks = sum(len(g) for g in doc_groups)
        pbar = tqdm(total=total_chunks, desc=desc, unit="chunk", leave=False)

        for grp in doc_groups:
            if not grp:
                results.append(np.empty((0, EMBED_DIM), dtype=np.float32))
                continue

            if len(grp) <= max_chunks_per_encode:
                # Encode the entire document in one call
                sub_embs = self._call_encode([grp])
                results.append(sub_embs[0])
                pbar.update(len(grp))
            else:
                # Document is too long — split into windows
                windows: list[np.ndarray] = []
                for start in range(0, len(grp), max_chunks_per_encode):
                    window = grp[start : start + max_chunks_per_encode]
                    window_embs = self._call_encode([window])
                    windows.append(window_embs[0])
                    pbar.update(len(window))
                results.append(np.vstack(windows))

        pbar.close()
        return results

    def _call_encode(self, doc_groups: list[list[str]]) -> list[np.ndarray]:
        """
        Call ``model.encode()`` with automatic OOM retry.

        On OOM the CUDA cache is cleared and the call is retried up to 3 times.
        After each successful call the cache is also cleared to prevent
        fragmentation accumulation across sequential window calls.
        """
        for attempt in range(4):
            try:
                with torch.no_grad():
                    batch_embs = self.model.encode(doc_groups)
                # Convert to numpy BEFORE releasing GPU tensors
                results = [np.asarray(e, dtype=np.float32) for e in batch_embs]
                # Explicitly free the GPU tensor references, then compact the
                # allocator pool so the next window starts with a clean slate.
                del batch_embs
                torch.cuda.empty_cache()
                return results
            except RuntimeError as exc:
                if "out of memory" in str(exc).lower():
                    torch.cuda.empty_cache()
                    if attempt < 3:
                        log.warning(
                            "OOM on GPU %s (attempt %d/4) — clearing cache and retrying …",
                            self.device,
                            attempt + 1,
                        )
                    else:
                        raise
                else:
                    raise
        raise RuntimeError("unreachable")


# ===========================================================================
# pplx-embed-v1-4B query encoder  (standard, non-context model)
# ===========================================================================

class PplxQueryEmbedder:
    """
    Wrapper for pplx-embed-v1-4B (standard bi-encoder, no late chunking).

    Used at QUERY TIME in api/server.py.  Takes a flat list of query strings
    and returns a (N, 2560) float32 numpy array.

    Unlike PplxContextEmbedder, this model does NOT need document groups —
    each string is encoded independently.

    Args:
        device: CUDA device, e.g. ``"cuda:0"``.
    """

    def __init__(self, device: str = "cuda:0") -> None:
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415

        self.device = device

        log.info("Loading pplx-embed-v1-4B (query model) on %s …", device)
        t0 = time.time()
        self.model = SentenceTransformer(
            PPLX_QUERY_MODEL_ID,
            device=device,
            trust_remote_code=True,
            local_files_only=True,  # fail fast if not cached; server falls back to context model
        )
        log.info(
            "pplx-embed-v1-4B loaded in %.1f s  (device=%s)",
            time.time() - t0,
            device,
        )

    def encode(
        self,
        texts: list[str],
        batch_size: int = 16,
        desc: str = "pplx-query-embed",
    ) -> np.ndarray:
        """
        Encode *texts* into (N, 2560) float32 vectors.

        The query model accepts a flat list of strings (each encoded
        independently, unlike the context model which needs doc groups).

        Returns:
            float32 numpy array of shape (len(texts), EMBED_DIM).
        """
        result = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(result, dtype=np.float32)


# ===========================================================================
# BGE-M3 ColBERT encoder
# ===========================================================================

class BgeM3Encoder:
    """
    Wrapper for BAAI/bge-m3 that extracts per-token ColBERT vectors.

    Uses FlagEmbedding's BGEM3FlagModel (M3Embedder) with the reranker stubs
    applied at module load time.  ColBERT matrices are returned as FP32 numpy
    arrays; the caller serialises them to FP16 BLOBs via :func:`colbert_to_blob`.

    Args:
        device:     CUDA device string, e.g. ``"cuda:1"``.
        batch_size: Inference batch size passed to BGEM3FlagModel.
        verbose:    Enable debug-level log messages.
    """

    def __init__(
        self,
        device: str = "cuda:1",
        batch_size: int = 16,
        verbose: bool = False,
    ) -> None:
        if not _BGEM3_AVAILABLE:
            raise RuntimeError(
                "BGEM3FlagModel could not be imported.  "
                "Check FlagEmbedding / transformers compatibility."
            )
        self.device = device
        self.verbose = verbose
        self._batch_size = batch_size

        log.info("Loading BGE-M3 on %s …", device)
        t0 = time.time()
        self.model = BGEM3FlagModel(
            BGE_MODEL_ID,
            use_fp16=True,
            normalize_embeddings=True,
            devices=device,
            return_dense=False,
            return_sparse=False,
            return_colbert_vecs=True,
            batch_size=batch_size,
            passage_max_length=MAX_SEQ_LEN,
        )
        log.info("BGE-M3 loaded in %.1f s", time.time() - t0)

    # ------------------------------------------------------------------

    def encode_colbert(
        self,
        texts: list[str],
        batch_size: int | None = None,
        desc: str = "bge-m3 colbert",
    ) -> list[np.ndarray]:
        """
        Encode *texts* and return a list of per-chunk ColBERT token matrices.

        Each matrix has shape ``(num_tokens - 1, 1024)`` (CLS token removed).
        Returns float32 arrays.

        Args:
            texts:      List of strings to encode.
            batch_size: Override the model's default batch size.
            desc:       tqdm progress bar label.

        Returns:
            List of float32 numpy arrays, one per input text.
        """
        bs = batch_size or self._batch_size
        all_matrices: list[np.ndarray] = []
        n = len(texts)
        pbar = tqdm(total=n, desc=desc, unit="chunk", leave=False)

        i = 0
        while i < n:
            batch = texts[i : i + bs]
            try:
                results = self.model.encode(
                    batch,
                    return_dense=False,
                    return_sparse=False,
                    return_colbert_vecs=True,
                )
                colbert_vecs = results["colbert_vecs"]   # list of (T, 1024) arrays
                for mat in colbert_vecs:
                    # Remove the CLS token (first row) — it is a global repr,
                    # not a token-level vector used in MaxSim scoring.
                    mat_np = np.asarray(mat, dtype=np.float32)
                    all_matrices.append(mat_np[1:] if mat_np.shape[0] > 1 else mat_np)
                pbar.update(len(batch))
                i += bs
            except RuntimeError as exc:
                if "out of memory" in str(exc).lower() and bs > 1:
                    torch.cuda.empty_cache()
                    bs = max(1, bs // 2)
                    log.warning(
                        "OOM on GPU %s — halved ColBERT batch size to %d …",
                        self.device,
                        bs,
                    )
                else:
                    pbar.close()
                    raise

        pbar.close()
        return all_matrices


# ===========================================================================
# Database helpers
# ===========================================================================

def load_chunks(db_path: Path) -> list[dict[str, Any]]:
    """
    Read all columns needed for embedding from the ``chunks`` table.

    Returns a list of dicts with keys:
      id, brand, model, layer, content_type, source_language,
      title, content, source, page_start, is_current,
      has_procedures, has_warnings
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id, brand, model, layer, content_type, source_language,
            title, content, source,
            COALESCE(page_start, 0)   AS page_start,
            COALESCE(is_current, 1)   AS is_current,
            COALESCE(has_procedures, 0) AS has_procedures,
            COALESCE(has_warnings, 0)   AS has_warnings
        FROM chunks
        ORDER BY id
        """
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    log.info("Loaded %d chunks from %s", len(rows), db_path)
    return rows


def get_existing_colbert_ids(db_path: Path) -> set[str]:
    """Return the set of chunk_ids already present in colbert_vectors."""
    conn = sqlite3.connect(str(db_path), timeout=60)
    cur = conn.cursor()
    cur.execute("SELECT chunk_id FROM colbert_vectors")
    ids = {row[0] for row in cur.fetchall()}
    conn.close()
    return ids


def save_colbert_vectors(
    db_path: Path,
    chunk_ids: list[str],
    matrices: list[np.ndarray],
    force: bool = False,
) -> int:
    """
    Write ColBERT matrices to the ``colbert_vectors`` table.

    Uses ``INSERT OR IGNORE`` by default, ``INSERT OR REPLACE`` when *force*.
    Writes are batched in transactions of :data:`COLBERT_BATCH_SIZE` rows.

    Returns the number of rows written.
    """
    if len(chunk_ids) != len(matrices):
        raise ValueError(
            f"chunk_ids ({len(chunk_ids)}) and matrices ({len(matrices)}) length mismatch"
        )

    insert_sql = (
        "INSERT OR REPLACE INTO colbert_vectors (chunk_id, colbert_matrix, token_count) VALUES (?,?,?)"
        if force
        else
        "INSERT OR IGNORE INTO colbert_vectors (chunk_id, colbert_matrix, token_count) VALUES (?,?,?)"
    )

    conn = sqlite3.connect(str(db_path), timeout=300)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    cur = conn.cursor()

    def _commit_batch(data: list) -> None:
        """Commit a batch with unlimited retry on 'database is locked'."""
        for attempt in range(9999):
            try:
                cur.executemany(insert_sql, data)
                conn.commit()
                return
            except sqlite3.OperationalError as exc:
                if "locked" in str(exc).lower():
                    wait = min(5 * (attempt + 1), 30)   # 5s, 10s, … max 30s
                    log.warning(
                        "SQLite locked (attempt %d) — retrying in %ds …",
                        attempt + 1, wait,
                    )
                    time.sleep(wait)
                    # Re-open cursor after lock (connection stays open)
                    cur.execute("ROLLBACK")
                else:
                    raise

    written = 0
    batch_data: list[tuple[str, bytes, int]] = []

    pbar = tqdm(
        total=len(chunk_ids),
        desc="colbert→sqlite",
        unit="row",
        leave=False,
    )
    for cid, mat in zip(chunk_ids, matrices):
        blob = colbert_to_blob(mat)
        batch_data.append((cid, blob, mat.shape[0]))
        if len(batch_data) >= COLBERT_BATCH_SIZE:
            _commit_batch(batch_data)
            written += len(batch_data)
            pbar.update(len(batch_data))
            batch_data = []

    if batch_data:
        _commit_batch(batch_data)
        written += len(batch_data)
        pbar.update(len(batch_data))

    pbar.close()
    conn.close()
    return written


# ===========================================================================
# LanceDB helpers
# ===========================================================================

def build_arrow_content_emb(
    chunks: list[dict[str, Any]],
    vectors: np.ndarray,
) -> pa.Table:
    """
    Build the ``content_emb`` PyArrow table from chunk metadata + dense vectors.

    *vectors* must be float32, shape ``(len(chunks), 2560)``.
    """
    n = len(chunks)
    assert vectors.shape == (n, EMBED_DIM), (
        f"vectors shape {vectors.shape} != ({n}, {EMBED_DIM})"
    )

    flat = vectors.flatten().astype(np.float32)
    vec_array = pa.FixedSizeListArray.from_arrays(flat, type=pa.list_(pa.float32(), EMBED_DIM))

    return pa.table(
        {
            "chunk_id":        [c["id"]                         for c in chunks],
            "vector":          vec_array,
            "brand":           [c["brand"]                      for c in chunks],
            "model":           [c["model"]                      for c in chunks],
            "layer":           [c["layer"]                      for c in chunks],
            "content_type":    [c["content_type"]               for c in chunks],
            "source_language": [c["source_language"]            for c in chunks],
            "title":           [c["title"]                      for c in chunks],
            "content_snippet": [c["content"][:800]              for c in chunks],
            "is_current":      [bool(c["is_current"])           for c in chunks],
            "has_procedures":  [bool(c["has_procedures"])       for c in chunks],
            "has_warnings":    [bool(c["has_warnings"])         for c in chunks],
            "source":          [c["source"]                     for c in chunks],
            "page_start":      pa.array(
                                   [int(c["page_start"]) for c in chunks],
                                   type=pa.int32(),
                               ),
        },
        schema=CONTENT_EMB_SCHEMA,
    )


def build_arrow_title_emb(
    chunks: list[dict[str, Any]],
    vectors: np.ndarray,
) -> pa.Table:
    """
    Build the ``title_emb`` PyArrow table (chunk_id + title vector only).

    *vectors* must be float32, shape ``(len(chunks), 2560)``.
    """
    n = len(chunks)
    assert vectors.shape == (n, EMBED_DIM), (
        f"vectors shape {vectors.shape} != ({n}, {EMBED_DIM})"
    )

    flat = vectors.flatten().astype(np.float32)
    vec_array = pa.FixedSizeListArray.from_arrays(flat, type=pa.list_(pa.float32(), EMBED_DIM))

    return pa.table(
        {
            "chunk_id": [c["id"] for c in chunks],
            "vector":   vec_array,
        },
        schema=TITLE_EMB_SCHEMA,
    )


def write_lancedb_tables(
    lancedb_dir: Path,
    content_arrow: pa.Table,
    title_arrow: pa.Table,
    force: bool = False,
) -> lancedb.db.DBConnection:
    """
    Write both LanceDB tables in ``overwrite`` or ``create`` mode.

    Returns the open :class:`lancedb.db.DBConnection`.
    """
    lancedb_dir.mkdir(parents=True, exist_ok=True)

    log.info("Connecting to LanceDB at %s …", lancedb_dir)
    db = lancedb.connect(str(lancedb_dir))

    # Use "overwrite" if --force, or if tables don't exist yet ("create" fails
    # when table already exists; "overwrite" is safe for both cases).
    existing = set(db.table_names())
    if force or ("content_emb" not in existing and "title_emb" not in existing):
        mode = "overwrite"
    else:
        # Tables exist — overwrite to replace with the full fresh encode.
        # pplx-embed always re-encodes all chunks, so overwrite is correct.
        mode = "overwrite"
        log.info("LanceDB tables exist — overwriting with updated embeddings")

    # -- content_emb --
    log.info("Writing content_emb table (%d rows) …", len(content_arrow))
    t0 = time.time()
    tbl_content = db.create_table(
        "content_emb",
        data=content_arrow,
        schema=CONTENT_EMB_SCHEMA,
        mode=mode,
        on_bad_vectors="fill",
        fill_value=0.0,
    )
    log.info(
        "content_emb written in %.1f s  (%d rows)",
        time.time() - t0,
        tbl_content.count_rows(),
    )

    # -- title_emb --
    log.info("Writing title_emb table (%d rows) …", len(title_arrow))
    t0 = time.time()
    tbl_title = db.create_table(
        "title_emb",
        data=title_arrow,
        schema=TITLE_EMB_SCHEMA,
        mode=mode,
        on_bad_vectors="fill",
        fill_value=0.0,
    )
    log.info(
        "title_emb written in %.1f s  (%d rows)",
        time.time() - t0,
        tbl_title.count_rows(),
    )

    return db


def build_indexes(db: lancedb.db.DBConnection, num_rows: int) -> None:
    """
    Build IVF-PQ ANN indexes and scalar indexes on both LanceDB tables.

    IVF-PQ parameters are adjusted down automatically when the dataset is
    smaller than the expected minimum (num_partitions * sample_rate rows).
    Scalar indexes on ``brand`` and ``source_language`` speed up pre-filtered
    searches by brand or language in the API layer.
    """
    # For small datasets reduce num_partitions so training converges.
    # Default sample_rate=256 → need at least num_partitions * 256 rows.
    num_partitions = IVF_NUM_PARTITIONS
    min_rows_needed = num_partitions * 256
    if num_rows < min_rows_needed:
        # Pick the largest power-of-2 partition count that fits
        q = max(1, num_rows // 256)
        num_partitions = max(1, 1 << max(0, q.bit_length() - 1))
        if num_partitions == 0:
            num_partitions = 1
        log.warning(
            "Dataset has only %d rows — reducing IVF partitions from %d to %d",
            num_rows,
            IVF_NUM_PARTITIONS,
            num_partitions,
        )

    ivf_kwargs = dict(
        metric="cosine",
        num_partitions=num_partitions,
        num_sub_vectors=IVF_NUM_SUB_VECTORS,
        index_type="IVF_PQ",
        vector_column_name="vector",
        replace=True,
    )

    for tbl_name in ("content_emb", "title_emb"):
        log.info("Building IVF-PQ index on %s …", tbl_name)
        t0 = time.time()
        tbl = db.open_table(tbl_name)
        tbl.create_index(**ivf_kwargs)
        log.info("  IVF-PQ on %s done in %.1f s", tbl_name, time.time() - t0)

    # Scalar indexes — only on content_emb (has the metadata columns)
    tbl_content = db.open_table("content_emb")
    for col in ("brand", "source_language"):
        log.info("Building scalar index on content_emb.%s …", col)
        t0 = time.time()
        tbl_content.create_scalar_index(col)
        log.info("  scalar index on %s done in %.1f s", col, time.time() - t0)


# ===========================================================================
# Verification
# ===========================================================================

def verify_search(db: lancedb.db.DBConnection, n_results: int = 5) -> None:
    """
    Run a random-vector query against both tables and log the top results.

    This is a sanity check that the IVF-PQ index is operational and returns
    results.  A RuntimeError is raised if no results are returned.
    """
    log.info("--- Verification: random-query search test ---")
    query_vec = np.random.rand(EMBED_DIM).astype(np.float32)

    for tbl_name in ("content_emb", "title_emb"):
        tbl = db.open_table(tbl_name)
        results = tbl.search(query_vec).limit(n_results).to_list()
        if not results:
            raise RuntimeError(
                f"Verification FAILED: search on {tbl_name} returned 0 results"
            )
        top = results[0]
        chunk_id = top.get("chunk_id", "?")
        dist = top.get("_distance", float("nan"))
        log.info("  %s  → top-1: chunk_id=%s  dist=%.4f", tbl_name, chunk_id, dist)

    log.info("--- Verification passed ---")


# ===========================================================================
# Main build function
# ===========================================================================

def build_embeddings(
    db_path: Path,
    lancedb_dir: Path,
    batch_size: int = 32,
    pplx_device: str = "cuda:0",
    bge_device: str = "cuda:1",
    force: bool = False,
    skip_colbert: bool = False,
    skip_dense: bool = False,
    verbose: bool = False,
) -> None:
    """
    Full embedding pipeline.

    Steps:
     1. Load chunks from SQLite.
     2. Group chunks by source document.
     3. Load pplx-embed-context-v1-4B on *pplx_device* (late chunking).
     4. Encode title+content → content vectors (2560d, contextual).
     5. Encode title        → title vectors   (2560d, contextual).
     6. Flatten embeddings back to original chunk order.
     7. Write content_emb + title_emb LanceDB tables.
     6. Load BGE-M3 on *bge_device* (unless *skip_colbert*).
     7. Encode content → ColBERT token matrices.
     8. Write ColBERT BLOBs to SQLite colbert_vectors.
     9. Build IVF-PQ and scalar indexes on LanceDB.
    10. Verify with random-query search test.
    11. Print statistics.
    """
    t_start = time.time()
    stats: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # 1. Load chunks
    # ------------------------------------------------------------------
    log.info("=" * 62)
    log.info("  STEP 1: Loading chunks from %s", db_path)
    log.info("=" * 62)
    chunks = load_chunks(db_path)
    n = len(chunks)
    stats["total_chunks"] = n
    if n == 0:
        log.error("No chunks found in %s — aborting.", db_path)
        sys.exit(1)

    # Pre-compute flat text lists for grouping.
    # Content is truncated to MAX_CONTENT_CHARS so that even the longest chunks
    # (max 8 403 chars in this KB) stay within the pplx-context model's 32K
    # token window when combined in late-chunking windows.
    # 96.8% of chunks are ≤2 048 chars → almost no quality loss.
    content_texts = [
        f"{c['title']}\n\n{c['content'][:MAX_CONTENT_CHARS]}" for c in chunks
    ]
    title_texts = [c["title"] for c in chunks]

    # Group chunk indices by source document (preserving original order)
    log.info("Grouping %d chunks by source document …", n)
    _seen_sources: dict[str, int] = {}
    _group_indices: list[list[int]] = []   # [group_k] = [orig_idx, ...]
    for orig_idx, chunk in enumerate(chunks):
        src = chunk["source"]
        if src not in _seen_sources:
            _seen_sources[src] = len(_group_indices)
            _group_indices.append([])
        _group_indices[_seen_sources[src]].append(orig_idx)

    num_docs = len(_group_indices)
    log.info(
        "  → %d unique source documents, %.1f chunks/doc avg",
        num_docs,
        n / max(1, num_docs),
    )

    doc_groups_content = [
        [content_texts[i] for i in grp] for grp in _group_indices
    ]
    doc_groups_title = [
        [title_texts[i] for i in grp] for grp in _group_indices
    ]

    # ------------------------------------------------------------------
    # 2–5. pplx-embed-context encoding + LanceDB write  [skippable]
    # ------------------------------------------------------------------
    if skip_dense:
        log.info("--skip-dense: reusing existing LanceDB tables at %s", lancedb_dir)
        db = lancedb.connect(str(lancedb_dir))
        stats["content_enc_time"]  = 0.0
        stats["title_enc_time"]    = 0.0
        stats["lancedb_write_time"] = 0.0
    else:
        log.info("=" * 62)
        log.info("  STEP 2-4: pplx-embed-context-v1-4B encoding on %s", pplx_device)
        log.info("=" * 62)

        ctx_pplx = PplxContextEmbedder(device=pplx_device, verbose=verbose)

        t_enc = time.time()
        log.info(
            "Encoding content vectors (late chunking, title+content) for %d docs …",
            num_docs,
        )
        content_embs_by_doc = ctx_pplx.encode_grouped(
            doc_groups_content,
            desc="pplx-ctx content",
        )
        stats["content_enc_time"] = time.time() - t_enc
        log.info("Content vectors encoded in %.1f s", stats["content_enc_time"])

        t_enc = time.time()
        log.info("Encoding title vectors (late chunking) for %d docs …", num_docs)
        title_embs_by_doc = ctx_pplx.encode_grouped(
            doc_groups_title,
            desc="pplx-ctx titles",
        )
        stats["title_enc_time"] = time.time() - t_enc
        log.info("Title vectors encoded in %.1f s", stats["title_enc_time"])

        # Flatten back to original chunk order
        content_vecs = np.zeros((n, EMBED_DIM), dtype=np.float32)
        title_vecs   = np.zeros((n, EMBED_DIM), dtype=np.float32)
        for k, grp in enumerate(_group_indices):
            for j, orig_idx in enumerate(grp):
                content_vecs[orig_idx] = content_embs_by_doc[k][j]
                title_vecs[orig_idx]   = title_embs_by_doc[k][j]

        log.info(
            "Flattened: content_vecs=%s  title_vecs=%s",
            content_vecs.shape,
            title_vecs.shape,
        )

        # Free GPU memory before loading BGE-M3
        del ctx_pplx, content_embs_by_doc, title_embs_by_doc
        torch.cuda.empty_cache()

        # ------------------------------------------------------------------
        # 5. Write LanceDB tables
        # ------------------------------------------------------------------
        log.info("=" * 62)
        log.info("  STEP 5: Writing LanceDB tables to %s", lancedb_dir)
        log.info("=" * 62)

        # Sanitise: replace NaN/Inf with 0 before building Arrow arrays.
        nan_content = int(np.isnan(content_vecs).any(axis=1).sum())
        nan_title   = int(np.isnan(title_vecs).any(axis=1).sum())
        if nan_content or nan_title:
            log.warning(
                "NaN vectors detected: content=%d  title=%d — replacing with zeros",
                nan_content, nan_title,
            )
        content_vecs = np.nan_to_num(content_vecs, nan=0.0, posinf=0.0, neginf=0.0)
        title_vecs   = np.nan_to_num(title_vecs,   nan=0.0, posinf=0.0, neginf=0.0)

        content_arrow = build_arrow_content_emb(chunks, content_vecs)
        title_arrow   = build_arrow_title_emb(chunks, title_vecs)

        t_write = time.time()
        db = write_lancedb_tables(lancedb_dir, content_arrow, title_arrow, force=force)
        stats["lancedb_write_time"] = time.time() - t_write

        # Free arrow tables from RAM
        del content_arrow, title_arrow, content_vecs, title_vecs

    # ------------------------------------------------------------------
    # 6–8. BGE-M3 ColBERT encoding + SQLite write
    # ------------------------------------------------------------------
    if skip_colbert or not _BGEM3_AVAILABLE:
        reason = "disabled by --skip-colbert" if skip_colbert else "BGEM3 unavailable"
        log.info("Skipping ColBERT encoding (%s).", reason)
        stats["colbert_encoded"] = 0
        stats["colbert_written"] = 0
    else:
        log.info("=" * 62)
        log.info("  STEP 6-8: BGE-M3 ColBERT encoding on %s", bge_device)
        log.info("=" * 62)

        # Determine which chunks still need encoding (resume-friendly)
        if force:
            # Wipe existing ColBERT rows
            log.info("--force: deleting all existing colbert_vectors rows …")
            conn_tmp = sqlite3.connect(str(db_path))
            conn_tmp.execute("DELETE FROM colbert_vectors")
            conn_tmp.commit()
            conn_tmp.close()
            pending_chunks = chunks
        else:
            existing_ids = get_existing_colbert_ids(db_path)
            pending_chunks = [c for c in chunks if c["id"] not in existing_ids]
            skipped = n - len(pending_chunks)
            if skipped:
                log.info(
                    "Skipping %d chunks already in colbert_vectors (use --force to re-encode).",
                    skipped,
                )

        stats["colbert_encoded"] = len(pending_chunks)

        if pending_chunks:
            bge = BgeM3Encoder(
                device=bge_device,
                batch_size=max(1, batch_size // 2),  # ColBERT is heavier
                verbose=verbose,
            )

            pending_texts = [c["content"] for c in pending_chunks]
            pending_ids   = [c["id"]      for c in pending_chunks]

            t_enc = time.time()
            log.info("Encoding ColBERT vectors for %d chunks …", len(pending_chunks))
            matrices = bge.encode_colbert(
                pending_texts,
                desc="bge-m3 colbert",
            )
            stats["colbert_enc_time"] = time.time() - t_enc
            log.info(
                "ColBERT encoded %d matrices in %.1f s",
                len(matrices),
                stats["colbert_enc_time"],
            )

            del bge
            torch.cuda.empty_cache()

            t_write = time.time()
            log.info("Writing ColBERT BLOBs to SQLite …")
            written = save_colbert_vectors(db_path, pending_ids, matrices, force=force)
            stats["colbert_written"]    = written
            stats["colbert_write_time"] = time.time() - t_write
            log.info(
                "ColBERT: %d rows written in %.1f s",
                written,
                stats["colbert_write_time"],
            )
            del matrices

        else:
            log.info("No new ColBERT vectors to encode.")
            stats["colbert_written"] = 0

    # ------------------------------------------------------------------
    # 9. Build LanceDB indexes
    # ------------------------------------------------------------------
    log.info("=" * 62)
    log.info("  STEP 9: Building LanceDB indexes")
    log.info("=" * 62)

    t_idx = time.time()
    build_indexes(db, num_rows=n)
    stats["index_build_time"] = time.time() - t_idx

    # ------------------------------------------------------------------
    # 10. Verification
    # ------------------------------------------------------------------
    log.info("=" * 62)
    log.info("  STEP 10: Verification")
    log.info("=" * 62)

    try:
        verify_search(db)
        stats["verification"] = "PASSED"
    except Exception as exc:
        stats["verification"] = f"FAILED: {exc}"
        log.error("Verification failed: %s", exc)

    # ------------------------------------------------------------------
    # 11. Update kb_meta in SQLite
    # ------------------------------------------------------------------
    build_ts = datetime.now(timezone.utc).isoformat()
    conn_meta = sqlite3.connect(str(db_path), timeout=300)
    colbert_count = conn_meta.execute(
        "SELECT COUNT(*) FROM colbert_vectors"
    ).fetchone()[0]
    meta_rows = [
        ("embeddings_build_timestamp", build_ts),
        ("pplx_model_id",             PPLX_CONTEXT_MODEL_ID),
        ("pplx_query_model_id",       PPLX_QUERY_MODEL_ID),
        ("bge_model_id",              BGE_MODEL_ID),
        ("embed_dim",                 str(EMBED_DIM)),
        ("colbert_dim",               str(COLBERT_DIM)),
        ("colbert_vectors_count",     str(colbert_count)),
        ("lancedb_dir",               str(lancedb_dir)),
        ("embedder_version",          "2.0.0"),
    ]
    for attempt in range(9999):
        try:
            conn_meta.executemany(
                "INSERT OR REPLACE INTO kb_meta (key, value) VALUES (?,?)",
                meta_rows,
            )
            conn_meta.commit()
            break
        except sqlite3.OperationalError as exc:
            if "locked" in str(exc).lower():
                wait = min(5 * (attempt + 1), 30)
                log.warning("kb_meta write locked (attempt %d) — retrying in %ds …", attempt + 1, wait)
                time.sleep(wait)
                conn_meta.execute("ROLLBACK")
            else:
                raise
    conn_meta.close()

    t_total = time.time() - t_start

    # ------------------------------------------------------------------
    # Statistics summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 62)
    print("  DIAGNOSTICA KB EMBEDDINGS COMPLETE")
    print("=" * 62)
    print(f"  DB path         : {db_path}")
    print(f"  LanceDB dir     : {lancedb_dir}")
    print(f"  Build timestamp : {build_ts}")
    print(f"  Total chunks    : {stats['total_chunks']:,}")
    print()
    print(f"  pplx content enc: {stats.get('content_enc_time', 0):.1f} s")
    print(f"  pplx title enc  : {stats.get('title_enc_time',   0):.1f} s")
    print(f"  LanceDB write   : {stats.get('lancedb_write_time', 0):.1f} s")
    print(f"  ColBERT encoded : {stats.get('colbert_encoded', 0):,} chunks")
    print(f"  ColBERT written : {stats.get('colbert_written', 0):,} rows")
    if "colbert_enc_time" in stats:
        print(f"  ColBERT enc     : {stats['colbert_enc_time']:.1f} s")
    if "colbert_write_time" in stats:
        print(f"  ColBERT SQLite  : {stats['colbert_write_time']:.1f} s")
    print(f"  Index build     : {stats.get('index_build_time', 0):.1f} s")
    print(f"  Total time      : {t_total:.1f} s")
    print(f"  Verification    : {stats.get('verification', '?')}")
    print()
    print(f"  colbert_vectors in SQLite: {colbert_count:,}")
    print("=" * 62 + "\n")


# ===========================================================================
# CLI entry-point
# ===========================================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build dense vector embeddings for the LLCAR Diagnostica KB.  "
            "Writes LanceDB tables (content_emb, title_emb) and ColBERT "
            "BLOBs to the existing SQLite knowledge base."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help=(
            "Path to kb.db.  "
            "Defaults to <script_parent>/../knowledge-base/kb.db"
        ),
    )
    parser.add_argument(
        "--lancedb-dir",
        default=None,
        help=(
            "Directory for LanceDB tables.  "
            "Defaults to <script_parent>/../knowledge-base/lancedb"
        ),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="pplx-embed inference batch size (ColBERT uses half this value).",
    )
    parser.add_argument(
        "--pplx-device",
        default="cuda:0",
        help="CUDA device for pplx-embed-v1-4B.",
    )
    parser.add_argument(
        "--bge-device",
        default="cuda:1",
        help="CUDA device for BGE-M3 (ColBERT).",
    )
    parser.add_argument(
        "--skip-colbert",
        action="store_true",
        default=False,
        help="Skip BGE-M3 ColBERT encoding (encode dense vectors only).",
    )
    parser.add_argument(
        "--skip-dense",
        action="store_true",
        default=False,
        help=(
            "Skip pplx-embed-context encoding and LanceDB write.  "
            "Assumes LanceDB tables already exist.  "
            "Useful to resume after a ColBERT-only failure without re-encoding."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help=(
            "Overwrite existing LanceDB tables and delete all ColBERT rows "
            "before re-encoding.  Without this flag the script is idempotent."
        ),
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
    script_dir   = Path(__file__).resolve().parent
    project_root = script_dir.parent

    db_path = (
        Path(args.db_path).resolve()
        if args.db_path
        else project_root / "knowledge-base" / "kb.db"
    )
    lancedb_dir = (
        Path(args.lancedb_dir).resolve()
        if args.lancedb_dir
        else project_root / "knowledge-base" / "lancedb"
    )

    log.info("Project root : %s", project_root)
    log.info("DB path      : %s", db_path)
    log.info("LanceDB dir  : %s", lancedb_dir)
    log.info("pplx device  : %s", args.pplx_device)
    log.info("BGE device   : %s", args.bge_device)
    log.info("Batch size   : %d", args.batch_size)
    log.info("Force        : %s", args.force)
    log.info("Skip ColBERT : %s", args.skip_colbert)
    log.info("Skip Dense   : %s", args.skip_dense)

    if not db_path.is_file():
        log.error("kb.db not found at %s", db_path)
        return 1

    if not torch.cuda.is_available():
        log.error(
            "CUDA is not available.  This script requires at least one GPU.  "
            "Check your PyTorch installation and CUDA drivers."
        )
        return 1

    n_gpus = torch.cuda.device_count()
    log.info("CUDA GPUs available: %d", n_gpus)
    for i in range(n_gpus):
        props = torch.cuda.get_device_properties(i)
        free_b, total_b = torch.cuda.mem_get_info(i)
        log.info(
            "  GPU %d: %s  |  total %.1f GB  |  free %.1f GB",
            i,
            props.name,
            total_b / 1e9,
            free_b / 1e9,
        )

    build_embeddings(
        db_path=db_path,
        lancedb_dir=lancedb_dir,
        batch_size=args.batch_size,
        pplx_device=args.pplx_device,
        bge_device=args.bge_device,
        force=args.force,
        skip_colbert=args.skip_colbert,
        skip_dense=args.skip_dense,
        verbose=args.verbose,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
