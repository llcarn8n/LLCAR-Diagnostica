#!/usr/bin/env python3
"""
faq_liautorussia_scraper.py — Scraper for faq.liautorussia.ru (Li Auto Club Russia FAQ).

Most cited source in research — curated list of known problems, maintenance tips,
software/OTA guides, parts info. ~37,000 members.

Pages:
  /known-problems              — known problems list
  /aggregation/specs/*         — tech specs and partial solutions
  /no_software_update          — OTA guide
  /faq/*                       — FAQ articles
"""
from __future__ import annotations

import logging
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

BASE = "https://faq.liautorussia.ru"

SEED_URLS = [
    f"{BASE}/known-problems",
    f"{BASE}/no_software_update",
    f"{BASE}/aggregation/specs/air_suspention_partial_solution",
    f"{BASE}/",
]


class FaqLiAutoRussiaScraper(BaseScraper):
    source_name = "faq_liautorussia"
    lang = "ru"
    delay_range = (2.0, 4.0)
    min_content_length = 200
    min_relevance = 0.0  # all content is relevant

    def scrape(self) -> Iterator[ScrapedItem]:
        visited = set()
        to_visit = list(SEED_URLS)

        # Discover links from main page
        try:
            page = static_fetch(BASE, timeout=20)
            if page.status == 200:
                for href in page.css("a::attr(href)").getall():
                    if not href:
                        continue
                    full = href if href.startswith("http") else f"{BASE}{href}"
                    if full.startswith(BASE) and full not in to_visit:
                        # Skip static assets, anchors
                        if not any(ext in full for ext in ['.css', '.js', '.png', '.jpg', '.svg', '#']):
                            to_visit.append(full)
                self._sleep()
        except Exception as exc:
            log.warning("Main page error: %s", exc)

        for url in to_visit:
            url = url.split('#')[0].rstrip('/')
            if url in visited or self._already_scraped(url):
                continue
            visited.add(url)

            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""

                # Extract content from main area
                content_parts = []
                for sel in ["article", ".content", ".main-content", "main", ".page-content"]:
                    for el in page.css(f"{sel} p"):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 20:
                            content_parts.append(text)
                    if content_parts:
                        break

                # Also grab lists (FAQ often uses ul/ol)
                for el in page.css("article li, .content li, main li"):
                    text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                    if len(text) > 20:
                        content_parts.append(text)

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
                log.warning("Page error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = FaqLiAutoRussiaScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
