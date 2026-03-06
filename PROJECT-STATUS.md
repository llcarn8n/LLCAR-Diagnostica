# LLCAR Diagnostica KB — Статус проекта

> Дата фиксации: 2026-03-06
> Проект: C:\Users\Петр\threejs-project\Final 3d\LLCAR-Transfer

---

## Что это

Полноценное приложение для диагностики автомобилей Li Auto L7/L9:
- **База знаний** (SQLite + LanceDB) — 11,872 чанка из официальных мануалов + веб-статей
- **Гибридный поиск** (BM25 + dense vectors + ColBERT reranking) — FastAPI сервер
- **Веб-интерфейс** (SPA) — мобильный стиль, 3D-просмотр (Three.js), 7 экранов, 5 языков
- **Каталог запчастей** — 2,577 деталей (OCR через Qwen2.5-VL-7B)
- **15 веб-скраперов** — 164 статьи из 14 источников

---

## Ключевые метрики

| Метрика | Значение |
|---------|----------|
| Чанки в KB | 12,729 (11,024 manual + 488 DTC + 264 parts + 420 web/scraped + 47 topics + 40 research + 23 config + остальное) |
| Переводы | 48,384 строк (ZH: 12,570 / RU: 12,604 / EN: 12,604 / ES: 5,303 / AR: 5,303) |
| Модели авто | L7 (6,960), L9 (4,391), L7+L9 shared (521) |
| Слои | 15: body, interior, brakes, sensors, ev, engine, hvac, battery, drivetrain, lighting, chassis, infotainment, adas, parts, web_scraped |
| DTC-коды | 488 привязано |
| Глоссарий | 65,287 связей (8,597 уникальных терминов × 5 языков) |
| Изображения | 7,109 подписано + 11,426 извлечено из PDF + 10,014 привязано к чанкам |
| ColBERT-вектора | 11,799 (BGE-M3, FP16 BLOB) |
| Запчасти | 2,577 (22 системы, OCR + bridge к KB/3D) |
| Скрапинг | 420 статей (379 чистых + 41 garbage), 21 источник, 25 скраперов |
| Исследование | 40 research issues (консенсус 6 агентов) + 47 unified topics (анализ 394+ статей) |
| Тренировочные пары | 20,900+ (ZH↔EN/RU/AR/ES) |
| Размер БД | 4.28 GB (SQLite) + 0.62 GB (LanceDB) |
| Situation tags | 11,813 чанков с тегами (urgency, type, trust, season, events) |

---

## Структура проекта

```
LLCAR-Transfer/
├── api/
│   └── server.py              ← FastAPI сервер (~3300 строк, 10+ эндпоинтов)
├── frontend/
│   ├── index.html             ← SPA точка входа
│   ├── app.js                 ← Роутер/контроллер
│   ├── knowledge-base.js      ← API-клиент KB
│   ├── three-viewer.js        ← Three.js 3D-viewer
│   ├── kb-glossary.js         ← Глоссарий-тултипы
│   ├── css/diagnostica.css    ← Все стили
│   ├── screens/               ← 7 экранов (car-select, dashboard, diagnostics,
│   │                             digital-twin, knowledge, knowledge-v2, ai-assistant)
│   ├── scraping.html          ← GUI управления скрапингом
│   └── data/                  ← i18n (5 языков), architecture (маппинги, глоссарий)
├── scripts/
│   ├── scrapers/              ← 15 скраперов + base_scraper + run_scrapers
│   ├── rescrape_all.py        ← Mass re-scrape через новую систему извлечения
│   ├── build_kb.py, build_embeddings.py, translate_kb.py, etc.
│   └── ocr_parts_tables.py, reocr_missing_parts.py, audit_parts_coverage.py
├── knowledge-base/
│   ├── kb.db                  ← 4.28 GB SQLite (29 таблиц)
│   ├── lancedb/               ← 0.62 GB (content_emb + title_emb + image_emb)
│   ├── manuals/               ← 15 MD-файлов (11,097 чанков)
│   ├── articles/              ← 18 MD-файлов (301 статья)
│   └── training_pairs_*.jsonl ← Тренировочные данные
├── assets/models/             ← 4 GLB-модели (Li7/Li9 × unified/5layer)
├── mineru-output/             ← 11,426 JPG из PDF
├── deploy/                    ← deploy.bat, check_deploy.py, requirements.txt
├── node_modules/three/        ← Three.js 0.182
└── scraping-gui.bat           ← Запуск GUI скрапинга
```

