#!/usr/bin/env python3
"""
drom_scraper.py — Scraper for drom.ru Li Auto L7/L9 pages.

Extracts: model descriptions, specs summary, review introductions.
Uses static Fetcher (no JS needed — key content is server-rendered).
"""
from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem
from typing import Iterator

log = logging.getLogger(__name__)

DROM_PAGES = [
    # L9 catalog/specs
    ("https://www.drom.ru/catalog/li/l9/", "ru", "Li L9 каталог — drom.ru"),
    ("https://www.drom.ru/catalog/li/l9/g_2025_22507/", "ru", "Li L9 2025 характеристики — drom.ru"),
    ("https://www.drom.ru/catalog/li/l9/g_202206_22507/", "ru", "Li L9 2022 характеристики — drom.ru"),
    # L7 catalog/specs
    ("https://www.drom.ru/catalog/li/l7/", "ru", "Li L7 каталог — drom.ru"),
    ("https://www.drom.ru/catalog/li/l7/g_2025_22529/", "ru", "Li L7 2025 характеристики — drom.ru"),
    ("https://www.drom.ru/catalog/li/l7/g_202206_22529/", "ru", "Li L7 2022 характеристики — drom.ru"),
    # L6, L8, MEGA — additional Li Auto models
    ("https://www.drom.ru/catalog/li/l6/", "ru", "Li L6 каталог — drom.ru"),
    ("https://www.drom.ru/catalog/li/l8/", "ru", "Li L8 каталог — drom.ru"),
    ("https://www.drom.ru/catalog/li/mega/", "ru", "Li MEGA каталог — drom.ru"),
    # Brand overview
    ("https://www.drom.ru/catalog/li/", "ru", "Li Auto все модели — drom.ru"),
]


class DromScraper(BaseScraper):
    source_name = "drom_ru"
    lang = "ru"
    delay_range = (2.0, 5.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        from base_scraper import static_fetch

        for url, lang, title_hint in DROM_PAGES:
            if self._already_scraped(url):
                log.info("Skip: %s", url)
                continue

            log.info("Fetching: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                title = (page.css("title::text").get() or title_hint)
                # Clean title
                title = title.split(" - ")[0].split(" | ")[0].strip()

                content = self._extract(page)
                if len(content) < 100:
                    log.warning("Short content (%d chars) for %s", len(content), url)
                    continue

                log.info("Extracted %d chars from %s", len(content), url)

                yield ScrapedItem(
                    url=url,
                    source_name=self.source_name,
                    lang=lang,
                    title=title,
                    content=content,
                )

            except Exception as exc:
                log.warning("Error: %s — %s", url, exc)

    def _extract(self, page) -> str:
        """Extract useful text from all text nodes, filtering JS noise."""
        all_text = page.css("body ::text").getall()

        JS_NOISE = ("function(", "document.", "window.", ".src =",
                    "new Image()", "escape(", "Math.random", "@context",
                    "@type", "itemListElement", "BreadcrumbList",
                    "namedChunks", "viewType=", "encodeURIComponent")

        seen = set()
        lines = []
        for t in all_text:
            t = t.strip()
            if len(t) < 15:
                continue
            if any(kw in t for kw in JS_NOISE):
                continue
            # Skip pure CSS blocks
            if t.startswith(".css-") or t.startswith("{margin") or t.startswith("{padding"):
                continue
            if t in seen:
                continue
            seen.add(t)
            lines.append(t)

        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = DromScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
