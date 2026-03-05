#!/usr/bin/env python3
"""
base_scraper.py — Base class for all Li Auto KB scrapers.

Handles:
- Rate limiting (configurable delay between requests)
- Deduplication via URL hash cache in SQLite
- Structured output to scraped_content table in kb.db
- Retry logic with exponential backoff
"""
from __future__ import annotations

import hashlib
import logging
import sqlite3
import time
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# ── Scrapling compatibility helpers ─────────────────────────────────────────
# Scrapling 0.4.x API changes:
#   Static (no JS):  Fetcher.get(url)          — class method, curl_cffi
#   Dynamic (JS):    StealthyFetcher().fetch(url) — instance method, patchright
#   Old API used:    StealthyFetcher().get(url)  — no longer exists in 0.4.x


class _BS4Page:
    """Lightweight page wrapper around httpx + BeautifulSoup to match scrapling API."""
    def __init__(self, status_code: int, html: str, final_url: str = ""):
        self.status = status_code
        self._html = html
        self.url = final_url
        self._soup = None

    @property
    def soup(self):
        if self._soup is None:
            from bs4 import BeautifulSoup
            self._soup = BeautifulSoup(self._html, "lxml")
        return self._soup

    def css(self, selector: str):
        """Scrapling-compatible CSS selector returning _BS4Selection."""
        return _BS4Selection(self.soup, selector)


class _BS4Selection:
    """Mimics scrapling CSS selection API (get, getall, iteration)."""
    def __init__(self, soup, selector: str):
        from bs4 import BeautifulSoup
        # Handle pseudo-element selectors: ::text, ::attr(xxx)
        self._pseudo = None
        self._attr_name = None
        clean_sel = selector

        if "::text" in selector:
            clean_sel = selector.replace("::text", "").strip()
            self._pseudo = "text"
        elif "::attr(" in selector:
            import re
            m = re.search(r"::attr\((\w+)\)", selector)
            if m:
                self._attr_name = m.group(1)
                clean_sel = selector[:m.start()].strip()

        # Use CSS select
        try:
            self._elements = soup.select(clean_sel) if clean_sel else [soup]
        except Exception:
            self._elements = []

    def get(self):
        """Get first match."""
        results = self.getall()
        return results[0] if results else None

    def getall(self):
        """Get all matches."""
        if self._pseudo == "text":
            texts = []
            for el in self._elements:
                texts.extend(el.stripped_strings)
            return texts
        elif self._attr_name:
            return [el.get(self._attr_name, "") for el in self._elements if el.get(self._attr_name)]
        else:
            return self._elements

    def __iter__(self):
        if self._pseudo or self._attr_name:
            return iter(self.getall())
        # For iterating over elements, wrap each in a mini-page for .css() calls
        return iter([_BS4ElementWrapper(el) for el in self._elements])

    def __getitem__(self, key):
        items = list(self.__iter__())
        return items[key]


class _BS4ElementWrapper:
    """Wraps a single BeautifulSoup element with .css() method."""
    def __init__(self, element):
        self._el = element
        self.attrib = dict(element.attrs) if hasattr(element, 'attrs') else {}

    def css(self, selector: str):
        return _BS4Selection(self._el, selector)


_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/131.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,zh;q=0.7",
}


def static_fetch(url: str, timeout: int = 20, retries: int = 2, verify: bool = True):
    """Fetch url with httpx (no JS). Returns page object with scrapling-compatible API.
    Retries on connection errors. Set verify=False for sites with expired SSL."""
    import httpx
    for attempt in range(retries + 1):
        try:
            r = httpx.get(url, timeout=timeout, follow_redirects=True, headers=_HEADERS, verify=verify)
            return _BS4Page(r.status_code, r.text, str(r.url))
        except Exception as exc:
            if attempt < retries:
                wait = 2 ** attempt + random.random()
                log.debug("Retry %d/%d for %s (%.1fs): %s", attempt + 1, retries, url, wait, exc)
                time.sleep(wait)
            else:
                log.warning("static_fetch failed after %d attempts: %s — %s", retries + 1, url, exc)
                return _BS4Page(0, "", url)


