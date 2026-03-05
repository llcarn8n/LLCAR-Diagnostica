# LLCAR Diagnostica — Transfer to New Machine

## What's already on HuggingFace Hub (nothing to copy)

| What | HF ID | Size |
|------|-------|------|
| Fine-tuned translation model (R6, BLEU=13.39) | `Petr117/m2m-diagnostica-automotive` | ~2.4 GB |
| Training pairs (20,900 pairs) | `Petr117/diagnostica-training-pairs` | ~50 MB |

These will be downloaded automatically from HF.

---

## What to copy (heavy files, ~7 GB total)

Pack with 7-Zip or robocopy:

```
knowledge-base\kb.db                 4.2 GB  ← main SQLite database
knowledge-base\lancedb\              0.6 GB  ← vector store (LanceDB)
mineru-output\                       2.0 GB  ← PDF images (11,352 files)
```

### Fastest transfer options:
- **USB 3.0 SSD**: ~2 min for 7 GB
- **LAN (gigabit)**: robocopy or scp, ~1-2 min
- **Archive**: `7z a llcar-kb-data.7z knowledge-base\kb.db knowledge-base\lancedb\ mineru-output\`

---

## What to copy (code, ~50 MB)

```
api\                  FastAPI server
frontend\             Web SPA (3D viewer + KB)
scripts\              Build / scrape / embed scripts
deploy\               This deployment guide
package.json          npm dependencies
```

Clone from git if repo exists, otherwise zip and copy.

---

## What to download on new machine (HF models, ~20 GB)

These are downloaded automatically by `deploy.bat` (Step 5), or manually:

```python
from huggingface_hub import snapshot_download

# ColBERT reranker (~2 GB) — REQUIRED
snapshot_download("BAAI/bge-m3")

# Query embeddings (~8 GB) — REQUIRED for search
snapshot_download("perplexity-ai/pplx-embed-v1-4b")

# Document embeddings (~8 GB) — REQUIRED for re-indexing
snapshot_download("perplexity-ai/pplx-embed-context-v1-4b")

# Translation model (~2 GB) — OPTIONAL
snapshot_download("Petr117/m2m-diagnostica-automotive")
```

> Note: If you're only running the API (search), you need pplx-embed-v1-4b + bge-m3.
> The pplx-embed-context-v1-4b is only needed if you rebuild the index.

---

## Step-by-step setup

1. **Copy** the 7 GB data files (see above)
2. **Copy or clone** the code
3. **Run** `deploy\deploy.bat` — it will:
   - Create Python venv
   - Install PyTorch (ask for CUDA version)
   - Install Python packages from `deploy\requirements.txt`
   - Install Three.js (`npm install three`)
   - Download HF models (optional, takes 30-60 min)
4. **Verify**: `python deploy\check_deploy.py`
5. **Start**:
   - Terminal 1: `.venv\Scripts\activate && uvicorn api.server:app --host 0.0.0.0 --port 8000`
   - Terminal 2: `npx http-server -p 8080`
   - Browser: http://localhost:8080/frontend/

---

## Minimum requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 8 GB (one GPU) | 24 GB × 2 |
| RAM | 32 GB | 64 GB |
| Disk (free) | 30 GB | 100 GB |
| CUDA | 11.8+ | 12.1+ |
| Python | 3.11 | 3.12–3.14 |
| OS | Windows 10 | Windows 11 |

---

## Quick check after setup

```bash
python deploy/check_deploy.py
```

Expected output: `All checks passed! App should be ready.`