---

## Что сделано (завершено)

### Фаза 1: База знаний
- [x] OCR мануалов (MinerU) → 11,097 чанков (ZH)
- [x] LanceDB embeddings (pplx-embed-context-v1-4b, 2560d)
- [x] ColBERT-вектора (BGE-M3) для всех чанков
- [x] Переводы ZH→RU/EN/AR/ES (44,623 строки)
- [x] Подписи к 7,109 изображениям (Qwen2.5-VL)
- [x] Fine-tuning M2M модели (Round 6, BLEU=13.39 → Petr117/m2m-diagnostica-automotive)
- [x] Тренировочные данные (20,900+ пар → Petr117/diagnostica-training-pairs)

### Фаза 2: API сервер
- [x] FastAPI: 3-стадийный гибридный поиск (BM25 + dense + ColBERT)
- [x] 10+ эндпоинтов: /search, /chunk/{id}, /dtc/{code}, /glossary/search, /parts/search, /stats
- [x] Скрапинг-эндпоинты: /scrapers/scrape-url, /scrapers/preview-extract, /scrapers/rescrape-all, /scrapers/rescrape/{id}
- [x] FTS5 баги исправлены (4 бага: JOIN, fallback, phrase split, findEntryById)

### Фаза 3: Фронтенд
- [x] SPA с 7 экранами, мобильный UI
- [x] 3D-viewer (Three.js 0.182, 5-слойная декомпозиция)
- [x] KB Search v1 (expert) + v2 (beginner, progressive disclosure)
- [x] Глоссарий-тултипы (8,597 терминов, 5 языков)
- [x] DTC-интеграция (клик по коду → детали + связанные статьи)
- [x] Дерево решений для новичков
- [x] Персонализация Новичок/Эксперт
- [x] 5 языков (RU/EN/ZH/AR/ES)

### Фаза 4: Запчасти
- [x] OCR 2,577 деталей (Qwen2.5-VL-7B, 3 раунда + rendered pages)
- [x] Дедупликация (3,222→2,473→2,577)
- [x] Parts-KB-3D bridge (22 системы → 5 диагностических групп)
- [x] API: /parts/search, /parts/stats, /parts/{number}
- [x] Фронтенд: таб "Parts" в knowledge.js, номера деталей в digital-twin.js

### Фаза 5: Веб-скрапинг
- [x] 25 скраперов (httpx + BeautifulSoup, без внешних зависимостей)
- [x] 420 статей из 21 источника (379 чистых + 41 garbage отмечено)
- [x] 6 методов извлечения: auto, trafilatura, bs4_article, bs4, regex, site-specific
- [x] GUI управления скрапингом (scraping.html)
- [x] Mass re-scrape через новую систему (scripts/rescrape_all.py)
- [x] Situation tags для всех 11,813 чанков

### Фаза 7: Исследование и анализ статей
- [x] 6-агентное исследование с эксклюзивными пулами (Telegram, Drom, Drive2, EN, CN, техБД)
- [x] 6 кросс-валидаторов (ротация): проверка фактов, отсев галлюцинаций
- [x] Консенсус: 42 проблемы → 40 импортированы (2 галлюцинации отсеяны)
- [x] 4 агента-аналитика: 394+ статей → 120 сырых топиков → 47 unified
- [x] import_research.py: 40 research chunks (RU+EN, с how_found методологией)
- [x] import_topics.py: 47 topic chunks (RU+EN, confidence scoring)
- [x] Бейджи в knowledge.js для research_consensus и article_analysis

### Фаза 6: Экспорт
- [x] Мануалы → 15 MD-файлов (knowledge-base/manuals/)
- [x] Статьи → 18 MD-файлов (knowledge-base/articles/)
- [x] Каталог запчастей → L9-PARTS-CATALOG.md

---

## Скрапинг: детальный статус

### Источники (работающие — 164 статьи)

