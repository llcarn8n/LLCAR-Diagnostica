# LLCAR Diagnostica — История разработки

> Полная хронология фаз проекта, решений, багов и планов.
> Проект: диагностическая KB для автомобилей Li Auto L7/L9.

---

## Фаза 1: Построение базы знаний (KB)

### 1.1 OCR мануалов (MinerU)
- Извлечение текста из PDF-мануалов Li Auto L7 и L9 через MinerU
- 15 исходных документов (конфигурации, руководства пользователя, каталоги запчастей)
- Результат: 11,097 чанков на китайском языке (ZH)
- Изображения: 11,426 JPG извлечено из PDF, 10,014 привязано к чанкам
- Подписи к 7,109 изображениям через Qwen2.5-VL-7B

### 1.2 SQLite KB
- БД: kb.db (~4.3 GB), 29 таблиц
- Основные таблицы: chunks, chunk_content, colbert_vectors, chunk_images, scraped_content, parts
- 11,872 чанка (11,024 manual + 488 DTC + 264 parts + 73 web + 23 config)
- 15 слоёв (layers): body, interior, brakes, sensors, ev, engine, hvac, battery, drivetrain, lighting, chassis, infotainment, adas, parts, web_scraped
- Модели: L7 (6,960), L9 (4,391), L7+L9 shared (521)

### 1.3 Эмбеддинги (LanceDB)
- Dense vectors: pplx-embed-context-v1-4b (Perplexity, 2560 dimensions)
- Title vectors: тот же pplx-embed
- Image vectors: CLIP ViT-L/14
- ColBERT token vectors: BGE-M3 (FP16 BLOB в SQLite) — 11,799 чанков
- LanceDB: ~638 MB (content_emb + title_emb + image_emb)

### 1.4 Переводы
- 5 языков: ZH (primary), RU, EN, ES, AR
- 44,623 строк в chunk_content (ZH:11,800 / RU:11,122 / EN:11,095 / ES:5,303 / AR:5,303)
- Глоссарий: 8,597 уникальных терминов × 5 языков = 65,287 связей

### 1.5 Fine-tuning M2M модели
- Базовая модель: `utrobinmv/m2m_translate_en_ru_zh_large_4096`
- 6 раундов fine-tuning
- Round 6 (лучший): BLEU=13.39
- Опубликована: `Petr117/m2m-diagnostica-automotive` (HuggingFace)
- Тренировочные данные: 20,900+ пар (ZH↔EN/RU/AR/ES)
  - training_pairs_tier1.jsonl: 9,524 пары
  - training_pairs_bridge.jsonl: 10,606 пар (EN↔AR/ES via NLLB)
  - training_pairs_session15.jsonl: 770 пар
  - training_pairs_parts.jsonl: 3,158 пар
- Опубликованы: `Petr117/diagnostica-training-pairs`

### 1.6 DTC база
- 488 DTC-кодов привязано к чанкам
- P, C, B, U коды (двигатель, шасси, кузов, сеть)
- Слабое место: мало C-кодов (31) для авто с пневмоподвеской

---

## Фаза 2: API сервер (FastAPI)

### 2.1 Гибридный поиск (3 стадии)
```
Query → [Stage 1] FTS5 BM25 + LanceDB dense + LanceDB title
      → [Stage 2] RRF fusion → 20 кандидатов
      → [Stage 3] ColBERT MaxSim reranking (BGE-M3)
      → top-10 результатов
```

### 2.2 Эндпоинты
- `POST /search` — основной поиск (гибрид)
- `GET /chunk/{id}` — один чанк
- `GET /dtc/{code}` — DTC код (P0300, C0265...)
- `POST /glossary/search` — поиск терминов
- `GET /stats` — статистика KB
- `GET /parts/search` — каталог запчастей
- `GET /parts/stats` — статистика по системам
- `GET /parts/{number}` — деталь по номеру
- `GET /parts/subsystems/{system}` — подсистемы
- `POST /scrapers/scrape-url` — скрапинг URL
- `POST /scrapers/preview-extract` — предпросмотр извлечения
- `POST /scrapers/rescrape-all` — mass re-scrape
- `POST /scrapers/rescrape/{id}` — re-scrape одной статьи
- `GET /health` — здоровье системы

