"""
ColBERT re-encoding for merged chunks using sentence-transformers.
Compatible with transformers 5.x (unlike FlagEmbedding).

Usage:
    python scripts/reindex_colbert_st.py [--device cuda:0] [--db PATH]
"""

import sqlite3
import sys
import os
import time
import numpy as np

DB_PATH = os.environ.get(
    "KB_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db"),
)


def load_model(device="cuda:0"):
    """Load BGE-M3 via sentence-transformers."""
    from sentence_transformers import SentenceTransformer
    print(f"Loading BGE-M3 on {device}...")
    t0 = time.time()
    model = SentenceTransformer("BAAI/bge-m3", device=device)
    print(f"  Loaded in {time.time() - t0:.1f}s")
    return model


def encode_colbert_st(model, texts, batch_size=32):
    """Encode texts to token-level embeddings (ColBERT-style)."""
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # sentence-transformers encode returns sentence embeddings by default
        # For token-level (ColBERT), we need to use the underlying model
        features = model.tokenize(batch)
        features = {k: v.to(model.device) for k, v in features.items()}

        import torch
        with torch.no_grad():
            output = model.forward(features)

        # token_embeddings shape: (batch, seq_len, hidden_dim)
        token_embs = output.get("token_embeddings")
        if token_embs is None:
            # Fallback: use last_hidden_state from the model
            token_embs = output.get("last_hidden_state", None)

        if token_embs is not None:
            attention_mask = features["attention_mask"]
            for j in range(len(batch)):
                mask = attention_mask[j].bool()
                vecs = token_embs[j][mask].cpu().numpy()
                # Normalize each token vector
                norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                norms[norms == 0] = 1
                vecs = vecs / norms
                all_vectors.append(vecs)
        else:
            # Last resort: use sentence embedding repeated
            embs = model.encode(batch, normalize_embeddings=True)
            for emb in embs:
                all_vectors.append(emb.reshape(1, -1))

        if (i + batch_size) % 100 == 0:
            print(f"  Encoded {min(i + batch_size, len(texts))}/{len(texts)}")
    return all_vectors


def vectors_to_blob(vecs):
    """Convert numpy array to FP16 blob for SQLite storage."""
    fp16 = vecs.astype(np.float16)
    return fp16.tobytes()


def main():
    device = "cuda:0"
    for i, arg in enumerate(sys.argv):
        if arg == "--device" and i + 1 < len(sys.argv):
            device = sys.argv[i + 1]

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
    model = load_model(device)

    # Encode
    chunk_ids = [m[0] for m in merged]
    texts = [m[1] for m in merged]

    print(f"Encoding {len(texts)} texts...")
    t0 = time.time()
    vectors = encode_colbert_st(model, texts, batch_size=32)
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
