#!/usr/bin/env python3
"""
lixiang_sto_scraper.py — Scraper for lixiang-sto.ru (Moscow Li Auto service center).

Real repair procedures, costs, parts availability, diagnostic tips.
Blog articles with detailed technical content.
"""
from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes
from typing import Iterator

log = logging.getLogger(__name__)

BASE = "https://lixiang-sto.ru"

SEED_URLS = [
    f"{BASE}/blog/",
    f"{BASE}/blog/remont-pnevmopodveski-lixiang-l7/",
    f"{BASE}/blog/remont-pnevmopodveski-lixiang-l9/",
]


class LixiangStoScraper(BaseScraper):
    source_name = "lixiang_sto"
    lang = "ru"
    delay_range = (2.0, 4.0)
    min_content_length = 200
    min_relevance = 0.0  # service center content always relevant

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        # Discover articles from blog listing
        for seed in SEED_URLS:
            if '/blog/' == seed.replace(BASE, '').rstrip('/') + '/':
                # Blog listing page
                try:
                    page = static_fetch(seed, timeout=20)
                    if page.status == 200:
                        for href in page.css("a::attr(href)").getall():
                            if not href:
                                continue
                            full = href if href.startswith("http") else f"{BASE}{href}"
                            if '/blog/' in full and full != seed and full.startswith(BASE):
                                article_urls.add(full.split('#')[0].rstrip('/') + '/')
                    self._sleep()
                except Exception as exc:
                    log.warning("Blog listing error: %s", exc)
            else:
                article_urls.add(seed)

        # Also discover from service pages
        try:
            for path in ["/uslugi/", "/brands/lixiang/"]:
                page = static_fetch(f"{BASE}{path}", timeout=20)
                if page.status == 200:
                    for href in page.css("a::attr(href)").getall():
                        if not href:
                            continue
                        full = href if href.startswith("http") else f"{BASE}{href}"
                        if full.startswith(BASE) and ('/blog/' in full or '/uslugi/' in full):
                            article_urls.add(full.split('#')[0].rstrip('/') + '/')
                self._sleep()
        except Exception as exc:
            log.warning("Service pages error: %s", exc)

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
                for sel in [".entry-content p", ".post-content p", "article p", ".page-content p", "main p"]:
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
                log.warning("Page error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = LixiangStoScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
