# Архитектура ситуационных эмбеддингов для офлайн-матчинга статей

> Версия: 1.0 | Дата: 2026-03-05
> Проект: LLCAR Diagnostica KB

---

## Оглавление

1. [Стратегия эмбеддингов](#1-стратегия-эмбеддингов)
2. [Конструирование ситуационного вектора](#2-конструирование-ситуационного-вектора)
3. [Офлайн-пакет данных](#3-офлайн-пакет-данных)
4. [Алгоритм матчинга](#4-алгоритм-матчинга)
5. [Метаданные статей для матчинга](#5-метаданные-статей-для-матчинга)
6. [Конкретный пайплайн](#6-конкретный-пайплайн)

---

## 1. Стратегия эмбеддингов

### Проблема

Текущие эмбеддинги не подходят для мобильного офлайна:

| Ресурс | Размер | Проблема |
|--------|--------|----------|
| LanceDB (pplx-embed-context-v1-4b, 2560d) | 637 МБ векторов + 8 ГБ модель | Нереально для мобильных |
| ColBERT (BGE-M3, token-level) | 4.2 ГБ BLOB'ов + 2 ГБ модель | Ещё хуже |
| kb.db полный | 4.3 ГБ | Неприемлемо |

### Решение: Pre-computed Situation Vectors (PSV) — БЕЗ модели на устройстве

**Ключевой инсайт:** нам НЕ нужна модель на устройстве, если мы предвычислим ВСЕ возможные запросы.

Автомобильная диагностика — это **закрытый домен**. Количество уникальных ситуаций конечно:

- 5 групп (electric, fuel, suspension, cabin, tech)
- 22 системы (Service Brake System, HVAC, и т.д.)
- 488 DTC-кодов
- 4 диапазона пробега
- 4 сезона
- 5 типов событий (warning_light, noise, vibration, performance, maintenance)
- ~100 ключевых компонентов (из glossary)

Вместо того чтобы генерировать эмбеддинг запроса в рантайме, мы **предвычисляем score-таблицу**: для каждой комбинации (контекст → топ-N статей) ответ уже готов.

### Двухуровневая архитектура

```
┌─────────────────────────────────────────────────┐
│ Уровень 1: ИНДЕКСНЫЙ МАТЧИНГ (мгновенный)      │
│                                                 │
│ situation_index.json                            │
│ {                                               │
│   "by_dtc":      {"P0010": ["chunk_1", ...]},  │
│   "by_system":   {"brakes": ["chunk_2", ...]},  │
│   "by_component":{"brake_pad": ["chunk_3",...]}, │
│   "by_event":    {"warning_light": [...]},       │
│   "by_mileage":  {"30-60k": [...]},              │
│   "by_season":   {"winter": [...]}               │
│ }                                               │
│                                                 │
│ → Пересечение множеств = кандидаты              │
└──────────────────────┬──────────────────────────┘
                       │ кандидаты (10-50 штук)
                       ▼
┌─────────────────────────────────────────────────┐
│ Уровень 2: SCORE-РАНЖИРОВАНИЕ (< 10 мс)        │
│                                                 │
│ article_scores.bin (Float16, 384d на статью)    │
│ situation_templates.bin (384d на шаблон)         │
│                                                 │
│ → cosine_similarity среди кандидатов             │
│ → top-3 результат                               │
└─────────────────────────────────────────────────┘
```

### Почему 384d + all-MiniLM-L6-v2

Для **предвычисления** (на сервере) используем `all-MiniLM-L6-v2`:
- 80 МБ модель (не грузим на телефон — нужна только на сервере для сборки)
- 384 измерения — хороший баланс качества/размера
- 11,398 статей × 384d × FP16 = **8.3 МБ** (все базовые векторы)
- Даже с 5 ситуационными вариантами на статью: 11,398 × 5 × 384 × 2 = **41.5 МБ**
- Мультиязычная альтернатива: `multilingual-e5-small` (120 МБ, 384d) — для ZH/RU/EN

**Выбор:** `multilingual-e5-small` — потому что статьи на ZH/RU/EN и нам нужен корректный кросс-язычный матчинг при предвычислении.

### На устройстве НЕТ модели

На устройстве хранятся только:
1. **Индексы** (JSON, ~2 МБ gzip)
2. **Pre-computed векторы** (binary Float16, ~42 МБ)
3. **Pre-computed шаблоны ситуаций** (binary Float16, ~0.5 МБ)
4. **Контент статей** (SQLite lite-версия, ~15 МБ)

**Итого на устройстве: ~60 МБ** (без ML-модели)

---

## 2. Конструирование ситуационного вектора

### 2.1 Ситуационные шаблоны (предвычислены на сервере)

Каждая возможная ситуация превращается в текстовый промпт и эмбеддится заранее:

```python
SITUATION_TEMPLATES = {
    # DTC-ситуации (488 штук)
    "dtc:P0010": "diagnostic trouble code P0010 camshaft position actuator circuit malfunction",
    "dtc:P0011": "diagnostic trouble code P0011 camshaft position timing over-advanced",
    "dtc:C0265": "diagnostic trouble code C0265 EBCM motor relay circuit malfunction",

    # Система + событие (22 системы × 5 событий = 110 штук)
    "sys:brakes+evt:warning_light": "brake system warning light on dashboard indicator",
    "sys:brakes+evt:noise": "brake system unusual noise grinding squealing",
    "sys:brakes+evt:vibration": "brake system vibration pulsation during braking",
    "sys:brakes+evt:performance": "brake system reduced performance longer stopping distance",
    "sys:brakes+evt:maintenance": "brake system scheduled maintenance service interval",

    "sys:hvac+evt:noise": "HVAC air conditioning unusual noise rattling clicking",
    "sys:hvac+evt:performance": "HVAC heating cooling insufficient weak airflow",
    # ...

    # Компонент + событие (100 компонентов × 5 событий = 500 штук)
    "comp:brake_pad+evt:noise": "brake pad worn grinding noise replacement needed",
    "comp:brake_pad+evt:maintenance": "brake pad inspection replacement schedule interval",
    "comp:battery_pack+evt:warning_light": "high voltage battery warning fault indicator",
    # ...

    # Пробег (4 диапазона)
    "mil:0-10k": "new vehicle break-in period initial inspection first service",
    "mil:10-30k": "regular maintenance oil change brake inspection tire rotation",
    "mil:30-60k": "major service transmission fluid brake pads replacement coolant",
    "mil:60k+": "high mileage wear items suspension bushings timing chain",

    # Сезон (4 варианта)
    "season:winter": "cold weather winter preparation battery antifreeze tire chains",
    "season:summer": "hot weather summer cooling system AC refrigerant overheating",
    "season:spring": "spring maintenance inspection winter damage cleanup",
    "season:autumn": "autumn preparation winter readiness heating system check",
}
```

**Итого шаблонов:** ~1,100 (488 DTC + 110 sys×evt + 500 comp×evt + 4 mil + 4 season)

Каждый шаблон → один вектор 384d → `situation_templates.bin`:
- 1,100 × 384 × 2 bytes = **845 КБ**

### 2.2 Как строится запрос в рантайме (без модели)

Пользовательский контекст:
```json
{
    "selected_part": "brake_pad",
    "season": "winter",
    "mileage": 45000,
    "dtc_codes": ["C0265"],
    "event": "warning_light"
}
```

Алгоритм на клиенте (чистый JS, без ML):

```javascript
function buildSituationQuery(context) {
    const templateKeys = [];

    // 1. DTC — самый сильный сигнал
    if (context.dtc_codes?.length) {
        for (const dtc of context.dtc_codes) {
            templateKeys.push({ key: `dtc:${dtc}`, weight: 3.0 });
        }
    }

    // 2. Компонент + событие
    if (context.selected_part && context.event) {
        templateKeys.push({
            key: `comp:${context.selected_part}+evt:${context.event}`,
            weight: 2.5
        });
    }

    // 3. Система + событие (определяем систему из компонента через parts-bridge)
    const system = getSystemForComponent(context.selected_part);
    if (system && context.event) {
        templateKeys.push({
            key: `sys:${system}+evt:${context.event}`,
            weight: 2.0
        });
    }

    // 4. Пробег
    if (context.mileage != null) {
        const range = getMileageRange(context.mileage);
        templateKeys.push({ key: `mil:${range}`, weight: 1.0 });
    }

    // 5. Сезон
    if (context.season) {
        templateKeys.push({ key: `season:${context.season}`, weight: 0.5 });
    }

    return templateKeys;
}
```

### 2.3 Ситуационные эмбеддинги статей

Для каждой из 11,398 статей предвычисляем **1 базовый + 3-5 ситуационных вектора**:

```python
def generate_article_embeddings(chunk):
    vectors = {}

    # Базовый вектор — из title + первые 200 символов content
    base_text = f"{chunk['title']}. {chunk['content'][:200]}"
    vectors['base'] = embed(base_text)  # multilingual-e5-small

    # Ситуационный вектор 1: "что за проблема"
    problem_text = f"{chunk['title']} problem diagnosis troubleshooting"
    if chunk['has_warnings']:
        problem_text += " warning safety critical"
    vectors['problem'] = embed(problem_text)

    # Ситуационный вектор 2: "процедура обслуживания"
    if chunk['has_procedures']:
        procedure_text = f"{chunk['title']} repair procedure step by step how to"
        vectors['procedure'] = embed(procedure_text)

    # Ситуационный вектор 3: "DTC-контекст"
    dtc_codes = get_dtc_for_chunk(chunk['id'])
    if dtc_codes:
        dtc_text = f"{chunk['title']} diagnostic code {' '.join(dtc_codes)}"
        vectors['dtc'] = embed(dtc_text)

    # Ситуационный вектор 4: "компонент-контекст"
    glossary_ids = get_glossary_for_chunk(chunk['id'])
    if glossary_ids:
        components = ' '.join(g.replace('@', ' ').replace('_', ' ') for g in glossary_ids[:5])
        vectors['component'] = embed(f"{chunk['title']} {components}")

    return vectors
```

**Среднее количество векторов на статью: ~3** (base + 1-2 ситуационных)

Размер: 11,398 × 3 × 384 × 2 bytes = **24.9 МБ**

---

## 3. Офлайн-пакет данных

### 3.1 Структура пакета

```
offline-package/
├── manifest.json              # Версия, дата, чексуммы (1 КБ)
├── articles-lite.db           # SQLite: chunk_id, title, content (обрезан), layer, model (~15 МБ)
├── situation-index.json       # Инвертированные индексы (gzip ~2 МБ)
├── article-vectors.bin        # Float16 матрица [N_vectors × 384] (~25 МБ)
├── article-vector-map.json    # chunk_id → offset в article-vectors.bin (~0.5 МБ)
├── template-vectors.bin       # Float16 матрица [1100 × 384] (~845 КБ)
├── template-keys.json         # template_key → offset в template-vectors.bin (~30 КБ)
├── parts-bridge-lite.json     # Облегчённый parts-bridge (component→system) (~200 КБ)
└── dtc-index.json             # DTC → {description, chunk_ids, system} (~100 КБ)
```

### 3.2 Оценка размеров

| Файл | Размер (raw) | Размер (gzip) | Описание |
|------|-------------|---------------|----------|
| articles-lite.db | 15 МБ | 6 МБ | Только id, title, content (до 500 символов), layer, model, has_procedures, has_warnings |
| situation-index.json | 5 МБ | 2 МБ | Все инвертированные индексы |
| article-vectors.bin | 25 МБ | 20 МБ | Float16 плохо жмётся, но ~20% экономия |
| article-vector-map.json | 0.5 МБ | 0.2 МБ | Маппинг chunk_id → смещение |
| template-vectors.bin | 0.85 МБ | 0.7 МБ | Шаблоны ситуаций |
| template-keys.json | 0.03 МБ | 0.01 МБ | Ключи шаблонов |
| parts-bridge-lite.json | 0.2 МБ | 0.08 МБ | Облегчённый бридж |
| dtc-index.json | 0.1 МБ | 0.04 МБ | DTC-индекс |
| **ИТОГО** | **~47 МБ** | **~29 МБ** | **Начальная загрузка** |

**29 МБ gzip** — приемлемо для первой загрузки PWA (даже на мобильном LTE).

### 3.3 articles-lite.db — облегчённая БД

Из текущей kb.db (4.3 ГБ) берём только:

```sql
-- Создаём облегчённую БД
CREATE TABLE articles (
    chunk_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content_preview TEXT NOT NULL,    -- первые 500 символов
    content_full TEXT,                -- NULL для офлайна, загружается по требованию
    layer TEXT NOT NULL,
    model TEXT NOT NULL,
    has_procedures BOOLEAN DEFAULT 0,
    has_warnings BOOLEAN DEFAULT 0,
    content_type TEXT DEFAULT 'manual'
);

-- Переводы (только RU и EN, без AR/ES)
CREATE TABLE translations (
    chunk_id TEXT NOT NULL,
    lang TEXT NOT NULL,   -- 'ru' или 'en'
    title TEXT,
    content_preview TEXT,  -- первые 500 символов
    PRIMARY KEY (chunk_id, lang)
);

-- DTC-линки
CREATE TABLE dtc_links (
    dtc_code TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    PRIMARY KEY (dtc_code, chunk_id)
);

-- Glossary-линки (только для матчинга, без полных определений)
CREATE TABLE glossary_links (
    chunk_id TEXT NOT NULL,
    glossary_id TEXT NOT NULL,  -- "brake_pad@brakes"
    PRIMARY KEY (chunk_id, glossary_id)
);
```

### 3.4 Стратегия инкрементальных обновлений

```json
// manifest.json
{
    "version": "2026.03.05",
    "total_articles": 11398,
    "checksum_index": "sha256:abc...",
    "checksum_vectors": "sha256:def...",
    "checksum_db": "sha256:ghi...",
    "delta_from": null,  // или "2026.02.28" для дельта-обновления
    "files": {
        "articles-lite.db": { "size": 15000000, "sha256": "..." },
        "article-vectors.bin": { "size": 25000000, "sha256": "..." },
        // ...
    }
}
```

**Стратегия:**
1. **Первая загрузка**: скачиваем всё (~29 МБ gzip)
2. **Обновления**: сервер генерирует дельта-пакет (только новые/изменённые статьи)
3. **Дельта-формат**:
   - `delta-articles.jsonl` — новые/обновлённые записи
   - `delta-vectors.bin` — новые векторы (append)
   - `delta-index-patch.json` — патч для индексов
4. **На клиенте**: IndexedDB хранит текущую версию, применяет дельту

Ожидаемый размер дельты при 50 новых статьях: ~200 КБ.

### 3.5 Хранение на устройстве

```
IndexedDB:
  store: "offline-kb"
    ├── key: "manifest"     → JSON manifest
    ├── key: "index"        → situation-index (распакованный JSON)
    ├── key: "vectors"      → ArrayBuffer (article-vectors.bin)
    ├── key: "templates"    → ArrayBuffer (template-vectors.bin)
    ├── key: "vector-map"   → JSON (chunk_id → offset)
    └── key: "template-map" → JSON (template_key → offset)

  store: "articles"
    ├── key: "chunk_id_1"   → {title, content_preview, layer, ...}
    ├── key: "chunk_id_2"   → ...
    └── ...

  store: "dtc"
    ├── key: "P0010"        → {description, chunk_ids, system}
    └── ...
```

SQLite через sql.js (~1.2 МБ wasm) — альтернатива, если нужен FTS.
Но для 11K записей IndexedDB быстрее и проще.

---

## 4. Алгоритм матчинга

### 4.1 Полный алгоритм (JS, без ML)

```javascript
class SituationMatcher {
    constructor() {
        this.articleVectors = null;   // Float16Array
        this.templateVectors = null;  // Float16Array
        this.vectorMap = null;        // {chunk_id: {base: offset, problem: offset, ...}}
        this.templateMap = null;      // {template_key: offset}
        this.index = null;            // situation-index
    }

    async init() {
        // Загружаем из IndexedDB (~50 мс)
        const db = await openDB('offline-kb');
        this.articleVectors = new Float32Array(await db.get('vectors'));
        this.templateVectors = new Float32Array(await db.get('templates'));
        this.vectorMap = await db.get('vector-map');
        this.templateMap = await db.get('template-map');
        this.index = await db.get('index');
    }

    /**
     * Основной метод матчинга
     * @param {Object} context - пользовательский контекст
     * @param {number} topK - количество результатов (default: 3)
     * @returns {Array<{chunk_id, score, reason}>}
     */
    match(context, topK = 3) {
        // ═══════════════════════════════════════════
        // ЭТАП 1: Индексный отбор кандидатов (< 1 мс)
        // ═══════════════════════════════════════════

        const candidateSets = [];
        const weights = {};

        // DTC — высший приоритет
        if (context.dtc_codes?.length) {
            for (const dtc of context.dtc_codes) {
                const chunks = this.index.by_dtc[dtc] || [];
                candidateSets.push({ chunks, weight: 5.0, reason: `DTC ${dtc}` });
            }
        }

        // Система
        const system = this.resolveSystem(context);
        if (system) {
            const chunks = this.index.by_system[system] || [];
            candidateSets.push({ chunks, weight: 2.0, reason: `system:${system}` });
        }

        // Компонент
        if (context.selected_part) {
            const chunks = this.index.by_component[context.selected_part] || [];
            candidateSets.push({ chunks, weight: 3.0, reason: `part:${context.selected_part}` });
        }

        // Событие
        if (context.event) {
            const chunks = this.index.by_event[context.event] || [];
            candidateSets.push({ chunks, weight: 1.5, reason: `event:${context.event}` });
        }

        // Пробег
        if (context.mileage != null) {
            const range = this.getMileageRange(context.mileage);
            const chunks = this.index.by_mileage[range] || [];
            candidateSets.push({ chunks, weight: 0.8, reason: `mileage:${range}` });
        }

        // Сезон
        if (context.season) {
            const chunks = this.index.by_season[context.season] || [];
            candidateSets.push({ chunks, weight: 0.5, reason: `season:${context.season}` });
        }

        // Объединяем кандидатов с накоплением весов
        const candidateScores = new Map();
        for (const { chunks, weight, reason } of candidateSets) {
            for (const chunkId of chunks) {
                if (!candidateScores.has(chunkId)) {
                    candidateScores.set(chunkId, { score: 0, reasons: [] });
                }
                const entry = candidateScores.get(chunkId);
                entry.score += weight;
                entry.reasons.push(reason);
            }
        }

        // Берём top-50 по индексному скору
        let candidates = [...candidateScores.entries()]
            .sort((a, b) => b[1].score - a[1].score)
            .slice(0, 50);

        // ═══════════════════════════════════════════
        // ЭТАП 2: Векторное ранжирование (< 5 мс)
        // ═══════════════════════════════════════════

        if (candidates.length === 0) {
            return this.fallback(context, topK);
        }

        // Собираем ситуационный вектор запроса
        // (взвешенная сумма предвычисленных шаблонов)
        const queryVector = this.buildQueryVector(context);

        // Считаем cosine similarity для каждого кандидата
        const results = [];
        for (const [chunkId, { score: indexScore, reasons }] of candidates) {
            const vectors = this.getArticleVectors(chunkId);

            // Берём максимальный cosine similarity среди всех
            // ситуационных векторов статьи
            let maxCosine = -1;
            let bestVariant = 'base';

            for (const [variant, vector] of Object.entries(vectors)) {
                const cosine = this.cosineSimilarity(queryVector, vector);
                if (cosine > maxCosine) {
                    maxCosine = cosine;
                    bestVariant = variant;
                }
            }

            // Комбинированный скор:
            // 60% — нормализованный индексный скор
            // 40% — cosine similarity
            const normalizedIndex = indexScore / candidateSets.length;
            const combinedScore = 0.6 * normalizedIndex + 0.4 * maxCosine;

            results.push({
                chunk_id: chunkId,
                score: combinedScore,
                cosine_score: maxCosine,
                index_score: normalizedIndex,
                matched_variant: bestVariant,
                reasons
            });
        }

        // Сортируем и возвращаем top-K
        results.sort((a, b) => b.score - a.score);
        return results.slice(0, topK);
    }

    /**
     * Строит query vector как взвешенную сумму шаблонных векторов
     */
    buildQueryVector(context) {
        const components = [];

        // DTC-шаблоны
        if (context.dtc_codes?.length) {
            for (const dtc of context.dtc_codes) {
                const key = `dtc:${dtc}`;
                if (this.templateMap[key] != null) {
                    components.push({
                        vector: this.getTemplateVector(key),
                        weight: 3.0
                    });
                }
            }
        }

        // Компонент + событие
        if (context.selected_part && context.event) {
            const key = `comp:${context.selected_part}+evt:${context.event}`;
            if (this.templateMap[key] != null) {
                components.push({
                    vector: this.getTemplateVector(key),
                    weight: 2.5
                });
            }
        }

        // Система + событие
        const system = this.resolveSystem(context);
        if (system && context.event) {
            const key = `sys:${system}+evt:${context.event}`;
            if (this.templateMap[key] != null) {
                components.push({
                    vector: this.getTemplateVector(key),
                    weight: 2.0
                });
            }
        }

        // Пробег
        if (context.mileage != null) {
            const range = this.getMileageRange(context.mileage);
            const key = `mil:${range}`;
            if (this.templateMap[key] != null) {
                components.push({
                    vector: this.getTemplateVector(key),
                    weight: 1.0
                });
            }
        }

        // Сезон
        if (context.season) {
            const key = `season:${context.season}`;
            if (this.templateMap[key] != null) {
                components.push({
                    vector: this.getTemplateVector(key),
                    weight: 0.5
                });
            }
        }

        // Взвешенная сумма + нормализация
        return this.weightedSum(components);
    }

    // ... вспомогательные методы ниже
}
```

### 4.2 Обработка частичного контекста

| Контекст | Стратегия |
|----------|-----------|
| Только DTC | Index: by_dtc. Vector: dtc-шаблон. Почти всегда точное попадание. |
| Только компонент | Index: by_component + by_system. Vector: comp+evt:maintenance (дефолт). |
| Только пробег | Index: by_mileage. Vector: mileage-шаблон. Возвращаем ТО-статьи. |
| Компонент + событие | Самый частый кейс. Index: пересечение. Vector: comp+evt шаблон. |
| Ничего (пустой контекст) | Fallback: популярные статьи по модели (предвычисленный топ-10). |

### 4.3 Пороги и фоллбеки

```javascript
const THRESHOLDS = {
    // Минимальный combined score для "уверенного" матча
    CONFIDENT: 0.45,

    // Минимальный score для показа (ниже — "нет релевантных статей")
    MINIMUM: 0.20,

    // Если cosine < этого — индексный матч ненадёжный
    COSINE_FLOOR: 0.15,

    // Максимум кандидатов для векторного ранжирования
    MAX_CANDIDATES: 50,
};

function postProcess(results) {
    // Фильтруем по порогу
    const filtered = results.filter(r => r.score >= THRESHOLDS.MINIMUM);

    if (filtered.length === 0) {
        return {
            results: [],
            message: "Не найдено подходящих статей. Попробуйте изменить параметры.",
            suggestion: suggestBroaderSearch(context)
        };
    }

    // Помечаем уровень уверенности
    for (const r of filtered) {
        r.confidence = r.score >= THRESHOLDS.CONFIDENT ? 'high'
                     : r.score >= 0.30 ? 'medium' : 'low';
    }

    return { results: filtered };
}
```

### 4.4 Cosine Similarity на чистом JS (оптимизированный)

```javascript
/**
 * Cosine similarity для Float32Array vectors
 * Оптимизация: векторы предварительно нормализованы → dot product = cosine
 */
function cosineSimilarity(a, b) {
    // Если векторы нормализованы (L2 norm = 1), достаточно dot product
    let dot = 0;
    for (let i = 0; i < a.length; i++) {
        dot += a[i] * b[i];
    }
    return dot;
}

// 384d dot product: ~1 μs на современном телефоне
// 50 кандидатов × 3 вектора × 1 μs = ~150 μs = 0.15 мс
```

---

## 5. Метаданные статей для матчинга

### 5.1 Схема тегов

Для каждой из 11,398 статей нужны следующие теги (хранятся в `situation-index.json`):

```typescript
interface ArticleTags {
    chunk_id: string;

    // Тип ситуации
    situation_type: 'emergency' | 'maintenance' | 'learning' | 'troubleshooting' | 'specification';

    // Сезонная релевантность
    season: 'winter' | 'summer' | 'all';  // spring/autumn → 'all'

    // Диапазоны пробега (может быть несколько)
    mileage_ranges: ('0-10k' | '10-30k' | '30-60k' | '60k+')[];

    // Система и компоненты (из layer + glossary_links)
    system: string;         // "brakes", "hvac", ...
    group: string;          // "suspension", "cabin", ...
    components: string[];   // ["brake_pad@brakes", "brake_caliper@brakes"]

    // Связанные DTC
    dtc_codes: string[];    // ["C0265", "C0035"]

    // Типы событий, для которых статья релевантна
    events: ('warning_light' | 'noise' | 'vibration' | 'performance' | 'maintenance')[];

    // Приоритет/срочность (1-5)
    urgency: number;        // 5 = critical safety, 1 = informational

    // Флаги из существующих данных
    has_procedures: boolean;
    has_warnings: boolean;
}
```

### 5.2 Правила автоматической разметки

```python
def auto_tag_article(chunk, dtc_links, glossary_links):
    tags = {}

    # ── situation_type ──
    if chunk['has_warnings'] and any(w in chunk['content'].lower()
            for w in ['emergency', 'danger', '紧急', '危险', 'опасно', 'немедленно']):
        tags['situation_type'] = 'emergency'
    elif chunk['has_procedures']:
        tags['situation_type'] = 'maintenance'
    elif chunk['content_type'] == 'dtc':
        tags['situation_type'] = 'troubleshooting'
    elif any(w in chunk['content'].lower() for w in ['specification', '规格', 'характеристик']):
        tags['situation_type'] = 'specification'
    else:
        tags['situation_type'] = 'learning'

    # ── season ──
    content_lower = chunk['content'].lower()
    winter_words = ['winter', 'cold', 'freeze', 'antifreeze', '冬', 'зим', 'мороз', 'антифриз']
    summer_words = ['summer', 'hot', 'overheat', 'cooling', '夏', 'лет', 'перегрев', 'охлаждени']

    is_winter = any(w in content_lower for w in winter_words)
    is_summer = any(w in content_lower for w in summer_words)

    if is_winter and not is_summer:
        tags['season'] = 'winter'
    elif is_summer and not is_winter:
        tags['season'] = 'summer'
    else:
        tags['season'] = 'all'

    # ── mileage_ranges ──
    # Определяем по типу операции
    tags['mileage_ranges'] = infer_mileage_ranges(chunk)

    # ── system / group / components ──
    tags['system'] = chunk['layer']
    tags['group'] = KB_LAYER_BRIDGE.get(chunk['layer'])
    tags['components'] = [g['glossary_id'] for g in glossary_links]

    # ── dtc_codes ──
    tags['dtc_codes'] = [d['dtc_code'] for d in dtc_links]

    # ── events ──
    tags['events'] = infer_events(chunk)

    # ── urgency ──
    tags['urgency'] = compute_urgency(chunk)

    return tags


def infer_mileage_ranges(chunk):
    """Определяет релевантные диапазоны пробега"""
    ranges = []
    content = chunk['content'].lower()

    # Обкатка / новый автомобиль
    if any(w in content for w in ['break-in', '磨合', 'обкатк', 'new vehicle']):
        ranges.append('0-10k')

    # Замена расходников (тормозные колодки, масло, фильтры)
    if any(w in content for w in ['replace', 'change', '更换', 'замен']):
        if chunk['layer'] in ['brakes', 'engine']:
            ranges.extend(['10-30k', '30-60k'])

    # Капитальные работы
    if any(w in content for w in ['overhaul', 'rebuild', '大修', 'капитальн']):
        ranges.append('60k+')

    # Если ничего не определили — релевантно для всех
    if not ranges:
        ranges = ['0-10k', '10-30k', '30-60k', '60k+']

    return list(set(ranges))


def infer_events(chunk):
    """Определяет типы событий, для которых статья релевантна"""
    events = []
    content = chunk['content'].lower()

    # Warning light
    if any(w in content for w in ['warning light', 'indicator', 'dashboard',
            '警告灯', '指示灯', 'индикатор', 'сигнал', 'лампа']):
        events.append('warning_light')

    # Noise
    if any(w in content for w in ['noise', 'sound', 'squeal', 'grind', 'rattle',
            '噪音', '声音', '异响', 'шум', 'скрип', 'стук', 'скрежет']):
        events.append('noise')

    # Vibration
    if any(w in content for w in ['vibration', 'shake', 'wobble', 'pulsation',
            '振动', '抖动', 'вибрац', 'биение', 'дрожан']):
        events.append('vibration')

    # Performance degradation
    if any(w in content for w in ['reduced', 'weak', 'slow', 'poor', 'failure',
            '降低', '减弱', 'снижен', 'слаб', 'плох']):
        events.append('performance')

    # Maintenance / scheduled
    if chunk['has_procedures'] or any(w in content for w in [
            'maintenance', 'service', 'inspect', 'schedule',
            '保养', '维护', '检查', 'обслуживан', 'проверк', 'осмотр']):
        events.append('maintenance')

    if not events:
        events = ['maintenance']  # default fallback

    return events


def compute_urgency(chunk):
    """Вычисляет уровень срочности (1-5)"""
    score = 2  # базовый

    if chunk['has_warnings']:
        score += 1

    content = chunk['content'].lower()

    # Критическая безопасность
    if any(w in content for w in ['danger', 'fatal', 'fire', 'explosion',
            '危险', '致命', '火灾', '爆炸', 'опасно', 'пожар', 'взрыв']):
        score = 5

    # Высокий приоритет (HV, тормоза)
    elif chunk['layer'] in ['battery', 'brakes'] and chunk['has_warnings']:
        score = max(score, 4)

    # DTC = повышенный приоритет
    elif chunk['content_type'] == 'dtc':
        score = max(score, 3)

    return min(score, 5)
```

### 5.3 Инвертированные индексы (situation-index.json)

```json
{
    "version": "2026.03.05",
    "by_dtc": {
        "P0010": ["li_auto_l9_l7_ru_18303c8f", "li_auto_l9_l7_en_48905e1c"],
        "C0265": ["li_auto_l9_ru_abc123", ...]
    },
    "by_system": {
        "brakes": ["chunk_1", "chunk_2", ...],
        "ev": ["chunk_3", ...],
        "hvac": [...]
    },
    "by_group": {
        "electric": ["chunk_3", ...],
        "suspension": ["chunk_1", "chunk_2", ...]
    },
    "by_component": {
        "brake_pad@brakes": ["chunk_1", ...],
        "traction_battery@ev": ["chunk_3", ...]
    },
    "by_event": {
        "warning_light": ["chunk_1", "chunk_3", ...],
        "noise": ["chunk_2", ...],
        "vibration": [...],
        "performance": [...],
        "maintenance": [...]
    },
    "by_mileage": {
        "0-10k": [...],
        "10-30k": [...],
        "30-60k": [...],
        "60k+": [...]
    },
    "by_season": {
        "winter": [...],
        "summer": [...],
        "all": [...]
    },
    "by_urgency": {
        "5": [...],
        "4": [...],
        "3": [...],
        "2": [...],
        "1": [...]
    },
    "popular_by_model": {
        "l7": ["chunk_a", "chunk_b", ...],
        "l9": ["chunk_c", "chunk_d", ...]
    }
}
```

---

## 6. Конкретный пайплайн

### 6.1 Скрипты для сборки

#### Скрипт 1: `scripts/build_situation_tags.py` — Разметка всех статей

```
Вход:  knowledge-base/kb.db
Выход: knowledge-base/situation_tags.json (все теги для 11,398 статей)
Время: ~30 секунд (чистый SQL + regex, без ML)

Шаги:
1. SELECT все chunks + JOIN chunk_dtc, chunk_glossary
2. Для каждого chunk → auto_tag_article()
3. Сохранить JSON с полной разметкой
```

#### Скрипт 2: `scripts/build_situation_embeddings.py` — Вычисление векторов

```
Вход:  knowledge-base/kb.db + situation_tags.json
Выход: offline-package/article-vectors.bin
       offline-package/article-vector-map.json
       offline-package/template-vectors.bin
       offline-package/template-keys.json
Время: ~20 минут на GPU (multilingual-e5-small, 11,398 × ~3.5 вектора)

Шаги:
1. Загрузить multilingual-e5-small (120 МБ)
2. Сгенерировать ~1,100 situation templates → embed → template-vectors.bin
3. Для каждого chunk:
   a. base vector: embed(title + content[:200])
   b. problem vector: embed(title + " problem diagnosis")  [если has_warnings]
   c. procedure vector: embed(title + " repair procedure") [если has_procedures]
   d. dtc vector: embed(title + " DTC " + codes)           [если есть DTC]
   e. component vector: embed(title + " " + components)    [если есть glossary]
4. Упаковать в binary Float16 + map
```

#### Скрипт 3: `scripts/build_situation_index.py` — Сборка индексов

```
Вход:  situation_tags.json
Выход: offline-package/situation-index.json
Время: ~5 секунд

Шаги:
1. Загрузить situation_tags.json
2. Построить инвертированные индексы (by_dtc, by_system, ...)
3. Построить popular_by_model (топ-10 по urgency × has_procedures)
4. Сохранить JSON
```

#### Скрипт 4: `scripts/build_offline_db.py` — Облегчённая БД

```
Вход:  knowledge-base/kb.db
Выход: offline-package/articles-lite.db
Время: ~10 секунд

Шаги:
1. Создать новую SQLite БД
2. INSERT INTO articles — только нужные поля, content обрезан до 500 символов
3. INSERT INTO translations — только RU и EN
4. INSERT INTO dtc_links — из chunk_dtc
5. INSERT INTO glossary_links — из chunk_glossary (cleaned, ~8,597 строк)
6. VACUUM
```

#### Скрипт 5: `scripts/package_offline.py` — Финальная упаковка

```
Вход:  offline-package/* (все файлы выше)
Выход: offline-package/llcar-offline-v{date}.tar.gz
       offline-package/manifest.json
Время: ~5 секунд

Шаги:
1. Вычислить SHA256 для каждого файла
2. Создать manifest.json
3. gzip-упаковка всего пакета
4. Вывести статистику размеров
```

### 6.2 Мастер-скрипт

```bash
#!/bin/bash
# scripts/build_offline_package.sh

echo "=== LLCAR Offline Package Builder ==="

echo "[1/5] Tagging articles..."
python scripts/build_situation_tags.py

echo "[2/5] Building situation embeddings..."
python scripts/build_situation_embeddings.py --model multilingual-e5-small --device cuda:0

echo "[3/5] Building situation index..."
python scripts/build_situation_index.py

echo "[4/5] Building lite database..."
python scripts/build_offline_db.py

echo "[5/5] Packaging..."
python scripts/package_offline.py

echo "=== Done! Package: offline-package/llcar-offline-*.tar.gz ==="
```

### 6.3 Тестирование качества матчинга

#### Тестовый набор (ручной, ~50 кейсов)

```json
// tests/situation_matching_test_cases.json
[
    {
        "id": "test_001",
        "description": "Скрип тормозов зимой на L9 с пробегом 45000",
        "context": {
            "selected_part": "brake_pad",
            "season": "winter",
            "mileage": 45000,
            "dtc_codes": [],
            "event": "noise",
            "model": "l9"
        },
        "expected_layers": ["brakes"],
        "expected_has_procedures": true,
        "expected_keywords": ["brake", "pad", "noise", "тормоз", "колодк"],
        "min_results": 2
    },
    {
        "id": "test_002",
        "description": "Ошибка C0265 — индикатор ABS",
        "context": {
            "dtc_codes": ["C0265"],
            "event": "warning_light"
        },
        "expected_dtc_in_result": "C0265",
        "expected_layers": ["brakes", "sensors"],
        "min_results": 1
    },
    {
        "id": "test_003",
        "description": "Пустой контекст — фоллбек",
        "context": {},
        "min_results": 3,
        "expected_fallback": true
    }
    // ... ещё 47 кейсов
]
```

#### Скрипт тестирования

```python
# scripts/test_situation_matching.py

def evaluate_matching():
    matcher = SituationMatcher()  # Python-версия для тестов
    matcher.init()

    test_cases = json.load(open('tests/situation_matching_test_cases.json'))

    passed = 0
    failed = 0

    for tc in test_cases:
        results = matcher.match(tc['context'], top_k=5)

        # Проверяем наличие результатов
        if len(results) < tc.get('min_results', 1):
            print(f"FAIL {tc['id']}: got {len(results)} results, expected >= {tc['min_results']}")
            failed += 1
            continue

        # Проверяем релевантность слоёв
        if 'expected_layers' in tc:
            result_layers = set(get_layer(r['chunk_id']) for r in results[:3])
            if not result_layers.intersection(tc['expected_layers']):
                print(f"FAIL {tc['id']}: layers {result_layers} not in {tc['expected_layers']}")
                failed += 1
                continue

        # Проверяем DTC
        if 'expected_dtc_in_result' in tc:
            result_dtcs = set()
            for r in results[:3]:
                result_dtcs.update(get_dtc_codes(r['chunk_id']))
            if tc['expected_dtc_in_result'] not in result_dtcs:
                print(f"FAIL {tc['id']}: DTC {tc['expected_dtc_in_result']} not found")
                failed += 1
                continue

        # Проверяем ключевые слова в контенте
        if 'expected_keywords' in tc:
            all_content = ' '.join(r.get('title', '') + ' ' + r.get('content', '')
                                   for r in results[:3]).lower()
            found = any(kw in all_content for kw in tc['expected_keywords'])
            if not found:
                print(f"FAIL {tc['id']}: no keywords found in results")
                failed += 1
                continue

        passed += 1

    print(f"\n=== Results: {passed} passed, {failed} failed out of {len(test_cases)} ===")

    # Целевая метрика: >= 80% passed
    return passed / len(test_cases) >= 0.80
```

### 6.4 Порядок реализации

| Шаг | Скрипт | Зависимости | Время разработки |
|-----|--------|-------------|-----------------|
| 1 | `build_situation_tags.py` | kb.db | 2-3 часа |
| 2 | Тестовые кейсы (50 штук) | Ручная работа | 2-3 часа |
| 3 | `build_situation_index.py` | situation_tags.json | 1 час |
| 4 | `build_situation_embeddings.py` | multilingual-e5-small, tags | 3-4 часа |
| 5 | `build_offline_db.py` | kb.db | 1 час |
| 6 | `SituationMatcher` (JS-класс) | Все bin/json файлы | 4-5 часов |
| 7 | `package_offline.py` + manifest | Все offline-файлы | 1 час |
| 8 | `test_situation_matching.py` | Тестовые кейсы + matcher | 2-3 часа |
| 9 | Интеграция в frontend | SituationMatcher | 3-4 часа |
| **Итого** | | | **~20-24 часа** |

---

## Итоговая сводка

| Параметр | Значение |
|----------|---------|
| ML-модель на устройстве | **НЕТ** (0 МБ) |
| Размер офлайн-пакета | **~29 МБ** (gzip) |
| Время матчинга | **< 10 мс** (индекс + dot product) |
| Покрытие ситуаций | ~1,100 предвычисленных шаблонов |
| Статей с тегами | 11,398 (все) |
| Точность (целевая) | >= 80% на тестовом наборе |
| Обновления | Дельта-пакеты (~200 КБ при 50 новых статьях) |
| Фоллбек при пустом контексте | Топ-10 популярных по модели |
