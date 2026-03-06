# CHANGELOG — LLCAR Diagnostica KB

Все изменения проекта фиксируются здесь. Формат: дата, коммит, описание.

---

## 2026-03-06

### feat: article analysis pipeline — 120 topics -> 47 unified, KB import [66ca23f]
- 4 агента-аналитика обработали 394+ статей из 18 источников
  - RU-аналитик: 35 топиков из 276 русских статей (drom, autonews, getcar, autoreview, telegram)
  - Telegram-аналитик: 25 топиков из 125 сообщений @lixiangautorussia
  - EN-аналитик: 25 топиков из 128 англоязычных статей (cnevpost, carnewschina, carscoops)
  - NEW-аналитик: 35 топиков из 130 статей 5 новых источников (kursiv, autoplt, 110km, lixiang_sto)
- `scripts/merge_topics.py` — дедупликация по keyword-группам, 120 -> 47 объединённых топиков
- `scripts/import_topics.py` — импорт в chunks + chunk_content (RU+EN)
- KB: 12,729 чанков (было ~10,079), 12,604 переводов RU и EN
- Бейджи `research_consensus` и `article_analysis` добавлены в knowledge.js
- Исправлен URL duplication bug в 110km_scraper.py и complaints_12365auto_scraper.py
- 41 мусорная статья помечена как garbage в scraped_content
- Исправлены layer assignments (brakes, infotainment, adas, battery)

### feat: 6-agent research + cross-validation + 7 new scrapers [5ef7f8a]
- 6 агентов-исследователей с эксклюзивными пулами источников
- 6 кросс-валидаторов (ротация: каждый проверяет чужие данные)
- Консенсус: 42 дедуплицированных проблемы, 40 импортированы (2 галлюцинации исключены)
- `research/consensus_issues.json` — 40 issues с how_found методологией
- `scripts/import_research.py` — импорт в KB (chunks + chunk_content RU+EN)
- 7 новых скраперов: faq_liautorussia, kursiv_media, cnevpost, lixiang_sto, 110km, autoplt, 12365auto
- Обновлены существующие: drom_reviews (+L6/L8), drive2 (+13 URL), autonews (+5 queries), getcar (+4 URL)
- run_scrapers.py обновлён с 25 скраперами
- Запуск скраперов: +120 новых статей (31 kursiv + 69 cnevpost + 8 lixiang_sto + 11 110km + 11 autoplt)

## 2026-03-05

### feat: KB restructure phase 2 + smart cards UI [49ed974]
- Situation tags для 11,813 чанков (urgency, type, trust, season, events)
- Smart cards UI: trust badges, urgency colors, translation indicators
- Фаза 2 реструктуризации KB

### feat: KB restructure phase 1+3 [27f5c3c]
- Merge фрагментов, quality scoring, glossary cleanup

### feat: article<->component integration [7b4cda3]
- Кликабельные RU теги компонентов
- Навигация к диаграммам из статей
- Увеличенные изображения запчастей

### docs: rewrite IMPLEMENTATION_PLAN.md [71b5922]
- Полный статус проекта + 5-фазный roadmap

## 2026-03-04

### feat: split GUI into 3 pages [d9d36fe]
- Home, Downloads, Scraping — три страницы GUI

### feat: add Telegram scraper + scraping GUI [fa374f2]
- Telegram scraper через Telethon с поиском по ключевым словам
- Скрапинг GUI (scraping.html + scraping-gui.bat)
- Unified DB: все скраперы пишут в kb.db

### feat: integrate AutoManuals backend [430ba09]
- LLCAR scraping subsystem integration
