# LLCAR KB Restructure — Master Plan

> Generated 2026-03-06 by 5 research agents + 3 architect agents
> Cross-review pending (Architect C still working)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [UX Architecture Requirements](#2-ux-architecture-requirements)
3. [Current DB Audit](#3-current-db-audit)
4. [Best Practices Research](#4-best-practices-research)
5. [Architect A: Merge + Restructure](#5-architect-a-merge--restructure)
6. [Architect B: Situational Article Layer](#6-architect-b-situational-article-layer)
7. [Architect C: Pragmatic MVP](#7-architect-c-pragmatic-mvp)
8. [Cross-Review & Synthesis](#8-cross-review--synthesis)
9. [Final Implementation Plan](#9-final-implementation-plan)

---

## 1. Problem Statement

### Core Issue
80% of 11,872 KB chunks are useless to end users:
- 38% < 200 chars (TOC entries, headers, OCR garbage)
- 80% < 500 chars (too short for any useful information)
- Average length: 449 chars (should be 1200-2000)
- 6,704 chunks from MinerU OCR have ALL `page_start=1` (no real page numbers)
- Glossary: 38% of 65,287 links are noise ("car", "manual", "auto", "owner")
- Parts: 14 of 22 systems have ZERO article connections
- User feedback: "статьи выглядят как мусор", "связи единичные"

### What Users Actually Need (from UX Report)
Users don't want manual chapters — they want **situational guidance**:
- ❌ "Двигатель → Масло → Замена"
- ✅ "Загорелся индикатор масла" → Что делать → Пошаговая инструкция → Когда на СТО

---

## 2. UX Architecture Requirements

Source: `LLCAR_UX_Architecture_Report.docx`

### 5 UX Principles

#### Principle 1: Situational Navigation
Articles structured by USER SITUATIONS, not manual sections:
| ❌ Classic | ✅ Situational |
|-----------|----------------|
| Двигатель → Масло → Замена | "Загорелся индикатор масла" → Что делать → Замена → Когда на СТО |
| Тормоза → Колодки → Износ | "Скрип при торможении" → Проверка → Инструкция → Запись на сервис |
| Электрика → АКБ → Зарядка | "Автомобиль не заводится" → Диагностика → АКБ или стартер → Действия |

#### Principle 2: Progressive Disclosure
Two levels for every piece of information:
- **Level 1 — Краткая карточка** (5 сек): что произошло, критичность (🟢/🟡/🔴), одно действие
- **Level 2 — Расширенная статья**: техническое объяснение, пошаговая инструкция с фото/3D, связанные системы, ссылки на мануал

#### Principle 3: Объединение по ситуации
Одна ситуация = несколько систем. Пример "Перегрев двигателя в пробке":
```
├── Охлаждение → антифриз, термостат
├── Двигатель → температура, масло, обороты
├── Электрика → вентилятор радиатора, реле
├── Действия → остановиться → открыть капот → проверить уровень
└── Неопределённость → "Если не помогло → эвакуатор"
```

#### Principle 4: Связь OBD2 → Контент
| OBD2 параметр | Порог | Триггер контента |
|---------------|-------|------------------|
| Coolant temp > 105°C | Критический | "Перегрев двигателя" |
| Oil pressure < 1.0 bar | Критический | "Низкое давление масла" |
| Battery voltage < 12.0V | Предупреждение | "АКБ разряжена" |
| Brake pad wear > 80% | Предупреждение | "Скоро замена колодок" |

#### Principle 5: Поведение в неопределённости
Не паниковать → Дерево решений → Оценка безопасности → Связь с экспертом

### User Personas
| Персона | Возраст | Потребность | Экспертиза |
|---------|---------|-------------|------------|
| Семьянин | 35-50 | "Чтобы не сломалось" | Низкая |
| Энтузиаст | 25-40 | "Хочу понимать машину" | Высокая |
| Молодой водитель | 18-28 | "Что значат индикаторы?" | Минимальная |
| Пенсионер | 60+ | "Когда менять масло" | Низкая-средняя |

### Situation Categories
| Категория | Примеры | Системы |
|-----------|---------|---------|
| 🔴 Экстренные | Перегрев, потеря масла, отказ тормозов | Двигатель + Охлаждение + Тормоза |
| 🟡 Предупреждения | Износ колодок, низкий заряд, расход | Тормоза + Электрика + Топливная |
| 🟢 Плановое ТО | Замена масла, фильтров, свечей | Двигатель + Фильтры + Зажигание |
| 🔵 Сезонные | Зима/лето, шины, антифриз | Ходовая + Охлаждение + Электрика |
| ⚪ Неопределённые | Странный звук, вибрация, Check Engine | Дерево диагностики |

### Information Hierarchy
- **Level 0** — Главный дашборд (always-on KPI: статус, температура, масло, АКБ, пробег до ТО)
- **Level 1** — Система/Компонент (датчики, тренды, связанные ситуации)
- **Level 2** — Ситуационная статья (что/почему/что делать, 3D, глоссарий)
- **Level 3** — Пошаговый wizard (Шаг 1→2→N, "Получилось? Да/Нет", ветвление)

---

## 3. Current DB Audit

### Content Length Distribution (11,872 chunks)
| Threshold | Count | % | Assessment |
|-----------|-------|---|------------|
| < 50 chars | 350 | 3% | Pure garbage |
| < 100 chars | 1,547 | 13% | TOC, single-line headers |
| < 200 chars | 4,550 | 38% | Too short for useful info |
| < 500 chars | 9,551 | 80% | Majority useless |
| < 1000 chars | 11,118 | 94% | Almost everything |
| ≥ 500 chars | 2,321 | 20% | The "good" content |

### Sources — The Fragmentation Problem
| Source | Chunks | Avg chars | Pages | Problem |
|--------|--------|-----------|-------|---------|
| mineru_l7_zh_owners | 3,913 | 223 | ALL p=1 | OCR split into crumbs |
| pdf_l7_zh_full | 2,376 | 326 | 2,376 unique | Granular but has pages |
| mineru_l9_zh_owners | 1,401 | 171 | ALL p=1 | Even smaller crumbs |
| mineru_l9_ru | 1,390 | 678 | ALL p=1 | OK-ish size |
| pdf_l9_ru | 755 | 603 | 483 unique | OK-ish |
| dtc_database | 488 | 206 | — | Fine as-is |
| pdf_l7_zh | 450 | 1,271 | 391 unique | **Best quality** |
| web_l7_zh | 199 | 1,390 | — | Good |
| drom_reviews | 53 | 7,813 | — | **Excellent** user content |

### Content Patterns
| Pattern | Count | % |
|---------|-------|---|
| Procedures (has_procedures=1) | 2,870 | 24% |
| Warnings (has_warnings=1) | 3,260 | 27% |
| Real text ≥500 chars | 2,321 | 20% |
| Headers only <80 chars | 1,078 | 9% |
| TOC entries (".. " + <200) | 44 | 0.4% |

### Situation Tags (already exist!)
| Type | Count |
|------|-------|
| learning | 5,976 |
| maintenance | 2,584 |
| troubleshooting | 1,976 |
| emergency | 1,103 |
| specification | 174 |

### Glossary Quality
- Total links: 65,287
- **Noise (38.2%):** car(4569), owner_s_manual(3659), manual(3356), auto(2512), ang(2327), age(2311), output(2308)
- **Real terms (61.8%):** steering_wheel(911), brake_pedal(684), range_extender(596), rear_view_mirror(546), seat_belt(527)

### Parts ↔ Chunks Gap
14 of 22 parts systems have ZERO chunks mentioning them:
- Autonomous Driving System (16 parts) → 0 chunks
- Closures (Doors, Hood, Tailgate) (225 parts) → 0 chunks
- Passive Safety System (276 parts) → 0 chunks
- Service Brake System (86 parts) → 0 chunks
- Seat System (241 parts) → 0 chunks
- etc.

### Duplicates
- 182 chunks with identical first 100 chars
- Worst: 26 copies of "Настройки" article

---

## 4. Best Practices Research (20 sources, 2024-2025)

### Optimal Chunk Size
- **Target: 1200-2000 chars (300-500 tokens)**
- Current avg 449 chars is critically fragmented
- Evidence: recursive 512-token = 69% accuracy (best of 7 strategies tested)
- Page-level chunking = 0.648 accuracy + lowest variance
- BGE-M3 best at 200-600 tokens for MaxSim scoring
- Procedures can go to 4000 chars as atomic units

### Merge Algorithm (Greedy Consecutive)
1. Group by (source, model, layer, section/page)
2. Sort by page_start / insertion order
3. Greedy merge: accumulate until 1800 chars
4. New chunk boundary on: title change, page jump >2, content_type change
5. Hard max: 2500 chars (procedures: 4000)
6. 50-100 char overlap as context_prefix

### Hierarchical Chunking (Parent/Child)
- **Parent (Level 0):** Full section 2000-4000 chars → display to user, LLM context
- **Child (Level 1):** Merged paragraphs 1200-2000 chars → embedding, retrieval, ColBERT
- New table: chunk_parents

### Context Prefix (Anthropic Contextual Retrieval)
- Prepend `[Li Auto {model} | {layer} | {title}]` before embedding
- Reduces retrieval failures by 35% (Anthropic research)
- Zero-cost structured version vs LLM-generated ($2.75 for 11K chunks)

### Quality Scoring (5 metrics, composite 0-100)
1. Length adequacy (25%): Gaussian at 1500 chars
2. Information density (25%): unique tokens / total tokens
3. Structural completeness (20%): complete thought heuristic
4. Translation alignment (15%): RU/EN length ratio 0.5-2.0
5. Dedup uniqueness (15%): 1 - max(cosine_sim) in same layer

### Dedup Strategy
- Tier 1: SHA256 exact dedup
- Tier 2: Cosine ≥0.90 within (source, layer) → merge or delete
- Tier 3: Cross-source dedup (mineru vs pdf may overlap)

### Special Handling
- **Procedures:** never split mid-step, merge all steps, up to 4000 chars
- **Warnings:** keep atomic, attach small ones (<200) to parent
- **Tables:** keep complete, merge across pages
- **DTC:** keep as-is (488, well-structured)
- **Web articles:** chunk at paragraphs ~1500 chars

### Expected Outcome
- Chunks: 11,800 → 4,000-5,000
- Avg size: 449 → ~1,500 chars
- Retrieval accuracy: +20-35%

### Sources
Firecrawl 2025, arXiv (Rethinking Chunk Size), ACL 2025 (Optimize Chunking Granularity), Milvus, Unstructured, Anthropic Contextual Retrieval, HiChunk (arXiv), LangChain Parent-Child, ColBERTv2, BGE-M3, pplx-embed (Perplexity Research), Mitchell Bryson (RAG Data Quality), NVIDIA NeMo (Semantic Dedup), Microsoft (Multilingual RAG), Weaviate, LangCopilot

---

## 5. Architect A: Merge + Restructure

### Core Idea
Physical merge of fragments into larger chunks + new situations/parts tables.

### Merge Algorithm: Title-Chain Aggregation

**Step 1:** Group by source + normalized title → chunks from same section
**Step 2:** Order by rowid (= insertion order = document order)
**Step 3:** Concatenate adjacent chunks, respecting 3000-char max
**Step 4:** Absorb header-only chunks (<80 chars) into next chunk
**Step 5:** Deduplicate by content_hash or first 100 chars

### Target Structure
| Metric | Before | After |
|--------|--------|-------|
| Active chunks | 11,872 | ~4,500-5,500 |
| Avg content length | 449 | ~1,200-1,800 |
| Headers-only | 1,078 | 0 |
| Duplicates | 182 | 0 |

### New DB Tables

```sql
-- Merge lineage
CREATE TABLE chunk_merge_map (
    original_chunk_id TEXT PRIMARY KEY,
    merged_chunk_id TEXT NOT NULL,
    merge_batch TEXT NOT NULL
);

-- Situations (UX groupings)
CREATE TABLE situations (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,           -- emergency|warning|maintenance|seasonal|uncertain
    urgency INTEGER DEFAULT 1,
    title_ru TEXT NOT NULL,
    title_en TEXT NOT NULL,
    title_zh TEXT,
    description_ru TEXT,
    quick_answer_ru TEXT,
    icon TEXT,
    season TEXT DEFAULT 'all',
    search_queries TEXT,              -- JSON array
    layers TEXT,                      -- JSON array
    sort_order INTEGER DEFAULT 0
);

-- Situation-chunk links
CREATE TABLE situation_chunks (
    situation_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    relevance_score REAL DEFAULT 0.5,
    role TEXT DEFAULT 'detail',       -- quick_answer|procedure|warning|detail|specification
    display_order INTEGER DEFAULT 0,
    PRIMARY KEY (situation_id, chunk_id)
);

-- Parts-chunks bridge
CREATE TABLE parts_chunks (
    part_id INTEGER NOT NULL,
    chunk_id TEXT NOT NULL,
    link_type TEXT NOT NULL,           -- name_match|system_match|glossary_bridge
    confidence REAL DEFAULT 0.5,
    PRIMARY KEY (part_id, chunk_id)
);

-- New columns
ALTER TABLE chunks ADD COLUMN quality_score REAL DEFAULT 0.0;
ALTER TABLE chunks ADD COLUMN merged_from TEXT;
ALTER TABLE chunk_glossary ADD COLUMN weight REAL DEFAULT 1.0;
```

### Glossary Cleanup
Stop-list (~30 terms): car, auto, vehicle, manual, owner, system, component, part, assembly, unit, device, module, element + CJK/RU equivalents.
Frequency filter: terms matching >50% of chunks = noise.
IDF weighting: remaining terms get weight column.
Result: 65,287 → ~35,000-40,000 links.

### Quality Score Formula
```python
quality = (
    0.20 * min(len(content) / 2000, 1.0) +    # length
    0.15 * has_procedures +                      # procedures
    0.10 * has_warnings +                        # warnings
    0.20 * (trust_level / 5.0) +                # trust
    0.15 * min(translation_count / 5, 1.0) +    # translations
    0.10 * (1.0 if page_start > 1 else 0.0) +  # real page number
    0.10 * min(glossary_count / 5, 1.0)         # glossary richness
)
```

Integration into search: `blended = 0.65 * colbert + 0.25 * rrf + 0.10 * quality_score`

### Parts↔Chunks Linking (3 methods)
1. **Name match** (confidence 0.8-1.0): FTS5 search part_name in chunk titles/content
2. **System-layer match** (confidence 0.4-0.6): SYSTEM_TO_KB_LAYERS mapping
3. **Glossary bridge** (confidence 0.6-0.8): shared glossary terms between part and chunk

### Situation Generation
- Seed 9 situations from existing SITUATION_CLUSTERS in knowledge-v2.js
- Auto-generate 20-30 more from situation_tags groupings (layer + situation_type + events)
- Link chunks via FTS5 search + tag matching
- Assign roles: warning, procedure, specification, detail, quick_answer

### Migration Phases
```
Phase 0: Backup (5 min)
Phase 1: Cleanup — dedup + absorb headers + glossary (30 min)
Phase 2: Merge fragments — title-chain aggregation (2 hours)
Phase 3: Quality scoring (5 min)
Phase 4: Situations + Parts bridge (30 min)
Phase 5: Re-embed merged chunks (2-4 hours GPU)
```

Rollback: soft-delete (is_current=0), chunk_merge_map for lineage.

---

## 6. Architect B: Situational Article Layer

### Core Idea
Don't merge chunks — add a **virtual article layer** on top. Articles are metadata/recipes, content stays in chunks.

### Key Insight
> "There is no 'article' entity in the system. The DB has only chunks and the frontend has only hardcoded cluster definitions. The gap is the missing article abstraction."

### Architecture: Virtual Article Assembly

```
articles (manifest)
    ├── article_chunks (composition recipe)
    │     ├── chunk_1 (section: "what_happened", display: full)
    │     ├── chunk_2 (section: "diagnostics", display: full)
    │     ├── chunk_3 (section: "steps", display: full)
    │     └── chunk_4 (section: "warnings", display: quote)
    ├── article_parts (linked parts)
    │     ├── X01-12345678 (primary)
    │     └── X01-23456789 (consumable)
    └── metadata (title, summary, template, urgency, ...)
```

### 6 Article Templates
| Template | Sections |
|----------|----------|
| `troubleshooting` | What happened / Why / Diagnostics checklist / What to do / When to service / Parts / DTC |
| `maintenance` | When to do / What you need / Step-by-step / Warnings / Intervals / Parts list |
| `emergency` | STOP banner / Immediate actions / Do NOT do / Call support / DTC / 3D view |
| `learning` | How it works / Key specs / Tips / Glossary / Related systems |
| `comparison` | L7 vs L9 differences / Specs table / Recommendations |
| `specification` | Specs table / Torque values / Fluid types / Capacities |

### DB Schema

```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    template TEXT NOT NULL,
    model TEXT,
    layer TEXT NOT NULL,
    layers TEXT,                       -- JSON array
    urgency INTEGER DEFAULT 1,
    season TEXT DEFAULT 'all',
    title_ru TEXT NOT NULL,
    title_en TEXT,
    title_zh TEXT,
    summary_ru TEXT NOT NULL,          -- 1-2 sentences for card
    summary_en TEXT,
    quick_answer_ru TEXT,              -- immediate advice
    quick_answer_en TEXT,
    search_queries TEXT,               -- JSON array
    decision_tree_id TEXT,
    related_articles TEXT,             -- JSON array of article IDs
    dtc_codes TEXT,                    -- JSON array
    glossary_ids TEXT,                 -- JSON array for 3D
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE article_chunks (
    article_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    section TEXT NOT NULL,             -- what_happened|diagnostics|steps|warnings|specs|detail
    sort_order INTEGER DEFAULT 0,
    display_mode TEXT DEFAULT 'full',  -- full|summary|quote|hidden
    PRIMARY KEY (article_id, chunk_id, section)
);

CREATE TABLE article_parts (
    article_id TEXT NOT NULL,
    part_number TEXT NOT NULL,
    relevance TEXT DEFAULT 'related',  -- primary|consumable|tool|related
    PRIMARY KEY (article_id, part_number)
);
```

### Search: Stage 4 — Article Elevation
```
Stage 1-3: Existing hybrid search → top-10 chunks
Stage 4 (NEW): Check article_chunks for each result chunk
  → If 5 chunks belong to same article, show ARTICLE once at top
  → Orphan chunks shown below
```

Response format:
```json
{
  "articles": [{"id": "art_brake_noise", "title": "Скрип при торможении", "chunk_count": 8, "score": 0.72}],
  "orphan_chunks": [{"chunk_id": "...", "score": 0.45}]
}
```

New endpoints: `GET /article/{slug}`, `POST /articles/browse`

### Article Creation Pipeline
1. **Convert SITUATION_CLUSTERS** (9 existing) → article records
2. **Auto-compose from situation_tags** → group by (layer, situation_type), 3+ chunks = candidate
3. **Assign chunks to sections** by heuristics: has_warnings→warnings, has_procedures→steps, DTC→diagnostics
4. **Link parts** via layer-to-group mapping from parts-bridge.json
5. **LLM summaries** (Phase 2): generate summary_ru, quick_answer_ru per article

### 3D Integration
- Article has `glossary_ids[]` → "Show in 3D" highlights ALL relevant components
- 3D click → query `article_chunks JOIN chunk_glossary` → get curated articles (not raw fragments)
- Parts overlay: article_parts → display part numbers on 3D model

### Migration Strategy: ADDITIVE, NOT DESTRUCTIVE
- Chunks remain untouched
- ColBERT vectors unchanged
- LanceDB embeddings unchanged
- SITUATION_CLUSTERS gradually replaced by API data
- Fallback: if API offline, hardcoded clusters still work

### Example: "Brake Noise" End-to-End
**Before:** 15 tiny fragments of Chinese manual
**After:** Structured article with sections:
- Quick Answer: "Проверьте толщину колодок..."
- What Happened: 2 chunks about brake symptoms
- Diagnostics: 3 chunks + DTC P0100 link
- What To Do: step-by-step pad replacement (wizard-ready)
- Warnings: brake fluid contamination
- Parts: X01-12345678 (Front Brake Pad Set)
- 3D: brake_pad@brakes, brake_disc@brakes, abs_sensor@brakes

---

## 7. Architect C: Pragmatic MVP (3 sessions, zero risk)

### Core Idea
Maximum user impact with ZERO data destruction. No merge, no re-embed, no schema breaks. 3 independent sessions.

### Philosophy
> "Don't merge/delete chunks from the DB. Quality scoring achieves the same UX result (garbage hidden) without data destruction."

### SESSION 1: Quality Scoring + Search Boost (~3 hours)

#### 1A. New `chunk_quality` table (side table, like situation_tags)
```sql
CREATE TABLE chunk_quality (
    chunk_id TEXT PRIMARY KEY,
    content_length INTEGER NOT NULL,
    quality_tier INTEGER NOT NULL,  -- 1=garbage, 2=low, 3=medium, 4=good, 5=excellent
    is_stub INTEGER DEFAULT 0,
    is_image_only INTEGER DEFAULT 0,
    has_ocr_noise INTEGER DEFAULT 0,
    parent_chunk_id TEXT,
    merge_group TEXT
);
```

Tier assignment:
- Tier 1 (<50 chars): garbage — image captions, page numbers → ~800-1000
- Tier 2 (<150 chars): low — single-sentence notes → ~2500-3000
- Tier 3 (<500 chars): medium — short paragraphs → ~4000
- Tier 4 (<2000 chars): good — full sections → ~2500
- Tier 5 (≥2000 chars): excellent — comprehensive → ~500-800

Adjustments: procedures bump to tier 4+, warnings to tier 3+, DTC always tier 3+.

#### 1B. Quality-boosted search scoring
```python
# Current: blended = 0.7 * colbert + 0.3 * rrf
# New: multiply by quality factor
quality_mult = {1: 0.3, 2: 0.7, 3: 1.0, 4: 1.1, 5: 1.15}[tier]
if is_stub: quality_mult *= 0.5
blended = base * quality_mult
```

#### 1C. Add `quality_tier` to SearchResult API response
One new field, backward-compatible.

### SESSION 2: Glossary Cleanup + Parts Bridge (~2 hours)

#### 2A. Glossary cleanup
- Delete links where term appears in >30% of chunks (~15-20 terms, ~20K links)
- Delete links where term < 4 chars (ZH) or < 5 chars (EN/RU)
- Result: 65,287 → ~40,000 links

#### 2B. Parts-to-chunks bridge
```sql
CREATE TABLE parts_chunks (
    part_id INTEGER NOT NULL,
    chunk_id TEXT NOT NULL,
    match_type TEXT NOT NULL,  -- name_match|system_match|dtc_match
    relevance REAL DEFAULT 0.5,
    PRIMARY KEY (part_id, chunk_id)
);
```

Two strategies:
1. **Name match** (relevance 0.8): FTS5 search part name in chunk content
2. **System-layer match** (relevance 0.4): SYSTEM_TO_KB_LAYERS, top chunks by quality_tier

New endpoint: `GET /parts/{number}/articles`

### SESSION 3: Frontend UX (~2 hours)

#### 3A. Content snippets in article cards
- Tier 4-5: show 2-line content preview
- Tier 1-2: show "краткая справка" label

#### 3B. Quality indicators
```
★★ Подробная статья (tier 5, green)
★  Хорошая статья (tier 4, blue)
   (no indicator for tier 3)
○  Краткая заметка (tier 2, orange)
·  Фрагмент (tier 1, red)
```

#### 3C. Sort by quality in browse mode
Emergency first → then quality_tier desc → then score desc.

### What Architect C EXPLICITLY SCOPED OUT
1. **No chunk merge/delete** — breaks chunk_id, requires re-embed
2. **No re-embedding** — pplx-embed needs 8GB VRAM (unavailable)
3. **No touch chunk_content/translations** — 44,623 rows, FTS triggers
4. **No ML scoring** — pure heuristics sufficient

### Success Criteria
| Metric | Before | After |
|--------|--------|-------|
| Garbage in top-10 results | ~2-3/query | 0-1/query |
| Quality visible to user | No | Yes (badges + snippets) |
| Parts with articles | 0 | ~1000-1500 |
| Glossary noise | 65,287 | ~40,000 |
| Broken features | — | 0 |

---

## 8. Cross-Review & Synthesis

### PLAN A: Physical Merge — Review

| Aspect | Verdict |
|--------|---------|
| **Strengths** | Addresses root cause (chunk size), title-chain merge is sound for MinerU, chunk_merge_map is well-designed, IDF glossary weighting is correct |
| **Critical Flaw** | **Phase 5 re-embedding is impossible on this machine** (SKIP_PPLX_EMBED=1, OOM). ColBERT on CPU = 15-30 hours, not 2-4. Without re-embedding, merged chunks are invisible to search. |
| **Flaw 2** | `is_current=0` soft-delete: NOT A SINGLE search query in server.py filters by is_current. At least 15+ SQL statements need modification. |
| **Flaw 3** | 44,623 translations cannot be trivially concatenated — each was translated independently, some start with "In this section..." |
| **Flaw 4** | rowid order ≠ document order for MinerU sources (depends on processing pipeline) |
| **Feasibility** | LOW on this machine, MEDIUM with workstation |
| **User Impact** | HIGH if completed end-to-end |

### PLAN B: Virtual Article Layer — Review

| Aspect | Verdict |
|--------|---------|
| **Strengths** | Zero data destruction, fills genuine article abstraction gap, templates are well-designed, Stage 4 elevation is clever, 3D multi-component highlighting |
| **Critical Flaw** | **Does NOT solve retrieval quality.** Chunks still 449 chars avg, ColBERT still scores 100-char headers poorly. Article layer is presentation fix, not search fix. |
| **Flaw 2** | Auto-composition is underspecified. situation_type has only 5 values across 11,872 chunks — "learning" alone = 5,976. Not useful for grouping. |
| **Flaw 3** | 50-80 articles = ~5% of chunks covered. 95% remain orphaned with unchanged search experience. |
| **Flaw 4** | Frontend rendering adds significant complexity (~500+ lines to knowledge-v2.js, already 2010 lines) |
| **Feasibility** | HIGH for schema+API, MEDIUM for content curation |
| **User Impact** | MEDIUM — great for 50-80 situations, unchanged for everything else |

### PLAN C: Pragmatic MVP — Review

| Aspect | Verdict |
|--------|---------|
| **Strengths** | Zero risk, immediately deployable, quality scoring is 80% effective at 1% cost, side table pattern is correct, each session independent |
| **Critical Flaw** | **Does not address fundamental chunking problem.** Hiding garbage ≠ fixing garbage. Search still runs ColBERT on 4,550 useless chunks. |
| **Flaw 2** | No situational navigation — the UX report's core insight completely unaddressed |
| **Flaw 3** | Frontend quality badges ("Фрагмент" + red dot) — confusing UX. Why show results the system itself thinks are garbage? |
| **Flaw 4** | parts_chunks FTS5 name matching = many false positives. confidence=0.8 for FTS5 match is too high |
| **Feasibility** | VERY HIGH (~6-7 hours total) |
| **User Impact** | LOW-MEDIUM — garbage drops from top results, but still "fragments not articles" |

---

## 9. Final Implementation Plan: THE OPTIMAL HYBRID

> Strategy: **C First → B Next → A Targeted (on workstation)**
> Take the best of each plan, skip the rest.

### PHASE 1: Ship Now (~4 hours, zero risk)
**Source: Plan C (Session 1 + 2) with modifications**

#### 1.1 chunk_quality side table
- Exactly as Plan C: tiers 1-5 based on length + has_procedures + has_warnings + content_type
- New table `chunk_quality`, not ALTER TABLE on chunks (4.2GB DB)

#### 1.2 Search boost + quality filter
- Quality multiplier: `{1: 0.3, 2: 0.7, 3: 1.0, 4: 1.1, 5: 1.15}`
- **KEY CHANGE from Plan C:** Add `WHERE quality_tier >= 2` as default filter (not badges). Tier-1 garbage NEVER appears unless `min_quality=1` param passed.
- Better than Plan C's "show garbage with red dot" approach

#### 1.3 Glossary cleanup
- Delete links where term frequency >30% of chunks
- Delete links where term < 4 chars (ZH) or < 5 chars (EN/RU)
- Result: 65,287 → ~40,000 links

#### 1.4 Parts-chunks bridge
- **Corrected confidence** (from reviewer): FTS5 name_match = 0.5, system_match = 0.3
- Plan C's 0.8/0.4 was too optimistic for fuzzy FTS5 matches

**Outcome:** Garbage disappears from search. Glossary cleaned. Parts get article connections.

### PHASE 2: Next Week (~6-8 hours, low risk)
**Source: Plan B (Minimal Article Layer)**

#### 2.1 articles + article_chunks tables
- Plan B's schema, but START WITH ONLY 9 situations (from existing SITUATION_CLUSTERS)
- Do NOT attempt auto-generation of 50-80 articles yet
- Hand-write quick_answer_ru for 9 situations (they already exist in JS)

#### 2.2 Semi-auto chunk assignment
- For each situation: run its searchQueries against API
- Take top-20 results with quality_tier ≥ 3
- Insert into article_chunks with sections by heuristic: has_procedures→steps, has_warnings→warnings, DTC→diagnostics

#### 2.3 API endpoint
- `GET /article/{slug}` — compose chunks by template sections
- `POST /articles/browse` — filterable article list

#### 2.4 Frontend: replace hardcoded SITUATION_CLUSTERS
- knowledge-v2.js: fetch from `/articles/browse` instead of hardcoded array
- Fallback to hardcoded if API offline
- Do NOT implement Stage 4 article elevation yet

**Outcome:** Beginner mode becomes data-driven. 9 situational articles with real content.

### PHASE 3: When Workstation Available (~1 day + GPU time)
**Source: Plan A (Targeted Merge, NOT universal)**

#### 3.1 Merge ONLY the worst offenders
- `mineru_l7_zh_owners`: 3,913 chunks, avg 223 chars → merge to ~1,300
- `mineru_l9_zh_owners`: 1,401 chunks, avg 171 chars → merge to ~470
- Total: 5,314 chunks → ~1,770 (3:1 ratio)
- Do NOT touch other sources (pdf_l7_zh avg 1271, drom_reviews avg 7813 — already fine)

#### 3.2 Title-chain aggregation (Plan A algorithm)
- Group by (source, normalized title)
- Order by rowid
- Concat until 3000 chars max
- Absorb headers (<80 chars) into next chunk

#### 3.3 ColBERT re-encoding on workstation
- 2x RTX 3090, BGE-M3 model
- ~1,770 new chunks × ColBERT encoding = ~30 min on GPU
- Skip pplx-embed (unless cached on workstation)

#### 3.4 is_current filter
- Add `WHERE is_current != 0` to ALL search queries in server.py (8+ places)
- Must be done BEFORE soft-deleting originals

#### 3.5 Translation merge
- Concatenate existing translations (they are short fragments in same order)
- Acceptable for ZH→RU/EN (MinerU fragments were adjacent paragraphs)

**Outcome:** Search quality jumps for ZH manual content. DB shrinks from ~11,800 to ~8,300 active chunks.

### What to SKIP Entirely

| Skipped | Why |
|---------|-----|
| Plan A's quality_score ON chunks table | Use side table (Plan C) instead. Don't ALTER 4.2GB table |
| Plan A's situations table | Plan B's articles table is strictly more capable |
| Plan A's universal merge | Only mineru_*_owners need merging |
| Plan B's article_parts table | Premature. parts_chunks bridge covers this |
| Plan B's LLM summaries | Not needed yet. Hand-write for 9 situations |
| Plan B's 50-80 auto-articles | Start with 9, expand later |
| Plan C's frontend quality badges | Confusing UX. Filter out garbage instead |

### Success Metrics

| Metric | Before | Phase 1 | Phase 2 | Phase 3 |
|--------|--------|---------|---------|---------|
| Garbage in top-10 | ~2-3/query | 0-1 | 0-1 | 0 |
| Situational articles | 0 (hardcoded JS) | 0 | 9 (DB-driven) | 9+ |
| Parts with article links | 0 | ~1000-1500 | ~1000-1500 | ~1500+ |
| Glossary noise | 65,287 | ~40,000 | ~40,000 | ~40,000 |
| Active chunks | 11,872 | 11,872 | 11,872 | ~8,300 |
| Avg chunk size (active) | 449 | 449 | 449 | ~650 |
| Broken features | — | 0 | 0 | 0 |
| Risk level | — | Zero | Low | Medium |

### Scripts to Create

| Script | Phase | Purpose |
|--------|-------|---------|
| `scripts/build_chunk_quality.py` | 1 | Populate chunk_quality table |
| `scripts/clean_glossary_links.py` | 1 | Remove noise glossary links |
| `scripts/build_parts_chunks.py` | 1 | Build parts↔chunks bridge |
| `scripts/build_articles.py` | 2 | Convert SITUATION_CLUSTERS → DB articles |
| `scripts/merge_fragments.py` | 3 | Title-chain merge of mineru chunks |

### Key Files to Modify

| File | Phase | Changes |
|------|-------|---------|
| `api/server.py` | 1,2,3 | Quality boost in scoring, quality_tier in response, /article endpoints, is_current filter |
| `frontend/screens/knowledge-v2.js` | 2 | Replace SITUATION_CLUSTERS with API calls |
| `frontend/screens/knowledge.js` | 1 | Sort by quality in browse mode |

### Dependency Graph
```
Phase 1.1 (chunk_quality)
    ├─→ Phase 1.2 (search boost)
    ├─→ Phase 1.4 (parts_chunks, uses quality for system_match)
    └─→ Phase 2.2 (article chunks, filters by quality_tier ≥ 3)

Phase 1.3 (glossary cleanup) ── independent

Phase 2.1-2.4 (articles) ── depends on Phase 1

Phase 3 (merge) ── independent, needs workstation GPU
    └─→ Phase 3.4 (is_current filter) ── MUST be done before soft-delete
```

---

## Appendix: Frontend Chunk Consumption Map

### 19 Chunk Fields Used in UI
| Field | Usage |
|-------|-------|
| chunk_id | Entry identification, detail fetch |
| title | Card headline, detail header |
| content | Full detail view (markdown) |
| layer | Color-coding (LAYER_COLORS), system filtering |
| source | Icon badge (SOURCE_BADGES) |
| source_language | Translation badge, i18n filter |
| model | L7/L9 vehicle filtering |
| page_start | Page reference |
| score | Relevance bar (0-1) |
| urgency | Red emergency styling (≥4) |
| trust_level | Dot badges (●●●○○) |
| situation_type | Emoji badge (⚠️🔍🔧📋📖) |
| dtc_codes | Clickable DTC badges |
| glossary_terms | Component tags, 3D linking |
| has_procedures | "Пошаговая инструкция" badge |
| has_warnings | "Предупреждение" badge |
| source_url | "Open source" link |
| translations | Localized content |
| preview | Fallback if content missing |

### API Endpoints Used
| Endpoint | Usage |
|----------|-------|
| POST /search | Main hybrid search |
| POST /search/semantic | Dense-only search |
| POST /search/keyword | FTS5 BM25 only |
| GET /browse?layer=X | Browse by system |
| GET /chunk/{id} | Full detail + translations |
| POST /dtc/{code} | DTC code lookup |
| POST /glossary/search | Component search |
| GET /parts/search | Parts catalog |
| GET /parts/stats | Parts overview |
| GET /parts/{number} | Part detail |
| GET /health | Init check |
| GET /stats | KB statistics |

### Screens Using Chunks
1. **Knowledge (Expert)** — search, browse, DTC tab, parts catalog, article detail
2. **Knowledge-v2 (Beginner)** — situational clusters, daily tips, decision tree, progressive disclosure
3. **Digital Twin** — component filtering, info bar with part numbers
4. **Diagnostics** — future DTC integration
5. **Dashboard** — future health alerts
6. **AI Assistant** — future chat context
7. **KB Viewer** — markdown rendering

---

## Appendix: Key Files for Implementation

| File | Role |
|------|------|
| `scripts/build_kb.py` | Chunk creation logic (chunk_text, make_chunk_id, upsert_chunk) |
| `scripts/build_embeddings.py` | LanceDB + ColBERT vector encoding |
| `scripts/build_situation_tags.py` | Situation type/urgency/trust classification |
| `scripts/build_parts_bridge.py` | SYSTEM_TO_KB_LAYERS mapping |
| `api/server.py` | Search logic, scoring, all endpoints |
| `frontend/screens/knowledge.js` | Expert mode (1883 lines) |
| `frontend/screens/knowledge-v2.js` | Beginner mode (2010 lines) |
| `frontend/screens/digital-twin.js` | 3D viewer + component selection |
| `frontend/knowledge-base.js` | API client (517 lines) |
