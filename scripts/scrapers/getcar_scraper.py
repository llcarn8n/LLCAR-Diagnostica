#!/usr/bin/env python3
"""
getcar_scraper.py — Scraper for getcar.ru Li Auto reliability/maintenance articles.

GetCar.ru has detailed articles about Li L9 problems in Russia:
- Suspension failures, brake issues, electronics bugs
- Real mileage data, repair costs, parts availability
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

# Known valuable articles + search pages
SEED_URLS = [
    "https://getcar.ru/blog/nadyozhnost-lixiang-l9-ekspluatacziya/",
    "https://getcar.ru/blog/polomki-lixiang-l9-rossiya/",
    "https://getcar.ru/blog/problemy-pnevmopodveski-lixiang-l9/",
    "https://getcar.ru/blog/komfort-nedostatki-lixiang-l9/",
    # Research-informed: additional articles found
    "https://getcar.ru/blog/obsluzhivanie-lixiang-l9-rossiya/",
    "https://getcar.ru/blog/lixiang-l9-ne-edet/",
    "https://getcar.ru/blog/shum-lixiang-l9-prichiny/",
    "https://getcar.ru/blog/problemy-lixiang-l9-2024/",
    "https://getcar.ru/en/blog/nadyozhnost-lixiang-l9-ekspluatacziya/",
    # Search queries
    "https://getcar.ru/blog/?s=lixiang",
    "https://getcar.ru/blog/?s=li+auto",
    "https://getcar.ru/blog/?s=li+l9",
    "https://getcar.ru/blog/?s=li+l7",
    "https://getcar.ru/blog/?s=lixiang+пневмоподвеска",
    "https://getcar.ru/blog/?s=lixiang+тормоза",
    "https://getcar.ru/blog/?s=lixiang+двигатель",
]


class GetCarScraper(BaseScraper):
    source_name = "getcar_ru"
    lang = "ru"
    delay_range = (2.0, 4.0)
    min_content_length = 300
    min_relevance = 0.0  # getcar articles are always relevant

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        # Collect article URLs from seed/search pages
        for url in SEED_URLS:
            if url.endswith('/') and 'blog/?' not in url and 's=' not in url:
                # Direct article URL
                article_urls.add(url)
                continue

            log.info("Searching: %s", url)
            try:
                page = static_fetch(url, timeout=20, verify=False)
                if page.status != 200:
                    continue
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    if '/blog/' in link and link.count('/') >= 4:
                        full = link if link.startswith('http') else f"https://getcar.ru{link}"
                        # Skip search/category/tag pages
                        if '?' not in full and '/page/' not in full:
                            article_urls.add(full.rstrip('/') + '/')
                self._sleep()
            except Exception as exc:
                log.warning("Search error: %s — %s", url, exc)

        log.info("Found %d article URLs", len(article_urls))

        # Scrape individual articles
        for url in sorted(article_urls):
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20, verify=False)
                if page.status != 200:
                    continue

                title = page.css("h1::text").get() or page.css("title::text").get() or ""

                # Extract article body
                content_parts = []
                for selector in [".entry-content p", ".post-content p", "article p", ".blog-post p"]:
                    for el in page.css(selector):
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

                # Filter out cookie/promo noise at the end
                content = _clean_content(content)

                yield ScrapedItem(
                    url=url, source_name=self.source_name,
                    lang="ru", title=title.strip()[:200], content=content,
                )
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


def _clean_content(text: str) -> str:
    """Remove common website noise from content."""
    noise_patterns = [
        r'Подписывайтесь на наш.*$',
        r'Поделитесь с друзьями.*$',
        r'Оставьте комментарий.*$',
        r'Cookie.*$',
        r'Нажимая.*согласие.*$',
        r'Политика конфиденциальности.*$',
        r'©.*$',
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
    return text.strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = GetCarScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
