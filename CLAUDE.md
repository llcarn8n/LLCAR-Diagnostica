# LLCAR Diagnostica KB — Agent Instructions

> This file is for a Claude Code agent on a **new machine**.
> Read this entirely before touching any code.

---

## What This Project Is

**LLCAR Diagnostica** is a knowledge base application for Li Auto L7/L9 vehicle diagnostics.
It consists of:
- A **SQLite + LanceDB knowledge base** with 11,813 chunks from official manuals (ZH/RU/EN)
- A **FastAPI search server** with 3-stage hybrid search (BM25 + dense vectors + ColBERT reranking)
- A **web frontend** with a mobile-style UI, 3D car viewer (Three.js), and KB search screen
- A **fine-tuned M2M translation model** (Round 6, BLEU=13.39) on HuggingFace

The app is already built. Your job is to **get it running on this machine**.

---

## Project Structure

```
LLCAR-Transfer/               ← this folder (copy to e.g. C:/Diagnostica-KB-Package/)
  api/
    server.py                 ← FastAPI server (1750+ lines), runs on port 8000
    config.py                 ← legacy config, not used by server.py directly
    requirements.txt          ← API-specific deps (fastapi, uvicorn, lancedb, numpy)
  frontend/
    index.html                ← SPA entry point (served at /frontend/)
    app.js                    ← main JS controller (ES modules)
    knowledge-base.js         ← KB API client (calls localhost:8000)
    three-viewer.js           ← Three.js 3D model viewer
    screens/
      car-select.js           ← onboarding / vehicle selector
      dashboard.js            ← health overview
      diagnostics.js          ← OBD-II codes + search
      digital-twin.js         ← 3D model view
      knowledge.js            ← KB search screen (uses knowledge-base.js)
      ai-assistant.js         ← AI assistant screen
  scripts/
    build_kb.py               ← build SQLite KB from JSON sections
    build_embeddings.py       ← compute LanceDB vectors (pplx-embed + BGE-M3)
    translate_kb.py           ← translate chunks ZH->RU/EN
    finetune_m2m.py           ← fine-tune M2M translation model
    export_manuals_md.py      ← export manual chunks → knowledge-base/manuals/*.md
    ocr_parts_tables.py       ← Qwen2.5-VL OCR of parts table images → SQLite parts table
    build_parts_bridge.py     ← link parts ↔ glossary ↔ KB ↔ 3D → parts-bridge.json
    gen_l9_catalog.py         ← generate L9 parts catalog MD from OCR content_list
    scrapers/                 ← web scrapers (15 scrapers, 18 sources)
      run_scrapers.py         ← orchestrator, run all scrapers
  deploy/
    deploy.bat                ← SETUP SCRIPT — run this first
    check_deploy.py           ← verify setup is correct
    requirements.txt          ← full Python requirements
    TRANSFER.md               ← transfer checklist
  knowledge-base/
    kb.db                     ← 4.2 GB SQLite: chunks + translations + DTC + glossary
    lancedb/
      content_emb.lance       ← dense vectors (pplx-embed-context-v1-4b, 2560d)
      title_emb.lance         ← title vectors (same model)
      image_emb.lance         ← CLIP image embeddings (ViT-L/14)
    manuals/                  ← 15 MD files + INDEX (11,097 chunks, 10,014 image refs)
    articles/                 ← 18 MD files + INDEX (301 web-scraped articles by source)
    training_pairs_tier1.jsonl   ← 9524 translation pairs (ZH<>EN/RU)
    training_pairs_bridge.jsonl  ← 10606 pairs (EN<>AR/ES via NLLB)
    training_pairs_session15.jsonl ← 770 additional pairs
  mineru-output/              ← 11,352 JPG images extracted from PDFs
  node_modules/
    three/                    ← Three.js 0.182 (already installed, don't re-install)
  package.json
  README-DEPLOY.md
  CLAUDE.md                   ← this file
```

---

## Step 1: Run Setup

```cmd
deploy\deploy.bat
```

