#!/usr/bin/env python3
"""
ru_auto_scraper.py — Scraper for accessible Russian Li Auto sources.

Sites that work with httpx (no anti-bot):
  - avtotachki.com — Russian-language EV reviews and specs
  - motor.ru — car reviews and news
  - autostat.ru — automotive statistics and news
  - chinamobil.ru — Chinese cars portal
  - kitaec.ua — Chinese car reviews (Ukrainian/Russian)
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

LISTING_URLS = [
    # Avtotachki — search (verified working)
    ("https://avtotachki.com/?s=li+auto", "ru", "avtotachki", "Li Auto поиск"),
    ("https://avtotachki.com/?s=li+l9", "ru", "avtotachki", "Li L9 поиск"),
    ("https://avtotachki.com/?s=li+l7", "ru", "avtotachki", "Li L7 поиск"),
    ("https://avtotachki.com/?s=li+mega", "ru", "avtotachki", "Li MEGA поиск"),
    ("https://avtotachki.com/obzor-li-auto-l9/", "ru", "avtotachki", "Li Auto L9 обзор"),
    ("https://avtotachki.com/obzor-li-auto-l7/", "ru", "avtotachki", "Li Auto L7 обзор"),
    # Motor.ru — search (verified working)
    ("https://motor.ru/search?query=li+auto", "ru", "motor_ru", "Li Auto — Motor.ru"),
    ("https://motor.ru/search?query=li+l9", "ru", "motor_ru", "Li L9 — Motor.ru"),
    ("https://motor.ru/search?query=li+l7", "ru", "motor_ru", "Li L7 — Motor.ru"),
    # Autostat — search (verified working)
    ("https://www.autostat.ru/search/?q=li+auto", "ru", "autostat", "Li Auto — Autostat"),
    ("https://www.autostat.ru/search/?q=li+l9", "ru", "autostat", "Li L9 — Autostat"),
    # Chinamobil — Chinese cars portal (verified working)
    ("https://chinamobil.ru/?s=li+auto", "ru", "chinamobil", "Li Auto — Chinamobil"),
    ("https://chinamobil.ru/?s=li+l9", "ru", "chinamobil", "Li L9 — Chinamobil"),
    ("https://chinamobil.ru/?s=li+l7", "ru", "chinamobil", "Li L7 — Chinamobil"),
    # Kitaec.ua — Chinese car reviews (verified working)
    ("https://kitaec.ua/search/?q=li+auto", "ru", "kitaec", "Li Auto — Kitaec"),
    ("https://kitaec.ua/search/?q=li+l9", "ru", "kitaec", "Li L9 — Kitaec"),
    ("https://kitaec.ua/search/?q=li+l7", "ru", "kitaec", "Li L7 — Kitaec"),
]


class RuAutoScraper(BaseScraper):
    source_name = "ru_auto"
    lang = "ru"
    delay_range = (2.0, 4.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        article_urls = set()

        # Phase 1: scrape seed pages directly + discover article links
        for url, lang, source_tag, title_hint in LISTING_URLS:
            log.info("[%s] Fetching: %s", source_tag, url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                # Yield the seed page itself (if it has substantial content)
                if not self._already_scraped(url):
                    title = (page.css("h1::text").get()
                             or page.css("title::text").get()
                             or title_hint)
                    title = re.sub(r"\s*[|—\-]\s*.*$", "", title).strip() or title_hint
                    content = self._extract_content(page)
                    if len(content) > 300:
                        yield ScrapedItem(
                            url=url, source_name=source_tag,
                            lang=lang, title=title[:200], content=content,
                        )

                # Look for article links
                for link in page.css("a::attr(href)").getall():
                    if not link:
                        continue
                    link = link.split("#")[0].rstrip("/")
                    full = link if link.startswith("http") else self._make_full_url(url, link)
                    link_lower = full.lower()

                    has_li = ("li-auto" in link_lower or "/li/" in link_lower or
                              "lixiang" in link_lower or "li_auto" in link_lower or
                              "lilauto" in link_lower)
                    is_article = (has_li and
                                  not any(x in link_lower for x in ["/tag", "/category",
                                          "/page/", "?q=", "/search"]) and
                                  full != url)

                    if is_article:
                        article_urls.add((full, lang, source_tag))

                self._sleep()
            except Exception as exc:
                log.warning("Error: %s — %s", url, exc)

        log.info("Discovered %d article URLs", len(article_urls))

        # Phase 2: scrape articles
        for url, lang, source_tag in sorted(article_urls)[:50]:
            if self._already_scraped(url):
                continue
            try:
                page = static_fetch(url, timeout=20)
                if page.status != 200:
                    continue

                title = (page.css("h1::text").get()
                         or page.css("title::text").get() or "")
                title = re.sub(r"\s*[|—\-]\s*.*$", "", title).strip()
                if not title:
                    slug = url.rstrip("/").split("/")[-1]
                    title = slug.replace("-", " ").replace("_", " ").title()

                content = self._extract_content(page)
                if len(content) < 200:
                    continue

                yield ScrapedItem(
                    url=url, source_name=source_tag,
                    lang=lang, title=title[:200], content=content,
                )
                self._sleep()
            except Exception as exc:
                log.warning("Article error: %s — %s", url, exc)

    def _extract_content(self, page) -> str:
        sections = []

        # Spec tables
        for row in page.css("table tr"):
            cells = [" ".join(c.css("::text").getall()).strip()
                     for c in row.css("th, td")]
            cells = [c for c in cells if c]
            if cells:
                sections.append(" | ".join(cells))

        # Article paragraphs
        for el in page.css("article p, .article__text p, .review-text p, "
                           ".post-content p, .entry-content p, .content p, "
                           ".description p, main p"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if len(text) > 20:
                sections.append(text)

        # Headings
        for el in page.css("h2, h3"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if text and len(text) > 3:
                sections.append(f"## {text}")

        if len("\n".join(sections)) < 200:
            sections = extract_text_nodes(page, min_len=15)

        return "\n".join(sections)

    @staticmethod
    def _make_full_url(base_url: str, path: str) -> str:
        if path.startswith("http"):
            return path
        from urllib.parse import urljoin
        return urljoin(base_url, path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = RuAutoScraper()
    count = scraper.run()
    print(f"Done. New items saved: {count}")
