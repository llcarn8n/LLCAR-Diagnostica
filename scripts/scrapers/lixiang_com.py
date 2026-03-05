#!/usr/bin/env python3
"""
lixiang_com.py — Scraper for lixiang.com (official Li Auto site).

Scrapes:
  - L9 / L7 model overview pages
  - News / press-release pages

Language: zh (primary)
Uses StealthyFetcher (Chromium) — site has heavy JS rendering.
NOTE: Requires patchright chromium installed: python -m patchright install chromium
"""
from __future__ import annotations

import logging
import re
import sys
import os
from typing import Iterator

sys.path.insert(0, os.path.dirname(__file__))
from base_scraper import BaseScraper, ScrapedItem, stealth_fetch, extract_text_nodes

log = logging.getLogger(__name__)


# Pages to scrape — (url, lang, title_hint)
LIXIANG_PAGES = [
    # L9 model page
    ("https://www.lixiang.com/l9.html",   "zh", "Li L9 概览 — lixiang.com"),
    # L7 model page — /l7.html and /l7/* consistently timeout (heavy JS).
    # Known alternative that works: /l7pro.html or /li7.html
    ("https://www.lixiang.com/l7pro.html","zh", "Li L7 Pro 概览 — lixiang.com"),
    # Home page (overview of both L7 and L9)
    ("https://www.lixiang.com/",          "zh", "理想汽车 — lixiang.com"),
]


class LixiangComScraper(BaseScraper):
    source_name = "lixiang_com"
    lang = "zh"
    delay_range = (3.0, 6.0)

    def scrape(self) -> Iterator[ScrapedItem]:
        for url, lang, title_hint in LIXIANG_PAGES:
            if self._already_scraped(url):
                log.info("Skip: %s", url)
                continue

            log.info("Fetching (stealth): %s", url)
            try:
                page = stealth_fetch(url, timeout=60)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                title = page.css("title::text").get() or title_hint
                title = re.sub(r"\s*[-|—]\s*(理想汽车|lixiang).*$", "", title, flags=re.I).strip()

                # Detect unwanted redirects: page redirected to home if URL didn't match
                final_url = page.url if hasattr(page, 'url') else url
                if final_url and final_url.rstrip('/') not in url.rstrip('/'):
                    # Check if both are home page variations
                    home_variants = ["lixiang.com/", "lixiang.com"]
                    req_is_home = any(url.rstrip('/').endswith(v) for v in home_variants)
                    fin_is_home = any(final_url.rstrip('/').endswith(v) for v in home_variants)
                    if fin_is_home and not req_is_home:
                        log.warning("Redirect to home page detected for %s → %s, skipping", url, final_url)
                        continue

                lines = extract_text_nodes(page, min_len=10)
                content = "\n".join(lines)

                if len(content) < 100:
                    log.warning("Short content (%d chars) for %s", len(content), url)
                    continue

                log.info("Extracted %d chars from %s", len(content), url)
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = LixiangComScraper()
    count = scraper.run()
    print(f"Saved {count} new items from lixiang.com")