This script will:
1. Check Python 3.11+ and Node.js are installed
2. Create `.venv` Python virtual environment
3. Ask your CUDA version → install PyTorch accordingly
4. Install Python packages from `deploy\requirements.txt`
5. Skip Three.js (already in `node_modules/three/`)
6. Optionally download HuggingFace models (~18 GB total)
7. Run `deploy\check_deploy.py` for verification

**CUDA version guide:**
- RTX 30xx/40xx with recent drivers → choose CUDA 12.1 (safest)
- Check your CUDA: `nvidia-smi` → look for "CUDA Version: X.Y"

---

## Step 2: Download HuggingFace Models

If not done in deploy.bat, run manually (needs ~18 GB disk + internet):

```python
from huggingface_hub import snapshot_download

# REQUIRED for search (download in this order — smallest first):
snapshot_download("BAAI/bge-m3")                              # 2 GB — ColBERT reranker
snapshot_download("perplexity-ai/pplx-embed-v1-4b")          # 8 GB — query embeddings
snapshot_download("perplexity-ai/pplx-embed-context-v1-4b")  # 8 GB — doc embeddings (for re-indexing)

# OPTIONAL (translation):
snapshot_download("Petr117/m2m-diagnostica-automotive")       # 2.4 GB — fine-tuned M2M R6
```

Models are cached to `%USERPROFILE%\.cache\huggingface\hub\`.

---

## Step 3: Start the Application

**Terminal 1 — API server:**
```cmd
.venv\Scripts\activate
uvicorn api.server:app --host 0.0.0.0 --port 8000
```
Wait for: `Application startup complete.` (takes 7-15 sec — models loading on GPU)

**Terminal 2 — Web server:**
```cmd
npx http-server -p 8080
```
Must be run from the **project root** (where `package.json` and `node_modules/` are).

**Browser:**
```
http://localhost:8080/frontend/
```

---

## Step 4: Verify Everything Works

```cmd
python deploy\check_deploy.py
```

Expected: `32 passed, 0 warnings, 0 fatal errors`

Manual API test:
```python
import urllib.request, json
body = json.dumps({"query": "brake noise", "lang": "en", "top_k": 3}).encode()
req = urllib.request.Request("http://localhost:8000/search", data=body,
                              headers={"Content-Type": "application/json"})
r = urllib.request.urlopen(req, timeout=15)
print(json.loads(r.read()))
# Expected: {"results": [...], "total": 10, "mode": "hybrid_colbert"}
```

---

## Architecture: How Search Works

```
User query (text)
    │
    ▼
[Stage 1A] FTS5 BM25 fulltext search → top-20 chunk IDs
[Stage 1B] LanceDB dense search (pplx-embed-v1-4b, 2560d) → top-20
[Stage 1C] LanceDB title search → top-20
    │
    ▼ RRF fusion → 20 candidates
    │
[Stage 2] ColBERT MaxSim reranking
          - BGE-M3 token vectors stored in colbert_vectors (SQLite BLOB, FP16)
          - Query encoded with BGE-M3, MaxSim score per candidate
    │
    ▼ top-10 reranked results
    │
[Stage 3] Enrich: fetch full content + translations + metadata from SQLite
    │
    ▼
