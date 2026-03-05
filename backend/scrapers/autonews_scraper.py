#!/usr/bin/env python3
"""
autonews_scraper.py — Scraper for autonews.ru Li Auto problem/review articles (RU).

Autonews has structured articles about Li Auto problems,
owner complaints, and maintenance costs in Russia.
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

SEARCH_QUERIES = [
    "https://www.autonews.ru/search?query=lixiang",
    "https://www.autonews.ru/search?query=li+auto",
    "https://www.autonews.ru/search?query=li+l9",
    "https://www.autonews.ru/search?query=li+l7",
    "https://www.autonews.ru/search?query=lixiang+проблемы",
    "https://www.autonews.ru/search?query=lixiang+обслуживание",
]

# Known valuable article
DIRECT_URLS = [
    "https://www.autonews.ru/news/683eae5d9a7947cdb92ef1cd",
]


class AutonewsScraper(BaseScraper):
    source_name = "autonews_ru"
    lang = "ru"
    delay_range = (2.0, 5.0)
    min_content_length = 400
    min_relevance = 0.2  # filter pure news

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set(DIRECT_URLS)

        # Search pages
        for url in SEARCH_QUERIES:
            log.info("Searching: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    full = link if link.startswith('http') else f"https://www.autonews.ru{link}"
                    # Article URLs: /news/XXXXX
                    if '/news/' in full and re.search(r'/news/[a-f0-9]{20,}', full):
                        article_urls.add(full)
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
                for selector in [
                    ".article__text p", ".article__body p",
                    ".article-content p", "article p",
                    ".news-item__text p",
                ]:
                    for el in page.css(selector):
                        text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                        if len(text) > 30:
                            content_parts.append(text)
                    if content_parts:
                        break

                if not content_parts:
                    content_parts = extract_text_nodes(page, min_len=30)

                content = "\n\n".join(content_parts)
                if len(content) < 300:
                    continue

                content = _clean(content)

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="ru", title=title.strip()[:200], content=content,
                )
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


def _clean(text: str) -> str:
    noise = [
        r'Подписывайтесь.*$', r'Читайте также.*$', r'Фото:.*$',
        r'Автор:.*$', r'©.*$', r'Реклама.*$',
    ]
    for p in noise:
        text = re.sub(p, '', text, flags=re.MULTILINE | re.IGNORECASE)
    return text.strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = AutonewsScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
