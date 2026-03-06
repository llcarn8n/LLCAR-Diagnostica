#!/usr/bin/env python3
"""
kursiv_media_scraper.py — Scraper for kz.kursiv.media (Kazakhstan business media).

Detailed Li Auto analysis articles:
- Problem compilations (timing chain, suspension, winter issues)
- Market analysis and sales data for CIS region
"""
from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

BASE = "https://kz.kursiv.media"

SEARCH_QUERIES = [
    "li+auto", "lixiang", "li+auto+проблемы", "lixiang+подвеска",
    "lixiang+двигатель", "li+auto+зимой",
]


class KursivMediaScraper(BaseScraper):
    source_name = "kursiv_media"
    lang = "ru"
    delay_range = (2.0, 4.0)
    min_content_length = 300
    min_relevance = 0.0

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

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
                    if BASE in full and ("li-auto" in full.lower() or "lixiang" in full.lower() or "kmlz" in full.lower()):
                        article_urls.add(full.split('#')[0].rstrip('/'))
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

                title = page.css("h1::text").get() or page.css("title::text").get() or ""

                content_parts = []
                for sel in [".article-body p", ".post-content p", "article p", ".entry-content p"]:
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
                    lang="ru", title=title.strip()[:200], content=content[:5000],
                )
                self._sleep()
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = KursivMediaScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