### 2.3 Исправленные баги (FTS5)
1. **FTS5 JOIN** — joinился chunk_content.rowid вместо chunks.rowid
2. **Нет LIKE fallback** — FTS5 возвращал 0 результатов, fallback только на OperationalError
3. **_fts_fallback** — искал целую фразу, а не отдельные слова
4. **knowledge.js findEntryById** — не вызывал getChunk API

### 2.4 Критический баг SQLite
- `get_db_conn()` не имел `commit()` — изменения скрапинга не сохранялись в БД
- Обнаружен при тестировании скрапинг-эндпоинтов

---

## Фаза 3: Фронтенд (SPA)

### 3.1 Архитектура
- Single Page Application, мобильный UI
- Three.js 0.182 (ES modules, import map)
- 7 экранов: car-select, dashboard, diagnostics, digital-twin, knowledge, knowledge-v2, ai-assistant
- 5 языков UI (RU/EN/ZH/AR/ES) через i18n.js

### 3.2 3D Viewer
- 4 GLB модели: Li7/Li9 × unified/5-layer
- 5-слойная декомпозиция (body, engine, drivetrain, ev, brakes...)
- OrbitControls, клик по mesh → info bar
- System manifest: system-components.json
- KB-3D bridge: 5 диагностических групп (electric, fuel, suspension, cabin, tech)

### 3.3 KB Search v1 (Expert)
- knowledge.js — полнотекстовый поиск
- Табы: Все, Мануалы, Запчасти, DTC
- Фильтры: модель, слой, язык

### 3.4 KB Search v2 (Beginner) — 9 фаз
- knowledge-v2.js — progressive disclosure
- **Фаза 1**: Скаффолд, регистрация экрана
- **Фаза 2**: Progressive disclosure (карточки → полная статья → wizard)
- **Фаза 3**: Глоссарий-тултипы (kb-glossary.js, 8,597 терминов)
- **Фаза 4**: DTC → KB интеграция (клик по коду → детали + связанные статьи)
- **Фаза 5**: Ситуационная навигация
- **Фаза 6**: Дерево решений для новичков
- **Фаза 7**: 3D интеграция в статьях
- **Фаза 8**: Заботливый тон + Sparklines
- **Фаза 9**: Персонализация Новичок/Эксперт (localStorage 'llcar-persona')

### 3.5 Scraping GUI
- scraping.html + scraping.js
- Визуальное управление скраперами
- Предпросмотр извлечения с 6 методами
- Mass re-scrape через API

---

## Фаза 4: Каталог запчастей (OCR)

### 4.1 OCR Pipeline
- **Модель**: Qwen2.5-VL-7B (bfloat16, eager attention)
- **Критическое**: device_map="cuda" вызывает ACCESS_VIOLATION → грузить на CPU → .to("cuda:0")
- 352 таблицы из L9 parts manual
- Рабочая станция: 2× RTX 3090 (24 GB each)

### 4.2 Итерации OCR
| Шаг | Действие | Результат |
|-----|----------|-----------|
| Initial OCR | 352 таблиц, max_side=1024 | 3,222 parts |
| Dedup | Удаление 749 точных дубликатов | 2,473 parts |
| Re-OCR R1 | Enhanced prompts, max_side=1280 | +60 → 2,533 |
| Re-OCR R2 | Retry zero-OCR, max_side=768 | +31 → 2,564 |
| Rendered pages | 25 missing PDF pages (PyMuPDF) | +13 → 2,577 |

### 4.3 Покрытие
- 22 системы, 2,577 деталей
- Coverage score: 60/100 (217 диаграмм с пробелами, ~1,500 missing hotspots)
- Оставшиеся пробелы — OCR-трудные таблицы (мелкий текст, merged cells)

