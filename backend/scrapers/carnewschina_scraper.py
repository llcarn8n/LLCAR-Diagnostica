#!/usr/bin/env python3
"""
carnewschina_scraper.py — Scraper for English-language Li Auto journalism sources.

Sources:
  - carnewschina.com — English news about Chinese EVs
  - cnevpost.com — Chinese EV news in English
  - gasgoo.com — Chinese auto industry news (EN)

Uses static_fetch — these sites are mostly server-rendered.
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

# Search/tag pages that list Li Auto articles
LISTING_URLS = [
    "https://autonews.gasgoo.com/articles/news/minieye-catl-intelligent-team-up-in-smart-driving-field-2029093142307901441",
    # carnewschina.com — tag pages with pagination
    ("https://carnewschina.com/tag/li-auto/", "en", "carnewschina", "Li Auto articles — CarNewsChina"),
    ("https://carnewschina.com/tag/li-auto/page/2/", "en", "carnewschina", "Li Auto p2 — CarNewsChina"),
    ("https://carnewschina.com/tag/li-auto/page/3/", "en", "carnewschina", "Li Auto p3 — CarNewsChina"),
    ("https://carnewschina.com/tag/li-l7/", "en", "carnewschina", "Li L7 — CarNewsChina"),
    ("https://carnewschina.com/tag/li-l7/page/2/", "en", "carnewschina", "Li L7 p2 — CarNewsChina"),
    ("https://carnewschina.com/tag/li-l9/", "en", "carnewschina", "Li L9 — CarNewsChina"),
    ("https://carnewschina.com/tag/li-l9/page/2/", "en", "carnewschina", "Li L9 p2 — CarNewsChina"),
    ("https://carnewschina.com/tag/li-mega/", "en", "carnewschina", "Li MEGA — CarNewsChina"),
    ("https://carnewschina.com/?s=li+auto+l7", "en", "carnewschina", "Li Auto L7 search — CarNewsChina"),
    ("https://carnewschina.com/?s=li+auto+l9", "en", "carnewschina", "Li Auto L9 search — CarNewsChina"),
    # cnevpost.com — tag pages with pagination
    ("https://cnevpost.com/tag/li-auto/", "en", "cnevpost", "Li Auto — CnEVPost"),
    ("https://cnevpost.com/tag/li-auto/page/2/", "en", "cnevpost", "Li Auto p2 — CnEVPost"),
    ("https://cnevpost.com/tag/li-auto/page/3/", "en", "cnevpost", "Li Auto p3 — CnEVPost"),
    ("https://cnevpost.com/tag/li-auto/page/4/", "en", "cnevpost", "Li Auto p4 — CnEVPost"),
    ("https://cnevpost.com/?s=li+auto+l7", "en", "cnevpost", "Li L7 search — CnEVPost"),
    ("https://cnevpost.com/?s=li+auto+l9", "en", "cnevpost", "Li L9 search — CnEVPost"),
    # gasgoo.com
    ("https://autonews.gasgoo.com/tag/Li%20Auto", "en", "gasgoo", "Li Auto — Gasgoo"),
]


class CarNewsChinaScraper(BaseScraper):
    source_name = "carnewschina_en"
    lang = "en"
    delay_range = (2.0, 4.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        # Phase 1: discover articles from listing pages
        for url, lang, source_tag, title_hint in LISTING_URLS:
            log.info("Listing [%s]: %s", source_tag, url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    # Strip fragment (#comments, etc.)
                    link = link.split("#")[0].rstrip("/")
                    link_lower = link.lower()
                    has_keywords = ("li-auto" in link_lower or "li-l7" in link_lower or
                                    "li-l9" in link_lower or "lixiang" in link_lower or
                                    "li+auto" in link_lower)
                    not_nav = not link_lower.endswith(("/tag", "/page", "/category",
                                                       "/topics", "/author"))
                    no_query = "?" not in link
                    has_date = bool(re.search(r"/\d{4}/\d{2}/\d{2}/", link))
                    # CnEVPost uses /YYYY/MM/slug/ format too
                    has_date2 = bool(re.search(r"/\d{4}/\d{2}/", link))
                    is_article = has_keywords and not_nav and no_query and (has_date or has_date2)
                    if is_article:
                        full = link if link.startswith("http") else url.rstrip("/") + link
                        article_urls.add((full, lang, source_tag))

                self._sleep()
            except Exception as exc:
                log.warning("Listing error: %s — %s", url, exc)

        log.info("Discovered %d article URLs", len(article_urls))

        # Phase 2: scrape individual articles
        for url, lang, source_tag in sorted(article_urls)[:150]:
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                # Try h1 first, then title tag, then og:title meta
                title = (page.css("h1.entry-title::text").get()
                         or page.css("h1::text").get()
                         or page.css("meta[property='og:title']::attr(content)").get()
                         or page.css("title::text").get()
                         or "")
                title = re.sub(r"\s*[|—\-]\s*(CarNewsChina|CnEVPost|Gasgoo).*$", "", title, flags=re.I).strip()
                if not title or title.lower() in ("search", "search results", ""):
                    # Extract from URL slug
                    slug = url.rstrip("/").split("/")[-1]
                    title = slug.replace("-", " ").title()

                # Extract article content
                paragraphs = []
                for el in page.css("article p, .entry-content p, .post-content p, "
                                   ".article-body p, .content-area p"):
                    text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                    if len(text) > 30:
                        paragraphs.append(text)

                if not paragraphs:
                    paragraphs = extract_text_nodes(page, min_len=20)

                content = "\n\n".join(paragraphs)
                if len(content) < 200:
                    continue

                yield ScrapedItem(
                    url=url, source_name=f"{source_tag}_en",
                    lang=lang, title=title[:200], content=content,
                )
                self._sleep()
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = CarNewsChinaScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
