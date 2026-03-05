#!/usr/bin/env python3
"""
autohome_scraper.py — Scraper for autohome.com.cn (汽车之家).

Scrapes owner reviews, forum threads, and spec sheets for Li Auto L7/L9.
Uses StealthyFetcher (Chromium) — site requires JS for content.

NOTE: autohome.com.cn may be geo-restricted. Requires chromium:
      python -m patchright install chromium
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

# Li Auto model IDs on autohome (from URL patterns)
AUTOHOME_URLS = [
    # L9 specs — series ID 70050
    ("https://www.autohome.com.cn/spec/70050/",  "zh", "理想L9 参数配置"),
    # L7 specs — series ID 71100
    ("https://www.autohome.com.cn/spec/71100/",  "zh", "理想L7 参数配置"),
    # Owner review pages — NOTE: k.autohome.com.cn/NNNN/ returns HTTP 200 but
    # content is "404: This page could not be found"; skip these URLs
    # ("https://k.autohome.com.cn/70050/",         "zh", "理想L9 用户口碑"),
    # ("https://k.autohome.com.cn/71100/",         "zh", "理想L7 用户口碑"),
    # Correct koubei (口碑) URL format:
    ("https://www.autohome.com.cn/koubei/#pvareaid=2042490",  "zh", "理想 用户口碑"),
]


class AutohomeScraper(BaseScraper):
    source_name = "autohome_cn"
    lang = "zh"
    delay_range = (4.0, 8.0)  # autohome has strict rate limiting

    def scrape(self) -> Iterator[ScrapedItem]:
        for url, lang, title_hint in AUTOHOME_URLS:
            if self._already_scraped(url):
                log.info("Skip: %s", url)
                continue

            log.info("Fetching (stealth): %s", url)
            try:
                page = stealth_fetch(url, timeout=35)
                if page.status != 200:
                    log.warning("HTTP %d for %s", page.status, url)
                    continue

                title = page.css("title::text").get() or title_hint
                title = re.sub(r"\s*[_\-|].*$", "", title).strip()

                content = self._extract_content(page)
                if len(content) < 100:
                    log.warning("Short content (%d) for %s", len(content), url)
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

    def _extract_content(self, page) -> str:
        """Extract spec tables, review text, forum posts."""
        sections = []

        # Spec table rows
        for row in page.css("table tr"):
            cells = [" ".join(c.css("::text").getall()).strip() for c in row.css("th, td")]
            cells = [c for c in cells if c]
            if cells:
                sections.append(" | ".join(cells))

        # Review / article text paragraphs
        for el in page.css(".article-content p, .koubei-content p, .forum-content p, "
                            ".review-item p, .summary p, .config-detail"):
            text = " ".join(t.strip() for t in el.css("::text").getall() if t.strip())
            if len(text) > 20:
                sections.append(text)

        # Fallback: extract all visible text if little extracted
        if len("\n".join(sections)) < 200:
            sections = extract_text_nodes(page, min_len=15)

        return "\n".join(sections)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = AutohomeScraper()
    count = scraper.run()
    print(f"Saved {count} new items from autohome.com.cn")
