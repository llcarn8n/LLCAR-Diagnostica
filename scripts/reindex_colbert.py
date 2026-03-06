"""
Phase 3b: Re-encode ColBERT vectors for merged chunks using BGE-M3.
Run on workstation with GPU.

Usage:
    python scripts/reindex_colbert.py [--device cuda:0] [--db PATH]
"""

import sqlite3
import struct
import sys
import os
import time
import numpy as np

DB_PATH = os.environ.get(
    "KB_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db"),
)


def load_bge_m3(device="cuda:0"):
    """Load BGE-M3 model for ColBERT token encoding."""
    from FlagEmbedding import BGEM3FlagModel
    print(f"Loading BGE-M3 on {device}...")
    t0 = time.time()
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True, device=device)
    print(f"  Loaded in {time.time() - t0:.1f}s")
    return model


def encode_colbert(model, texts, batch_size=32):
    """Encode texts to ColBERT token vectors."""
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        output = model.encode(batch, return_colbert_vecs=True)
        vecs = output["colbert_vecs"]  # list of numpy arrays
        all_vectors.extend(vecs)
        if (i + batch_size) % 100 == 0:
            print(f"  Encoded {min(i + batch_size, len(texts))}/{len(texts)}")
    return all_vectors


def vectors_to_blob(vecs):
    """Convert numpy array to FP16 blob for SQLite storage."""
    fp16 = vecs.astype(np.float16)
    return fp16.tobytes()


def main():
    device = "cuda:0"
    for arg in sys.argv:
        if arg.startswith("--device"):
            device = sys.argv[sys.argv.index(arg) + 1]

    db_path = os.path.abspath(DB_PATH)
    print(f"DB: {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Find merged chunks that need ColBERT vectors
    merged = cur.execute("""
        SELECT id, content FROM chunks
        WHERE source LIKE '%_merged'
        AND id NOT IN (SELECT chunk_id FROM colbert_vectors)
    """).fetchall()

    if not merged:
        print("No merged chunks need ColBERT encoding.")
        conn.close()
        return

    print(f"Found {len(merged)} merged chunks needing ColBERT vectors")

    # Load model
    model = load_bge_m3(device)

    # Encode
    chunk_ids = [m[0] for m in merged]
    texts = [m[1] for m in merged]

    print(f"Encoding {len(texts)} texts...")
    t0 = time.time()
    vectors = encode_colbert(model, texts, batch_size=32)
    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s ({len(texts) / elapsed:.1f} texts/sec)")

    # Store in colbert_vectors table
    print("Storing vectors...")
    for cid, vecs in zip(chunk_ids, vectors):
        blob = vectors_to_blob(vecs)
        cur.execute(
            "INSERT OR REPLACE INTO colbert_vectors (chunk_id, colbert_matrix, token_count) VALUES (?, ?, ?)",
            (cid, blob, vecs.shape[0]),
        )

    conn.commit()

    # Verify
    total_cv = cur.execute("SELECT COUNT(*) FROM colbert_vectors").fetchone()[0]
    print(f"\nDone! ColBERT vectors: {total_cv} total")

    conn.close()


if __name__ == "__main__":
    main()
