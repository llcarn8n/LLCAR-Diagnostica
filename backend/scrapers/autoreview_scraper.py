#!/usr/bin/env python3
"""
autoreview_scraper.py — Scraper for autoreview.ru Li Auto articles.

Autoreview.ru is a leading Russian auto magazine with professional
tests, reviews, comparisons, and news about Li Auto vehicles.

Uses static_fetch — content is server-rendered.
"""
from __future__ import annotations

import logging
import re
import sys
import os
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, extract_text_nodes

log = logging.getLogger(__name__)

# Search queries to find Li Auto content
SEARCH_QUERIES = [
    "li+auto",
    "li+l9",
    "li+l7",
    "li+l6",
    "li+mega",
    "li+i8",
    "lixiang",
]

BASE_URL = "https://autoreview.ru"


class AutoreviewScraper(BaseScraper):
    source_name = "autoreview_ru"
    lang = "ru"
    delay_range = (2.0, 4.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        # Phase 1: discover articles from search pages
        for query in SEARCH_QUERIES:
            url = f"{BASE_URL}/search?q={query}"
            log.info("Search: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    # Strip fragments (#comments etc)
                    link = link.split("#")[0].rstrip("/")
                    # Only article/test/news pages with enough path depth
                    # e.g. /articles/sravnitel-nye-testy/odnofamil-cy (3+ segments)
                    # NOT /articles/sravnitel-nye-testy (category listing)
                    path_parts = [p for p in link.split("/") if p]
                    has_section = any(
                        p in link for p in
                        ["/articles/", "/test/", "/news/", "/first-drive/"]
                    )
                    # Must have at least 2 path segments after /articles/ etc
                    is_deep_enough = len(path_parts) >= 3
                    # Skip pure category pages
                    is_listing = link.rstrip("/").endswith((
                        "/sravnitel-nye-testy", "/pervaya-vstrecha",
                        "/articles", "/test", "/news", "/gruzoviki-i-avtobusy",
                        "/autosport", "/avtorynok", "/bezopasnost",
                        "/kak-eto-rabotaet", "/first-drive", "/pervaya-vstrecha",
                    ))
                    if has_section and is_deep_enough and not is_listing:
                        full = link if link.startswith("http") else BASE_URL + link
                        article_urls.add(full)

                self._sleep()
            except Exception as exc:
                log.warning("Search error: %s — %s", url, exc)

        log.info("Discovered %d article URLs", len(article_urls))

        # Phase 2: scrape individual articles
        for url in sorted(article_urls)[:80]:
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                # Extract title
                title = (page.css("h1::text").get()
                         or page.css("meta[property='og:title']::attr(content)").get()
                         or page.css("title::text").get() or "")
                title = re.sub(
                    r"\s*[|—\-]\s*(Авторевю|Autoreview|autoreview).*$",
                    "", title, flags=re.I
                ).strip()
                if not title:
                    slug = url.rstrip("/").split("/")[-1]
                    title = slug.replace("-", " ").title()

                # Extract article content
                paragraphs = []
                for el in page.css("article p, .article-text p, .article__text p, "
                                   ".entry-content p, .post-content p, .text p"):
                    text = " ".join(
                        t.strip() for t in el.css("::text").getall() if t.strip()
                    )
                    if len(text) > 30:
                        paragraphs.append(text)

                if not paragraphs:
                    paragraphs = extract_text_nodes(page, min_len=20)

                content = "\n\n".join(paragraphs)
                if len(content) < 200:
                    log.debug("Short content (%d) for %s", len(content), url)
                    continue

                yield ScrapedItem(
                    url=url,
                    source_name=self.source_name,
                    lang="ru",
                    title=title[:200],
                    content=content,
                )
                self._sleep()
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = AutoreviewScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