JSON response: {results: [{chunk_id, title, content, score, layer, model, ...}]}
```

**Search score:** ~0.4-0.6 is good. Below 0.2 = poor match.

---

## Knowledge Base: What's Inside

| Metric | Value |
|--------|-------|
| Total chunks | 11,398 (11,097 manual + 301 web-scraped) |
| Translations (5 langs) | 33,161 rows in chunk_content |
| Languages | ZH (primary), RU, EN, ES, AR |
| Models covered | Li Auto L7, L9, L7+L9 shared |
| Layers | engine, ev, body, interior, brakes, sensors, battery, drivetrain, lighting, chassis, hvac, infotainment, adas, parts |
| DTC codes | 488 linked |
| Glossary terms | 8,597 links (cleaned from 65K) |
| Images captioned | 7,109 |
| Image refs in manuals | 10,014 (100% verified, all files exist on disk) |

**DB Schema (key tables):**
- `chunks` — main content (id, brand, model, source_language, layer, content_type, title, content, ...)
- `chunk_content` — multilingual translations (chunk_id, lang, title, content)
- `colbert_vectors` — BGE-M3 token vectors as FP16 BLOBs
- `chunk_images` — links chunks to extracted PDF images
- `scraped_content` — web-scraped articles (18 sources, 301 items)
- `parts` — OCR-extracted parts catalog (part_number, part_name_zh/en, system, subsystem, hotspot_id)

---

## API Endpoints Reference

All endpoints accept/return JSON.

### `GET /health`
```json
{"status": "ok", "chunks_total": 11813, "lancedb_available": true, ...}
```

### `POST /search` — main search
```json
Request:  {"query": "brake pad replacement", "lang": "en", "top_k": 10,
           "model": "l9",  "layer": "brakes",  "include_translations": false}
Response: {"results": [{
    "chunk_id": "li_auto_l9_zh_a1b2c3d4",
    "title": "...",
    "content": "...",
    "score": 0.52,
    "model": "l9",
    "layer": "brakes",
    "source_language": "zh",
    "page_start": 42,
    "has_procedures": true,
    "has_warnings": false,
    "dtc_codes": [],
    "glossary_terms": ["brake_pad@brakes"],
    "source_url": null
}], "total": 10, "mode": "hybrid_colbert"}
```

### `GET /chunk/{chunk_id}` — fetch single chunk
### `GET /dtc/{code}` — DTC code lookup (e.g. `P0300`, `C0265`)
### `POST /glossary/search` — search glossary terms
### `GET /stats` — detailed KB statistics

### `GET /parts/search` — search parts catalog
```json
Request:  GET /parts/search?q=brake&system=&limit=50
Response: {"query": "brake", "system": "", "total": 12, "results": [
    {"id": 1, "part_number": "X01-12345678", "part_name_zh": "...", "part_name_en": "...",
     "hotspot_id": "1", "system_zh": "...", "system_en": "Service Brake System",
     "subsystem_zh": "...", "subsystem_en": "Front Brake Assembly", "page_idx": 150}
]}
```

### `GET /parts/stats` — parts catalog statistics by system
### `GET /parts/{part_number}` — get part by exact number

---

## Frontend: KB Search Screen

The knowledge screen (`frontend/screens/knowledge.js`) uses `frontend/knowledge-base.js`:

```javascript
const kb = new KnowledgeBase({ apiBase: 'http://localhost:8000' });
await kb.init();                        // checks /health
const results = await kb.search("brake noise", {lang: 'ru'}, 10);
// results.results[0] = {chunk_id, title, content, score, ...}
```

**The importmap** in `index.html` maps `three` → `../../node_modules/three/build/three.module.js`.
From the URL `http://localhost:8080/frontend/`, this resolves to:
`http://localhost:8080/node_modules/three/build/three.module.js`
→ which maps to `<project-root>/node_modules/three/build/three.module.js` ✓

---

## Common Issues and Fixes

### App shows blank page / nothing loads
1. Open browser DevTools → Console tab → look for red errors
2. Check `http://localhost:8080/frontend/app.js` returns 200 (not 404)
   - If 404: `index.html` has wrong script path. Should be `src="app.js"` (not `src="js/app.js"`)
3. Check `http://localhost:8080/node_modules/three/build/three.module.js` returns 200
   - If 404: run `npm install three` from project root

### API not starting
- Check Python venv is activated: `.venv\Scripts\activate`
- Check models exist: `python deploy\check_deploy.py`
- Models load in background thread — wait 15 sec after startup before testing

### API starts but search returns 0 results
- LanceDB may need warm-up: try the query again after 30 sec
- Check `GET /health` → `lancedb_available` should be `true`
- Check `GET /health` → `embed_models_available` should be `true`

