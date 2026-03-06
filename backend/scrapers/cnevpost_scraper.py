#!/usr/bin/env python3
"""
cnevpost_scraper.py — Scraper for cnevpost.com (Chinese EV news in English).

Key content: Li Auto recalls, incidents, sales data, technology updates.
High-quality English articles about Chinese NEV industry.
"""
from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

BASE = "https://cnevpost.com"

SEARCH_QUERIES = [
    "li+auto", "li+auto+recall", "li+auto+l9", "li+auto+l7",
    "li+auto+suspension", "li+auto+quality", "lixiang",
]

# Known valuable articles
SEED_URLS = [
    "https://cnevpost.com/2022/07/18/li-auto-in-spotlight-for-li-l9-test-car-suspension-breakage/",
    "https://cnevpost.com/2025/11/14/li-auto-fires-employees-mega-recall/",
]


class CnevpostScraper(BaseScraper):
    source_name = "cnevpost_en"
    lang = "en"
    delay_range = (2.0, 4.0)
    min_content_length = 300
    min_relevance = 0.0

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set(SEED_URLS)

        for q in SEARCH_QUERIES:
            url = f"{BASE}/?s={q}"
            log.info("Searching: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue
                for href in page.css("a::attr(href)").getall():
                    if not href:
                        continue
                    full = href if href.startswith("http") else f"{BASE}{href}"
                    if BASE in full and "/20" in full and full.count('/') >= 5:
                        article_urls.add(full.split('#')[0].rstrip('/') + '/')
                self._sleep()
            except Exception as exc:
                log.warning("Search error: %s — %s", url, exc)

        log.info("Found %d article URLs", len(article_urls))

        for url in sorted(article_urls):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = page.css("h1.entry-title::text").get() or \
                        page.css("h1::text").get() or \
                        page.css("title::text").get() or ""

                content_parts = []
                for sel in [".entry-content p", ".post-content p", "article p"]:
                    for el in page.css(sel):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 30:
                            content_parts.append(text)
                    if content_parts:
                        break

                if not content_parts:
                    content_parts = extract_text_nodes(page, min_len=30)

                content = "\n\n".join(content_parts)
                if len(content) < 200:
                    continue

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="en", title=title.strip()[:200], content=content[:5000],
                )
                self._sleep()
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = CnevpostScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
