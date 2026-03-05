# Parts Integration Plan — Post-OCR Cleanup & UI Fixes

> Generated: 2026-03-04, based on team brainstorm (data-analyst, ui-reviewer, architect)
> Status: COMPLETE

## Context

OCR completed: 3,222 parts extracted from 352 table images (Qwen2.5-VL-7B, 87 min).
Infrastructure exists: API (4 endpoints), frontend (3-level drill-down), parts-bridge.json, KB client.
This plan addresses data quality, bugs, and bridge issues.

---

## Phase 1 — Data Cleanup (local + workstation GPU)

### 1.1 System assignment for 889 unmapped parts
- **Problem:** 91 pages have no system_zh/system_en (27.6% of all parts)
- **Root cause:** OCR page_map built from text entries; some pages have no text with system name
- **Fix:** Nearest-neighbor inference: for each unmapped page, use system from closest mapped page (±10)
- **Effort:** ~30 min, local Python script
- [x] Done — 889 parts fixed across 91 pages, 100% system coverage

### 1.2 Fastener pattern translation (~1,100 parts)
- **Problem:** 0% English name coverage
- **Fix:** Dictionary-based translation for standard fastener names (六角法兰面螺栓 → Hex Flange Bolt, etc.)
- [x] Done — 1,386 parts translated via pattern dictionary

### 1.3 Glossary lookup translation (43 parts)
- **Problem:** Some part names match glossary terms directly
- **Fix:** Match part_name_zh against i18n-glossary-data.json zh field
- [x] Done — 425 parts translated from glossary (1,523 entries)

### 1.4 Translation for remaining functional parts (~802)
- **Problem:** Remaining parts have no English name
- **Fix:** Qwen2.5-VL-7B (738/802) + Claude Sonnet (100% final), then RU via 4 parallel Sonnet agents
- [x] Done — EN: 3,222/3,222 (100%), RU: 3,222/3,222 (100%)

### 1.5 Add is_fastener flag
- **Fix:** ALTER TABLE parts ADD COLUMN is_fastener INTEGER DEFAULT 0; UPDATE based on name patterns
- [x] Done — 1,248 fasteners marked

---

## Phase 2 — UI/API Bug Fixes (P0)

### 2.1 Cache parts-bridge.json in knowledge.js
- **Bug:** Re-fetched on every part detail click (no module-level cache)
- **Fix:** Add `let _partsBridgeCache = null;` and reuse
- [x] Done

### 2.2 Fix search() call parameter
- **Bug:** `renderPartDetail` calls `kb.search(term, {top_k: 5})` — `top_k` is ignored, should be `limit`
- **Fix:** Change to `{}, 5` (limit as 3rd arg)
- [x] Done

### 2.3 Make parts clickable in 3D info bar
- **Bug:** Part numbers in digital-twin info bar are plain text, not navigable
- **Fix:** Added click handler → sets `__llcar_partDetail` → navigates to knowledge screen → renders part detail
- [x] Done

### 2.4 Fix coarse glossary matching
- **Bug:** `findPartsForGlossaryId` returns ALL parts in a system when system-level match
- **Fix:** Two-pass: direct glossary_id matches first, system-level fallback limited to 8
- [x] Done

### 2.5 Don't clear partsBridgeCache on digital-twin cleanup
- **Bug:** Static data re-fetched on every screen visit
- [x] Done

---

## Phase 3 — Bridge Rebuild

### 3.1 Create system→group mapping table
- Map 22 part catalog systems → 5 diagnostic groups (electric, fuel, suspension, cabin, tech)
- Map 22 part catalog systems → 8 3D layer keys (body, engine, drivetrain, ev, brakes, etc.)
- [x] Done — in build_parts_bridge.py

### 3.2 Fix mesh name aliases
- **Bug:** 51 broken refs — Cyrillic L7 names used instead of ASCII L9 names
- **Fix:** Bridge v2 uses only real L9 mesh names from system-components.json
- [x] Done

### 3.3 Regenerate parts-bridge.json
- All 3,222 parts included (was 2,173)
- 22 systems → 5 groups, correct L9 mesh refs
- 211 parts with glossary_id, 383 meshes across groups
- [x] Done

---

## Phase 4 — UX Polish

### 4.1 Add pagination to /parts/search (offset param + has_more)
- [x] Done — offset + has_more (LIMIT+1 trick)

### 4.2 Add getSubsystems() to KnowledgeBase client (replace raw fetch)
- [x] Done — knowledge-base.js: getSubsystems(systemName)

### 4.3 Add search-within-subsystem filter (client-side text input)
- [x] Done — filter input in renderPartsResults, searches across ZH/EN/RU/number

### 4.4 Preserve drill-down state on screen switch
- [x] Done — cleanup() no longer resets activeCategory/searchQuery

### 4.5 Show part names in UI language (ZH/EN/RU)
- [x] Done — _partDisplayName()/_partSecondaryName() + system/subsystem labels
- Fixed digital-twin.js: i18n.currentLanguage → i18n.lang + name_ru support

### 4.6 Inline image preview instead of new-tab link
- [x] Done — collapsible preview with toggle, click for full-size

### 4.7 Don't clear partsBridgeCache on digital-twin cleanup
- [x] Done (Phase 2)

### 4.8 Case-insensitive search for Cyrillic
- [x] Done — API searches both lower() and capitalize() variants

---

## Workstation Info (for delegated tasks)

- HOST: 192.168.50.2
- USER: baza / PASS: Llcar2024!
- Python: C:\Users\BAZA\AppData\Local\Programs\Python\Python311\python.exe
- Project: C:\LLCAR-Transfer
- GPUs: 2x RTX (24 GB each)
- **Critical:** Model loading must use CPU-first pattern (no device_map), bfloat16 + eager attention
