# LLCAR — Implementation Plan

**Version:** 3.1
**Updated:** 2026-03-06
**Repository:** https://github.com/llcarn8n/LLCAR-Diagnostica

---

## Current State Summary

### What's Working

| Component | Status | Details |
|-----------|--------|---------|
| **KB Search API** | DONE | FastAPI, 3-stage hybrid (BM25 + dense + ColBERT), port 8000 |
| **Frontend SPA** | DONE | Three.js 3D viewer + KB search + multilingual, port 8080 |
| **Web Control Panel** | DONE | Flask on port 5000, 3-page GUI (home/downloads/scraping) |
| **File Downloaders** | DONE | Telegram (1111 LOC), Web (979), GitHub (454), Torrent (298) |
| **Article Scrapers** | DONE | 22 scrapers (4313 LOC), 15 active sources, 289 articles |
| **Telegram Scraper** | DONE | Telethon, keyword search, thread aggregation, 125 articles |
| **Unified DB** | DONE | All scrapers write to `knowledge-base/kb.db` |
| **SQLite KB** | DONE | 11,872 chunks, 44,623 translations, 2,577 parts |
| **LanceDB Vectors** | DONE | content_emb + title_emb (pplx-embed, 2560d) + image_emb (CLIP) |
| **ColBERT Reranking** | DONE | BGE-M3 token vectors for all chunks |
| **Parts Catalog** | DONE | 2,577 parts, OCR via Qwen2.5-VL, coverage 60/100 |
| **Translation** | DONE | ZH->RU/EN/AR/ES, M2M fine-tuned R6 (BLEU=13.39) |
| **Manuals Export** | DONE | 15 MD files, 11,097 chunks, 10,014 image refs |

### Codebase Stats

| Module | Files | Lines |
|--------|-------|-------|
| `web_control.py` (Flask GUI) | 1 | 3,821 |
| `backend/downloaders/` | 5 | 3,258 |
| `backend/scrapers/` | 22 | 4,313 |
| `backend/utils/` | 5 | ~800 |
| `api/server.py` (FastAPI) | 1 | 1,750+ |
| `frontend/` | 8 | ~3,000 |
| **Total backend** | | **~14,000** |

### Scraped Articles (289 total in `knowledge-base/kb.db`)

| Source | Lang | Count |
|--------|------|-------|
| telegram_lixiangautorussia | RU | 125 |
| drom_reviews | RU | 54 |
| autoreview_ru | RU | 41 |
| carnewschina_en | EN | 37 |
| autochina_blog | RU | 6 |
| carscoops_en | EN | 6 |
| liautocn_news | EN | 5 |
| getcar_ru | RU | 4 |
| kitaec | RU | 4 |
| electrek_en | EN | 2 |
| Others (5 sources) | mixed | 5 |

**Blocked:** drive2.ru (403), autohome.com.cn (geo), dongchedi.com (geo)

---

## Phase 1: Data Completeness (next priority)

> Goal: Make all scraped data searchable through KB API.

### 1.1 Embed 289 web articles into LanceDB
- **Priority:** P0
- **Status:** NOT STARTED
- **Script:** `scripts/build_embeddings.py`
- **Effort:** ~30 min GPU time
- **Why:** Articles exist in DB but aren't searchable via dense vectors. FTS5 finds them, ColBERT can't rerank.

### 1.2 Translate 289 web articles
- **Priority:** P0
- **Status:** NOT STARTED
- **Script:** `scripts/translate_kb.py`
- **Effort:** ~1-2 hours GPU time
- **Why:** Most articles are RU/EN only. Need ZH/AR/ES translations for multilingual search.

### 1.3 Import scraped articles to KB chunks
- **Priority:** P0
- **Status:** PARTIAL (GUI has "Import to KB" button, but 0 imported)
- **File:** `web_control.py` `/api/scrapers/import`
- **Why:** 289 articles sit in `scraped_content` but aren't in `chunks` table yet. Need to convert and insert.