### CUDA out of memory
- Two models load: pplx-embed-v1-4b (GPU 0) + BGE-M3 (GPU 1)
- With one GPU: set env `FORCE_CPU_EMBED=1` → slower but works
- With 8 GB VRAM: BGE-M3 fits, pplx-embed may not → use CPU for pplx

### Port already in use
```cmd
# Find what's on port 8000:
netstat -ano | findstr :8000
# Kill it:
taskkill /PID <pid> /F
```

---

## Environment Requirements

| Component | Minimum | Used in source project |
|-----------|---------|----------------------|
| Python | 3.11 | 3.14.2 |
| torch | 2.1 + CUDA 11.8+ | 2.10.0+cu130 |
| CUDA | 11.8 | 13.0 |
| GPU VRAM | 8 GB (1 GPU) | 24 GB × 2 |
| RAM | 32 GB | 128 GB |
| Disk (free) | 30 GB | 376 GB |
| Node.js | 18+ | 25.6.0 |
| OS | Windows 10 | Windows 11 |

---

## HuggingFace Resources (already uploaded)

| Resource | HF ID | Notes |
|----------|-------|-------|
| Fine-tuned translation model (R6, best) | `Petr117/m2m-diagnostica-automotive` | BLEU=13.39, ZH/EN/RU |
| Training pairs (20,900 pairs) | `Petr117/diagnostica-training-pairs` | Tier1 + Bridge datasets |

Base model: `utrobinmv/m2m_translate_en_ru_zh_large_4096`

---

## What Was Already Done (context for next tasks)

### Phase 1 — COMPLETE
- [x] SQLite KB: 11,097 chunks from Li L7/L9 manuals (ZH OCR via MinerU, after cleanup)
- [x] LanceDB: content_emb + title_emb (pplx-embed-context-v1-4b, 2560d) + image_emb (CLIP)
- [x] ColBERT vectors: BGE-M3 token vectors for all chunks
- [x] Translations: ZH->RU/EN/AR/ES for all chunks (33,161 rows in chunk_content)
- [x] Image captioning: 7,109 images captioned with Qwen2.5-VL-7B
- [x] Fine-tuning Round 6: BLEU=13.39 (best), pushed to `Petr117/m2m-diagnostica-automotive`
- [x] Training data: 20,900 pairs pushed to `Petr117/diagnostica-training-pairs`
- [x] API server: 3-stage hybrid search (BM25 + dense + ColBERT), all endpoints tested
- [x] Frontend: SPA with 3D viewer + KB search + multilingual (RU/EN/ZH/AR/ES)
- [x] Web scrapers: 15 scrapers, 301 web-scraped chunks from 18 sources
- [x] 3D self-contained: assets/models/ + frontend/data/architecture/ copied from Diagnostica
- [x] KB-3D bridge mapping: 5-group system (electric, fuel, suspension, cabin, tech)
- [x] System manifest: frontend/data/architecture/system-components.json
- [x] Manuals exported as MD: 15 files in knowledge-base/manuals/ (11,097 chunks, 10,014 image refs)
- [x] Articles exported as MD: 18 files in knowledge-base/articles/ (301 web-scraped by source)
- [x] DB image path fix: 2,312 chunks had absolute paths `C:/Diagnostica-KB-Package/` → fixed to relative

### Web Scraping Infrastructure (scripts/scrapers/)