def stealth_fetch(url: str, timeout: int = 30):
    """
    Fetch url with scrapling StealthyFetcher (anti-bot Chromium).
    Falls back to patchright, then to httpx.
    """
    # Try scrapling StealthyFetcher first (best anti-bot)
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from scrapling.fetchers import StealthyFetcher
            sf = StealthyFetcher()
            return sf.fetch(url, timeout=timeout * 1000)
    except ImportError:
        pass
    except Exception as exc:
        log.warning("scrapling StealthyFetcher failed: %s — %s", url, exc)

    # Try patchright headless Chromium
    try:
        from patchright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=_HEADERS["User-Agent"],
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )
            pg = context.new_page()
            resp = pg.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
            pg.wait_for_timeout(2000)
            status = resp.status if resp else 0
            html = pg.content()
            final_url = pg.url
            browser.close()
            return _BS4Page(status, html, final_url)
    except ImportError:
        pass
    except Exception as exc:
        log.warning("patchright failed: %s — %s", url, exc)

    # Final fallback to httpx
    log.info("Stealth not available, falling back to httpx for %s", url)
    return static_fetch(url, timeout=timeout)


def extract_text_nodes(page, min_len: int = 15) -> list[str]:
    """
    Extract all visible text nodes from page body, filtering JS noise.
    Works with Scrapling page object.
    """
    JS_NOISE = ("function(", "document.", "window.", ".src =",
                "new Image()", "escape(", "Math.random", "@context",
                "@type", "itemListElement", "BreadcrumbList",
                "namedChunks", "viewType=", "encodeURIComponent",
                "gtag(", "dataLayer", "ga('send'", "fbq(")
    seen: set[str] = set()
    lines: list[str] = []
    for t in page.css("body ::text").getall():
        t = t.strip()
        if len(t) < min_len:
            continue
        if any(kw in t for kw in JS_NOISE):
            continue
        if t.startswith((".css-", "{margin", "{padding", "/*")):
            continue
        if t in seen:
            continue
        seen.add(t)
        lines.append(t)
    return lines


# Try scrapling, fall back to httpx for basic fetching
def _make_fetcher():
    """Return a simple fetch function: url -> (status, html_text)."""
    try:
        from scrapling.fetchers import Fetcher as _ScraplingFetcher
        class _ScraplingAdapter:
            def get(self, url, timeout=20, **kw):
                return _ScraplingFetcher.get(url, timeout=timeout)
        return _ScraplingAdapter()
    except Exception:
        import httpx
        class _HttpxAdapter:
            def get(self, url, timeout=20, **kw):
                r = httpx.get(url, timeout=timeout, follow_redirects=True,
                              headers={"User-Agent": "Mozilla/5.0 (compatible; LI-KB-Bot/1.0)"})
                class _R:
                    status = r.status_code
                    html = r.text
                    def css(self, sel):
                        return _NullCSS()
                return _R()
        return _HttpxAdapter()


class _NullCSS:
    def get(self): return None
    def getall(self): return []
    def __iter__(self): return iter([])

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "scraped_articles.db"

# ── Relevance scoring & content classification ────────────────────────────

import re as _re

DTC_PATTERN = _re.compile(r'\b[PCBU]\d{4,5}\b')

DIAGNOSTIC_KEYWORDS = {
    'ru': [
        'ремонт', 'обслуживание', 'проблема', 'поломка', 'ошибка', 'замена',
        'неисправность', 'диагностика', 'сервис', 'пробег', 'расход',
        'зарядка', 'подвеска', 'масло', 'фильтр', 'тормоз', 'аккумулятор',
        'батарея', 'пневмо', 'скрип', 'вибрация', 'перегрев', 'индикатор',
        'обновление', 'запас хода', 'колодки', 'антифриз', 'охлаждение',
        'компрессор', 'датчик', 'калибровка', 'шум', 'стук',
        'рычаг', 'амортизатор', 'ota', 'прошивка',
        'регламент', 'интервал', 'гарантия', 'отзыв', 'рекомендация',
    ],
    'en': [
        'repair', 'maintenance', 'problem', 'issue', 'fault', 'error', 'code',
        'replace', 'service', 'suspension', 'oil', 'filter', 'brake', 'battery',
        'troubleshoot', 'diagnostic', 'mileage', 'recall', 'charging', 'range',
        'nvh', 'noise', 'vibration', 'overheat', 'ota', 'update', 'firmware',
        'coolant', 'compressor', 'sensor', 'calibration', 'rattle', 'squeak',
        'arm', 'damper', 'shock', 'strut', 'warranty', 'interval', 'schedule',
        'procedure', 'step-by-step', 'how to', 'diy', 'fix',
    ],
    'zh': [
        '维修', '保养', '问题', '故障', '错误', '更换', '悬架', '机油', '滤芯',
        '制动', '电池', '诊断', '里程', '召回', '充电', '续航', '噪音', '异响',
        '减震', '传感器', '校准', 'OTA', '固件', '冷却', '压缩机',
    ],
}