### 4.4 Parts Integration (PLAN-PARTS-INTEGRATION.md — COMPLETE)
- **Phase 1**: Data cleanup — system assignment (889 parts), fastener patterns (1,386), glossary lookup (425), full EN/RU translation (100%)
- **Phase 2**: UI/API bugs — cache, search params, 3D clickable parts, glossary matching, case-insensitive Cyrillic
- **Phase 3**: Bridge rebuild — 22 systems → 5 groups, fixed 51 broken Cyrillic mesh refs, parts-bridge.json v2
- **Phase 4**: UX polish — pagination, subsystem filter, drill-down state, i18n part names, inline image preview

---

## Фаза 5: Веб-скрапинг

### 5.1 Инфраструктура
- Base scraper: httpx + BeautifulSoup (не scrapling — меньше зависимостей)
- _BS4Page/_BS4Selection: миникласссы, имитирующие scrapling CSS API
- stealth_fetch: fallback chain (scrapling → patchright → httpx)
- Wikipedia: REST API (`/api/rest_v1/page/summary/`) вместо скрапинга (403)
- URL fragments (#comments) stripped before dedup

### 5.2 Скраперы (15 шт, 14 рабочих)
| Scraper | Source | Lang | Items |
|---------|--------|------|-------|
| drom_reviews | drom.ru отзывы | RU | 54 |
| autoreview | autoreview.ru | RU | 41 |
| carnewschina | carnewschina.com | EN | 37 |
| autochina_blog | autochina.blog | EN | 6 |
| carscoops | carscoops.com | EN | 6 |
| liautocn_news | ir.lixiang.com | EN | 5 |
| getcar | getcar.ru | RU | 4 |
| kitaec | kitaec.ua | RU | 4 |
| electrek | electrek.co | EN | 2 |
| autonews | autonews.ru | RU | 1 |
| drom | drom.ru каталог | RU | 1 |
| insideevs | insideevs.com | EN | 1 |
| topelectricsuv | topelectricsuv.com | EN | 1 |
| wikipedia | Wikipedia REST API | multi | 1 |
| drive2 | drive2.ru | RU | 0 (403 blocked) |

### 5.3 Система извлечения контента (6 методов)
1. **auto** — пробует site-specific → trafilatura → bs4 → regex
2. **bs4_article** — CSS-селекторы по сайту
3. **trafilatura** — библиотечное извлечение
4. **trafilatura_precision** — строгий режим
5. **bs4** — generic BeautifulSoup
6. **regex** — fallback через `<p>` теги

### 5.4 Аудит качества
- Удалено 40 мусорных элементов (поисковые страницы, homepage-дампы, paywall)
- 37 заголовков carnewschina исправлены ("Search" → из контента/URL)
- Итого: 164 чистые статьи, 0 пустых, 0 garbage

### 5.5 Situation tags
- build_situation_tags.py: авто-разметка 11,813 чанков
- Поля: urgency(1-5), situation_type, trust_level(1-5), season, events, mileage_ranges
- Чистый SQL + regex, ~30 секунд
- situation_tags.json в knowledge-base/

---

## Фаза 6: Экспорт и документация

### 6.1 Мануалы как Markdown
- scripts/export_manuals_md.py
- 15 MD-файлов в knowledge-base/manuals/ (11,097 чанков, 13 MB)
- 10,014 image references (100% verified, relative paths)
- INDEX.md с оглавлением

### 6.2 Статьи как Markdown
- 18 MD-файлов в knowledge-base/articles/ (301 статья, 1.2 MB)
- INDEX.md по источникам

### 6.3 DB Image Path Fix
- 2,312 чанков имели абсолютные пути `C:/Diagnostica-KB-Package/` → исправлены на relative

---

## Инфраструктура

### Рабочая станция (удалённая, через SSH/Ethernet)
- IP: 192.168.50.2, User: baza, Password: Llcar2024!
- GPU: 2× RTX 3090 (24 GB each)
- torch 2.10+cu130, transformers 5.2, Python 3.14.2 + 3.11
- Использовалась для: OCR, re-OCR, caption_images, translate

### Ноутбук (основная разработка)
- SKIP_PPLX_EMBED=1 (4B модель не влезает в VRAM)
- Поиск: hybrid_colbert (FTS5 + ColBERT через BGE-M3)
- BGE-M3: ~2 GB, загружается за ~7 секунд

### HuggingFace ресурсы
| Resource | HF ID |
|----------|-------|
| Fine-tuned M2M (R6, best) | Petr117/m2m-diagnostica-automotive |
| Training pairs (20,900) | Petr117/diagnostica-training-pairs |

---

## Планы улучшений (Phase 2+)

### PLAN-KB-ENRICHMENT.md — Обогащение контента
**Проблема**: KB на 93% из OCR-мануалов. Нет "как пользоваться" и "что делать когда сломалось".

**12 контентных пробелов (P0-P2):**
1. Ежедневная эксплуатация EREV (режимы, зарядка) — P0
2. Зимняя эксплуатация (батарея, запас хода) — P0
3. NVH проблемы 2025 (рычаг подвески, скрипы) — P0
4. OTA обновления (история 4.6-8.0) — P0
5. Типичные проблемы 1-го года — P1
6. L7 vs L9 сравнение — P1
7. Реальный расход по режимам — P1
8. Зарядка на практике (РФ) — P1
9. Воздушная подвеска — P2
10. Infotainment / Li Auto App — P2
11. Сервис в России — P2
12. Дополнительные DTC коды — P1

**Ожидаемый результат**: +400-700 практических чанков, web-контент 2.5% → 5-7%

**Ключевые источники**:
- Drive2.ru (403 blocked, нужен прокси) — 100-200 статей
- Telegram @lixiangautorussia (40K подп.) — 500-1000 сообщений
- YouTube транскрипты — 20-50 видео
- Autonews.ru, GetCar.ru — новые скраперы

**Улучшения скраперов**:
- Фильтр релевантности (ключевые слова диагностики)
- Извлечение DTC кодов из текста
- Классификация content_type при импорте
- Консолидация 15 → 8 скраперов

### PLAN-KB-SMART-CARDS.md — Умные карточки
**Проблема**: 11,000 статей выглядят одинаково. Нет разницы между "ОСТАНОВИСЬ" и "история модели".

**3 шага**:
1. **Паспорт статьи** — авто-разметка urgency/trust/season/events (DONE: situation_tags)
2. **Умные карточки UI** — красная рамка для экстренных, точки доверия, метка перевода, бейдж типа
3. **Блок "Сейчас важно"** — контекстные карточки (зима/лето, DTC, пробег)

### Другие TODO
- [ ] Embed 164 web-scraped articles в LanceDB
- [ ] Translate 301 web-scraped chunks
- [ ] COMET-KIWI evaluation на translation cache
- [ ] Update query embedder: pplx-embed-v1-4b (сейчас context model fallback)
- [ ] Fine-tuning Round 8+ (24,058 пар)
- [ ] Китайские источники через VPN (autohome, dongchedi)
- [ ] Drive2.ru через residential proxy
- [ ] Telegram скрапер (ждём API credentials)
- [ ] Expand to more vehicle brands (Phase 2 scope)

---

## Ключевые технические решения

| Решение | Почему |
|---------|--------|
| httpx+BS4 over scrapling | Меньше зависимостей, надёжнее |
| Wikipedia REST API | Web scraping даёт 403 |
| CPU-first model loading | device_map="cuda" crashит Qwen2.5-VL |
| bfloat16 for Qwen2.5-VL | float16 даёт garbage output "!!!" |
| eager attention | Default attention crashит с ACCESS_VIOLATION |
| SKIP_PPLX_EMBED=1 | 4B модель OOM на ноутбуке |
| Параллельный KB v1/v2 | Не ломаем рабочий экран при разработке нового |
| 5-group diagnostic mapping | Связь 22 систем запчастей с 3D моделью |
| FP16 ColBERT BLOBs | Экономия места: FP32 → FP16 для BGE-M3 vectors |
| URL fragment stripping | Dedup: url#comment1 и url#comment2 = один URL |