| Scraper | Source | Lang | Items | Status |
|---------|--------|------|-------|--------|
| carnewschina | carnewschina.com, li-mega tag | EN | 78 | OK |
| cnevpost | cnevpost.com (4 pages pagination) | EN | 60 | OK |
| autoreview | autoreview.ru (7 search queries) | RU | 58 | OK |
| drom_reviews | drom.ru owner reviews L6/L7/L8/L9 (46 reviews) | RU | 48 | OK |
| drom | drom.ru catalog L6/L7/L8/L9/MEGA | RU | 10 | OK |
| kitaec | kitaec.ua Chinese car reviews | RU | 7 | OK |
| carscoops | carscoops.com (paginated) | EN | 6 | OK |
| avtotachki | avtotachki.com search | RU | 6 | OK |
| wikipedia | Wikipedia REST API (EN/RU/ZH) | multi | 10 | OK |
| liautocn_news | ir.lixiang.com press releases | EN | 5 | OK |
| motor_ru | motor.ru search | RU | 3 | OK |
| chinamobil | chinamobil.ru search | RU | 3 | OK |
| electrek | electrek.co, carscoops.com | EN | 2 | OK |
| autostat | autostat.ru search | RU | 2 | OK |
| lixiang_com | lixiang.com | ZH | 2 | OK |
| drive2 | drive2.ru | RU | 0 | 403 blocked |
| autohome | autohome.com.cn | ZH | 0 | geo-blocked |
| dongchedi | dongchedi.com | ZH | 0 | geo-blocked |

**Total: 11,398 chunks** (11,097 manual + 301 web-scraped)

Key technical decisions:
- base_scraper.py uses httpx + BeautifulSoup (not scrapling) for static fetching
- _BS4Page/_BS4Selection classes mimic scrapling CSS API for compatibility
- stealth_fetch falls back: scrapling StealthyFetcher -> patchright -> httpx
- Wikipedia uses REST API (`/api/rest_v1/page/summary/`) to avoid 403 blocks
- All URLs stripped of #fragments before deduplication

### Exported Markdown Files

**Manuals** (`knowledge-base/manuals/`, generated by `scripts/export_manuals_md.py`):
- 15 MD files, one per source (= per original PDF/document)
- 11,097 chunks total, 13 MB on disk
- 10,014 image references (all as relative paths to `mineru-output/`, 100% verified)
- Chunks grouped by layer, ordered by page number
- Includes [PROCEDURE] and [WARNING] badges
- INDEX.md with summary table and descriptions
- Re-generate: `python scripts/export_manuals_md.py`

**Articles** (`knowledge-base/articles/`, generated inline):
- 18 MD files, one per web-scraped source
- 301 articles total from 18 sources (EN/RU/ZH)
- Each file: URL, language, content length, article text (max 3000 chars)
- INDEX.md with source statistics

**DB fix applied**: 2,312 chunks in `chunks.content` contained absolute paths `C:/Diagnostica-KB-Package/mineru-output/...` from the original build machine. Fixed in DB via `REPLACE()` to relative `mineru-output/...`. The export script also has `_fix_content_image_paths()` as safety fallback.

### Parts Catalog Pipeline (scripts/)

**Current state: 2,577 parts in `parts` table, coverage score 60/100**

**OCR extraction** (`scripts/ocr_parts_tables.py`):
- Qwen2.5-VL-7B OCR on 352 table images from L9 parts manual
- Builds page-to-system mapping from content_list.json text entries (22 systems, 415 pages)
- Supports --resume, --dry-run, --limit, --output-log
- Creates/populates `parts` table in kb.db
- Runtime: ~1.5 hours on GPU (352 tables x ~15s each)
- Run: `python scripts/ocr_parts_tables.py` (or `--limit 5 --dry-run` for testing)

**Re-OCR pipeline** (`scripts/reocr_missing_parts.py`):
- Analyzes hotspot gaps per system/diagram and finds entirely missing pages
- Re-runs Qwen2.5-VL on table images with enhanced context-aware prompts
- Only inserts NEW parts (checks part_number + hotspot + page + system)
- Supports `--retry-oom <json>` for retrying failed images with smaller resolution
- Round 1 (max_side=1280): 230 tasks → 98 success, +60 parts
- Round 2 (max_side=768, retry zero-OCR): 132 tasks → 118 success, +31 parts
- Run: `python scripts/reocr_missing_parts.py --device cuda:0 --output-log reocr.jsonl`