# Keywords for content classification
_CLASSIFICATION_KEYWORDS = {
    'troubleshooting': [
        'проблема', 'поломка', 'ошибка', 'неисправность', 'problem', 'issue',
        'fault', 'error', 'troubleshoot', 'fix', 'решение', 'причина',
        '故障', '问题', '错误',
    ],
    'maintenance': [
        'обслуживание', 'замена', 'масло', 'фильтр', 'регламент', 'ТО',
        'maintenance', 'oil', 'filter', 'service', 'schedule', 'interval',
        'replace', '保养', '更换', '机油', '滤芯',
    ],
    'guide': [
        'инструкция', 'пошагово', 'как', 'руководство', 'how to', 'step',
        'guide', 'tutorial', 'diy', '指南', '教程',
    ],
    'specs': [
        'характеристики', 'спецификация', 'параметр', 'мощность', 'крутящий',
        'specification', 'specs', 'power', 'torque', 'dimension',
        '参数', '规格', '功率',
    ],
    'owner_review': [
        'отзыв', 'владелец', 'опыт', 'впечатление', 'достоинство', 'недостаток',
        'review', 'owner', 'experience', 'pros', 'cons',
        '车主', '评价', '优点', '缺点',
    ],
}


def relevance_score(content: str, lang: str = 'ru') -> float:
    """Score 0.0–1.0 based on diagnostic keyword density.
    Score ≥ 0.2 = relevant, < 0.2 = likely noise."""
    keywords = DIAGNOSTIC_KEYWORDS.get(lang, DIAGNOSTIC_KEYWORDS['en'])
    text = content.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    return min(hits / 5.0, 1.0)


def extract_dtc_codes(content: str) -> list[str]:
    """Extract unique DTC codes (P0300, C0265, etc.) from text."""
    return sorted(set(DTC_PATTERN.findall(content.upper())))


def classify_content(content: str, source_name: str = '') -> str:
    """Auto-classify content into content_type.
    Returns: troubleshooting | maintenance | guide | specs | owner_review | news"""
    # Source-based hints
    if source_name in ('drom_reviews', 'drive2'):
        return 'owner_review'

    text = content.lower()

    # DTC codes → troubleshooting
    if DTC_PATTERN.search(content):
        return 'troubleshooting'

    # Score each category
    best_cat = 'news'
    best_score = 0
    for cat, keywords in _CLASSIFICATION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > best_score:
            best_score = score
            best_cat = cat

    return best_cat if best_score >= 2 else 'news'

# ── Schema ───────────────────────────────────────────────────────────────────

