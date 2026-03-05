#!/usr/bin/env python3
"""
ru_sources_scraper.py — Scraper for Russian-language Li Auto sources.

Sources:
  - drom.ru     — reviews and specs (static Fetcher, no JS needed)
  - drive2.ru   — owner stories and reviews (StealthyFetcher, anti-bot)
  - auto.ru     — specs (StealthyFetcher, JS-rendered)
"""
from __future__ import annotations

import logging
import re
import sys
import os
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, stealth_fetch, extract_text_nodes

log = logging.getLogger(__name__)

# (url, lang, source_tag, title_hint, use_stealth)
RU_URLS = [
    # drom.ru — specs and reviews (static, no JS needed)
    ("https://www.drom.ru/catalog/li/l9/",        "ru", "drom.ru",   "Li Auto L9 характеристики - drom.ru", False),
    ("https://www.drom.ru/catalog/li/l7/",        "ru", "drom.ru",   "Li Auto L7 характеристики - drom.ru", False),
    ("https://www.drom.ru/reviews/?brand=li",     "ru", "drom.ru",   "Li Auto отзывы - drom.ru",            False),
    # drive2.ru — owner journals (anti-bot, needs StealthyFetcher)
    ("https://www.drive2.ru/cars/lilauto/",       "ru", "drive2.ru", "Li Auto на Drive2",                   True),
    ("https://www.drive2.ru/b/lilauto/l9/",       "ru", "drive2.ru", "Li Auto L9 на Drive2",                True),
    ("https://www.drive2.ru/b/lilauto/l7/",       "ru", "drive2.ru", "Li Auto L7 на Drive2",                True),
    # auto.ru — specs (JS-rendered)
    ("https://auto.ru/catalog/cars/li_auto/l9/",  "ru", "auto_ru",   "Li Auto L9 на auto.ru",               True),
    ("https://auto.ru/catalog/cars/li_auto/l7/",  "ru", "auto_ru",   "Li Auto L7 на auto.ru",               True),
]


class RuSourcesScraper(BaseScraper):
    source_name = "ru_sources"
    lang = "ru"
    delay_range = (2.0, 5.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        for url, lang, source, title_hint, use_stealth in RU_URLS:
            if self._already_scraped(url):
                log.info("Skip (already scraped): %s", url)
                continue

            log.info("[%s] Fetching%s: %s", source, " (stealth)" if use_stealth else "", url)
            try:
                page = stealth_fetch(url, timeout=30) if use_stealth else static_fetch(url, timeout=20)

                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                title = page.css("title::text").get() or title_hint
                title = re.sub(r"\s*[|—\-]\s*(drom|drive2|авто|auto).*$", "", title, flags=re.I).strip()

                content = self._extract_content(page)
                if len(content) < 100:
                    log.warning("Short content (%d) for %s", len(content), url)
                    continue

                log.info("Extracted %d chars from %s", len(content), url)
                yield ScrapedItem(
                    url=url,
                    source_name=source,
                    lang=lang,
                    title=title,
                    content=content,
                )

            except Exception as exc:
                log.warning("Error scraping %s: %s", url, exc)

            self._sleep()

    def _extract_content(self, page) -> str:
        """Extract article text, spec tables, review content."""
        lines = []

        # Spec tables
        for row in page.css("table tr"):
            cells = [" ".join(c.css("::text").getall()).strip() for c in row.css("th, td")]
            cells = [c for c in cells if c]
            if cells:
                lines.append(" | ".join(cells))

        # Article / review content
        for el in page.css("article p, .article__text p, .review-text p, .journal-entry p, "
                           ".car-description, .technical-specs li, .spec-item"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if len(text) > 20:
                lines.append(text)

        # Headings for structure
        for el in page.css("h1, h2, h3"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if text:
                lines.append(f"## {text}")

        # Fallback: extract all visible text if little extracted
        if len("\n".join(lines)) < 200:
            lines = extract_text_nodes(page, min_len=15)

        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = RuSourcesScraper()
    count = scraper.run()
    print(f"Saved {count} new items from Russian sources")
