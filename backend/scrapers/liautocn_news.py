#!/usr/bin/env python3
"""
liautocn_news.py — Scraper for Li Auto official news and press releases.

Sources:
  - ir.lixiang.com/news  (EN investor relations / press releases)
  - Weibo / WeChat: skipped (login required)

Uses static Fetcher (ir.lixiang.com is mostly server-rendered).
"""
from __future__ import annotations

import logging
import re
import sys
import os
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, static_fetch, stealth_fetch

log = logging.getLogger(__name__)

# Verified accessible press-release URLs on ir.lixiang.com
# NOTE: /news-releases → 404; /news → 200 OK (listing)
# Individual articles are under /news-releases/news-release-details/...
NEWS_SOURCES = [
    # News listing page — scraper will follow article links from here
    ("https://ir.lixiang.com/news",                        "en", "Li Auto Investor Relations News"),
    # Known press releases (verified working, 2025-2026)
    ("https://ir.lixiang.com/news-releases/news-release-details/"
     "li-auto-inc-december-2025-delivery-update",          "en", "Li Auto December 2025 Delivery Update"),
    ("https://ir.lixiang.com/news-releases/news-release-details/"
     "li-auto-inc-february-2026-delivery-update",          "en", "Li Auto February 2026 Delivery Update"),
    ("https://ir.lixiang.com/news-releases/news-release-details/"
     "li-auto-inc-january-2026-delivery-update",           "en", "Li Auto January 2026 Delivery Update"),
    ("https://ir.lixiang.com/news-releases/news-release-details/"
     "li-auto-inc-report-fourth-quarter-and-full-year-2025-financial",
                                                           "en", "Li Auto Q4 FY2025 Financial Results"),
    # Older press releases
    ("https://ir.lixiang.com/news-releases/news-release-details/"
     "li-auto-delivers-first-batch-l9-customers-0",        "en", "L9 First Delivery Press Release"),
    ("https://ir.lixiang.com/news-releases/news-release-details/"
     "li-auto-inc-reports-fourth-quarter-and-full-year-2022-financial-results",
                                                           "en", "Li Auto 2022 Annual Results"),
    ("https://ir.lixiang.com/news-releases/news-release-details/"
     "li-auto-inc-reports-fourth-quarter-and-full-year-2023-financial-results",
                                                           "en", "Li Auto 2023 Annual Results"),
]


class LiAutoNewsScaper(BaseScraper):
    source_name = "liautocn_news"
    lang = "en"
    delay_range = (2.0, 4.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        for url, lang, title_hint in NEWS_SOURCES:
            if self._already_scraped(url):
                log.info("Skip: %s", url)
                continue

            log.info("Fetching: %s", url)
            try:
                page = static_fetch(url, timeout=20)
                if page.status == 403 or page.status == 0:
                    # Try stealth if blocked
                    log.info("Static blocked (%d), retrying with stealth: %s", page.status, url)
                    page = stealth_fetch(url, timeout=30)

                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                title = page.css("title::text, h1::text").get() or title_hint
                title = re.sub(r"\s*[|—\-]\s*Li Auto.*$", "", title).strip()

                is_article = "news-release-details" in url
                if is_article:
                    # Single article
                    content = self._extract_article(page)
                else:
                    # Listing — collect titles + links
                    content = self._extract_listing(page)

                    # Follow article links from any listing page (/news or /news-releases)
                    for link in page.css("a[href*='news-release']")[:20]:
                        href = link.attrib.get("href", "")
                        if not href.startswith("http"):
                            href = "https://ir.lixiang.com" + href
                        if href and "news-release-details" in href and not self._already_scraped(href):
                            self._sleep()
                            try:
                                p2 = static_fetch(href, timeout=20)
                                if p2.status != 200:
                                    p2 = stealth_fetch(href, timeout=30)
                                if p2.status == 200:
                                    t2 = p2.css("title::text, h1::text").get() or href
                                    t2 = re.sub(r"\s*[|—\-]\s*Li Auto.*$", "", t2).strip()
                                    c2 = self._extract_article(p2)
                                    if len(c2) > 80:
                                        yield ScrapedItem(
                                            url=href,
                                            source_name=self.source_name,
                                            lang=lang,
                                            title=t2,
                                            content=c2,
                                        )
                            except Exception as e:
                                log.debug("Article fetch failed %s: %s", href, e)

                if len(content) < 80:
                    continue

                yield ScrapedItem(
                    url=url,
                    source_name=self.source_name,
                    lang=lang,
                    title=title,
                    content=content,
                )

            except Exception as exc:
                log.warning("Error scraping %s: %s", url, exc)

            self._sleep()

    def _extract_article(self, page) -> str:
        texts = []
        for el in page.css("article, .news-content, .press-release-body, "
                           "main p, .article-body p, .field--type-text-with-summary p"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if len(text) > 20:
                texts.append(text)
        # Fallback: all <p> tags
        if not texts:
            for el in page.css("p"):
                text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
                if len(text) > 40:
                    texts.append(text)
        return "\n".join(texts)

    def _extract_listing(self, page) -> str:
        items = []
        for el in page.css(".news-item, .press-item, article, .field--name-title"):
            title = el.css("h2::text, h3::text, .title::text, a::text").get() or ""
            desc = el.css("p::text, .desc::text, .field--name-body::text").get() or ""
            date = el.css("time::text, .date::text, .field--name-field-date::text").get() or ""
            if title:
                items.append(f"[{date}] {title.strip()}: {desc.strip()}")
        return "\n".join(items)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = LiAutoNewsScaper()
    count = scraper.run()
    print(f"Saved {count} new items from Li Auto news")
