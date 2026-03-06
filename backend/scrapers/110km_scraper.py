#!/usr/bin/env python3
"""
110km_scraper.py — Scraper for 110km.ru owner reviews.

Structured owner reviews with ratings, pros/cons for Li Auto models.
Also news articles about Li Auto winter issues and reliability.
"""
from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

BASE = "https://110km.ru"

SEED_URLS = [
    # Owner reviews
    f"{BASE}/opinion/lixiang/l7/",
    f"{BASE}/opinion/lixiang/l9/",
    f"{BASE}/opinion/lixiang/",
    # Search for articles
    f"{BASE}/?s=lixiang",
    f"{BASE}/?s=li+auto",
    f"{BASE}/?s=lixiang+проблемы",
    f"{BASE}/?s=lixiang+зима",
]


class Scraper110km(BaseScraper):
    source_name = "110km_ru"
    lang = "ru"
    delay_range = (2.0, 4.0)
    min_content_length = 200
    min_relevance = 0.0

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        for seed in SEED_URLS:
            log.info("Fetching: %s", seed)
            try:
                page = static_fetch(seed, timeout=20)
                if page.status != 200:
                    continue
                for href in page.css("a::attr(href)").getall():
                    if not href:
                        continue
                    full = href if href.startswith("http") else f"{BASE}{href}"
                    if not full.startswith(BASE):
                        continue
                    # Article or review pages
                    if any(p in full for p in ['/art/', '/opinion/', '/news/']):
                        if '?' not in full and '/page/' not in full:
                            article_urls.add(full.split('#')[0].rstrip('/'))
                self._sleep()
            except Exception as exc:
                log.warning("Seed error: %s — %s", seed, exc)

        log.info("Found %d URLs", len(article_urls))

        for url in sorted(article_urls):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""

                content_parts = []
                # Review pages often have structured blocks
                for sel in [".review-text p", ".article-body p", ".entry-content p",
                            ".post-content p", "article p"]:
                    for el in page.css(sel):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 20:
                            content_parts.append(text)
                    if content_parts:
                        break

                if not content_parts:
                    content_parts = extract_text_nodes(page, min_len=20)

                content = "\n\n".join(content_parts)
                if len(content) < 150:
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
    scraper = Scraper110km()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