SCRAPED_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS scraped_content (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    url_hash      TEXT NOT NULL UNIQUE,
    url           TEXT NOT NULL,
    source_name   TEXT NOT NULL,          -- e.g. 'lixiang_com', 'autohome', 'drive2'
    lang          TEXT NOT NULL,          -- 'zh', 'ru', 'en'
    title         TEXT,
    content       TEXT NOT NULL,
    scraped_at    TEXT DEFAULT (datetime('now')),
    imported      INTEGER DEFAULT 0,      -- 1 = added to chunks
    chunk_id      TEXT,                   -- FK to chunks.id after import
    relevance     REAL DEFAULT 0,         -- 0.0–1.0 diagnostic relevance score
    dtc_codes     TEXT DEFAULT '',        -- comma-separated DTC codes found
    content_class TEXT DEFAULT 'news'     -- auto-classified: troubleshooting/maintenance/guide/etc.
);
CREATE INDEX IF NOT EXISTS idx_scraped_source ON scraped_content(source_name);
CREATE INDEX IF NOT EXISTS idx_scraped_imported ON scraped_content(imported);
CREATE INDEX IF NOT EXISTS idx_scraped_url_hash ON scraped_content(url_hash);
"""

# Migration: add new columns to existing table if missing
SCRAPED_TABLE_MIGRATE = """
ALTER TABLE scraped_content ADD COLUMN relevance REAL DEFAULT 0;
ALTER TABLE scraped_content ADD COLUMN dtc_codes TEXT DEFAULT '';
ALTER TABLE scraped_content ADD COLUMN content_class TEXT DEFAULT 'news';
"""


@dataclass
class ScrapedItem:
    url: str
    source_name: str
    lang: str
    title: str
    content: str
    dtc_codes: list[str] = field(default_factory=list)
    content_class: str = ''    # auto-classified type
    score: float = 0.0         # relevance score 0.0–1.0

    @property
    def url_hash(self) -> str:
        return hashlib.sha256(self.url.encode()).hexdigest()[:16]

    def compute_metadata(self) -> None:
        """Auto-compute relevance score, DTC codes, and content class."""
        self.score = relevance_score(self.content, self.lang)
        self.dtc_codes = extract_dtc_codes(self.content)
        self.content_class = classify_content(self.content, self.source_name)


class BaseScraper(ABC):
    """
    Abstract base for all source-specific scrapers.

    Subclasses must implement:
        - source_name: str  (e.g. 'lixiang_com')
        - lang: str         (primary language, e.g. 'zh')
        - scrape() -> Iterator[ScrapedItem]
    """

    source_name: str
    lang: str
    delay_range: tuple[float, float] = (1.5, 3.5)   # seconds between requests
    max_retries: int = 3

    min_content_length: int = 300        # skip items shorter than this
    min_relevance: float = 0.0           # 0.0 = accept all; 0.2 = filter noise
    skip_relevance_filter: bool = False  # subclass can disable filtering

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCRAPED_TABLE_DDL)
            # Migrate: add new columns if missing
            for line in SCRAPED_TABLE_MIGRATE.strip().split('\n'):
                try:
                    conn.execute(line.strip().rstrip(';'))
                except sqlite3.OperationalError:
                    pass  # column already exists

    def _already_scraped(self, url: str) -> bool:
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM scraped_content WHERE url_hash=?", (url_hash,)
            ).fetchone()
        return row is not None

    def _save(self, item: ScrapedItem) -> bool:
        """Save item to DB. Returns False if URL already exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR IGNORE INTO scraped_content
                       (url_hash, url, source_name, lang, title, content,
                        relevance, dtc_codes, content_class)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (item.url_hash, item.url, item.source_name,
                     item.lang, item.title, item.content,
                     item.score, ','.join(item.dtc_codes), item.content_class),
                )
            return True
        except Exception as exc:
            log.warning("DB save failed for %s: %s", item.url, exc)
            return False

    def _sleep(self) -> None:
        delay = random.uniform(*self.delay_range)
        log.debug("Sleeping %.1fs", delay)
        time.sleep(delay)

    @abstractmethod
    def scrape(self) -> Iterator[ScrapedItem]:
        """Yield ScrapedItems. Skip already-scraped URLs."""
        ...

    def run(self) -> int:
        """Run scraper, save results, return count of new items.
        Auto-computes relevance, DTC codes, and content class.
        Filters by min_content_length and min_relevance."""
        saved = 0
        skipped_short = 0
        skipped_irrelevant = 0
        for item in self.scrape():
            # Filter: minimum content length
            if len(item.content) < self.min_content_length:
                skipped_short += 1
                log.debug("[%s] Skipped (too short %d chars): %s",
                          self.source_name, len(item.content), item.title[:60])
                continue

            # Auto-compute metadata
            item.compute_metadata()

            # Filter: minimum relevance
            if not self.skip_relevance_filter and self.min_relevance > 0 and item.score < self.min_relevance:
                skipped_irrelevant += 1
                log.debug("[%s] Skipped (relevance %.2f < %.2f): %s",
                          self.source_name, item.score, self.min_relevance, item.title[:60])
                continue

            if self._save(item):
                saved += 1
                dtc_info = f" DTC:{','.join(item.dtc_codes)}" if item.dtc_codes else ""
                log.info("[%s] Saved: %s (lang=%s, rel=%.2f, class=%s%s)",
                         self.source_name, item.title[:60], item.lang,
                         item.score, item.content_class, dtc_info)
            self._sleep()

        if skipped_short or skipped_irrelevant:
            log.info("[%s] Skipped: %d short, %d irrelevant",
                     self.source_name, skipped_short, skipped_irrelevant)
        log.info("[%s] Done. New items: %d", self.source_name, saved)
        return saved
