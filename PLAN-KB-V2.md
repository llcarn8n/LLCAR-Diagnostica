# Knowledge Base v2 — План реализации

> Этот файл — план по созданию нового экрана "База знаний v2" на основе UX-отчёта.
> Старый экран knowledge.js НЕ трогаем. Новый — knowledge-v2.js.
> Создан: 2026-03-05

## Статус: РЕАЛИЗОВАНО (Фазы 1-9)

### Созданные/изменённые файлы

| # | Файл | Действие | Статус |
|---|------|----------|--------|
| 1 | `frontend/screens/knowledge-v2.js` | CREATE | DONE |
| 2 | `frontend/kb-glossary.js` | CREATE | DONE |
| 3 | `frontend/index.html` | MODIFY | DONE — добавлен `<div id="screen-knowledge-v2">` |
| 4 | `frontend/app.js` | MODIFY | DONE — импорт, регистрация, TAB_TO_SCREEN |
| 5 | `frontend/css/diagnostica.css` | MODIFY | DONE — ~300 строк CSS с префиксом `kbv2-` |
| 6 | `frontend/data/i18n/ru.json` | MODIFY | DONE — ключи `kbv2.*` |
| 7 | `PLAN-KB-V2.md` | UPDATE | Этот файл |

### Фазы

| # | Фаза | Статус |
|---|------|--------|
| 1 | Фундамент (скаффолд, регистрация) | DONE |
| 2 | Progressive Disclosure (карточки, статья, wizard) | DONE |
| 3 | Глоссарий-тултипы | DONE |
| 4 | DTC → KB интеграция | DONE |
| 5 | Ситуационная навигация | DONE |
| 6 | Дерево решений | DONE |
| 7 | 3D интеграция в статьях | DONE |
| 8 | Заботливый тон + Sparklines | DONE |
| 9 | Персонализация (Новичок/Эксперт) | DONE |

### Проверка

1. `npx http-server -p 8080 -c-1` → `http://localhost:8080/frontend/`
2. Таб "ЗНАНИЯ" → knowledge-v2 (ситуации)
3. Поиск → краткие карточки с цветовым кодированием
4. Клик → полная статья с глоссарий-тултипами
5. Таб DTC → DTC detail с "Можно ли ехать?"
6. "Не знаю что делать?" → дерево решений
7. Переключатель Новичок/Эксперт → изменение тона
8. Старый экран: через `switchScreen('knowledge')` в консоли

### Архитектурные решения

- **Параллельность**: knowledge-v2.js НЕ трогает knowledge.js
- **Переключение**: TAB_TO_SCREEN.knowledge → 'knowledge-v2', старый доступен напрямую
- **Persona**: localStorage 'llcar-persona' = 'beginner' | 'expert'
- **CSS**: все классы с префиксом `kbv2-` для изоляции
- **Навигация**: стек `_navStack` для кнопки "Назад"
- **API**: использует тот же `KnowledgeBase` класс из knowledge-base.js
- **Глоссарий**: `GlossaryTooltips` читает i18n-glossary-data.json, аннотирует HTML