### 1.4 Parts catalog coverage improvement
- **Priority:** P1
- **Status:** 60/100 — 217 diagrams with gaps, ~1,500 missing hotspots
- **Scripts:** `scripts/reocr_missing_parts.py`, `scripts/audit_parts_coverage.py`
- **Blocker:** Remaining gaps are OCR-hard tables (small text, merged cells). Diminishing returns.
- **Target:** 75/100

---

## Phase 2: Downloader Stability (weeks 1-4)

> Goal: Make file downloader production-ready.

### 2.1 Download queue unification
- **Priority:** P0
- **Status:** NOT STARTED (`download_queue.py` exists, 416 LOC, but downloaders aren't integrated)
- **Files:** `downloaders/download_queue.py`, all downloaders
- **Why:** Each downloader runs independently. No unified pause/resume/retry across sources.

### 2.2 Byte-level resume for large files
- **Priority:** P0
- **Status:** NOT STARTED
- **Files:** `downloaders/web_downloader.py`, `downloaders/telegram_downloader.py`
- **Why:** No HTTP Range resume for Web/GitHub. No `iter_download(offset=)` for Telegram. Large files restart from 0.

### 2.3 Standardized error handling & retry
- **Priority:** P1
- **Status:** NOT STARTED
- **Why:** Each downloader has its own retry logic. Need unified `RetryPolicy` with backoff + jitter.

### 2.4 Telegram: video, audio, photo albums
- **Priority:** P1
- **Status:** NOT STARTED
- **Files:** `downloaders/telegram_downloader.py`
- **Why:** Currently only handles documents. Need `MessageMediaPhoto`, `DocumentAttributeVideo/Audio`, `grouped_id`.

---

## Phase 3: Scraping Expansion (weeks 5-8)

> Goal: Grow article database from 289 to 1000+.

### 3.1 More Telegram channels
- **Priority:** P0
- **Status:** BLOCKED — need Telegram API ID/Hash for additional accounts
- **Targets:** Li Auto owner groups (40K+ members), Chinese EV communities
- **Why:** Telegram groups are the richest source of owner experiences.

### 3.2 Drive2.ru via proxy
- **Priority:** P1
- **Status:** BLOCKED — 403 on all methods (IP banned)
- **Need:** Residential proxy or browser automation
- **Why:** Drive2 has thousands of Li Auto owner reviews and repair logs.

### 3.3 Chinese sources via VPN
- **Priority:** P1
- **Status:** BLOCKED — autohome.com.cn, dongchedi.com geo-blocked outside China
- **Need:** Chinese VPN/proxy
- **Why:** Primary source for ZH technical content.

### 3.4 New source scrapers
- **Priority:** P2
- **Status:** NOT STARTED
- **Candidates:** motor1.com, caranddriver.com, youche.com, xchuxing.com
- **Template:** `backend/scrapers/base_scraper.py` (505 LOC) + GUI "Add source" form

---

## Phase 4: Intelligence & UX (weeks 9-14)

> Goal: Smarter search, better user experience.

### 4.1 Browser engine for JS-heavy sites
- **Priority:** P1
- **Status:** NOT STARTED
- **Deps:** playwright, playwright-stealth
- **Why:** ManualsLib, some forums require JS rendering. Stealth fetch covers ~80%, but not all.

### 4.2 AI classification of files
- **Priority:** P1
- **Status:** PARTIAL (`utils/car_brands.py` exists with basic rules)
- **Deps:** rapidfuzz, sentence-transformers (optional)
- **Why:** Auto-tag downloaded files by brand/model/type. Current accuracy ~60%.

### 4.3 Cross-source deduplication
- **Priority:** P2
- **Status:** NOT STARTED
- **Why:** Same manual from Telegram and Web = duplicate. Need MD5 + fuzzy filename matching.

### 4.4 Real-time download dashboard (WebSocket)
- **Priority:** P2
- **Status:** NOT STARTED (current polling via setInterval)
- **Deps:** flask-socketio
- **Why:** Better UX for live download progress, speed/ETA display.

### 4.5 Scheduled auto-updates
- **Priority:** P2
- **Status:** NOT STARTED (`scheduler.py` exists but no incremental scan)
- **Deps:** APScheduler
- **Why:** Auto-scan Telegram channels and web sources for new content daily.

---

## Phase 5: Scale & Translation (weeks 15-20)

> Goal: Expand beyond Li Auto, improve translation quality.

### 5.1 Fine-tuning Round 8+ (M2M translation)
- **Priority:** P2
- **Status:** NOT STARTED (24,058 training pairs available)
- **Current:** Round 6 BLEU=13.39
- **Why:** More training data from parts catalog (3,158 ZH-EN pairs) and new articles.

### 5.2 COMET-KIWI translation evaluation
- **Priority:** P2
- **Status:** NOT STARTED (`scripts/compare_models.py` exists)
- **Why:** Need quality-aware metrics beyond BLEU. COMET-KIWI is reference-free.

### 5.3 Multi-brand expansion
- **Priority:** P3
- **Status:** NOT STARTED
- **Why:** Architecture supports it (brand/model fields in chunks), but all data is Li Auto L7/L9.
- **Candidates:** NIO, XPeng, BYD, Zeekr

### 5.4 Cloud sync
- **Priority:** P3
- **Status:** NOT STARTED
- **Deps:** rclone
- **Why:** Sync downloaded library to Google Drive/S3 for backup.

---

## Known Bugs

| ID | Severity | Description | File |
|----|----------|-------------|------|
| BUG-001 | MAJOR | Hardcoded Telegram creds as fallback | `config.py:89-91` |
| BUG-002 | MINOR | File handle leak (open without with) | `torrent_downloader.py:~1301` |
| BUG-003 | MINOR | Private API `_default_headers` aiohttp | `web_downloader.py:292-293` |
| BUG-004 | MINOR | Old `scraped_articles.db` still in `backend/data/` (orphan, all data in kb.db) | `backend/data/` |
| BUG-005 | MINOR | `debug=False` in Flask — no auto-reload for templates | `web_control.py:3828` |

---

## Architecture

```
scraping-gui.bat
    |
    v
Flask (port 5000) ─── web_control.py (3821 LOC)
    |
    ├── GET /           → home.html (landing page)
    ├── GET /downloads  → panel.html (6-tab file downloader)
    ├── GET /scraping   → scraping.html (article scraper GUI)
    |
    ├── /api/sources, /api/download, /api/status  → downloaders/
    ├── /api/scrapers/*                            → scrapers/
    ├── /api/telegram/*                            → scrapers/telegram_scraper.py
    |
    └── All data → knowledge-base/kb.db (SQLite)

http-server (port 8080) ─── frontend/
    |
    └── GET /frontend/  → SPA (Three.js + KB search)

FastAPI (port 8000) ─── api/server.py
    |
    ├── POST /search    → 3-stage hybrid (BM25 + dense + ColBERT)
    ├── GET /chunk/{id} → single chunk
    ├── GET /dtc/{code} → DTC lookup
    ├── GET /parts/*    → parts catalog
    └── Models: pplx-embed-v1-4b (GPU) + BGE-M3 (CPU/GPU)
```

---

## Dependencies (by phase)

| Package | Phase | Purpose | Required |
|---------|-------|---------|----------|
| flask | current | Web GUI | Yes |
| telethon | current | Telegram scraping | Yes |
| httpx + bs4 | current | Web scraping | Yes |
| trafilatura | current | Content extraction | Yes |
| playwright | 4 | JS rendering | Optional |
| flask-socketio | 4 | WebSocket | Optional |
| rapidfuzz | 4 | Fuzzy matching | Optional |
| APScheduler | 4 | Scheduling | Optional |
| sentence-transformers | 4 | AI classification | Optional |
| rclone | 5 | Cloud sync | Optional |

---

## Principles

1. **Unified DB** — all data in `knowledge-base/kb.db`, no split databases
2. **Separate GUIs** — downloader and scraper are independent pages, not merged
3. **Graceful degradation** — optional deps don't block startup
4. **UTF-8 everywhere** — `PYTHONIOENCODING=utf-8`, io wrappers for Windows
5. **Secrets in .env** — no hardcoded credentials (fix BUG-001)
6. **Test before deploy** — `deploy/check_deploy.py` validates setup
7. **Threaded operations** — downloads and scraping run in parallel via threading