**Rendered missing pages** (`scripts/render_missing_pages.py`):
- Uses PyMuPDF to render PDF pages missing from MinerU content_list
- 25 pages were missing — they are single-row table overflows (MinerU skipped them)
- 13 had actual data rows, 6 header-only, 6 blank
- +13 parts inserted directly (no GPU needed — data read visually)
- Run: `python scripts/render_missing_pages.py --ocr --device cuda:0` (or render-only without --ocr)

**Coverage audit** (`scripts/audit_parts_coverage.py`):
- Universal audit tool: hotspot gaps, missing pages, duplicates, system mapping, translations
- Scoring system 0-100, JSON and text output
- `--fix-duplicates` removes exact dupes (749 removed in first run: 3222→2473)
- Run: `python scripts/audit_parts_coverage.py` (or `--fix-duplicates`)

**Parts-KB-3D bridge** (`scripts/build_parts_bridge.py`):
- Connects parts to i18n glossary (1,636 terms), KB chunks, and 3D meshes
- Fuzzy-matches part names (ZH/EN) to glossary IDs
- Maps 22 systems to 5 diagnostic groups (electric/fuel/suspension/cabin/tech)
- Outputs `frontend/data/architecture/parts-bridge.json`
- Run: `python scripts/build_parts_bridge.py` (after ocr_parts_tables.py)

**Training pairs export** (`scripts/export_parts_training_pairs.py`):
- Exports ZH↔EN part name pairs for M2M fine-tuning
- 3,158 pairs from parts catalog → `knowledge-base/training_pairs_parts.jsonl`
- Run: `python scripts/export_parts_training_pairs.py`

**Frontend integration**:
- `knowledge-base.js`: searchParts(), getPartsStats(), getPart() methods
- `screens/knowledge.js`: "Parts" category tab, parts stats overview, parts search
- `screens/digital-twin.js`: shows part numbers in info bar when clicking 3D meshes

### Parts OCR history
| Step | Action | Result |
|------|--------|--------|
| Initial OCR | 352 table images, max_side=1024 | 3,222 raw parts |
| Dedup | Remove 749 exact duplicates | 2,473 parts |
| Re-OCR R1 | Enhanced prompts, max_side=1280 | +60 → 2,533 |
| Re-OCR R2 | Retry zero-OCR, max_side=768 | +31 → 2,564 |
| Rendered pages | 25 missing PDF pages via PyMuPDF | +13 → 2,577 |

### Remaining / Phase 2 tasks
- [x] Run `ocr_parts_tables.py` to populate parts table — DONE (2,577 parts)
- [x] Run `build_parts_bridge.py` to generate parts-bridge.json — DONE
- [x] Deduplicate parts table (749 dupes removed)
- [x] Re-OCR missing parts (rounds 1+2, +91 parts)
- [x] Render missing PDF pages (+13 parts)
- [ ] Coverage still 60/100 — remaining gaps are OCR-hard tables (small text, merged cells)
- [ ] Update `server.py` query embedder to use `pplx-embed-v1-4b` directly (currently uses context model as fallback)
- [ ] COMET-KIWI evaluation on translation cache (`scripts/compare_models.py` exists)
- [ ] Embed 301 new web_scraped chunks into LanceDB (run build_embeddings.py)
- [ ] Translate 301 new web_scraped chunks (run translate_kb.py)
- [ ] Expand to more vehicle brands (Phase 2 in PLAN-KB-v4.2.md)
- [ ] Fine-tuning Round 8+ with expanded training data (24,058 pairs now)
- [ ] Add Chinese sources via VPN/proxy (autohome, dongchedi)
- [ ] Add drive2.ru via residential proxy (blocked by IP)

---

## Quick Start (summary)

```cmd
# 1. Setup (first time only)
deploy\deploy.bat

# 2. Every time
.venv\Scripts\activate
start "API" uvicorn api.server:app --host 0.0.0.0 --port 8000
npx http-server -p 8080

# 3. Open
start http://localhost:8080/frontend/

# 4. Verify
python deploy\check_deploy.py
```