| Источник | Статей | Язык | Содержание |
|----------|--------|------|------------|
| drom_reviews | 54 | RU | Отзывы владельцев Li L6/L7/L8/L9 |
| autoreview_ru | 41 | RU | Тесты, обзоры, статистика Авторевю |
| carnewschina_en | 37 | EN | Новости Li Auto (carnewschina.com) |
| autochina_blog | 6 | EN | Длинные обзоры китайских авто |
| carscoops_en | 6 | EN | Автоновости (carscoops.com) |
| liautocn_news | 5 | EN | Пресс-релизы Li Auto (ir.lixiang.com) |
| getcar_ru | 4 | RU | Русские обзоры (getcar.ru) |
| kitaec | 4 | RU | Обзоры китайских авто (kitaec.ua) |
| electrek_en | 2 | EN | EV-новости (electrek.co) |
| autonews_ru | 1 | RU | Автоновости (autonews.ru) |
| drom | 1 | RU | Подробный обзор L9 (drom.ru) |
| insideevs | 1 | EN | EV-обзор (insideevs.com) |
| topelectricsuv | 1 | EN | EV-обзор (topelectricsuv.com) |
| wikipedia_en | 1 | EN | Статья Li L7 |

### Источники (заблокированные/пустые)

| Источник | Статус | Причина |
|----------|--------|---------|
| drive2.ru | 403 Forbidden | Anti-bot защита, нужен резидентный прокси |
| autohome.com.cn | Гео-блок | Нужен китайский VPN |
| dongchedi.com | Гео-блок | Нужен китайский VPN |
| liforum.ru | 0 результатов | Нет топиков о Li Auto |
| chinacarforums.com | Таймаут | Сайт недоступен |

### Система извлечения контента

6 методов парсинга с GUI сравнением:
- **auto** — пробует site-specific → trafilatura → bs4 → regex
- **bs4_article** — сайт-специфичные CSS-селекторы (drom: `.b-editable-area`, carnewschina: `article .entry-content`, и др.)
- **trafilatura** — библиотека извлечения статей
- **trafilatura_precision** — строгий режим trafilatura
- **bs4** — generic BeautifulSoup (article/main/biggest div)
- **regex** — fallback через `<p>` теги

### Аудит качества (последний)
- Удалено 40 мусорных элементов (поисковые страницы, homepage-дампы, навигация, paywall)
- Исправлены 37 заголовков carnewschina (были "Search" после re-scrape → восстановлены из контента/URL)
- Все 164 статьи прошли через `_extract_article()` с auto-методом
- 0 пустых, 0 garbage-заголовков, 0 раздутых (>30K)

---

## На чём остановились (2026-03-06)

### Текущие задачи

1. **Перевод новых чанков** — 159 чанков без ZH перевода
   - 87 (topic+research) имеют RU+EN, нужен ZH
   - Нужно скачать M2M модель на воркстанцию (192.168.50.2)
   - `translate_kb.py` на воркстанции (2x RTX 3090)

2. **Embed в LanceDB** — 420+ статей + 87 topic/research НЕ в LanceDB
   - `python scripts/build_embeddings.py` (нужен GPU для pplx-embed)
   - Воркстанция: 2x RTX 3090

3. **Drive2.ru** — заблокирован (403)
   - Все методы заблокированы, нужен платный прокси

4. **Telegram** — 125 статей скраплены, ждём API ID + Hash для расширения

5. **Багфиксы scrapers** — faq_liautorussia возвращает 0 (нужен JS rendering)

---

## Запуск проекта

```cmd
:: Первый раз
deploy\deploy.bat

:: Каждый раз
.venv\Scripts\activate
set SKIP_PPLX_EMBED=1
uvicorn api.server:app --host 0.0.0.0 --port 8000

:: Второй терминал
npx http-server -p 8080

:: Браузер
start http://localhost:8080/frontend/

:: Скрапинг GUI
scraping-gui.bat
```

### Важные нюансы
- `SKIP_PPLX_EMBED=1` — на машине без 16+ GB VRAM (pplx-embed-v1-4b не влезает)
- Поиск работает в режиме `hybrid_colbert` (FTS5 + ColBERT через BGE-M3)
- HF-модели: BGE-M3 (~2 GB, обязательна), pplx-embed-v1-4b (~8 GB, опциональна)
- Three.js 0.182 уже в node_modules/ — НЕ нужно `npm install`

---

## Файлы планов

| Файл | Статус | Содержание |
|------|--------|------------|
| PLAN-KB-V2.md | DONE | KB v2 экран (9 фаз, progressive disclosure, глоссарий, DTC, дерево решений) |
| PLAN-PARTS-INTEGRATION.md | DONE | OCR запчастей + bridge + API + frontend |
| PLAN-KB-ENRICHMENT.md | PLANNING | Расширение KB практическим контентом (200-350 чанков) |
| PLAN-KB-SMART-CARDS.md | PLANNING | Умные карточки (trust/urgency/translation badges) |
| PROJECT-STATUS.md | CURRENT | Этот файл |
