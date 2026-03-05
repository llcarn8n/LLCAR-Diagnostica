#!/usr/bin/env python3
"""
liforum_scraper.py — Scraper for liforum.ru (largest Russian Li Auto community).

Extracts: forum threads about L7/L9 maintenance, faults, mods.
"""
from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

SEED_URLS = [
    "https://www.liforum.ru/",
    "https://www.liforum.ru/forums/",
]


class LiforumScraper(BaseScraper):
    source_name = "liforum_ru"
    lang = "ru"
    delay_range = (2.0, 4.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        thread_urls = set()

        # Phase 1: discover forum sections and threads
        for seed in SEED_URLS:
            log.info("Seed: %s", seed)
            try:
                page = static_fetch(seed, timeout=20)
                if page.status != 200:
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    full = link if link.startswith("http") else f"https://www.liforum.ru{link}"
                    # Forum section links
                    if "/forums/" in full and full.endswith("/"):
                        thread_urls.add(full)
                    # Topic links
                    if "/topic/" in full or "/threads/" in full:
                        thread_urls.add(full)
                self._sleep()
            except Exception as exc:
                log.warning("Seed error: %s — %s", seed, exc)

        # Phase 1.5: crawl discovered sections for topic links
        sections = [u for u in thread_urls if "/forums/" in u]
        for section_url in sections[:10]:  # limit to avoid overload
            log.info("Section: %s", section_url)
            try:
                page = static_fetch(section_url, timeout=20)
                if page.status != 200:
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    full = link if link.startswith("http") else f"https://www.liforum.ru{link}"
                    if "/topic/" in full or "/threads/" in full:
                        thread_urls.add(full)
                self._sleep()
            except Exception as exc:
                log.warning("Section error: %s — %s", section_url, exc)

        topics = [u for u in thread_urls if "/topic/" in u or "/threads/" in u]
        log.info("Discovered %d topic URLs", len(topics))

        # Phase 2: scrape topics
        for url in sorted(topics):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""
                title = title.strip()

                # Extract post content
                posts = []
                for post_el in page.css(".cPost_contentWrap, .ipsType_normal, article, .post-content"):
                    text = " ".join(t.strip() for t in post_el.css("::text").getall() if t.strip())
                    if len(text) > 30:
                        posts.append(text)

                if not posts:
                    posts = extract_text_nodes(page, min_len=20)

                content = "\n\n".join(posts)
                if len(content) < 200:
                    continue

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="ru", title=title[:200], content=content,
                )
            except Exception as exc:
                log.warning("Topic error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = LiforumScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
